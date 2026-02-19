import contextlib
import io
import tempfile
from pathlib import Path
import unittest

from tailo_cli.__main__ import main as tailo_main
from tailo_cli.converter import hanzi_to_tailo
from tailo_cli.ipa import tailo_syllable_to_ipa, tailo_to_ipa
from tailo_cli.opencc_util import OpenCC, to_traditional
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
    @unittest.skipIf(OpenCC is None, "OpenCC not installed")
    def test_s2tw(self) -> None:
        self.assertEqual(to_traditional("简体中文", config="s2tw"), "簡體中文")


class TestIPA(unittest.TestCase):
    def test_tailo_syllable_to_ipa(self) -> None:
        self.assertEqual(tailo_syllable_to_ipa("tsi̍t"), "t͡sit̚⁸")
        self.assertEqual(tailo_syllable_to_ipa("ê"), "e⁵")
        self.assertEqual(tailo_syllable_to_ipa("buē"), "bue⁷")
        self.assertEqual(tailo_syllable_to_ipa("kiánn"), "kiã²")
        self.assertEqual(tailo_syllable_to_ipa("ia̍h"), "iaʔ⁸")

    def test_tailo_to_ipa_in_text(self) -> None:
        self.assertEqual(tailo_to_ipa("tsi̍t ê"), "t͡sit̚⁸ e⁵")
        self.assertEqual(tailo_to_ipa("{tsi̍t/it}"), "{t͡sit̚⁸/it̚⁴}")


class TestLookupCli(unittest.TestCase):
    def test_lookup_not_found_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "dict.csv"
            dict_path.write_text("word,chinese\nchit8,[一]\n", encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = tailo_main(["lookup", "--no-opencc", "--dict", str(dict_path), "嘛"])

            self.assertEqual(rc, 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("(not found) 嘛", stderr.getvalue())

    def test_lookup_best_effort_partial_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "dict.csv"
            dict_path.write_text("word,chinese\ntai5-uan5,[台灣]\n", encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = tailo_main(["lookup", "--no-opencc", "--dict", str(dict_path), "台灣嘛"])

            self.assertEqual(rc, 0)
            self.assertIn("(not found) 台灣嘛", stderr.getvalue())
            self.assertEqual(stdout.getvalue().strip(), "tâi-uân嘛")

    @unittest.skipIf(OpenCC is None, "OpenCC not installed")
    def test_lookup_opencc_does_not_reduce_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dict_path = Path(tmpdir) / "dict.csv"
            dict_path.write_text("word,chinese\ntai5-uan5,[台灣]\n", encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                rc = tailo_main(["lookup", "--dict", str(dict_path), "台灣嘛"])

            self.assertEqual(rc, 0)
            self.assertIn("(not found) 台灣嘛", stderr.getvalue())
            self.assertEqual(stdout.getvalue().strip(), "tâi-uân嘛")


if __name__ == "__main__":
    unittest.main()
