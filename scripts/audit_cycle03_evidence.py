#!/usr/bin/env python3
"""Build and validate the fail-closed Cycle 03 evidence audit.

The source PDFs and workbooks remain outside this public repository.  This
script records their verified identities, writes non-infringing table
transcriptions, and enforces the ten-gate admission rule.  It does not rerun a
CMB model because no Cycle 03 candidate exposes the complete historical input
and control package needed for a defensible rerun.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from typing import Iterable


GATE_COLUMNS = tuple(f"gate_{index}" for index in range(1, 11))
ALLOWED_GATE_VALUES = {"yes", "partial", "no"}

EXPECTED_SOURCE_FILES = {
    "BARRETT-DISSERTATION-2016.pdf": {
        "bytes": 16428674,
        "sha256": "abfbac7f88ff8f73ef2724b988e3418c8515950ada4ace5526293b03f9288853",
        "md5": "a0d4fcd1b559be6ebb10e95f8c48fa42",
    },
    "APHH_Beijing_radiocarbon_extended_Gelencser.xlsx": {
        "bytes": 21633,
        "sha256": "ac2e725312e8339db3770583280b55768336f324d727b3bfaecd8b6aed90cd6f",
        "md5": "f1be3a5a0cb61ff9f753254506e8ee81",
    },
    "Barrow_2015_ACS_supporting_information.pdf": {
        "bytes": 2216864,
        "sha256": "14aa663cb2a1b0d8c83d5c8249f47234123bde349bff48090cb03971d1087a65",
        "md5": "a2f9068e8e32c347b65756668b78e1e3",
    },
    "Barrett_2015_ESandT_Supporting_Information_official_ACS.pdf": {
        "bytes": 2250685,
        "sha256": "05484065cba94746e4f048d6dd34d5c9cbf16552d876428f9c2801fb446fc165",
        "md5": "2982a3584952ab02062abc4ea920766d",
    },
    "Chengdu_organic_components_PM25.xlsx": {
        "bytes": 29568,
        "sha256": "daa48d6e1c8f0aa3ee0ae2f70d75922445f657eec91fa9cbdc6fc57c9cbad021",
        "md5": "1dddd55281b5a84abc3504386daebda9",
    },
    "DOE-SC-ARM-14-017_BBCSI_Final_Report.pdf": {
        "bytes": 864441,
        "sha256": "be4152fa7b41671d65838c13336ec31f3d96d1ae1cf863b39bbe76f2a9196d25",
        "md5": "314b5c885d47bef9b5d367152ce451c2",
    },
    "Fairbanks_CMB_Report_Univ_MT_Final_030113.pdf": {
        "bytes": 797536,
        "sha256": "d546f2eec1fe69f871302cee0ec01190fa5add438875a83b1b08b0e98e1d1c03",
        "md5": "ab2761ae663b1d3e59dc938f1ff9c8f2",
    },
    "Tian_Chengdu_CMB_preprint.pdf": {
        "bytes": 721836,
        "sha256": "cc74f7341a50d215040fabab4570e8ffa276278b9944734df40cdbd1689e9226",
        "md5": "13bd1775a2ed1f722c030d141bcfebac",
    },
    "Xu_2021_APHH_Beijing_multi_method.pdf": {
        "bytes": 966170,
        "sha256": "fb1759c07dc3813bfc256173892742e3c4093442d0d972cb37bde531fe4d6d3b",
        "md5": "2a8c3bc7a031c118c60e46e103732431",
    },
}


# Manual transcription of Ward et al. (2013-03-01), Table 12.  The table was
# checked against the rendered report pages 19--20.  CMB values marked None are
# explicitly printed as "No CMB Conducted" in the source.
FAIRBANKS_TABLE12 = (
    ("State Building", "2011-11-17", "32.8", "39.3", "47.3", "73.9"),
    ("State Building", "2011-11-20", "34.2", "36.0", "43.4", None),
    ("State Building", "2011-12-17", "37.3", "33.9", "40.9", "81.1"),
    ("State Building", "2011-12-29", "31.8", "32.7", "39.4", "77.7"),
    ("State Building", "2012-01-01", "23.3", "30.0", "36.1", None),
    ("State Building", "2012-01-04", "14.3", "33.1", "39.9", "79.1"),
    ("State Building", "2012-01-28", "36.8", "14.2", "17.1", "65.0"),
    ("State Building", "2012-02-18", "25.6", "21.4", "25.8", "70.9"),
    ("State Building", "2012-03-10", "9.5", "22.9", "27.6", "62.8"),
    ("State Building", "2012-03-19", "10.6", "22.8", "27.5", "65.0"),
    ("North Pole", "2011-11-20", "82.6", "66.6", "78.1", "86.9"),
    ("North Pole", "2011-12-17", "36.4", "45.3", "54.5", "90.1"),
    ("North Pole", "2011-12-26", "38.3", "37.9", "45.0", "92.1"),
    ("North Pole", "2011-12-29", "34.1", "55.3", "66.6", "90.0"),
    ("North Pole", "2012-01-01", "33.5", "37.8", "45.5", "89.8"),
    ("North Pole", "2012-01-28", "64.9", "33.1", "39.8", "88.8"),
    ("North Pole", "2012-02-18", "29.2", "42.3", "51.0", "88.9"),
    ("North Pole", "2012-03-04", "26.0", "70.6", "82.0", "69.9"),
    ("North Pole", "2012-03-10", "11.1", "69.6", "80.0", "81.3"),
    ("North Pole", "2012-03-19", "18.3", "69.3", "82.4", "84.3"),
    ("RAMS", "2011-12-26", "45.0", "21.0", "25.3", "84.1"),
    ("RAMS", "2011-12-29", "24.6", "48.7", "58.7", "77.9"),
    ("RAMS", "2012-01-01", "21.3", "46.8", "56.3", "48.9"),
    ("RAMS", "2012-02-18", "25.9", "35.7", "43.0", "49.2"),
    ("NCORE", "2011-11-17", "38.1", "36.2", "43.6", "81.3"),
    ("NCORE", "2011-11-20", "30.4", "49.1", "59.2", "61.4"),
    ("NCORE", "2011-12-17", "29.7", "44.6", "53.7", "54.5"),
    ("NCORE", "2011-12-26", "24.9", "41.8", "50.3", "44.3"),
    ("NCORE", "2011-12-29", "23.6", "49.1", "59.1", "68.5"),
    ("NCORE", "2012-01-01", "28.0", "37.5", "45.2", "83.3"),
    ("NCORE", "2012-01-04", "33.6", "10.2", "12.3", "92.8"),
    ("NCORE", "2012-01-28", "28.1", "29.1", "35.0", "73.8"),
    ("NCORE", "2012-02-18", "26.9", "38.1", "45.9", "49.8"),
    ("NCORE", "2012-03-04", "13.1", "42.6", "51.3", "56.4"),
    ("NCORE", "2012-03-10", "9.8", "46.9", "56.6", "69.4"),
    ("NCORE", "2012-03-19", "12.1", "37.0", "44.6", "69.6"),
    ("NPF3", "2012-03-04", "37.4", "76.9", "87.2", "80.8"),
    ("NPF3", "2012-03-10", "20.5", "56.5", "68.1", "86.4"),
    ("NPF3", "2012-03-19", "27.8", "60.0", "72.3", "67.7"),
)


# Exact four-interval overlap between Barrett et al. Tables S1 and S2.
# Values are concentration +/- uncertainty in micrograms C per cubic metre.
BARROW_CROSSWALK = (
    (
        "2013-01-18/2013-01-25",
        ("0.052", "0.009", "0.072", "0.012"),
        ("0.025", "0.004", "0.005", "0.002"),
        ("0.168", "0.012", "0.089", "0.011"),
        ("0.252", "0.018", "0.036", "0.017"),
    ),
    (
        "2013-02-01/2013-02-08",
        ("0.048", "0.007", "0.053", "0.012"),
        ("0.019", "0.003", "0.016", "0.006"),
        ("0.112", "0.017", "0.046", "0.008"),
        ("0.177", "0.027", "0.110", "0.052"),
    ),
    (
        "2013-02-08/2013-02-15",
        ("0.067", "0.011", "0.072", "0.017"),
        ("0.030", "0.005", "0.027", "0.010"),
        ("0.323", "0.018", "0.060", "0.010"),
        ("0.417", "0.023", "0.190", "0.070"),
    ),
    (
        "2013-02-25/2013-03-01",
        ("0.018", "0.006", "0.034", "0.006"),
        ("0.018", "0.006", "0.003", "0.001"),
        ("0.060", "0.009", "0.016", "0.003"),
        ("0.100", "0.016", "0.021", "0.008"),
    ),
)


# Exact radiocarbon subset disclosed in Birmingham eData 572.  Xu et al.
# explicitly state that their Table 2 method comparison is restricted to these
# same radiocarbon-analyzed samples, but only group aggregates are public.
APHH_SAMPLES = (
    ("IAP", "winter", "2016-11-22"),
    ("IAP", "winter", "2016-11-24"),
    ("IAP", "winter", "2016-11-26"),
    ("IAP", "winter", "2016-12-01"),
    ("IAP", "winter", "2016-12-02"),
    ("IAP", "winter", "2016-12-03"),
    ("IAP", "winter", "2016-12-04"),
    ("IAP", "summer", "2017-05-24"),
    ("IAP", "summer", "2017-05-26"),
    ("IAP", "summer", "2017-05-27"),
    ("IAP", "summer", "2017-06-10"),
    ("IAP", "summer", "2017-06-16"),
    ("IAP", "summer", "2017-06-17"),
    ("PG", "winter", "2016-11-22"),
    ("PG", "winter", "2016-11-24"),
    ("PG", "winter", "2016-11-26"),
    ("PG", "winter", "2016-12-01"),
    ("PG", "winter", "2016-12-02"),
    ("PG", "winter", "2016-12-03"),
    ("PG", "winter", "2016-12-04"),
    ("PG", "summer", "2017-05-26"),
    ("PG", "summer", "2017-05-27"),
    ("PG", "summer", "2017-06-10"),
    ("PG", "summer", "2017-06-16"),
    ("PG", "summer", "2017-06-17"),
)


def sha(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source_files(input_dir: Path) -> list[dict[str, object]]:
    """Verify any present source file and fail on an identity mismatch."""

    results: list[dict[str, object]] = []
    for name, expected in EXPECTED_SOURCE_FILES.items():
        path = input_dir / name
        if not path.exists():
            results.append({"file": name, "status": "not_present"})
            continue
        actual = {
            "bytes": path.stat().st_size,
            "sha256": sha(path, "sha256"),
            "md5": sha(path, "md5"),
        }
        if actual != expected:
            raise ValueError(f"identity mismatch for {path}: {actual} != {expected}")
        results.append({"file": name, "status": "verified", **actual})
    return results


def fairbanks_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for site, date, mass, low_text, high_text, cmb_text in FAIRBANKS_TABLE12:
        low = Decimal(low_text)
        high = Decimal(high_text)
        row = {
            "site": site,
            "date": date,
            "pm25_ug_m3": mass,
            "radiocarbon_wood_smoke_min_pct": low_text,
            "radiocarbon_wood_smoke_max_pct": high_text,
            "cmb_wood_smoke_pct": cmb_text or "",
            "cmb_status": "reported" if cmb_text is not None else "not_conducted",
            "cmb_relative_to_14c_interval": "",
            "cmb_minus_14c_midpoint_pp": "",
            "distance_to_14c_interval_pp": "",
            "source_id": "ward_2013_0301_wayback",
            "source_table": "Table 12",
        }
        if cmb_text is not None:
            cmb = Decimal(cmb_text)
            midpoint = (low + high) / Decimal("2")
            if cmb < low:
                relation = "below"
                distance = low - cmb
            elif cmb > high:
                relation = "above"
                distance = cmb - high
            else:
                relation = "inside"
                distance = Decimal("0")
            row["cmb_relative_to_14c_interval"] = relation
            row["cmb_minus_14c_midpoint_pp"] = f"{cmb - midpoint:.2f}"
            row["distance_to_14c_interval_pp"] = f"{distance:.1f}"
        rows.append(row)
    return rows


def barrow_rows() -> list[dict[str, str]]:
    endpoints = (
        "fossil_ec",
        "contemporary_ec",
        "fossil_oc",
        "contemporary_oc",
    )
    rows: list[dict[str, str]] = []
    for interval, *values in BARROW_CROSSWALK:
        row = {
            "date_interval": interval,
            "exact_interval_match": "yes",
            "independent_reference": "radiocarbon",
            "endpoint_mapping": "published_fossil_contemporary_OC_EC",
            "profile_choice_frozen_before_reference": "no",
            "disposition": "HOLD",
            "source_id": "barrett_2015_si",
            "source_tables": "S1;S2",
        }
        for endpoint, (reference, reference_u, cmb, cmb_u) in zip(
            endpoints, values, strict=True
        ):
            row[f"radiocarbon_{endpoint}_ug_m3"] = reference
            row[f"radiocarbon_{endpoint}_uncertainty"] = reference_u
            row[f"cmb_{endpoint}_ug_m3"] = cmb
            row[f"cmb_{endpoint}_uncertainty"] = cmb_u
            row[f"cmb_minus_radiocarbon_{endpoint}_ug_m3"] = (
                f"{Decimal(cmb) - Decimal(reference):.3f}"
            )
        rows.append(row)
    return rows


def aphh_rows() -> list[dict[str, str]]:
    counts = {
        ("IAP", "winter"): 7,
        ("IAP", "summer"): 6,
        ("PG", "winter"): 7,
        ("PG", "summer"): 5,
    }
    return [
        {
            "site": site,
            "season": season,
            "date": date,
            "radiocarbon_record_public": "yes",
            "included_in_cmb_comparison_group": "yes",
            "cmb_group_id": f"{site}_{season}",
            "cmb_group_n": str(counts[(site, season)]),
            "sample_level_cmb_value_public": "no",
            "sample_level_endpoint_mapping_public": "no",
            "disposition": "HOLD",
            "source_ids": "aphh_edata_572;xu_2021_multimethod",
        }
        for site, season, date in APHH_SAMPLES
    ]


def write_csv(path: Path, rows: Iterable[dict[str, str]]) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError(f"cannot write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(materialized[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(materialized)


def validate_candidate_matrix(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("candidate matrix is empty")
    for row in rows:
        candidate = row["candidate_id"]
        for gate in GATE_COLUMNS:
            if row[gate] not in ALLOWED_GATE_VALUES:
                raise ValueError(f"{candidate}: invalid {gate}={row[gate]!r}")
        all_yes = all(row[gate] == "yes" for gate in GATE_COLUMNS)
        if row["disposition"] == "KEEP" and not all_yes:
            raise ValueError(f"{candidate}: KEEP with an incomplete gate")
        if all_yes and row["disposition"] != "KEEP":
            raise ValueError(f"{candidate}: all gates pass but disposition is not KEEP")
    counts = {
        status: sum(row["disposition"] == status for row in rows)
        for status in ("KEEP", "HOLD", "REMOVE")
    }
    return {
        "candidate_count": len(rows),
        "disposition_counts": counts,
        "overall_decision": "KEEP" if counts["KEEP"] else "HOLD",
        "manuscript_change_authorized": False,
    }


def validate_crosswalks() -> dict[str, object]:
    fairbanks = fairbanks_rows()
    barrow = barrow_rows()
    aphh = aphh_rows()
    reported = [row for row in fairbanks if row["cmb_status"] == "reported"]
    relations = {
        relation: sum(
            row["cmb_relative_to_14c_interval"] == relation for row in reported
        )
        for relation in ("above", "inside", "below")
    }
    differences = [
        Decimal(row["cmb_minus_14c_midpoint_pp"]) for row in reported
    ]
    mean_difference = sum(differences) / Decimal(len(differences))
    mean_absolute_error = sum(abs(value) for value in differences) / Decimal(
        len(differences)
    )
    if len(fairbanks) != 39 or len(reported) != 37:
        raise ValueError("unexpected Fairbanks Table 12 row counts")
    if relations != {"above": 32, "inside": 4, "below": 1}:
        raise ValueError(f"unexpected Fairbanks Table 12 relations: {relations}")
    if len(barrow) != 4 or not all(
        row["exact_interval_match"] == "yes" for row in barrow
    ):
        raise ValueError("unexpected Barrow exact-case crosswalk")
    if len(aphh) != 25 or any(
        row["sample_level_cmb_value_public"] != "no" for row in aphh
    ):
        raise ValueError("unexpected APHH radiocarbon-subset crosswalk")
    return {
        "fairbanks_table12_rows": len(fairbanks),
        "fairbanks_reported_cmb_rows": len(reported),
        "fairbanks_cmb_vs_14c_interval": relations,
        "fairbanks_mean_cmb_minus_14c_midpoint_pp": f"{mean_difference:.2f}",
        "fairbanks_mae_to_14c_midpoint_pp": f"{mean_absolute_error:.2f}",
        "barrow_exact_interval_rows": len(barrow),
        "aphh_exact_radiocarbon_subset_rows": len(aphh),
    }


def build(root: Path, input_dir: Path | None = None) -> dict[str, object]:
    output = root / "outputs" / "cycle03"
    write_csv(output / "fairbanks_2011_2012_table12_crosswalk.csv", fairbanks_rows())
    write_csv(output / "barrow_2012_2013_exact_case_crosswalk.csv", barrow_rows())
    write_csv(output / "aphh_beijing_radiocarbon_sample_crosswalk.csv", aphh_rows())
    report: dict[str, object] = {
        "schema_version": 1,
        "admission": validate_candidate_matrix(output / "candidate_dataset_matrix.csv"),
        "crosswalks": validate_crosswalks(),
    }
    if input_dir is not None:
        report["source_file_verification"] = verify_source_files(input_dir)
    target = output / "admission_audit.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="optional out-of-repository directory containing retrieved sources",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    report = build(root, args.input_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
