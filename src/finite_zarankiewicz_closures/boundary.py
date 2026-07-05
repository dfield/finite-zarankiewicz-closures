"""Exact-rational diagnostics for the Davies--Gill--Horsley LP boundary.

These formulas implement the degree-count inequalities in Theorem 1.2 of
Davies, Gill, and Horsley (2026).  This module is explanatory: the elementary
upper-bound proof does not depend on the LP.  Its purpose is to show exactly
why that stronger published relaxation still rounds down only to 104.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Union


ROWS = 9
COLUMNS = 23
S = 3
T = 3
PROFILES = {
    "balanced": {4: 11, 5: 12},
    "one_degree_3": {3: 1, 4: 9, 5: 13},
    "one_degree_6": {4: 12, 5: 10, 6: 1},
}


def rational_text(value: Union[Fraction, int]) -> str:
    """Render an exact rational without a redundant denominator."""

    fraction = Fraction(value)
    if fraction.denominator == 1:
        return str(fraction.numerator)
    return f"{fraction.numerator}/{fraction.denominator}"


def dgh_constraint(v: int, k: int) -> tuple[dict[int, Fraction], Fraction, int]:
    """Return coefficients, right side, and remainder for one DGH inequality."""

    denominator_binomial = math.comb(k - v, S - v)
    available = (T - 1) * math.comb(ROWS - v, S - v)
    alpha = available % denominator_binomial
    coefficients: dict[int, Fraction] = {}
    for degree in range(S - 1, ROWS + 1):
        if degree < k:
            small = math.comb(degree - v, S - v) if degree - v >= S - v else 0
            coefficient = Fraction(small - alpha, denominator_binomial - alpha) * math.comb(
                degree, v
            )
        else:
            coefficient = Fraction(math.comb(degree, v))
        coefficients[degree] = coefficient
    right_side = Fraction(
        math.comb(ROWS, v) * (available - alpha), denominator_binomial
    )
    return coefficients, right_side, alpha


def _evaluate(
    coefficients: dict[int, Fraction], counts: dict[int, Union[int, Fraction]]
) -> Fraction:
    return sum(
        (
            coefficients.get(degree, Fraction(0)) * count
            for degree, count in counts.items()
        ),
        Fraction(0),
    )


def boundary_report() -> dict[str, object]:
    """Construct the exact LP report embedded in the repository."""

    roman_bounds = []
    for k in range(S - 1, ROWS + 1):
        value = Fraction((T - 1) * math.comb(ROWS, S), math.comb(k, S - 1)) + Fraction(
            (k + 1) * (S - 1) * COLUMNS, S
        )
        roman_bounds.append(
            {"k": k, "value": rational_text(value), "floor": value.numerator // value.denominator}
        )

    constraints = [
        (
            "roman_triple_capacity",
            {degree: Fraction(math.comb(degree, S)) for degree in range(2, ROWS + 1)},
            Fraction((T - 1) * math.comb(ROWS, S)),
            None,
            None,
        )
    ]
    for v in range(1, S):
        for k in range(S, ROWS + 1):
            coefficients, right_side, alpha = dgh_constraint(v, k)
            constraints.append((f"dgh_v{v}_k{k}", coefficients, right_side, v, alpha))

    # Intersection of n4+n5=23 and 4*n4+10*n5=168.
    optimum_counts = {4: Fraction(31, 3), 5: Fraction(38, 3)}
    optimum = sum(
        (Fraction(degree) * count for degree, count in optimum_counts.items()),
        Fraction(0),
    )
    if optimum != Fraction(314, 3):
        raise AssertionError("unexpected Roman boundary")
    optimum_checks = []
    for name, coefficients, right_side, v, alpha in constraints:
        left_side = _evaluate(coefficients, optimum_counts)
        if left_side > right_side:
            raise AssertionError(f"fractional optimum violates {name}")
        optimum_checks.append(
            {
                "constraint": name,
                "lhs": rational_text(left_side),
                "rhs": rational_text(right_side),
                "slack": rational_text(right_side - left_side),
                "v": v,
                "alpha": alpha,
            }
        )

    integer_profiles = []
    for case_name, counts in PROFILES.items():
        checks = []
        for name, coefficients, right_side, _v, _alpha in constraints:
            left_side = _evaluate(coefficients, counts)
            if left_side > right_side:
                raise AssertionError(f"{case_name} violates {name}")
            checks.append(
                {
                    "constraint": name,
                    "lhs": rational_text(left_side),
                    "rhs": rational_text(right_side),
                    "slack": rational_text(right_side - left_side),
                }
            )
        integer_profiles.append(
            {
                "case": case_name,
                "degree_counts": counts,
                "objective": sum(degree * count for degree, count in counts.items()),
                "triple_incidences": sum(
                    math.comb(degree, 3) * count for degree, count in counts.items()
                ),
                "all_dgh_constraints_satisfied": True,
                "constraints": checks,
            }
        )

    return {
        "problem": "Z(9,23,3,3)",
        "source": {
            "authors": ["Sara Davies", "Peter Gill", "Daniel Horsley"],
            "title": "Improved upper bounds on Zarankiewicz numbers",
            "doi": "10.1016/j.disc.2025.114924",
            "arxiv": "2411.18842v2",
        },
        "roman_bounds": roman_bounds,
        "full_dgh_lp": {
            "exact_optimum": rational_text(optimum),
            "floor_upper_bound": optimum.numerator // optimum.denominator,
            "optimal_degree_profile": {
                str(degree): rational_text(count) for degree, count in optimum_counts.items()
            },
            "constraint_checks_at_optimum": optimum_checks,
        },
        "integer_profiles_at_objective_104": integer_profiles,
        "interpretation": (
            "The full degree-count relaxation retains the Roman optimum 314/3, and all three "
            "integral profiles at weight 104 satisfy every listed inequality. The final "
            "contradiction requires marked-row overlap information absent from this LP."
        ),
    }


KERNEL_FIELDS = [
    "kernel_id",
    "family",
    "ambient_rows",
    "kernel_width",
    "row_symmetry_orbit",
    "orbit_size",
    "weight_or_degree",
    "triple_incidence",
    "affine_lower_value",
    "gap_or_penalty",
    "marked_membership",
    "marked_triple_contribution",
    "deficit_residue_mod_3",
    "classification",
    "role",
]


def kernel_catalog_rows() -> list[dict[str, object]]:
    """Return the complete one-column row-symmetry quotient used in discovery.

    This is not an enumeration of arbitrary multi-column submatrices.  It is
    the complete quotient of the local one-column kernels that feed the proof:
    restrictions to three through five rows, all ten ambient degrees, and the
    marked-row membership types for degrees 3--6.
    """

    rows: list[dict[str, object]] = []
    for local_rows in range(3, 6):
        for weight in range(local_rows + 1):
            rows.append(
                {
                    "kernel_id": f"restricted_{local_rows}r_w{weight}",
                    "family": "single_column_restriction",
                    "ambient_rows": local_rows,
                    "kernel_width": 1,
                    "row_symmetry_orbit": f"weight_{weight}",
                    "orbit_size": math.comb(local_rows, weight),
                    "weight_or_degree": weight,
                    "triple_incidence": math.comb(weight, 3),
                    "affine_lower_value": "",
                    "gap_or_penalty": "",
                    "marked_membership": "",
                    "marked_triple_contribution": "",
                    "deficit_residue_mod_3": "",
                    "classification": "complete_row_symmetry_orbit",
                    "role": "one-column restriction quotient",
                }
            )

    for degree in range(ROWS + 1):
        incidence = math.comb(degree, 3)
        affine = 6 * degree - 20
        gap = incidence - affine
        classification = "equality" if gap == 0 else "near_equality" if gap <= 4 else "excluded_at_104"
        rows.append(
            {
                "kernel_id": f"column_9r_d{degree}",
                "family": "sharp_column_penalty",
                "ambient_rows": ROWS,
                "kernel_width": 1,
                "row_symmetry_orbit": f"degree_{degree}",
                "orbit_size": math.comb(ROWS, degree),
                "weight_or_degree": degree,
                "triple_incidence": incidence,
                "affine_lower_value": affine,
                "gap_or_penalty": gap,
                "marked_membership": "",
                "marked_triple_contribution": "",
                "deficit_residue_mod_3": "",
                "classification": classification,
                "role": "local inequality C(d,3) >= 6d-20",
            }
        )

    for degree in (3, 4, 5, 6):
        for membership in (0, 1):
            contribution = math.comb(degree - 1, 2) if membership else 0
            rows.append(
                {
                    "kernel_id": f"marked_d{degree}_in{membership}",
                    "family": "marked_row_overlap",
                    "ambient_rows": ROWS,
                    "kernel_width": 1,
                    "row_symmetry_orbit": f"degree_{degree}_membership_{membership}",
                    "orbit_size": math.comb(8, degree - 1) if membership else math.comb(8, degree),
                    "weight_or_degree": degree,
                    "triple_incidence": math.comb(degree, 3),
                    "affine_lower_value": 6 * degree - 20,
                    "gap_or_penalty": math.comb(degree, 3) - (6 * degree - 20),
                    "marked_membership": membership,
                    "marked_triple_contribution": contribution,
                    "deficit_residue_mod_3": (56 - contribution) % 3,
                    "classification": "overlap_residue_type",
                    "role": "equality/near-equality compatibility",
                }
            )
    return rows
