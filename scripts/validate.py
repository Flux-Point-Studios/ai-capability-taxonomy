#!/usr/bin/env python3
"""Validate taxonomy entries against the JSON Schema and check registry consistency.

Exit code 0 on success, 1 on any failure. Designed for CI but safe to run locally.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "entry.schema.json"
TAXONOMY_DIR = REPO_ROOT / "taxonomy"
REGISTRY_PATH = REPO_ROOT / "registry.json"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
REQUIRED_SECTIONS = ("Definition", "Positive example", "Negative example", "References")


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def parse_entry(path: Path) -> tuple[dict, str] | None:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail(f"{path.name}: missing YAML frontmatter (must start with --- ... ---)")
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        fail(f"{path.name}: invalid YAML frontmatter: {exc}")
        return None
    if not isinstance(data, dict):
        fail(f"{path.name}: frontmatter must be a YAML mapping")
        return None
    # YAML coerces bare ISO dates to datetime.date; the schema expects strings.
    for key in ("introduced", "deprecated"):
        value = data.get(key)
        if isinstance(value, dt.date):
            data[key] = value.isoformat()
    return data, match.group(2)


def check_sections(path: Path, body: str) -> bool:
    missing = [s for s in REQUIRED_SECTIONS if f"## {s}" not in body]
    if missing:
        fail(f"{path.name}: missing required section(s): {', '.join(missing)}")
        return False
    return True


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    entry_files = sorted(TAXONOMY_DIR.glob("*.md"))
    if not entry_files:
        fail("no entries found in taxonomy/")
        return 1

    on_disk: dict[str, dict] = {}
    ok = True

    for path in entry_files:
        parsed = parse_entry(path)
        if parsed is None:
            ok = False
            continue
        frontmatter, body = parsed

        errors = sorted(validator.iter_errors(frontmatter), key=lambda e: e.path)
        for err in errors:
            location = "/".join(str(p) for p in err.absolute_path) or "<root>"
            fail(f"{path.name}: schema violation at {location}: {err.message}")
            ok = False

        entry_id = frontmatter.get("id")
        if isinstance(entry_id, str):
            expected_name = f"{entry_id}.md"
            if path.name != expected_name:
                fail(f"{path.name}: filename does not match id ({expected_name} expected)")
                ok = False
            if entry_id in on_disk:
                fail(f"{path.name}: duplicate id {entry_id}")
                ok = False
            on_disk[entry_id] = frontmatter

        if not check_sections(path, body):
            ok = False

    if not REGISTRY_PATH.exists():
        fail("registry.json missing")
        return 1

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    required_registry_keys = {"version", "updated", "entries"}
    missing_keys = required_registry_keys - registry.keys()
    if missing_keys:
        fail(f"registry.json: missing key(s): {', '.join(sorted(missing_keys))}")
        return 1

    registry_entries = {e["id"]: e for e in registry["entries"]}

    disk_ids = set(on_disk.keys())
    registry_ids = set(registry_entries.keys())

    only_disk = disk_ids - registry_ids
    only_registry = registry_ids - disk_ids
    if only_disk:
        fail(f"registry.json missing entries present on disk: {sorted(only_disk)}")
        ok = False
    if only_registry:
        fail(f"registry.json lists entries with no file on disk: {sorted(only_registry)}")
        ok = False

    for entry_id in disk_ids & registry_ids:
        disk = on_disk[entry_id]
        reg = registry_entries[entry_id]
        for field in ("name", "severity", "status"):
            if disk.get(field) != reg.get(field):
                fail(
                    f"registry.json: {entry_id}.{field} disagrees with file "
                    f"(file={disk.get(field)!r}, registry={reg.get(field)!r})"
                )
                ok = False

    if ok:
        print(f"OK: {len(on_disk)} entries validated, registry consistent.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
