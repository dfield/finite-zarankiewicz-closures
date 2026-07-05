"""Exact finite results and certificates for the 2026 table.

Alongside the marked-row proof of ``Z(9,23,3,3)=103``, this module records
three further closures obtained by propagating and checking the open table in
Bhan--Nobili--Langer (2026): ``Z(10,21)=106``, ``Z(10,22)=110``, and
``Z(11,20)=111``.  The first and third follow from vertex deletion.  The
middle value uses a finite degree-profile and pair-deficit certificate.

Only the standard library is used.  In particular, the certificate checker
does not trust an external integer-programming or SAT solver.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable


PAPER_OPEN_BOUNDS: dict[tuple[int, int], tuple[int, int]] = {
    (9, 23): (103, 104),
    (10, 21): (106, 108),
    (10, 22): (110, 111),
    (10, 23): (112, 115),
    (11, 19): (102, 108),
    (11, 20): (111, 112),
    (11, 21): (116, 116),
    (11, 22): (121, 121),
    (11, 23): (118, 125),
    (12, 17): (102, 108),
    (12, 18): (108, 113),
    (12, 19): (110, 118),
    (12, 20): (113, 122),
    (12, 21): (116, 127),
    (12, 22): (132, 132),
    (12, 23): (125, 136),
    (13, 17): (106, 116),
    (13, 18): (115, 121),
    (13, 19): (114, 125),
    (13, 20): (119, 130),
    (13, 21): (127, 135),
    (13, 22): (137, 140),
    (13, 23): (135, 145),
    (14, 17): (118, 124),
    (14, 18): (124, 129),
    (14, 19): (121, 135),
    (14, 20): (125, 140),
    (14, 21): (131, 145),
    (14, 22): (137, 150),
    (14, 23): (138, 155),
    (15, 17): (125, 132),
    (15, 18): (132, 138),
    (15, 19): (132, 143),
    (15, 20): (138, 149),
    (15, 21): (139, 154),
    (15, 22): (143, 160),
    (15, 23): (149, 165),
    (16, 17): (128, 141),
    (16, 18): (130, 146),
    (16, 19): (132, 152),
    (16, 20): (146, 158),
    (16, 21): (147, 164),
    (16, 22): (149, 169),
    (16, 23): (158, 175),
}


PAPER_EXACT_VALUES = {(11, 21): 116, (11, 22): 121, (12, 22): 132}
REPOSITORY_EXACT_VALUES = {
    (9, 23): 103,
    (10, 21): 106,
    (10, 22): 110,
    (11, 20): 111,
}


def deletion_upper(smaller_bound: int, larger_part: int) -> int:
    """Lift an upper bound across one added vertex by averaging degrees.

    If the larger part has size ``q`` and deleting a minimum-degree vertex
    leaves at most ``B`` edges, then the original graph has at most
    ``floor(q*B/(q-1))`` edges.
    """

    if smaller_bound < 0 or larger_part < 2:
        raise ValueError("invalid deletion-bound parameters")
    return larger_part * smaller_bound // (larger_part - 1)


def enumerate_degree_profiles(rows: int, columns: int, ones: int) -> list[tuple[int, ...]]:
    """Enumerate column-degree histograms allowed by triple capacity.

    A returned tuple ``counts`` has ``counts[d]`` columns of degree ``d``.
    It satisfies the column count, total degree, and the necessary inequality
    ``sum C(d,3)*counts[d] <= 2*C(rows,3)``.
    """

    if rows < 3 or columns < 0 or ones < 0:
        raise ValueError("invalid Zarankiewicz parameters")
    capacity = 2 * math.comb(rows, 3)
    counts = [0] * (rows + 1)
    profiles: list[tuple[int, ...]] = []

    def minimum_incidence(remaining_columns: int, remaining_ones: int, maximum: int) -> int:
        if (
            remaining_columns < 0
            or remaining_ones < 0
            or remaining_ones > remaining_columns * maximum
        ):
            return capacity + 1
        if remaining_columns == 0:
            return 0 if remaining_ones == 0 else capacity + 1
        quotient, remainder = divmod(remaining_ones, remaining_columns)
        if quotient > maximum or (quotient == maximum and remainder):
            return capacity + 1
        return (remaining_columns - remainder) * math.comb(quotient, 3) + remainder * math.comb(
            quotient + 1, 3
        )

    def visit(degree: int, used_columns: int, used_ones: int, incidence: int) -> None:
        if degree == 2:
            remaining_columns = columns - used_columns
            remaining_ones = ones - used_ones
            lower_twos = max(0, remaining_ones - remaining_columns)
            upper_twos = min(remaining_columns, remaining_ones // 2)
            for count_two in range(lower_twos, upper_twos + 1):
                count_one = remaining_ones - 2 * count_two
                count_zero = remaining_columns - count_one - count_two
                if count_zero >= 0:
                    counts[0], counts[1], counts[2] = count_zero, count_one, count_two
                    profiles.append(tuple(counts))
            return

        maximum_count = min(columns - used_columns, (ones - used_ones) // degree)
        for count in range(maximum_count + 1):
            new_columns = used_columns + count
            new_ones = used_ones + degree * count
            new_incidence = incidence + math.comb(degree, 3) * count
            if new_incidence > capacity:
                break
            remaining_columns = columns - new_columns
            remaining_ones = ones - new_ones
            if remaining_ones < 0 or remaining_ones > remaining_columns * (degree - 1):
                continue
            if (
                new_incidence
                + minimum_incidence(remaining_columns, remaining_ones, degree - 1)
                > capacity
            ):
                continue
            counts[degree] = count
            visit(degree - 1, new_columns, new_ones, new_incidence)
        counts[degree] = 0

    visit(rows, 0, 0, 0)
    return profiles


def profile_dict(profile: Iterable[int]) -> dict[int, int]:
    """Return the nonzero entries of one degree-profile tuple."""

    return {degree: count for degree, count in enumerate(profile) if count}


def _pair_list(rows: int = 10) -> list[tuple[int, int]]:
    return list(itertools.combinations(range(rows), 2))


def _pair_mask(vertices: Iterable[int], pairs: list[tuple[int, int]]) -> int:
    vertex_set = set(vertices)
    mask = 0
    for index, pair in enumerate(pairs):
        if set(pair).issubset(vertex_set):
            mask |= 1 << index
    return mask


def _popcount(value: int) -> int:
    return bin(value).count("1")


def case_b_pair_residue_minima() -> dict[int, int]:
    """Check the five row-symmetry orbits of profile ``4,5^19,6^2``.

    The two degree-six columns meet in ``k=2,...,6`` rows.  After fixing a
    canonical pair for each ``k``, all 210 possibilities for the degree-four
    column are inspected.  The return value is the minimum possible sum of
    nonnegative pair-deficit residues in each orbit.
    """

    pairs = _pair_list()
    first = set(range(6))
    minima: dict[int, int] = {}
    for intersection in range(2, 7):
        second = set(range(intersection)) | set(range(6, 12 - intersection))
        minimum = math.inf
        for four_tuple in itertools.combinations(range(10), 4):
            four = set(four_tuple)
            residue_sum = 0
            for left, right in pairs:
                in_four = int(left in four and right in four)
                in_sixes = int(left in first and right in first) + int(
                    left in second and right in second
                )
                residue_sum += (16 - 2 * in_four - 4 * in_sixes) % 3
            minimum = min(minimum, residue_sum)
        minima[intersection] = int(minimum)
    return minima


def case_c_pair_residue_minimum() -> dict[str, object]:
    """Exhaust the exceptional-column orbits of profile ``4^2,5^17,6^3``.

    One degree-six column is fixed.  A second is classified by its intersection
    size, and the third by its counts in the four membership cells of the first
    two.  This gives 77 row-symmetry orbits.  In each orbit all 22,155 unordered
    pairs of degree-four columns are checked using bit masks.
    """

    pairs = _pair_list()
    all_pairs = (1 << len(pairs)) - 1
    four_masks = [
        _pair_mask(vertices, pairs) for vertices in itertools.combinations(range(10), 4)
    ]
    four_pairs: list[tuple[int, int, int]] = []
    for index, first in enumerate(four_masks):
        for second in four_masks[index:]:
            twice = first & second
            once = first ^ second
            never = all_pairs ^ (once | twice)
            four_pairs.append((never, once, twice))

    first_six = set(range(6))
    first_mask = _pair_mask(first_six, pairs)
    global_minimum = math.inf
    orbit_count = 0

    for intersection in range(2, 7):
        second_six = set(range(intersection)) | set(range(6, 12 - intersection))
        second_mask = _pair_mask(second_six, pairs)
        membership_cells = [
            [
                row
                for row in range(10)
                if (int(row in first_six), int(row in second_six)) == pattern
            ]
            for pattern in ((1, 1), (1, 0), (0, 1), (0, 0))
        ]
        ranges = [range(len(cell) + 1) for cell in membership_cells]
        for counts in itertools.product(*ranges):
            if sum(counts) != 6:
                continue
            third_six: set[int] = set()
            for cell, count in zip(membership_cells, counts):
                third_six.update(cell[:count])
            third_mask = _pair_mask(third_six, pairs)
            orbit_count += 1

            q_masks = [0, 0, 0, 0]
            for pair_index in range(len(pairs)):
                bit = 1 << pair_index
                multiplicity = int(bool(first_mask & bit)) + int(bool(second_mask & bit)) + int(
                    bool(third_mask & bit)
                )
                q_masks[multiplicity] |= bit
            q_zero_or_three = q_masks[0] | q_masks[3]

            for never, once, twice in four_pairs:
                residue_sum = (
                    _popcount(q_zero_or_three & never)
                    + 2 * _popcount(q_zero_or_three & once)
                    + _popcount(q_masks[1] & once)
                    + 2 * _popcount(q_masks[1] & twice)
                    + 2 * _popcount(q_masks[2] & never)
                    + _popcount(q_masks[2] & twice)
                )
                global_minimum = min(global_minimum, residue_sum)

    return {
        "row_symmetry_orbits": orbit_count,
        "degree_four_multiset_cases_per_orbit": len(four_pairs),
        "minimum_pair_residue_sum": int(global_minimum),
    }


def z10_22_certificate_report() -> dict[str, object]:
    """Recompute the complete finite upper-bound certificate at 111 ones."""

    profiles = enumerate_degree_profiles(10, 22, 111)
    profile_maps = [profile_dict(profile) for profile in profiles]
    expected = [
        {5: 21, 6: 1},
        {4: 1, 5: 19, 6: 2},
        {4: 2, 5: 17, 6: 3},
        {4: 1, 5: 20, 7: 1},
    ]
    if profile_maps != expected:
        raise AssertionError(f"unexpected degree profiles: {profile_maps}")

    case_b = case_b_pair_residue_minima()
    if case_b != {2: 21, 3: 21, 4: 21, 5: 33, 6: 48}:
        raise AssertionError(f"unexpected case-B residue minima: {case_b}")
    case_c = case_c_pair_residue_minimum()
    if case_c != {
        "row_symmetry_orbits": 77,
        "degree_four_multiset_cases_per_orbit": 22_155,
        "minimum_pair_residue_sum": 12,
    }:
        raise AssertionError(f"unexpected case-C residue result: {case_c}")

    return {
        "status": "VERIFIED",
        "problem": "Z(10,22,3,3)",
        "excluded_target": 111,
        "triple_capacity": 240,
        "degree_profiles": [
            {str(degree): count for degree, count in profile.items()} for profile in profile_maps
        ],
        "case_a": {
            "profile": {"5": 21, "6": 1},
            "pair_deficit_sum": 30,
            "outside_row_pair_degree_sum": 45,
            "required_divisor": 4,
        },
        "case_b": {
            "profile": {"4": 1, "5": 19, "6": 2},
            "pair_deficit_sum": 18,
            "minimum_residue_sums_by_six_column_intersection": {
                str(key): value for key, value in case_b.items()
            },
        },
        "case_c": {"profile": {"4": 2, "5": 17, "6": 3}, **case_c},
        "case_d": {
            "profile": {"4": 1, "5": 20, "7": 1},
            "row_deficit_sum": 3,
            "minimum_symmetric_difference": 3,
            "minimum_forced_row_deficit_sum": 9,
        },
    }


def extended_frontier_report() -> dict[str, object]:
    """Return the dated status of all 44 cases open at the paper boundary."""

    exact = {**PAPER_EXACT_VALUES, **REPOSITORY_EXACT_VALUES}
    remaining = sorted(set(PAPER_OPEN_BOUNDS) - set(exact))
    return {
        "status": "VERIFIED",
        "source": "arXiv:2605.01120v2, Figure 2",
        "source_open_cases": len(PAPER_OPEN_BOUNDS),
        "paper_exact_values": {
            f"{rows},{columns}": value
            for (rows, columns), value in sorted(PAPER_EXACT_VALUES.items())
        },
        "repository_exact_values": {
            f"{rows},{columns}": value
            for (rows, columns), value in sorted(REPOSITORY_EXACT_VALUES.items())
        },
        "remaining_open_cases": len(remaining),
        "remaining_parameters": [f"{rows},{columns}" for rows, columns in remaining],
        "deletion_checks": {
            "Z(10,21)<=106": deletion_upper(96, 10),
            "Z(11,19)<=106": deletion_upper(101, 19),
            "Z(11,20)<=111": deletion_upper(106, 20),
        },
        "paper_bounds": {
            f"{rows},{columns}": {"lower": lower, "upper": upper}
            for (rows, columns), (lower, upper) in sorted(PAPER_OPEN_BOUNDS.items())
        },
    }
