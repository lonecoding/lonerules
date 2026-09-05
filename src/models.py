"""Small, client-independent objects shared by validation and adapters."""

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("AI", "Apple", "Streaming", "Social", "China", "Global")
RULE_TYPES = frozenset({"DOMAIN", "DOMAIN-SUFFIX", "IP-CIDR", "IP-CIDR6"})


@dataclass(frozen=True)
class Rule:
    type: str
    value: str
    source: str

    @property
    def key(self) -> tuple[str, str]:
        return self.type, self.value


@dataclass(frozen=True)
class RuleSet:
    name: str
    rules: tuple[Rule, ...]


@dataclass(frozen=True)
class ValidationResult:
    rulesets: tuple[RuleSet, ...]
    warnings: tuple[str, ...]


class ValidationError(ValueError):
    """An actionable source-data error that is safe to show in the CLI."""
