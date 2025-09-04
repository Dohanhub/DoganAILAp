
from .core.database import engine, SessionLocal
from . import models

def init_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        standards = [{'name': 'NCA', 'version': '2.0', 'description': 'National Cybersecurity Authority - Essential Cybersecurity Controls'}, {'name': 'SAMA', 'version': '2023', 'description': 'SAMA Cybersecurity Framework'}, {'name': 'ISO27001', 'version': '2022', 'description': 'Information security management'}]
        for std in standards:
            if (not db.query(models.ComplianceStandard).filter_by(name=std['name']).first()):
                db_std = models.ComplianceStandard(**std)
                db.add(db_std)
        nca_standard = db.query(models.ComplianceStandard).filter_by(name='NCA').first()
        if nca_standard:
            nca_controls = [{'control_id': 'NCA-1.1.1', 'title': 'Information Security Policy', 'is_mandatory': True}, {'control_id': 'NCA-1.1.2', 'title': 'Review of Information Security Policy', 'is_mandatory': True}, {'control_id': 'NCA-2.1.1', 'title': 'Asset Inventory', 'is_mandatory': True}]
            for ctrl in nca_controls:
                if (not db.query(models.Control).filter_by(control_id=ctrl['control_id']).first()):
                    db_ctrl = models.Control(standard_id=nca_standard.id, **{k: v for (k, v) in ctrl.items() if (k != 'control_id')}, control_id=ctrl['control_id'])
                    db.add(db_ctrl)
        db.commit()
        print('Database initialized successfully!')
    except Exception as e:
        print(f'Error initializing database: {e}')
        db.rollback()
    finally:
        db.close()
if (__name__ == '__main__'):
    init_db()
