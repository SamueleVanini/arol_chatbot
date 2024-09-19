from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
import re
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.runnables.history import RunnableWithMessageHistory


class LangChainBuilder:

    def get_template(self, template_type="chat"):

        def create_qa_template():
            system_prompt = (
                "You are an AI assistant acting as a sales agent for AROL company. "
                "Answer customer questions about products directly and concisely using the following information. "
                "Do not create a conversation or role-play as both agent and customer. "
                "If you don't know the answer, advise the customer to contact a human sales agent. "
                "\n\n"
                "{context}"
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}"),
                ]
            )
            return prompt

        def create_chat_template():
            system_prompt = (
                "You are an AI assistant acting as a sales agent for AROL company."
                "Answer customer questions about products directly and concisely using the following information. "
                "Do not create a conversation or role-play as both agent and customer. "
                "If you don't know the answer, advise the customer to contact a human sales agent. "
                "\n\n"
                "{context}"
            )
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )
            return qa_prompt

        if template_type == "chat":
            return create_chat_template()
        else:
            return create_qa_template()

    def response_parser(self, ai_message: dict) -> dict:
        # Access content from the dictionary
        cleaned = re.sub(r'^.*?(AI Assistant:|AI:)', '', ai_message['answer'], flags=re.DOTALL)
        # Trim any leading or trailing whitespace
        cleaned = cleaned.strip()
        ai_message['answer'] = cleaned
        return ai_message

    def create_rag_chain(self, llm, retriever, prompt):

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        return rag_chain

    def create_history_aware_chain(self, chain, history_session):
        return RunnableWithMessageHistory(
            chain,
            history_session,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
