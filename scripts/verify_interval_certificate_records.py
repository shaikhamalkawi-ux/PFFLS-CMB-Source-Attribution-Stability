#!/usr/bin/env python3
"""Independently replay saved interval proof objects; never invoke an LP solver.

This validator deliberately does not import the generating audit or its helpers.
It reconstructs original-decimal models from identity-checked native archives.
All mathematical acceptance checks use Fraction arithmetic and remain active
under python -O. Solver flags alone never constitute a mathematical certificate.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from io import BytesIO
import itertools
import json
from pathlib import Path
import platform
import time
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
DEFAULT_INPUT = ROOT.parent / "_inputs/strengthening_20260926/epa"
CONFIG_HASH = "9ad8d7a42075fe3c4821336dfcbea9ae545daa05d70dd85ce5668eceb5aa6f5a"
JOINT_HASH = "ba73f7f41de50d4b40edf1fe5be0513120dfb109c9a10730f1007e7f6c3143a2"
DEPENDENCIES = {
    "scripts/audit_epa_native_strengthening.py": "42c327b7ef629077bf1f11d1562ccee500a9192b236a1add771ff522070d1c09",
    "scripts/audit_interval_decisions.py": "ecb4e8f01f4028eb0a43d85870b3f458b75fce91d8bad9bdddaa815c3597da93",
    "tests/test_interval_decisions.py": "777862955c40b41a147886e701914840ff8eae6a061cd96a510f9e4de5e25033",
    "outputs/decision_research_20260926/interval_configuration.json": CONFIG_HASH,
    "outputs/strengthening_20260926/source_recovery.json": "4f60826ae3e564af7b16bc07ca64a3cd7df2d89aa99e554ef239a1dcb844d6f2",
}
ARCHIVE_HASHES = {
    "sjvf_data.zip": "3ca5bb3d4273e40f9c0f65a11f60e86fadafb525a086a046a9ef29a171fd229f",
    "pacs_data.zip": "e83d859f6a794504271ff4e84704787fe8b7a03e87940e6dcb105e560a7fef4f",
    "epa-cmb82test.zip": "f653311c3b9d0b89611a337b625e77d82d35650c852f5df8d7cb10c76f86d7ff",
    "sourcecmb82.zip": "44acea483c66cd5eb859340ecb7083fff18ab4b0401dde5d4f34972a22fbe8c9",
}
SOURCES = ["SOIL03", "BAMAJC", "SFCRUC", "MOVES2", "AMSUL", "AMNIT", "NANO3"]
SPECIES = ["N3IC", "S4IC", "N4TC", "KPAC", "NAAC", "ECTC", "OCTC", "ALXC", "SIXC", "CLXC", "KPXC", "CAXC", "TIXC", "VAXC", "CRXC", "MNXC", "FEXC", "NIXC", "BRXC", "PBXC"]
LABELS = dict(zip(SOURCES, ["soil", "wood", "oil", "vehicle", "ammonium_sulfate", "ammonium_nitrate", "sodium_nitrate"]))
IDENTITY = ("ID", "DATE", "DUR", "STHOUR", "SIZE")
UNIVERSES = ("full_seven_primary", "central_retained_bridge")
MODES = ("fixed_profile", "joint_intervals")
MASS_MODES = ("none", "historical_80_120_band")


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def fraction(value):
    require(isinstance(value, (str, int)) and not isinstance(value, bool), "proof coefficient must be a finite rational string/integer")
    require(not isinstance(value, str) or len(value) <= 10000, "oversized rational coefficient")
    try:
        return Q(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise VerificationError("malformed rational coefficient") from exc


def vector(values):
    return [fraction(v) for v in values]


def dot(a, b):
    require(len(a) == len(b), "dot-product dimension mismatch")
    return sum((x*y for x, y in zip(a, b)), Q(0))


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def check_hash(path, expected):
    payload = path.read_bytes()
    require(digest(payload) == expected, "input/dependency identity mismatch: " + path.name)
    return payload


def table(payload):
    rows = [line.split() for line in payload.decode("ascii").splitlines() if line.strip()]
    require(bool(rows) and len(rows[0]) == len(set(rows[0])), "invalid native table header")
    require(all(len(row) == len(rows[0]) for row in rows[1:]), "native table width mismatch")
    return [dict(zip(rows[0], row)) for row in rows[1:]]


def load_original_inputs(inputs):
    for relative, expected in DEPENDENCIES.items():
        check_hash(ROOT / relative, expected)
    recovery = json.loads((ROOT / "outputs/strengthening_20260926/source_recovery.json").read_bytes())
    prior = {row["name"]: row for row in recovery["records"]}
    members = 0
    sjvf = None
    for name, expected in ARCHIVE_HASHES.items():
        payload = check_hash(inputs / name, expected)
        require(prior[name]["sha256"] == expected and prior[name]["bytes"] == len(payload), "recovery archive record mismatch")
        with ZipFile(BytesIO(payload)) as archive:
            files = [i for i in archive.infolist() if not i.is_dir()]
            require(len(files) == len({i.filename for i in files}), "duplicate ZIP member")
            actual = {i.filename: (i.file_size, digest(archive.read(i.filename))) for i in files}
            recorded = {i["name"]: (i["bytes"], i["sha256"]) for i in prior[name]["members"]}
            require(actual == recorded, "native member identity mismatch")
            members += len(files)
            if name == "sjvf_data.zip":
                sjvf = {i.filename: archive.read(i.filename) for i in files}
    require(sjvf is not None and members == 39, "native input inventory incomplete")
    selection = lambda payload, column, field: [line.split()[field] for line in payload.decode("ascii").splitlines() if len(line) > column and line[column] == "*"]
    require(selection(sjvf["PRsjvf.sel"], 22, 1) == SOURCES, "native source selector mismatch")
    require(selection(sjvf["SPsjvf.sel"], 20, 0) == SPECIES == selection(sjvf["SPsjvf.sel"], 24, 0), "native species selector mismatch")
    receptors = [r for r in table(sjvf["ADsjvf.txt"]) if r["ID"] == "FRESNO" and r["SIZE"] == "FINE"]
    rows = [r for r in table(sjvf["PRsjvf.txt"]) if r["SIZE"] == "FINE"]
    profiles = {r["SID"]: r for r in rows}
    require(len(profiles) == len(rows), "duplicate native source mnemonic")
    require(len(receptors) == len({tuple(r[k] for k in IDENTITY) for r in receptors}) == 35, "native sample identity/count mismatch")
    prior_joint = json.loads(check_hash(PRIVATE / "joint_profile_ledger.json", JOINT_HASH))
    bridge = {tuple(s["sample"][k] for k in IDENTITY): s["retained_slots"] for s in prior_joint["samples"]}
    require(len(bridge) == 35, "bridge identity mismatch")
    return receptors, profiles, bridge


def reconstruct_model(receptor, profiles, sources, k, mode, mass_mode):
    require(k in (1, 2, 3) and mode in MODES and mass_mode in MASS_MODES, "unapproved model scenario")
    require(bool(sources) and len(set(sources)) == len(sources) and all(s in SOURCES for s in sources), "invalid central source universe")
    L, U, lo, hi = [], [], [], []
    for species in SPECIES:
        c, uc = fraction(receptor[species]), fraction(receptor[species[:-1] + "U"])
        require(c != -99 and uc > 0, "invalid receptor coefficient")
        lo.append(c-k*uc)
        hi.append(c+k*uc)
        low, high = [], []
        for sid in sources:
            f, uf = fraction(profiles[sid][species]), fraction(profiles[sid][species[:-1] + "U"])
            require(f >= 0 and uf >= 0, "invalid profile coefficient")
            radius = Q(0) if mode == "fixed_profile" else k*uf
            low.append(max(Q(0), f-radius))
            high.append(f+radius)
        L.append(low)
        U.append(high)
    G = L + [[-v for v in row] for row in U]
    h = hi + [-v for v in lo]
    mass = fraction(receptor["TMAC"])
    require(mass > 0, "invalid receptor mass")
    n = len(sources)
    caps = []
    for j in range(n):
        candidates = [rhs/row[j] for row, rhs in zip(L, hi) if row[j] > 0 and rhs >= 0]
        caps.append(min(candidates) if candidates else None)
    if mass_mode == "historical_80_120_band":
        G += [[Q(1)]*n, [Q(-1)]*n]
        h += [Q(6, 5)*mass, -Q(4, 5)*mass]
        caps = [min(b, Q(6, 5)*mass) if b is not None else Q(6, 5)*mass for b in caps]
    return {"G": G, "h": h, "n": n, "upper_bounds": caps, "names": [LABELS[s] for s in sources],
            "L": L, "U": U, "receptor_low": lo, "receptor_high": hi,
            "sources": sources, "mass": mass, "k": k, "profile_mode": mode, "mass_mode": mass_mode}


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, list):
        return [encode(v) for v in value]
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    return value


def primal_point(G, h, point, n):
    x = vector(point)
    require(len(x) == n and all(v >= 0 for v in x), "primal nonnegativity/dimension failure")
    require(all(dot(row, x) <= rhs for row, rhs in zip(G, h)), "primal inequality violated")
    return x


def farkas(G, h, n, cert):
    require(cert.get("verified") is True, "Farkas flag missing")
    y = vector(cert["y"])
    require(len(y) == len(G) and all(v >= 0 for v in y), "Farkas multiplier sign/dimension failure")
    require(all(sum(y[i]*G[i][j] for i in range(len(G))) >= 0 for j in range(n)), "Farkas column inequality violated")
    value = dot(h, y)
    require(value < 0 and value == fraction(cert["h_dot_y"]), "Farkas contradiction not strict/correct")


def verify_feasibility(info, G, h, n, counts):
    status = info["status"]
    if status == "EXACT_FEASIBLE":
        require(info["primal"].get("verified") is True, "feasible proof flag missing")
        primal_point(G, h, info["primal"]["point"], n)
        counts["primal_points"] += 1
    elif status == "EXACT_INFEASIBLE":
        farkas(G, h, n, info["farkas"])
        counts["farkas_certificates"] += 1
    else:
        require(status == "NUMERICALLY_UNRESOLVED", "unknown feasibility status")


def verify_objective(run, G, h, n, caps, expected, mass_mode, counts):
    q = vector(run["objective"])
    require(q == expected, "objective/source mapping mismatch")
    primal_ok = run.get("primal", {}).get("verified") is True
    dual_ok = run.get("dual", {}).get("verified") is True
    if primal_ok:
        x = primal_point(G, h, run["primal"]["point"], n)
        require(dot(q, x) == fraction(run["feasible_objective"]), "primal objective mismatch")
        counts["primal_points"] += 1
    else:
        require("feasible_objective" not in run, "unverified point reported as objective witness")
    if dual_ok:
        d = run["dual"]
        lam = vector(d["lambda"])
        require(len(lam) == len(G) and all(v <= 0 for v in lam), "dual multiplier sign/dimension failure")
        residual = [q[j]-sum(lam[i]*G[i][j] for i in range(len(G))) for j in range(n)]
        require(residual == vector(d["residual"]), "dual residual mismatch")
        needed = [j for j, r in enumerate(residual) if r < 0]
        require(all(caps[j] is not None for j in needed), "negative dual residual lacks a proven finite cap")
        correction = sum((residual[j]*caps[j] for j in needed), Q(0))
        value = dot(lam, h)+correction
        require(correction == fraction(d["correction"]), "dual correction mismatch")
        require(value == fraction(d["lower_bound"]) == fraction(run["verified_lower_bound"]), "dual lower-bound mismatch")
        require({str(j): caps[j] for j in needed} == {j: fraction(v) for j, v in d["upper_bounds_used"].items()}, "dual bound provenance mismatch")
        if primal_ok:
            gap = fraction(run["feasible_objective"])-value
            require(gap >= 0 and gap == fraction(run["verified_gap"]), "weak duality/gap failure")
        counts["dual_bounds"] += 1
    else:
        require("verified_lower_bound" not in run, "unverified dual reported as bound")
    status = run["status"]
    if status == "VERIFIED_BOUND_AND_WITNESS":
        require(primal_ok and dual_ok and run["crosscheck_agrees"] is True and run["crosscheck_status"] == 0, "verified objective missing proof/crosscheck")
    elif status == "EXACT_UNBOUNDED":
        require(mass_mode != "historical_80_120_band", "historical mass band cannot have an unbounded linear objective")
        r = run["recession"]
        require(r.get("verified") is True, "recession proof flag missing")
        primal_point(G, h, r["point"], n)
        ray = vector(r["ray"])
        require(len(ray) == n and all(v >= 0 for v in ray), "invalid recession direction")
        require(all(dot(row, ray) <= 0 for row in G), "recession inequality violated")
        require(dot(q, ray) < 0 and dot(q, ray) == fraction(r["objective_ray"]), "recession objective is not strictly improving")
        counts["recession_certificates"] += 1
    elif status == "EXACT_INFEASIBLE":
        farkas(G, h, n, run["farkas"])
        counts["farkas_certificates"] += 1
    else:
        require(status == "NUMERICALLY_UNRESOLVED", "unknown objective status")


def classify_pair(low, negative, threshold):
    lower = fraction(low["verified_lower_bound"]) if "verified_lower_bound" in low else None
    upper = -fraction(negative["verified_lower_bound"]) if "verified_lower_bound" in negative else None
    left = fraction(low["feasible_objective"]) if "feasible_objective" in low else None
    right = -fraction(negative["feasible_objective"]) if "feasible_objective" in negative else None
    low_valid = low["status"] == "VERIFIED_BOUND_AND_WITNESS"
    high_valid = negative["status"] == "VERIFIED_BOUND_AND_WITNESS"
    if low_valid and lower is not None and lower > threshold:
        status = "VERIFIED_A_GREATER_B"
    elif high_valid and upper is not None and upper < -threshold:
        status = "VERIFIED_B_GREATER_A"
    elif left is not None and right is not None and left < 0 < right:
        status = "EXACT_BOTH_ORDERINGS_WITNESSED"
    elif left == 0 or right == 0:
        status = "EXACT_TIE_WITNESSED"
    elif (low_valid and lower is not None and 0 < lower <= threshold) or (high_valid and upper is not None and -threshold <= upper < 0):
        status = "NEAR_ZERO_HOLD"
    else:
        status = "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP"
    return {"status": status, "verified_lower": lower, "verified_upper": upper,
            "minimum_feasible_witness_contrast": left, "maximum_feasible_witness_contrast": right,
            "near_zero_threshold": threshold}


def verify_result(result, model, counts):
    G, h, n = model["G"], model["h"], model["n"]
    caps, names = model["upper_bounds"], model["names"]
    require(result["sources"] == names, "result source names mismatch")
    verify_feasibility(result["feasibility"], G, h, n, counts)
    if result["feasibility"]["status"] != "EXACT_FEASIBLE":
        require(result["overall_status"] == result["feasibility"]["status"], "incompatible overall status")
        require(result["source_bounds"] == {} and result["pairs"] == [] and result["co_leaders"] == {}, "non-feasible model has decision claims")
        require(not result.get("verified_unique_leaders_above_margin_threshold"), "vacuous winner on incompatible/unresolved set")
    else:
        require(result["overall_status"] == "EXACT_COMPATIBLE", "compatible overall status mismatch")
        require(set(result["source_bounds"]) == set(names) == set(result["co_leaders"]), "source result coverage mismatch")
        for j, name in enumerate(names):
            q = [Q(int(i == j)) for i in range(n)]
            run = result["source_bounds"][name]
            require(set(run) == {"minimize", "maximize_negative"}, "source bound endpoint coverage mismatch")
            verify_objective(run["minimize"], G, h, n, caps, q, model["mass_mode"], counts)
            verify_objective(run["maximize_negative"], G, h, n, caps, [-v for v in q], model["mass_mode"], counts)
            extra = []
            for other in range(n):
                if other != j:
                    row = [Q(0)]*n
                    row[other], row[j] = Q(1), Q(-1)
                    extra.append(row)
            verify_feasibility(result["co_leaders"][name], G+extra, h+[Q(0)]*len(extra), n, counts)
            counts["co_leader_decisions"] += 1
        expected_pairs = list(itertools.combinations(names, 2))
        require([(r["a"], r["b"]) for r in result["pairs"]] == expected_pairs, "pairwise coverage/order mismatch")
        threshold = Q(1, 10_000_000)*max(Q(1), model["mass"])
        for pair in result["pairs"]:
            a, b = names.index(pair["a"]), names.index(pair["b"])
            q = [Q(int(i == a)-int(i == b)) for i in range(n)]
            verify_objective(pair["minimize"], G, h, n, caps, q, model["mass_mode"], counts)
            verify_objective(pair["maximize_negative"], G, h, n, caps, [-v for v in q], model["mass_mode"], counts)
            require(pair["classification"] == encode(classify_pair(pair["minimize"], pair["maximize_negative"], threshold)), "pair decision/threshold mismatch")
            counts["pair_decisions"] += 1
        possible = [name for name in names if result["co_leaders"][name]["status"] == "EXACT_FEASIBLE"]
        rejected = [name for name in names if result["co_leaders"][name]["status"] == "EXACT_INFEASIBLE"]
        unresolved = [name for name in names if name not in possible+rejected]
        require(result["exact_possible_co_leaders"] == possible and result["exact_impossible_co_leaders"] == rejected and result["unresolved_co_leaders"] == unresolved, "co-leader summary mismatch")
        winners = []
        for name in names:
            relevant = [p for p in result["pairs"] if name in (p["a"], p["b"])]
            if len(relevant) == n-1 and all(p["classification"]["status"] == ("VERIFIED_A_GREATER_B" if p["a"] == name else "VERIFIED_B_GREATER_A") for p in relevant):
                winners.append(name)
        require(result["verified_unique_leaders_above_margin_threshold"] == winners, "unique-leader summary mismatch")
    return {"overall_status": result["overall_status"],
            "pair_status_counts": dict(Counter(p["classification"]["status"] for p in result["pairs"])),
            "source_bound_status_counts": dict(Counter(run["status"] for bounds in result["source_bounds"].values() for run in bounds.values())),
            "exact_possible_co_leaders": result.get("exact_possible_co_leaders", []),
            "unresolved_co_leaders": result.get("unresolved_co_leaders", []),
            "verified_unique_leaders_above_margin_threshold": result.get("verified_unique_leaders_above_margin_threshold", [])}


def verify_all(inputs, max_seconds=1800):
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    require(0 < max_seconds <= 3600, "verification time bound must be in (0,3600]")
    receptors, profiles, bridge = load_original_inputs(inputs)
    gate = json.loads((PUBLIC / "interval_stage1.json").read_bytes())
    require(gate["status"] == "PASS" and gate["configuration_sha256"] == CONFIG_HASH, "Stage1 gate missing or unapproved")
    require(gate["script_sha256"] == DEPENDENCIES["scripts/audit_interval_decisions.py"] and gate["tests_sha256"] == DEPENDENCIES["tests/test_interval_decisions.py"], "Stage1 code identity mismatch")
    index_bytes = (PRIVATE / "interval_index.json").read_bytes()
    index = json.loads(index_bytes)
    require(index["configuration_sha256"] == CONFIG_HASH and "completed_utc" in index, "final complete index missing")
    records = index["records"]
    require(len(records) == 840, "incomplete final panel index")
    keys = [(r["sample_zero_based_index"], r["universe"], r["k"], r["profile_mode"], r["mass_mode"]) for r in records]
    expected = set(itertools.product(range(35), UNIVERSES, (1, 2, 3), MODES, MASS_MODES))
    require(len(set(keys)) == 840 and set(keys) == expected, "panel/index Cartesian coverage mismatch")
    counts, cache, model_hashes = Counter(), {}, []
    panels = {}
    for number, (record, key) in enumerate(zip(records, keys), 1):
        if time.monotonic()-started > max_seconds:
            raise TimeoutError("bounded verification time exhausted; no complete verification claim")
        rec = receptors[key[0]]
        require(record["sample"] == {k: rec[k] for k in IDENTITY}, "index original sample identity mismatch")
        sources = SOURCES if key[1] == UNIVERSES[0] else bridge[tuple(rec[k] for k in IDENTITY)]
        model = reconstruct_model(rec, profiles, sources, key[2], key[3], key[4])
        canonical_model = encode(model)
        model_hash = digest(json_bytes(canonical_model))
        require(record["model_sha256"] == model_hash, "model not equal to independently reconstructed input problem")
        reused = model_hash in cache
        require(record["cached_identical_model"] is reused, "cache provenance mismatch")
        if reused:
            case_hash, summary = cache[model_hash]
        else:
            path = PRIVATE / "interval_cases" / ("interval_case_"+model_hash+".json")
            require(path.stat().st_size <= 50_000_000, "oversized proof case")
            payload = check_hash(path, record["case_sha256"])
            case = json.loads(payload)
            require(case["configuration_sha256"] == CONFIG_HASH and case["model_sha256"] == model_hash, "case identity mismatch")
            require(case["model"] == canonical_model, "stored model differs from reconstructed exact model")
            summary = verify_result(case["result"], model, counts)
            case_hash = digest(payload)
            cache[model_hash] = case_hash, summary
            model_hashes.append(model_hash)
            counts["unique_models"] += 1
        require(record["case_sha256"] == case_hash and record["summary"] == summary, "index case/summary mismatch")
        counts["panel_records"] += 1
        panel = panels.setdefault(key[1:], [])
        panel.append(summary)
        if number % 120 == 0:
            print(json.dumps({"records_verified": number, "unique_models_verified": len(cache), "elapsed_seconds": round(time.monotonic()-started, 2)}), flush=True)
    published = json.loads((PUBLIC / "interval_results.json").read_bytes())
    require(published["status"] == "COMPLETE" and published["configuration_sha256"] == CONFIG_HASH, "public Stage2 completion mismatch")
    require(published["private_index_sha256"] == digest(index_bytes) and published["unique_models"] == len(cache), "public index/unique-count mismatch")
    require(published["script_sha256"] == DEPENDENCIES["scripts/audit_interval_decisions.py"], "public generator identity mismatch")
    require(published["aggregate"]["records"] == 840 and len(published["aggregate"]["panels"]) == 24, "public denominator mismatch")
    for panel in published["aggregate"]["panels"]:
        key = (panel["universe"], panel["k"], panel["profile_mode"], panel["mass_mode"])
        rows = panels.pop(key)
        expected_panel = {"universe": key[0], "k": key[1], "profile_mode": key[2], "mass_mode": key[3], "initial_samples": len(rows),
            "compatibility_status": dict(Counter(r["overall_status"] for r in rows)),
            "unique_leader_samples": sum(bool(r["verified_unique_leaders_above_margin_threshold"]) for r in rows),
            "at_least_two_exact_possible_co_leaders_samples": sum(len(r["exact_possible_co_leaders"]) >= 2 for r in rows),
            "unresolved_co_leader_samples": sum(bool(r["unresolved_co_leaders"]) for r in rows),
            "pair_status_counts": dict(sum((Counter(r["pair_status_counts"]) for r in rows), Counter())),
            "source_bound_status_counts": dict(sum((Counter(r["source_bound_status_counts"]) for r in rows), Counter()))}
        require(panel == expected_panel and len(rows) == 35, "public panel aggregation mismatch")
    require(not panels, "unreported panel")
    return {"status": "PASS", "scope": "All final central-system Stage2 records; exact input reconstruction and saved-proof replay; no LP reruns, no statistical or environmental validation.",
            "started_utc": started_utc, "completed_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.monotonic()-started, 3), "python": platform.python_version(),
            "configuration_sha256": CONFIG_HASH, "private_index_sha256": digest(index_bytes),
            "verified_model_hash_set_sha256": digest(("\n".join(sorted(model_hashes))+"\n").encode()),
            "verifier_sha256": digest(Path(__file__).read_bytes()), "reviewed_dependencies": DEPENDENCIES,
            "native_archives_verified": 4, "native_members_verified": 39, "counts": dict(counts),
            "all_24_public_panels_reconciled": True, "all_panels_retain_35_samples": True,
            "historical_mass_unbounded_claims": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--max-seconds", type=float, default=1800)
    args = parser.parse_args()
    report = verify_all(args.inputs, args.max_seconds)
    (PUBLIC / "interval_certificate_verification.json").write_bytes(json_bytes(report))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
