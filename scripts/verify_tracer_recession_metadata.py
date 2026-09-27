"""Independent decimal-native sign/count replay; no solver or producer imports."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA = "3ca5bb3d4273e40f9c0f65a11f60e86fadafb525a086a046a9ef29a171fd229f"
MEMBER_SHA = {
    "PRsjvf.txt": "d46ba365514a99cd394207a94a4413dc10f6da368a4cb01f6ba39a1b653eb0ac",
    "ADsjvf.txt": "49db3300d44991b10c4fc1d041daa7d97428e58d9e2fc9e7bb10036bffe760f0",
}
TRACERS = {"SUXC": "SUXU", "CUXC": "CUXU", "ZNXC": "ZNXU"}
ORIGINAL = {
    "N3IC": "N3IU", "S4IC": "S4IU", "N4TC": "N4TU", "KPAC": "KPAU",
    "NAAC": "NAAU", "ECTC": "ECTU", "OCTC": "OCTU", "ALXC": "ALXU",
    "SIXC": "SIXU", "CLXC": "CLXU", "KPXC": "KPXU", "CAXC": "CAXU",
    "TIXC": "TIXU", "VAXC": "VAXU", "CRXC": "CRXU", "MNXC": "MNXU",
    "FEXC": "FEXU", "NIXC": "NIXU", "BRXC": "BRXU", "PBXC": "PBXU",
}
FAMILIES = (
    ("SOIL03", "SOIL08", "SOIL12", "SOIL29"),
    ("BAMAJC", "MAFISC", "MAMAJC"), ("SFCRUC", "CHCRUC"),
    ("MOVES1", "MOVES2", "MOVES3", "MOVES4", "MOVES5"),
    ("AMSUL",), ("AMNIT",), ("NANO3",),
)


def require(ok, label):
    if not ok:
        raise ValueError(label)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def number(token):
    require(isinstance(token, str) and 0 < len(token) <= 40, "invalid numeric token")
    value = Decimal(token)
    require(value.is_finite(), "nonfinite native number")
    require(-40 <= value.as_tuple().exponent <= 40, "unsupported native exponent")
    return value


def positive_lower(mean, uncertainty):
    # The guarded decimal-token range makes these operations exact at prec=200.
    with localcontext() as context:
        context.prec = 200
        f, u = number(mean), number(uncertainty)
        require(f >= 0 and u >= 0, "negative source field")
        return f > 3 * u


def table(payload):
    rows = [line.split() for line in payload.decode("ascii").splitlines() if line.strip()]
    require(len(rows) >= 2, "empty native table")
    header = rows[0]
    require(len(header) == len(set(header)), "duplicate columns")
    require(all(len(row) == len(header) for row in rows[1:]), "ragged native table")
    return [dict(zip(header, row)) for row in rows[1:]]


def replay(inputs):
    payload = (inputs / "sjvf_data.zip").read_bytes()
    require(digest(payload) == ARCHIVE_SHA, "archive identity")
    with ZipFile(BytesIO(payload)) as archive:
        members = {name: archive.read(name) for name in MEMBER_SHA}
    for name, data in members.items():
        require(digest(data) == MEMBER_SHA[name], "member identity")
    source_rows = [r for r in table(members["PRsjvf.txt"]) if r["SIZE"] == "FINE"]
    sources = {r["SID"]: r for r in source_rows}
    require(len(sources) == len(source_rows), "duplicate fine profile IDs")
    receptors = [r for r in table(members["ADsjvf.txt"]) if r["SIZE"] == "FINE" and r["ID"] == "FRESNO"]
    ids = [tuple(r[k] for k in ("ID", "DATE", "DUR", "STHOUR", "SIZE")) for r in receptors]
    require(len(receptors) == len(set(ids)) == 35, "receptor selection or duplicates")
    universe = set().union(*map(set, FAMILIES))
    require(len(universe) == 17 and universe <= sources.keys(), "source selection")
    validity = {}
    with localcontext() as context:
        context.prec = 200
        for mean, unc in TRACERS.items():
            valid_sources = sum(number(sources[s][mean]) >= 0 and number(sources[s][unc]) >= 0 for s in universe)
            valid_receptors = sum(number(r[mean]) != -99 and number(r[unc]) > 0 for r in receptors)
            valid_upper = sum(number(r[mean]) + 3 * number(r[unc]) >= 0 for r in receptors)
            require((valid_sources, valid_receptors, valid_upper) == (17, 35, 35), "tracer completeness")
            validity[mean] = {"valid_source_pairs": valid_sources, "valid_receptor_pairs": valid_receptors,
                              "nonnegative_receptor_upper_endpoints": valid_upper}
    positive_counts = {}
    added_positive = 0
    for vehicle in FAMILIES[3]:
        row = sources[vehicle]
        original_count = sum(positive_lower(row[m], row[u]) for m, u in ORIGINAL.items())
        added_count = sum(positive_lower(row[m], row[u]) for m, u in TRACERS.items())
        added_positive += added_count
        positive_counts[vehicle] = {"original_20_positive": original_count,
                                    "added_3_positive": added_count}
    require(added_positive == 0, "does not reproduce recorded extra-tracer signs")
    require([v["original_20_positive"] for v in positive_counts.values()] == [0, 0, 4, 0, 0],
            "does not reproduce recorded original-column signs")
    multiplicity = len(FAMILIES[0]) * len(FAMILIES[1]) * len(FAMILIES[2])
    surviving = sum(v["original_20_positive"] == v["added_3_positive"] == 0 for v in positive_counts.values()) * multiplicity
    return {"status": "PASS", "completed_utc": datetime.now(timezone.utc).isoformat(),
            "method": "Independent standard-library native-table parse with explicit uncertainty-field map and exact decimal sign comparisons",
            "archive_sha256": ARCHIVE_SHA, "members_sha256": MEMBER_SHA,
            "verifier_sha256": digest(Path(__file__).read_bytes()),
            "tests_sha256": digest((ROOT / "tests/test_tracer_recession_metadata.py").read_bytes()),
            "all_15_added_vehicle_lower_bounds_zero": added_positive == 0,
            "positive_lower_counts": positive_counts, "tracer_validity": validity,
            "historical_input_systems": 120, "systems_per_vehicle": multiplicity,
            "input_systems_retaining_zero_vehicle_lower_column": surviving,
            "producer_imported": False, "historical_private_records_read": False,
            "new_field_fits": 0, "new_field_LPs": 0,
            "limits": "Post-outcome metadata replay only. Count96 is input geometry, not feasible receptors or profile systems. A ray persists only in a nonempty branch. Added observations may eliminate branches; that was not tested. No held-out, source-truth, coverage or superiority claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=ROOT.parent / "_inputs/strengthening_20260926/epa")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/decision_research_20260926/tracer_recession_independent_verification.json")
    args = parser.parse_args()
    require(not args.output.exists(), "output already exists")
    result = replay(args.inputs)
    payload = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with args.output.open("xb") as handle:
        handle.write(payload)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
