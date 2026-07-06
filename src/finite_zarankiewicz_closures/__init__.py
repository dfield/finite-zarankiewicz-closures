"""Auditable utilities for six exact finite Zarankiewicz results.

The package intentionally uses only the Python standard library.  Its role is
verification, not discovery: the mathematical argument is written first in
``docs/PROOF.md`` and ``docs/EXTENDED_RESULTS.md``, and each module checks a
clearly identified part of those arguments.
"""

from .certificate import CertificateError, penalty, verify_certificate
from .case_certificates import CaseCertificateError, verify_case_certificate
from .matrix import MatrixCheck, read_boolean_csv, verify_by_row_triples

__all__ = [
    "CertificateError",
    "CaseCertificateError",
    "MatrixCheck",
    "penalty",
    "read_boolean_csv",
    "verify_by_row_triples",
    "verify_certificate",
    "verify_case_certificate",
]
