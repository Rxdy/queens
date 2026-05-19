# Queens Game Solver 🎯

Application interactive pour le **Problème des N-Reines**. Cette app compare deux types de modèles de résolution, tout en fournissant un vrai solveur de grille pour le jeu.

Vous pouvez dessiner votre plateau, importer une image de grille de zones colorées, puis lancer la résolution et le benchmark des deux modèles.

## 🎮 À propos du jeu des Reines

Le problème des N-Reines consiste à placer **N reines** sur un échiquier de taille **N×N** de manière à ce que :
- Aucune deux reines ne soient sur la même **ligne**
- Aucune deux reines ne soient sur la même **colonne**  
- Aucune deux reines ne soient sur la même **diagonale**

### Variante avec zones colorées

Dans cette application, l'échiquier est divisé en **zones colorées** pour ajouter une couche de complexité :
- Chaque zone représente une région contrainte
- Vous devez placer les reines en respect des zones ET des règles classiques

## 🤖 Deux algorithmes en compétition

### 1. **TRM (Transformer-based Reasoning Model)**
- Approche moderne utilisant des réseaux de neurones  
- Optimisé pour les grilles de 4 à 12 reines
- Utilise le raisonnement transformateur

### 2. **Baseline (Greedy + Local Search)**
- Approche classique heuristique
- Combinaison de recherche gourmande + optimisation locale
- Référence de performance

**Fonctionnalité Benchmark** : Testez et comparez les deux modèles sur des grilles de 4 à 12 reines avec des temps d'exécution détaillés.

## ✨ Fonctionnalités

- 🎨 **Interface interactive** : Dessinez les zones colorées directement
- 🔍 **Import d'images** : Extrayez une grille de zones à partir d'une photo
- 📊 **Benchmark** : Comparez TRM vs Baseline sur 9 tailles différentes
- 📜 **Historique** : Retrouvez vos résolutions précédentes
- 📱 **Responsive** : Fonctionne sur tous les appareils

---

## 🚀 Installation & Lancement

### Prérequis

- **Git** pour cloner le projet
- **Docker et Docker Compose** pour l'exécution

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/yourusername/queens.git
cd queens
```

### 2️⃣ Lancer l'application

```bash
# Démarrage simple (logs visibles)
make up

# Ou pour lancer en arrière-plan
make run
```

Les services démarrent automatiquement. Les dépendances sont installées dans les containers.

### 3️⃣ Accéder à l'application

- **Interface Web** : http://localhost:5173
- **API TRM** : http://localhost:8000
- **API Baseline** : http://localhost:8001

### ✅ Vérifier l'état des services

```bash
make services
```

Affiche l'état de chaque service avec son URL et son statut.

---

## 🛠️ Commandes Make disponibles

```bash
# Gestion des services
make up        # Démarrer les services avec logs
make run       # Démarrer en arrière-plan
make stop      # Arrêter les services
make down      # Arrêter et supprimer les containers
make logs      # Afficher les logs en temps réel
make services  # État et URLs des services

# Maintenance
make build     # Construire/reconstruire les images
make clean     # Nettoyer complètement (containers + volumes)

# Aide
make help      # Afficher toutes les commandes disponibles
```

---

## 🏗️ Architecture

| Composant | Technologie | Port |
|-----------|-------------|------|
| **Frontend** | Vue.js 3 + Vite | 5175 |
| **Backend TRM** | FastAPI + Python 3.12 | 8000 |
| **Backend Baseline** | FastAPI + Python 3.12 | 8001 |

Tous les services s'exécutent dans des **containers Docker isolés**.

---

## 📁 Structure du projet

```
queens/
├── front/                    # Application Vue.js
│   ├── src/
│   │   └── App.vue          # Composant principal
│   ├── package.json
│   └── vite.config.js
├── TRM/                      # Solveur principal (Transformer Model)
│   ├── api/
│   │   ├── routes.py        # Endpoints API
│   │   ├── models.py        # Modèles Pydantic
│   ├── core/
│   │   ├── solver.py        # Algorithme TRM
│   ├── app.py
│   └── requirements.txt
├── baseline-8queens/        # Solveur de comparaison
├── docker-compose.yml       # Orchestration des services
├── Makefile                 # Automatisation
├── generate_test_images.py  # Génération de tests d'extraction
└── README.md
```

---

## 🔧 Développement local (sans Docker)

Si vous préférez développer en local :

```bash
# Frontend (terminal 1)
cd front
npm install
npm run dev         # Écoute sur http://localhost:5175

# Backend TRM (terminal 2)
cd TRM
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Backend Baseline (terminal 3)
cd baseline-8queens
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

---

## 🧪 Tests

Tests d'extraction d'images synthétiques :

```bash
# Dans le container ou localement avec Python 3.12+
python generate_test_images.py
```

Génère 6 images de test avec validation d'extraction (5x5 à 8x8).

---

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez (`git commit -m 'Add some AmazingFeature'`)
4. Pushez (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT.
