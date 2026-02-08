import unittest

from tailo_cli.converter import hanzi_to_tailo
from tailo_cli.opencc_util import to_traditional
from tailo_cli.romanize import convert_numeric_poj_in_text, convert_poj_word_to_tailo


class TestRomanize(unittest.TestCase):
    def test_convert_poj_word_to_tailo_basic(self) -> None:
        self.assertEqual(convert_poj_word_to_tailo("chit8"), "tsi̍t")
        self.assertEqual(convert_poj_word_to_tailo("boe7"), "buē")
        self.assertEqual(convert_poj_word_to_tailo("toa7"), "tuā")
        self.assertEqual(convert_poj_word_to_tailo("kiaN2"), "kiánn")

    def test_convert_numeric_poj_in_text(self) -> None:
        self.assertEqual(convert_numeric_poj_in_text("foo chit8 bar"), "foo tsi̍t bar")


class TestHanziConversion(unittest.TestCase):
    def test_longest_match_and_spacing(self) -> None:
        mapping = {
            "一": ["tsi̍t", "it"],
            "大": ["tuā"],
            "囝": ["kiánn"],
            "一大": ["tsi̍t-tuā"],
        }
        out = hanzi_to_tailo("一大囝", mapping, max_key_len=2)
        self.assertEqual(out, "tsi̍t-tuā kiánn")

    def test_ambiguous_all(self) -> None:
        mapping = {"一": ["tsi̍t", "it"]}
        out = hanzi_to_tailo("一", mapping, max_key_len=1, ambiguous="all")
        self.assertEqual(out, "{tsi̍t/it}")

    def test_unknown_mark(self) -> None:
        mapping = {"一": ["tsi̍t"]}
        out = hanzi_to_tailo("二", mapping, max_key_len=1, unknown="mark")
        self.assertEqual(out, "<?>")


class TestOpenCC(unittest.TestCase):
    def test_s2tw(self) -> None:
        self.assertEqual(to_traditional("简体中文", config="s2tw"), "簡體中文")


if __name__ == "__main__":
    unittest.main()
