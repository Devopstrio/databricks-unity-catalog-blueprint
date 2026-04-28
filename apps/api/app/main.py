import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pythonjsonlogger import jsonlogger

# Logger setup
logger = logging.getLogger("governance-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Databricks UC Hub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/catalogs")
def get_catalogs():
    return [
        {"id": "cat-fin-prod", "name": "finance_prod", "owner": "Finance Data Team", "type": "MANAGED", "schemas": 12, "health_score": 0.98},
        {"id": "cat-mkt-staging", "name": "marketing_staging", "owner": "Marketing Lead", "type": "EXTERNAL", "schemas": 4, "health_score": 0.85},
        {"id": "cat-sales-dev", "name": "sales_dev", "owner": "Sales Engineering", "type": "MANAGED", "schemas": 8, "health_score": 0.92}
    ]

@app.get("/lineage")
def get_lineage_summary():
    return {
        "total_nodes": 1450,
        "total_edges": 4200,
        "critical_paths": 12,
        "last_sync": "2026-04-28 14:00:00"
    }

@app.get("/scores/summary")
def get_scores_summary():
    return {
        "global_governance_index": 0.942,
        "policy_violations": 4,
        "stale_assets_detected": 15,
        "adoption_rate": "82%"
    }

@app.get("/dashboard/summary")
def get_dashboard_summary():
    return {
        "total_managed_tables": 4520,
        "active_shares": 14,
        "total_storage_governed": "1.2 PB",
        "avg_query_latency": "140ms"
    }

@app.post("/catalogs")
def create_catalog(name: str, domain: str):
    logger.info(f"Provisioning catalog {name} for domain {domain}")
    return {"status": "Catalog Job Enqueued", "job_id": "job_cat_123"}

@app.post("/grants/apply")
def apply_grants(catalog: str, group: str, permission: str):
    logger.info(f"Applying {permission} on {catalog} for {group}")
    return {"status": "Grant Sync Enqueued", "job_id": "job_grant_456"}
