from collections import defaultdict
import json
from typing import Optional

from pydantic import BaseModel, Field

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


class MachineModel(BaseModel):
    """Search over a database of customised capping machines for any closure need."""

    content_search: str = Field(
        ..., description="Similarity search query applied to the machine objects expressed in json format"
    )
    name: Optional[str] = Field(
        ..., description="Complete or partial name of the machine. Only use if explicitly specified."
    )
    application_field: Optional[str] = Field(
        ..., description="Machine's field of application. Only use if explicitly specified."
    )
    main_features: Optional[dict[str, list[str]]] = Field(
        # default=defaultdict(list[str]),
        None,
        description="Machine main features dictionary. The key is the name of the feature while the value explain the type of feature. Only use if explicitly specified.",
    )
    versions: Optional[dict[str, list[str]]] = Field(
        # default=defaultdict(list[str]),
        None,
        description="Machine versions dictionary. The key is the name of the version while the value gives more infomation about the machine version. Only use if explicitly specified.",
    )
    options: Optional[dict[str, list[str]]] = Field(
        # default=defaultdict(list[str]),
        None,
        description="Machine options dictionary. The key is the type of option while the value gives more infomation about the configuration of the option. Only use if explicitly specified.",
    )

    def pretty_print(self) -> None:
        for field in self.model_fields:
            if getattr(self, field) is not None and getattr(self, field) != getattr(
                self.model_fields[field], "default", None
            ):
                print(f"{field}: {getattr(self, field)}")


class MachineEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
