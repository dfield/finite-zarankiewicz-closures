"""Exact checker for the independent degree-deficit certificate.

The JSON certificate is treated as untrusted input.  In particular, this
module enumerates the feasible degree histograms itself instead of accepting
the certificate's three-case split.  It then recomputes every incidence,
deficit, residue, and strict contradiction used in Sections 3--5 of
``docs/PROOF.md``.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


class CertificateError(ValueError):
    """Raised when a certificate field disagrees with a recomputed fact."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def penalty(degree: int) -> int:
    """Return :math:`p(d)=\binom d3-6d+20` from the proof."""

    if not 0 <= degree <= 9:
        raise ValueError("a column degree must lie between 0 and 9")
    return math.comb(degree, 3) - 6 * degree + 20


def enumerate_degree_profiles(
    *, columns: int = 23, target_ones: int = 104, maximum_penalty: int = 4
) -> list[tuple[int, ...]]:
    """Enumerate all ten-entry degree histograms meeting the proof boundary.

    The recursion is tiny because positive penalties prune almost every branch.
    It is deliberately independent of the case list stored in the certificate.
    """

    found: list[tuple[int, ...]] = []

    def visit(
        degree: int,
        columns_left: int,
        weight_left: int,
        penalty_used: int,
        counts: tuple[int, ...],
    ) -> None:
        if penalty_used > maximum_penalty or weight_left < 0:
            return
        if degree == 9:
            count = columns_left
            if 9 * count != weight_left:
                return
            if penalty_used + count * penalty(9) <= maximum_penalty:
                found.append(counts + (count,))
            return
        for count in range(columns_left + 1):
            visit(
                degree + 1,
                columns_left - count,
                weight_left - degree * count,
                penalty_used + count * penalty(degree),
                counts + (count,),
            )

    visit(0, columns, target_ones, 0, ())
    return sorted(found)


def _integer_list(value: Any, *, length: int, field: str) -> list[int]:
    _require(isinstance(value, list), f"{field} must be a list")
    _require(len(value) == length, f"{field} must have length {length}")
    _require(
        all(type(item) is int and item >= 0 for item in value),
        f"{field} must contain nonnegative integers",
    )
    return value


def _expected_categories(counts: list[int], capacity: int, rows: int) -> list[dict[str, Any]]:
    """Compute row categories from a verified degree histogram."""

    exceptional = [degree for degree, count in enumerate(counts) if count and degree not in (4, 5)]
    _require(len(exceptional) <= 1, "a boundary profile has more than one exceptional degree")
    if not exceptional:
        residue = (capacity * math.comb(rows - 1, 2)) % 3
        return [
            {
                "rows": rows,
                "exceptional_degree": None,
                "exceptional_membership": None,
                "deficit_residue_mod_3": residue,
                "minimum_nonnegative_deficit": residue,
            }
        ]

    degree = exceptional[0]
    _require(counts[degree] == 1, "the exceptional degree must occur once")
    inside_residue = (
        capacity * math.comb(rows - 1, 2) - math.comb(degree - 1, 2)
    ) % 3
    outside_residue = (capacity * math.comb(rows - 1, 2)) % 3
    return [
        {
            "rows": degree,
            "exceptional_degree": degree,
            "exceptional_membership": True,
            "deficit_residue_mod_3": inside_residue,
            "minimum_nonnegative_deficit": inside_residue,
        },
        {
            "rows": rows - degree,
            "exceptional_degree": degree,
            "exceptional_membership": False,
            "deficit_residue_mod_3": outside_residue,
            "minimum_nonnegative_deficit": outside_residue,
        },
    ]


