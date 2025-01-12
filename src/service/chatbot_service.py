from langchain_community.document_loaders import TextLoader
from langchain.storage import InMemoryStore
from langchain.chains import create_history_aware_retriever

from langchain_text_splitters import RecursiveCharacterTextSplitter
from query_construction.self_querying import metadata_extraction
from vector_stores.chroma import custom_cosine_relevance_score_fn
from .file_loader_service import FileLoaderFactory, LoaderType
from .history_service import MemoryType
from .indexing_serivce import (
    build_vector_store,
    build_vector_store_as_retriever,
    create_embeddings,
    get_embedding_function,
)
from .langchain.langchain_builder_service import LangChainBuilder
from .langchain.chain_configs import ChainType
from .llm_service import LlmFactory
from .retriever_service import SetMergeRetrieverDirector, create_vectorstore_retriever, RetrieverFactory, RetrieverType
from .langchain.prompt.prompt_template import get_template
from .langchain.prompt.prebuilt_prompt import get_system_prompt, SystemPromptType
from core.config import (
    PERSIST_DIRECTORY,
    JSON_MACHINES_FILE_PATH,
    MACHINE_PARAGRAPH,
    COMPANY_INFO_FILE_PATH,
    COMPANY_INFO_2_FILE_PATH,
    SELF_QUERYING_COLLECTION_NAME,
    PARRENT_DOCUMENT_COLLECTION,
    COMPANY_INFO_COLLECTION,
)
from doc_loader.transform_pipe import FromFileToText

import os


class ArolChatBot:

    @staticmethod
    async def initialize_chat_bot():
        llm = LlmFactory.get_model("llama3-8b-8192", temperature=0)

        transformation_pipe = FromFileToText(text_docs_path=MACHINE_PARAGRAPH)

        machines_hybrid_loader = FileLoaderFactory.get_loader(
            LoaderType.HYBRID,
            JSON_MACHINES_FILE_PATH,
            transformation_pipe=transformation_pipe,
            metadata_func=metadata_extraction,
            max_tokens=8192,
        )
        company_info_loader = TextLoader(COMPANY_INFO_2_FILE_PATH)

        machines_docs = machines_hybrid_loader.load()
        company_docs = company_info_loader.load()

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

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
        company_docs_splitted = text_splitter.split_documents(company_docs)

        company_info_retriever = build_vector_store_as_retriever(
            COMPANY_INFO_COLLECTION,
            PERSIST_DIRECTORY,
            embedding_function,
            company_docs_splitted,
            custom_cosine_relevance_score_fn,
            retriever_kwargs={
                "search_type": "similarity_score_threshold",
                # "search_kwargs": {"score_threshold": 0.6, "k": 1},
                "search_kwargs": {"score_threshold": 0.2},
            },
        )

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

        llm_context = get_template(
            system_prompt=get_system_prompt(SystemPromptType.LLM_RETRIEVAL_WITH_HISTORY), chain_type=ChainType.RETRIEVER
        )

        history_aware_retriever = create_history_aware_retriever(
            llm,
            retriever,
            llm_context,
        )

        #### OLD CODE

        # docs = FileLoaderFactory.get_loader(loader_type=LoaderType.JSON, file_path="data/processed_catalog.json").load()
        # # docs = FileLoaderFactory.get_loader(loader_type=LoaderType.JSON, file_path="processed_catalog.json").load()
        # indexing = create_embeddings(docs=docs)
        # retriever = create_vectorstore_retriever(indexing)

        # history_aware_retriever = RetrieverFactory.get_retriever(
        #     retriever_type=RetrieverType.HISTORY_AWARE,
        #     llm=llm,
        #     store=retriever,
        #     llm_context=get_template(
        #         system_prompt=get_system_prompt(SystemPromptType.LLM_RETRIEVAL_WITH_HISTORY), chain_type=ChainType.CHAT
        #     ),
        # )
        # Initialize the builder with desired options
        # ChainType: An enumeration of the types of chains
        chain_builder = LangChainBuilder(memory_type=MemoryType.REDIS)

        # Build the chain
        final_chain = chain_builder.build_chain(llm, history_aware_retriever)

        return final_chain
