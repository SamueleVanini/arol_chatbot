from pathlib import Path
from doc_loader.transform_pipe import FromFileToText
from evaluation.evaluators import MultilabelEvaluator
from evaluation.pipeline import LangsmithEvaluator
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from icecream import ic
from langchain.storage import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers.multi_vector import SearchType
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_community.document_loaders import TextLoader

from core.logger import get_logger
from core.config import load_dotenv
from query_construction.self_querying import metadata_extraction
from service.file_loader_service import FileLoaderFactory, LoaderType
from service.llm_service import LlmFactory
from service.retriever_service import SetMergeRetrieverDirector
from vector_stores.chroma import ChromaCollection, custom_cosine_relevance_score_fn

load_dotenv()
logger = get_logger(__name__)

FILE_PATH = "./data/processed_catalog.json"
COLLECTION_NAME = "retrival_matches"
PERSIST_DIRECTORY = "./data"
COMPANY_INFO_FILE_PATH = "./data/company_info_cleaned.txt"

# Embedding function should get a class/function to get it?
EMBEDDING_FUNC = HuggingFaceEmbeddings(model_name="msmarco-distilbert-base-v4")
DATASET_NAME = "retrival_matches"
COMPANY_COLLECTION = "company_info"
# MODEL = "llama-3.1-70b-versatile"
MODEL = "llama3-8b-8192"

transformation_pipe = FromFileToText(text_docs_path=Path("./data/json_rewritten.csv"))
loader = FileLoaderFactory.get_loader(
    LoaderType.HYBRID,
    FILE_PATH,
    transformation_pipe=transformation_pipe,
    metadata_func=metadata_extraction,
    max_tokens=8192,
)
# loader = FileLoaderFactory.get_loader(LoaderType.JSON, FILE_PATH, metadata_func=metadata_extraction)
company_info_loader = TextLoader(COMPANY_INFO_FILE_PATH)
logger.info("File loader ready")

docs = loader.load()
company_docs = company_info_loader.load()
logger.info("Docs loaded")


self_querying_store = ChromaCollection.get_collection(
    COLLECTION_NAME, PERSIST_DIRECTORY, EMBEDDING_FUNC, docs, override_collection_if_exists=True
)

child_store = ChromaCollection.get_collection(
    collection_name="full_documents",
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=EMBEDDING_FUNC,
)
# we reset the collection to be sure to start from an empty one
child_store.reset_collection()

company_info_collection = ChromaCollection.get_collection(
    COMPANY_COLLECTION,
    PERSIST_DIRECTORY,
    EMBEDDING_FUNC,
    company_docs,
    override_collection_if_exists=True,
    relevance_score_fn=custom_cosine_relevance_score_fn,
)

store = InMemoryStore()
logger.info("Obtained vector store")

kwargs = {}
llm = LlmFactory.get_model(MODEL, temperature=0, max_tokens=8000)
kwargs["self_querying_model"] = llm


child_splitter = RecursiveCharacterTextSplitter(chunk_size=200)
# child_splitter = RecursiveJsonSplitter(max_chunk_size=200)
retriever = SetMergeRetrieverDirector.build_self_parrent(
    child_vectorstore=child_store,
    self_store=self_querying_store,
    store=store,
    child_splitter=child_splitter,
    parrent_docs=docs,
    **kwargs,
)
# parrent_search_kwargs = {"score_threshold": 0.4, "k": 23}
# retriever = ParentDocumentRetriever(
#     vectorstore=child_store,
#     docstore=store,
#     child_splitter=child_splitter,
#     search_kwargs=parrent_search_kwargs,
#     search_type=SearchType.similarity_score_threshold,
# )
# retriever.add_documents(docs, ids=None)

logger.info("Obtained retriever")

# print(retriever.invoke("Machines with stainless steel components", verbose=True))
# out = retriever.invoke("Machines with main market personal care")
# logger.info(out)

logger.info("Loading evaluation pipeline")

pipeline = LangsmithEvaluator()
pipeline.add_dataset(DATASET_NAME)
evaluator = MultilabelEvaluator()
pipeline.add_summary_evaluator(evaluator)
pipeline.set_target(retriever)
pipeline.results
logger.info(evaluator.get_report_str())
