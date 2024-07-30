import json
import pymupdf

from pathlib import Path
from .pdf_extraction_refactoring import PdfPreprocessing


def main_preprocessing_cli():
    pdf_path = Path("data/AROL_GENERAL_CATALOGUE_11.0_EN_20230215.pdf")
    doc = pymupdf.open(pdf_path)
    state_machine = PdfPreprocessing()
    # doc.pages() follow the same convension of bult-in range() function => stop is excluded
    pages_iterator: Iterable[Page] = doc.pages(start=6, stop=64)  # type: ignore (pages() -> Unknown, pyrigth is mad about it)\
    for page in pages_iterator:
        page_structure = page.get_text(option="dict", sort=True)
        for block in page_structure["blocks"]:
            if block["type"] == 0:
                match state_machine.current_state.id:
                    case "application_field":
                        state_machine.add_application(block)
                    case "machine_names":
                        state_machine.add_name(block)
                    case "main_feature" | "versions" | "options" | "dirty":
                        state_machine.add_info(block)
                    case _:
                        raise Exception(f"Found state not expected: {state_machine.current_state.id}")
    state_machine.go_to_final_state()

    output_path = Path("data/processed_catalog.json")
    with open(output_path, mode="w") as out_f:
        for k, v in state_machine.machines.items():
            json.dump({k: v.__dict__}, out_f)
    print(f"{len(pages_iterator)} pages has been processed")
