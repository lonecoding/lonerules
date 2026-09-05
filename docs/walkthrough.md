# Build and verification walkthrough

Run these commands from the repository root after following the
[development setup](development.md).

## 1. Validate sources

Maintain the six YAML files in `data/rules/`. Record authors, URLs, and licenses
in `data/sources.yaml`. The initial 20 rules are independently selected; no
third-party lists are imported, and coverage is intentionally limited.

```bash
python -m src.validate --strict
```

The initial dataset reports `Validated 6 categories, 20 unique rules`. Counts
change as rules are added. Duplicate rules, unknown types, empty values, and
invalid formats fail validation with file locations.

## 2. Normalize and resolve conflicts

`src/normalize.py` handles domain case, trailing root dots, and CIDR network
addresses. `src/validate.py` detects duplicates after normalization. Normal
builds deduplicate rules within a category with a warning; strict validation
rejects them. Cross-category duplicates always require a manual decision.
Different types, parent/child domains, and overlapping networks are not merged.

## 3. Build client outputs

`src/targets/quantumultx.py` maps rule formats, while
`profiles/quantumultx/basic.conf.template` defines the configuration structure.
The adapter adds policy names; sources do not contain client-specific syntax.

```bash
python -m src.build
```

The initial build reports `Built 10 files in dist/`: six lists, a configuration,
source records, the MIT license, and a SHA-256 manifest. Published lists include
a policy name in the third column.

## 4. Run checks

```bash
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -v
python -m src.build --check
```

Tests should finish with `OK`; output verification reports
`Verified 10 files in dist/`. The `--check` option does not overwrite files.
It detects missing, modified, or stale outputs.

## 5. Commit sources and outputs

Generated files are tracked so raw URLs work and output changes can be reviewed.
Do not edit `dist/` manually. Edit sources, validate, build, test, and commit
sources and outputs together.

```bash
git status --short
git add data src profiles tests dist
git commit -m "feat: extend AI rule coverage"
git push
```

Adjust paths and the commit message to match your changes, including documentation
or dependencies when relevant. Push and pull-request checks reject inconsistent
outputs.

## 6. Release

Prepare the version, changelog, and release notes. After main-branch CI passes,
create a version tag. The tag triggers CI, and artifacts are uploaded only after
all checks pass. See [Maintenance](maintenance.md) for commands and recovery.

## 7. Verify on a device

Download `basic.conf` from a release, import it, and add your servers. Switch the
Proxy group from `direct` to `proxy` to enable proxy routing. Inspect request logs
to confirm AI, Apple, Global, and other categories match as intended.

Automated checks do not replace iPhone testing. Device import and live routing
remain unverified for v0.1.0. Follow the [device checklist](quantumultx.md).
