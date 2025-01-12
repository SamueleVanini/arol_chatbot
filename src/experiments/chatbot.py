from pathlib import Path
from langchain.storage import InMemoryStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader


from core.logger import get_logger
from core.config import load_dotenv
from query_construction.self_querying import metadata_extraction
from service.llm_service import LlmFactory
from service.retriever_service import SetMergeRetrieverDirector
from service.file_loader_service import FileLoaderFactory, LoaderType
from vector_stores.chroma import ChromaCollection

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.documents import Document
from doc_loader.transform_pipe import ContentTransformation, FromFileToText, FromJsonToText

load_dotenv()

logger = get_logger(__name__)

FILE_PATH = "./data/processed_catalog.json"
COMPANY_INFO_FILE_PATH = "./data/company_info_cleaned.json"
COLLECTION_NAME = "retrival_matches"
PERSIST_DIRECTORY = "./data"

# Embedding function should get a class/function to get it?
EMBEDDING_FUNC = HuggingFaceEmbeddings(model_name="msmarco-distilbert-base-v4")
DATASET_NAME = "retrival_matches"
CHILD_COLLECTION = "full_documents"
COMPANY_COLLECTION = "company_info"
MODEL = "llama3-8b-8192"
# MODEL = "llama3-groq-8b-8192-tool-use-preview"

llm = LlmFactory.get_model(MODEL, max_tokens=8192)

# transformation_pipe = FromJsonToText(save_results=True, saving_path=Path("./data/json_rewritten.csv"))
transformation_pipe = FromFileToText(text_docs_path=Path("./data/json_rewritten.csv"))
loader = FileLoaderFactory.get_loader(
    LoaderType.HYBRID,
    FILE_PATH,
    transformation_pipe=transformation_pipe,
    metadata_func=metadata_extraction,
    max_tokens=8192,
)
company_info_loader = TextLoader(COMPANY_INFO_FILE_PATH)
logger.info("File loader ready")

docs = loader.load()
company_docs = company_info_loader.load()
logger.info("Docs loaded")

self_querying_store = ChromaCollection.get_collection(
    COLLECTION_NAME, PERSIST_DIRECTORY, EMBEDDING_FUNC, docs, override_collection_if_exists=True
)
# we still don't have a way to reset a chroma collection if it's already present but we want do add docs in the future
parrent_store = ChromaCollection.get_collection(
    CHILD_COLLECTION, PERSIST_DIRECTORY, EMBEDDING_FUNC, docs, override_collection_if_exists=True
)

company_info_collection = ChromaCollection.get_collection(
    COMPANY_COLLECTION, PERSIST_DIRECTORY, EMBEDDING_FUNC, company_docs, override_collection_if_exists=True
)

store = InMemoryStore()
logger.info("Obtained vector store")

company_info_retriever = company_info_collection.as_retriever()

child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
retriever = SetMergeRetrieverDirector.build_self_parrent(
    child_vectorstore=parrent_store,
    self_store=self_querying_store,
    store=store,
    child_splitter=child_splitter,
    parrent_docs=docs,
    company_info_retriever=company_info_retriever,
)
logger.info("Obtained retriever")


contextualize_q_system_prompt = """
You are an assistant that reformulates user questions into standalone questions based on the provided chat history.

<< Instructions >>:
- Take the Chat History and the User Question as input.
- If the User Question relies on the context of the Chat History, rewrite it as a standalone question that is fully understandable without referring to the Chat History.
- If the User Question is unrelated to the Chat History or does not need the context, return the User Question exactly as it is.

<< Input Format>> :
- Chat History: (context of prior conversation)
- User Question: (user's query)
<<Output Format>>:
- Standalone Question: (reformulated question or original query)

<< Example 1>>:
Chat History:
- User: What are some good Italian dishes to try?
- Assistant: Pasta carbonara, margherita pizza, and risotto are all popular options.

User Question: Are any of these gluten-free?

Standalone Question: Are any of pasta carbonara, margherita pizza, or risotto gluten-free?

<<Example 2>>:
Chat History:
- User: What are some benefits of daily exercise?
- Assistant: Improved cardiovascular health, better mood, and increased energy are some benefits.

User Question: How about yoga?

Standalone Question: What are the benefits of daily yoga practice?

<<Example 3>>:
Chat History:
- User: What’s the weather like in New York today?
- Assistant: It’s sunny with a high of 65°F.

User Question: What's the capital of France?

Standalone Question: What's the capital of France?

<<Example 4>>:
Chat History: (empty)

User Question: What's the time?

Standalone Question: What's the time?

<<Example 5>>:
Chat History:
- User: Which are the machines with stainless steel components?
- Assistant: According to the provided context, the machines with stainless steel components are:
    1. The "Over" machine has a stainless steel structure.
    2. The "Reverse" machine has external surfaces made of stainless steel, making it suitable for washing and sanitizing.
These are the only machines mentioned in the context with stainless steel components.

User Question: Give me more information about the Gemini RF machine please.

Standalone Question: Give me more information about the Gemini RF machine please."
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

system_prompt = (
    "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question."
    "If you don't find relevant information about your old answer in the following pieces of retrieved context don't apologize, just answer the new query."
    "If you don't know the answer, say that you don't know."
    "\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# chat_history = []

# question = "Which are the machines with stainless steel components?"
# ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
# chat_history.extend(
#     [
#         HumanMessage(content=question),
#         AIMessage(content=ai_msg_1["answer"]),
#     ]
# )
# logger.info(ai_msg_1["answer"])

# second_question = "Give me more information about the Gemini RF machine please."
# ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})
# chat_history.extend(
#     [
#         HumanMessage(content=second_question),
#         AIMessage(content=ai_msg_2["answer"]),
#     ]
# )
# logger.info(ai_msg_2["answer"])

# third_question = 'Give me all the details about the machine called "esse".'
# ai_msg_3 = rag_chain.invoke({"input": third_question, "chat_history": chat_history})
# chat_history.extend(
#     [
#         HumanMessage(content=third_question),
#         AIMessage(content=ai_msg_3["answer"]),
#     ]
# )

# logger.info(ai_msg_3["answer"])


### Statefully manage chat history ###

from typing import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict


# We define a dict representing the state of the application.
# This state has the same input and output keys as `rag_chain`.
class State(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: str


# We then define a simple node that runs the `rag_chain`.
# The `return` values of the node update the graph state, so here we just
# update the chat history with the input message and response.
def call_model(state: State):
    response = rag_chain.invoke(state)
    return {
        "chat_history": [
            HumanMessage(state["input"]),
            AIMessage(response["answer"]),
        ],
        "context": response["context"],
        "answer": response["answer"],
    }


# Our graph consists only of one node:
workflow = StateGraph(state_schema=State)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Finally, we compile the graph with a checkpointer object.
# This persists the state, in this case in memory.
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# "Which are the machines with stainless steel components?"
query = ""
config = {"configurable": {"thread_id": "abc123"}}

while query != "exit":
    query = input(">")
    result = app.invoke(
        {"input": query},
        config=config,
    )
    logger.info(result["answer"])
    logger.debug(result["context"])
