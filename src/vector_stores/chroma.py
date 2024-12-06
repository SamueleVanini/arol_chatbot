import logging
from typing import Callable, Dict, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from core.logger import get_logger

logger = get_logger(__name__)


def custom_cosine_relevance_score_fn(distance: float) -> float:
    """Normalize the distance to a score on a scale [0, 1].

    Args:
       distance (float): distance between 2 vectors (since Chroma uses the concept of distance and not similarity the range will be in [0,2])

    Returns:
       float: distance normalized in [0,1]
    """
    return 1 - min(distance, 1)


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
        relevance_score_fn: Optional[Callable[[float], float]] = None,
    ) -> Chroma:

        if override_collection_if_exists and documents is not None:
            return Chroma.from_documents(
                documents,
                embedding_function,
                collection_name=collection_name,
                persist_directory=persist_directory,
                collection_metadata=collection_metadata,
                relevance_score_fn=relevance_score_fn,
            )
        try:
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding_function,
                persist_directory=persist_directory,
                create_collection_if_not_exists=False,
                collection_metadata=collection_metadata,
                relevance_score_fn=relevance_score_fn,
            )
        except:
            logger.warning(
                f"requested collection not found at path: {persist_directory}, creating a new collection: {collection_name}"
            )

            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding_function,
                persist_directory=persist_directory,
                create_collection_if_not_exists=True,
                collection_metadata=collection_metadata,
                relevance_score_fn=relevance_score_fn,
            )
