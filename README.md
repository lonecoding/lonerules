# LoneRules

[![CI](https://github.com/lonecoding/lonerules/actions/workflows/ci.yml/badge.svg)](https://github.com/lonecoding/lonerules/actions/workflows/ci.yml)

One unified rule source. Validated, normalized and generated client outputs.

An independently designed and implemented open-source project by **lonecoding**.

## v0.1 scope

Quantumult X is the only supported target. The initial 20 rules cover a small
selection of domains in **AI, Apple, Streaming, Social, China and Global**.
These are deliberately small starter lists, not complete service inventories.
Surge, Loon, Mihomo and sing-box are future targets, not implemented adapters.

- Client-independent YAML sources, with explicit provenance.
- Domain and IPv4/IPv6 CIDR validation and normalization.
- Stable duplicate removal; strict CI rejects duplicates and category conflicts.
- Generated Quantumult X `.list` files and a self-contained `basic.conf`.
- Deterministic outputs, SHA-256 manifest, tests and push/PR checks.
- Tagged GitHub releases, published only after all CI checks pass.

## Use with Quantumult X

Download [basic.conf](https://github.com/lonecoding/lonerules/releases/latest/download/basic.conf)
from the [latest release](https://github.com/lonecoding/lonerules/releases/latest),
then import it into Quantumult X. Add your own servers and switch the **Proxy**
group from `direct` to `proxy`. Until then, this starter routes traffic directly.
Apple and China default to direct; other categories default to the Proxy group.

The profile embeds the generated rules. Re-import a newer version to update
that snapshot. For automatic updates inside an existing configuration, use the
individual remote rule lists instead; see the [Quantumult X guide](docs/quantumultx.md).

Client syntax is based on the
[official Quantumult X reference](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf).
Automated tests cover generation and internal configuration consistency.
**Device import and live routing have not yet been verified on an iOS device.**
This project does not provide proxy servers or subscriptions.

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
Unknown types are errors. See the [schema and validation contract](docs/rule-schema.md)
for domain restrictions, duplicate behavior and ordering.

All initial rules are independently selected original data. No third-party
rule lists are imported. Future imports require a source record and explicit
license review; attribution alone does not grant permission to redistribute.
See [CONTRIBUTING.md](CONTRIBUTING.md).

Original code, templates and original rule data are [MIT licensed](LICENSE).
Future third-party data retain their own applicable licenses.

## Maintenance

There is no automatic third-party fetch or background update process in v0.1.
Updates arrive through reviewed source changes. A `v*` tag matching the project
version publishes release artifacts after CI succeeds.

- [Contributor guide](CONTRIBUTING.md)
- [Quantumult X setup and device checks](docs/quantumultx.md)
- [Architecture and release procedure](docs/maintenance.md)
- [逐步开发与验证说明（中文）](docs/walkthrough.zh-CN.md)
- [Changelog](CHANGELOG.md)
