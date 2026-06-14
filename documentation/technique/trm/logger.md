# Logger — TRM

`TRM/utils/logger.py`

---

## setup_logging(log_level)

Configure et retourne un logger nommé `"trm_solver"`.

```python
def setup_logging(log_level: str = "INFO") -> logging.Logger:
```

| Paramètre | Valeurs | Description |
|---|---|---|
| `log_level` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | Niveau de log (depuis `LOG_LEVEL` dans `config.py`) |

**Format des logs :**
```
2024-01-15 10:32:01,234 - trm_solver - INFO - 🚀 TRM Solver démarré
```

---

## Comportement idempotent

Le logger vérifie `hasHandlers()` avant d'ajouter un handler. Cela évite la duplication des messages lors des rechargements à chaud (`uvicorn --reload` en dev) :

```python
if logger.hasHandlers():
    return logger  # handler déjà configuré
```

`logger.propagate = False` empêche aussi les logs de remonter au logger root de Python.

---

## Utilisation dans les modules

```python
import logging
logger = logging.getLogger("trm_solver")
logger.info("Message")
```

Le logger est partagé entre tous les modules via le nom `"trm_solver"`.

---

[← models.md](./models.md) | [Sommaire TRM](./README.md)
