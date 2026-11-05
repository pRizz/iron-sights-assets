# Repository instructions

These instructions apply throughout this repository.

## Repo-Local Guidance

- Read [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) before
  changing assets. Their rules are binding: draw everything in our own
  sources, never trace a game's art, fonts or any texture or font pack or copy
  their outlines, coordinates, pixels or metrics, keep ROM-derived data
  (including glyph metrics, texture checksums and comparison images) out of the
  repository, do not name assets after the game or its fonts, and keep
  everything MIT. Derivatives of other open works stay out of Git. The owner
  may compare with the game's own glyphs locally (Iron Sights'
  `scripts/port/compare_open_font.py`); note in the provenance when a
  comparison informed a change.
- Sign off every commit (`git commit -s`, Developer Certificate of Origin), and
  give each asset change a provenance note: author, what it was made from, tools.
- Python 3.12 builds everything. Install the pinned tools with
  `python -m pip install -r requirements.txt`; do not upgrade them casually,
  since outputs must rebuild identically.
- After changing a font's sources or the tools, run `python -m tools.build`
  and commit the rewritten `dist/`. Before committing, run
  `python -m unittest discover -s tests -t .`, `python -m tools.check_dist` and
  `bun scripts/bright-builds-check.ts all`. CI runs all three.
- Determinism matters across Windows and Linux: avoid platform maths functions
  whose last bit can differ (such as `hypot`) in anything that reaches an
  output; prefer `sqrt(x*x + y*y)`. PNGs are compared by pixels, the TTF and
  JSON by bytes.
- Releases come from `v*` tags: CI packs each font with the license and
  SHA-256 checksums (`tools/package_release.py`). Tag only after the owner has
  reviewed the change, and record released versions in Iron Sights'
  [open assets plan](https://github.com/pRizz/Iron-Sights/blob/main/scripts/port/open_assets_plan.md).
- Keep scratch work, venvs and downloaded tools under the ignored `build/`.

<!-- bright-builds-rules-managed:begin -->

# Bright Builds Rules

`AGENTS.md` is the entrypoint for repo-local instructions, not the complete Bright Builds Rules specification.

This managed block is owned upstream by `bright-builds-rules`. If this block needs a fix, open an upstream PR or issue instead of editing the managed text in a downstream repo. Keep downstream-specific instructions outside this managed block.

Before plan, review, implementation, or audit work:

1. Read the repo-local instructions in `AGENTS.md`, including any `## Repo-Local Guidance` section and any instructions outside this managed block.
1. Read `AGENTS.bright-builds.md`.
1. Read `standards-overrides.md` when present.
1. Read the local managed standards pages under `standards/` relevant to the task.
1. If you have not done that yet, stop and load those sources before continuing.

Use this routing map when deciding what to load next:

- For repo-specific commands, prerequisites, generated-file ownership, CI-only suites, or recurring workflow facts, use the local `AGENTS.md`, especially `## Repo-Local Guidance`.
- For the Bright Builds default workflow and high-signal cross-cutting rules used in most tasks, use `AGENTS.bright-builds.md`.
- For deliberate repo-specific exceptions to the Bright Builds defaults, use `standards-overrides.md`.
- To choose the right managed standards page, start with the local Bright Builds entrypoint `standards/index.md`.
- For business-logic structure, domain modeling, and functional-core versus imperative-shell decisions, use the managed standards page `standards/core/architecture.md`.
- For control flow, naming, function/file size, and readability rules, use the managed standards page `standards/core/code-shape.md`.
- For frontend visual defaults, theme defaults, and dark-mode decisions, use the managed standards page `standards/core/frontend-ui.md`.
- For sync, bootstrap, and pre-commit verification rules, use the managed standards page `standards/core/verification.md`.
- For the managed starter checks, run `bun scripts/bright-builds-check.ts all`; use its `--help` output for check-specific commands, exact-file exceptions, and trailing-slash `file-lengths` directory exceptions.
- For unit-test expectations, use the managed standards page `standards/core/testing.md`.
- For Rust or TypeScript/JavaScript-specific rules, use the matching managed standards page under `standards/languages/`.
- For TypeScript/JavaScript frontend framework and UI-library defaults, use `standards/languages/typescript-javascript.md`.
- Keep recurring repo-specific workflow facts, commands, and links in a `## Repo-Local Guidance` section elsewhere in this file.
- Record deliberate repo-specific exceptions and override decisions in `standards-overrides.md`.
- If instructions elsewhere in `AGENTS.md` conflict with `AGENTS.bright-builds.md`, follow the repo-local instructions and treat them as an explicit local exception.

<!-- bright-builds-rules-managed:end -->
