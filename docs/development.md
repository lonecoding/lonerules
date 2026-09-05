# Development

Run commands from the repository root.

## Build locally

Use Python **3.11 or newer**. Clone the source repository and work from its root:

```bash
git clone https://github.com/lonecoding/lonerules.git
cd lonerules
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m src.validate --strict
python -m src.build
python -m unittest discover -s tests -v
python -m src.build --check
```

Check `python3 --version` first: the Python shipped with some macOS versions
is too old. On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell.
CI verifies Python 3.11, 3.13 and 3.14 on Linux, plus Python 3.11 on macOS.
Run `python -m ruff check .` and `python -m ruff format --check .` before a PR.

Expected output includes:

```text
Validated 6 categories, 20 unique rules
Built 10 files in dist/
...
OK
Verified 10 files in dist/
```

The command-line build is a **source-checkout tool**; keep `data/` and `profiles/`
alongside `src/`. Standalone wheel distribution is not part of v0.1.

## Source to output

```yaml
name: AI
source: lonerules-original
rules:
  - type: DOMAIN-SUFFIX
    value: openai.com
```

The Quantumult X adapter adds client syntax and the category's policy name:

```text
host-suffix,openai.com,AI
```

Unlike the initial two-column prototype, published lists contain a policy
field, matching the official format. When importing a list separately, bind it
to an existing policy with `force-policy`.

```text
data/rules/*.yaml + data/sources.yaml
                  ↓
          validate → normalize → deduplicate
                  ↓
        Quantumult X adapter + profile template
                  ↓
                 dist/
```

| Path | Purpose |
| --- | --- |
| `data/rules/` | The six maintained rule sources |
| `data/sources.yaml` | Authors, source URLs and licenses |
| `src/validate.py`, `src/normalize.py` | Shared input checks and canonicalization |
| `src/targets/quantumultx.py` | Quantumult X rendering only |
| `profiles/quantumultx/` | Maintained configuration template |
| `dist/quantumultx/` | Generated rules and profile |
| `dist/manifest.json` | Counts and hashes of distributed files |
| `tests/`, `.github/workflows/` | Regression tests and CI/release pipeline |

**Never edit `dist/` manually.** Generated files are committed to make raw URLs
usable and output changes reviewable. Run the builder after editing a source
or template; CI rejects any mismatch, including missing or extra artifacts.

## Rule semantics and provenance

Supported source types: `DOMAIN`, `DOMAIN-SUFFIX`, `IP-CIDR`, `IP-CIDR6`.
Unknown types are errors. See the [schema and validation contract](rule-schema.md)
for domain restrictions, duplicate behavior and ordering.

All initial rules are independently selected original data. No third-party
rule lists are imported. Future imports require a source record and explicit
license review; attribution alone does not grant permission to redistribute.
See [CONTRIBUTING.md](../CONTRIBUTING.md).

Original code, templates and original rule data are [MIT licensed](../LICENSE).
Future third-party data retain their own applicable licenses.


## Maintenance

There is no automatic third-party fetching or background update process in v0.1.
Updates arrive through reviewed source changes. A `v*` tag matching the project
version publishes release artifacts after CI succeeds. See the
[maintenance guide](maintenance.md) for release procedures.
