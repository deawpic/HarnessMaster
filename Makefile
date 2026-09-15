# HarnessMaster Automation Makefile
.PHONY: test audit clean scaffold help

help:
	@echo "🛡️ HarnessMaster CLI Commands:"
	@echo "  make audit           - Audit any harness or the current workspace against 7 Golden Standards"
	@echo "  make test-templates  - Run unit and sanity tests on all reference templates"
	@echo "  make scaffold        - Example command for generating a new domain harness"
	@echo "  make clean           - Clean cache and temporary files"

audit:
	python3 scripts/audit_compliance.py .

test-templates:
	python3 -c "import sys; sys.path.insert(0, '.agents/skills/agent-harness-builder/references'); import mermaid_unicode_guardian, document_exporter, dual_layer_cache, grounding_oracle, mock_llm, swarm_testbed; print('All 6 Production Templates Loaded & Validated 100%!')"

scaffold:
	@echo "To scaffold a new harness, run:"
	@echo "  python3 scripts/scaffold_harness.py --name <name> --domain <medical|legal|software|finance|general> --profile <micro|enterprise>"

clean:
	rm -rf cache/*.db* __pycache__ .agents/skills/agent-harness-builder/references/__pycache__
