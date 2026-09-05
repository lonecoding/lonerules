# LoneRules

[![CI](https://github.com/lonecoding/lonerules/actions/workflows/ci.yml/badge.svg)](https://github.com/lonecoding/lonerules/actions/workflows/ci.yml)

An experimental tool that validates YAML rule sources and builds reproducible
client configurations. Currently supports Quantumult X.

The initial 20 rules cover a small selection of AI, Apple, streaming, social,
China, and global domains. They are starter lists, not complete service coverage.
For the separate service-rule collection with advertising blocklists, see
[QuantumultX-Rules](https://github.com/lonecoding/QuantumultX-Rules).

## Quick start

Download [basic.conf](https://github.com/lonecoding/lonerules/releases/latest/download/basic.conf)
from the [latest release](https://github.com/lonecoding/lonerules/releases/latest)
and import it into Quantumult X. Add your own servers, then switch the **Proxy**
group from `direct` to `proxy`. Traffic routes directly until you do so;
Apple and China default to direct.

The profile embeds a snapshot of the rules. Re-import it to update, or use
[remote lists](docs/quantumultx.md) for automatic refreshes.

**Device import and live routing have not yet been verified on an iOS device.**
This project does not provide servers or subscriptions. Surge, Loon, Mihomo,
and sing-box adapters are future plans and are not implemented.

## How it works

```text
YAML sources → validate and normalize → Quantumult X output
```

Builds include rule lists, a configuration template, source records, and a
SHA-256 manifest. Automated checks validate inputs and generated outputs.

## Documentation

- [Quantumult X setup and device checks](docs/quantumultx.md)
- [Local development](docs/development.md)
- [Build and verification walkthrough](docs/walkthrough.md)
- [Rule schema](docs/rule-schema.md)
- [Contributing](CONTRIBUTING.md) · [Maintenance](docs/maintenance.md) · [Changelog](CHANGELOG.md)

## License

Original code, templates, and rule data are [MIT licensed](LICENSE).
Third-party data, if added, retain their applicable licenses.
