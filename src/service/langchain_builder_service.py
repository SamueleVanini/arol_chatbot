from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
import re
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from .history_service import get_local_session_history, get_redis_history
from enum import Enum, auto


class ChainType(Enum):
    CHAT = auto()
    QA = auto()


class MemoryType(Enum):
    NONE = auto()
    LOCAL = auto()
    REDIS = auto()


class LangChainBuilder:
    def __init__(self, chain_type: ChainType = ChainType.CHAT, memory_type: MemoryType = MemoryType.REDIS):
        if not isinstance(chain_type, ChainType):
            raise ValueError(f"chain_type must be a ChainType, got {type(chain_type)}")
        if not isinstance(memory_type, MemoryType):
            raise ValueError(f"memory_type must be a MemoryType, got {type(memory_type)}")

        self.chain_type = chain_type
        self.memory_type = memory_type

    def get_template(self):
        system_prompt = (
            "You are an AI assistant acting as a sales agent for AROL company. "
            "Answer customer questions about products directly and concisely using the following information. "
            "Do not create a conversation or role-play as both agent and customer. "
            "If you don't know the answer, advise the customer to contact a human sales agent. "
            "\n\n"
            "{context}"
        )

        if self.chain_type == ChainType.CHAT:
            return ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
        else:  # QA template
            return ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])

    def response_parser(self, ai_message: dict) -> dict:
        cleaned = re.sub(r'^.*?(AI Assistant:|AI:)', '', ai_message['answer'], flags=re.DOTALL)
        cleaned = cleaned.strip()
        ai_message['answer'] = cleaned
        return ai_message

    def create_rag_chain(self, llm, retriever):
        prompt = self.get_template()
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        return rag_chain | self.response_parser

    def build_chain(self, llm, retriever):
        chain = self.create_rag_chain(llm, retriever)

        if self.memory_type != MemoryType.NONE:
            is_local = self.memory_type == MemoryType.LOCAL
            if is_local:
                history_session = get_local_session_history
            else:
                history_session = get_redis_history
            return RunnableWithMessageHistory(
                chain,
                history_session,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )

        return chain
