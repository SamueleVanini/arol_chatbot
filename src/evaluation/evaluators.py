import itertools
from typing import Protocol
from langsmith.schemas import Run, Example
from sklearn.metrics import classification_report
from sklearn.preprocessing import MultiLabelBinarizer
from icecream import ic


class CustomRowEvaluator(Protocol):

    def evaluation(self, run: Run, example: Example) -> dict[str, list[dict[str, str | float]]]: ...


class CustomSummaryEvaluator(Protocol):

    def evaluation(self, runs: list[Run], examples: list[Example]) -> dict[str, list[dict[str, str | float]]]: ...


class MultilabelEvaluator:

    def __init__(self) -> None:
        self.multilabel_binarizer = MultiLabelBinarizer()
        self.report: dict | None = None

    def evaluation(self, runs: list[Run], examples: list[Example]) -> dict[str, list[dict[str, str | float]]]:

        machines_pred = []
        runs_no_output = 0
        for run in runs:
            docs_run = []
            docs = run.outputs["output"]
            # NOTE: if the run for some reason didn't went well the output is None, take care of it
            if docs is not None:
                for doc in docs:
                    if doc is not None:
                        docs_run.append(doc.metadata["name"].lower())
                machines_pred.append(docs_run)
            else:
                machines_pred.append(["DUMMY"])
                runs_no_output += 1

        # list of list of matchs
        matchs = [example.outputs["matchs"] for example in examples]
        matchs = [list(map(str.lower, match_list)) for match_list in matchs]

        self.classes = list(set(itertools.chain.from_iterable(matchs)))

        # TODO: if the model return an empty output we have a mismatch between y_true and y_pred. Handle the case
        self.y_true = self.multilabel_binarizer.fit_transform(matchs)
        self.y_pred = self.multilabel_binarizer.transform(machines_pred)

        self.report = classification_report(y_true=self.y_true, y_pred=self.y_pred, target_names=self.classes, output_dict=True)  # type: ignore
        ic("Summary metrics evaluated")

        results: list[dict[str, str | float]] = []
        if not isinstance(self.report, dict):
            raise Exception("Something went wrong, we don't have a report...")
        for label, metrics in self.report.items():
            ic(label, metrics)
            for metric, score in metrics.items():
                results.append({"key": f"{label}_{metric}", "score": score})
        results.append({"key": "no docs run", "score": runs_no_output})
        return {"results": results}

    def get_report_str(self) -> str:
        return classification_report(
            y_true=self.y_true, y_pred=self.y_pred, target_names=self.classes, output_dict=False
        )  # type: ignore


class FullChainAnswerPrecision:

    def __init__(self, machines: list[str]) -> None:
        self.multilabel_binarizer = MultiLabelBinarizer()
        self.report: dict | None = None
        self.machines = list(map(str.lower, machines))

    def evaluation(self, runs: list[Run], examples: list[Example]) -> dict[str, list[dict[str, str | float]]]:
        assert len(runs) == len(
            examples
        ), f"Error in FullChainAnswerPrecision, length of runs: {len(runs)} and example does not match: {len(examples)}"

        machines_pred = []
        runs_no_output = 0
        for run in runs:
            docs_run = []
            answer: str = run.outputs["output"]["answer"]
            for machine in self.machines:
                if machine in answer.lower():
                    docs_run.append(machine)
            if not docs_run:
                docs_run = ["DUMMY"]
            machines_pred.append(docs_run)

        # predicted_right = 0
        # total_support = 0
        # for run, example in zip(runs, examples):
        #     for example in examples:
        #         if run.outputs["answer"]

        matchs = [example.outputs["matchs"] for example in examples]
        matchs = [list(map(str.lower, match_list)) for match_list in matchs]

        self.classes = list(set(itertools.chain.from_iterable(matchs)))

        # TODO: if the model return an empty output we have a mismatch between y_true and y_pred. Handle the case
        self.y_true = self.multilabel_binarizer.fit_transform(matchs)
        self.y_pred = self.multilabel_binarizer.transform(machines_pred)

        self.report = classification_report(y_true=self.y_true, y_pred=self.y_pred, target_names=self.classes, output_dict=True)  # type: ignore
        results: list[dict[str, str | float]] = []
        if not isinstance(self.report, dict):
            raise Exception("Something went wrong, we don't have a report...")
        for label, metrics in self.report.items():
            for metric, score in metrics.items():
                results.append({"key": f"{label}_{metric}", "score": score})
        results.append({"key": "no docs run", "score": runs_no_output})
        return {"results": results}

    def get_report_str(self) -> str:
        return classification_report(
            y_true=self.y_true, y_pred=self.y_pred, target_names=self.classes, output_dict=False
        )  # type: ignore
