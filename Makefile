.PHONY: up down build run stop logs clean check-docker help

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

# Aide
help:
	@echo "🎯 Commandes disponibles :"
	@echo "  make up     - Démarrer les services (dépendances installées automatiquement)"
	@echo "  make down   - Arrêter les services"
	@echo "  make build  - Construire les images"
	@echo "  make run    - Démarrer en arrière-plan"
	@echo "  make stop   - Arrêter les services"
	@echo "  make logs   - Afficher les logs"
	@echo "  make clean  - Nettoyer les containers et volumes"
	@echo "  make help   - Afficher cette aide"
	@echo ""
	@echo "📦 Aucune dépendance n'est requise sur votre machine !"
