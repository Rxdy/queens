# Routes API — Baseline

`baseline-8queens/api/routes.py`

---

## POST /api/solve

```python
@router.post("/solve", response_model=BaselineSolution)
async def solve(grid: GridInput):
```

Exécute `QueensGreedyBaseline.solve_exhaustive()` dans un thread via `asyncio.get_running_loop().run_in_executor`.

**Flux :**
1. Appelle `_model.solve_exhaustive(size, zones)` (instance unique au niveau module)
2. Mesure le temps d'exécution avec `time.perf_counter()`
3. Retourne `BaselineSolution` avec `supported=True`

En cas d'exception, retourne `BaselineSolution(supported=False, error=...)` — toujours HTTP 200.

---

## GET /api/health

```python
@router.get("/health")
async def health():
    return {"status": "healthy", "service": "Baseline Queens Solver (Greedy)"}
```

---

## Configuration

```python
app.include_router(router, prefix="/api")
```

En production, Nginx préfixe avec `/baseline/` puis enlève ce préfixe avant de transmettre au service :
```nginx
rewrite ^/baseline(/.*)$ $1 break;
proxy_pass http://baseline-solveur:8001;
```

---

[← greedy_model.md](./greedy_model.md) | [Sommaire Baseline](./README.md)
