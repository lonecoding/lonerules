LoneRules v0.1.0 is the first Quantumult X MVP of an independent, MIT-licensed
rule-source and build project independently designed and implemented by lonecoding.

- Six small categories with 20 original domain rules.
- YAML validation, domain/CIDR normalization, duplicate detection and conflict checks.
- Generated native Quantumult X lists, a basic profile, provenance and SHA-256 manifest.
- Tests and CI checks for sources, formatting, reproducibility and output drift.

Download `basic.conf` or the ZIP. Import your own servers and switch the Proxy
group from direct to proxy to enable proxy routing. The basic profile embeds
a snapshot; use individual remote lists for updates in an existing profile.

The lists are intentionally incomplete starter coverage. Automated checks pass,
but iOS device import and live routing remain unverified. See the client guide
in the repository or ZIP for setup and device verification steps.
