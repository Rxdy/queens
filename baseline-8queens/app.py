"""
Baseline Queens Solver API - Modèle heuristique léger (sans PyTorch)
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.limiter import limiter
from api.routes import router

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Baseline Queens Solver API",
    description="Modèle heuristique (greedy + local search) pour la résolution des N-Reines",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html lang="fr">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Baseline Queens Solver API</title>
            <style>
              body {
                margin: 0;
                font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                min-height: 100vh;
                background: linear-gradient(135deg, #020617 0%, #0f172a 100%);
                color: #f8fafc;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 2rem;
              }
              .page {
                max-width: 900px;
                width: 100%;
                border-radius: 28px;
                background: rgba(15, 23, 42, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 30px 90px rgba(15, 23, 42, 0.35);
                padding: 2.5rem;
              }
              h1 {
                margin: 0;
                font-size: clamp(2.4rem, 4vw, 3.4rem);
              }
              h2 {
                margin: 1.5rem 0 0.75rem;
                font-size: 1.25rem;
              }
              p {
                line-height: 1.8;
                color: #cbd5e1;
              }
              .status {
                margin: 1.75rem auto 0;
                display: inline-flex;
                gap: 0.75rem;
                flex-wrap: wrap;
              }
              .chip {
                padding: 0.7rem 1rem;
                border-radius: 999px;
                font-weight: 700;
                letter-spacing: 0.02em;
              }
              .chip.up {
                background: rgba(34, 197, 94, 0.18);
                color: #22c55e;
              }
              .chip.down {
                background: rgba(248, 113, 113, 0.16);
                color: #ef4444;
              }
              .links {
                margin-top: 2rem;
                display: grid;
                gap: 0.85rem;
                justify-items: center;
              }
              .link-button {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 0.95rem 1.4rem;
                border-radius: 999px;
                border: none;
                background: linear-gradient(135deg, #ec4899, #6366f1);
                color: #fff;
                text-decoration: none;
                font-weight: 700;
                transition: transform 0.2s ease;
              }
              .link-button:hover { transform: translateY(-2px); }
              code {
                background: rgba(148, 163, 184, 0.16);
                color: #e2e8f0;
                padding: 0.2rem 0.45rem;
                border-radius: 0.45rem;
              }
            </style>
          </head>
          <body>
            <div class="page">
              <h1>Baseline Queens Solver API</h1>
              <p>Service backend heuristique pour les N-Reines avec contraintes de zones.</p>
              <div class="status">
                <span class="chip up">UP</span>
                <span class="chip">Port <code>8001</code></span>
                <span class="chip">Type <code>Baseline</code></span>
              </div>
              <div class="links">
                <a class="link-button" href="/docs">Ouvrir la documentation Swagger</a>
              </div>
            </div>
          </body>
        </html>
        """
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        timeout_keep_alive=0,
        timeout_graceful_shutdown=None,
    )
