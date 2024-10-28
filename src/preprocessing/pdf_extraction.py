from collections import defaultdict
from copy import copy
from typing import Any, List
from statemachine import StateMachine, State

from .machine import Machine

utf8_dot = "\xe2\x80\xa2"
UNICODE_DOT = "\u2022"
OPEN_QUOTE = "\u201c"
CLOSE_QUOTE = "\u201d"
UNICODE_DIAMETER = "\u00f8"
# no idea why 2 different glyph for the same concept but ok
UNICODE_LESS_OR_EQUAL_1 = "\uf0a3"
UNICODE_LESS_OR_EQUAL_2 = "\u2264"


class PdfPreprocessing(StateMachine):

    initial_state = State(initial=True)
    application_field = State()
    machine_name = State()
    main_feature = State()
    versions = State()
    options = State()
    dirty = State()
    final_state = State(final=True)

    parse_block = (
        initial_state.to(application_field, cond="is_application_field_section")
        | application_field.to(machine_name, cond="is_machine_name_section")
        | application_field.to(dirty, unless="is_machine_name_section")
        | machine_name.to(main_feature, cond="is_main_features_section")
        | machine_name.to(dirty, unless="is_main_features_section")
        | main_feature.to(versions, cond="is_versions_section")
        | main_feature.to(dirty, cond="is_dirty")
        | main_feature.to(main_feature, unless="is_versions_section")
        | versions.to(options, cond="is_options_section")
        | versions.to(versions, unless="is_options_section")
        | options.to(application_field, cond="is_application_field_section")
        | options.to(dirty, cond="is_dirty")
        | options.to(options, unless=["is_application_field_section", "is_dirty"])
        | dirty.to(application_field, cond="is_application_field_section")
        | dirty.to(machine_name, cond="is_machine_name_section")
        | dirty.to(dirty, unless=["is_application_field_section", "is_machine_name_section"])
    )

    go_to_final_state = options.to(final_state) | dirty.to(final_state)

    def __init__(
        self,
        model: Any = None,
        state_field: str = "state",
        start_value: Any = None,
        rtc: bool = True,
        allow_event_without_transition: bool = False,
        listeners: List[object] | None = None,
    ):
        self.machines: dict[str, list[Machine]] = defaultdict(list)
        self.current_machine = None
        super().__init__(model, state_field, start_value, rtc, allow_event_without_transition, listeners)

    @application_field.enter
    def create_machine_add_app_field(self, block):
        text = ""
        for line_dict in block["lines"]:
            for span_dict in line_dict["spans"]:
                text += span_dict["text"].lower() + " "
        application_field = self._sanitize_text(text.strip())
        self.save_current_machine_if_needed()
        self.current_machine = Machine()
        self.current_machine.application_field = application_field

    @machine_name.enter
    def add_machine_name(self, block):
        assert self.current_machine is not None
        name = ""
        for line in block["lines"]:
            for span in line["spans"]:
                name = f'{name} {span["text"].lower()}'.strip()
        name = self._sanitize_text(name)
        # name = self._sanitize_text(block["lines"][0]["spans"][0]["text"].lower())
        machines_for_application_field = self.machines.get(self.current_machine.application_field)
        if machines_for_application_field is not None:
            for machine in machines_for_application_field:
                if machine.name == name:
                    return
        self.current_machine.name = name.replace(UNICODE_DOT, "-")

    @main_feature.enter
    @versions.enter
    @options.enter
    def add_machine_info(self, block):
        assert self.current_machine is not None
        if self.current_state.id == "main_feature":
            info_dict = self.current_machine.main_features
        elif self.current_state.id == "versions":
            info_dict = self.current_machine.versions
        elif self.current_state.id == "options":
            info_dict = self.current_machine.other_info
        else:
            raise Exception("Can't trace where store information with the current state")

        last_span_seen_is_key = False
        key = None

        for line in block["lines"]:
            for span in line["spans"]:
                if self._is_key(span):
                    if key is not None:
                        key = f'{key} {span["text"].lower().strip()}'
                    else:
                        key = span["text"].lower().strip()
                    last_span_seen_is_key = True
                else:
                    full_span = self._sanitize_text(span["text"].lower().strip())
                    last_features_added = info_dict.get(key)
                    if last_features_added is not None and last_span_seen_is_key == False:
                        last_feature_added = last_features_added.pop()
                        full_span = f"{last_feature_added} {full_span}"
                    for info in full_span.split(UNICODE_DOT):
                        info_dict[key].append(info.strip())
                    last_span_seen_is_key = False

    @go_to_final_state.on
    def save_current_machine_if_needed(self) -> bool:
        if self.current_machine is not None and self.current_machine.name != "":
            self.machines[self.current_machine.application_field].append(copy(self.current_machine))
            return True
        return False

    def is_application_field_section(self, block):
        span = block["lines"][0]["spans"][0]
        return "Bold" in span["font"] and span["size"] == 23.0

    def is_machine_name_section(self, block):
        span = block["lines"][0]["spans"][0]
        return "Bold" in span["font"] and span["size"] == 33.0

    def is_main_features_section(self, block):
        span = block["lines"][0]["spans"][0]
        return span["text"] == "MAIN FEATURES"

    def is_versions_section(self, block):
        span = block["lines"][0]["spans"][0]
        return span["text"] == "VERSIONS"

    def is_options_section(self, block):
        span = block["lines"][0]["spans"][0]
        return span["text"] == "OPTIONS"

    def is_dirty(self, block):
        span = block["lines"][0]["spans"][0]
        # trying fast fix (some text span like "FREE STANDING EXECUTION" has size 8.0 or 10.0 and not 7.0
        # return "Bold" not in span["font"] and (span["size"] == 7.0 or span["size"] == 8.0) and span["flags"] != 20
        return "Bold" not in span["font"] and span["flags"] != 20

    def _is_key(self, span) -> bool:
        return "Bold" in span["font"]

    def _sanitize_text(self, value: str) -> str:
        return (
            value.replace(OPEN_QUOTE, "'")
            .replace(CLOSE_QUOTE, "'")
            .replace(UNICODE_DIAMETER, " diameter")
            .replace(UNICODE_LESS_OR_EQUAL_1, "less or equal")
            .replace(UNICODE_LESS_OR_EQUAL_2, "less or equal")
        )
