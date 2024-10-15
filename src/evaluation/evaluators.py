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

    # TODO: add metrics for number of run without an output

    def evaluation(self, runs: list[Run], examples: list[Example]) -> dict[str, list[dict[str, str | float]]]:

        machines_pred = []
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
                print(run.outputs)

        # list of list of matchs
        matchs = [example.outputs["matchs"] for example in examples]
        matchs = [list(map(str.lower, match_list)) for match_list in matchs]

        classes = list(set(itertools.chain.from_iterable(matchs)))

        y_true = self.multilabel_binarizer.fit_transform(matchs)
        y_pred = self.multilabel_binarizer.transform(machines_pred)

        report: dict = classification_report(y_true=y_true, y_pred=y_pred, target_names=classes, output_dict=True)  # type: ignore
        ic("Summary metrics evaluated")

        results: list[dict[str, str | float]] = []
        for label, metrics in report.items():
            ic(label, metrics)
            for metric, score in metrics.items():
                results.append({"key": f"{label}_{metric}", "score": score})
        return {"results": results}
