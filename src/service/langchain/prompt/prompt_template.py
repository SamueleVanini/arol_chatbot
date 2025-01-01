from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from service.langchain.chain_configs import ChainType


def get_template(system_prompt: str, chain_type: ChainType) -> ChatPromptTemplate:
    if chain_type.value == ChainType.CHAT.value:
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
    else:  # QA template
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
