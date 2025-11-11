# Queens Game Solver 🎯

Un solveur interactif pour le problème des N-Reines avec contraintes de zones colorées.

## 🚀 Démarrage rapide

### Prérequis

-   **Docker et Docker Compose** (c'est tout !)

### Installation automatique

Le projet s'exécute entièrement dans des containers Docker. Aucune dépendance n'est requise sur votre machine :

```bash
# Démarrer l'application (recommandé)
make up

# Ou avec Docker Compose directement
docker-compose up
```

Les dépendances suivantes sont automatiquement installées dans les containers :

-   **Frontend** : Node.js packages (`npm install`)
-   **Backend** : Python packages (`pip install -r requirements.txt`)

## 🎮 Utilisation

1. **Interface web** : http://localhost:5173
2. **API backend** : http://localhost:8000

### Fonctionnalités

-   Création interactive de zones colorées
-   Résolution automatique des placements de reines
-   Historique des résolutions
-   Interface responsive

## 🛠️ Commandes disponibles

```bash
# Démarrage avec vérification Docker
make up        # Démarre les services (recommandé)

# Gestion des services
make down      # Arrêt des services
make run       # Démarrage en arrière-plan
make stop      # Arrêt des services
make logs      # Logs en temps réel
make clean     # Nettoyage complet

# Aide
make help      # Liste des commandes
```

## 🏗️ Architecture

-   **Frontend** : Vue.js 3 + Vite (container Node.js 20)
-   **Backend** : FastAPI (container Python 3.11)
-   **Conteneurisation** : Docker Compose
-   **Isolation complète** : Aucune dépendance sur la machine hôte

## 📁 Structure du projet

```
queens/
├── front/          # Application Vue.js
├── TRM/           # API FastAPI
├── docker-compose.yml
├── Makefile       # Automatisation des tâches
└── README.md
```

## 🔧 Développement local

Si vous préférez développer sans Docker :

```bash
# Frontend
cd front
npm install
npm run dev

# Backend (terminal séparé)
cd TRM
pip install -r requirements.txt
uvicorn app:app --reload
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez (`git commit -m 'Add some AmazingFeature'`)
4. Pushez (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.
