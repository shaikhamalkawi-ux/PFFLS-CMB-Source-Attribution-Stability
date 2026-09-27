#!/usr/bin/env python3
"""Exploratory bounded-error LP audit with independently verified rational bounds.

Known interval/set-membership mathematics; not a statistical confidence procedure.
Stage 1 must pass before explicitly invoking Stage 2. No full-profile-grid stage.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import scipy
from scipy.optimize import linprog

import audit_epa_native_strengthening as native

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "outputs/decision_research_20260926"
PRIVATE = ROOT / "private/decision_research_20260926"
CONFIG_PATH = PUBLIC / "interval_configuration.json"
CONFIG_HASH = "9ad8d7a42075fe3c4821336dfcbea9ae545daa05d70dd85ce5668eceb5aa6f5a"
PROPOSAL_PATH = PUBLIC / "INTERVAL_FEASIBILITY_PROPOSAL.md"
JOINT_PATH = PRIVATE / "joint_profile_ledger.json"
OPTIONS = {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}
LABELS = {"SOIL03": "soil", "BAMAJC": "wood", "SFCRUC": "oil", "MOVES2": "vehicle",
          "AMSUL": "ammonium_sulfate", "AMNIT": "ammonium_nitrate", "NANO3": "sodium_nitrate"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configuration() -> dict:
    payload = CONFIG_PATH.read_bytes()
    if native.sha256(payload) != CONFIG_HASH:
        raise ValueError("frozen interval configuration identity changed")
    config = json.loads(payload)
    identities = [(PROPOSAL_PATH, "approved_proposal_sha256"),
                  (Path(native.__file__), "native_script_sha256")]
    for path, key in identities:
        if native.sha256(path.read_bytes()) != config[key]:
            raise ValueError(f"frozen dependency differs: {path.name}")
    if native.sha256(native.json_bytes(native.CONFIG)) != config["native_configuration_sha256"]:
        raise ValueError("frozen native configuration changed")
    return config


def dot(a, b) -> Q:
    return sum((x * y for x, y in zip(a, b)), Q(0))


def as_q(value) -> Q:
    """Use original decimal strings for field inputs; float conversion only for solver candidates."""
    if isinstance(value, Q):
        return value
    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            raise ValueError("nonfinite numeric input")
        return Q(str(float(value)))
    return Q(value)


def encode_q(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: encode_q(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode_q(item) for item in value]
    return value


def make_model(G, h, n=None, bounds=None, names=None) -> dict:
    G = [[as_q(value) for value in row] for row in G]
    h = [as_q(value) for value in h]
    n = len(G[0]) if n is None and G else n
    if n is None or n < 1 or len(G) != len(h) or any(len(row) != n for row in G):
        raise ValueError("inconsistent LP dimensions")
    upper = [None] * n if bounds is None else [as_q(b) if b is not None else None for b in bounds]
    if len(upper) != n or any(b is not None and b < 0 for b in upper):
        raise ValueError("invalid separately justified upper bounds")
    return {"G": G, "h": h, "n": n, "upper_bounds": upper,
            "names": names or [str(i) for i in range(n)]}


def field_model(receptor: dict, profiles: dict, sources: list[str], k: int,
                profile_mode: str, mass_mode: str) -> dict:
    if k not in (1, 2, 3) or profile_mode not in ("fixed_profile", "joint_intervals"):
        raise ValueError("unfrozen interval scenario")
    if mass_mode not in ("none", "historical_80_120_band"):
        raise ValueError("unapproved mass model")
    species = native.CONFIG["species"]
    low, high, receptor_low, receptor_high = [], [], [], []
    for name in species:
        c, uc = as_q(receptor[name]), as_q(receptor[name[:-1] + "U"])
        if uc <= 0 or c == -99:
            raise ValueError("missing/invalid ambient value or uncertainty")
        row_low, row_high = [], []
        for sid in sources:
            f, uf = as_q(profiles[sid][name]), as_q(profiles[sid][name[:-1] + "U"])
            if f < 0 or uf < 0:
                raise ValueError("negative/sentinel selected profile value or uncertainty")
            radius = Q(0) if profile_mode == "fixed_profile" else k * uf
            row_low.append(max(Q(0), f - radius))
            row_high.append(f + radius)
        low.append(row_low)
        high.append(row_high)
        receptor_low.append(c - k * uc)
        receptor_high.append(c + k * uc)
    G = low + [[-x for x in row] for row in high]
    h = receptor_high + [-x for x in receptor_low]
    mass = as_q(receptor["TMAC"])
    if mass <= 0:
        raise ValueError("invalid ambient total mass")
    # Bounds are justified only from nonnegative L rows, not arbitrary G rows.
    upper = []
    for j in range(len(sources)):
        candidates = [u / row[j] for row, u in zip(low, receptor_high) if row[j] > 0 and u >= 0]
        upper.append(min(candidates) if candidates else None)
    if mass_mode == "historical_80_120_band":
        G += [[Q(1)] * len(sources), [Q(-1)] * len(sources)]
        h += [Q(6, 5) * mass, -Q(4, 5) * mass]
        upper = [min(b, h[-2]) if b is not None else h[-2] for b in upper]
    model = make_model(G, h, bounds=upper, names=[LABELS[s] for s in sources])
    model.update({"L": low, "U": high, "receptor_low": receptor_low, "receptor_high": receptor_high,
                  "sources": sources, "mass": mass, "k": k, "profile_mode": profile_mode,
                  "mass_mode": mass_mode})
    return model


def exact_feasible(model: dict, x) -> bool:
    return len(x) == model["n"] and all(v >= 0 for v in x) and all(
        dot(row, x) <= rhs for row, rhs in zip(model["G"], model["h"]))


def exact_rank(rows: list[list[Q]]) -> int:
    if not rows:
        return 0
    mat = [list(row) for row in rows]
    pivot = 0
    for column in range(len(mat[0])):
        choice = next((i for i in range(pivot, len(mat)) if mat[i][column]), None)
        if choice is None:
            continue
        mat[pivot], mat[choice] = mat[choice], mat[pivot]
        scale = mat[pivot][column]
        mat[pivot] = [v / scale for v in mat[pivot]]
        for i in range(pivot + 1, len(mat)):
            scale = mat[i][column]
            if scale:
                mat[i] = [a - scale * b for a, b in zip(mat[i], mat[pivot])]
        pivot += 1
        if pivot == len(mat):
            break
    return pivot


def exact_square_solve(A: list[list[Q]], b: list[Q]) -> list[Q] | None:
    n = len(b)
    if len(A) != n or any(len(row) != n for row in A):
        return None
    mat = [list(row) + [rhs] for row, rhs in zip(A, b)]
    for col in range(n):
        choice = next((i for i in range(col, n) if mat[i][col]), None)
        if choice is None:
            return None
        mat[col], mat[choice] = mat[choice], mat[col]
        scale = mat[col][col]
        mat[col] = [v / scale for v in mat[col]]
        for i in range(n):
            if i != col and mat[i][col]:
                scale = mat[i][col]
                mat[i] = [a - scale * b for a, b in zip(mat[i], mat[col])]
    return [row[-1] for row in mat]


def repair_primal(model: dict, candidate) -> dict:
    if candidate is None or len(candidate) != model["n"] or not np.all(np.isfinite(candidate)):
        return {"verified": False, "method": "NO_FINITE_CANDIDATE"}
    x = [as_q(value) for value in candidate]
    if exact_feasible(model, x):
        return {"verified": True, "method": "EXACT_DECIMALIZED_SOLVER_POINT", "point": x}
    support = [i for i, value in enumerate(candidate) if value > 0]
    if not support:
        zero = [Q(0)] * model["n"]
        return {"verified": True, "method": "EXACT_ZERO_POINT", "point": zero} if exact_feasible(model, zero) else {
            "verified": False, "method": "NO_POSITIVE_SUPPORT"}
    near = []
    for index, (row, rhs) in enumerate(zip(model["G"], model["h"])):
        slack = float(rhs) - sum(float(a) * float(b) for a, b in zip(row, candidate))
        scale = 1 + abs(float(rhs)) + sum(abs(float(a) * float(b)) for a, b in zip(row, candidate))
        if abs(slack) / scale <= 1e-7:
            near.append((abs(slack) / scale, index))
    basis, values, indices = [], [], []
    for _, index in sorted(near):
        reduced = [model["G"][index][j] for j in support]
        if exact_rank(basis + [reduced]) > len(basis):
            basis.append(reduced)
            values.append(model["h"][index])
            indices.append(index)
            if len(basis) == len(support):
                break
    if len(basis) != len(support):
        return {"verified": False, "method": "INSUFFICIENT_EXACT_ACTIVE_BASIS"}
    repaired = exact_square_solve(basis, values)
    if repaired is None:
        return {"verified": False, "method": "SINGULAR_EXACT_ACTIVE_BASIS"}
    x = [Q(0)] * model["n"]
    for index, value in zip(support, repaired):
        x[index] = value
    if not exact_feasible(model, x):
        return {"verified": False, "method": "EXACT_ACTIVE_BASIS_POINT_NOT_FEASIBLE", "basis_rows": indices}
    return {"verified": True, "method": "EXACT_ACTIVE_BASIS", "point": x, "basis_rows": indices}


def solve_float(model: dict, q, method="highs-ds"):
    try:
        return linprog(np.array([float(v) for v in q]),
                       A_ub=np.array([[float(v) for v in row] for row in model["G"]]) if model["G"] else None,
                       b_ub=np.array([float(v) for v in model["h"]]) if model["h"] else None,
                       bounds=[(0, None)] * model["n"], method=method, options=OPTIONS)
    except (ValueError, RuntimeError) as exc:
        return SimpleNamespace(status=4, message=f"NUMERICAL_EXCEPTION: {exc}", x=None, fun=None)


def verify_farkas(model: dict, y: list[Q]) -> bool:
    return (len(y) == len(model["G"]) and all(v >= 0 for v in y)
            and all(sum(y[i] * model["G"][i][j] for i in range(len(y))) >= 0 for j in range(model["n"]))
            and dot(model["h"], y) < 0)


def infeasibility_certificate(model: dict) -> dict:
    # Phase I always has a feasible nonnegative t; its positive optimum may yield a Farkas ray.
    phase = make_model([row + [Q(-1)] for row in model["G"]], model["h"], n=model["n"] + 1)
    result = solve_float(phase, [Q(0)] * model["n"] + [Q(1)])
    if result.status != 0:
        return {"verified": False, "phase1_status": int(result.status)}
    y_float = [-min(0.0, float(v)) for v in result.ineqlin.marginals]
    y = [as_q(v) for v in y_float]
    if verify_farkas(model, y):
        return {"verified": True, "method": "EXACT_DECIMALIZED_PHASE1_DUAL", "y": y,
                "h_dot_y": dot(model["h"], y)}
    m = len(model["G"])
    dual_model = make_model([[-model["G"][i][j] for i in range(m)] for j in range(model["n"])]
                           + [[Q(1)] * m], [Q(0)] * model["n"] + [Q(1)], n=m)
    repaired = repair_primal(dual_model, y_float)
    if repaired["verified"] and verify_farkas(model, repaired["point"]):
        y = repaired["point"]
        return {"verified": True, "method": "EXACT_REPAIRED_PHASE1_DUAL", "y": y,
                "h_dot_y": dot(model["h"], y), "repair": repaired["method"]}
    return {"verified": False, "phase1_objective": float(result.fun), "repair_method": repaired["method"]}


def feasibility(model: dict) -> dict:
    result = solve_float(model, [Q(0)] * model["n"])
    answer = {"solver_status": int(result.status), "solver_message": result.message}
    if result.status == 0:
        witness = repair_primal(model, result.x)
        answer.update({"status": "EXACT_FEASIBLE" if witness["verified"] else "NUMERICALLY_UNRESOLVED",
                       "primal": witness})
    elif result.status == 2:
        cert = infeasibility_certificate(model)
        answer.update({"status": "EXACT_INFEASIBLE" if cert["verified"] else "NUMERICALLY_UNRESOLVED",
                       "farkas": cert})
    else:
        answer["status"] = "NUMERICALLY_UNRESOLVED"
    return answer


def lower_certificate(model: dict, q: list[Q], marginals) -> dict:
    if marginals is None or len(marginals) != len(model["G"]) or not np.all(np.isfinite(marginals)):
        return {"verified": False, "reason": "MISSING_DUAL"}
    lam = [min(Q(0), as_q(value)) for value in marginals]
    residual = [q[j] - sum(lam[i] * model["G"][i][j] for i in range(len(lam))) for j in range(model["n"])]
    needed = [j for j, value in enumerate(residual) if value < 0]
    if any(model["upper_bounds"][j] is None for j in needed):
        return {"verified": False, "reason": "DUAL_RESIDUAL_REQUIRES_UNAVAILABLE_UPPER_BOUND",
                "lambda": lam, "residual": residual}
    correction = sum((residual[j] * model["upper_bounds"][j] for j in needed), Q(0))
    return {"verified": True, "lower_bound": dot(lam, model["h"]) + correction,
            "lambda": lam, "residual": residual, "correction": correction,
            "upper_bounds_used": {str(j): model["upper_bounds"][j] for j in needed}}


def recession_certificate(model: dict, q: list[Q], feasible_point: list[Q] | None) -> dict:
    if feasible_point is None or not exact_feasible(model, feasible_point):
        return {"verified": False, "reason": "NO_EXACT_FEASIBLE_BASE_POINT"}
    ray_model = make_model(model["G"] + [[Q(1)] * model["n"]],
                           [Q(0)] * len(model["G"]) + [Q(1)], n=model["n"])
    result = solve_float(ray_model, q)
    if result.status != 0:
        return {"verified": False, "reason": "RAY_LP_FAILED", "solver_status": int(result.status)}
    primal = repair_primal(ray_model, result.x)
    if primal["verified"] and dot(q, primal["point"]) < 0:
        return {"verified": True, "point": feasible_point, "ray": primal["point"],
                "objective_ray": dot(q, primal["point"])}
    return {"verified": False, "reason": "NO_EXACT_IMPROVING_RAY"}


def objective_bound(model: dict, q: list[Q], feasible_point=None) -> dict:
    result = solve_float(model, q)
    answer = {"objective": q, "solver_status": int(result.status), "solver_message": result.message}
    if result.status == 0:
        cross = solve_float(model, q, method="highs-ipm")
        tolerance = 1e-7 * max(1, abs(float(result.fun)), abs(float(cross.fun)) if cross.status == 0 else 1)
        agrees = cross.status == 0 and abs(float(result.fun) - float(cross.fun)) <= tolerance
        primal = repair_primal(model, result.x)
        dual = lower_certificate(model, q, result.ineqlin.marginals)
        answer.update({"crosscheck_status": int(cross.status), "crosscheck_agrees": bool(agrees),
                       "solver_objective": float(result.fun), "primal": primal, "dual": dual,
                       "status": "VERIFIED_BOUND_AND_WITNESS" if agrees and primal["verified"] and dual["verified"]
                                 else "NUMERICALLY_UNRESOLVED"})
        if primal["verified"]:
            answer["feasible_objective"] = dot(q, primal["point"])
        if dual["verified"]:
            answer["verified_lower_bound"] = dual["lower_bound"]
        if primal["verified"] and dual["verified"]:
            if dual["lower_bound"] > answer["feasible_objective"]:
                raise AssertionError("independent primal/dual verification contradicts weak duality")
            answer["verified_gap"] = answer["feasible_objective"] - dual["lower_bound"]
    elif result.status == 3:
        ray = recession_certificate(model, q, feasible_point)
        answer.update({"status": "EXACT_UNBOUNDED" if ray["verified"] else "NUMERICALLY_UNRESOLVED", "recession": ray})
    elif result.status == 2:
        cert = infeasibility_certificate(model)
        answer.update({"status": "EXACT_INFEASIBLE" if cert["verified"] else "NUMERICALLY_UNRESOLVED", "farkas": cert})
    else:
        answer["status"] = "NUMERICALLY_UNRESOLVED"
    return answer


def pair_classification(lower_run: dict, negative_run: dict, threshold: Q) -> dict:
    low = lower_run.get("verified_lower_bound")
    high = -negative_run["verified_lower_bound"] if "verified_lower_bound" in negative_run else None
    min_witness = lower_run.get("feasible_objective")
    max_witness = -negative_run["feasible_objective"] if "feasible_objective" in negative_run else None
    lower_verified = lower_run["status"] == "VERIFIED_BOUND_AND_WITNESS"
    upper_verified = negative_run["status"] == "VERIFIED_BOUND_AND_WITNESS"
    # A one-sided order needs only its corresponding valid bound and a nonempty
    # set, already established by that run's exact primal witness. The opposite
    # side may be unbounded without weakening this certificate.
    if lower_verified and low is not None and low > threshold:
        status = "VERIFIED_A_GREATER_B"
    elif upper_verified and high is not None and high < -threshold:
        status = "VERIFIED_B_GREATER_A"
    elif min_witness is not None and max_witness is not None and min_witness < 0 < max_witness:
        status = "EXACT_BOTH_ORDERINGS_WITNESSED"
    elif min_witness == 0 or max_witness == 0:
        status = "EXACT_TIE_WITNESSED"
    elif ((lower_verified and low is not None and 0 < low <= threshold)
          or (upper_verified and high is not None and -threshold <= high < 0)):
        status = "NEAR_ZERO_HOLD"
    else:
        status = "NUMERICALLY_UNRESOLVED_OR_CERTIFICATION_GAP"
    return {"status": status, "verified_lower": low, "verified_upper": high,
            "minimum_feasible_witness_contrast": min_witness, "maximum_feasible_witness_contrast": max_witness,
            "near_zero_threshold": threshold}


def co_leader_model(model: dict, leader: int) -> dict:
    extra = []
    for j in range(model["n"]):
        if j != leader:
            row = [Q(0)] * model["n"]
            row[j], row[leader] = Q(1), Q(-1)
            extra.append(row)
    return make_model(model["G"] + extra, model["h"] + [Q(0)] * len(extra),
                      n=model["n"], bounds=model["upper_bounds"], names=model["names"])


def analyze_model(model: dict) -> dict:
    feasible = feasibility(model)
    answer = {"feasibility": feasible, "sources": model["names"], "source_bounds": {}, "pairs": [], "co_leaders": {}}
    if feasible["status"] != "EXACT_FEASIBLE":
        answer["overall_status"] = feasible["status"]
        return answer
    point = feasible["primal"]["point"]
    for j, name in enumerate(model["names"]):
        q = [Q(int(i == j)) for i in range(model["n"])]
        low = objective_bound(model, q, point)
        high = objective_bound(model, [-v for v in q], point)
        answer["source_bounds"][name] = {"minimize": low, "maximize_negative": high}
        answer["co_leaders"][name] = feasibility(co_leader_model(model, j))
    threshold = Q(1, 10_000_000) * max(Q(1), model.get("mass", Q(1)))
    for a, b in itertools.combinations(range(model["n"]), 2):
        q = [Q(int(i == a) - int(i == b)) for i in range(model["n"])]
        low = objective_bound(model, q, point)
        high = objective_bound(model, [-v for v in q], point)
        answer["pairs"].append({"a": model["names"][a], "b": model["names"][b],
                                "minimize": low, "maximize_negative": high,
                                "classification": pair_classification(low, high, threshold)})
    possible = [name for name, info in answer["co_leaders"].items() if info["status"] == "EXACT_FEASIBLE"]
    rejected = [name for name, info in answer["co_leaders"].items() if info["status"] == "EXACT_INFEASIBLE"]
    unresolved = [name for name in model["names"] if name not in possible + rejected]
    winners = []
    for name in model["names"]:
        related = [pair for pair in answer["pairs"] if name in (pair["a"], pair["b"])]
        if len(related) == model["n"] - 1 and all(
            pair["classification"]["status"] == ("VERIFIED_A_GREATER_B" if name == pair["a"] else "VERIFIED_B_GREATER_A")
            for pair in related):
            winners.append(name)
    answer.update({"overall_status": "EXACT_COMPATIBLE", "exact_possible_co_leaders": possible,
                   "exact_impossible_co_leaders": rejected, "unresolved_co_leaders": unresolved,
                   "verified_unique_leaders_above_margin_threshold": winners})
    return answer


def metadata_audit(inputs: Path, config: dict) -> tuple[dict, list, dict, dict]:
    inventory = native.archive_inventory(inputs)
    recovered = native.verify_recovery_identities(inventory, ROOT / "outputs/strengthening_20260926/source_recovery.json")
    receptors, profiles, summary = native.load_inputs(inputs)
    if native.sha256(JOINT_PATH.read_bytes()) != config["joint_ledger_sha256"]:
        raise ValueError("preexisting joint ledger identity differs")
    prior = json.loads(JOINT_PATH.read_bytes())
    fields = list(native.CONFIG["case_identity"])
    bridge = {tuple(s["sample"][key] for key in fields): s["retained_slots"] for s in prior["samples"]}
    if len(bridge) != len(receptors):
        raise ValueError("bridge sample identities not one-to-one")
    sources, species = native.CONFIG["central_initial_sources"], native.CONFIG["species"]
    validation_counts = Counter()
    for receptor in receptors:
        identity = tuple(receptor[key] for key in fields)
        retained = bridge[identity]
        if any(sid not in sources for sid in retained) or len(set(retained)) != len(retained):
            raise ValueError("bridge source universe differs")
        for name in species:
            c, uc = as_q(receptor[name]), as_q(receptor[name[:-1] + "U"])
            if uc <= 0 or c == -99:
                raise ValueError("invalid ambient interval input")
            validation_counts["ambient_species_pairs"] += 1
        if as_q(receptor["TMAC"]) <= 0:
            raise ValueError("invalid ambient mass")
    for sid in sources:
        for name in species:
            f, uf = as_q(profiles[sid][name]), as_q(profiles[sid][name[:-1] + "U"])
            if f < 0 or uf < 0:
                raise ValueError("negative/sentinel nominal profile or uncertainty")
            validation_counts["profile_species_pairs"] += 1
            validation_counts["zero_profile_uncertainty"] += uf == 0
            validation_counts["zero_profile_abundance"] += f == 0
            for k in (1, 2, 3):
                validation_counts[f"profile_upper_above_one_k{k}"] += f + k * uf > 1
    return {"status": "PASS", "identity_verification": recovered, "input_summary": summary,
            "validation_counts": dict(validation_counts),
            "physical_profile_columns_complete_disjoint": "NOT ESTABLISHED; no column-sum constraints",
            "uncertainty_semantics": "released uncertainty fields; k multiples are sensitivity bounds, not coverage probabilities",
            "manual_source": "https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P1009R4F.TXT",
            "physical_mass_upper_panel": "NOT RUN",
            "stage3_full_profile_grid": "NOT RUN"}, receptors, profiles, bridge


def stage1(inputs: Path) -> dict:
    config = configuration()
    metadata, _, _, _ = metadata_audit(inputs, config)
    tests = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests",
                            "-p", "test_interval_decisions.py", "-v"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    report = {"stage": 1, "completed_utc": now(), "status": "PASS" if tests.returncode == 0 else "HOLD_TEST_FAILURE",
              "configuration_sha256": CONFIG_HASH, "script_sha256": native.sha256(Path(__file__).read_bytes()),
              "tests_sha256": native.sha256((ROOT / "tests/test_interval_decisions.py").read_bytes()),
              "metadata": metadata, "test_exit_code": tests.returncode,
              "test_output": tests.stdout + tests.stderr,
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}}
    (PUBLIC / "interval_stage1.json").write_bytes(native.json_bytes(report))
    if tests.returncode:
        raise RuntimeError("synthetic gate failed; do not run field LPs")
    return report


def compact_result(result: dict) -> dict:
    pair_counts = Counter(pair["classification"]["status"] for pair in result["pairs"])
    bound_status = Counter(run["status"] for bounds in result["source_bounds"].values() for run in bounds.values())
    return {"overall_status": result["overall_status"], "pair_status_counts": dict(pair_counts),
            "source_bound_status_counts": dict(bound_status),
            "exact_possible_co_leaders": result.get("exact_possible_co_leaders", []),
            "unresolved_co_leaders": result.get("unresolved_co_leaders", []),
            "verified_unique_leaders_above_margin_threshold": result.get("verified_unique_leaders_above_margin_threshold", [])}


def aggregate(index: list[dict]) -> dict:
    groups = defaultdict(list)
    for record in index:
        key = (record["universe"], record["k"], record["profile_mode"], record["mass_mode"])
        groups[key].append(record)
    panels = []
    for key, records in sorted(groups.items()):
        panels.append({"universe": key[0], "k": key[1], "profile_mode": key[2], "mass_mode": key[3],
                       "initial_samples": len(records),
                       "compatibility_status": dict(Counter(r["summary"]["overall_status"] for r in records)),
                       "unique_leader_samples": sum(bool(r["summary"]["verified_unique_leaders_above_margin_threshold"]) for r in records),
                       "at_least_two_exact_possible_co_leaders_samples": sum(len(r["summary"]["exact_possible_co_leaders"]) >= 2 for r in records),
                       "unresolved_co_leader_samples": sum(bool(r["summary"]["unresolved_co_leaders"]) for r in records),
                       "pair_status_counts": dict(sum((Counter(r["summary"]["pair_status_counts"]) for r in records), Counter())),
                       "source_bound_status_counts": dict(sum((Counter(r["summary"]["source_bound_status_counts"]) for r in records), Counter()))})
    return {"panels": panels, "records": len(index), "all_initial_samples_per_panel_expected": 35}


def stage2(inputs: Path) -> dict:
    config = configuration()
    gate = json.loads((PUBLIC / "interval_stage1.json").read_bytes())
    if (gate["status"] != "PASS" or gate["configuration_sha256"] != CONFIG_HASH
            or gate["script_sha256"] != native.sha256(Path(__file__).read_bytes())
            or gate["tests_sha256"] != native.sha256((ROOT / "tests/test_interval_decisions.py").read_bytes())):
        raise ValueError("current code/configuration has not passed Stage1")
    metadata, receptors, profiles, bridge = metadata_audit(inputs, config)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    frozen = PRIVATE / "interval_configuration_frozen.json"
    if frozen.exists() and frozen.read_bytes() != CONFIG_PATH.read_bytes():
        raise ValueError("private interval freeze differs")
    frozen.write_bytes(CONFIG_PATH.read_bytes())
    case_dir = PRIVATE / "interval_cases"
    case_dir.mkdir(exist_ok=True)
    started, index, cache = now(), [], {}
    fields = list(native.CONFIG["case_identity"])
    for number, receptor in enumerate(receptors):
        identity = {key: receptor[key] for key in fields}
        retained = bridge[tuple(receptor[key] for key in fields)]
        for universe, sources in (("full_seven_primary", native.CONFIG["central_initial_sources"]),
                                  ("central_retained_bridge", retained)):
            for k, profile_mode, mass_mode in itertools.product(config["k_values"], config["profile_uncertainty"], config["mass_models"]):
                model = field_model(receptor, profiles, sources, k, profile_mode, mass_mode)
                model_bytes = native.json_bytes(encode_q(model))
                model_hash = native.sha256(model_bytes)
                cached = model_hash in cache
                if cached:
                    summary, case_hash = cache[model_hash]
                else:
                    result = analyze_model(model)
                    payload = native.json_bytes(encode_q({"configuration_sha256": CONFIG_HASH,
                               "model_sha256": model_hash, "model": model, "result": result}))
                    (case_dir / ("interval_case_" + model_hash + ".json")).write_bytes(payload)
                    summary, case_hash = compact_result(result), native.sha256(payload)
                    cache[model_hash] = summary, case_hash
                index.append({"sample": identity, "sample_zero_based_index": number, "universe": universe,
                              "k": k, "profile_mode": profile_mode, "mass_mode": mass_mode,
                              "model_sha256": model_hash, "case_sha256": case_hash, "cached_identical_model": cached,
                              "summary": summary})
                progress = {"stage": 2, "status": "RUNNING", "started_utc": started, "updated_utc": now(),
                            "configuration_sha256": CONFIG_HASH, "completed_records": len(index),
                            "expected_records": 35 * 2 * 3 * 2 * 2, "unique_models": len(cache)}
                (PUBLIC / "interval_progress.json").write_bytes(native.json_bytes(progress))
        (PRIVATE / "interval_index_partial.json").write_bytes(native.json_bytes({"started_utc": started, "records": index}))
        print(json.dumps({"sample_number_completed": number + 1, "of": len(receptors), "records": len(index), "unique_models": len(cache)}), flush=True)
    ledger = native.json_bytes({"configuration_sha256": CONFIG_HASH, "started_utc": started,
                               "completed_utc": now(), "records": index})
    (PRIVATE / "interval_index.json").write_bytes(ledger)
    report = {"stage": 2, "status": "COMPLETE", "started_utc": started, "completed_utc": now(),
              "configuration_sha256": CONFIG_HASH, "script_sha256": native.sha256(Path(__file__).read_bytes()),
              "stage1": {key: gate[key] for key in ("status", "script_sha256", "tests_sha256", "completed_utc")},
              "metadata": metadata, "environment": gate["environment"], "unique_models": len(cache),
              "private_index_sha256": native.sha256(ledger), "aggregate": aggregate(index),
              "public_scope": "Aggregate compatibility counts and certificate-status counts only; per-sample matrices, contributions and certificates private.",
              "limits": config["limitations"]}
    (PUBLIC / "interval_results.json").write_bytes(native.json_bytes(report))
    (PUBLIC / "interval_progress.json").write_bytes(native.json_bytes({"stage": 2, "status": "COMPLETE",
          "completed_records": len(index), "expected_records": 840, "unique_models": len(cache), "completed_utc": now()}))
    (PUBLIC / "interval_report.md").write_text(render_report(report), encoding="utf-8", newline="\n")
    return report


def render_report(report: dict) -> str:
    rows = ["# Interval decision audit — central historical profile system only", "",
            "This is an exploratory application of established interval/set-membership mathematics, not a new theorem or confidence procedure.", "",
            f"Stage 1: **{report['stage1']['status']}**. Stage 2: **{report['status']}**. No Stage 3 full-profile-grid LP was run.",
            f"Frozen configuration SHA-256: `{CONFIG_HASH}`. All 35 samples retained in every panel.", "",
            "## Compatibility and decision outcomes", "",
            "Each row is a separate panel. The historical mass band is a diagnostic sensitivity, not physical conservation. Independent entrywise boxes do not establish physical attainability of every witness.", "",
            "| Universe | k | Uncertainty | Mass model | Exact feasible | Exact infeasible | Unresolved | Verified unique leader | >=2 exact possible co-leaders |",
            "|---|---:|---|---|---:|---:|---:|---:|---:|"]
    for panel in report["aggregate"]["panels"]:
        status = panel["compatibility_status"]
        rows.append(f"| {panel['universe']} | {panel['k']} | {panel['profile_mode']} | {panel['mass_mode']} | {status.get('EXACT_COMPATIBLE', 0)} | {status.get('EXACT_INFEASIBLE', 0)} | {status.get('NUMERICALLY_UNRESOLVED', 0)} | {panel['unique_leader_samples']} | {panel['at_least_two_exact_possible_co_leaders_samples']} |")
    rows += ["", "## Verification and interpretation", "",
             "- Exact feasible status requires a rational point independently satisfying every inequality. Exact infeasible status requires an independently verified rational Farkas certificate.",
             "- A verified order uses a rational, residual-corrected dual lower bound with independently justified source upper bounds, an exactly feasible primal point, and a fixed-method floating solver cross-check. Float solver optimality is never itself called a proof.",
             "- Exact unboundedness requires an exactly feasible point and an exactly verified improving recession ray. Any missing proof component remains unresolved.",
             "- A nonpositive lower bound alone does not establish reversal: reversal/order/tie labels require exactly feasible witnesses.",
             "- Co-leader feasibility imposes all leader inequalities simultaneously. Separate pairwise possibilities are insufficient.",
             "- Nonnegative sources are an explicit modeling restriction. The full-seven universe is primary; the fit-pruned retained universe is a separately labeled bridge sensitivity.",
             "- KEEP the qualified compatibility results and proof objects; HOLD external accuracy, probabilistic coverage, physical box attainability and full-profile-grid claims.",
             f"- Private index SHA-256: `{report['private_index_sha256']}`; case files are individually hashed in that private index.", "",
             "## Reproduce", "", "```text", "python scripts/audit_interval_decisions.py --stage1",
             "python scripts/audit_interval_decisions.py --run-field-stage2", "```", ""]
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=native.DEFAULT_INPUT)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--stage1", action="store_true")
    modes.add_argument("--run-field-stage2", action="store_true")
    args = parser.parse_args()
    report = stage1(args.inputs) if args.stage1 else stage2(args.inputs)
    print(json.dumps({"stage": report["stage"], "status": report["status"]}, indent=2))


if __name__ == "__main__":
    main()
