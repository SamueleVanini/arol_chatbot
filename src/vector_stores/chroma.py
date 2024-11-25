import chromadb
import logging
from typing import Dict, Optional
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ChromaCollection:

    @classmethod
    def get_collection(
        cls,
        collection_name: str,
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Embeddings] = None,
        documents: Optional[list[Document]] = None,
        override_collection_if_exists: Optional[bool] = False,
        collection_metadata: Optional[Dict] = {"hnsw:space": "cosine"},
    ) -> Chroma:

        if override_collection_if_exists and documents is not None:
            return Chroma.from_documents(
                documents,
                embedding_function,
                collection_name=collection_name,
                persist_directory=persist_directory,
                collection_metadata=collection_metadata,
            )
        try:
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding_function,
                persist_directory=persist_directory,
                create_collection_if_not_exists=False,
                collection_metadata=collection_metadata,
            )
        except ValueError as e:
            logger.warning(
                f"requested collection not found at path: {persist_directory}, creating a new collection: {collection_name}"
            )

        if documents is None:
            raise ValueError("can't create an empty collection")

        return Chroma.from_documents(
            documents,
            embedding_function,
            collection_name=collection_name,
            persist_directory=persist_directory,
            collection_metadata=collection_metadata,
        )
