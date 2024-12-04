import csv
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from doc_loader.transform_pipe import ContentTransformation, FromJsonToText
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from service.llm_service import LlmFactory


# TODO: load text documents from file and skip llm call
class HybridLoader(JSONLoader):

    def __init__(
        self,
        file_path: str | PathLike,
        jq_schema: str,
        content_key: str | None = None,
        is_content_key_jq_parsable: bool | None = False,
        metadata_func: Callable[[Dict, Dict], Dict] | None = None,
        text_content: bool = True,
        json_lines: bool = False,
        transformation_pipe: ContentTransformation = FromJsonToText(),
    ):
        super().__init__(
            file_path, jq_schema, content_key, is_content_key_jq_parsable, metadata_func, text_content, json_lines
        )
        self.transformation_pipe = transformation_pipe

    def load(self) -> list[Document]:
        docs = super().load()
        for doc in docs:
            doc.page_content = self.transformation_pipe.transform(doc)
        return docs
