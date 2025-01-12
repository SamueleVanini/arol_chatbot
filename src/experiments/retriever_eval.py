import os
import sys

# this is more of an hack than a solution, consider re-structure the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core.config import load_dotenv

load_dotenv()

from core.logger import get_logger
from evaluation.evaluators import MultilabelEvaluator
from evaluation.pipeline import LangsmithEvaluator
from langchain_community.document_loaders import TextLoader
from langchain.storage import InMemoryStore

from langchain_text_splitters import RecursiveCharacterTextSplitter
from query_construction.self_querying import metadata_extraction
from vector_stores.chroma import custom_cosine_relevance_score_fn
from service.file_loader_service import FileLoaderFactory, LoaderType
from src.service.history_service import MemoryType
from service.indexing_serivce import (
    build_vector_store,
    build_vector_store_as_retriever,
    get_embedding_function,
)
from service.langchain.langchain_builder_service import LangChainBuilder
from service.llm_service import LlmFactory
from service.retriever_service import (
    SetMergeRetrieverDirector,
)
from core.config import (
    PERSIST_DIRECTORY,
    JSON_MACHINES_FILE_PATH,
    MACHINE_PARAGRAPH,
    SELF_QUERYING_COLLECTION_NAME,
    PARRENT_DOCUMENT_COLLECTION,
)
from doc_loader.transform_pipe import FromFileToText

DATASET_NAME = "retrival_matches"
# DATASET_NAME = "debug_ds"

logger = get_logger(__name__)

kwargs = {}
llm = LlmFactory.get_model("llama3-8b-8192", temperature=0, max_tokens=8000)
kwargs["self_querying_model"] = llm

transformation_pipe = FromFileToText(text_docs_path=MACHINE_PARAGRAPH)

machines_hybrid_loader = FileLoaderFactory.get_loader(
    LoaderType.HYBRID,
    JSON_MACHINES_FILE_PATH,
    transformation_pipe=transformation_pipe,
    metadata_func=metadata_extraction,
    max_tokens=8192,
)

machines_docs = machines_hybrid_loader.load()

logger.info("Finished to load files")

embedding_function = get_embedding_function()

self_querying_store = build_vector_store(
    SELF_QUERYING_COLLECTION_NAME,
    PERSIST_DIRECTORY,
    embedding_function,
    machines_docs,
    custom_cosine_relevance_score_fn,
)

parrent_vector_store = build_vector_store(
    PARRENT_DOCUMENT_COLLECTION,
    PERSIST_DIRECTORY,
    embedding_function,
    machines_docs,
    custom_cosine_relevance_score_fn,
)

logger.info("Obtained vector store")

parrent_store = InMemoryStore()

child_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=100)
retriever = SetMergeRetrieverDirector.build_self_parrent(
    child_vectorstore=parrent_vector_store,  # type: ignore
    self_store=self_querying_store,
    store=parrent_store,
    child_splitter=child_splitter,
    parrent_docs=machines_docs,
    company_info_retriever=None,
    **kwargs,
)

chain_builder = LangChainBuilder(memory_type=MemoryType.NONE)

final_chain = chain_builder.build_chain(llm, retriever, is_test=True)

logger.info("Chain constructed")

machines = machine_names = [
    "euro pk",
    "next",
    "eagle pk",
    "euro vp",
    "eagle vp",
    "geyser",
    "euro dd",
    "equatorque",
    "euro pp-c",
    "euro pp-g",
    "kamma pkv",
    "eagle pp",
    "euro va-cb",
    "euro va",
    "euro vpa",
    "eagle va",
    "esse",
    "esse pk",
    "eagle c",
    "quasar r",
    "quasar f",
    "quasar rf",
    "saturno r",
    "saturno f",
    "saturno rf",
    "gemini r",
    "gemini f",
    "gemini rf",
    "la champenoise",
    "reverse",
    "over",
]

logger.info("Loading evaluation pipeline")

pipeline = LangsmithEvaluator()
pipeline.add_dataset(DATASET_NAME)
evaluator = MultilabelEvaluator()
pipeline.add_summary_evaluator(evaluator)
pipeline.set_target(retriever)

try:
    results = pipeline.results
    if results:
        logger.info(evaluator.get_report_str())
    else:
        logger.error("Evaluation did not complete successfully")
except Exception as e:
    logger.error(f"Error during evaluation: {str(e)}")
