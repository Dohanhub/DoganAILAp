"""
Seed the compliance database from YAML policy files in config/policies.

Creates ComplianceStandard entries (one per file) and Control entries for each control found.
"""
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml

from app.database import SessionLocal
from app import models


def find_controls(doc: Any) -> Iterable[Dict[str, Any]]:
    """Try to extract a list of controls from a YAML document with flexible schemas."""
    if isinstance(doc, dict):
        # Common patterns
        for key in ("controls", "Controls", "CONTROL_LIST", "control_items"):
            if key in doc and isinstance(doc[key], list):
                for item in doc[key]:
                    if isinstance(item, dict):
                        yield item
        # Nested search
        for v in doc.values():
            yield from find_controls(v)
    elif isinstance(doc, list):
        for item in doc:
            yield from find_controls(item)


def normalize_control(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize control fields to our model columns."""
    cid = (
        item.get("control_id")
        or item.get("ControlId")
        or item.get("id")
        or item.get("ID")
        or item.get("number")
    )
    title = item.get("title") or item.get("Title") or item.get("name") or item.get("Name") or "Untitled"
    desc = item.get("description") or item.get("Description") or item.get("details")
    mandatory = bool(item.get("is_mandatory", True))
    return {"control_id": str(cid) if cid is not None else title, "title": str(title), "description": desc, "is_mandatory": mandatory}


def seed_from_policies(policies_dir: Path) -> Dict[str, int]:
    db = SessionLocal()
    try:
        created_regs = 0
        created_standards = 0
        created_controls = 0
        for path in sorted(policies_dir.glob("*.y*ml")):
            # Use filename as standard name and version if embedded
            stem = path.stem
            # Parse name@version in filename if present
            if "@" in stem:
                name, version = stem.split("@", 1)
            else:
                name, version = stem, "1.0"
            # Create or get standard
            std = db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == name).first()
            if not std:
                std = models.ComplianceStandard(name=name, version=version, description=f"Seeded from {path.name}")
                # Try link regulator
                reg = db.query(models.Regulator).filter(models.Regulator.name == name).first()
                if not reg:
                    reg = models.Regulator(name=name)
                    db.add(reg)
                    db.flush()
                    created_regs += 1
                std.regulator_id = reg.id
                db.add(std)
                db.commit()
                db.refresh(std)
                created_standards += 1
            else:
                # Update version/description if changed
                changed = False
                if std.version != version:
                    std.version = version
                    changed = True
                if not std.description:
                    std.description = f"Seeded from {path.name}"
                    changed = True
                # Ensure regulator link
                if not std.regulator_id:
                    reg = db.query(models.Regulator).filter(models.Regulator.name == name).first()
                    if not reg:
                        reg = models.Regulator(name=name)
                        db.add(reg)
                        db.flush()
                        created_regs += 1
                    std.regulator_id = reg.id
                    changed = True
                if changed:
                    db.add(std)
                    db.commit()

            # Parse YAML and insert controls
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            for raw in find_controls(data):
                norm = normalize_control(raw)
                exists = (
                    db.query(models.Control)
                    .filter(models.Control.standard_id == std.id, models.Control.control_id == norm["control_id"])
                    .first()
                )
                if exists:
                    continue
                ctrl = models.Control(
                    standard_id=std.id,
                    control_id=norm["control_id"],
                    title=norm["title"],
                    description=norm.get("description"),
                    is_mandatory=norm.get("is_mandatory", True),
                )
                db.add(ctrl)
                created_controls += 1
            db.commit()
        print("Seeding completed.")
        return {"regulators": created_regs, "standards": created_standards, "controls": created_controls}
    finally:
        db.close()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    policies = root / "config" / "policies"
    if not policies.exists():
        print(f"Policies directory not found: {policies}")
        return
    res = seed_from_policies(policies)
    print(res)


if __name__ == "__main__":
    main()
