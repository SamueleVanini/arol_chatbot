from langchain_community.embeddings import SentenceTransformerEmbeddings            
from langchain_community.document_loaders import JSONLoader
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_NAMES = {
    # max seq length: 256
    "ALL-MINILM": "all-MiniLM-L6-v2",
    # max seq length: 384
    "ALL-MPNET": "all-mpnet-base-v2",
    # max seq length: 512
    "MSMARCO-DISTILBERT": "msmarco-distilbert-base-v4",
}
TOKENIZER_NAMES = {
    "ALL-MINILM": "sentence-transformers/all-MiniLM-L6-v2",
    "ALL-MPNET": "sentence-transformers/all-mpnet-base-v2",
    "MSMARCO-DISTILBERT": "sentence-transformers/msmarco-distilbert-base-v4",
}

# cleaup_tokenization_spaces: Whether or not the model should cleanup the spaces that were added when splitting the input text during the tokenization process. 
CLEAN_UP_TOKENIZATION_SPACES = True


def get_embedding_function(model_name):
    # This notation is horrible and I hate it, blame the langchain_huggingface library developers for it
    model_kwargs = {"tokenizer_kwargs": {"clean_up_tokenization_spaces": CLEAN_UP_TOKENIZATION_SPACES}}
    embedding_function = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)
    print(F"EMBEDDING MAX SEQ LENGTH: {embedding_function.client.get_max_seq_length()}")
    return embedding_function


def print_documents_len_statistics(docs: list[str]):
    docs_content_len = [len(doc) for doc in docs]
    smallest_doc = min(docs_content_len)
    largest_doc = max(docs_content_len)
    avg_doc = sum(docs_content_len) / len(docs_content_len)
    print(f"Smallest doc is {smallest_doc}")
    print(f"Largest doc is {largest_doc}")
    print(f"Average doc is {avg_doc}")


def print_documents_tokens_statistics(docs: list[str], model_name, apply_padding, apply_truncation):
    tokenizer = AutoTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=CLEAN_UP_TOKENIZATION_SPACES)
    encoded_input = tokenizer(docs, padding=apply_padding, truncation=apply_truncation, return_tensors=None)
    len_words_ids = [len(encoding.word_ids) for encoding in encoded_input.encodings]
    smallest_tokenization = min(len_words_ids)
    largest_tokenization = max(len_words_ids)
    avg_tokenization = sum(len_words_ids) / len(len_words_ids)
    print(f"Smallest doc tokens is {smallest_tokenization}")
    print(f"Largest doc tokens is {largest_tokenization}")
    print(f"Average doc tokens is {avg_tokenization}")  


if __name__ == "__main__":
    loader = JSONLoader(file_path="./data/processed_catalog.json", jq_schema=".[]", text_content=False)
    documents = loader.load()
    print(f"EMBEDDING: {EMBEDDING_NAMES["ALL-MINILM"]}")
    print(f"TOKENIZER: {TOKENIZER_NAMES['ALL-MINILM']}")
    embedding_function = get_embedding_function(EMBEDDING_NAMES["ALL-MINILM"])
    docs_content = [doc.page_content for doc in documents]
    print_documents_len_statistics(docs_content)
    print_documents_tokens_statistics(
        docs_content, TOKENIZER_NAMES["ALL-MINILM"], apply_padding=True, apply_truncation=False
    )
