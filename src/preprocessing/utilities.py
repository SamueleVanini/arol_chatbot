from copy import deepcopy
from typing import Callable
from preprocessing.machine import Machine


def fix_machines(machines: list[Machine]):
    # map to fix the machines that have known problem after parsing
    # (the issue should be fixed in the parser but for now it's fine to be here)
    machines_to_fix: dict[str, Callable] = {
        "next": _multiple_versions,
        "eagle vp": _multiple_caps,
        "euro pp-c euro pp-g": _multiple_name,
        "quasar r-f-rf": _caps_application,
        "saturno r-f-rf": _caps_application,
        "gemini r-f-rf": _caps_application,
        "over": _fix_production_speed,
    }

    new_machines_list = []
    for machine in machines:
        if machine.name in machines_to_fix:
            func = machines_to_fix[machine.name]
            new_machines = func(machine)
            new_machines_list.extend(new_machines)
        else:
            new_machines_list.append(deepcopy(machine))

    return new_machines_list


def _multiple_versions(machine: Machine):
    speed_production_str = machine.main_features["speed production"][0]
    splits = speed_production_str.split("bph", maxsplit=1)
    m1_production_speed = splits[0] + "bph"
    m2_production_speed = splits[1]
    m1 = deepcopy(machine)
    m2 = deepcopy(machine)

    # fix machine 1
    m1.name += " pk"
    m1.main_features["speed production"][0] = m1_production_speed
    m1.versions.pop("pk")
    values = m1.versions.pop("pk vp")
    m1.versions["pk"] = values

    # fix machine 2
    m2.name += " vp"
    m2.main_features["speed production"][0] = m2_production_speed
    m2.versions.pop("pk")
    values = m2.versions.pop("pk vp")
    m2.versions["vp"] = values
    return [m1, m2]


def _multiple_caps(machine: Machine):
    speed_production_str = machine.main_features["speed production"][0]
    splits = speed_production_str.split("bph", maxsplit=1)
    m1_production_speed = splits[0] + "bph"
    m2_production_speed = splits[1]
    m1 = deepcopy(machine)
    m2 = deepcopy(machine)
    # m1.name += "_capsuleDiameterLessEqual38"
    m1.main_features["speed production"][0] = m1_production_speed
    # m2.name += "_capsuleDiameterGreater38"
    m2.main_features["speed production"][0] = m2_production_speed
    return [m1, m2]


def _multiple_name(machine: Machine):
    m1 = deepcopy(machine)
    m2 = deepcopy(machine)
    names = machine.name.split("pp-c", maxsplit=1)
    m1.name = names[0] + "pp-c"
    m2.name = names[1].strip()
    return [m1, m2]


def _caps_application(machine: Machine):
    name = machine.name
    splits = name.split("-")
    base_name, first_version = splits.pop(0).split(" ")
    # base_name, first_version = splits[0].split(" ")
    splits.append(first_version)
    new_machines = []
    for version in splits:
        new_m = deepcopy(machine)
        new_m.name = base_name + " " + version
        for cap in machine.main_features["caps application"]:
            if f"{version} version" in cap:
                new_m.main_features["caps application"] = [cap.split("(")[0].strip()]
                break
        new_machines.append(new_m)
    return new_machines


def _fix_production_speed(machine: Machine):
    machine.main_features["speed production"] = ["up to 1.200 cpm / 72.000 cph"]
    return [machine]
