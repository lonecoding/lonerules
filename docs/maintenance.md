# Architecture and maintenance

## Build boundary

1. `validate.py` loads YAML with a safe loader that rejects duplicate keys,
   checks the registry and schema, and returns immutable rulesets.
2. `normalize.py` canonicalizes domains and CIDRs. Validation identifies
   normalized duplicates and cross-category conflicts.
3. The Quantumult X adapter translates validated rules and fills the maintained
   configuration template. Future targets can consume the same rule objects.
4. `build.py` renders everything before writing, atomically replaces individual
   files and removes stale files from the generated-only `dist/` tree.

No input errors modify an existing build. Writes are atomic per file, not a
transaction over the whole directory. Builds must not run concurrently into
the same `dist/`. No clocks or network access are used during generation.
The SHA-256 manifest covers all other distributed files, not itself.

`dist/` is tracked for convenient GitHub raw subscriptions. Generated changes
must accompany source changes. CI first checks committed files without writing,
then rebuilds and runs tests. Editing output without its source fails CI.

## Publish a version

Work on a normal branch and submit a PR. Before a release:

1. Update `pyproject.toml` version, `CHANGELOG.md`, `docs/release-notes.md`, and
   any version-specific examples in the docs.
2. Run the contributor checks; commit source changes and rebuilt `dist/`.
3. Merge to `main` after CI succeeds.
4. Tag that commit and push the tag:

```bash
git switch main
git pull --ff-only
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

The push workflow validates and tests on all matrix environments. Only a
successful tagged run can publish; the tag must match the project version.
The release job independently verifies and builds the artifacts, then uploads
individual files and a ZIP containing `dist/`, the client guide and MIT license.

Do not overwrite published tags or release assets to fix a version. Publish
a patch release instead. If a release job fails before publication, inspect the
log and rerun it after resolving the environmental issue. If publication was
partial, inspect the existing assets before deciding how to recover; the job
does not automatically clobber releases.

## Keeping the project small

v0.1 intentionally has no third-party fetcher, web UI, subscription converter,
plugin framework or adapters for unimplemented targets. Dependencies are fixed
in `pyproject.toml`; update them deliberately in PRs with full CI validation.
The CLI is for source checkouts, not a separately installed wheel application.
