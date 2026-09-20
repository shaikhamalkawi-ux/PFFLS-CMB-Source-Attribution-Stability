#!/usr/bin/env python3
"""Retrieve the small public Cycle 01 audit set and verify exact bytes.

Downloaded third-party files stay outside the repository.  The command refuses
hash mismatches and does not package or commit the downloaded bytes.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import urllib.request


SOURCES = {
    "fairbanks_report": (
        "https://dec.alaska.gov/media/17116/fairbanks-cmb-final-report-122313.pdf",
        "Ward_2013_Fairbanks_CMB_Final_Report.pdf",
        "9d71371a413b517a4cbaa441be01477bab4ef58d831aac55caab5c0658ca534e",
    ),
    "school_bus_evda": (
        "https://pdfs.semanticscholar.org/5c69/030e6ce631020fa788c00571051a07fecdec.pdf",
        "Larson_2011_school_bus_EVDA_CMB.pdf",
        "30c98a7040a716d5284a543c8eb08a0be25be56861c24b884bedb0e71235923c",
    ),
    "school_bus_jats": (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=2914332",
        "Liu_2010_PMC2914332_jats.xml",
        "b3be866ac36fdf5552343d515c105abe8e648a2f32ce19f5ac835e7da8f699c0",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(key: str, destination: Path) -> Path:
    url, filename, expected = SOURCES[key]
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / filename
    request = urllib.request.Request(url, headers={"User-Agent": "PFFLS-cycle01-audit/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, target.open("wb") as handle:
        while block := response.read(1024 * 1024):
            handle.write(block)
    actual = sha256(target)
    if actual != expected:
        target.unlink(missing_ok=True)
        raise RuntimeError(f"SHA-256 mismatch for {key}: expected {expected}, got {actual}")
    print(f"{key}: {target} {actual}")
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--source", choices=[*SOURCES, "all"], default="all")
    args = parser.parse_args()
    keys = SOURCES if args.source == "all" else (args.source,)
    for key in keys:
        fetch(key, args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
