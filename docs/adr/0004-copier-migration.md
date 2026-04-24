# ADR 0004 — Migrate from a prose SETUP.md to a Copier template

- Status: accepted
- Date: 2026-04-24
- Supersedes: the 2500-line `SETUP.md` in the origin project.

## Context

The original delivery format was a single `SETUP.md` file (~2500 lines, ~90 KB) that told an
AI agent how to scaffold a fresh ESP32-S3 hexagonal-lite project. Problems observed in the
review pass:

- **Non-determinism.** Two agents reading the same MD produce subtly different projects.
- **Drift.** Forward references and redundant sections accumulated with each edit (e.g.
  §4.22 vs §5.13 both specifying `pyproject.toml`).
- **Slow execution.** 30+ files materialised from quoted snippets, thousands of tool calls.
- **No schema / no CI.** Nothing to answer "did the agent get it right?" mechanically.
- **No update path.** Projects scaffolded last month can't pull in upstream fixes.

## Decision

Adopt **Copier** as the delivery format.

- Files live in `template/{{project_name}}/` as real files. Substitution uses `.jinja`
  suffix where variables are needed. Custom delimiters (`[[`, `]]`, `[%`, `%]`) avoid
  collisions with shell `{{}}` and C++ `{}`.
- `copier.yml` defines the questionnaire: `project_name`, `board_variant`, `psram_mode`,
  `flash_size_mb`, `enable_hil`, `enable_mcp`, `use_gsd`, `cpp_standard`, plus author info.
- `copier update` pulls upstream template fixes into an existing scaffolded project with a
  diff3-style merge.
- `tests/test_scaffold.py` runs `copier copy` into a scratch dir and asserts structure +
  `pio test -e native` + `pio run -e esp32s3`.
- `.github/workflows/scaffold-matrix.yml` runs the test matrix on every PR.

## Consequences

- **Deterministic:** the same answers produce the same files, byte-for-byte.
- **CI-able:** a golden-file hash pins the default-answers run (`scripts/verify_scaffold.py`).
- **Updatable:** users run `copier update` to pull template fixes.
- **Smaller:** the prose-wrapped file snippets are now the files themselves; the explanation
  lives in `docs/` and is read once by humans, not "executed" by agents.

The old `SETUP.md` in the origin project shrinks to a stub pointing at this template repo.

## Alternatives considered

- **`git clone` template + rename script.** Rejected: no questionnaire, no update mode, no
  parameterisation.
- **Cookiecutter.** Rejected: older sibling of Copier without update mode — strictly worse.
- **Custom executable scaffolder (Python/TS CLI).** Rejected: reinvents Copier badly.

## Migration plan

Executed in three stages (see the original review plan):

1. Consistency patch to `SETUP.md` (one atomic commit of the 19 mechanical fixes).
2. New sections in `SETUP.md`: embedded coding rules + testing & debugging strategy.
3. Copier template repo skeleton (this stage).

After stage 3, `SETUP.md` shrinks to a 5-line stub pointing here.
