"""Canonicalize only representations that preserve rule meaning."""

import ipaddress
import re

import idna

from src.models import RULE_TYPES, ValidationError

DOMAIN_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", re.ASCII)


def normalize_value(rule_type: str, value: object) -> str:
    if rule_type not in RULE_TYPES:
        raise ValidationError(f"unknown rule type: {rule_type!r}")
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("value must be a non-empty string")
    value = value.strip()
    if rule_type in {"DOMAIN", "DOMAIN-SUFFIX"}:
        domain = value.lower().removesuffix(".")
        labels = domain.split(".")
        if (
            not value.isascii()
            or len(domain) > 253
            or len(labels) < 2
            or any(DOMAIN_LABEL.fullmatch(label) is None for label in labels)
            or labels[-1].isdigit()
        ):
            raise ValidationError(f"invalid domain: {value!r}; use an ASCII hostname")
        # Validate A-labels as well as ordinary ASCII labels. Unicode input must
        # be explicitly converted to punycode by the contributor.
        for label in labels:
            if label.startswith("xn--"):
                try:
                    idna.decode(label)
                except UnicodeError as error:
                    raise ValidationError(f"invalid punycode label: {label!r}") from error
        return domain
    if (
        "/" not in value
        or not value.rsplit("/", 1)[1].isascii()
        or not value.rsplit("/", 1)[1].isdigit()
    ):
        raise ValidationError(f"invalid CIDR: {value!r}; an explicit prefix length is required")
    if "%" in value:
        raise ValidationError("CIDR scope identifiers are not supported")
    try:
        network = ipaddress.ip_network(value, strict=False)
    except ValueError as error:
        raise ValidationError(f"invalid CIDR: {value!r}") from error
    expected_version = 4 if rule_type == "IP-CIDR" else 6
    if network.version != expected_version:
        raise ValidationError(f"{rule_type} requires IPv{expected_version}: {value!r}")
    return str(network)
