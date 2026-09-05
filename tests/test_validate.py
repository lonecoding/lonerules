"""Invalid inputs and canonical duplicates must fail before generation."""

from src.models import ValidationError
from src.normalize import normalize_value
from src.validate import validate
from tests.helpers import ProjectTestCase


class ValidationTests(ProjectTestCase):
    def test_cidr_duplicates_are_detected_after_network_normalization(self):
        self.write_ai("""name: AI
source: lonerules-original
rules:
  - {type: IP-CIDR, value: 192.0.2.7/24}
  - {type: IP-CIDR, value: 192.0.2.0/24}
""")
        result = validate(self.root)
        self.assertEqual(len(result.rulesets[0].rules), 1)
        self.assertEqual(result.rulesets[0].rules[0].value, "192.0.2.0/24")
        self.assertEqual(len(result.warnings), 1)

    def test_per_rule_source_override_retains_attribution(self):
        path = self.root / "data/sources.yaml"
        path.write_text(
            path.read_text()
            + """
  - id: test-third-party
    kind: third-party
    author: Example Author
    url: https://example.org/rules
    license: CC0-1.0
"""
        )
        self.write_ai("""name: AI
source: lonerules-original
rules:
  - {type: DOMAIN, value: example.org, source: test-third-party}
""")
        result = validate(self.root)
        self.assertEqual(result.rulesets[0].rules[0].source, "test-third-party")

    def test_duplicate_rule_keys_and_unsafe_yaml_tags_fail(self):
        for text in [
            "name: AI\nsource: lonerules-original\nrules: [{type: DOMAIN, value: a.com, value: b.com}]",
            "!!python/object/apply:os.system ['echo should-not-execute']",
        ]:
            self.write_ai(text)
            with self.assertRaisesRegex(ValidationError, "ai.yaml"):
                validate(self.root)

    def test_registry_rejects_malformed_urls_and_duplicate_ids(self):
        path = self.root / "data/sources.yaml"
        original = path.read_text()
        for text in [
            original.replace("https://github.com/lonecoding/lonerules", "https://[bad"),
            original.replace("https://github.com/lonecoding/lonerules", "http://example.org"),
            original + original.removeprefix("sources:\n"),
        ]:
            path.write_text(text)
            with self.assertRaisesRegex(ValidationError, "sources.yaml"):
                validate(self.root)

    def test_all_categories_and_provenance(self):
        result = validate(self.root, strict=True)
        self.assertEqual(
            [s.name for s in result.rulesets],
            ["AI", "Apple", "Streaming", "Social", "China", "Global"],
        )
        self.assertEqual(sum(len(s.rules) for s in result.rulesets), 20)
        self.assertFalse(result.warnings)

    def test_normalization(self):
        cases = [
            ("DOMAIN", "  Example.COM.  ", "example.com"),
            ("DOMAIN-SUFFIX", "xn--bcher-kva.de", "xn--bcher-kva.de"),
            ("DOMAIN-SUFFIX", "xn--fa-hia.de", "xn--fa-hia.de"),
            ("IP-CIDR", "192.0.2.7/24", "192.0.2.0/24"),
            ("IP-CIDR6", "2001:0DB8::1/32", "2001:db8::/32"),
        ]
        for kind, raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_value(kind, raw), expected)

    def test_invalid_domains(self):
        for value in [
            "",
            " ",
            None,
            123,
            True,
            "localhost",
            "https://example.com",
            "*.example.com",
            "example.com/path",
            "foo..com",
            "-foo.com",
            "foo-.com",
            "foo_bar.com",
            "127.0.0.1",
            "1.2.3.999",
            "a,proxy.com",
            "a\nb.com",
            "a#b.com",
            "a" * 64 + ".com",
            "bücher.de",
            "K.com",
            "xn--.com",
            "example.com..",
        ]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                normalize_value("DOMAIN-SUFFIX", value)

    def test_invalid_cidrs_and_unknown_types(self):
        for kind, value in [
            ("IP-CIDR", "192.0.2.0"),
            ("IP-CIDR", "192.0.2.0/33"),
            ("IP-CIDR", "999.0.0.0/8"),
            ("IP-CIDR", "::/0"),
            ("IP-CIDR6", "0.0.0.0/0"),
            ("IP-CIDR6", "::/129"),
            ("IP-CIDR6", "fe80::%en0/64"),
            ("IP-CIDR", "192.0.2.0/255.255.255.0"),
            ("UNKNOWN", "example.com"),
        ]:
            with self.subTest(kind=kind, value=value), self.assertRaises(ValidationError):
                normalize_value(kind, value)

    def test_deduplication_preserves_order_and_strict_mode_fails(self):
        self.write_ai("""name: AI
source: lonerules-original
rules:
  - {type: DOMAIN-SUFFIX, value: Example.COM.}
  - {type: DOMAIN-SUFFIX, value: example.com}
  - {type: DOMAIN, value: example.com}
""")
        result = validate(self.root)
        self.assertEqual([r.type for r in result.rulesets[0].rules], ["DOMAIN-SUFFIX", "DOMAIN"])
        self.assertEqual(len(result.warnings), 1)
        with self.assertRaisesRegex(ValidationError, "duplicate rules"):
            validate(self.root, strict=True)

    def test_cross_category_conflict(self):
        self.write_ai(
            "name: AI\nsource: lonerules-original\nrules: [{type: DOMAIN-SUFFIX, value: APPLE.com.}]\n"
        )
        with self.assertRaisesRegex(ValidationError, "cross-category conflict"):
            validate(self.root)

    def test_bad_yaml_and_schema_report_source_path(self):
        cases = [
            "",
            "[]",
            "name: AI\nrules: []",
            "name: AI\nrules: [",
            "name: AI\nname: AI\nrules: []",
            "name: AI\nrules: [null]",
            "name: AI\nrules: [{type: UNKNOWN, value: a.com, source: lonerules-original}]",
            "name: AI\nsource: missing\nrules: [{type: DOMAIN, value: a.com}]",
            "name: AI\nsource: lonerules-original\nrules: [{type: DOMAIN, value: a.com, typo: true}]",
            "name: '../escape'\nrules: []",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.write_ai(text)
                with self.assertRaisesRegex(ValidationError, "ai.yaml"):
                    validate(self.root)

    def test_source_is_required(self):
        self.write_ai("name: AI\nrules: [{type: DOMAIN, value: a.com}]\n")
        with self.assertRaisesRegex(ValidationError, "source must"):
            validate(self.root)

    def test_missing_and_unexpected_categories(self):
        (self.root / "data/rules/apple.yaml").unlink()
        (self.root / "data/rules/typo.yml").write_text("name: Typo")
        with self.assertRaisesRegex(
            ValidationError, "missing files.*apple.yaml.*unexpected files.*typo.yml"
        ):
            validate(self.root)

    def test_source_license_and_author_are_required(self):
        path = self.root / "data/sources.yaml"
        original = path.read_text()
        for text in [
            original.replace("license: MIT", "license: unknown"),
            original.replace("author: lonecoding", "author: ''"),
        ]:
            path.write_text(text)
            with self.assertRaisesRegex(ValidationError, "sources.yaml"):
                validate(self.root)
