from pathlib import Path
from typing import Any, Callable, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever

from vector_stores.chroma import ChromaCollection


def create_embeddings(
    docs, collection_name: str = "catalog_indexing", persist_directory: str = "./chroma_catalog_indexing", split=False
):
    if split:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=0
        )  # chunk_size: The size of each chunk in characters
        docs = text_splitter.split_documents(docs)  # split_documents: Split a list of documents into chunks
    model_name = "sentence-transformers/multi-qa-mpnet-base-dot-v1"  # model_name: The name of the model to use
    model_kwargs = {"device": "cpu"}  # model_kwargs: Keyword arguments to pass to the model
    encode_kwargs = {"normalize_embeddings": True}  # encode_kwargs: Keyword arguments to pass to the encode method
    hf_embeddings = HuggingFaceEmbeddings(  # HuggingFaceEmbeddings: A class for using Hugging Face models
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )
    vectorstore = ChromaCollection.get_collection(
        collection_name=collection_name,
        persist_directory=persist_directory,
        embedding_function=hf_embeddings,
        documents=docs,
    )  # Chroma.from_documents: Create a vectorstore from a list of documents
    return vectorstore


def get_embedding_function(
    model_name: str = "msmarco-distilbert-base-v4",
    model_kwargs: Optional[dict] = {"device": "cpu"},
    encode_kwargs: Optional[dict] = {"normalize_embeddings": True},
):
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)


def build_vector_store(
    collection_name: str,
    persist_directory: Optional[str],
    embedding_function: Embeddings,
    docs: list[Document],
    relevance_score_fn: Callable[[float], float],
) -> VectorStore:
    """Build or retrieve a vector_store based on Chroma

    Args:
        collection_name (str): name of the collection to create or retrieve
        persist_directory (Optional[str]): path where to store the collection. If None the collection is in memory only
        embedding_function (): embedding function used to create vectors from documents
        docs (list[Document]): documents to store
        relevance_score_fn (Callable[[float], float]): function to normalize Chroma's similarity distance (from range [0,2]) to range [0,1]
        retriever_kwargs (Optional[dict[str, Any]], optional): arguments for the vector_store as retriever (e.g. search_type and search_kwargs). If get_as_retriever is set to False the argument is ignored. Defaults to None.

    Returns:
        Chroma: Chroma vector store
    """
    vector_store = ChromaCollection.get_collection(
        collection_name,
        persist_directory,
        embedding_function,
        docs,
        override_collection_if_exists=True,
        relevance_score_fn=relevance_score_fn,
    )

    return vector_store


def build_vector_store_as_retriever(
    collection_name: str,
    persist_directory: Optional[str],
    embedding_function: Embeddings,
    docs: list[Document],
    relevance_score_fn: Callable[[float], float],
    retriever_kwargs: Optional[dict[str, Any]] = None,
) -> VectorStoreRetriever:
    """Build or get a vector_store based on Chroma as retriever

    Args:
        collection_name (str): name of the collection to create or retrieve
        persist_directory (Optional[str]): path where to store the collection. If None the collection is in memory only
        embedding_function (): embedding function used to create vectors from documents
        docs (list[Document]): documents to store
        relevance_score_fn (Callable[[float], float]): function to normalize Chroma's similarity distance (from range [0,2]) to range [0,1]
        retriever_kwargs (Optional[dict[str, Any]], optional): arguments for the vector_store as retriever (e.g. search_type and search_kwargs). Defaults to None.
    Returns:
        VectorStoreRetriever: Chroma vector store as retriever
    """
    vector_store = build_vector_store(collection_name, persist_directory, embedding_function, docs, relevance_score_fn)
    if retriever_kwargs is not None:
        return vector_store.as_retriever(**retriever_kwargs)
    return vector_store.as_retriever()
