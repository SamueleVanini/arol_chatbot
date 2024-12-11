import sys
import os

# this is more of an hack than a solution, consider re-structure the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core.config import load_dotenv

load_dotenv()

from core.logger import get_logger
from evaluation.evaluators import FullChainAnswerPrecision
from evaluation.pipeline import LangsmithEvaluator
from langchain_community.document_loaders import TextLoader
from langchain.storage import InMemoryStore
from langchain.chains import create_history_aware_retriever

from langchain_text_splitters import RecursiveCharacterTextSplitter
from query_construction.self_querying import metadata_extraction
from vector_stores.chroma import custom_cosine_relevance_score_fn
from service.file_loader_service import FileLoaderFactory, LoaderType
from service.history_service import MemoryType
from service.indexing_serivce import (
    build_vector_store,
    build_vector_store_as_retriever,
    create_embeddings,
    get_embedding_function,
)
from service.langchain.langchain_builder_service import LangChainBuilder
from service.langchain.chain_configs import ChainType
from service.llm_service import LlmFactory
from service.retriever_service import (
    SetMergeRetrieverDirector,
    create_vectorstore_retriever,
    RetrieverFactory,
    RetrieverType,
)
from service.langchain.prompt.prompt_template import get_template
from service.langchain.prompt.prebuilt_prompt import get_system_prompt, SystemPromptType
from core.config import (
    PERSIST_DIRECTORY,
    JSON_MACHINES_FILE_PATH,
    MACHINE_PARAGRAPH,
    COMPANY_INFO_FILE_PATH,
    SELF_QUERYING_COLLECTION_NAME,
    PARRENT_DOCUMENT_COLLECTION,
    COMPANY_INFO_COLLECTION,
)
from doc_loader.transform_pipe import FromFileToText

# DATASET_NAME = "retrival_matches"
DATASET_NAME = "debug_ds"

logger = get_logger(__name__)

llm = LlmFactory.get_model("llama3-8b-8192", temperature=0)

transformation_pipe = FromFileToText(text_docs_path=MACHINE_PARAGRAPH)

machines_hybrid_loader = FileLoaderFactory.get_loader(
    LoaderType.HYBRID,
    JSON_MACHINES_FILE_PATH,
    transformation_pipe=transformation_pipe,
    metadata_func=metadata_extraction,
    max_tokens=8192,
)
company_info_loader = TextLoader(COMPANY_INFO_FILE_PATH)

machines_docs = machines_hybrid_loader.load()
company_docs = company_info_loader.load()

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
company_info_retriever = build_vector_store_as_retriever(
    COMPANY_INFO_COLLECTION,
    PERSIST_DIRECTORY,
    embedding_function,
    company_docs,
    custom_cosine_relevance_score_fn,
    retriever_kwargs={
        "search_type": "similarity_score_threshold",
        # "search_kwargs": {"score_threshold": 0.6, "k": 1},
        "search_kwargs": {"score_threshold": 0.6},
    },
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
    company_info_retriever=company_info_retriever,
)

chain_builder = LangChainBuilder(memory_type=MemoryType.NONE)

final_chain = chain_builder.build_chain(llm, retriever)

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

pipeline = LangsmithEvaluator()
pipeline.add_dataset(DATASET_NAME)
evaluator = FullChainAnswerPrecision(machines)
pipeline.add_summary_evaluator(evaluator)
pipeline.set_target(final_chain, use_dict_input=True)
pipeline.results
logger.info(evaluator.get_report_str())
