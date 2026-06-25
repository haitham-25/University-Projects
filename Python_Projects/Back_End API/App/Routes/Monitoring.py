from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

metrics = {
    "total_requests": 0,
    "errors": 0,
    "recent_logs": [],
    "response_times": [],
    "endpoint_counts": {}   # NEW: per-endpoint breakdown
}
@router.get("/health")
def health_check():
    """System health endpoint"""
    return {
        "status": "healthy",
        "total_requests": metrics["total_requests"],
        "error_rate": round(metrics["errors"] / metrics["total_requests"] * 100, 1)
        if metrics["total_requests"] > 0 else 0,
    }

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Simple HTML monitoring dashboard"""
    total = metrics["total_requests"]
    errors = metrics["errors"]
    error_rate = round((errors / total * 100), 1) if total > 0 else 0
    avg_rt = round(sum(metrics["response_times"]) / len(metrics["response_times"]), 1) if metrics["response_times"] else 0

    import re as _re
    def _is_error_log(line: str) -> bool:
        m = _re.search(r'-> (\d{3})', line)
        return bool(m and m.group(1)[0] in ('4', '5'))

    logs_html = "".join(
        f'<div class="log-line {"log-err" if _is_error_log(l) else ""}">{l}</div>'
        for l in reversed(metrics["recent_logs"][-30:])
    )

    top_eps = sorted(metrics["endpoint_counts"].items(), key=lambda x: x[1], reverse=True)[:10]
    endpoints_html = "".join(
        f'<div class="log-line"><span style="flex:1;font-family:monospace">{ep}</span><span style="color:#60a5fa;margin-left:12px">{cnt} req</span></div>'
        for ep, cnt in top_eps
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Monitoring Dashboard</title>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="10">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }}
    h1 {{ font-size: 22px; font-weight: 600; margin-bottom: 20px; color: #f8fafc; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }}
    .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
    .card-label {{ font-size: 12px; color: #94a3b8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: .5px; }}
    .card-value {{ font-size: 32px; font-weight: 700; }}
    .blue {{ color: #60a5fa; }} .red {{ color: #f87171; }} .green {{ color: #34d399; }} .amber {{ color: #fbbf24; }}
    h2 {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; color: #cbd5e1; }}
    .log-box {{ background: #1e293b; border-radius: 10px; padding: 16px; border: 1px solid #334155; max-height: 400px; overflow-y: auto; }}
    .log-line {{ font-family: monospace; font-size: 12px; color: #94a3b8; padding: 3px 0; border-bottom: 1px solid #0f172a; }}
    .log-err {{ color: #f87171; }}
    .badge {{ display: inline-block; background: #0f172a; border-radius: 6px; padding: 2px 8px; font-size: 11px; color: #64748b; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <h1>System Dashboard</h1>
  <div class="badge">Auto-refreshes every 10s</div>
  <div class="grid">
    <div class="card"><div class="card-label">Total Requests</div><div class="card-value blue">{total}</div></div>
    <div class="card"><div class="card-label">Total Errors</div><div class="card-value red">{errors}</div></div>
    <div class="card"><div class="card-label">Error Rate</div><div class="card-value {"red" if error_rate > 10 else "green"}">{error_rate}%</div></div>
    <div class="card"><div class="card-label">Avg Response Time</div><div class="card-value amber">{avg_rt}ms</div></div>
  </div>
  <h2>Top Endpoints (by hit count)</h2>
  <div class="log-box" style="margin-bottom:24px">{endpoints_html if endpoints_html else '<div class="log-line">No data yet...</div>'}</div>
  <h2>Recent Requests (latest first)</h2>
  <div class="log-box">{logs_html if logs_html else '<div class="log-line">No requests yet...</div>'}</div>
</body>
</html>"""
    return html

@router.get("/stats")
def get_stats():
    total = metrics["total_requests"]
    avg_rt = round(sum(metrics["response_times"]) / len(metrics["response_times"]), 1) \
             if metrics["response_times"] else 0
    top_endpoints = [
        {"endpoint": ep, "count": cnt}
        for ep, cnt in sorted(
            metrics["endpoint_counts"].items(), key=lambda x: x[1], reverse=True
        )[:10]
    ]
    return {
        "total_requests": total,
        "errors": metrics["errors"],
        "error_rate_percent": round(metrics["errors"] / total * 100, 1) if total > 0 else 0,
        "avg_response_time_ms": avg_rt,
        "top_endpoints": top_endpoints,
        "recent_logs": metrics["recent_logs"][-30:],
    }