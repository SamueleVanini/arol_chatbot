from dataclasses import dataclass, field

from collections import defaultdict
from copy import copy
from statemachine import StateMachine, State

# from src.preprocessing.machine import Machine, PdfData
from .machine import Machine, PdfData

utf8_dot = "\xe2\x80\xa2"
unicode_dot = "\u2022"

# TODO: Finish to write unit test for the code


@dataclass(eq=False)
class MutableStateValue:
    last_seen_type: str = field(default="")
    last_seen_key_value: str = field(default="")


class PdfPreprocessing(StateMachine):

    # possible state states
    application_field = State(initial=True)
    machine_name = State()
    main_feature = State()
    versions = State()
    options = State()
    dirty = State()
    final_state = State(final=True)

    # add_application = (application_field.to(machine) | application_field.to(application_field))
    add_application = application_field.to(machine_name)
    add_name = machine_name.to(main_feature)
    # add_image = application_field.to(machine)
    add_info = (
        main_feature.to(versions, cond="is_features_finished")
        | main_feature.to.itself(internal=True, unless="is_features_finished")
        | versions.to(options, cond="is_versions_finished")
        | versions.to.itself(internal=True, unless="is_versions_finished")
        | options.to(application_field, cond="is_options_finished")
        | options.to(dirty, cond="is_dirty")
        | options.to.itself(internal=True, unless=["is_options_finished", "is_dirty"])
        | dirty.to(application_field, cond="is_application_field_title")
    )
    go_to_final_state = options.to(final_state) | dirty.to(final_state)

    def __init__(self):
        self.machines: dict[str, list[Machine]] = defaultdict(list)
        # self.machines: list[Machine] = []
        self.mutable_state = MutableStateValue()
        self.main_feature_finished = False
        self.versions_finished = False
        self.options_finished = False
        super(PdfPreprocessing, self).__init__()

    @add_application.before
    def create_machine_add_app_field(self, block):
        self.current_machine = Machine()
        text = ""
        for line_dict in block["lines"]:
            for span_dict in line_dict["spans"]:
                text += span_dict["text"].lower() + " "
        application_field = text.strip()
        self.current_machine.application_field = application_field

    @add_name.before
    def add_machine_name(self, block):
        name = block["lines"][0]["spans"][0]["text"].lower()
        self.current_machine.name = name

    @add_info.on
    def extract_feature(self, block, target):
        for line in block["lines"]:
            for span in line["spans"]:
                match self.current_state.id:
                    case "main_feature":
                        if "Bold" in span["font"]:
                            text_value = span["text"].lower().strip()
                            if text_value == "main features":
                                return
                            if self.mutable_state.last_seen_type == "key":
                                self.mutable_state.last_seen_key_value += " " + text_value
                            else:
                                self.mutable_state.last_seen_type = "key"
                                self.mutable_state.last_seen_key_value = text_value
                        else:
                            features = span["text"].lower()
                            for feature in features.split(unicode_dot):
                                if self.mutable_state.last_seen_type != "key":
                                    last_feature_seen = self.current_machine.main_features[
                                        self.mutable_state.last_seen_key_value
                                    ][-1]
                                    last_feature_seen += " " + feature.strip()
                                    self.current_machine.main_features[self.mutable_state.last_seen_key_value][
                                        -1
                                    ] = last_feature_seen
                                    self.mutable_state.last_seen_type = "value"
                                else:
                                    self.current_machine.main_features[self.mutable_state.last_seen_key_value].append(
                                        feature.strip()
                                    )
                            self.mutable_state.last_seen_type = "value"
                    case "versions":
                        if "Bold" in span["font"]:
                            text_value = span["text"].lower().strip()
                            if text_value == "versions":
                                return
                            if self.mutable_state.last_seen_type == "key":
                                self.mutable_state.last_seen_key_value += " " + text_value
                            else:
                                self.mutable_state.last_seen_type = "key"
                                self.mutable_state.last_seen_key_value = text_value
                        else:
                            version = span["text"].lower().strip()
                            if self.mutable_state.last_seen_type != "key":
                                self.current_machine.versions[self.mutable_state.last_seen_key_value][-1] += (
                                    " " + version
                                )
                            else:
                                self.current_machine.versions[self.mutable_state.last_seen_key_value].append(version)
                            self.mutable_state.last_seen_type = "value"
                    case "options":
                        if target.id == "dirty" or target.id == "application_field":
                            return
                        if "bold" in span["font"].lower():
                            self.mutable_state.last_seen_type = "key"
                            self.mutable_state.last_seen_key_value = span["text"].lower().strip()
                        else:
                            full_span = span["text"].lower().strip()
                            if self.mutable_state.last_seen_type != "key":
                                last_option_seen = self.current_machine.other_info[
                                    self.mutable_state.last_seen_key_value
                                ].pop()
                                full_span = f"{last_option_seen} {full_span.strip()}"
                            for option in full_span.split(unicode_dot):
                                self.current_machine.other_info[self.mutable_state.last_seen_key_value].append(
                                    option.strip()
                                )
                            self.mutable_state.last_seen_type = "value"

    @main_feature.enter
    @versions.enter
    @options.enter
    def clear_mutable_state_value(self):
        self.mutable_state.last_seen_type = ""
        self.mutable_state.last_seen_key_value = ""

    @options.exit
    def machine_finished(self):
        self.machines[self.current_machine.application_field].append(copy(self.current_machine))

    def is_features_finished(self, block):
        span = block["lines"][0]["spans"][0]
        return span["text"] == "VERSIONS"

    def is_versions_finished(self, block):
        span = block["lines"][0]["spans"][0]
        return span["text"] == "OPTIONS"

    def is_options_finished(self, block):
        span = block["lines"][0]["spans"][0]
        return "Bold" in span["font"] and span["size"] > 20

    def is_dirty(self, block):
        span = block["lines"][0]["spans"][0]
        condition: bool = (
            self.mutable_state.last_seen_type == "value" and "light" in span["font"].lower() and span["size"] < 10
        )
        return condition

    def is_application_field_title(self, block):
        return self.is_options_finished(block)


class PdfPreprocessingException(Exception):

    def __init__(self, current_state: str, block, message: str = "Unexpected block found") -> None:
        super().__init__(message)
        self.error_block = block
        self.current_state = current_state
