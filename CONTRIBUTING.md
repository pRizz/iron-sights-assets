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
