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

### Backend — Baseline (FastAPI port 8001)
- [x] Même corrections lifespan + CORS que TRM
- [x] `asyncio.get_event_loop()` → `asyncio.get_running_loop()` dans les routes
- [x] Code mort supprimé : `greedy_place`, `local_search_improve`, `count_conflicts`, `solve`, `__init__` avec `random.seed`
- [x] `model.py` (PyTorch MLP, jamais importé, sans dépendance) supprimé

### Frontend — Vue 3
- [x] Variables d'environnement : `.env` (dev) + `.env.production` (prod)
- [x] Toutes les URLs `localhost:800X` remplacées par `${TRM_BASE}` / `${BASELINE_BASE}`
- [x] `useLocalStorage` pour brouillons et index de brouillon (persistance)
- [x] Support tactile complet (`touchstart`, `touchmove` via `elementFromPoint`)
- [x] Système undo/redo peinture (`Ctrl+Z`, MAX_UNDO = 20)
- [x] Raccourcis clavier : `Enter`/`Espace` → résoudre, `←`/`→` → naviguer solutions, `Échap` → fermer modals
- [x] CSS dupliqué `.main-layout.history-hidden` nettoyé
- [x] Code mort supprimé : `gridDebugInfo`, `measureGridCells`, `windowWidth/Height`, `parseMatrixTextInputPreview`, `availableColors`, `closeWelcomeModal`, `closeHelpModal`, `const size` shadow, délai 500ms benchmark, appel silencieux save-test-image
- [x] `parseMatrixTextInput` extraite dans `src/utils/parseMatrix.js`
- [x] `formatMs` extraite dans `src/utils/format.js`
- [x] `defineExpose` ajouté pour la testabilité

### Infrastructure
- [x] `docker-compose` → `docker compose` (nouvelle syntaxe) dans le Makefile
- [x] Nginx : gzip + cache 30j sur assets statiques
- [x] Vite : code splitting (`vue` et `vueuse` en chunks séparés)
- [x] Nginx : headers sécurité (CSP, HSTS, X-Frame-Options…) + `server_tokens off`
- [x] `TRM/requirements-dev.txt` créé (pytest + pytest-asyncio + httpx)
- [x] `baseline-8queens/requirements-dev.txt` créé (idem)

### Tests — Frontend (Vitest) — **61 tests**
- [x] Vitest + @vue/test-utils + jsdom installés
- [x] `src/__tests__/setup.js` : mocks globaux (`URL.createObjectURL`, `navigator.clipboard`, `canvas.getContext`)
- [x] `src/__tests__/format.spec.js` : 16 tests — toutes les plages (ns/µs/ms/s), null/undefined
- [x] `src/__tests__/parseMatrix.spec.js` : 12 tests — cas valides, non-carrée, taille < 4, token invalide, valeur < -1, trop de zones, remapping
- [x] `src/__tests__/BenchmarkChart.spec.js` : 14 tests — rendu vide/données, singulier/pluriel, moyenne, tri, tooltip show/hide
- [x] `src/__tests__/App.spec.js` : 19 tests — état initial, initializeZones, isGridComplete, emptyCellsCount, undo/redo, MAX_UNDO

### Tests — Backend TRM (pytest) — **22 tests**
- [x] `TRM/tests/test_solver.py` : 11 tests — solutions valides, compteur, thread-safety, max_iterations
- [x] `TRM/tests/test_routes.py` : 11 tests — health, solve 200/400, extract-matrix 400

### Tests — Backend Baseline (pytest) — **15 tests**
- [x] `baseline-8queens/tests/test_baseline.py` : 8 tests unitaires + 7 tests API — solutions valides, count == TRM, grille impossible, health, solve

### Documentation
- [x] `tailscale.md` : guide complet accès SSH distant via Tailscale
- [x] `TODO.md` : suivi des tâches (ce fichier)

---

## 🔲 Reste à faire

### Tests — E2E Playwright — **35 tests** ✅
- [x] `front/tests/helpers.js` : utilitaires partagés (`dismissWelcome`, `pickColor`, `paintCell`, `paint4x4`)
- [x] `front/tests/painting.spec.js` — 6 tests : peindre/effacer, Ctrl+Z, nouvelle grille, reset, grille complète active Résoudre
- [x] `front/tests/solve-workflow.spec.js` — 9 tests : résolution 4×4, reines affichées, panneau comparaison, navigation solutions, flèches, Enter/Espace, remplissage aléatoire
- [x] `front/tests/import-export.spec.js` — 8 tests : ouverture modal, Échap, Annuler, matrice valide charge grille, active Résoudre, non-carrée erreur, trop petite erreur, vide désactivé
- [x] `front/tests/drafts.spec.js` — 7 tests : brouillon initial, création, actif, changement, suppression, persistance localStorage, taille affichée
- [x] `front/tests/error-handling.spec.js` — 5 tests : erreur réseau, 500, 0 solutions, grille incomplète désactive Résoudre, titre bouton avec nb cases vides

### Infrastructure
- [ ] `docker-compose.yml` (dev) : ajouter `healthcheck` sur les 3 services (optionnel)
- [ ] `docker-compose.prod.yml` : ajouter `healthcheck` sur nginx + backends (optionnel)

### Documentation
- [x] `documentation/` : architecture complète (technique + utilisateurs × 3 services)
  - [x] `documentation/README.md` — sommaire général + architecture + commandes
  - [x] `documentation/technique/trm/` — solver, routes, models, logger (4 fichiers)
  - [x] `documentation/technique/baseline/` — greedy_model, routes (2 fichiers)
  - [x] `documentation/technique/frontend/` — App.vue, BenchmarkChart, utils (3 fichiers)
  - [x] `documentation/utilisateurs/trm/` — endpoints TRM avec exemples cURL
  - [x] `documentation/utilisateurs/baseline/` — endpoints Baseline
  - [x] `documentation/utilisateurs/frontend/` — grille, brouillons, import, benchmark, raccourcis (5 fichiers)
- [ ] `README.md` (racine) : mettre à jour pour pointer vers `documentation/`
