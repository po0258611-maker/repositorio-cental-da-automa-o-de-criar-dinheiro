"""
AME - Main FastAPI Application
Assembles all APIs: /agents, /tasks, /experiments, /products, /marketing, /sales, /finance, /analytics, /memory, /integrations, /system, /health
"""
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
from pathlib import Path

from app.core.config import settings
from app.core.database import init_db
from app.core.observability import logger, REQUEST_COUNT, REQUEST_LATENCY, metrics_store
from app.core.security import rate_limit

# Import routers
from app.api import health, agents, tasks, experiments, products, marketing, sales, finance, analytics, memory, integrations, system

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("ame_startup", version="1.0.0", env=settings.ame_env)
    # Init DB
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
    # Start durable task worker
    try:
        from app.core.task_runner import task_runner
        await task_runner.start()
    except Exception as e:
        logger.error("task_runner_start_failed", error=str(e))

    # Register agents
    try:
        from app.core.orchestrator import orchestrator
        from app.agents import register_all
        register_all(orchestrator)
        logger.info("agents_registered", count=len(orchestrator.agents_registry))
    except Exception as e:
        logger.error("agents_register_failed", error=str(e))
    yield
    # Shutdown
    try:
        from app.core.task_runner import task_runner
        await task_runner.stop()
    except Exception as e:
        logger.error("task_runner_stop_failed", error=str(e))
    logger.info("ame_shutdown")

app = FastAPI(
    title="Autonomous Money Engine - AME",
    description="Plataforma de automação empresarial orientada à geração de receita. Loop: OBSERVE → RESEARCH → DISCOVER → VALIDATE → DECIDE → BUILD → PUBLISH → DISTRIBUTE → SELL → MEASURE → LEARN → OPTIMIZE → REINVEST",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware: observability
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    endpoint = request.url.path
    # Metrics
    try:
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        metrics_store.inc(f"{request.method} {endpoint}")
        metrics_store.record_latency(endpoint, latency)
    except:
        pass
    response.headers["X-AME-Latency"] = str(round(latency, 4))
    response.headers["X-AME-Version"] = "1.0.0"
    return response

# Routers
app.include_router(health.router, tags=["health"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(marketing.router, prefix="/marketing", tags=["marketing"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(finance.router, prefix="/finance", tags=["finance"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])
app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
app.include_router(system.router, prefix="/system", tags=["system"])

# Root
@app.get("/", response_class=HTMLResponse, tags=["root"])
def root():
    # Serve dashboard HTML if exists, else redirect info
    dashboard_path = Path("dashboard/index.html")
    if dashboard_path.exists():
        return dashboard_path.read_text(encoding="utf-8")
    return """
    <html><head><meta http-equiv="refresh" content="0; url=/docs"></head><body>
    <h1>AME - Autonomous Money Engine</h1>
    <p><a href='/docs'>API Docs</a> | <a href='/health'>Health</a> | <a href='/dashboard'>Dashboard</a></p>
    </body></html>
    """

@app.get("/dashboard", response_class=HTMLResponse, tags=["root"])
def dashboard_redirect():
    # Proxy to new dashboard if exists
    p = Path("dashboard/index.html")
    if p.exists():
        return p.read_text(encoding="utf-8")
    return "<html><body><h1>Dashboard em /dashboard - use app/main.py</h1><a href='/docs'>Docs</a></body></html>"

@app.get("/api")
def api_info():
    return {
        "name": "Autonomous Money Engine",
        "version": "1.0.0",
        "mode": settings.ame_env,
        "endpoints": ["/agents","/tasks","/experiments","/products","/marketing","/sales","/finance","/analytics","/memory","/integrations","/system","/health"],
        "loop": ["OBSERVE","RESEARCH","DISCOVER","VALIDATE","DECIDE","BUILD","PUBLISH","DISTRIBUTE","SELL","MEASURE","LEARN","OPTIMIZE","REINVEST","REPEAT"],
        "docs": "/docs"
    }

# Legacy compatibility: mount old dashboard/app.py routes
@app.get("/legacy/dashboard", tags=["legacy"])
def legacy_dashboard():
    return {"message": "Legacy dashboard at /dashboard - new AME dashboard is at / and /docs"}

# Error handlers
@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found", "path": str(request.url.path), "hint": "Check /docs for available endpoints"})

@app.exception_handler(500)
async def internal_error(request: Request, exc):
    logger.error("internal_error", path=str(request.url.path), error=str(exc))
    return JSONResponse(status_code=500, content={"error": "Internal server error", "request_id": str(time.time())})
