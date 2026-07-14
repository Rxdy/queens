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

# CORS — liste d'origines séparées par virgule, "*" par défaut (dev)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Fichier des statistiques globales agrégées (monté sur un volume persistant en prod)
STATS_FILE_PATH = os.getenv("STATS_FILE_PATH", "/app/data/stats.json")
