import re
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.service.history_service import ChatHistoryFactory, MemoryType
from .chain_configs import ChainType
from .prompt.prompt_template import get_template
from .prompt.prebuilt_prompt import get_system_prompt, SystemPromptType


class LangChainBuilder:

    def __init__(self, memory_type: MemoryType = MemoryType.REDIS):
        if not isinstance(memory_type, MemoryType):
            raise ValueError(f"memory_type must be a MemoryType, got {type(memory_type)}")
        self.memory_type = memory_type

    @staticmethod
    def response_parser(ai_message: dict) -> dict:
        cleaned = re.sub(r"^.*?(AI Assistant:|AI:)", "", ai_message["answer"], flags=re.DOTALL)
        cleaned = cleaned.strip()
        ai_message["answer"] = cleaned
        return ai_message

    def create_rag_chain(self, llm, retriever):
        if self.memory_type == MemoryType.NONE:
            chain_type = ChainType.QA
        else:
            chain_type = ChainType.CHAT

        prompt = get_template(
            system_prompt=get_system_prompt(prompt_type=SystemPromptType.CHAT_TEST), chain_type=chain_type
        )

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        return rag_chain | self.response_parser

    def build_chain(self, llm, retriever):
        chain = self.create_rag_chain(llm, retriever)
        if self.memory_type == MemoryType.NONE:
            return chain

        history_session = ChatHistoryFactory.get_chat_history(memory_type=self.memory_type)
        return RunnableWithMessageHistory(
            chain,
            history_session,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
