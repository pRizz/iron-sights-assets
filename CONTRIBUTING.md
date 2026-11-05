# Contributing

Thanks for helping. Everything here must be original and MIT licensed, so
contributions need two things: a sign-off and a provenance note.

## Sign-off (Developer Certificate of Origin)

Sign off every commit with `git commit -s`. The `Signed-off-by:` line certifies
the [Developer Certificate of Origin 1.1](https://developercertificate.org/):
that you made the contribution, or have the right to submit it, under this
repository's MIT license.

## Provenance note

Every pull request that adds or changes an asset includes a short note in its
description:

- **Author:** who drew, designed or generated it.
- **Made from:** where it started, for example "blank canvas", "parameters in
  `fonts/<name>/source/params.json`", or "our own earlier version". References
  you looked at for general style (for example "a 1990s bold grotesque") are
  fine to mention; anything you traced or measured is not allowed (see below).
- **Tools:** the editors and generators used, with versions where it matters.

## Not allowed

- Tracing, sampling, scanning or measuring any game's art, fonts or textures,
  or any texture or font pack, whatever its license.
- Committing anything read from a game ROM, including glyph widths, kerning,
  texture layouts and checksums.
- Committing assets derived from other open works (OFL, Apache-2.0, CC-BY and
  so on). They keep their own license and cannot become MIT.
- Naming assets after the game or its fonts.

## Builds and checks

Outputs must rebuild byte-for-byte from their sources with the tools in
`tools/`. Run the checks in `tests/` before opening a pull request; they never
need a ROM:

```bash
python -m unittest discover -s tests -t .
python -m tools.check_dist
```

<!-- bright-builds-rules-contributing:begin -->

# Bright Builds Contribution Defaults

This managed block is owned upstream by `bright-builds-rules`. If this block needs a fix, open an upstream PR or issue instead of editing the managed text in a downstream repo. Keep repo-local contribution guidance outside this managed block.

## Default contribution expectations

- Treat `AGENTS.md` as the entrypoint for repo-local instructions, not the complete Bright Builds Rules spec.
- Before plan, review, implementation, or audit work, read local `AGENTS.md`, `AGENTS.bright-builds.md`, `standards-overrides.md` when present, and the local managed standards pages relevant to the task; if that has not happened yet, stop and load them before continuing.
- Follow the local `AGENTS.md`.
- Use the local managed standards pages as the canonical reference, with source provenance recorded in `AGENTS.bright-builds.md` and `bright-builds-rules.audit.md`.
- Prefer simple, root-cause fixes over broad rewrites.
- Document repo-specific exceptions in `standards-overrides.md`.

## Code expectations

- Keep business logic in a functional core when practical.
- Prefer early returns and shallow control flow.
- Prefix internal nullable or optional names with `maybe`, including functions, bindings, and internal fields, and use `MaybeX` aliases only when they materially clarify a repeated nullable surface.
- Split oversized functions and files into sensible units.
- Do not hide substantial foreign-language logic inside strings; keep workflow and automation config thin, move scripts, queries, and similar artifacts into repo-owned or language-aware files, make checked-in scripts rerunnable when sensible, and have them leave breadcrumb-heavy logs and summaries in a repo-defined gitignored location.
- Parse boundary input into domain types when that removes repeated validation.
- Apply any relevant language-specific guidance from the local managed standards.

## Verification expectations

- Before substantive implementation work, sync first: fetch remote state before editing; if the current branch tracks an upstream and the worktree is clean, prefer rebasing onto the latest upstream or the repo's equivalent sync path, such as `git pull --rebase` when local guidance uses it; if a worktree starts detached, assume the repo default branch, often `main`; resolve any sync conflicts before proceeding, then run the repo's normal bootstrap or dependency-sync step when dependencies or tools may be stale.
- Before formatting Markdown, inspect repo-local guidance and formatter configuration, require the configured syntax extensions, preserve existing configuration, use repo-owned setup or migration commands when provided, and run check mode before an authorized, scoped write. Never fall back to bare `mdformat` when required plugins are unavailable.
- Before committing, run the relevant repo-native verification steps for the changed paths, including repository-compatible Markdown or shell formatter checks when supported tools are already available and local guidance does not define a clearer workflow, and do not commit if they fail.
- Prefer a repo-owned verify/check/validate/ci command when it exists over reconstructing tool commands by hand.
- Run `bun scripts/bright-builds-check.ts all` when the managed starter checker is installed. Use `.bright-builds-rules-checks.tsv` only for deliberate exact-file exceptions or trailing-slash `file-lengths` directory exceptions with a required reason; the file is user-owned and must not be generated by Bright Builds.
- Heavy integration, end-to-end, or external-service suites may stay pre-push or CI-only when local guidance or `standards-overrides.md` documents that choice.
- If hooks appear to own verification here and the local workflow is unclear, clarify whether the repo expects hooks, manual checks, or both.

## Test expectations

- Unit test pure code and business logic.
- Keep each unit test focused on one concept.
- Use explicit Arrange, Act, Assert sections unless the structure is truly obvious.

## Pull request expectations

- Explain the behavior change, not just the code movement.
- Call out any new exceptions to the standards.
- When plan, review, or audit work relied on these standards, briefly name the local guidance, sidecar, overrides, or standards pages that materially informed the work.
- Include verification evidence for the changed paths.
- Note any residual risks or follow-up work.

<!-- bright-builds-rules-contributing:end -->
