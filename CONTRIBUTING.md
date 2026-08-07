# Contributing to crossbio-algo

Thanks for helping. This is a short, practical guide — read the README and `PROJECT_SUMMARY.md` for the "why", this file for the "how".

## How the repo is laid out

```
skills/                       the 7 skills (each: SKILL.md + optional support files)
  _shared/                    the loop contract + the 5 cross-stage validation rules
schemas/stage-schemas.json    CANONICAL machine schema ($defs + oneOf) — single source of truth
crossbio_validate/            the validator CLI package (crossbio console script)
examples/scout/               the flagship run (spatial RNA+ATAC on PLS+OT) + its tests
tests/test_validator.py       validator suite (21 tests)
.claude-plugin/plugin.json    Claude Code plugin manifest
pyproject.toml                validator package + console script + test extra
```

## The loop the skills implement

```
data-and-estimand-audit  (GATE — fatal issues stop the chain)
  → brainstorm → topic-viability-assessment → algorithm-design → spec-writing → code
      ★ adversarial-panel-audit before trusting any stage artifact
```

Every stage emits an `artifact.json` conforming to `schemas/stage-schemas.json`. Artifacts link via `parent_artifact_id` and carry a `provenance_hash`. The chain is checked by the 5 cross-stage rules (estimand continuity / no-orphan failure_boundary / notation consistency / pseudocode→code / provenance).

## Running things

```bash
# install the validator + test deps (creates the `crossbio` console script)
pip install -e ".[test]"

# run every test (validator + scout)
python -m pytest tests/

# validate a directory of artifact.json as a chain
crossbio validate-chain <dir>

# other subcommands: validate <one.json> | validate-project <dir> | stamp <one.json>
```

## The rules that matter

- **Skill edits must keep YAML frontmatter valid** (`name` + `description` at minimum). The CI sanity step parses every `skills/**/SKILL.md` frontmatter and the plugin manifest; a broken `---` block fails CI.
- **Field lists must stay consistent with `schemas/stage-schemas.json`.** If you add/rename a required field in a skill's output contract, update the matching `$defs` entry (and the validator tests) in the same change. The schema is the single source of truth — don't restate a divergent field list in prose.
- **Honest-colleague principle.** The agent is a counsel, not a gatekeeper (except the data-audit GATE). It never vetoes; it forces informed decisions and carries competitor truth forward. Audit is two-way insurance — it guards against both under-scoring (judging crowded from names) and over-claiming (cross-domain "novelty" that's already ported). New skill content should reinforce, not erode, this.
- **Truth carries forward.** Don't soften a finding when handing to the next stage; don't invent test counts or claims you didn't verify.

## Commit style

Conventional commits — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`. Keep the subject line ≤72 chars. Example: `feat(validator): add rule5 provenance hash check`.

## Before you open a PR

- `python -m pytest tests/` is green.
- `crossbio validate-chain` passes on any artifact dir you touched.
- If you changed a skill, its frontmatter still parses and its field list still matches `schemas/stage-schemas.json`.