def verify_certificate(certificate: Mapping[str, Any]) -> dict[str, Any]:
    """Check the complete JSON reduction and return a compact audit report.

    No solver is invoked.  Success means the certificate agrees with exact
    integer arithmetic and that every enumerated 104-one degree profile has a
    marked-row deficit lower bound strictly larger than its exact total.
    """

    _require(certificate.get("certificate_type") == "exact_integer_double_counting", "unknown certificate type")
    problem = certificate.get("problem")
    _require(isinstance(problem, Mapping), "problem must be an object")
    expected_problem = {"columns": 23, "rows": 9, "target_ones": 104, "triple_capacity": 2}
    _require(dict(problem) == expected_problem, "problem parameters do not match the theorem")
    rows = 9
    columns = 23
    target = 104
    capacity = 2

    identity = certificate.get("global_identity")
    _require(isinstance(identity, Mapping), "global_identity must be an object")
    computed_penalties = [penalty(degree) for degree in range(rows + 1)]
    _require(identity.get("affine_slope") == 6, "wrong affine slope")
    _require(identity.get("affine_intercept_per_column") == -20, "wrong affine intercept")
    _require(identity.get("penalty_by_column_degree_0_through_9") == computed_penalties, "wrong penalty table")
    base = 6 * target - 20 * columns
    maximum = capacity * math.comb(rows, 3)
    maximum_penalty = maximum - base
    _require(identity.get("base_triple_incidence") == base == 164, "wrong base incidence")
    _require(identity.get("maximum_triple_incidence") == maximum == 168, "wrong maximum incidence")
    _require(identity.get("maximum_total_penalty") == maximum_penalty == 4, "wrong penalty budget")

    raw_cases = certificate.get("allowed_degree_cases")
    _require(isinstance(raw_cases, list), "allowed_degree_cases must be a list")
    claimed_profiles = []
    for index, case in enumerate(raw_cases):
        _require(isinstance(case, Mapping), f"case {index} must be an object")
        claimed_profiles.append(
            tuple(
                _integer_list(
                    case.get("counts_by_degree_0_through_9"),
                    length=10,
                    field=f"case {index} counts",
                )
            )
        )
    enumerated = enumerate_degree_profiles(
        columns=columns, target_ones=target, maximum_penalty=maximum_penalty
    )
    _require(sorted(claimed_profiles) == enumerated, "certificate case split is incomplete or duplicated")

    reports: list[dict[str, Any]] = []
    for case in raw_cases:
        name = case.get("name")
        _require(isinstance(name, str) and name, "every case needs a name")
        counts = _integer_list(
            case.get("counts_by_degree_0_through_9"), length=10, field=f"{name} counts"
        )
        _require(sum(counts) == columns, f"{name}: wrong column count")
        _require(sum(degree * count for degree, count in enumerate(counts)) == target, f"{name}: wrong total degree")
        incidences = sum(math.comb(degree, 3) * count for degree, count in enumerate(counts))
        deficit = maximum - incidences
        exact_marked_sum = 3 * deficit
        _require(case.get("triple_incidences") == incidences, f"{name}: wrong triple incidence")
        _require(case.get("global_deficit") == deficit, f"{name}: wrong global deficit")
        _require(case.get("sum_row_deficits") == exact_marked_sum, f"{name}: wrong marked deficit sum")

        expected_categories = _expected_categories(counts, capacity, rows)
        _require(case.get("row_categories") == expected_categories, f"{name}: wrong row categories")
        lower_bound = sum(
            category["rows"] * category["minimum_nonnegative_deficit"]
            for category in expected_categories
        )
        _require(
            case.get("certified_lower_bound_sum_row_deficits") == lower_bound,
            f"{name}: wrong certified lower bound",
        )
        _require(lower_bound > exact_marked_sum, f"{name}: no strict contradiction")

        exceptional = next(
            (degree for degree, count in enumerate(counts) if count and degree not in (4, 5)),
            None,
        )
        coefficients: dict[int, int] = {}
        for degree, count in enumerate(counts):
            if not count:
                continue
            numerator = math.comb(degree - 1, 2)
            if degree == exceptional:
                numerator += expected_categories[0]["deficit_residue_mod_3"] - 2
            _require(numerator % 3 == 0, f"{name}: nonintegral row-cut coefficient")
            coefficients[degree] = numerator // 3
        claimed_coefficients = case.get("row_cut_coefficients_by_degree")
        _require(isinstance(claimed_coefficients, Mapping), f"{name}: row coefficients missing")
        normalized = {int(key): value for key, value in claimed_coefficients.items()}
        _require(normalized == coefficients, f"{name}: wrong row-cut coefficients")
        _require(case.get("row_cut_rhs") == 18, f"{name}: wrong row-cut right side")
        aggregate_lhs = sum(degree * coefficients[degree] * count for degree, count in enumerate(counts) if count)
        aggregate_rhs = rows * 18
        _require(case.get("aggregate_row_cut_lhs") == aggregate_lhs, f"{name}: wrong aggregate left side")
        _require(case.get("aggregate_row_cut_rhs") == aggregate_rhs, f"{name}: wrong aggregate right side")
        _require(aggregate_lhs > aggregate_rhs, f"{name}: aggregate row cut is not contradictory")

        reports.append(
            {
                "name": name,
                "profile": counts,
                "exact_sum_row_deficits": exact_marked_sum,
                "residue_lower_bound": lower_bound,
                "aggregate_row_cut": [aggregate_lhs, aggregate_rhs],
            }
        )

    _require(
        certificate.get("conclusion") == "No 9-by-23 K_3,3-free Boolean matrix has 104 ones.",
        "wrong conclusion",
    )
    return {
        "status": "VERIFIED",
        "profiles_enumerated": len(enumerated),
        "penalty_table": computed_penalties,
        "cases": reports,
        "conclusion": certificate["conclusion"],
    }
