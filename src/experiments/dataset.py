from collections import defaultdict
import csv
import json
from pathlib import Path
from icecream import ic

# CSV_FILE_PATH = "data/test.csv"
CSV_FILE_PATH = "data/new_benchmark_arol_chatbot.csv"
JSON_FILE_PATH = "data/processed_catalog.json"


def get_ds_machines() -> set[str]:
    csv_path = Path(CSV_FILE_PATH)
    with open(csv_path, mode="r") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the first line
        matchs = []
        for row in reader:
            question = row[0]
            if question.startswith("#"):
                continue
            for match in row[1:]:
                if match == "NULL":
                    break
                matchs.append(match.lower().strip())
    return set(matchs)


def get_pdf_machines() -> set[str]:
    json_path = Path(JSON_FILE_PATH)
    with open(json_path, mode="r") as json_file:
        data = json.load(json_file)
    names = set()
    for machine in data:
        names.add(machine["name"])
    return names


if __name__ == "__main__":
    ds = get_ds_machines()
    machines = get_pdf_machines()
    ic(("dataset len", len(ds)))
    ic(("pdf len", len(machines)))

    machines_missmatch = 0
    for m_ds in ds:
        if m_ds not in machines:
            ic(m_ds)
            machines_missmatch += 1
    ic(machines_missmatch)
    ic(machines)
