"""
Application principale TRM Solver - Tiny Recursive Model

Architecture Clean:
- api/ : Endpoints et modèles API
- core/ : Logique métier (solveur, config)
- utils/ : Utilitaires (logging, helpers)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from utils.logger import setup_logging
from core.config import HOST, PORT, LOG_LEVEL

# Configuration du logging
logger = setup_logging(LOG_LEVEL)

# Création de l'application FastAPI
app = FastAPI(
    title="TRM Solver API",
    description="Tiny Recursive Model pour résoudre le problème des N-Reines avec contraintes de zones",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, permettre toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes API
app.include_router(api_router, prefix="/api", tags=["solver"])

# Route de santé à la racine
@app.get("/")
async def root():
    """Point d'entrée principal"""
    return {
        "service": "TRM Solver",
        "description": "Tiny Recursive Model pour les N-Reines",
        "version": "2.0.0",
        "architecture": "Clean Architecture"
    }

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    logger.info("🚀 TRM Solver démarré")
    logger.info(f"📡 Écoute sur {HOST}:{PORT}")
    logger.info("� Architecture modulaire activée")

@app.on_event("shutdown")
async def shutdown_event():
    """Événement d'arrêt de l'application"""
    logger.info("🛑 TRM Solver arrêté")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, reload=True)