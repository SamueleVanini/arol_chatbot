from __future__ import annotations
from abc import ABC, abstractmethod
from copy import copy
from functools import partial, singledispatchmethod
from typing import Any, Optional

from langsmith import evaluate
from langchain_core.runnables import Runnable

from .evaluators import CustomRowEvaluator, CustomSummaryEvaluator


class BaseEvaluator(ABC):

    @property
    @abstractmethod
    def results(self) -> Any:
        pass

    @singledispatchmethod
    @abstractmethod
    def add_dataset(self, dataset) -> None:
        raise NotImplementedError(f"Implementation of add_dataset with dataset's type: {type(dataset)}")

    @abstractmethod
    def add_row_evaluator(self, evaluator: CustomRowEvaluator) -> None:
        pass

    @abstractmethod
    def add_summary_evaluator(self, evaluator: CustomSummaryEvaluator) -> None:
        pass

    @abstractmethod
    def add_metadata(self, data: dict[str, str]) -> None:
        pass

    @abstractmethod
    def set_target(self, chain: Runnable) -> None:
        pass


class LangsmithEvaluator(BaseEvaluator):

    def __init__(self, options: Optional[dict[str, Any]] = None) -> None:
        self.target = None
        self.row_evaluators = []
        self.summary_evaluators = []
        self.dataset = None
        self.metadata = None
        if options is None:
            options = {}
        self.experiment_prefix = options.get("experiment_prefix", None)
        self.description = options.get("description", None)
        self.num_repetitions = options.get("num_repetitions", 1)

    @singledispatchmethod
    def add_dataset(self, dataset) -> None:
        raise NotImplementedError(f"Implementation of add_dataset with dataset's type: {type(dataset)}")

    @add_dataset.register
    def _(self, dataset: str) -> None:
        self.dataset = dataset

    # @add_dataset.register
    # def _(self, dataset: dict[str, list[dict[str, str]]]) -> None:
    #     raise NotImplementedError("Evaluation given directily the examples is not supported yet")

    def add_row_evaluator(self, evaluator: CustomRowEvaluator) -> None:
        self.row_evaluators.append(evaluator.evaluation)

    def add_summary_evaluator(self, evaluator: CustomSummaryEvaluator) -> None:
        self.summary_evaluators.append(evaluator.evaluation)

    def add_metadata(self, data: dict[str, str]) -> None:
        self.metadata = copy(data)

    def set_target(self, chain: Runnable) -> None:

        def target_fun(chain, inputs):
            output = chain.invoke(inputs["question"])
            return {"output": output}

        self.target = partial(target_fun, chain)

    @property
    def results(self) -> Any:
        if (
            self.target is None
            or self.dataset is None
            or (len(self.row_evaluators) == 0 and len(self.summary_evaluators) == 0)
        ):
            raise Exception(
                "The evaluation pipeline is not fully constructed, please finish the configuration before running it"
            )
        results = evaluate(
            self.target,
            self.dataset,
            self.row_evaluators,
            summary_evaluators=self.summary_evaluators,
            metadata=self.metadata,
            experiment_prefix=self.experiment_prefix,
            description=self.description,
            num_repetitions=self.num_repetitions,
        )
        results.wait()
        return results
