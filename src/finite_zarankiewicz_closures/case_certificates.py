"""Uniform, case-specific certificates for the eight established exact values.

Each stored JSON certificate is treated as untrusted.  This module rebuilds
the witness invariants and the appropriate upper-bound certificate, then
requires byte-level semantic equality with the supplied object.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from .certificate import verify_certificate
from .extended import (
    deletion_upper,
    z10_22_certificate_report,
    z12_23_certificate_report,
)
from .matrix import read_boolean_csv, verify_by_row_triples


class CaseCertificateError(ValueError):
    """Raised when a case certificate differs from recomputed evidence."""


@dataclass(frozen=True)
class CaseSpec:
    """Static parameters for one established result."""

    slug: str
    rows: int
    columns: int
    value: int
    witness_file: str
    publication_status: str = "established"

    @property
    def theorem(self) -> str:
        """Return the conventional theorem label."""

        return f"Z({self.rows},{self.columns},3,3)={self.value}"


ALL_CASE_SPECS = (
    CaseSpec("z9_23_103", 9, 23, 103, "data/z9_23_103_matrix.csv"),
    CaseSpec("z10_21_106", 10, 21, 106, "data/z10_21_106_matrix.csv"),
    CaseSpec("z10_22_110", 10, 22, 110, "data/z10_22_110_matrix.csv"),
    CaseSpec("z10_23_112", 10, 23, 112, "data/z10_23_112_matrix.csv"),
    CaseSpec("z11_19_106", 11, 19, 106, "data/z11_19_106_matrix.csv"),
    CaseSpec("z11_20_111", 11, 20, 111, "data/z11_20_111_matrix.csv"),
    CaseSpec("z11_23_123", 11, 23, 123, "data/z11_23_123_matrix.csv"),
    CaseSpec("z12_23_134", 12, 23, 134, "data/z12_23_134_matrix.csv"),
)
ESTABLISHED_CASE_SPECS = ALL_CASE_SPECS
CANDIDATE_CASE_SPECS: tuple[CaseSpec, ...] = ()
# Backwards-compatible public name used by the publication certificate gate.
CASE_SPECS = ESTABLISHED_CASE_SPECS
CASE_BY_SLUG = {case.slug: case for case in CASE_SPECS}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _witness_certificate(root: Path, case: CaseSpec) -> dict[str, Any]:
    path = root / case.witness_file
    report = verify_by_row_triples(
        read_boolean_csv(path),
        expected_rows=case.rows,
        expected_columns=case.columns,
        expected_ones=case.value,
        raw_bytes=path.read_bytes(),
    )
    if not report.valid:
        raise CaseCertificateError(f"invalid witness for {case.slug}")
    return {"file": case.witness_file, **report.as_dict()}


@lru_cache(maxsize=None)
def _z10_23_upper_report(root_text: str) -> dict[str, Any]:
    """Deeply verify and cache the complete 113-one certificate family."""

    from .sat_certificate import load_and_verify_z10_23_sat_manifest

    return load_and_verify_z10_23_sat_manifest(Path(root_text))


def _upper_certificate(root: Path, case: CaseSpec) -> dict[str, Any]:
    if case.slug == "z9_23_103":
        path = root / "certificates" / "degree_deficit.json"
        detailed = json.loads(path.read_text(encoding="utf-8"))
        report = verify_certificate(detailed)
        return {
            "method": "marked_row_deficit",
            "excluded_target": 104,
            "detailed_certificate": "certificates/degree_deficit.json",
            "detailed_certificate_sha256": _sha256(path),
            "profiles_enumerated": report["profiles_enumerated"],
            "terminal_residue_lower_bounds": [
                item["residue_lower_bound"] for item in report["cases"]
            ],
            "lean_kernel": "ZarankiewiczZ923.ArithmeticKernel",
        }
    if case.slug == "z10_21_106":
        bound = deletion_upper(96, 10)
        if bound != 106:
            raise CaseCertificateError("unexpected Z(10,21) deletion bound")
        return {
            "method": "vertex_deletion",
            "excluded_target": 107,
            "steps": [
                {
                    "source": "Z(9,21,3,3)<=96",
                    "source_upper_bound": 96,
                    "larger_part": 10,
                    "formula_numerator": 960,
                    "formula_denominator": 9,
                    "recomputed_upper_bound": bound,
                }
            ],
            "lean_kernel": "ZarankiewiczFiniteClosures.ArithmeticKernels",
        }
    if case.slug == "z10_22_110":
        report = z10_22_certificate_report()
        return {
            "method": "pair_deficit_enumeration",
            "excluded_target": 111,
            "detailed_report": report,
            "lean_kernel": "ZarankiewiczFiniteClosures.ArithmeticKernels",
            "computer_assisted_component": (
                "case-B and case-C row-symmetry orbit enumeration"
            ),
        }
    if case.slug == "z10_23_112":
        manifest = root / "certificates" / "z10_23_sat.json"
        report = _z10_23_upper_report(str(root.resolve()))
        if report.get("status") != "VERIFIED" or report.get("sat_profiles") != 13:
            raise CaseCertificateError("incomplete Z(10,23) certificate family")
        return {
            "method": "arithmetic_reduction_and_replayable_certificates",
            "excluded_target": 113,
            "master_manifest": "certificates/z10_23_sat.json",
            "master_manifest_sha256": _sha256(manifest),
            "detailed_report": report,
            "computer_assisted_component": (
                "eleven DRAT/LRAT profile refutations and two exact SCIP/VIPR "
                "orbit-cover refutations"
            ),
            "lean_kernel": "Zarankiewicz.Z10_23.ArithmeticFrontEnd",
        }
    if case.slug == "z11_19_106":
        bound = deletion_upper(101, 19)
        if bound != 106:
            raise CaseCertificateError("unexpected Z(11,19) deletion bound")
        return {
            "method": "vertex_deletion",
            "excluded_target": 107,
            "steps": [
                {
                    "source": "Z(11,18,3,3)<=101",
                    "source_upper_bound": 101,
                    "larger_part": 19,
                    "formula_numerator": 1919,
                    "formula_denominator": 18,
                    "recomputed_upper_bound": bound,
                }
            ],
            "lean_kernel": "ZarankiewiczFiniteClosures.ArithmeticKernels",
        }
    if case.slug == "z11_20_111":
        first = deletion_upper(101, 19)
        second = deletion_upper(first, 20)
        if (first, second) != (106, 111):
            raise CaseCertificateError("unexpected Z(11,20) deletion chain")
        return {
            "method": "vertex_deletion_chain",
            "excluded_target": 112,
            "steps": [
                {
                    "source": "Z(11,18,3,3)<=101",
                    "source_upper_bound": 101,
                    "larger_part": 19,
                    "formula_numerator": 1919,
                    "formula_denominator": 18,
                    "recomputed_upper_bound": first,
                },
                {
                    "source": "Z(11,19,3,3)<=106",
                    "source_upper_bound": first,
                    "larger_part": 20,
                    "formula_numerator": 2120,
                    "formula_denominator": 19,
                    "recomputed_upper_bound": second,
                },
            ],
            "lean_kernel": "ZarankiewiczFiniteClosures.ArithmeticKernels",
        }
    if case.slug == "z11_23_123":
        # If a K_3,3-free 11 x 23 matrix had 124 ones, one of its eleven
        # rows would have degree at most floor(124/11)=11.  Deleting that row
        # would leave at least 113 ones in a 10 x 23 matrix, contradicting the
        # independently certified bound Z(10,23)<=112.
        excluded_target = 124
        deleted_degree = excluded_target // 11
        remaining = excluded_target - deleted_degree
        if (deleted_degree, remaining) != (11, 113):
            raise CaseCertificateError("unexpected Z(11,23) deletion arithmetic")
        z10_report = _z10_23_upper_report(str(root.resolve()))
        if z10_report.get("status") != "VERIFIED":
            raise CaseCertificateError("Z(11,23) depends on an unverified Z(10,23) bound")
        return {
            "method": "minimum_row_deletion",
            "excluded_target": excluded_target,
            "steps": [
                {
                    "source": "Z(10,23,3,3)<=112",
                    "source_upper_bound": 112,
                    "larger_row_part": 11,
                    "minimum_deleted_degree_at_most": deleted_degree,
                    "remaining_ones_at_least": remaining,
                    "contradictory_target": 113,
                }
            ],
            "source_certificate": "certificates/z10_23_112.json",
            "source_manifest": "certificates/z10_23_sat.json",
            "source_manifest_sha256": _sha256(
                root / "certificates" / "z10_23_sat.json"
            ),
            "lean_kernel": "Zarankiewicz.Z11_23.Deletion",
        }
    if case.slug == "z12_23_134":
        return {
            "method": "two_stage_row_pair_deficit",
            "excluded_target": 135,
            "detailed_report": z12_23_certificate_report(),
            "lean_kernel": "ZarankiewiczFiniteClosures.ArithmeticKernels",
            "computer_assisted_component": (
                "finite row-type enumeration for profile 5^4 6^18 7^1"
            ),
        }
    raise CaseCertificateError(f"unknown case: {case.slug}")


@lru_cache(maxsize=None)
def _expected_json(root_text: str, slug: str) -> str:
    root = Path(root_text)
    case = CASE_BY_SLUG[slug]
    certificate = {
        "schema_version": 1,
        "certificate_type": "exact_finite_zarankiewicz_case",
        "slug": case.slug,
        "theorem": case.theorem,
        "parameters": {
            "rows": case.rows,
            "columns": case.columns,
            "forbidden_rows": 3,
            "forbidden_columns": 3,
            "exact_value": case.value,
        },
        "lower_bound": _witness_certificate(root, case),
        "upper_bound": _upper_certificate(root, case),
        "conclusion": case.theorem,
    }
    return json.dumps(certificate, indent=2, sort_keys=True) + "\n"


def expected_case_certificate(root: Path, slug: str) -> dict[str, Any]:
    """Recompute and return the complete certificate for ``slug``."""

    if slug not in CASE_BY_SLUG:
        raise CaseCertificateError(f"unknown case slug: {slug}")
    return json.loads(_expected_json(str(root.resolve()), slug))


def verify_case_certificate(certificate: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Verify one untrusted case certificate against recomputed evidence."""

    slug = certificate.get("slug")
    if not isinstance(slug, str) or slug not in CASE_BY_SLUG:
        raise CaseCertificateError("certificate has an unknown slug")
    observed = copy.deepcopy(dict(certificate))
    expected = expected_case_certificate(root, slug)
    if observed != expected:
        raise CaseCertificateError(f"certificate fields do not match recomputation: {slug}")
    return {
        "status": "VERIFIED",
        "slug": slug,
        "theorem": expected["theorem"],
        "method": expected["upper_bound"]["method"],
        "witness_sha256": expected["lower_bound"]["sha256"],
    }


def rendered_case_certificates(root: Path) -> dict[str, str]:
    """Return deterministic JSON text for every case certificate."""

    return {
        case.slug: _expected_json(str(root.resolve()), case.slug)
        for case in CASE_SPECS
    }
