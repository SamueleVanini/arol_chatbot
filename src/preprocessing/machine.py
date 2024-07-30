from collections import defaultdict

type PdfData = dict[str, list[str]]


class Machine:

    def __init__(self) -> None:
        self.name: str
        self.application_field: str
        self.main_features: PdfData = defaultdict(list[str])
        self.versions: PdfData = defaultdict(list[str])
        self.other_info: PdfData = defaultdict(list[str])
