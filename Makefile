.PHONY: up down build run stop logs clean services status check-docker help dev-front dev-backend dev-both dev-ide test-e2e test-e2e-debug test-e2e-ui test-e2e-all test-images test-components test-integration test-unit-front test-unit-front-watch test-unit-front-coverage test-unit-front-ui ide-view

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

# Commandes de développement local (sans Docker)
dev-front:
	cd front && npm run dev -- --host 0.0.0.0 --port 5173

dev-backend:
	. .venv/bin/activate && python TRM/app.py

test-e2e:
	cd front && npx playwright test --headed

test-e2e-debug:
	cd front && npx playwright test --debug

test-e2e-ui:
	cd front && npx playwright test --ui

test-e2e-all:
	cd front && npx playwright test --headed --reporter=list

test-images:
	cd front && npx playwright test image-import.spec.js --headed

test-components:
	cd front && npx playwright test components.spec.js --headed

test-integration:
	cd front && npx playwright test integration.spec.js --headed

test-unit-front:
	cd front && npm test -- --run

test-unit-front-watch:
	cd front && npm test -- --watch

test-unit-front-coverage:
	cd front && npm run test:coverage

test-unit-front-ui:
	cd front && npm run test:ui

ide-view:
	@echo "🌐 Ouverture de l'app dans VS Code..."
	code --open-url http://localhost:5173

# Combine: lancer le frontend + ouvrir dans VS Code
dev-ide: dev-front ide-view

# Combine: lancer backend + frontend en arrière-plan
dev-both:
	@echo "🚀 Démarrage du backend et du frontend..."
	@cd TRM && . ../.venv/bin/activate && python app.py > /tmp/trm.log 2>&1 &
	@cd front && npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/front.log 2>&1 &
	@echo "Backend sur port 8000, Frontend sur port 5173"
	@sleep 2
	@echo "✅ Services lancés!"

# Aide
help:
	@echo "🎯 Commandes disponibles :"
	@echo ""
	@echo "🐳 AVEC DOCKER (services complets) :"
	@echo "  make up     - Démarrer les services (logs visibles)"
	@echo "  make run    - Démarrer en arrière-plan"
	@echo "  make down   - Arrêter et supprimer les containers"
	@echo "  make stop   - Arrêter les services"
	@echo "  make logs   - Afficher les logs en temps réel"
	@echo "  make services - État et URLs des services"
	@echo "  make build  - Construire/reconstruire les images"
	@echo "  make clean  - Nettoyer complètement (containers + volumes)"
	@echo ""
	@echo "💻 DÉVELOPPEMENT LOCAL (sans Docker) :"
	@echo "  make dev-front - Lancer le frontend en mode dev (port 5173)"
	@echo "  make dev-backend - Lancer le backend TRM (port 8000)"
	@echo "  make dev-both - Lancer backend + frontend"
	@echo "  make dev-ide - Lancer frontend et ouvrir dans VS Code"
	@echo ""
	@echo "🧪 TESTS UNITAIRES VUE (composants) :"
	@echo "  make test-unit-front - Lancer tous les tests unitaires"
	@echo "  make test-unit-front-watch - Lancer en mode watch (surveillance)"
	@echo "  make test-unit-front-ui - UI interactive pour les tests (🎯)"
	@echo "  make test-unit-front-coverage - Générer un rapport de couverture"
	@echo ""
	@echo "🧪 TESTS PLAYWRIGHT (E2E, composants, intégration) :
	@echo "  make test-e2e - Lancer tous les tests en mode headed"
	@echo "  make test-e2e-debug - Lancer les tests en mode debug"
	@echo "  make test-e2e-ui - Lancer les tests dans l'IDE Playwright (🎯)"
	@echo "  make test-e2e-all - Tous les tests avec rapport détaillé"
	@echo "  make test-images - Tests d'import d'images (test_images/)"
	@echo "  make test-components - Tests des composants Vue"
	@echo "  make test-integration - Tests d'intégration complet"
	@echo ""
	@echo "  make ide-view - Ouvrir l'app sur localhost:5173"
	@echo "  make help   - Afficher cette aide"
	@echo ""
	@echo "📦 Aucune dépendance n'est requise sur votre machine !"
