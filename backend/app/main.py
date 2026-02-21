"""FastAPI application entry point."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, backtest

app = FastAPI(
    title="Trade_Bot API",
    description="Stock backtesting API with Backtrader",
    version="1.0.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3100").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(backtest.router, prefix="/api", tags=["backtest"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Trade_Bot API", "version": "1.0.0"}
