from os import PathLike
from typing import Any, Callable, Dict, Optional
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from service.llm_service import LlmFactory


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
        transformationModel: BaseChatModel | None = None,
        model_kwargs: Optional[Dict] = None,
    ):
        super().__init__(
            file_path, jq_schema, content_key, is_content_key_jq_parsable, metadata_func, text_content, json_lines
        )

        if transformationModel is None:
            model_kwargs = model_kwargs or {}
            transformationModel = LlmFactory.get_model("llama3-8b-8192", temperature=0, **model_kwargs)
        self.transformation_chain = (
            {"doc": lambda x: x.page_content}
            | ChatPromptTemplate.from_template(
                "Rewrite the following json object describing a machine into a small paragraph containing all the relevant information:\n\n{doc}"
            )
            | transformationModel
            | StrOutputParser()
        )

    def load(self) -> list[Document]:
        docs = super().load()
        for doc in docs:
            doc.page_content = self.transformation_chain.invoke(doc)
        return docs
