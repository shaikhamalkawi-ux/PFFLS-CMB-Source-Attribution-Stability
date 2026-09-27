#!/usr/bin/env python3
"""Synthetic mathematical falsification tests, not environmental observations.

The example is deliberately constructed. Exact Fraction arithmetic independently
checks a full-rank, positive-profile CMB example where all one-at-a-time swaps
preserve the leading source and a simultaneous swap reverses it. No EPA data are
read, no manuscript file is altered, and no result is written to disk.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import product
from math import inf
import unittest

import numpy as np

from audit_epa_native_strengthening import effective_variance_fit


PROFILE_PARAMETERS = ((Q(-2), Q(-14, 5)), (Q(3), Q(5, 2)))
SPECIES = ["X1C", "X2C", "X3C"]
OBSERVED = (Q(3), Q(3), Q(4))


def profile(t: Q) -> tuple[Q, ...]:
    return (Q(3, 10) + t / 20, Q(3, 10) - t / 25, Q(2, 5) - t / 100)


def exact_fit(choice: tuple[int, int]) -> tuple[Q, Q]:
    a, b = (PROFILE_PARAMETERS[i][choice[i]] for i in range(2))
    return Q(10) * b / (b - a), Q(10) * (-a) / (b - a)


def exact_left_inverse(choice: tuple[int, int]) -> tuple[tuple[Q, ...], ...]:
    """(F^T F)^-1 F^T via exact 2-by-2 algebra; no numerical fitting."""
    u, v = (profile(PROFILE_PARAMETERS[i][choice[i]]) for i in range(2))
    aa, ab, bb = sum(x*x for x in u), sum(x*y for x, y in zip(u, v)), sum(y*y for y in v)
    determinant = aa * bb - ab * ab
    if determinant <= 0:
        raise ValueError("example profile matrix is not full rank")
    return (tuple((bb*x-ab*y)/determinant for x, y in zip(u, v)),
            tuple((aa*y-ab*x)/determinant for x, y in zip(u, v)))


def exact_receptor_radius() -> Q:
    """Strict L-infinity receptor radius preserving every example top decision.

    This is a deterministic fixed-profile ordinary-LS calculation, not a
    confidence interval or an error certificate for uncertainty-weighted EVLS.
    """
    radii = []
    for choice in product(range(2), repeat=2):
        pinv = exact_left_inverse(choice)
        contrast = tuple(a-b for a, b in zip(*pinv))
        margin = sum(a*b for a, b in zip(contrast, OBSERVED))
        radii.append(abs(margin) / sum(abs(v) for v in contrast))
    return min(radii)


def radius_bounds(states: dict[tuple[int, ...], str], axis_sizes: tuple[int, ...]) -> dict:
    """Sound bounds for a COMPLETE finite enumeration with unresolved entries.

    Input labels describe mathematically resolved decisions or the decisions of
    a declared finite computational procedure. They are not proof that a 1%
    EVLS stopping rule bounds the unknown error in an exact nonlinear solution.
    A 'bad' result includes a tie if the declared question is unique-winner
    preservation. 'excluded' must mean established inadmissibility, not failure
    to converge. The all-zero central choice must be admissible and stable.
    """
    if not axis_sizes or any(not isinstance(n, int) or isinstance(n, bool) or n < 1 for n in axis_sizes):
        raise ValueError("positive integer axis sizes required")
    universe = set(product(*(range(n) for n in axis_sizes)))
    if set(states) != universe:
        raise ValueError("incomplete enumeration; missing choices cannot be discarded")
    if any(status not in {"stable", "bad", "excluded", "unknown"} for status in states.values()):
        raise ValueError("unrecognized state")
    if states[(0,) * len(axis_sizes)] != "stable":
        raise ValueError("central fit must establish a unique admissible leading source")
    distance = lambda choice: sum(value != 0 for value in choice)
    witness = min((distance(c) for c, s in states.items() if s == "bad"), default=inf)
    unresolved = min((distance(c) for c, s in states.items() if s == "unknown"), default=inf)
    lower = min(witness, unresolved)
    maximum_distance = sum(size > 1 for size in axis_sizes)
    certified_through = maximum_distance if lower == inf else int(lower) - 1
    return {"minimum_bad_distance_lower": lower, "minimum_bad_distance_upper": witness,
            "first_unresolved_distance": unresolved, "certified_through_distance": certified_through,
            "exact_minimum_known": lower == witness,
            "scope": "declared finite universe and decision procedure only"}


class PositiveCmbCounterexample(unittest.TestCase):
    def test_profiles_are_strictly_positive_and_normalized(self):
        for options in PROFILE_PARAMETERS:
            for t in options:
                values = profile(t)
                self.assertTrue(all(value > 0 for value in values))
                self.assertEqual(sum(values), 1)

    def test_all_four_designs_are_full_rank(self):
        for choice in product(range(2), repeat=2):
            pinv = exact_left_inverse(choice)
            columns = [profile(PROFILE_PARAMETERS[i][choice[i]]) for i in range(2)]
            for i, row in enumerate(pinv):
                for j, column in enumerate(columns):
                    self.assertEqual(sum(a*b for a, b in zip(row, column)), int(i == j))

    def test_exact_positive_fit_and_mass_closure(self):
        for choice in product(range(2), repeat=2):
            values = exact_fit(choice)
            self.assertTrue(all(value > 0 for value in values))
            self.assertEqual(sum(values), 10)
            columns = [profile(PROFILE_PARAMETERS[i][choice[i]]) for i in range(2)]
            predicted = tuple(sum(values[j]*columns[j][i] for j in range(2)) for i in range(3))
            self.assertEqual(predicted, OBSERVED)

    def test_every_one_at_a_time_swap_keeps_a_largest(self):
        for choice in ((0, 0), (1, 0), (0, 1)):
            a, b = exact_fit(choice)
            self.assertGreater(a, b)

    def test_joint_swap_reverses_largest_source(self):
        a, b = exact_fit((1, 1))
        self.assertLess(a, b)
        self.assertEqual((a, b), (Q(250, 53), Q(280, 53)))

    def test_closed_form_contributions(self):
        self.assertEqual(exact_fit((0, 0)), (Q(6), Q(4)))
        self.assertEqual(exact_fit((1, 0)), (Q(150, 29), Q(140, 29)))
        self.assertEqual(exact_fit((0, 1)), (Q(50, 9), Q(40, 9)))

    def test_counterexample_has_nonzero_receptor_perturbation_neighborhood(self):
        # Exactly derived radius, independent of a grid or a positive search.
        radius = exact_receptor_radius()
        self.assertGreater(radius, Q(1, 100))
        for choice in product(range(2), repeat=2):
            pinv = exact_left_inverse(choice)
            wanted = 1 if choice != (1, 1) else -1
            for signs in product((-1, 1), repeat=3):
                observed = tuple(value + sign*radius/2 for value, sign in zip(OBSERVED, signs))
                fit = tuple(sum(a*b for a, b in zip(row, observed)) for row in pinv)
                self.assertGreater(wanted*(fit[0]-fit[1]), 0)

    def test_small_noisy_receptors_retain_good_fits_and_joint_reversal(self):
        saw_nonzero_residual = False
        for choice in product(range(2), repeat=2):
            pinv = exact_left_inverse(choice)
            columns = [profile(PROFILE_PARAMETERS[i][choice[i]]) for i in range(2)]
            wanted = 1 if choice != (1, 1) else -1
            for signs in product((-1, 1), repeat=3):
                observed = tuple(value + Q(sign, 100) for value, sign in zip(OBSERVED, signs))
                fit = tuple(sum(a*b for a, b in zip(row, observed)) for row in pinv)
                predicted = tuple(sum(fit[j]*columns[j][i] for j in range(2)) for i in range(3))
                residual = sum((a-b)**2 for a, b in zip(observed, predicted))
                saw_nonzero_residual |= residual > 0
                chi2 = residual / Q(1, 20)**2  # Three species minus two sources = one d.f.
                r2 = 1 - residual / sum(value**2 for value in observed)
                percent_mass = 10 * sum(fit)
                self.assertTrue(all(value > 0 for value in fit))
                self.assertGreater(wanted*(fit[0]-fit[1]), 0)
                self.assertLessEqual(chi2, Q(3, 25))
                self.assertGreater(r2, Q(8, 10))
                self.assertGreaterEqual(percent_mass, 80)
                self.assertLessEqual(percent_mass, 120)
        self.assertTrue(saw_nonzero_residual)

    def test_frozen_evls_agrees_with_independent_exact_algebra(self):
        receptor = {name: float(value) for name, value in zip(SPECIES, OBSERVED)}
        receptor.update({name[:-1]+"U": 0.05 for name in SPECIES})
        receptor["TMAC"] = 10.0
        for choice in product(range(2), repeat=2):
            profiles = {}
            for j, sid in enumerate(("A", "B")):
                profiles[sid] = {name: float(value) for name, value in zip(SPECIES, profile(PROFILE_PARAMETERS[j][choice[j]]))}
                profiles[sid].update({name[:-1]+"U": 0.0 for name in SPECIES})
            result = effective_variance_fit(receptor, profiles, ["A", "B"], species=SPECIES)
            self.assertTrue(result["converged"])
            np.testing.assert_allclose(list(result["source_contributions"].values()),
                                       [float(value) for value in exact_fit(choice)], rtol=0, atol=1e-12)
            self.assertAlmostEqual(result["R2"], 1.0, places=12)
            self.assertLess(result["reduced_chi2"], 1e-20)
            self.assertAlmostEqual(result["percent_mass"], 100.0, places=12)


class SoundUnresolvedCertificate(unittest.TestCase):
    def setUp(self):
        self.stable = {choice: "stable" for choice in product(range(2), repeat=2)}

    def test_complete_stability_is_finite_scope_only(self):
        result = radius_bounds(self.stable, (2, 2))
        self.assertEqual(result["minimum_bad_distance_lower"], inf)
        self.assertEqual(result["certified_through_distance"], 2)

    def test_joint_witness_yields_exact_radius_two(self):
        self.stable[(1, 1)] = "bad"
        result = radius_bounds(self.stable, (2, 2))
        self.assertEqual(result["minimum_bad_distance_lower"], 2)
        self.assertEqual(result["minimum_bad_distance_upper"], 2)
        self.assertEqual(result["certified_through_distance"], 1)

    def test_nearer_unknown_prevents_exact_radius_claim(self):
        self.stable[(1, 0)] = "unknown"
        self.stable[(1, 1)] = "bad"
        result = radius_bounds(self.stable, (2, 2))
        self.assertEqual((result["minimum_bad_distance_lower"], result["minimum_bad_distance_upper"]), (1, 2))
        self.assertEqual(result["certified_through_distance"], 0)
        self.assertFalse(result["exact_minimum_known"])

    def test_equal_distance_unknown_does_not_reduce_witness_lower_bound(self):
        self.stable[(1, 0)] = "unknown"
        self.stable[(0, 1)] = "bad"
        result = radius_bounds(self.stable, (2, 2))
        self.assertEqual((result["minimum_bad_distance_lower"], result["minimum_bad_distance_upper"]), (1, 1))

    def test_unknown_without_witness_is_not_a_stability_certificate(self):
        self.stable[(1, 1)] = "unknown"
        result = radius_bounds(self.stable, (2, 2))
        self.assertEqual(result["minimum_bad_distance_lower"], 2)
        self.assertEqual(result["minimum_bad_distance_upper"], inf)
        self.assertEqual(result["certified_through_distance"], 1)

    def test_incomplete_universe_is_rejected(self):
        del self.stable[(1, 1)]
        with self.assertRaises(ValueError):
            radius_bounds(self.stable, (2, 2))

    def test_unresolved_central_anchor_is_rejected(self):
        self.stable[(0, 0)] = "unknown"
        with self.assertRaises(ValueError):
            radius_bounds(self.stable, (2, 2))

    def test_all_possible_resolutions_obey_bounds(self):
        # Exhaust all 4^3 labelled finite ensembles and every admissible
        # completion of unknown states; this checks the proposition directly.
        tail = [(0, 1), (1, 0), (1, 1)]
        for labels in product(("stable", "bad", "excluded", "unknown"), repeat=3):
            states = {(0, 0): "stable", **dict(zip(tail, labels))}
            result = radius_bounds(states, (2, 2))
            unknown = [key for key, value in states.items() if value == "unknown"]
            for completions in product(("stable", "bad", "excluded"), repeat=len(unknown)):
                completed = {**states, **dict(zip(unknown, completions))}
                actual = min((sum(x != 0 for x in key) for key, value in completed.items() if value == "bad"), default=inf)
                self.assertLessEqual(result["minimum_bad_distance_lower"], actual)
                self.assertLessEqual(actual, result["minimum_bad_distance_upper"])


if __name__ == "__main__":
    unittest.main()
