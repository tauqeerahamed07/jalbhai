import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.crud import seed_if_empty
from app.routers import assess, wards, report

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="JalRakshak API",
    description="RTRWH/AR assessment API for Chennai, India.",
    version="0.1.0",
)

# Wide open for the hackathon demo - explicitly no auth/rate limiting per scope.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assess.router)
app.include_router(wards.router)
app.include_router(report.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "service": "JalRakshak API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
