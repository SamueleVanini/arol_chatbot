from enum import Enum, auto
from typing import Dict, Optional

from langchain_core.runnables import Runnable
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers.multi_vector import SearchType
from langchain_text_splitters import TextSplitter
from langchain_core.stores import BaseStore
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain_core.documents import Document

from query_construction.self_querying import DOCUMENT_CONTENT_DESCRIPTION, METADATA_FIELD_INFO
from service.llm_service import LlmFactory
from retriever.set_merger_retriever import SetMergerRetriever


def create_vectorstore_retriever(vectorstore):
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 20}
    )  # as_retriever: Convert the vectorstore to a retriever
    return retriever


def get_history_aware_retriever(llm, retriever):
    contextualize_q_system_prompt = (  # contextualize_q_system_prompt: The system prompt for the contextualize_q_prompt
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(  # ChatPromptTemplate: A class for creating chat prompts
        [
            (
                "system",
                contextualize_q_system_prompt,
            ),  # contextualize_q_system_prompt: The system prompt for the contextualize_q_prompt
            MessagesPlaceholder("chat_history"),  # MessagesPlaceholder: A class for creating placeholders for messages
            ("human", "{input}"),  # input: The input to the model
        ]
    )
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    return history_aware_retriever


class RETRIEVER_TYPE(Enum):
    SELF_QUERYING = auto()
    PARENT_DOC = auto()
    HISTORY_AWARE = auto()


class RetrieverFactory:

    @classmethod
    def get_retriever(
        cls,
        retriever_type: RETRIEVER_TYPE,
        llm: BaseLanguageModel,
        store: VectorStore | BaseRetriever,
        llm_context: str | ChatPromptTemplate,
        *input,
        **kwargs,
    ) -> Runnable:
        match retriever_type:
            case RETRIEVER_TYPE.SELF_QUERYING:
                if not isinstance(store, VectorStore):
                    raise ValueError("Store object must be a VectorStore for self-querying retrieval")
                # we should check for all the variation of the parameters type, think if it is not better to change the pattern...
                return SelfQueryRetriever.from_llm(llm, store, llm_context, *input, **kwargs)  # type: ignore
            case RETRIEVER_TYPE.HISTORY_AWARE:
                return create_history_aware_retriever(llm, store, llm_context, *input, **kwargs)


class SetMergeRetrieverDirector:

    @classmethod
    def build_self_parrent(
        cls,
        child_vectorstore: VectorStore,
        self_store: VectorStore,
        store: BaseStore,
        child_splitter: TextSplitter,
        parrent_docs: list[Document],
        search_type: SearchType = SearchType.similarity_score_threshold,
        parrent_search_kwargs: Optional[Dict] = None,
        *input,
        **kwargs,
    ) -> SetMergerRetriever:
        if parrent_search_kwargs is None:
            parrent_search_kwargs = {"score_threshold": 0.4, "k": 23}
        parent = ParentDocumentRetriever(
            vectorstore=child_vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            search_kwargs=parrent_search_kwargs,
            search_type=search_type,
        )
        parent.add_documents(parrent_docs, ids=None)
        llm = kwargs.pop("self_querying_model", None)
        if llm is None:
            llm = LlmFactory.get_model("llama3-8b-8192", temperature=0)
        self_quering = RetrieverFactory.get_retriever(
            RETRIEVER_TYPE.SELF_QUERYING,
            llm,
            self_store,
            DOCUMENT_CONTENT_DESCRIPTION,
            metadata_field_info=METADATA_FIELD_INFO,
            structured_query_translator=ChromaTranslator(),
            use_original_query=True,
            verbose=True,
            # enable limit will set the k for the chroma search (default value is 10, find out how to modify it)
            # enable_limit=True,
        )

        return SetMergerRetriever(retrievers=[parent, self_quering])  # type: ignore
