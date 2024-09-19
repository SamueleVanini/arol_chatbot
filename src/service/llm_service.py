from os.path import expanduser
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_groq import ChatGroq


def create_llm_model(is_local=False, local_path: str | None = None):
    def create_local_llm(model_path: str):
        model_path = expanduser(model_path)

        llm = LlamaCpp(
            model_path=model_path,
            n_ctx=4096,
            max_tokens=1024,
            temperature=0.65,
            verbose=True
        )
        return llm

    def create_groq_llm(model="llama3-8b-8192"):
        llm = ChatGroq(model=model)
        return llm

    if is_local:
        return create_local_llm(local_path)
    else:
        return create_groq_llm()
