# Bond Modelling Engine: Agent Rules & Workflow

This file defines the official project-scoped rules for all Antigravity agents operating in this workspace. These constraints are consolidated from `docs/AGENTS.md` and `docs/development_workflow.md`.

## 1. Python Execution & Virtual Environment (uv)
- The agent sandbox does not automatically source the virtual environment. 
- **NEVER** run bare `python <script.py>` or `jupyter` commands. 
- **ALWAYS** prefix Python executions with `uv run` (e.g., `uv run python <script.py>`, `uv run pytest`) to ensure dependencies are resolved correctly.
- Do not suggest or use `pip` or `poetry`.

## 2. Mandatory Pre-Commit Verification
Before ANY commit (especially before pushing or opening a PR), the Agent MUST run the following exact commands in the local sandbox and confirm all pass:
```bash
uv run ruff check .
uv run ruff format . --check
uv run mypy src/
PYTHONPATH=. uv run pytest -v --tb=short
```
If any command fails, fix the issue before committing. Do not skip or defer any of these checks.

## 3. Jupyter Notebook Verification Standard
When a module is completed and requires "notebook verification", you must execute the notebooks programmatically and save the outputs in-place.
- Use the exact command: `uv run jupyter nbconvert --to notebook --execute --inplace notebooks/<notebook_name>.ipynb`
- When executing multiple notebooks, use a bash loop to execute them sequentially and check for errors, rather than a glob which will halt prematurely on the first failure.

## 4. Consolidated Output Regeneration (Phase C)
After a feature update that modifies any source notebook or Python source, the consolidated output must be rebuilt before merging:
1. Execute all source notebooks.
2. Merge into consolidated notebook: `uv run nbmerge -o output/consolidated.ipynb notebooks/*.ipynb`
3. Execute consolidated notebook: `uv run jupyter nbconvert --to notebook --execute --inplace output/consolidated.ipynb`
4. Convert to HTML: `uv run jupyter nbconvert --to html output/consolidated.ipynb`
5. Update `docs/project_status.md` (bump date, module status, test counts).
6. Stage the generated outputs and status docs: `git add output/ docs/project_status.md`

## 5. Branch Strategy & Conventional Commits
- **Branch Naming**: Feature branches must be named `feat/<module>-<description>` (e.g., `feat/module2-duration`).
- **Commit Convention**: All commits must follow Conventional Commits format (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- **PR Workflow**: Feature branches must be Pull Requested into `dev` and **squash-merged**.

## 6. Agent Handoff & Safety Rules
- **Human Authorization**: The Agent MUST NOT perform squash-merges, branch deletions, or pushes to `dev`/`main` without explicit step-by-step Human authorization.
- **PR Creation**: When creating PRs via the `gh` CLI, dynamically generate a fresh temporary file for the PR body (e.g., `/tmp/pr_body.md`). DO NOT reference stale scratch artifacts for the `--body-file`.
- **Two-Strike Escape**: If sandbox verification (lint/tests) fails twice, the Agent MUST halt execution, present the exact failing diff and logs, and offer 2-3 logical solutions to the Human. Do not loop endlessly.

## 7. Subagent Architecture
When tackling complex tasks, utilize subagents:
- **`quant_modelling`**: For mathematical validation, fixed-income theory, and test harness design.
- **`python_coder`**: For clean Python 3.10+ typing implementation, `pytest` suites, and sandbox verification.
