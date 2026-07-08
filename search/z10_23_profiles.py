"""Dependency-free profile metadata shared by the Z(10,23) proof tools."""

from __future__ import annotations


ROWS = 10
COLUMNS = 23
TARGET = 113
SAT_PROFILES = (
    "4x2,5x21",
    "4x3,5x19,6x1",
    "4x4,5x17,6x2",
    "4x4,5x18,7x1",
    "4x5,5x15,6x3",
    "4x5,5x16,6x1,7x1",
    "4x6,5x13,6x4",
    "4x7,5x11,6x5",
    "3x1,5x22",
    "3x1,4x1,5x20,6x1",
    "3x1,4x2,5x18,6x2",
    "3x1,4x3,5x16,6x3",
    "3x1,4x4,5x14,6x4",
)


def parse_profile(text: str) -> dict[int, int]:
    """Parse ``degree x multiplicity`` terms and validate the target."""

    counts: dict[int, int] = {}
    for term in text.split(","):
        degree_text, count_text = term.split("x", 1)
        degree, count = int(degree_text), int(count_text)
        if not 0 <= degree <= ROWS or count <= 0 or degree in counts:
            raise ValueError(f"invalid profile term: {term}")
        counts[degree] = count
    if sum(counts.values()) != COLUMNS:
        raise ValueError("profile does not contain 23 columns")
    if sum(degree * count for degree, count in counts.items()) != TARGET:
        raise ValueError("profile does not contain 113 ones")
    return counts


def canonical_profile(text: str) -> str:
    """Return one profile in ascending-degree notation."""

    counts = parse_profile(text)
    return ",".join(f"{degree}x{counts[degree]}" for degree in sorted(counts))


def profile_slug(text: str) -> str:
    """Return the stable filename form of a canonical profile."""

    return canonical_profile(text).replace(",", "_").replace("x", "d")


def ordered_degrees(text: str) -> list[int]:
    """Put rare blocks first while keeping equal degrees contiguous."""

    counts = parse_profile(text)
    groups = sorted(counts.items(), key=lambda item: (item[1], item[0]))
    return [degree for degree, count in groups for _ in range(count)]
