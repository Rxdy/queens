# Queens Game Solveur — TODO

## ✅ Terminé

### Backend — TRM (FastAPI port 8000)
- [x] Mutable state solver corrigé (`iterations` local → thread-safe)
- [x] `asyncio.get_event_loop()` → `asyncio.get_running_loop()`
- [x] `@app.on_event` → `lifespan` context manager
- [x] CORS : suppression `allow_credentials=True` incompatible avec `allow_origins=["*"]`
- [x] Logger : garde `hasHandlers()` pour éviter les doublons de handlers (hot reload)
- [x] Endpoint mort `/api/stats` supprimé (lisait `data/summary.json` inexistant, jamais appelé)
- [x] Endpoint mort `/save-test-image` supprimé
- [x] Imports morts (`json`, `Path`, `os`) nettoyés
- [x] `solver_new.py` (doublon non tracké) supprimé
- [x] **Rate limiting** : `slowapi` sur `/api/solve` (30 req/min/IP, 429 automatique)
- [x] **CORS restrictif** : `allow_origins` piloté par `CORS_ORIGINS` env var

### Backend — Baseline (FastAPI port 8001)
- [x] Même corrections lifespan + CORS que TRM
- [x] `asyncio.get_event_loop()` → `asyncio.get_running_loop()` dans les routes
- [x] Code mort supprimé : `greedy_place`, `local_search_improve`, `count_conflicts`, `solve`, `__init__` avec `random.seed`
- [x] `model.py` (PyTorch MLP, jamais importé, sans dépendance) supprimé
- [x] **Rate limiting** : `slowapi` sur `/api/solve` (30 req/min/IP, 429 automatique)

### Frontend — Vue 3
- [x] Variables d'environnement : `.env` (dev) + `.env.production` (prod)
- [x] Toutes les URLs hardcodées remplacées par `${TRM_BASE}` / `${BASELINE_BASE}`
- [x] `useLocalStorage` pour brouillons et historique benchmark (persistance, cap 100)
- [x] Support tactile complet (`touchstart`, `touchmove` via `elementFromPoint`)
- [x] Système undo/redo peinture (`Ctrl+Z`, MAX_UNDO = 20)
- [x] Raccourcis clavier : `Enter`/`Espace` → résoudre, `←`/`→` → naviguer solutions, `Échap` → fermer modals
- [x] Code mort supprimé, `parseMatrixTextInput` et `formatMs` extraites dans `src/utils/`
- [x] **Aria labels** sur les 9 boutons toolbar + `role="toolbar"` sur le conteneur
- [x] **Découpage App.vue** (3360 → 1966 lignes) : extraction de `HelpWelcomeModal.vue`, `HistoryPanel.vue`, `ImportModal.vue`
- [x] **BenchmarkChart** : tooltip migré de SVG vers `<div>` HTML (positionnement correct, z-index, plus jamais masqué)
- [x] **Vite proxy** : `/api/` → TRM, `/baseline/` → Baseline via noms de services Docker (fonctionne derrière tunnel Cloudflare)
- [x] `server.allowedHosts: true` dans `vite.config.js` pour autoriser les hôtes externes

### Qualité de code
- [x] Pydantic v2 : `class Config` → `model_config = ConfigDict()` dans les 3 modèles TRM
- [x] HTML valide : `<ul>` extrait du `<p>` dans le modal d'aide
- [x] **ESLint + Prettier** configurés (`eslint.config.js`, `.prettierrc.json`)
- [x] **Ruff** configuré (`pyproject.toml`) pour les deux backends Python
- [x] **Seuils de couverture** : 80 % lignes/fonctions/statements, 70 % branches dans `vitest.config.js`

### Tests — Frontend (Vitest) — **60 tests**
- [x] Vitest + @vue/test-utils + jsdom installés
- [x] `src/__tests__/setup.js` : mocks globaux
- [x] `src/__tests__/format.spec.js` : 16 tests
- [x] `src/__tests__/parseMatrix.spec.js` : 12 tests
- [x] `src/__tests__/BenchmarkChart.spec.js` : 14 tests — dont tooltip show/hide avec les nouvelles classes HTML
- [x] `src/__tests__/App.spec.js` : 18 tests

### Tests — Backend TRM (pytest) — **22 tests**
- [x] `TRM/tests/test_solver.py` : 11 tests
- [x] `TRM/tests/test_routes.py` : 11 tests

### Tests — Backend Baseline (pytest) — **15 tests**
- [x] `baseline-8queens/tests/test_baseline.py` : 8 tests unitaires + 7 tests API

### Infrastructure
- [x] `docker-compose.yml` : healthcheck sur les 3 services, `depends_on: condition: service_healthy`
- [x] Variables `VITE_TRM_PROXY_TARGET` / `VITE_BASELINE_PROXY_TARGET` injectées dans le conteneur queens
- [x] `.github/workflows/test-front.yml` : pipeline CI Vitest à chaque push
- [x] Déploiement Raspberry Pi via `git pull` + `docker compose up -d`

### Documentation
- [x] `tailscale.md` : guide accès SSH distant via Tailscale
- [x] `documentation/` : architecture complète (technique + utilisateurs × 3 services)
- [x] `README.md` : section Documentation avec tableau vers `documentation/`

---

## 💡 Reste à faire

### Qualité de code
- [ ] **Pre-commit hooks** : `husky` + `lint-staged` (JS) / `pre-commit` (Python) pour bloquer les commits qui cassent le lint

### Backend
- [ ] **Logging Baseline** : ajouter le même logger que TRM pour faciliter le debug en production

### Infrastructure
- [ ] **Tunnel Cloudflare permanent** : créer un tunnel nommé avec compte Cloudflare (URL fixe au lieu de `*.trycloudflare.com` qui change à chaque redémarrage)
