from .file_loader_service import FileLoaderFactory, LoaderType
from .history_service import MemoryType
from .indexing_serivce import create_embeddings
from .langchain.langchain_builder_service import LangChainBuilder
from .langchain.chain_configs import ChainType
from .llm_service import LlmFactory
from .retriever_service import create_vectorstore_retriever, RetrieverFactory, RetrieverType
from .langchain.prompt.prompt_template import get_template
from .langchain.prompt.prebuilt_prompt import get_system_prompt, SystemPromptType
import os


class ArolChatBot:
    @staticmethod
    async def initialize_chat_bot():
        llm = LlmFactory.get_model("llama3-8b-8192", temperature=0)

        docs = FileLoaderFactory.get_loader(loader_type=LoaderType.JSON, file_path="data/processed_catalog.json").load()
        # docs = FileLoaderFactory.get_loader(loader_type=LoaderType.JSON, file_path="processed_catalog.json").load()
        indexing = create_embeddings(docs=docs)
        retriever = create_vectorstore_retriever(indexing)

        history_aware_retriever = RetrieverFactory.get_retriever(
            retriever_type=RetrieverType.HISTORY_AWARE,
            llm=llm,
            store=retriever,
            llm_context=get_template(
                system_prompt=get_system_prompt(SystemPromptType.LLM_RETRIEVAL_WITH_HISTORY),
                chain_type=ChainType.CHAT
            )
        )
        # Initialize the builder with desired options
        # ChainType: An enumeration of the types of chains
        chain_builder = LangChainBuilder(memory_type=MemoryType.REDIS)

        # Build the chain
        final_chain = chain_builder.build_chain(llm, history_aware_retriever)

        return final_chain
