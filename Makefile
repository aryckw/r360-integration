# r360-integration gate. This Makefile runs INSIDE the container image.
# From the Windows host, do not invoke it directly:
#     docker compose -f compose/docker-compose.yml run --rm gate    (or: .\gate.ps1)

.PHONY: help gate stack-verify stack-lock contracts-verify gen gen-check fmt fmt-write \
        lint types test trace deps deps-write clean

PROTO_DIR := contracts/proto
PY_OUT    := generated/python
PROTOS    := $(shell find $(PROTO_DIR) -name '*.proto' | sort)
WORKSPACE ?= /workspace

export PYTHONPATH := $(PY_OUT):$(CURDIR)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── THE GATE ─────────────────────────────────────────────────────────────────
# The composed stack is already up when this runs: compose brings up the broker, the
# database, the object store and both services, and waits for them to be healthy, before
# this container starts. A green gate here means those five things worked together.
gate: contracts-verify stack-verify fmt lint types gen-check test trace deps
	@echo ""
	@echo "  r360-integration GATE PASSED"
	@echo ""

# ── stack composition ────────────────────────────────────────────────────────
stack-verify:  ## REQ-INT-001/004: pinned revisions that agree about the contract
	python tools/stack_lock.py verify --workspace $(WORKSPACE)

stack-lock:  ## record the current sibling revisions as a proven combination
	python tools/stack_lock.py update --workspace $(WORKSPACE)

contracts-verify:  ## the vendored proto tree matches contracts.lock
	python tools/contracts_vendor.py verify

gen:  ## regenerate Python bindings from the vendored contracts
	@rm -rf $(PY_OUT)
	@mkdir -p $(PY_OUT)
	python -m grpc_tools.protoc -I$(PROTO_DIR) \
	       --python_out=$(PY_OUT) --pyi_out=$(PY_OUT) --grpc_python_out=$(PY_OUT) $(PROTOS)
	@echo "generated $(words $(PROTOS)) proto files"

gen-check: gen  ## regeneration must leave a clean git diff
	@git diff --exit-code -- $(PY_OUT) \
	  || (echo "FAIL: generated bindings are stale; commit the result of 'make gen'" && exit 1)
	@test -z "$$(git ls-files --others --exclude-standard -- $(PY_OUT))" || ( \
	    echo "FAIL: generation produced untracked bindings; commit them:"; \
	    git ls-files --others --exclude-standard -- $(PY_OUT); \
	    exit 1)
	@echo "generation is deterministic and committed"

# ── static checks ────────────────────────────────────────────────────────────
fmt:
	ruff format --check tests tools

fmt-write:
	ruff format tests tools

lint:
	ruff check tests tools

types:
	mypy --strict tools

# ── tests ────────────────────────────────────────────────────────────────────
test:  ## cross-repository acceptance against the composed stack
	pytest -q tests

trace:  ## every active requirement has at least one referencing test
	python tools/trace.py --tests tests

deps:
	python tools/license_inventory.py --check

deps-write:
	python tools/license_inventory.py

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
