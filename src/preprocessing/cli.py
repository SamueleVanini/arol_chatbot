from collections import defaultdict
from copy import deepcopy
import json
import pymupdf
import csv

from typing import Callable, Generator
from pathlib import Path
from argparse import ArgumentParser, Namespace
from tqdm import tqdm
from .pdf_extraction import PdfPreprocessing, UNICODE_DOT
from .machine import MachineEncoder, Machine
from .utilities import fix_machines
from core.config import configure_system

from langsmith import Client


def dataset_preprocessing_cli(args: Namespace):
    csv_path = Path(args.file_path)

    if not csv_path.exists():
        raise ValueError(f"The requested path does not exists, path: {csv_path}")

    with open(csv_path, mode="r") as csv_file:
        reader = csv.reader(csv_file)
        dataset = defaultdict(list)
        next(reader)  # skip the first line
        for row in reader:
            question = row[0]
            if question.startswith("#"):
                continue
            matchs = []
            for match in row[1:]:
                if match == "NULL":
                    break
                matchs.append(match)
            dataset["input"].append({"question": question})
            dataset["output"].append({"matchs": matchs})

    configure_system()

    client = Client()
    langsmith_ds = client.create_dataset(args.name, description=args.description)
    client.create_examples(
        inputs=dataset["input"],
        outputs=dataset["output"],
        dataset_id=langsmith_ds.id,
    )


def pdf_preprocessing_cli(args: Namespace):
    pdf_path = Path(args.file_path)
    doc = pymupdf.open(pdf_path)
    state_machine = PdfPreprocessing()
    # doc.pages() follow the same convension of bult-in range() function => stop is excluded
    pages_gen: Generator[pymupdf.Page] = doc.pages(start=args.start_page - 1, stop=args.end_page)  # type: ignore (pages() -> Unknown, pyrigth is mad about it)\
    total_page_parsed = (args.end_page - args.start_page) + 1
    for page in tqdm(pages_gen, total=total_page_parsed):
        page_structure = page.get_text(option="dict", sort=True)  # type: ignore
        for block in page_structure["blocks"]:
            if block["type"] == 0:
                state_machine.parse_block(block)
    state_machine.go_to_final_state()

    output_path = Path(args.file_out_path)
    with open(output_path, mode="w") as out_f:
        machines = []
        for machine_list in state_machine.machines.values():
            machines.extend(machine_list)
        machines_fixed = fix_machines(machines)
        json.dump(machines_fixed, out_f, cls=MachineEncoder)
    print(f"{total_page_parsed} pages has been processed")


parser = ArgumentParser(
    prog="arol-preprocessing",
    description="CLI utils to perform pre-processing operation",
    epilog="Program finished",
)

subparser = parser.add_subparsers(title="commands", description="commands available in the cli tool")

pdf_extraction = subparser.add_parser("pdf_ext", help="parse Arol PDF catalog into json file")
pdf_extraction.set_defaults(func=pdf_preprocessing_cli)

pdf_config = pdf_extraction.add_argument_group("config")
pdf_config.add_argument(
    "-f",
    "--file-path",
    type=str,
    required=False,
    default="data/AROL_GENERAL_CATALOGUE_11.0_EN_20230215.pdf",
    help="Path for the pdf catalog to parse",
)

pdf_config.add_argument(
    "-f-o",
    "--file-out-path",
    type=str,
    required=False,
    default="data/processed_catalog.json",
    help="Path for the output json file",
)

pdf_general = pdf_extraction.add_argument_group("pages")
pdf_general.add_argument(
    "-s",
    "--start-page",
    type=int,
    required=False,
    default=6,
    help="Starting page for the parsing (assuming the initial catalog's page is 1)",
)
pdf_general.add_argument("-e", "--end-page", type=int, required=False, default=65)

dataset_creation = subparser.add_parser("dataset", help="create a dataset given a csv file")
dataset_creation.set_defaults(func=dataset_preprocessing_cli)


ds_config = dataset_creation.add_argument_group("csv config")
ds_config.add_argument(
    "-f",
    "--file-path",
    type=str,
    required=False,
    default="data/dataset.csv",
    help="Path for the csv file to use",
)

ds_general = dataset_creation.add_argument_group("dataset config")
ds_general.add_argument(
    "-n",
    "--name",
    type=str,
    required=False,
    default="DEBUG",
    help="Name of the dataset to create",
)
ds_general.add_argument(
    "-d",
    "--description",
    type=str,
    required=False,
    default="DEBUG DESCRIPTION",
    help="Description of the dataset to create",
)


def main_preprocessing_cli():
    args = parser.parse_args()
    args.func(args)
