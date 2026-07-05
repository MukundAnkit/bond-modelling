# Development Workflow

> Practices to follow throughout the project lifecycle.

---

## 1. Branch Strategy

```
main ──────────────────────────────────────  (releases only)
  │                          ↑
  └── dev ───────────────────┘             (integration)
        │            ↑
        └── feat/* ──┘                     (feature branches)
```

| Branch | Purpose |
|---|---|
| `main` | Production releases. Empty base — only ever receives code from `dev` via merge + tag. |
| `dev` | Active development. All features land here. Should always pass tests. |
| `feat/*` | Short-lived branches for individual units of work. Naming: `feat/<module>-<description>`, e.g. `feat/module2-duration`. |

---

## 2. Commit Convention — Conventional Commits

Every commit on `dev` and `feat/*` branches should follow:

```
<type>: <short description>

<optional body>
```

| Type | When to use | Example |
|---|---|---|
| `feat` | New feature | `feat: add Macaulay Duration calculation` |
| `fix` | Bug fix | `fix: YTM solver diverges for zero-coupon bonds` |
| `test` | Adding / fixing tests | `test: cover shock simulation edge cases` |
| `docs` | Documentation | `docs: update project status after Module 2` |
| `refactor` | Code restructuring (no behavior change) | `refactor: extract numerical derivative helper` |
| `chore` | Tooling, config, CI | `chore: add pytest-cov to dev deps` |

This enables automatic changelog generation and clear release notes.

---

## 3. Commit Frequency

**On `feat/*` branches** — commit as often as you like. Every logical checkpoint where code compiles / tests pass is a good candidate:

```
feat: add Modified Duration function skeleton
feat: implement Modified Duration core logic
test: add Modified Duration tests
fix: edge case for zero-coupon bond Modified Duration
```

These WIP commits don't need to be polished — they get compressed on merge.

**On `dev`** — commits land here only via squash-merge from feature branches (see below).

---

## 4. PR & Merge Workflow

### Feature branch → `dev`

```
feat/module2-duration ──→ PR ──→ squash-merge ──→ dev
```

1. Create feature branch from `dev`
2. Develop and commit freely on the branch
3. Push and open a pull request on GitHub (`feat/*` → `dev`)
4. Use the **PR template** (`.github/pull_request_template.md`)
5. Ensure CI passes (tests, lint)
6. **Squash and merge** into `dev`

**Why squash-merge?** Collapses all WIP commits into a single clean commit on `dev`:

```
dev history:   feat: add Macaulay Duration     ← one clean commit
               feat: implement risk shocks      ← one clean commit
               fix: correct YTM edge case       ← one clean commit
```

vs. without squash:

```
dev history:   WIP: start duration              ← noisy
               fix typo in duration             ← noisy
               add more tests                   ← noisy
               ...
```

### `dev` → `main`

```
dev ──→ PR ──→ merge commit ──→ main (tagged)
```

1. When a module is fully implemented and verified (notebook cross-checks against textbooks)
2. Open a PR from `dev` → `main`
3. Run full test suite + notebook verification
4. Use a **merge commit** (not squash) to preserve the module's commit history
5. Tag the merge: `git tag v1.0.0 && git push origin v1.0.0`

---

## 5. Pre-Merge Checklist

Before merging any PR:

- [ ] Linting passes: `uv run ruff check .`
- [ ] Format check passes: `uv run ruff format . --check`
- [ ] Type check passes: `uv run mypy src/`
- [ ] All tests pass: `uv run pytest`
- [ ] New functionality has corresponding tests
- [ ] If a module is completed, notebook verification has been run
- [ ] Consolidated output rebuilt (`output/consolidated.html` and `output/consolidated.ipynb` are up to date with source notebooks)
- [ ] `docs/project_status.md` updated (module progress, test counts, "Last updated" date)

---

## 6. Versioning — Semantic Versioning

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

## 7. CI Expectations

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically runs on every push and PR to `dev` or `main`:

- **Environment**: Python 3.12, uv-managed
- **Commands**:
  1. `ruff check .` — lint check
  2. `ruff format . --check` — format check
  3. `mypy src/` — type check
  4. `pytest -v --tb=short` — test suite
- **Expectation**: All four gates must pass. A red CI blocks the merge.

---

## 8. Summary — Typical Session

```bash
# 1. Start a feature
git checkout dev
git pull
git checkout -b feat/module2-duration

# 2. Develop (commit freely)
# ... code ...
git add -A && git commit -m "feat: add Macaulay Duration"
# ... code ...
git add -A && git commit -m "test: add Duration tests"
# ... code ...
git add -A && git commit -m "fix: edge case for zero-coupon"

# 3. Push & open PR
git push -u origin feat/module2-duration
# → Open PR on GitHub: feat/module2-duration → dev
# → Squash-merge after CI passes

# 4. Back to dev
git checkout dev
git pull
```
