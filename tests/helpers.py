"""Isolated project fixtures; tests never modify repository rule sources."""

import shutil
import tempfile
import unittest
from pathlib import Path

from src.models import PROJECT_ROOT


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        shutil.copytree(PROJECT_ROOT / "data", self.root / "data")
        if (PROJECT_ROOT / "profiles").exists():
            shutil.copytree(PROJECT_ROOT / "profiles", self.root / "profiles")

    def write_ai(self, text: str):
        (self.root / "data/rules/ai.yaml").write_text(text, encoding="utf-8")
