import os
import csv
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .database import SessionLocal
from . import models

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_session() -> Session:
    return SessionLocal()


def seed_admin(db: Session) -> None:
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    enable = os.getenv("ENABLE_ADMIN_SEED", "true").lower() in {"1", "true", "yes"}
    if not enable:
        return
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return
    hpw = pwd_ctx.hash(password)
    db.add(models.User(email=email, hashed_password=hpw, full_name="Admin User", is_superuser=True, role="admin"))
    db.commit()


def seed_standards_and_controls(db: Session) -> None:
    standards = [
        {"name": "NCA", "version": "2.0", "description": "Saudi NCA - ECC"},
        {"name": "SAMA", "version": "2023", "description": "SAMA Cybersecurity"},
        {"name": "ISO27001", "version": "2022", "description": "ISMS"},
    ]
    for std in standards:
        if not db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == std["name"]).first():
            db.add(models.ComplianceStandard(**std))
    db.commit()

    nca = db.query(models.ComplianceStandard).filter(models.ComplianceStandard.name == "NCA").first()
    if nca:
        base_controls = [
            {"control_id": "NCA-1.1.1", "title": "Information Security Policy", "is_mandatory": True},
            {"control_id": "NCA-1.1.2", "title": "Policy Review", "is_mandatory": True},
            {"control_id": "NCA-2.1.1", "title": "Asset Inventory", "is_mandatory": True},
        ]
        for c in base_controls:
            if not db.query(models.Control).filter(models.Control.control_id == c["control_id"]).first():
                db.add(models.Control(standard_id=nca.id, **c))
        db.commit()


def seed_regulators(db: Session) -> None:
    # Minimal set to make UI meaningful
    regs = [
        ("NCA", "Saudi National Cybersecurity Authority", "KSA"),
        ("SDAIA", "Saudi Data & AI Authority", "KSA"),
        ("SAMA", "Saudi Central Bank", "KSA"),
        ("ZATCA", "Zakat, Tax and Customs Authority", "KSA"),
        ("SFDA", "Saudi Food & Drug Authority", "KSA"),
    ]
    for name, full, country in regs:
        if not db.query(models.Regulator).filter(models.Regulator.name == name).first():
            db.add(models.Regulator(name=name, country=country, sector=None, website=None))
    db.commit()


def seed_vendors(db: Session) -> None:
    vendors = [
        ("ZATCA", "Gov API"),
        ("SFDA", "Gov API"),
        ("NPHIES", "Health Integration"),
        ("OPENBANK", "Banking"),
        ("UNIFONIC", "CPaaS"),
    ]
    for name, cat in vendors:
        if not db.query(models.Vendor).filter(models.Vendor.name == name).first():
            db.add(models.Vendor(name=name, category=cat, website=None, contact_email=None))
    db.commit()


def seed_connectors_csv(db: Session, csv_path: str) -> int:
    created = 0
    if not os.path.exists(csv_path):
        return created
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vcode = (row.get("vendor_id") or row.get("vendor") or row.get("vendor_code") or "").strip()
            rcode = (row.get("reg_id") or row.get("regulator") or row.get("reg_code") or "").strip()
            if not vcode or not rcode:
                continue
            v = db.query(models.Vendor).filter(models.Vendor.name == _normalize_vendor(vcode)).first()
            if not v:
                v = models.Vendor(name=_normalize_vendor(vcode))
                db.add(v)
                db.flush()
            r = db.query(models.Regulator).filter(models.Regulator.name == _normalize_reg(rcode)).first()
            if not r:
                r = models.Regulator(name=_normalize_reg(rcode), country="KSA")
                db.add(r)
                db.flush()
            # Create connector if not exists
            cname = f"{v.name}-{r.name}"
            exists = (
                db.query(models.Connector)
                .filter(models.Connector.name == cname)
                .first()
            )
            if not exists:
                db.add(models.Connector(name=cname, category="integration", vendor_id=v.id, regulator_id=r.id, description=row.get("trigger") or None))
                created += 1
    db.commit()
    return created


def seed_regulators_from_csv(db: Session, csv_path: str) -> int:
    created = 0
    if not os.path.exists(csv_path):
        return created
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("reg_id") or row.get("code") or row.get("name") or "").strip()
            if not code:
                continue
            code = _normalize_reg(code)
            if not db.query(models.Regulator).filter(models.Regulator.name == code).first():
                db.add(models.Regulator(name=code, country=(row.get("country") or "KSA")))
                created += 1
    db.commit()
    return created


def seed_vendors_from_csv(db: Session, csv_path: str) -> int:
    created = 0
    if not os.path.exists(csv_path):
        return created
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid = (row.get("vendor_id") or row.get("vendor") or "").strip()
            if not vid:
                continue
            name = _normalize_vendor(vid)
            if not db.query(models.Vendor).filter(models.Vendor.name == name).first():
                db.add(models.Vendor(name=name, category=row.get("category") or None, website=row.get("dev_portal") or None))
                created += 1
    db.commit()
    return created


def _normalize_vendor(code: str) -> str:
    # Accept both plain names and codes like V-ZATCA
    code = code.strip()
    if code.upper().startswith("V-"):
        return code.split("-", 1)[1].upper()
    return code.upper()


def _normalize_reg(code: str) -> str:
    code = code.strip()
    if code.upper().startswith("REG-"):
        return code.split("-", 1)[1].upper()
    return code.upper()


def _dataset_dir() -> Optional[str]:
    # Prefer explicit mount path, else local repo dataset/
    for p in [os.getenv("SEED_DATASET_DIR"), "/seed", os.path.join(os.getcwd(), "dataset")]:
        if p and os.path.isdir(p):
            return p
    return None


def main() -> None:
    db = _get_session()
    try:
        seed_standards_and_controls(db)
        seed_regulators(db)
        seed_vendors(db)
        ddir = _dataset_dir()
        if ddir:
            seed_regulators_from_csv(db, os.path.join(ddir, "regulators.csv"))
            seed_vendors_from_csv(db, os.path.join(ddir, "vendors.csv"))
            seed_connectors_csv(db, os.path.join(ddir, "vendor_regulator_map.csv"))
        else:
            # Fallback to root CSV if present
            csv_file = os.path.join(os.getcwd(), "vendor_regulator_map.csv")
            seed_connectors_csv(db, csv_file)
        seed_admin(db)
        print("Seeding completed ✅")
    finally:
        db.close()


if __name__ == "__main__":
    main()
