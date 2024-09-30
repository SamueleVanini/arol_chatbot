from os.path import expanduser
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_groq import ChatGroq


def create_llm_model(is_local=False, local_path: str | None = None): #based on groq
    def create_local_llm(model_path: str):
        model_path = expanduser(model_path) #expanduser: Expand the path to the user's home directory

        llm = LlamaCpp(
            model_path=model_path,
            n_ctx=4096, #n_ctx: The number of tokens in the context window
            max_tokens=1024, #max_tokens: The maximum number of tokens to generate
            temperature=0.65, #temperature: The temperature of the sampling distribution
            verbose=True #verbose: Whether to print debug information
        )
        return llm #llama cpp 

    def create_groq_llm(model="llama3-8b-8192"):
        llm = ChatGroq(model=model)
        return llm

    if is_local:
        return create_local_llm(local_path)
    else:
        return create_groq_llm()
