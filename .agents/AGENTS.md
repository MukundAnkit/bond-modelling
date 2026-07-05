# Bond Modelling Engine: Agent Rules & Workflow

This file defines the official project-scoped rules for all agents operating in this workspace. These rules are auto-loaded at session start via `opencode.json`. You MUST follow them for every task.

## 1. Python Execution & Virtual Environment (uv)
- The agent sandbox does not automatically source the virtual environment.
- **NEVER** run bare `python <script.py>` or `jupyter` commands.
- **ALWAYS** prefix Python executions with `uv run` (e.g., `uv run python <script.py>`, `uv run pytest`) to ensure dependencies are resolved correctly.
- Do not suggest or use `pip` or `poetry`.

## 2. Core Methodology: The 5-Step Loop
Every feature or bug fix MUST follow this exact sequence:

1. **[Goal]**: The Human defines the objective.
2. **[Inspect]**: Analyze existing code/context and report missing context, ambiguities, or design constraints.
3. **[Simulate]**: Output a detailed `docs/implementation_plan.md` (no implementation code allowed yet). The Human must review and approve the plan before proceeding.
4. **[Patch Minimally]**: Implement the minimal changes and write corresponding unit tests.
5. **[Verify]**: Run the full verification suite (see section 3). The Human reviews the walkthrough and merges.

**Never skip to code without an approved plan.**

## 3. Mandatory Pre-Commit Verification
Before ANY commit (especially before pushing or opening a PR), run these exact commands and confirm all pass:

```bash
uv run ruff check .
uv run ruff format . --check
uv run mypy src/
PYTHONPATH=. uv run pytest -v --tb=short
```

If any command fails, fix the issue before committing. Do not skip or defer any of these checks.

### Deterministic Break (Two-Strike Rule)
If verification fails **twice**, halt execution, present the exact failing diff and logs, and offer 2-3 logical solutions to the Human. Do not loop endlessly.

## 4. Jupyter Notebook Verification Standard
When a module is completed and requires "notebook verification", execute the notebooks programmatically and save the outputs in-place:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/<notebook_name>.ipynb
```

When executing multiple notebooks, use a bash loop to run them sequentially and check for errors. Do not use a glob that halts on first failure.

## 5. Consolidated Output Regeneration & Status Update (Phase C)
After a feature update that modifies any source notebook or Python source, rebuild the consolidated output and update status docs before merging into `dev`:

1. Execute all source notebooks.
2. Merge into consolidated notebook: `uv run nbmerge -o output/consolidated.ipynb notebooks/*.ipynb`
3. Execute consolidated notebook: `uv run jupyter nbconvert --to notebook --execute --inplace output/consolidated.ipynb`
4. Convert to HTML: `uv run jupyter nbconvert --to html output/consolidated.ipynb`
5. **CRITICAL Blocker**: Update `docs/project_status.md` (bump date, module status, test counts). **DO NOT OPEN A PR until this file is confirmed updated.**
6. Stage the generated files: `git add output/consolidated.ipynb output/consolidated.html docs/project_status.md`

Perform this during **Phase C** after the verification suite passes and before committing.

## 6. Standard Workflow Execution Phases

### Phase A: Architecture (Human & Reasoning Agent)
1. Human injects relevant specifications and source files.
2. Execute [Inspect] and [Simulate] to produce `docs/implementation_plan.md`.
3. Human reviews and approves the plan.

### Phase B: Test Generation (Agent in Sandbox)
1. Generate tests in the `tests/` directory.
2. Run `uv run pytest` to verify tests fail (TDD enforcement).

### Phase C: Implementation & Verification (Agent in Sandbox)
1. Implement business logic to pass tests.
2. Run the **full mandatory pre-commit verification** (see section 3). All must pass.
3. Rebuild consolidated output and update `docs/project_status.md` (see section 5).
4. Commit passing, well-formatted, fully verified code to the local feature branch.
5. Write `docs/walkthrough.md` summarizing changes and test runs.

### Phase D: Review & Git Checkpoint (Human & Agent)

> **Agent Handoff Rule**: When Phase D is reached, list the remaining steps and explicitly ask the Human which steps to delegate. Do NOT perform squash-merges, branch deletions, or pushes to `dev`/`main` without explicit step-by-step Human authorization.

1. Human reviews the walkthrough, the diff, and the implementation-level commits.
2. Human runs final local checks if desired.
3. Human removes feature artifacts (`docs/implementation_plan.md`, `docs/walkthrough.md`) and archives any completed roadmap docs.
4. **PR Creation**: When creating PRs via `gh`, dynamically generate a fresh temporary file for the PR body. Do NOT reference stale scratch artifacts.
5. **CI Auto-Remediation**: After opening a PR, if the CI pipeline fails, you MUST autonomously fetch the CI logs using the `gh pr checks` or `gh run view` commands and implement the necessary fixes until the CI is green. Do not wait for the Human to instruct you to fix CI failures.
6. Human performs the final checkpoint (squash-merge into `dev`).
7. Human flushes the context window for the next session.

## 7. Branch Strategy & Conventional Commits
- **Branch Naming**: Feature branches must be named `feat/<module>-<description>` (e.g., `feat/module2-duration`).
- **Commit Convention**: All commits must follow Conventional Commits format (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- **PR Workflow**: Feature branches must be Pull Requested into `dev` and **squash-merged**.

## 8. Proactive Command Permissions
At the start of a session (or before invoking autonomous subagents), proactively use the permission tool to request session-wide execution permissions for core workflow prefixes: `uv`, `git`, and `gh`. This eliminates redundant approval prompts during high-autonomy execution phases.

## 9. Subagent Architecture
When tackling complex tasks, you may spawn specialized subagents:

- **`quant_modelling`**: For mathematical validation, fixed-income theory, and test harness design. Use during Phase A/B.
- **`python_coder`**: For clean Python 3.10+ typing implementation, `pytest` suites, and sandbox verification. Use during Phase C.

## 10. Strict Coding Standards
- **Type Hinting**: Strict Python 3.10+ type hints are mandatory for all function signatures and complex variables. Use mypy-compatible syntax.
- **Docstrings**: All functions, classes, and modules must use standard NumPy-style docstrings.
- **Testing**: All features require corresponding unit tests in `tests/` using `pytest`. Edge cases must be explicitly tested.
- **Minimal Patching**: Touch the absolute minimum number of lines required. No opportunistic refactoring unless requested.
- **TDD Enforcement**: Write pytest harnesses and see them fail before implementing business logic.
