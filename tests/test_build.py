"""Exercise full builds, generated-file drift, and output safety."""

import hashlib
import json

from src.build import build
from src.models import Rule, RuleSet, ValidationError
from src.targets.quantumultx import render, render_profile
from tests.helpers import ProjectTestCase


class BuildTests(ProjectTestCase):
    def setUp(self):
        super().setUp()
        # Build also ships the license with standalone downloads.
        from src.models import PROJECT_ROOT

        (self.root / "LICENSE").write_bytes((PROJECT_ROOT / "LICENSE").read_bytes())

    def test_full_build_and_repeatability(self):
        paths = build(self.root)
        self.assertEqual(len(paths), 10)
        first = {path.relative_to(self.root): path.read_bytes() for path in paths}
        build(self.root)
        self.assertEqual(first, {path.relative_to(self.root): path.read_bytes() for path in paths})
        build(self.root, check=True)
        content = (self.root / "dist/quantumultx/rules/AI.list").read_text()
        self.assertIn("host-suffix,openai.com,AI\n", content)
        self.assertIn("DO NOT EDIT", content)
        manifest = json.loads((self.root / "dist/manifest.json").read_text())
        self.assertEqual(sum(manifest["categories"].values()), 20)
        for name, digest in manifest["sha256"].items():
            self.assertEqual(
                hashlib.sha256((self.root / "dist" / name).read_bytes()).hexdigest(), digest
            )

    def test_check_detects_manual_edits_without_repairing_them(self):
        build(self.root)
        path = self.root / "dist/quantumultx/rules/AI.list"
        path.write_text("manually edited\n")
        with self.assertRaisesRegex(ValidationError, "stale"):
            build(self.root, check=True)
        self.assertEqual(path.read_text(), "manually edited\n")
        build(self.root)
        build(self.root, check=True)

    def test_missing_and_extra_outputs(self):
        build(self.root)
        (self.root / "dist/quantumultx/rules/AI.list").unlink()
        stale = self.root / "dist/quantumultx/rules/Old.list"
        stale.write_text("obsolete")
        with self.assertRaisesRegex(ValidationError, "Old.list"):
            build(self.root, check=True)
        build(self.root)
        self.assertFalse(stale.exists())
        build(self.root, check=True)

    def test_invalid_input_preserves_previous_build(self):
        paths = build(self.root)
        before = {path: path.read_bytes() for path in paths}
        self.write_ai("name: AI\nrules: []")
        with self.assertRaises(ValidationError):
            build(self.root)
        self.assertEqual(before, {path: path.read_bytes() for path in paths})

    def test_invalid_input_creates_no_output(self):
        self.write_ai("name: AI\nrules: []")
        with self.assertRaises(ValidationError):
            build(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_output_symlinks_are_rejected(self):
        external = self.root / "external"
        external.mkdir()
        (self.root / "dist").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValidationError, "symbolic links"):
            build(self.root)
        self.assertEqual(list(external.iterdir()), [])

    def test_adapter_maps_all_supported_types(self):
        rules = (
            Rule("DOMAIN", "example.com", "original"),
            Rule("DOMAIN-SUFFIX", "example.org", "original"),
            Rule("IP-CIDR", "192.0.2.0/24", "original"),
            Rule("IP-CIDR6", "2001:db8::/32", "original"),
        )
        self.assertEqual(
            render(RuleSet("AI", rules)).splitlines()[1:],
            [
                "host,example.com,AI",
                "host-suffix,example.org,AI",
                "ip-cidr,192.0.2.0/24,AI",
                "ip6-cidr,2001:db8::/32,AI",
            ],
        )
        with self.assertRaisesRegex(ValidationError, "does not support"):
            render(RuleSet("AI", (Rule("UNKNOWN", "x", "original"),)))

    def test_profile_contains_defined_policies_and_final_rule(self):
        build(self.root)
        profile = (self.root / "dist/quantumultx/basic.conf").read_text()
        self.assertNotIn("$rules", profile)
        sections = {}
        section = None
        for line in profile.splitlines():
            if line.startswith("["):
                section = line
                sections[section] = []
            elif line and not line.startswith("#"):
                sections[section].append(line)
        policies = {line.split("=", 1)[1].split(",", 1)[0].strip() for line in sections["[policy]"]}
        for line in sections["[filter_local]"]:
            self.assertIn(line.split(",")[-1], policies | {"direct", "proxy", "reject"})
        self.assertEqual(len(sections["[filter_local]"]), 30)
        self.assertEqual(sections["[filter_local]"][-1], "final,Global")
        self.assertEqual(sections["[server_remote]"], [])
        self.assertIn("static = Proxy, direct, proxy", profile)

    def test_domains_precede_ip_rules_across_categories(self):
        sets = (
            RuleSet("AI", (Rule("IP-CIDR", "192.0.2.0/24", "original"),)),
            RuleSet("Apple", (Rule("DOMAIN", "example.com", "original"),)),
        )
        profile = render_profile(sets, "$rules\n")
        self.assertEqual(
            profile.splitlines(), ["host,example.com,Apple", "ip-cidr,192.0.2.0/24,AI"]
        )

    def test_bad_template_is_reported(self):
        with self.assertRaisesRegex(ValidationError, "invalid Quantumult X template"):
            render_profile((), "$missing")
