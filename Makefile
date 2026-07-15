PYTHON ?= python3
export PYTHONPATH := src

.PHONY: all analysis audit candidate-certificate certificate checksums extended models new-bounds test verify witness z10-23-certificate

all: verify

test:
	$(PYTHON) -m unittest discover -s tests -v

witness:
	$(PYTHON) scripts/verify_witness.py
	$(PYTHON) scripts/verify_witness_independent.py

certificate:
	$(PYTHON) scripts/check_proof_certificate.py
	$(PYTHON) scripts/build_z10_23_sat_manifest.py --check
	$(PYTHON) scripts/check_case_certificates.py --check
	$(PYTHON) scripts/check_frontier_certificate.py --check

# Self-contained integrity gate: regenerates both VIPR orbit covers and every
# OPB leaf, but does not download the 25 GB external-checker release assets.
z10-23-certificate:
	$(PYTHON) scripts/build_z10_23_sat_manifest.py --check
	$(PYTHON) scripts/check_z10_23_certificate.py

# Backwards-compatible name from the pre-publication candidate phase.
candidate-certificate: z10-23-certificate

extended:
	$(PYTHON) scripts/check_extended_results.py --check
	$(PYTHON) scripts/verify_extended_witnesses_independent.py

new-bounds:
	$(PYTHON) scripts/check_new_bounds.py --check

models:
	$(PYTHON) scripts/generate_models.py --check

analysis:
	$(PYTHON) scripts/analyze_boundary.py --check

checksums:
	$(PYTHON) scripts/build_checksums.py --check

audit:
	$(PYTHON) scripts/audit_repository.py

verify: test witness certificate extended new-bounds models analysis checksums audit
