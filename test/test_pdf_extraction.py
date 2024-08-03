import unittest
from preprocessing.machine import Machine, PdfData
import pymupdf

from pathlib import Path
from src.preprocessing.pdf_extraction import PdfPreprocessing


class TestPdfExtraction(unittest.TestCase):

    # used to not truncate the difference output when tests fails
    # unittest.TestCase.maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.pages_dict = []
        pdf_path = Path("data/AROL_GENERAL_CATALOGUE_11.0_EN_20230215.pdf")
        doc = pymupdf.open(pdf_path)
        # IMPORTANT, PAGE STARTS AT 0 NOT 1
        pages_iterator: Iterable[Page] = doc.pages(start=5, stop=9)  # type: ignore (pages() -> Unknown, pyrigth is mad about it)\
        for page in pages_iterator:
            cls.pages_dict.append(page.get_text(option="dict", sort=True))

    def _move_to_desired_state(self, state_id: str):
        """Utility method used run the state machine until the desired state.
        Since the state given an input depends on the previous one, call this method to update the state of the
        state machine until the desired one. IMPORTANT: the state machine is designed to parse all the pdf,
        due to this is we try to parse more the one machine (application page + machine description page) it will
        stop to the first one met.

        Args:
            state_id (str): id of the state to reach

        Raises:
            Exception: if we encounter a state not experceted to encouter
            Exception: raised if we parse all the input given, this point is reached only if the desired state
            is not reached => raise error

        Returns:
            (int, int): indexes of the last page and block reached before reaching the desired state
        """
        self.state_machine = PdfPreprocessing()
        should_stop = self.state_machine.current_state.id == state_id
        for page_idx, page_dict in enumerate(self.pages_dict):
            for block_idx, block in enumerate(page_dict["blocks"]):
                if should_stop:
                    return page_idx, block_idx
                if block["type"] == 0:
                    match self.state_machine.current_state.id:
                        case "application_field":
                            self.state_machine.add_application(block)
                        case "machine_name":
                            self.state_machine.add_name(block)
                        case "main_feature" | "versions" | "options" | "dirty":
                            self.state_machine.add_info(block)
                        case _:
                            raise Exception(f"Found state not expected: {self.state_machine.current_state.id}")
                    should_stop = self.state_machine.current_state.id == state_id
        raise Exception("We should not reach this point, something went wrong")

    def _skip_bad_block(self, start_page_idx: int, start_block_idx: int, return_good_block=False):
        for cur_page_idx, page in enumerate(self.pages_dict[start_page_idx:], start=start_page_idx):
            block_idx = 0 if cur_page_idx > start_page_idx else start_block_idx
            for cur_block_idx, block in enumerate(page["blocks"][block_idx:], start=block_idx):
                # for idx, block in enumerate(self.pages_dict[page_idx:]["blocks"][block_idx:]):
                if block["type"] == 0:
                    return cur_page_idx, cur_block_idx
        raise Exception("There is not a good block left after the initial one")

    def test_machine_application_field(self):
        page_idx, block_idx = self._move_to_desired_state("application_field")
        self.assertEqual(self.state_machine.current_state.id, "application_field")
        self.state_machine.add_application(self.pages_dict[page_idx]["blocks"][block_idx])
        self.assertEqual(self.state_machine.current_machine.application_field, "pre-threaded plastic caps capper")
        self.assertEqual(self.state_machine.current_state.id, "machine_name")

    def test_machine_name(self):
        page_idx, block_idx = self._move_to_desired_state("machine_name")
        self.assertEqual(self.state_machine.current_state.id, "machine_name")
        cur_page_idx, cur_block_idx = self._skip_bad_block(page_idx, block_idx)
        self.state_machine.add_name(self.pages_dict[cur_page_idx]["blocks"][cur_block_idx])
        self.assertEqual(self.state_machine.current_machine.name, "euro pk")
        self.assertEqual(self.state_machine.current_state.id, "main_feature")

    def test_machine_main_features(self):
        main_features: PdfData = {
            "speed production": ["up to 1.500 bpm / 90.000 bph"],
            "main market": ["beverage", "food", "chemical", "pharmaceutical"],
            "caps application": ["sport and flat pre-threaded plastic caps"],
            "closure heads": ["magnetic syncronous heads", "hysteresis heads"],
        }
        page_idx, block_idx = self._move_to_desired_state("main_feature")
        self.assertEqual(self.state_machine.current_state.id, "main_feature")
        cur_page_idx, cur_block_idx = self._skip_bad_block(page_idx, block_idx)
        for block in self.pages_dict[cur_page_idx]["blocks"][cur_block_idx:]:
            if self.state_machine.current_state.id != "main_feature":
                break
            self.state_machine.add_info(block)
        self.assertDictEqual(self.state_machine.current_machine.main_features, main_features)
        self.assertEqual(self.state_machine.current_state.id, "versions")

    def test_machine_versions(self):
        versions = {
            "standard": ["structure with painted steel components. not washable"],
            "inox external surfaces (i.e.s.)": [
                "external stainless steel components. suitable for washing of the capping zone"
            ],
            "washable": [
                "stainless steel components. complete washing of the capper is possible (thanks to gaskets and labyrinths)"
            ],
        }
        page_idx, block_idx = self._move_to_desired_state("versions")
        self.assertEqual(self.state_machine.current_state.id, "versions")
        cur_page_idx, cur_block_idx = self._skip_bad_block(page_idx, block_idx)
        for block in self.pages_dict[cur_page_idx]["blocks"][cur_block_idx:]:
            if self.state_machine.current_state.id != "versions":
                break
            self.state_machine.add_info(block)
        self.assertDictEqual(self.state_machine.current_machine.versions, versions)
        self.assertEqual(self.state_machine.current_state.id, "options")

    def test_machine_options(self):
        options = {
            "on caps chute": [
                "overturned caps automatic ejector (a.e.d.)",
                "n 2 injection device",
                "caps washing",
                "ionizer/dust extraction",
                "uv lamp",
                "bottle neck cleaning",
                "steam injection",
            ],
            "quick format change": [
                "sorter (manual or automatic)",
                "caps chute",
                "pick & place",
                "containers handling",
            ],
            "other": [
                "motorized height adjustment (standard for “free standing” version)",
                "centralized lubrication",
                "multibody",
                "caps elevator",
                "caps buffer: twin hopper, flat buffer",
            ],
        }
        page_idx, block_idx = self._move_to_desired_state("options")
        self.assertEqual(self.state_machine.current_state.id, "options")
        cur_page_idx, cur_block_idx = self._skip_bad_block(page_idx, block_idx)
        for block in self.pages_dict[cur_page_idx]["blocks"][cur_block_idx:]:
            if self.state_machine.current_state.id != "options":
                break
            self.state_machine.add_info(block)
        self.assertDictEqual(self.state_machine.current_machine.other_info, options)
        # we can move to a bunch of different state, understand how test it
        # self.assertEqual(self.state_machine.current_state.id, "options")

    def test_finish_machine_info_page(self):
        mock_machine = Machine()
        mock_machine.application_field = "pre-threaded plastic caps capper"
        mock_machine.name = "euro pk"
        page_idx, block_idx = self._move_to_desired_state("options")
        self.assertEqual(self.state_machine.current_state.id, "options")
        cur_page_idx, cur_block_idx = self._skip_bad_block(page_idx, block_idx)
        for idx, page in enumerate(self.pages_dict[cur_page_idx:], start=cur_page_idx):
            cur_block_idx = 0 if idx > cur_page_idx else cur_block_idx
            for block in page["blocks"][cur_block_idx:]:
                # for block in page["blocks"]:
                if block["type"] != 0:
                    continue
                if self.state_machine.current_state.id == "application_field":
                    self.state_machine.add_application(block)
                elif self.state_machine.current_state.id == "options" or self.state_machine.current_state.id == "dirty":
                    self.state_machine.add_info(block)
                elif self.state_machine.current_state.id == "machine_name":
                    self.state_machine.add_name(block)
        self.assertEqual(self.state_machine.current_machine, mock_machine)


if __name__ == "__main__":
    # verbosity set the log level printed (0: quiet, 1: normal, 2: verbose)
    unittest.main(verbosity=1)
