from enum import Enum, auto
from pathlib import Path
from typing import Optional
from doc_loader.hybrid_loader import HybridLoader
from doc_loader.transform_pipe import ContentTransformation, FromJsonToText
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders.base import BaseLoader


def file_loader(file_path: str, loader_model="json"):
    def pdf_loader():
        loader = PyMuPDFLoader(file_path)
        return loader.load()

    def json_loader():
        loader = JSONLoader(file_path=file_path, jq_schema=".[]", text_content=False)
        return loader.load()

    loaders = {
        "pdf": pdf_loader,
        "json": json_loader,
    }
    if loader_model in loaders:
        docs = loaders[loader_model]()
        print(len(docs))

        return docs
    else:
        print("Invalid input. Please try again.")


class LoaderType(Enum):
    JSON = auto()
    PDF = auto()
    HYBRID = auto()


class FileLoaderFactory:

    def __init__(self) -> None:
        raise EnvironmentError(
            "FileLoaderFactory is designed to be instantiated using the `FileLoaderFactory.get_loader(loader_type, file_path)` method."
        )

    @classmethod
    def get_loader(
        cls,
        loader_type: LoaderType,
        file_path: str | Path,
        transformation_pipe: Optional[ContentTransformation] = None,
        **kwargs,
    ) -> BaseLoader:

        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            raise ValueError(f"The file path: {file_path} does not exist")

        match loader_type:
            case LoaderType.JSON:
                metadata_func = kwargs.pop("metadata_func", None)
                return JSONLoader(file_path=file_path, jq_schema=".[]", text_content=False, metadata_func=metadata_func)
            case LoaderType.PDF:
                return PyMuPDFLoader(str(file_path))
            case LoaderType.HYBRID:
                metadata_func = kwargs.pop("metadata_func", None)
                if transformation_pipe is None:
                    transformation_pipe = FromJsonToText()
                return HybridLoader(
                    file_path=file_path,
                    jq_schema=".[]",
                    text_content=False,
                    metadata_func=metadata_func,
                    transformation_pipe=transformation_pipe,
                )
