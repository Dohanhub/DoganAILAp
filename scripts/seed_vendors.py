"""
Seed vendors from YAML files in config/vendors.
"""
from pathlib import Path
import yaml
from app.database import SessionLocal
from app import models


def main() -> None:
    db = SessionLocal()
    try:
        root = Path(__file__).resolve().parents[1]
        vdir = root / 'config' / 'vendors'
        if not vdir.exists():
            print(f"Vendors directory missing: {vdir}")
            return
        for f in sorted(vdir.glob('*.y*ml')):
            try:
                data = yaml.safe_load(f.read_text(encoding='utf-8')) or {}
            except Exception:
                continue
            name = data.get('name') or f.stem
            category = data.get('category') or data.get('type')
            website = data.get('website') or data.get('url')
            contact = data.get('contact_email') or data.get('contact')
            desc = data.get('description')
            exists = db.query(models.Vendor).filter(models.Vendor.name == name).first()
            if exists:
                continue
            v = models.Vendor(name=name, category=category, website=website, contact_email=contact, description=desc)
            db.add(v)
        db.commit()
        print('Vendor seeding complete')
    finally:
        db.close()


if __name__ == '__main__':
    main()

