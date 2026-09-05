# Unified rule schema (v0.1)

Each of the six files is required. Names are case-sensitive: `AI`, `Apple`,
`Streaming`, `Social`, `China`, `Global`; filenames are their lowercase names
with `.yaml`. Unknown files, fields, rule types and duplicate YAML keys fail.

```yaml
name: AI
source: lonerules-original
rules:
  - type: DOMAIN-SUFFIX
    value: openai.com
  - type: DOMAIN
    value: api.example.com
    source: another-registered-source
```

`source` is a provenance identifier, not a client policy. A rule can override
the file default; every effective source must exist in `data/sources.yaml`.
The example override above requires a corresponding record before use.

| Type | Accepted value | Canonical example | Quantumult X |
| --- | --- | --- | --- |
| `DOMAIN` | ASCII hostname | `api.example.com` | `host` |
| `DOMAIN-SUFFIX` | ASCII hostname | `example.com` | `host-suffix` |
| `IP-CIDR` | IPv4 with numeric prefix length | `192.0.2.0/24` | `ip-cidr` |
| `IP-CIDR6` | IPv6 with numeric prefix length | `2001:db8::/32` | `ip6-cidr` |

Domain values are trimmed, lowercased, and lose one terminal root dot.
Hostnames require at least two labels, each 1–63 ASCII letters/digits/hyphens,
with no leading/trailing hyphen, and a maximum total length of 253 characters.
The last label cannot be all digits. Wildcards, underscores, URLs, ports, IP
literals and internal whitespace are rejected. Internationalized domains must
be supplied as valid `xn--` punycode labels; raw Unicode is not accepted in v0.1.
Validation checks syntax only, not DNS existence, ownership or service coverage.

CIDRs require an explicit numeric prefix, the correct address family and no
scope identifier. Host bits are normalized to the network address:
`192.0.2.9/24` becomes `192.0.2.0/24`. IPv6 uses compressed lowercase notation.
Dotted netmasks and implicit `/32` or `/128` are not accepted.

## Duplicates, conflicts and ordering

The identity of a rule is its normalized **type and value**. In a normal build,
a same-category duplicate is reported and removed, retaining the first rule
and its source. `validate --strict` fails instead; CI always uses strict mode.
A normalized duplicate in a different category is an error in every mode.
`DOMAIN` and `DOMAIN-SUFFIX` are distinct, even when their values match.

No parent/child suffix reduction or CIDR range merging is performed. Such
changes can alter policy precedence. Semantic overlaps require human review.

Individual lists preserve source order. The basic profile emits all domain
rules first, then all source IP rules, preserving category order within each
phase: AI, Apple, Streaming, Social, China, Global. Built-in private-network
rules, the China GeoIP fallback and the final Global rule follow those sources.
Actual matching behavior also depends on Quantumult X; the builder does not
simulate the client or promise identical semantics across future adapters.

## Source registry

Each entry requires `id`, `kind` (`original` or `third-party`), `author`, `url`
(absolute HTTPS), and `license`; `notes` is optional. All required values must
be non-empty strings, source IDs must be unique, and placeholder licenses such
as `unknown` fail validation. This is a metadata check, not legal clearance or
a network check. Keep upstream revisions and additional notices in the record
and PR when importing third-party content.
