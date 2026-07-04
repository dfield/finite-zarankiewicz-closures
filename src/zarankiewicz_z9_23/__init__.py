"""Auditable utilities for the finite result :math:`Z(9,23,3,3)=103`.

The package intentionally uses only the Python standard library.  Its role is
verification, not discovery: the mathematical argument is written first in
``docs/PROOF.md`` and each module below checks a clearly identified part of it.
"""

from .certificate import CertificateError, penalty, verify_certificate
from .matrix import MatrixCheck, read_boolean_csv, verify_by_row_triples

__all__ = [
    "CertificateError",
    "MatrixCheck",
    "penalty",
    "read_boolean_csv",
    "verify_by_row_triples",
    "verify_certificate",
]
