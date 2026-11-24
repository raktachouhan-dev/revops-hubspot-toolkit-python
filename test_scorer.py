import csv
import pathlib

from toolkit.scorer import score_account, to_bool

CSV = pathlib.Path(__file__).parent.parent / "sample-data" / "pe_firms_sample.csv"
EXPECTED = {"Northfield Capital Partners": (100, "A"), "Alder Credit Advisors": (89, "A"),
            "Summit Ridge Credit": (82, "A"), "Meridian Buyout Group": (69, "B"),
            "Harbor Lane Real Assets": (52, "B"), "Brightwater Growth": (47, "B"),
            "Quill Street Capital": (28, "C"), "Kestrel Ventures": (18, "C")}


def test_sample_data_matches_published_results():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    got = {r["name"]: (score_account(r).score, score_account(r).tier) for r in rows}
    assert got == EXPECTED


def test_string_false_is_not_true():
    assert to_bool("false") is False and to_bool("true") is True
