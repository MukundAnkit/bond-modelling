# Developer SOP: Bond Modelling Engine

> Standard Operating Procedure for the Human Developer
> Agent rules are maintained separately in `.agents/AGENTS.md` (auto-loaded by opencode).

---

## 1. Roles & Scopes

Workload is bifurcated between the Human and the AI Agent.

### 1.1 The Human (Architect, Gatekeeper & Reviewer)

- **Context Injection**: Supplying the Agent with precise `@file` or `@symbol` references.
- **Model Stratification**: Selecting appropriate model capability tiers for each task.
- **Plan Gatekeeping**: Reviewing and explicitly approving Implementation Plans (`docs/implementation_plan.md`) before any code is modified.
- **Feature-Level Git Checkpointing**: Creating feature branches `feat/*`, opening PRs, squash-merging verified features into `dev`, and tagging/releasing on `main`.
- **Escalation & Intervention**: Intervening when the automated loop hits a deterministic break (two failed attempts).
- **Session Management**: Terminating and rotating chat sessions between major tasks.

### 1.2 The Agent (Planner & Executor)

The Agent works autonomously within boundaries set by the Human:
- Code analysis, plan generation, sandbox execution, incremental git commits on feature branches, minimal patching, and TDD enforcement.

Refer to `.agents/AGENTS.md` for the full agent rules.

---

## 2. Core Methodology

Every feature or bug fix follows this sequence:

```
[Goal] → [Inspect] → [Simulate] → [Patch Minimally] → [Verify]
```

1. **Goal**: The Human defines the objective.
2. **Inspect**: The Agent analyzes existing code and reports constraints.
3. **Simulate**: The Agent produces `docs/implementation_plan.md` for Human approval.
4. **Patch Minimally**: The Agent implements minimal changes + unit tests.
5. **Verify**: The Agent runs the full suite (ruff, mypy, pytest). Human reviews and merges.

---

## 3. Branch Strategy

```
main ──────────────────────────────────────  (releases only)
  │                          ↑
  └── dev ───────────────────┘             (integration)
        │            ↑
        └── feat/* ──┘                     (feature branches)
```

| Branch | Purpose |
|---|---|
| `main` | Production releases — code enters only from `dev` via merge + tag |
| `dev` | Active development — all features land here, must always pass CI |
| `feat/*` | Short-lived branches for individual units of work (e.g. `feat/module2-duration`) |

---

## 4. Commit Convention — Conventional Commits

Every commit on `dev` and `feat/*` follows:

```
<type>: <short description>
```

| Type | Use Case | Example |
|---|---|---|
| `feat` | New feature | `feat: add Macaulay Duration calculation` |
| `fix` | Bug fix | `fix: YTM solver diverges for zero-coupon bonds` |
| `test` | Adding / fixing tests | `test: cover shock simulation edge cases` |
| `docs` | Documentation | `docs: update project status after Module 2` |
| `refactor` | Code restructuring (no behavior change) | `refactor: extract numerical derivative helper` |
| `chore` | Tooling, config, CI | `chore: add pytest-cov to dev deps` |

---

## 5. PR & Merge Workflow

### Feature branch → `dev`

1. Create feature branch from `dev`.
2. Develop and commit freely on the branch.
3. Push and open a pull request on GitHub (`feat/*` → `dev`).
4. Use the **PR template** (`.github/pull_request_template.md`).
5. Ensure CI passes.
6. **Squash and merge** into `dev`.

### `dev` → `main`

1. Module fully implemented and verified (notebook cross-checks).
2. Open a PR from `dev` → `main`.
3. Run full test suite + notebook verification.
4. Use a **merge commit** (not squash) to preserve module history.
5. Tag the merge: `git tag v1.0.0 && git push origin v1.0.0`.

---

## 6. Pre-Merge Checklist

Before merging any PR:

- [ ] Linting passes: `uv run ruff check .`
- [ ] Format check passes: `uv run ruff format . --check`
- [ ] Type check passes: `uv run mypy src/`
- [ ] All tests pass: `uv run pytest`
- [ ] New functionality has corresponding tests
- [ ] If a module is completed, notebook verification has been run
- [ ] Consolidated output rebuilt (see `.agents/AGENTS.md` section 5)
- [ ] `docs/project_status.md` updated (module progress, test counts, date)
- [ ] (For `dev` → `main` only) Version tag created

---

## 7. Versioning — Semantic Versioning

```
v<major>.<minor>.<patch>
```

| Bump | When | Example |
|---|---|---|
| `major` | Module completed (dev → main) | `v1.0.0` (Module 1), `v2.0.0` (+ Module 2) |
| `minor` | Significant addition within a module | `v1.1.0` (add shock simulation) |
| `patch` | Bug fixes, docs, small tweaks | `v1.0.1` (fix tolerance edge case) |

Tags are created on `main` only.

---

## 8. CI Expectations

GitHub Actions runs on every push and PR to `dev` or `main`:

- **Environment**: Python 3.12, uv-managed
- **Gates**: `ruff check .` → `ruff format . --check` → `mypy src/` → `pytest -v --tb=short`
- **Expectation**: All four must pass. Red CI blocks merge.

---

## 9. Token Hygiene

- **Precise Injections**: Avoid injecting entire repos or folders. Use targeted file references with exact line numbers.
- **Immediate Session Flushing**: After a feature branch is squash-merged, flush the session to reset token accumulation.
- **Two-Strike Escapes**: If the Agent fails verification twice, it will halt and present the error + 2-3 solutions for you to choose from.

---

## 10. Typical Session

```bash
# 1. Start a feature
git checkout dev && git pull
git checkout -b feat/module2-duration

# 2. Develop (Agent handles this)
# Agent: inspect → simulate (implementation_plan.md) → patch → verify

# 3. Review & merge
# Human: review plan → review walkthrough → squash-merge PR
# Human: archive feature artifacts (implemention_plan.md, walkthrough.md)
# Human: flush session
```
