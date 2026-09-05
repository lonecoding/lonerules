"""Validate all unified sources: python -m src.validate --strict."""

import argparse
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from src.models import (
    CATEGORIES,
    PROJECT_ROOT,
    RULE_TYPES,
    Rule,
    RuleSet,
    ValidationError,
    ValidationResult,
)
from src.normalize import normalize_value


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently keeping the last value."""


def _mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValidationError(f"line {key_node.start_mark.line + 1}: YAML keys must be strings")
        if key in result:
            raise ValidationError(
                f"line {key_node.start_mark.line + 1}: duplicate YAML key {key!r}"
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def load_yaml(path: Path) -> object:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
        raise ValidationError(f"{path}: {error}") from error


def _fields(value: object, required: set[str], optional: set[str] = frozenset()) -> dict:
    if not isinstance(value, dict):
        raise ValidationError("expected a mapping")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise ValidationError(
            f"invalid fields (missing: {sorted(missing)}, unknown: {sorted(unknown)})"
        )
    return value


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    return value.strip()


def load_sources(path: Path) -> set[str]:
    try:
        document = _fields(load_yaml(path), {"sources"})
        if not isinstance(document["sources"], list) or not document["sources"]:
            raise ValidationError("sources must be a non-empty list")
        identifiers = set()
        for record in document["sources"]:
            record = _fields(record, {"id", "kind", "author", "url", "license"}, {"notes"})
            for field in ("id", "kind", "author", "url", "license"):
                _text(record[field], field)
            identifier = record["id"]
            if identifier in identifiers:
                raise ValidationError(f"duplicate source id: {identifier!r}")
            if record["kind"] not in {"original", "third-party"}:
                raise ValidationError("source kind must be original or third-party")
            try:
                url = urlsplit(record["url"])
            except ValueError as error:
                raise ValidationError("source url must be an absolute HTTPS URL") from error
            if url.scheme != "https" or not url.netloc:
                raise ValidationError("source url must be an absolute HTTPS URL")
            if record["license"].strip().lower() in {"unknown", "none", "tbd", "unlicensed"}:
                raise ValidationError("source license must be identified before importing rules")
            if "notes" in record:
                _text(record["notes"], "notes")
            identifiers.add(identifier)
        return identifiers
    except ValidationError as error:
        raise ValidationError(f"{path}: {error}") from error


def validate(root: Path = PROJECT_ROOT, *, strict: bool = False) -> ValidationResult:
    sources = load_sources(root / "data/sources.yaml")
    folder = root / "data/rules"
    expected = {f"{name.lower()}.yaml" for name in CATEGORIES}
    actual = {path.name for path in folder.glob("*") if path.is_file()}
    if actual != expected:
        raise ValidationError(
            f"{folder}: missing files {sorted(expected - actual)}; unexpected files {sorted(actual - expected)}"
        )
    rulesets, warnings = [], []
    owners: dict[tuple[str, str], str] = {}
    for name in CATEGORIES:
        path = folder / f"{name.lower()}.yaml"
        try:
            document = _fields(load_yaml(path), {"name", "rules"}, {"source"})
            if document["name"] != name:
                raise ValidationError(f"name must be {name!r}")
            default_source = document.get("source")
            if default_source is not None and _text(default_source, "source") not in sources:
                raise ValidationError(f"unknown source: {default_source!r}")
            raw_rules = document["rules"]
            if not isinstance(raw_rules, list) or not raw_rules:
                raise ValidationError("rules must be a non-empty list")
            rules, seen = [], {}
            for index, raw in enumerate(raw_rules, start=1):
                try:
                    raw = _fields(raw, {"type", "value"}, {"source"})
                    rule_type = _text(raw["type"], "type")
                    if rule_type not in RULE_TYPES:
                        raise ValidationError(f"unknown rule type: {rule_type!r}")
                    source = _text(raw.get("source", default_source), "source")
                    if source not in sources:
                        raise ValidationError(f"unknown source: {source!r}")
                    rule = Rule(rule_type, normalize_value(rule_type, raw["value"]), source)
                    if rule.key in seen:
                        warnings.append(
                            f"{path}: rule {index}: duplicate of rule {seen[rule.key]}: {rule.key}"
                        )
                        continue
                    if rule.key in owners:
                        raise ValidationError(
                            f"cross-category conflict with {owners[rule.key]}: {rule.key}"
                        )
                    seen[rule.key] = index
                    owners[rule.key] = f"{name} rule {index}"
                    rules.append(rule)
                except ValidationError as error:
                    raise ValidationError(f"rule {index}: {error}") from error
            rulesets.append(RuleSet(name, tuple(rules)))
        except ValidationError as error:
            raise ValidationError(f"{path}: {error}") from error
    if strict and warnings:
        raise ValidationError(
            "duplicate rules are not allowed in strict mode:\n" + "\n".join(warnings)
        )
    return ValidationResult(tuple(rulesets), tuple(warnings))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="fail on duplicate rules")
    args = parser.parse_args()
    try:
        result = validate(strict=args.strict)
    except ValidationError as error:
        parser.exit(1, f"Validation failed: {error}\n")
    for warning in result.warnings:
        print(f"Warning: {warning}")
    count = sum(len(ruleset.rules) for ruleset in result.rulesets)
    print(f"Validated {len(result.rulesets)} categories, {count} unique rules")


if __name__ == "__main__":
    main()
