.PHONY: up down build run stop logs clean services status check-docker help

# Vérifier que Docker et Docker Compose sont disponibles
check-docker:
	@echo "� Vérification de Docker..."
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "❌ Docker n'est pas installé ou pas dans le PATH"; \
		exit 1; \
	fi
	@if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then \
		echo "❌ Docker Compose n'est pas installé ou pas dans le PATH"; \
		exit 1; \
	fi
	@echo "✅ Docker et Docker Compose sont disponibles"

# Commandes Docker Compose (dépendances installées automatiquement dans les containers)
up: check-docker
	docker compose up

down:
	docker-compose down

build: check-docker
	docker-compose build

run: check-docker
	docker-compose up -d

stop:
	docker-compose stop

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

# État des services
services:
	@echo "📊 État des services:"
	@echo ""
	@echo "Frontend:"
	@if docker compose ps queens 2>/dev/null | grep -q "Up"; then \
		echo "  ✅ UP   → http://localhost:5173"; \
	else \
		echo "  🔴 DOWN → http://localhost:5173"; \
	fi
	@echo ""
	@echo "Backend TRM:"
	@if docker compose ps trm-solveur 2>/dev/null | grep -q "Up"; then \
		echo "  ✅ UP   → http://localhost:8000"; \
	else \
		echo "  🔴 DOWN → http://localhost:8000"; \
	fi
	@echo ""
	@echo "Backend Baseline:"
	@if docker compose ps baseline-solveur 2>/dev/null | grep -q "Up"; then \
		echo "  ✅ UP   → http://localhost:8001"; \
	else \
		echo "  🔴 DOWN → http://localhost:8001"; \
	fi
	@echo ""

status: services

# Aide
help:
	@echo "🎯 Commandes disponibles :"
	@echo "  make up     - Démarrer les services (logs visibles)"
	@echo "  make run    - Démarrer en arrière-plan"
	@echo "  make down   - Arrêter et supprimer les containers"
	@echo "  make stop   - Arrêter les services"
	@echo "  make logs   - Afficher les logs en temps réel"
	@echo "  make services - État et URLs des services"
	@echo "  make build  - Construire/reconstruire les images"
	@echo "  make clean  - Nettoyer complètement (containers + volumes)"
	@echo "  make help   - Afficher cette aide"
	@echo ""
	@echo "📦 Aucune dépendance n'est requise sur votre machine !"
