PYTHON ?= python3
export PYTHONPATH := src

.PHONY: all analysis audit candidate-certificate certificate checksums extended models new-bounds test verify witness

all: verify

test:
	$(PYTHON) -m unittest discover -s tests -v

witness:
	$(PYTHON) scripts/verify_witness.py
	$(PYTHON) scripts/verify_witness_independent.py

certificate:
	$(PYTHON) scripts/check_proof_certificate.py
	$(PYTHON) scripts/check_case_certificates.py --check
	$(PYTHON) scripts/check_frontier_certificate.py --check

# Optional heavyweight gate. It becomes available only after every Z(10,23)
# proof asset and the final SAT manifest have been harvested into the clone.
candidate-certificate:
	$(PYTHON) scripts/build_z10_23_sat_manifest.py --check

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
