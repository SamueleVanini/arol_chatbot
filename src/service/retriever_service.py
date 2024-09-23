from enum import Enum, auto

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_core.runnables import Runnable


def create_vectorstore_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    return retriever


def get_history_aware_retriever(llm, retriever):
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    return history_aware_retriever


class RETRIEVER_TYPE(Enum):
    SELF_QUERYING = auto()
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
