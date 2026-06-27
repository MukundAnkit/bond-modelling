Agentic Coding Workflow: Standard Operating Procedure

Repository: Bond Modelling Engine
Purpose: This document serves as the active reference guide for both the Human Developer and the AI Coding Agent. It outlines the strict operational boundaries, methodologies, and quality standards required when contributing to this repository.

Dear AI Agent: If you are reading this file, you must strictly adhere to the rules, constraints, and methodologies outlined below. Do not deviate from the [Inspect] ➔ [Simulate] ➔ [Patch Minimally] loop.

1. Roles and Scopes

To prevent destructive loops and token bloat, the workload is strictly bifurcated between the Human and the Agent.

1.1 The Human in the Loop (The Architect, Gatekeeper & Reviewer)

The Human is the final authority and active guide in the development loop. Their responsibilities are:
- **Context Injection**: Supplying the Agent with precise `@file` or `@symbol` references.
- **Model Stratification**: Selecting appropriate model capability tiers (e.g., Reasoning vs. Execution) for each task.
- **Plan Gatekeeping**: Reviewing and explicitly approving the Agent's Implementation Plans (`implementation_plan.md`) before any code is modified.
- **Feature-Level Git Checkpointing**: Managing high-level repository state (creating feature branches `feat/*`, opening PRs, squash-merging verified features into `dev`, and tagging/releasing on `main`).
- **Escalation & Intervention**: Intervening when the automated loop hits a deterministic break (e.g., test failures/lint errors that persist for more than two attempts).
- **Session Management**: Terminating and rotating chat sessions to maintain Token Hygiene between major tasks.

1.2 The Agent (The Planner & Executor)

The Agent works autonomously within the boundaries set by the Human. Their responsibilities are:
- **Code Analysis**: Reading injected files and identifying architectural constraints before generating solutions.
- **Plan Generation**: Outputting an implementation plan (`implementation_plan.md`) detailing intended changes and verifying it with the Human first.
- **Sandbox Execution & Verification**: Creating/modifying code and running linting (`ruff`), typing (`mypy`), and tests (`pytest`) inside the local terminal sandbox.
- **Code/Implementation-Level Git Checkpointing**: Making incremental, logical git commits directly on the active feature branch (`feat/*`) when code builds and tests pass.
- **Minimal Patching**: Touching the absolute minimum number of lines required. No opportunistic refactoring unless requested.
- **TDD Enforcement**: Writing pytest harnesses and seeing them fail before implementing business logic.

2. Core Methodology: The 5-Step Loop

Every feature or bug fix must follow this exact sequence:

1. **[Goal]**: The Human defines the objective.
2. **[Inspect]**: The Agent analyzes existing code/context and reports missing context, ambiguities, or design constraints.
3. **[Simulate]**: The Agent outputs a detailed `implementation_plan.md` (no implementation code allowed yet). The Human reviews and approves the plan.
4. **[Patch Minimally]**: The Agent implements the minimal changes and writes corresponding unit tests.
5. **[Verify]**: The Agent runs `uv run pytest`, `ruff check .`, and `mypy` in the local terminal sandbox. The Human reviews the final walkthrough and merges.

**Deterministic Break**: If the Agent's patch fails the sandbox test suite or linting more than twice, the Agent must halt execution, summarize the failure logs, and wait for Human intervention.

3. Strict Coding Standards & Tooling

The Agent must conform to the established tooling defined in `docs/development_workflow.md` and `pyproject.toml`.

- **Type Hinting**: Strict Python 3.10+ type hints are mandatory for all function signatures and complex variables. Use mypy-compatible syntax.
- **Docstrings**: All functions, classes, and modules must use standard NumPy-style docstrings.
- **Linting & Formatting**: Code must pass `ruff check .` and `ruff format .` without warnings.
- **Testing**: All features require corresponding unit tests in the `tests/` directory using `pytest`. Edge cases must be explicitly tested.
- **Package Management**: The project uses `uv`. The Agent should not recommend `pip` or `poetry`.

4. Standard Workflow Execution Phase

When starting a new module or feature, follow this flow:

**Phase A: Architecture (Human & Reasoning Agent)**
1. Human injects relevant specifications and source files.
2. Agent executes [Inspect] and [Simulate] to produce `implementation_plan.md`.
3. Human reviews and approves the plan.

**Phase B: Test Generation (Agent in Sandbox)**
1. Agent generates tests in the `tests/` directory.
2. Agent runs `uv run pytest` to verify tests fail.

**Phase C: Implementation & Verification (Agent in Sandbox)**
1. Agent implements business logic to pass tests.
2. Agent runs `uv run pytest`, `ruff check .`, and `mypy .` to verify a clean build.
3. Agent commits passing, well-formatted code to the local feature branch as an implementation checkpoint.
4. Agent writes a `walkthrough.md` summarizing changes and test runs.

**Phase D: Review & Git Checkpoint (Human)**
1. Human reviews the walkthrough, the diff, and the implementation-level commits on the feature branch.
2. Human runs final local checks if desired.
3. Human performs the final feature-level checkpointing (squash-merging the feature branch into `dev`).
4. Human flushes the context window and opens a new session for the next feature.

5. Human-Agent Interaction & Token Hygiene Protocols

To maximize developer efficiency and minimize token utilization, the following routines must be followed:

5.1 Interactive Q&A via `/grill-me`
- **When**: Prior to starting work on a new module or if requirements are ambiguous.
- **Trigger**: The Human should execute the `/grill-me` command to initiate an interactive Q&A session.
- **Goal**: Resolve all architectural assumptions, mathematical frameworks, and integration boundaries up front, eliminating downstream code churn.

5.2 Isolated Workspaces & Subagent Delegation
- **Research Handoff**: For complex library research (e.g., NumPy/SciPy optimization routines or Yahoo Finance/FRED API behaviors), the Agent should invoke a `research` subagent.
- **Task Isolation**: Subagent runs should be executed in branched/shared workspaces to keep the primary session clean of massive log dumps and experimental trials.

5.3 Token Hygiene Rules
- **Precise Injections**: Avoid injecting entire repositories or folders. Use targeted file references with exact line numbers where possible.
- **Immediate Session Flushing**: As soon as a feature branch is squash-merged, the Human should flush the active session to reset token accumulation.
- **Structured Two-Strike Escapes**: If the sandbox test suite or linting fails twice, the Agent will stop looping and output:
  1. The exact failing diff.
  2. The exact error output/logs.
  3. A list of 2-3 logical solutions or design decisions for the Human to choose from.

6. Specialized Subagent Architecture

When tackling mathematically complex implementation stages, the primary agent can spawn specialized subagents to isolate tasks.

6.1 Quantitative Finance Modeling Agent (`quant_modelling`)
- **Focus**: Quantitative finance theory, fixed-income math (yield curves, duration/convexity derivations, interpolation splines), optimization algorithms, and textbook validations.
- **Role**: Mathematical validation and test harness design. They ensure the equations and limits are precise.
- **Workflow**: Called during Phase A/B to inspect logic and design mathematical test cases.

6.2 Python Coding Agent (`python_coder`)
- **Focus**: Clean implementation mechanics, Python 3.10+ typing, `pytest` unit test suites, linting/formatting (`ruff`), and code optimization.
- **Role**: Software engineer. They write clean, minimal, compliant code that satisfies the mathematical constraints.
- **Workflow**: Called during Phase C to implement the finalized blueprints and verify they compile and pass within the sandbox.