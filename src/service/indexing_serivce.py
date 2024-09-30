from langchain_chroma import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_embeddings(docs, split=False):
    if split:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0) #chunk_size: The size of each chunk in characters
        docs = text_splitter.split_documents(docs) #split_documents: Split a list of documents into chunks
    model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1" #model_name: The name of the model to use
    model_kwargs = {'device': 'cpu'}                                #model_kwargs: Keyword arguments to pass to the model
    encode_kwargs = {'normalize_embeddings': True}              #encode_kwargs: Keyword arguments to pass to the encode method
    hf_embeddings = HuggingFaceEmbeddings(                      #HuggingFaceEmbeddings: A class for using Hugging Face models
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    vectorstore = Chroma.from_documents(documents=docs, embedding=hf_embeddings)    #Chroma.from_documents: Create a vectorstore from a list of documents
    return vectorstore
