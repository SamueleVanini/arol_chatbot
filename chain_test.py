from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from service.retriever_service import RETRIEVER_TYPE, RetrieverFactory


from src.core.config import configure_system
from src.query_construction.self_querying import metadata_extraction, DOCUMENT_CONTENT_DESCRIPTION, METADATA_FIELD_INFO
from src.service.llm_service import LlmFactory

TEST_FILE = "./data/machines_test_files.json"

configure_system()

loader = JSONLoader(file_path=TEST_FILE, jq_schema=".[]", text_content=False, metadata_func=metadata_extraction)
documents = loader.load()

embedding_function = HuggingFaceEmbeddings(model_name="msmarco-distilbert-base-v4")

vectorstore = Chroma.from_documents(documents, embedding_function)

llm = LlmFactory.get_model("llama3-8b-8192", temperature=0)

retriever = RetrieverFactory.get_retriever(
    RETRIEVER_TYPE.SELF_QUERYING,
    llm,
    vectorstore,
    DOCUMENT_CONTENT_DESCRIPTION,
    metadata_field_info=METADATA_FIELD_INFO,
    structured_query_translator=ChromaTranslator(),
)

print(retriever.invoke("What are the machines with at least 72000 caps closed per hour?"))
