from abc import ABC, abstractmethod
from typing import Optional

from service.langchain.chain_configs import ChainType
from service.langchain.prompt.prebuilt_prompt import get_system_prompt, SystemPromptType
from service.langchain.prompt.prompt_template import get_template
from src.query_construction.self_querying import metadata_extraction
from src.service.file_loader_service import FileLoaderFactory, LoaderType
from src.service.indexing_serivce import create_embeddings
from src.service.langchain.langchain_builder_service import LangChainBuilder
from src.service.retriever_service import create_vectorstore_retriever, RetrieverFactory, RetrieverType


class RoutableChainFactory(ABC):
    def __init__(self, name: str, llm, file_path: str, chain_builder: LangChainBuilder):
        if not name:
            raise ValueError("Chain must have a valid name")
        if not file_path:
            raise ValueError("Chain must have a valid file path")
        if not llm:
            raise ValueError("Chain must have a valid LLM model")

        self.name = name
        self.llm = llm
        self.file_path = file_path
        self.default_chain = chain_builder
        self.main_chain = None

    @abstractmethod
    def build_chain(self) -> "RoutableChainFactory":
        """Each chain will implement its own pipeline and return `self`."""
        pass

class CatalogChain(RoutableChainFactory):
    def __init__(self, name: str, llm, file_path: str,chain_builder:LangChainBuilder):
        super().__init__(name, llm, file_path,chain_builder)

    def build_chain(self) -> "RoutableChainFactory":
        docs = (FileLoaderFactory.get_loader(loader_type=LoaderType.JSON,
                                             file_path=self.file_path,
                                             metadata_func=metadata_extraction)).load()

        indexing = create_embeddings(docs=docs)
        retriever = create_vectorstore_retriever(indexing)
        history_aware_retriever = RetrieverFactory.get_retriever(
            retriever_type=RetrieverType.HISTORY_AWARE,
            llm=self.llm,
            store=retriever,
            llm_context=get_template(
                system_prompt=get_system_prompt(SystemPromptType.LLM_RETRIEVAL_WITH_HISTORY),
                chain_type=ChainType.CHAT
            )
        )
        self.main_chain = self.default_chain.build_chain(self.llm, history_aware_retriever)
        return self


class CompanyChain(RoutableChainFactory):
    def __init__(self, name: str, llm, file_path: str, chain_builder: LangChainBuilder):
        super().__init__(name, llm, file_path, chain_builder)

    def build_chain(self) -> "RoutableChainFactory":
        docs = (FileLoaderFactory.get_loader(loader_type=LoaderType.JSON, file_path=self.file_path)).load()

        indexing = create_embeddings(
            docs=docs,
            collection_name="company_indexing",
            persist_directory="./chroma_company_indexing"
        )

        retriever = create_vectorstore_retriever(indexing)
        history_aware_retriever = RetrieverFactory.get_retriever(
            retriever_type=RetrieverType.HISTORY_AWARE,
            llm=self.llm,
            store=retriever,
            llm_context=get_template(
                system_prompt=get_system_prompt(SystemPromptType.LLM_RETRIEVAL_WITH_HISTORY),
                chain_type=ChainType.CHAT
            )
        )
        self.main_chain = self.default_chain.build_chain(self.llm, history_aware_retriever)
        return self
