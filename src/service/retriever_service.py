from enum import Enum, auto

from langchain.chains import create_history_aware_retriever
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain_core.vectorstores import VectorStore


def create_vectorstore_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    return retriever


class RetrieverType(Enum):
    SELF_QUERYING = auto()
    HISTORY_AWARE = auto()


class RetrieverFactory:

    @classmethod
    def get_retriever(
            cls,
            retriever_type: RetrieverType,
            llm: BaseLanguageModel,
            store: VectorStore | BaseRetriever,
            llm_context: str | ChatPromptTemplate,
            *input,
            **kwargs,
    ) -> Runnable:
        match retriever_type:
            case RetrieverType.SELF_QUERYING:
                if not isinstance(store, VectorStore):
                    raise ValueError("Store object must be a VectorStore for self-querying retrieval")
                # we should check for all the variation of the parameters type, think if it is not better to change the pattern...
                return SelfQueryRetriever.from_llm(llm, store, llm_context, *input, **kwargs)  # type: ignore
            case RetrieverType.HISTORY_AWARE:
                if not isinstance(store, BaseRetriever):
                    raise ValueError("Store object must be a BaseRetriever for HISTORY_AWARE retrieval")
                return create_history_aware_retriever(llm, store, llm_context, *input, **kwargs)
