"""
Baseline Queens Solver API - Modèle heuristique léger (sans PyTorch)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="Baseline Queens Solver API",
    description="Modèle heuristique (greedy + local search) pour la résolution des N-Reines",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
