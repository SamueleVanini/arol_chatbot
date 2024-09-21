import json
import pymupdf

from typing import Generator
from pathlib import Path
from argparse import ArgumentParser
from tqdm import tqdm
from .pdf_extraction import PdfPreprocessing
from .machine import MachineEncoder

parser = ArgumentParser(
    prog="catalog-parse-cli",
    description="CLI utils to parse Arol PDF catalog into json file",
    epilog="Program finished",
)

config = parser.add_argument_group("config")
config.add_argument(
    "-f",
    "--file-path",
    type=str,
    required=False,
    default="data/AROL_GENERAL_CATALOGUE_11.0_EN_20230215.pdf",
    help="Path for the pdf catalog to parse",
)

config.add_argument(
    "-f-o",
    "--file-out-path",
    type=str,
    required=False,
    default="data/processed_catalog.json",
    help="Path for the output json file",
)

general = parser.add_argument_group("pages")
general.add_argument(
    "-s",
    "--start-page",
    type=int,
    required=False,
    default=6,
    help="Starting page for the parsing (assuming the initial catalog's page is 1)",
)
general.add_argument("-e", "--end-page", type=int, required=False, default=65)


def main_preprocessing_cli():
    args = parser.parse_args()
    pdf_path = Path(args.file_path)
    doc = pymupdf.open(pdf_path)
    state_machine = PdfPreprocessing()
    # doc.pages() follow the same convension of bult-in range() function => stop is excluded
    pages_gen: Generator[pymupdf.Page] = doc.pages(start=args.start_page - 1, stop=args.end_page)  # type: ignore (pages() -> Unknown, pyrigth is mad about it)\
    total_page_parsed = (args.end_page - args.start_page) + 1
    for page in tqdm(pages_gen, total=total_page_parsed):
        page_structure = page.get_text(option="dict", sort=True)
        for block in page_structure["blocks"]:
            if block["type"] == 0:
                state_machine.parse_block(block)
    state_machine.go_to_final_state()

    output_path = Path(args.file_out_path)
    with open(output_path, mode="w") as out_f:
        machines = []
        for machine_list in state_machine.machines.values():
            machines.extend(machine_list)
        json.dump(machines, out_f, cls=MachineEncoder)
    print(f"{total_page_parsed} pages has been processed")
