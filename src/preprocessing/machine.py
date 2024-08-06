from collections import defaultdict
import json

type PdfData = dict[str, list[str]]


class Machine:

    def __init__(self) -> None:
        self.name: str = ""
        self.application_field: str = ""
        self.main_features: PdfData = defaultdict(list[str])
        self.versions: PdfData = defaultdict(list[str])
        self.other_info: PdfData = defaultdict(list[str])

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name
            and self.application_field == other.application_field
            and self.main_features == other.main_features
            and self.versions == other.versions
            and self.other_info == other.other_info
        )


class MachineEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
