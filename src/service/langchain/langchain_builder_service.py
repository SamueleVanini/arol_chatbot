import re

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.service.history_service import ChatHistoryFactory, MemoryType
from .chain_configs import ChainType
from .prompt.prebuilt_prompt import get_system_prompt, SystemPromptType
from .prompt.prompt_template import get_template


class LangChainBuilder:

    def __init__(self, memory_type: MemoryType = MemoryType.REDIS):
        if not isinstance(memory_type, MemoryType):
            raise ValueError(f"memory_type must be a MemoryType, got {type(memory_type)}")
        self.memory_type = memory_type
        if self.memory_type == MemoryType.NONE:
            self.chain_type = ChainType.QA
        else:
            self.chain_type = ChainType.CHAT

    @staticmethod
    def response_parser(ai_message: dict) -> dict:
        cleaned = re.sub(r"^.*?(AI Assistant:|AI:)", "", ai_message["answer"], flags=re.DOTALL)
        cleaned = cleaned.strip()
        ai_message["answer"] = cleaned
        return ai_message

    # shared_state is now a dictionary with 3 key: "input", "chat_history", "context"
    def chain_selection(self, shared_state):
        if shared_state["context"]:
            return self.question_answer_chain
        return self.default_answer_chain

    def create_rag_chain(self, llm, retriever, is_test: bool = False):
        if self.memory_type == MemoryType.NONE:
            chain_type = ChainType.QA
        else:
            chain_type = ChainType.CHAT

        if is_test:
            question_answer_prompt = get_template(
                system_prompt=get_system_prompt(prompt_type=SystemPromptType.CHAT_EVAL), chain_type=chain_type
            )
        else:
            question_answer_prompt = get_template(
                system_prompt=get_system_prompt(prompt_type=SystemPromptType.CHAT_V2), chain_type=chain_type
            )

        no_answer_prompt = get_template(
            system_prompt=get_system_prompt(prompt_type=SystemPromptType.NO_ANSWER), chain_type=chain_type
        )

        output_parser = StrOutputParser()

        self.question_answer_chain = create_stuff_documents_chain(llm, question_answer_prompt)
        self.default_answer_chain = no_answer_prompt | llm | output_parser
        # rag_chain = create_retrieval_chain(retriever, self.question_answer_chain)
        rag_chain = create_retrieval_chain(retriever, RunnableLambda(self.chain_selection))
        return rag_chain | self.response_parser
        # return rag_chain

    def build_chain(self, llm, retriever, is_test: bool = False):
        chain = self.create_rag_chain(llm, retriever, is_test)
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
