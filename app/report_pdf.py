from typing import List, Dict, Any
from datetime import datetime

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    h1 { margin-bottom: 0; }
    .meta { color: #555; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 8px; font-size: 12px; }
    th { background: #f6f6f6; text-align: left; }
    .overdue { color: #b00020; font-weight: bold; }
  </style>
  <title>Compliance Report</title>
  </head>
<body>
  <h1>Compliance Report - {standard}</h1>
  <div class="meta">Generated: {generated}</div>
  <table>
    <thead>
      <tr><th>Control ID</th><th>Title</th><th>Status</th><th>Assessed At</th><th>Next Review</th></tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""


def build_html(standard: str, items: List[Dict[str, Any]]) -> str:
    def esc(s: Any) -> str:
        return (str(s) if s is not None else '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    row_html = []
    for it in items:
        row_html.append(
            f"<tr><td>{esc(it.get('control_id'))}</td><td>{esc(it.get('title'))}</td><td>{esc(it.get('status'))}</td>"
            f"<td>{esc(it.get('assessed_at'))}</td><td class={'\"overdue\"' if it.get('overdue') else ''}>{esc(it.get('next_review_date'))}</td></tr>"
        )
    return HTML_TEMPLATE.format(standard=esc(standard), generated=datetime.utcnow().isoformat(), rows='\n'.join(row_html))


def render_pdf(html: str) -> bytes | None:
    try:
        from weasyprint import HTML  # type: ignore
        pdf = HTML(string=html).write_pdf()
        return pdf
    except Exception:
        return None

