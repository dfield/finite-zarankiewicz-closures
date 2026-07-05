PYTHON ?= python3
export PYTHONPATH := src

.PHONY: all analysis audit certificate checksums extended models test verify witness

all: verify

test:
	$(PYTHON) -m unittest discover -s tests -v

witness:
	$(PYTHON) scripts/verify_witness.py
	$(PYTHON) scripts/verify_witness_independent.py

certificate:
	$(PYTHON) scripts/check_proof_certificate.py

extended:
	$(PYTHON) scripts/check_extended_results.py --check
	$(PYTHON) scripts/verify_extended_witnesses_independent.py

models:
	$(PYTHON) scripts/generate_models.py --check

analysis:
	$(PYTHON) scripts/analyze_boundary.py --check

checksums:
	$(PYTHON) scripts/build_checksums.py --check

audit:
	$(PYTHON) scripts/audit_repository.py

verify: test witness certificate extended models analysis checksums audit
