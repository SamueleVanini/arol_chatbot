from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import JSONLoader


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
