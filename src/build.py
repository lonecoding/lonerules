"""Generate every artifact, or verify it with python -m src.build --check."""

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from src.models import PROJECT_ROOT, ValidationError
from src.targets.quantumultx import render, render_profile
from src.validate import validate


def artifacts(root: Path) -> tuple[dict[str, bytes], tuple[str, ...]]:
    result = validate(root)
    files = {
        f"quantumultx/rules/{ruleset.name}.list": render(ruleset).encode("utf-8")
        for ruleset in result.rulesets
    }
    template = (root / "profiles/quantumultx/basic.conf.template").read_text(encoding="utf-8")
    files["quantumultx/basic.conf"] = render_profile(result.rulesets, template).encode("utf-8")
    files["SOURCES.yaml"] = (root / "data/sources.yaml").read_bytes()
    files["LICENSE"] = (root / "LICENSE").read_bytes()
    manifest = {
        "schema_version": 1,
        "target": "quantumultx",
        "categories": {ruleset.name: len(ruleset.rules) for ruleset in result.rulesets},
        "sha256": {
            name: hashlib.sha256(content).hexdigest() for name, content in sorted(files.items())
        },
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return files, result.warnings


def build(root: Path = PROJECT_ROOT, *, check: bool = False) -> tuple[Path, ...]:
    # Complete parsing and rendering before touching existing artifacts.
    files, warnings = artifacts(root)
    for warning in warnings:
        print(f"Warning: {warning}")
    destination = root / "dist"
    if destination.is_symlink() or any(path.is_symlink() for path in destination.rglob("*")):
        raise ValidationError("dist must not contain symbolic links")
    actual = {
        path.relative_to(destination).as_posix(): path
        for path in destination.rglob("*")
        if path.is_file()
    }
    if check:
        changed = [
            name
            for name, content in files.items()
            if name not in actual or actual[name].read_bytes() != content
        ]
        extra = sorted(actual.keys() - files.keys())
        if changed or extra:
            raise ValidationError(
                f"generated files are stale (changed/missing: {sorted(changed)}, extra: {extra}); run python -m src.build"
            )
    else:
        for name, content in sorted(files.items()):
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            # Avoid exposing partially written individual files to local readers.
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
                temporary.write(content)
                temporary_path = Path(temporary.name)
            try:
                os.replace(temporary_path, path)
            finally:
                temporary_path.unlink(missing_ok=True)
        for name in actual.keys() - files.keys():
            actual[name].unlink()
    return tuple(destination / name for name in sorted(files))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail if dist differs; do not write files"
    )
    args = parser.parse_args()
    try:
        paths = build(check=args.check)
    except (OSError, UnicodeError, ValidationError) as error:
        parser.exit(1, f"Build failed: {error}\n")
    print(f"{'Verified' if args.check else 'Built'} {len(paths)} files in dist/")


if __name__ == "__main__":
    main()
