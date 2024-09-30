from core.config import configure_system
from .file_loader_service import file_loader
from .indexing_serivce import create_embeddings
from .langchain_builder_service import LangChainBuilder, ChainType, MemoryType
from .llm_service import create_llm_model
from .retriever_service import create_vectorstore_retriever, get_history_aware_retriever


class ArolChatBot:
    async def initialize_chat_bot(self):
        configure_system()
        llm = create_llm_model()
        docs = file_loader(file_path="src/backend/processed_catalog.json", loader_model="json")
        indexing = create_embeddings(docs=docs)
        retriever = create_vectorstore_retriever(indexing)
        history_aware_retriever = get_history_aware_retriever(llm=llm, retriever=retriever)
        # Initialize the builder with desired options
        chain_builder = LangChainBuilder(chain_type=ChainType.CHAT, memory_type=MemoryType.REDIS) #ChainType: An enumeration of the types of chains

        # Build the chain
        final_chain = chain_builder.build_chain(llm, history_aware_retriever)

        return final_chain
