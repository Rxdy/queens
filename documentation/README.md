# Documentation — Queens Game Solveur

Bienvenue dans la documentation du projet. Deux sections sont disponibles selon ton profil.

---

## Sections

### [Documentation Technique](./technique/README.md)
Pour comprendre le fonctionnement interne du projet : algorithmes, composants, fonctions.

| Service | Contenu |
|---|---|
| [TRM](./technique/trm/README.md) | Solveur bitset, routes API, modèles Pydantic, logger |
| [Baseline](./technique/baseline/README.md) | Solveur naïf exhaustif, routes API |
| [Frontend](./technique/frontend/README.md) | App.vue, BenchmarkChart.vue, utilitaires |

---

### [Documentation Utilisateur](./utilisateurs/README.md)
Pour utiliser le projet : endpoints API, fonctionnalités de l'interface.

| Service | Contenu |
|---|---|
| [API TRM](./utilisateurs/trm/README.md) | Endpoints REST du solveur optimisé |
| [API Baseline](./utilisateurs/baseline/README.md) | Endpoints REST du solveur naïf |
| [Interface](./utilisateurs/frontend/README.md) | Grille, brouillons, import, benchmark, raccourcis |

---

## Architecture du projet

```
queens/
├── TRM/                    # Service FastAPI — solveur optimisé (port 8000)
├── baseline-8queens/       # Service FastAPI — solveur naïf (port 8001)
├── front/                  # Application Vue 3 (Vite)
├── docker-compose.yml      # Dev
├── docker-compose.prod.yml # Production (Raspberry Pi)
└── documentation/          # Ce dossier
```

## Lancer le projet

```bash
# Développement
docker compose up

# Production
docker compose -f docker-compose.prod.yml up -d
```

## Lancer les tests

```bash
# Frontend (Vitest)
cd front && npm run test:run

# Backend TRM (pytest)
cd TRM && python3 -m pytest tests/ -v

# Backend Baseline (pytest)
cd baseline-8queens && python3 -m pytest tests/ -v
```
