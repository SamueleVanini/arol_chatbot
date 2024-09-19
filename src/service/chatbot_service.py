from .llm_service import create_llm_model
from .file_loader_service import file_loader
from .indexing_serivce import create_embeddings
from .retriever_service import create_vectorstore_retriever, get_history_aware_retriever
from .langchain_builder_service import LangChainBuilder
from .history_service import connect_history_session
from core.config import configure_system


class ArolChatBot:
    async def initialize_chat_bot(self):
        configure_system()
        llm = create_llm_model()
        docs = file_loader(file_path="src/backend/processed_catalog.json", loader_model="json")
        indexing = create_embeddings(docs=docs)
        retriever = create_vectorstore_retriever(indexing)
        history_aware_retriever = get_history_aware_retriever(llm=llm, retriever=retriever)
        chain_builder = LangChainBuilder()
        prompt_template = chain_builder.get_template(template_type="chat")
        rag_chain = chain_builder.create_rag_chain(llm=llm, retriever=history_aware_retriever, prompt=prompt_template)
        rag_chain_with_parser = rag_chain | chain_builder.response_parser
        history_aware_chain = chain_builder.create_history_aware_chain(
            chain=rag_chain_with_parser,
            history_session=connect_history_session
        )
        return history_aware_chain
