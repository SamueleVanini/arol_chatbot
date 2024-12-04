import csv
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Protocol
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from service.llm_service import LlmFactory


class ContentTransformation(Protocol):

    def transform(self, doc: Document) -> Any: ...


class FromJsonToText:

    def __init__(
        self,
        model: BaseChatModel | None = None,
        model_kwargs: Optional[Dict] = None,
        save_results: bool = False,
        saving_path: Optional[Path] = None,
    ) -> None:
        file_exists = saving_path is not None and saving_path.exists() and saving_path.is_file()
        if save_results and not file_exists:
            raise ValueError(f"save results is set to true but path: {saving_path} is invalid")
        if model is None:
            model_kwargs = model_kwargs or {}
            model = LlmFactory.get_model("llama3-8b-8192", temperature=0, **model_kwargs)
        self.save_results = save_results
        self.saving_path = saving_path
        self.transformation_chain = (
            {"doc": lambda x: x.page_content}
            | ChatPromptTemplate.from_template(
                """You are an expert system in transforming json object into paragraph of text. Given an json object rewrite it in a small paragraph using normal language. DO NOT add any new content or preface like  "Here is the transformed paragraph:".

<<Example>>
- Input: {{
        "name": "flex",
        "application_field": "oriented caps elevator",
        "main_features": {{
            "speed production": [
                "up to 1.500 cpm / 90.000 cph"
            ],
            "main market": [
                "beverage",
                "food",
                "chemical"
            ],
            "caps application": [
                "flat pre-threaded caps",
                "sport pre-threaded caps"
            ],
            "main features": [
                "mechanical caps elevator",
                "star-wheel for equally spacing the caps",
                "conveyor belt"
            ],
            "quick format change": [
                "caps guide"
            ],
            "other": [
                "combined structure with centrifugal/mechanical sorter and/or buffer"
            ]
        }},
        "versions": {{}},
        "other_info": {{}}
    }}
- Output: Flex is an oriented caps elevator that specializes in the beverage, food, and chemical industries. It boasts impressive speeds, capable of producing up to 1,500 cases per minute or 90,000 cases per hour. The machine is designed to handle various types of caps, including flat pre-threaded and sport pre-threaded caps. Its main features include a mechanical caps elevator, a star-wheel for evenly spacing caps, and a conveyor belt. Additionally, Flex offers quick format changes with the aid of caps guides and can be integrated into a combined structure with a centrifugal or mechanical sorter and/or buffer for enhanced efficiency.

Document:
{doc}
"""
            )
            | model
            | StrOutputParser()
        )

    def transform(self, doc: Document) -> str:
        content = self.transformation_chain.invoke(doc)
        if self.save_results:
            with open(self.saving_path, "a") as f:  # type: ignore
                writer = csv.writer(f)
                writer.writerow((doc.metadata["name"], content))
        return content


# NOTE: for now the class just check if the file exists and append content as the end of it. You MUST check the first line and be sure that there are no content
class FromFileToText:

    def __init__(
        self,
        text_docs_path: str | PathLike = "./data/json_rewritten.csv",
    ) -> None:
        text_docs_path = Path(text_docs_path)
        if text_docs_path.exists() and text_docs_path.is_file():
            self.text_docs = self._parse_text_docs(text_docs_path)
        else:
            raise ValueError(f"text_docs_path: {text_docs_path} is invalid")

    def transform(self, doc: Document) -> str:
        machine_name = doc.metadata["name"]
        return self.text_docs[machine_name]

    @staticmethod
    def _parse_text_docs(path: Path):
        """Parse a csv file and extract the content. We are assuming the file is in the form
        (machine_name, rewritten_paragraf)

        Args:
            path (Path): file path

        Returns:
            dict[str, str]: dictionary containing the machines name as key and rewritten document content as value
        """
        docs = {}
        with open(path, "r") as f:
            file_reader = csv.reader(f)
            next(file_reader)  # skip the first line
            for row in file_reader:
                docs[row[0]] = row[1]
        return docs
