from src.core.logger import get_logger
from src.core.config import configure_system

configure_system()

from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain.storage import InMemoryStore
from langchain.chains import create_history_aware_retriever
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_text_splitters import RecursiveCharacterTextSplitter
from service.retriever_service import SetMergeRetrieverDirector
from service.langchain.chain_configs import ChainType
from service.langchain.prompt.prebuilt_prompt import SystemPromptType, get_system_prompt
from service.langchain.prompt.prompt_template import get_template
from src.doc_loader.transform_pipe import FromFileToText
from src.query_construction.self_querying import metadata_extraction
from src.service.file_loader_service import FileLoaderFactory, LoaderType
from src.service.llm_service import LlmFactory
from src.service.langchain.langchain_builder_service import LangChainBuilder
from src.service.history_service import ChatHistoryFactory, MemoryType
from src.vector_stores.chroma import ChromaCollection

logger = get_logger(__name__)

FILE_PATH = "./data/processed_catalog.json"
COMPANY_INFO_FILE_PATH = "./data/company_info_cleaned.txt"
COLLECTION_NAME = "retrival_matches"
PERSIST_DIRECTORY = "./data"

# Embedding function should get a class/function to get it?
EMBEDDING_FUNC = HuggingFaceEmbeddings(model_name="msmarco-distilbert-base-v4")
DATASET_NAME = "retrival_matches"
CHILD_COLLECTION = "full_documents"
COMPANY_COLLECTION = "company_info"
MODEL = "llama3-8b-8192"

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

company_info_retriever = company_info_collection.as_retriever(
    search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.6, "k": 23}
)

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

llm_context = get_template(
    system_prompt=get_system_prompt(SystemPromptType.LLM_RETRIEVAL_WITH_HISTORY), chain_type=ChainType.CHAT
)

history_aware_retriever = create_history_aware_retriever(
    llm,
    retriever,
    llm_context,
)

builder = LangChainBuilder(MemoryType.LOCAL)

final_chain = builder.build_chain(llm, history_aware_retriever)

query = ""
config = {"configurable": {"thread_id": "abc123"}}

while query != "exit":
    query = input(">")
    result = final_chain.invoke({"input": query}, config={"configurable": {"session_id": "abc123"}})
    logger.info(result["answer"])
    logger.debug(result["context"])
