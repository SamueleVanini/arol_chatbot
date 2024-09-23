import chromadb
import logging
from typing import Optional
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class ChromaCollection:

    @classmethod
    def get_collection(
        cls,
        collection_name: str,
        persist_directory: Optional[str] = None,
        embedding_function: Optional[Embeddings] = None,
    ) -> Chroma:
        persistent_client = chromadb.PersistentClient()
        try:
            collection = persistent_client.get_collection(collection_name)
        except ValueError:
            logger.info(f"requested collection not found, creating a new collection: {collection_name}")
            collection = Chroma(
                collection_name=collection_name,
                embedding_function=embedding_function,
                persist_directory=persist_directory,
            )
        return collection
