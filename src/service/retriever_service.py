from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate


def create_vectorstore_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={'k': 20}) #as_retriever: Convert the vectorstore to a retriever
    return retriever


def get_history_aware_retriever(llm, retriever):
    contextualize_q_system_prompt = (          #contextualize_q_system_prompt: The system prompt for the contextualize_q_prompt
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages( #ChatPromptTemplate: A class for creating chat prompts
        [
            ("system", contextualize_q_system_prompt), #contextualize_q_system_prompt: The system prompt for the contextualize_q_prompt
            MessagesPlaceholder("chat_history"), #MessagesPlaceholder: A class for creating placeholders for messages
            ("human", "{input}"), #input: The input to the model
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever
