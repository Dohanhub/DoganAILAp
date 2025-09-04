# Runbook (Gov profile)
- Start API: `uvicorn engine.api:app --host 0.0.0.0 --port 8000`
- Start UI: `streamlit run ui/app.py`
- Evaluate mapping: choose `MAP-GOV-SecurePortal-IBM-Lenovo` and click Evaluate.
- Export audit: use tools/audit_zip.py as needed.
