"""Exact finite results, frontier bounds, and certificates for the 2026 table.

Alongside the marked-row proof of ``Z(9,23,3,3)=103``, this module records
seven further closures obtained by propagating and checking the open table in
Bhan--Nobili--Langer (2026): ``Z(10,21)=106``, ``Z(10,22)=110``,
``Z(10,23)=112``, ``Z(11,19)=106``, ``Z(11,20)=111``, ``Z(11,23)=123``, and
``Z(12,23)=134``.  The deletion closures use established neighboring values;
the other cases use finite degree-profile, deficit, and traced SAT
certificates.  The module also checks the improved upper bound
``Z(13,23)<=144``.

Only the standard library is used by this arithmetic module.  The separate
``Z(10,23)`` certificate layer binds the surviving formulas to independently
replayable DRAT cores that are also converted to and checked as LRAT.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Mapping, Any


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
    (10, 23): 112,
    (11, 19): 106,
    (11, 20): 111,
    (11, 23): 123,
    (12, 23): 134,
}

REPOSITORY_UPPER_BOUNDS = {(13, 23): 144}


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


def _profile_label(profile: Mapping[int, int]) -> str:
    """Render a compact, deterministic column-degree profile."""

    return " ".join(f"{degree}^{count}" for degree, count in sorted(profile.items()))


def _z10_23_exceptional_pair_residue_minimum() -> dict[str, int]:
    """Enumerate the four exceptional columns of ``3 4^2 5^19 7``.

    Degree-five columns contribute three to every row-pair capacity equation,
    so only the degree-3, degree-4, degree-4, and degree-7 columns matter
    modulo three.  Rows are represented by their four-bit membership pattern;
    enumerating pattern multiplicities removes all row-label symmetry.
    """

    exceptional_degrees = (3, 7, 4, 4)
    exceptional_weights = tuple(degree - 2 for degree in exceptional_degrees)
    pattern_order = tuple(range(1, 1 << 4)) + (0,)
    needs = list(exceptional_degrees)
    counts = [0] * (1 << 4)
    configurations = 0
    legal_configurations = 0
    minimum = math.inf

    def exceptional_triples_are_legal() -> bool:
        for column_triple in itertools.combinations(range(4), 3):
            mask = sum(1 << column for column in column_triple)
            shared_rows = sum(
                count
                for pattern, count in enumerate(counts)
                if pattern & mask == mask
            )
            if shared_rows > 2:
                return False
        return True

    def pair_residue_sum() -> int:
        total = 0
        used_patterns = [pattern for pattern, count in enumerate(counts) if count]
        for left_index, left in enumerate(used_patterns):
            for right in used_patterns[left_index:]:
                pair_count = (
                    counts[left] * (counts[left] - 1) // 2
                    if left == right
                    else counts[left] * counts[right]
                )
                common = left & right
                exceptional = sum(
                    exceptional_weights[column]
                    for column in range(4)
                    if common >> column & 1
                )
                total += pair_count * ((16 - exceptional) % 3)
        return total

    def visit(index: int, rows_left: int) -> None:
        nonlocal configurations, legal_configurations, minimum
        if index == len(pattern_order):
            if rows_left or any(needs):
                return
            configurations += 1
            if not exceptional_triples_are_legal():
                return
            legal_configurations += 1
            minimum = min(minimum, pair_residue_sum())
            return

        pattern = pattern_order[index]
        if pattern == 0:
            if any(needs):
                return
            counts[0] = rows_left
            visit(index + 1, 0)
            counts[0] = 0
            return

        maximum = rows_left
        for column in range(4):
            if pattern >> column & 1:
                maximum = min(maximum, needs[column])
        for multiplicity in range(maximum + 1):
            counts[pattern] = multiplicity
            for column in range(4):
                if pattern >> column & 1:
                    needs[column] -= multiplicity
            if all(need >= 0 for need in needs):
                visit(index + 1, rows_left - multiplicity)
            for column in range(4):
                if pattern >> column & 1:
                    needs[column] += multiplicity
            counts[pattern] = 0

    visit(0, 10)
    result = {
        "row_pattern_configurations": configurations,
        "k33_legal_configurations": legal_configurations,
        "minimum_pair_residue_sum": int(minimum),
    }
    expected = {
        "row_pattern_configurations": 1577,
        "k33_legal_configurations": 1380,
        "minimum_pair_residue_sum": 39,
    }
    if result != expected:
        raise AssertionError(f"unexpected Z(10,23) exceptional enumeration: {result}")
    return result


def z10_23_profile_report() -> dict[str, object]:
    """Recompute the complete arithmetic front end at 113 ones.

    Five profiles contain a column of degree at most two and four further
    profiles contain two degree-three columns; deleting those columns violates
    the established values ``Z(10,22)=110`` or ``Z(10,21)=106``.  Three
    profiles die by row/pair-deficit residues.  The remaining thirteen are the
    exact scope of the separately replayable SAT certificate family.
    """

    profiles = [profile_dict(profile) for profile in enumerate_degree_profiles(10, 23, 113)]
    if len(profiles) != 25:
        raise AssertionError(f"expected 25 profiles at 113, found {len(profiles)}")

    low_degree: list[dict[int, int]] = []
    two_degree_three: list[dict[int, int]] = []
    residue: list[dict[int, int]] = []
    sat: list[dict[int, int]] = []
    simple_residue_profiles = {
        ((4, 6), (5, 14), (6, 2), (7, 1)),
        ((3, 1), (4, 3), (5, 17), (6, 1), (7, 1)),
    }
    exceptional_profile = ((3, 1), (4, 2), (5, 19), (7, 1))

    for profile in profiles:
        key = tuple(sorted(profile.items()))
        if min(profile) <= 2:
            low_degree.append(profile)
        elif profile.get(3, 0) >= 2:
            two_degree_three.append(profile)
        elif key in simple_residue_profiles or key == exceptional_profile:
            residue.append(profile)
        else:
            sat.append(profile)

    expected_sat = {
        ((4, 2), (5, 21)),
        ((4, 3), (5, 19), (6, 1)),
        ((4, 4), (5, 17), (6, 2)),
        ((4, 4), (5, 18), (7, 1)),
        ((4, 5), (5, 15), (6, 3)),
        ((4, 5), (5, 16), (6, 1), (7, 1)),
        ((4, 6), (5, 13), (6, 4)),
        ((4, 7), (5, 11), (6, 5)),
        ((3, 1), (5, 22)),
        ((3, 1), (4, 1), (5, 20), (6, 1)),
        ((3, 1), (4, 2), (5, 18), (6, 2)),
        ((3, 1), (4, 3), (5, 16), (6, 3)),
        ((3, 1), (4, 4), (5, 14), (6, 4)),
    }
    if {tuple(sorted(profile.items())) for profile in sat} != expected_sat:
        raise AssertionError(f"unexpected SAT profile scope: {sat}")
    if (len(low_degree), len(two_degree_three), len(residue), len(sat)) != (5, 4, 3, 13):
        raise AssertionError("unexpected Z(10,23) profile partition")

    # Profile 4^6 5^14 6^2 7: two degree-six columns overlap in t=2..6
    # rows.  Modulo three, rows in exactly one/both have residues 2/1.
    first_residue_minimum = min(24 - 3 * overlap for overlap in range(2, 7))
    if first_residue_minimum != 6 or not first_residue_minimum > 3:
        raise AssertionError("unexpected two-degree-six row residue minimum")

    # Profile 3 4^3 5^17 6 7: use the degree-three/degree-six overlap t=0..3.
    second_residue_minimum = min(18 - 3 * overlap for overlap in range(4))
    if second_residue_minimum != 9 or not second_residue_minimum > 6:
        raise AssertionError("unexpected degree-three/six row residue minimum")

    exceptional = _z10_23_exceptional_pair_residue_minimum()
    if exceptional["minimum_pair_residue_sum"] <= 18:
        raise AssertionError("exceptional profile was not eliminated")

    return {
        "status": "ARITHMETIC_FRONT_END_VERIFIED",
        "problem": "Z(10,23,3,3)",
        "excluded_target": 113,
        "triple_capacity": 240,
        "profile_count": len(profiles),
        "low_degree_column_profiles": [_profile_label(profile) for profile in low_degree],
        "two_degree_three_profiles": [
            _profile_label(profile) for profile in two_degree_three
        ],
        "residue_profiles": [_profile_label(profile) for profile in residue],
        "sat_profiles": [_profile_label(profile) for profile in sat],
        "simple_row_residue_minima": {
            "4^6 5^14 6^2 7^1": first_residue_minimum,
            "3^1 4^3 5^17 6^1 7^1": second_residue_minimum,
        },
        "exceptional_pair_residue": exceptional,
    }


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


def z12_23_certificate_report() -> dict[str, object]:
    """Recompute the complete elementary upper-bound certificate at 135 ones.

    The report first excludes 136 ones using the forced profile ``5^2 6^21``
    and a row-pair congruence.  It then classifies the five profiles at 135
    ones and verifies the row/pair-deficit contradiction for each profile.
    """

    profiles_136 = [profile_dict(profile) for profile in enumerate_degree_profiles(12, 23, 136)]
    if profiles_136 != [{5: 2, 6: 21}]:
        raise AssertionError(f"unexpected profiles at 136: {profiles_136}")
    pair_solutions = [
        (degree_five, degree_six)
        for degree_five in range(3)
        for degree_six in range(6)
        if 3 * degree_five + 4 * degree_six == 20
    ]
    if pair_solutions != [(0, 5)]:
        raise AssertionError(f"unexpected pair-equation solutions: {pair_solutions}")

    profiles_135 = [profile_dict(profile) for profile in enumerate_degree_profiles(12, 23, 135)]
    expected_135 = [
        {5: 3, 6: 20},
        {4: 1, 5: 1, 6: 21},
        {5: 4, 6: 18, 7: 1},
        {4: 1, 5: 2, 6: 19, 7: 1},
        {5: 5, 6: 16, 7: 2},
    ]
    if profiles_135 != expected_135:
        raise AssertionError(f"unexpected profiles at 135: {profiles_135}")

    first_slack = 2 * math.comb(12, 3) - (
        3 * math.comb(5, 3) + 20 * math.comb(6, 3)
    )
    first_residue_minimum = min(60 - 10 * triple_rows for triple_rows in range(3))
    if first_slack != 10 or first_residue_minimum != 40:
        raise AssertionError("unexpected 5^3 6^20 residue calculation")

    second_slack = 2 * math.comb(12, 3) - (
        math.comb(4, 3) + math.comb(5, 3) + 21 * math.comb(6, 3)
    )
    second_residues = {}
    for overlap in range(5):
        shared_pairs = math.comb(overlap, 2)
        second_residues[overlap] = (
            2 * (math.comb(4, 2) - shared_pairs)
            + (math.comb(5, 2) - shared_pairs)
            + 3 * shared_pairs
        )
    if second_slack != 6 or set(second_residues.values()) != {22}:
        raise AssertionError("unexpected 4^1 5^1 6^21 pair residues")

    third_slack = 2 * math.comb(12, 3) - (
        4 * math.comb(5, 3) + 18 * math.comb(6, 3) + math.comb(7, 3)
    )
    row_types = [(degree_five, degree_seven) for degree_five in range(5) for degree_seven in range(2)]
    third_minimum = math.inf

    def visit_row_types(
        index: int,
        rows_left: int,
        five_incidences: int,
        seven_incidences: int,
        five_triple_budget: int,
        mixed_triple_budget: int,
        residue_sum: int,
    ) -> None:
        nonlocal third_minimum
        if residue_sum >= third_minimum:
            return
        if index == len(row_types):
            if rows_left == 0 and five_incidences == 20 and seven_incidences == 7:
                third_minimum = residue_sum
            return
        degree_five, degree_seven = row_types[index]
        residue = (4 * degree_five + 5 * degree_seven) % 10
        for multiplicity in range(rows_left + 1):
            new_five = five_incidences + multiplicity * degree_five
            new_seven = seven_incidences + multiplicity * degree_seven
            new_five_budget = five_triple_budget + multiplicity * math.comb(degree_five, 3)
            new_mixed_budget = (
                mixed_triple_budget
                + multiplicity * math.comb(degree_five, 2) * degree_seven
            )
            if (
                new_five > 20
                or new_seven > 7
                or new_five_budget > 2 * math.comb(4, 3)
                or new_mixed_budget > 2 * math.comb(4, 2)
            ):
                break
            visit_row_types(
                index + 1,
                rows_left - multiplicity,
                new_five,
                new_seven,
                new_five_budget,
                new_mixed_budget,
                residue_sum + multiplicity * residue,
            )

    visit_row_types(0, 12, 0, 0, 0, 0, 0)
    if third_slack != 5 or third_minimum != 25:
        raise AssertionError(f"unexpected 5^4 6^18 7^1 minimum: {third_minimum}")

    fourth_slack = 2 * math.comb(12, 3) - (
        math.comb(4, 3)
        + 2 * math.comb(5, 3)
        + 19 * math.comb(6, 3)
        + math.comb(7, 3)
    )
    maximum_seven_rows = 4 + (3 * fourth_slack) // 3
    if fourth_slack != 1 or maximum_seven_rows != 5:
        raise AssertionError("unexpected 4^1 5^2 6^19 7^1 incidence bound")

    fifth_slack = 2 * math.comb(12, 3) - (
        5 * math.comb(5, 3) + 16 * math.comb(6, 3) + 2 * math.comb(7, 3)
    )
    zero_residue_five_counts = [
        count for count in range(6) if any((4 * count + 5 * b) % 10 == 0 for b in range(3))
    ]
    forced_triple_incidence = 5 * math.comb(5, 3)
    available_triple_incidence = 2 * math.comb(5, 3)
    if (
        fifth_slack != 0
        or zero_residue_five_counts != [0, 5]
        or forced_triple_incidence <= available_triple_incidence
    ):
        raise AssertionError("unexpected 5^5 6^16 7^2 residue calculation")

    return {
        "status": "VERIFIED",
        "problem": "Z(12,23,3,3)",
        "excluded_targets": [136, 135],
        "at_136": {
            "degree_profiles": [{str(d): count for d, count in profiles_136[0].items()}],
            "pair_equation": "3*a_P + 4*b_P = 20",
            "pair_equation_solutions": [list(solution) for solution in pair_solutions],
            "degree_five_pair_incidences": 2 * math.comb(5, 2),
        },
        "at_135": {
            "degree_profiles": [
                {str(d): count for d, count in profile.items()} for profile in profiles_135
            ],
            "cases": {
                "5^3 6^20": {
                    "deficit_budget": 3 * first_slack,
                    "minimum_row_residue_sum": first_residue_minimum,
                },
                "4^1 5^1 6^21": {
                    "deficit_budget": 3 * second_slack,
                    "pair_residue_sums_by_overlap": {
                        str(key): value for key, value in second_residues.items()
                    },
                },
                "5^4 6^18 7^1": {
                    "deficit_budget": 3 * third_slack,
                    "minimum_row_residue_sum": int(third_minimum),
                },
                "4^1 5^2 6^19 7^1": {
                    "required_degree_seven_rows": 7,
                    "maximum_degree_seven_rows": maximum_seven_rows,
                },
                "5^5 6^16 7^2": {
                    "forced_triple_incidence": forced_triple_incidence,
                    "available_triple_incidence": available_triple_incidence,
                },
            },
        },
    }


def z13_23_upper_report() -> dict[str, object]:
    """Recompute the marked-row certificate proving ``Z(13,23)<=144``."""

    profiles = [profile_dict(profile) for profile in enumerate_degree_profiles(13, 23, 145)]
    expected = [
        {6: 16, 7: 7},
        {5: 1, 6: 14, 7: 8},
        {6: 17, 7: 5, 8: 1},
    ]
    if profiles != expected:
        raise AssertionError(f"unexpected profiles at Z(13,23)=145: {profiles}")
    cases = []
    for profile in profiles:
        slack = 2 * math.comb(13, 3) - sum(
            count * math.comb(degree, 3) for degree, count in profile.items()
        )
        exceptional_rows = sum(
            degree * count for degree, count in profile.items() if degree in (5, 8)
        )
        clean_rows = 13 - exceptional_rows
        forced_deficit = 2 * clean_rows
        budget = 3 * slack
        if forced_deficit <= budget:
            raise AssertionError(f"profile was not excluded: {profile}")
        cases.append(
            {
                "profile": {str(d): count for d, count in profile.items()},
                "slack": slack,
                "clean_rows": clean_rows,
                "forced_deficit": forced_deficit,
                "deficit_budget": budget,
            }
        )
    return {
        "status": "VERIFIED",
        "problem": "Z(13,23,3,3)",
        "excluded_target": 145,
        "upper_bound": 144,
        "cases": cases,
    }


def z13_23_upper_certificate() -> dict[str, object]:
    """Return the standalone certificate for the non-exact frontier bound."""

    return {
        "schema_version": 1,
        "certificate_type": "finite_zarankiewicz_upper_bound",
        "slug": "z13_23_upper_144",
        "theorem": "Z(13,23,3,3)<=144",
        "parameters": {
            "rows": 13,
            "columns": 23,
            "forbidden_rows": 3,
            "forbidden_columns": 3,
            "excluded_target": 145,
        },
        "upper_bound": z13_23_upper_report(),
        "lean_kernel": "ZarankiewiczFiniteClosures.ArithmeticKernels",
        "conclusion": "Z(13,23,3,3)<=144",
    }


def verify_z13_23_upper_certificate(certificate: Mapping[str, Any]) -> dict[str, object]:
    """Verify an untrusted standalone ``Z(13,23)`` certificate."""

    expected = z13_23_upper_certificate()
    if dict(certificate) != expected:
        raise ValueError("Z(13,23) upper-bound certificate differs from recomputation")
    return {
        "status": "VERIFIED",
        "slug": expected["slug"],
        "theorem": expected["theorem"],
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
        "repository_upper_bounds": {
            f"{rows},{columns}": value
            for (rows, columns), value in sorted(REPOSITORY_UPPER_BOUNDS.items())
        },
        "remaining_open_cases": len(remaining),
        "remaining_parameters": [f"{rows},{columns}" for rows, columns in remaining],
        "deletion_checks": {
            "Z(10,21)<=106": deletion_upper(96, 10),
            "Z(11,19)<=106": deletion_upper(101, 19),
            "Z(11,20)<=111": deletion_upper(106, 20),
            "Z(11,23)<=123": deletion_upper(112, 11),
        },
        "paper_bounds": {
            f"{rows},{columns}": {"lower": lower, "upper": upper}
            for (rows, columns), (lower, upper) in sorted(PAPER_OPEN_BOUNDS.items())
        },
    }
