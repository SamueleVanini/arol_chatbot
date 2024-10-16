import multiprocessing
import os
from os.path import expanduser
from pathlib import Path
from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_community.chat_models import ChatLlamaCpp


class LlmFactory:

    def __init__(self) -> None:
        raise EnvironmentError(
            "Llm is designed to be instantiated using the `LlmFactory.get_model(pretrained_model_name_or_path)` method."
        )

    @classmethod
    def get_model(cls, model_path_or_name: str | Path, **kwargs):
        if isinstance(model_path_or_name, Path):
            model_path = expanduser(model_path_or_name)
            return LlamaCppFactory(model_path, **kwargs).get_model()
        else:
            return GroqFactory(model_path_or_name, **kwargs).get_model()


class LlamaCppFactory:

    def __init__(self, model_path: str, *inputs, **kwargs) -> None:
        path = Path(model_path)
        if not path.exists() or not path.is_file():
            raise ValueError(f"The model path {path} does not exist")
        self.model_path = model_path
        self.verbose = kwargs.pop("verbose", False)
        self.streaming = kwargs.pop("streaming", False)
        self.temperature = kwargs.pop("temperature", 0)
        self.inputs = inputs
        self.kwargs = kwargs

    def get_model(self) -> BaseChatModel:
        return ChatLlamaCpp(
            model_path=self.model_path,
            verbose=self.verbose,
            streaming=self.streaming,
            temperature=self.temperature,
            n_threads=multiprocessing.cpu_count() - 1,
            **self.kwargs,
        )


class GroqFactory:

    def __init__(self, model_name: str, *inputs, **kwargs) -> None:
        self.model_name = model_name
        self.inputs = inputs
        self.kwargs = kwargs
        rate_limiter = self.kwargs.get("rate_limiter", None)
        if rate_limiter is None:
            requests_per_second = self.kwargs.get("request_per_second", 30 / 60)
            check_every_n_seconds = self.kwargs.get("check_every_n_seconds", 0.1)
            max_bucket_size = self.kwargs.get("max_bucket_size", 30)
            self.rate_limiter = InMemoryRateLimiter(
                requests_per_second=requests_per_second,
                check_every_n_seconds=check_every_n_seconds,
                max_bucket_size=max_bucket_size,
            )
        else:
            self.rate_limiter = rate_limiter
        if "GROQ_API_KEY" not in os.environ:
            raise EnvironmentError(
                "Missing GROQ_API_KEY in environment variables, please specify it in the .env file or in the operating system to use the Groq provider"
            )

    def get_model(self) -> BaseChatModel:
        return ChatGroq(model=self.model_name, *self.inputs, rate_limiter=self.rate_limiter, **self.kwargs)
