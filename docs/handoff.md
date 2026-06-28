# Session Handoff — Next Feature: Module 2 (Risk & Sensitivity)

## Current State

- **Branch**: `dev` at `4fbbcca` — clean, all checks passing (34 tests, ruff, mypy)
- **Plotting utils**: `src/utils/plotting.py` committed, squashed, PR #4 merged
- **AGENTS.md**: Phase D handoff guardrail added (`4fbbcca`)
- **Feature branches**: all cleaned up

## Next Up: Module 2 — Risk & Sensitivity (Duration & Convexity)

Per MRD Execution Protocol, Module 2 must come next.

### Scope

| Component | File | Description |
|-----------|------|-------------|
| Macaulay Duration | `src/risk/duration.py` | Time-weighted avg of cash flows |
| Modified Duration | `src/risk/duration.py` | ModD = MacD / (1 + y/m) |
| Convexity | `src/risk/convexity.py` | Second derivative of price wrt yield |
| Shock Simulation | `src/risk/shock.py` | Taylor expansion: ΔP ≈ -ModD·P·Δy + ½·Cx·P·(Δy)² |
| Tests | `tests/test_risk/` | pytest with edge cases |
| Notebook | `notebooks/02-risk-sensitivity.ipynb` | Textbook cross-check |

### Key Dependencies

- `src/instruments/bond.py` — Bond dataclass
- `src/instruments/pricing.py` — `price()` function
- `src/utils/plotting.py` — plotting helpers for visualization

### Existing Scaffolds

- `src/risk/__init__.py` — empty
- `tests/test_risk/__init__.py` — empty

### Standard Workflow

```
feat/risk-duration-convexity ← PR ← squash-merge → dev
```

1. Human injects specs + references → Agent produces `docs/implementation_plan.md`
2. Human reviews and approves plan
3. Agent writes tests (TDD: see them fail first)
4. Agent implements → verifies (ruff, mypy, pytest)
5. Agent writes `docs/walkthrough.md`
6. Human reviews → Human squash-merges via PR
7. Session flushed
