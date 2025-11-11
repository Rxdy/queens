"""
Configuration de l'application TRM Solver
"""
import os

# Configuration du serveur
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Configuration du solver
MAX_ITERATIONS = 10_000_000

# Configuration des logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
