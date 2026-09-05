# Contributing

Small, explained and testable changes are welcome. Open an issue with the
service/domain, expected category and observed behavior before proposing a
large ruleset. Do not submit server credentials or personal subscription URLs.

## Local checks

Install Python 3.11+ and `python -m pip install -e '.[dev]'` in a virtual environment.
From the repository root:

```bash
python -m ruff check .
python -m ruff format --check .
python -m src.validate --strict
python -m src.build
python -m unittest discover -s tests -v
python -m src.build --check
```

Edit only maintained sources in `data/`, `src/` or `profiles/`. Include the
resulting **generated** `dist/` changes in your PR. Never hand-fix output files.
Use `python -m ruff format .` to format Python files.

## Rule changes

- Explain why a domain belongs to its category and the scope of its suffix match.
- Keep the original source order; avoid unnecessary sorting or bulk additions.
- Prefer `DOMAIN` when matching subdomains is not intended.
- Same-category duplicates fail strict checks; remove them from the source.
- Identical rules in different categories are conflicts and must be resolved.
- A parent suffix and a child rule can intentionally coexist. Explain any
  overlap: v0.1 does not automatically detect or resolve semantic overlaps.
- Add tests for changes to validation, normalization or conversion behavior.

## Provenance and licenses

Original rules can use `source: lonerules-original`. For an imported rule,
add a `kind: third-party` entry in `data/sources.yaml`, with a stable `id`,
original author, HTTPS source URL and exact license identifier or license URL.
Use the entry's ID in the rule's `source` field (or the file-level default).
Keep any required notices and license text with the change, and describe which
upstream revision you used in the record's `notes`.

Do not import data with missing or unclear permissions. Do not relabel
third-party data as MIT. CI checks that metadata is present and referenced;
maintainers must review whether redistribution and combination are permitted,
and include any additional required notices in release artifacts before merge.

Compatibility reference material can inform an adapter without importing
another project's code or rule lists. Keep implementations original.

## Pull requests and commits

Describe the problem, changed behavior and validation results. Keep unrelated
changes in separate PRs. Use concise commit subjects such as:

```text
fix: reject malformed IPv6 rule prefixes
feat: add a Quantumult X rule adapter
docs: explain rule source attribution
```

Contributions of original project code are under the MIT License. Third-party
material must be explicitly identified and retain its applicable terms.
