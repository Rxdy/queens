"""
Configuration de l'application TRM Solver
"""
import os

# Configuration du serveur
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Configuration du solver
MAX_ITERATIONS = 10**18  # Limite très haute (pratiquement illimitée)

# Configuration des logs
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
