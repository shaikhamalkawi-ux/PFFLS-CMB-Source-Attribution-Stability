#!/usr/bin/env python3
"""Recover the public, date-resolved Fairbanks evidence without overclaiming it.

The script extracts Appendix C tables from the Ward ADEC PDF with Poppler's
``pdftotext`` and joins the State Building dates to EPA AirData SPEC archives.
It deliberately labels EPA-versus-OMNI rows as profile-*system* sensitivity:
the OMNI runs introduce No. 2 fuel oil and therefore do not hold the source
universe fixed.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess
import zipfile


EPA_FIELDS = (
    "pm25_mass",
    "sulfate",
    "sulfate_se",
    "ammonium_nitrate",
    "ammonium_nitrate_se",
    "autos",
    "autos_se",
    "diesel",
    "diesel_se",
    "wood_smoke",
    "wood_smoke_se",
)
OMNI_FIELDS = (
    "pm25_mass",
    "sulfate",
    "sulfate_se",
    "ammonium_nitrate",
    "ammonium_nitrate_se",
    "no2_fuel_oil",
    "no2_fuel_oil_se",
    "wood_smoke",
    "wood_smoke_se",
)
REVISED_OMNI_FIELDS = (
    "pm25_mass",
    "sulfate",
    "sulfate_se",
    "ammonium_nitrate",
    "ammonium_nitrate_se",
    "no2_fuel_oil",
    "no2_fuel_oil_se",
    "autos",
    "autos_se",
    "diesel",
    "diesel_se",
    "wood_smoke",
    "wood_smoke_se",
)
ALL_RESULT_FIELDS = REVISED_OMNI_FIELDS


@dataclass(frozen=True)
class TableSpec:
    site: str
    system: str
    first_page: int
    last_page: int
    fields: tuple[str, ...]


TABLES = (
    TableSpec("state_building", "epa", 110, 111, EPA_FIELDS),
    TableSpec("state_building", "omni", 112, 113, OMNI_FIELDS),
    TableSpec("state_building", "omni_revised", 114, 115, REVISED_OMNI_FIELDS),
    TableSpec("north_pole", "epa", 116, 116, EPA_FIELDS),
    TableSpec("north_pole", "omni", 117, 117, OMNI_FIELDS),
    TableSpec("peger_road", "epa", 120, 120, EPA_FIELDS),
    TableSpec("peger_road", "omni", 121, 121, OMNI_FIELDS),
    TableSpec("peger_road", "omni_revised", 122, 122, REVISED_OMNI_FIELDS),
)


# Table 5 of the ADEC report defines the 43 measured CMB species as 36
# elements, five ions, organic carbon, and elemental carbon.  These are their
# AQS parameter codes in the 2008/2009 SPEC archives.
AQS_CMB_SPECIES = {
    "88140": "Magnesium",
    "88104": "Aluminum",
    "88165": "Silicon",
    "88152": "Phosphorus",
    "88169": "Sulfur",
    "88115": "Chlorine",
    "88180": "Potassium",
    "88111": "Calcium",
    "88161": "Titanium",
    "88164": "Vanadium",
    "88112": "Chromium",
    "88132": "Manganese",
    "88126": "Iron",
    "88136": "Nickel",
    "88114": "Copper",
    "88167": "Zinc",
    "88124": "Gallium",
    "88103": "Arsenic",
    "88154": "Selenium",
    "88109": "Bromine",
    "88176": "Rubidium",
    "88168": "Strontium",
    "88183": "Yttrium",
    "88185": "Zirconium",
    "88134": "Molybdenum",
    "88166": "Silver",
    "88110": "Cadmium",
    "88131": "Indium",
    "88160": "Tin",
    "88102": "Antimony",
    "88107": "Barium",
    "88146": "Lanthanum",
    "88142": "Mercury",
    "88128": "Lead",
    "88184": "Sodium",
    "88113": "Cobalt",
    "88403": "Sulfate",
    "88306": "Nitrate",
    "88301": "Ammonium",
    "88303": "Potassium ion",
    "88302": "Sodium ion",
    "88305": "Organic carbon",
    "88307": "Elemental carbon",
}


DATE_ROW = re.compile(r"^\s*(\d{1,2}/\d{1,2}/\d{2})\s+(.+?)\s*$")
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)(?:\*\*)?$")


def iso_date(value: str) -> str:
    return datetime.strptime(value, "%m/%d/%y").date().isoformat()


def parse_value(token: str) -> str:
    token = token.strip()
    if token in {"*", "**"}:
        return ""
    if not NUMBER.match(token):
        raise ValueError(f"unexpected table token: {token!r}")
    return token.removesuffix("**")


def parse_appendix_table(text: str, spec: TableSpec) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        match = DATE_ROW.match(line)
        if not match:
            continue
        date_raw, remainder = match.groups()
        tokens = remainder.split()
        if len(tokens) != len(spec.fields):
            raise ValueError(
                f"{spec.site}/{spec.system} {date_raw}: expected "
                f"{len(spec.fields)} values, found {len(tokens)}: {tokens}"
            )
        status = "valid"
        if tokens[0] == "*":
            status = "no_or_incomplete_cmb_dataset"
        elif tokens[0].endswith("**"):
            status = "mass_too_small_for_cmb"
        row = {
            "site": spec.site,
            "system": spec.system,
            "date": iso_date(date_raw),
            "cmb_row_status": status,
            "report_pages": f"{spec.first_page}-{spec.last_page}",
        }
        row.update({field: "" for field in ALL_RESULT_FIELDS})
        row.update(
            {field: parse_value(token) for field, token in zip(spec.fields, tokens)}
        )
        rows.append(row)
    if not rows:
        raise ValueError(f"no rows parsed for {spec.site}/{spec.system}")
    return rows


def pdftotext(pdf: Path, first_page: int, last_page: int) -> str:
    command = [
        "pdftotext",
        "-f",
        str(first_page),
        "-l",
        str(last_page),
        "-layout",
        str(pdf),
        "-",
    ]
    completed = subprocess.run(
        command, check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return completed.stdout


def appendix_rows(pdf: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for spec in TABLES:
        rows.extend(
            parse_appendix_table(
                pdftotext(pdf, spec.first_page, spec.last_page), spec
            )
        )
    return rows


def write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_crosswalk(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = {(row["site"], row["system"], row["date"]): row for row in rows}
    pairs: list[dict[str, str]] = []
    for row in rows:
        if row["system"] != "epa":
            continue
        omni = lookup.get((row["site"], "omni", row["date"]))
        revised = lookup.get((row["site"], "omni_revised", row["date"]))
        if not omni:
            continue
        aqs_id = "02-090-0010" if row["site"] == "state_building" else ""
        pairs.append(
            {
                "candidate_case_id": f"fairbanks_{row['site']}_{row['date']}",
                "site": row["site"],
                "date": row["date"],
                "sampling_duration": "24 hours",
                "pm_size_fraction": "PM2.5",
                "aqs_site_id": aqs_id,
                "cmb_sample_id": "not published",
                "epa_status": row["cmb_row_status"],
                "omni_status": omni["cmb_row_status"],
                "epa_wood_smoke_ug_m3": row["wood_smoke"],
                "epa_wood_smoke_se_ug_m3": row["wood_smoke_se"],
                "omni_wood_smoke_ug_m3": omni["wood_smoke"],
                "omni_wood_smoke_se_ug_m3": omni["wood_smoke_se"],
                "omni_no2_fuel_oil_ug_m3": omni["no2_fuel_oil"],
                "revised_omni_available": "yes" if revised else "no",
                "source_universe_identical": "no",
                "profile_choice_isolated": "no",
                "levoglucosan_sample_id": "not published",
                "radiocarbon_sample_id": "not published",
                "external_reference_same_sample": "not recoverable from published tables",
                "disposition": "HOLD",
                "reason": (
                    "EPA-versus-OMNI changes the source universe by adding No. 2 "
                    "fuel oil; Busby publishes paired analyses but not the exact "
                    "site/date/sample-ID crosswalk."
                ),
            }
        )
    return sorted(pairs, key=lambda item: (item["site"], item["date"]))


def read_aqs_rows(
    archives: list[Path], wanted_dates: set[str]
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for archive in archives:
        with zipfile.ZipFile(archive) as bundle:
            members = [name for name in bundle.namelist() if name.lower().endswith(".csv")]
            if len(members) != 1:
                raise ValueError(f"expected one CSV in {archive}, found {members}")
            with bundle.open(members[0]) as raw:
                import io

                reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig"))
                for source in reader:
                    if source["State Code"] != "02" or source["County Code"] != "090":
                        continue
                    if source["Site Num"] != "0010":
                        continue
                    if source["Date Local"] not in wanted_dates:
                        continue
                    code = source["Parameter Code"]
                    if code not in AQS_CMB_SPECIES:
                        continue
                    rows.append(
                        {
                            "candidate_case_id": (
                                f"fairbanks_state_building_{source['Date Local']}"
                            ),
                            "site": "state_building",
                            "date": source["Date Local"],
                            "aqs_site_id": "02-090-0010",
                            "parameter_code": code,
                            "report_species_name": AQS_CMB_SPECIES[code],
                            "aqs_parameter_name": source["Parameter Name"],
                            "value": source["Arithmetic Mean"],
                            "units": source["Units of Measure"],
                            "sample_duration": source["Sample Duration"],
                            "method_code": source["Method Code"],
                            "method_name": source["Method Name"],
                            "historical_cmb_input_identity": "not proven",
                            "receptor_uncertainty": "not present in AirData daily file",
                        }
                    )
    rows.sort(key=lambda item: (item["date"], item["parameter_code"]))
    return rows


def read_aqs_sass_mass(
    archives: list[Path], appendix_mass: dict[str, str]
) -> list[dict[str, str]]:
    """Recover SASS gravimetric mass (AQS 88502, POC 6) for linkage checks."""
    recovered: dict[str, dict[str, str]] = {}
    for archive in archives:
        with zipfile.ZipFile(archive) as bundle:
            members = [name for name in bundle.namelist() if name.lower().endswith(".csv")]
            if len(members) != 1:
                raise ValueError(f"expected one CSV in {archive}, found {members}")
            with bundle.open(members[0]) as raw:
                import io

                reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig"))
                for source in reader:
                    if (
                        source["State Code"] != "02"
                        or source["County Code"] != "090"
                        or source["Site Num"] != "0010"
                        or source["Parameter Code"] != "88502"
                        or source["POC"] != "6"
                        or source["Date Local"] not in appendix_mass
                    ):
                        continue
                    date = source["Date Local"]
                    published = appendix_mass[date]
                    if not published:
                        continue
                    aqs_value = source["Arithmetic Mean"]
                    difference = abs(float(published) - float(aqs_value))
                    recovered[date] = {
                        "candidate_case_id": f"fairbanks_state_building_{date}",
                        "site": "state_building",
                        "date": date,
                        "aqs_site_id": "02-090-0010",
                        "aqs_parameter_code": "88502",
                        "aqs_poc": "6",
                        "appendix_c_pm25_mass_ug_m3": published,
                        "aqs_sass_pm25_mass_ug_m3": aqs_value,
                        "absolute_difference_ug_m3": f"{difference:.6g}",
                        "matches_report_precision": "yes" if difference <= 0.11 else "no",
                        "method_code": source["Method Code"],
                        "method_name": source["Method Name"],
                        "inference_limit": (
                            "Strong site/date/instrument linkage only; this does not prove "
                            "the exact historical CMB uncertainty vector or final fitting species."
                        ),
                    }
    return [recovered[date] for date in sorted(recovered)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ward-pdf", required=True, type=Path)
    parser.add_argument("--aqs-spec-zip", action="append", default=[], type=Path)
    parser.add_argument("--aqs-mass-zip", action="append", default=[], type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    results = appendix_rows(args.ward_pdf.resolve())
    write_csv(
        args.out_dir / "appendix_c_2008_2009_daily.csv",
        ("site", "system", "date", "cmb_row_status", "report_pages", *ALL_RESULT_FIELDS),
        results,
    )
    crosswalk = build_crosswalk(results)
    write_csv(
        args.out_dir / "exact_case_crosswalk.csv",
        tuple(crosswalk[0]),
        crosswalk,
    )

    wanted_dates = {
        row["date"]
        for row in results
        if row["site"] == "state_building" and row["system"] == "epa"
    }
    aqs_rows = read_aqs_rows(
        [path.resolve() for path in args.aqs_spec_zip], wanted_dates
    )
    if aqs_rows:
        write_csv(
            args.out_dir / "aqs_state_building_receptor_candidates.csv",
            tuple(aqs_rows[0]),
            aqs_rows,
        )

    appendix_mass = {
        row["date"]: row["pm25_mass"]
        for row in results
        if row["site"] == "state_building" and row["system"] == "epa"
    }
    mass_rows = read_aqs_sass_mass(
        [path.resolve() for path in args.aqs_mass_zip], appendix_mass
    )
    if mass_rows:
        write_csv(
            args.out_dir / "aqs_state_building_mass_crosscheck.csv",
            tuple(mass_rows[0]),
            mass_rows,
        )

    print(f"Appendix C rows: {len(results)}")
    print(f"EPA/OMNI matched date rows: {len(crosswalk)}")
    print(f"AQS 43-species candidate rows: {len(aqs_rows)}")
    print(f"AQS SASS mass cross-check rows: {len(mass_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
