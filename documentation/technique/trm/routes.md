# Routes API TRM

`TRM/api/routes.py`

---

## POST /api/solve

Résout la grille en appelant `QueensSolver.solve()` dans un thread séparé via `asyncio.run_in_executor`.

```python
@router.post("/solve", response_model=Solution)
async def solve(grid: GridInput):
```

**Flux d'exécution :**
1. Valide le nombre de lignes (`len(grid.zones) != grid.size` → 400)
2. Valide le nombre de colonnes par ligne
3. Exécute `solver.solve()` dans `loop.run_in_executor(None, ...)` pour ne pas bloquer la boucle asyncio
4. Calcule `solutions_per_second` et retourne un objet `Solution`

**Note :** `asyncio.get_running_loop()` est utilisé (et non l'obsolète `get_event_loop()`).

---

## POST /api/extract-matrix

Extrait une grille de zones depuis une image uploadée.

```python
@router.post("/extract-matrix", response_model=ExtractedMatrix)
async def extract_matrix(file: UploadFile = File(...)):
```

**Flux d'exécution :**
1. Vérifie le `content_type` : accepte uniquement `image/png`, `image/jpeg`, `image/jpg`, `image/gif`
2. Lit les bytes de l'image
3. Délègue à `utils.image_processor.extract_matrix_from_image(image_data)`
4. Retourne `ExtractedMatrix` avec le score de confiance

---

## GET /api/health

```python
@router.get("/health")
async def health():
    return {"status": "healthy", "service": "TRM Solver", "max_iterations": MAX_ITERATIONS}
```

Utilisé par les health checks et le monitoring.

---

## Configuration du routeur

```python
app.include_router(api_router, prefix="/api", tags=["solver"])
```

Tous les endpoints sont accessibles sous `/api/`.

---

[← solver.md](./solver.md) | [Modèles →](./models.md) | [Sommaire TRM](./README.md)
