from enum import Enum, auto

_system_prompt: dict[str, str] = {
    "llm_retrieval_with_history": (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    ),
    "self-querying_with_metadata": (
        "You are an expert at converting user questions into database queries."
        "You have access to a database of customised capping machines for any closure need in json format."
        "Given a question, return a database query optimized to retrieve the most relevant results."
        "If there are acronyms or words you are not familiar with, do not try to rephrase them."),

    "chat": (
        "You are an AI assistant acting as a sales agent for AROL company."
        "Answer customer questions about products directly and concisely using the following information."
        "Do not create a conversation or role-play as both agent and customer."
        "If you don't know the answer, advise the customer to contact a human sales agent."
        "\n\n"
        "{context}"
    ),
    "metadata_extractor": (
        "Given the following JSON data about industrial machines:"
        "\n"
        " {json_data}"
        "\n"
        " Please provide the following information:"
        " 1. The total number of machines described in this data."
        " 2. Names of all the machines present in the data."
        " 3. The general categories or types of machines present (e.g., cappers, corkers, etc.)."
        " 4. A brief summary of the main markets these machines serve."
        " Respond with clear, concise bullet points."
        " generate the result in a json format"

    )
}


class SystemPromptType(Enum):
    LLM_RETRIEVAL_WITH_HISTORY = "llm_retrieval_with_history"
    SELF_QUERY_WITH_METADATA = "self-querying_with_metadata"
    CHAT = "chat"
    METADATA_EXTRACTOR = "metadata_extractor"


def get_system_prompt(prompt_type: SystemPromptType) -> str:
    return _system_prompt.get(prompt_type.value, "Prompt type not found")
