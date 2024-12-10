import asyncio
from typing import List

from core.logger import get_logger
from langchain_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.document_transformers import LongContextReorder


class SetMergerRetriever(BaseRetriever):
    """Retriever that merges the results of multiple retrievers in a single set of documents."""

    retrievers: List[BaseRetriever]
    """A list of retrievers to merge."""

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """
        Get the relevant documents for a given query.

        Args:
            query: The query to search for.

        Returns:
            A list of relevant documents.
        """

        # Merge the results of the retrievers.
        merged_documents = self.merge_documents(query, run_manager)

        return merged_documents

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """
        Asynchronously get the relevant documents for a given query.

        Args:
            query: The query to search for.

        Returns:
            A list of relevant documents.
        """

        # Merge the results of the retrievers.
        merged_documents = await self.amerge_documents(query, run_manager)

        return merged_documents

    def merge_documents(self, query: str, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        """
        Merge the results of the retrievers.

        Args:
            query: The query to search for.

        Returns:
            A list of merged documents.
        """

        logger = get_logger(__name__)

        # Get the results of all retrievers.
        retriever_docs = list[list[Document]]()
        for i, retriever in enumerate(self.retrievers):
            # Add error handling if retriever fails
            try:
                docs = retriever.invoke(
                    query,
                    config={"callbacks": run_manager.get_child("retriever_{}".format(i + 1))},
                )
                if docs is not None or len(docs):
                    retriever_docs.append(docs)
            except Exception as e:
                logger.debug(e)

        # Merge the results of the retrievers.
        merged_documents = list[Document]()
        documents_hash_set = set[int]()

        longest_list = len(max(retriever_docs, key=len))

        for doc_position in range(longest_list):
            for retriever_idx in range(len(self.retrievers)):
                docs = retriever_docs[retriever_idx]
                if docs is not None and docs:
                    doc = docs[doc_position]
                    content_hash = hash(doc.page_content)
                    if content_hash not in documents_hash_set:
                        merged_documents.append(doc)
                        documents_hash_set.add(content_hash)

        # for docs in retriever_docs:
        #     for doc in docs:
        #         content_hash = hash(doc.page_content)
        #         if content_hash not in documents_hash_set:
        #             merged_documents.append(doc)
        #             documents_hash_set.add(content_hash)

        reordering = LongContextReorder()
        reordered_docs = reordering.transform_documents(merged_documents)
        return list(reordered_docs)

        # return merged_documents

    async def amerge_documents(self, query: str, run_manager: AsyncCallbackManagerForRetrieverRun) -> List[Document]:
        """
        Asynchronously merge the results of the retrievers.

        Args:
            query: The query to search for.

        Returns:
            A list of merged documents.
        """

        # Get the results of all retrievers.
        retriever_docs = await asyncio.gather(
            *(
                retriever.ainvoke(
                    query,
                    config={"callbacks": run_manager.get_child("retriever_{}".format(i + 1))},
                )
                for i, retriever in enumerate(self.retrievers)
            )
        )

        # Merge the results of the retrievers.
        merged_documents = list[Document]()
        documents_hash_set = set[int]()
        for docs in retriever_docs:
            for doc in docs:
                content_hash = hash(doc.page_content)
                if content_hash not in documents_hash_set:
                    merged_documents.append(doc)
                    documents_hash_set.add(content_hash)
        return merged_documents
