from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from App.Database import engine, Base
from App.Models import User, Student, AuditLog, Course
from App.Routes import Auth, Students, Monitoring, Courses
from App.Utils.Logger import logger
import time, os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    endpoint = request.url.path
    logger.info(f"{request.method} {endpoint} -> {response.status_code} ({duration}ms)")
    Monitoring.metrics["endpoint_counts"][endpoint] = Monitoring.metrics["endpoint_counts"].get(endpoint, 0) + 1
    Monitoring.metrics["total_requests"] += 1
    Monitoring.metrics["response_times"].append(duration)
    if len(Monitoring.metrics["response_times"]) > 1000:
        Monitoring.metrics["response_times"] = Monitoring.metrics["response_times"][-1000:]
    if response.status_code >= 400:
        Monitoring.metrics["errors"] += 1
    Monitoring.metrics["recent_logs"].append(f"{request.method} {endpoint} -> {response.status_code} ({duration}ms)")
    if len(Monitoring.metrics["recent_logs"]) > 100:
        Monitoring.metrics["recent_logs"] = Monitoring.metrics["recent_logs"][-100:]
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(Auth.router)
app.include_router(Students.router)
app.include_router(Courses.router)
app.include_router(Monitoring.router)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/")
def root():
    return {"message": "Student Management API running", "docs": "/docs", "dashboard": "/monitoring/dashboard"}
