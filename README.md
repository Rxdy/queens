# Queens Game Solver 🎯

Application interactive pour le **Problème des N-Reines**. Cette app compare deux types de modèles de résolution, tout en fournissant un vrai solveur de grille pour le jeu.

Vous pouvez dessiner votre plateau, importer une image de grille de zones colorées, puis lancer la résolution et le benchmark des deux modèles.

## 🎮 À propos du jeu des Reines

Dans cette application, le plateau est divisé en **zones colorées**. Le but est de placer **une reine par zone** de sorte que :
- Aucune reine ne soit sur la même **ligne** qu'une autre
- Aucune reine ne soit sur la même **colonne** qu'une autre
- Aucune reine ne soit sur la même **diagonale** qu'une autre
- Aucune reine ne soit sur une **case adjacente** à une autre reine

### Variante basée sur les zones

Chaque zone correspond à une région du plateau et doit contenir exactement **une reine**. Les zones introduisent une structure supplémentaire :
- il faut respecter une reine par zone
- il faut respecter les contraintes de ligne, colonne, diagonale et adjacency

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

- **Page d'accueil** : http://localhost:5173
  - Statut : service **Frontend**
  - Description : page d’accueil élégante qui présente le projet et guide vers l’application
- **Application Vue** : http://localhost:5173/app.html
  - Statut : service **Frontend**
  - Description : interface principale pour dessiner la grille, importer une image et lancer les résolutions
- **API TRM** : http://localhost:8000
  - Statut : service **Solveur TRM**
  - Description : endpoint principal du modèle moderne, utilisé pour résoudre la grille et comparer les performances
- **API Baseline** : http://localhost:8001
  - Statut : service **Solveur Baseline**
  - Description : endpoint de comparaison heuristique, pour mesurer les performances du solveur de référence

### ✅ Vérifier l'état des services

```bash
make services
```

> Si vous suivez les étapes du README avec Docker et Docker Compose, le lancement du projet doit fonctionner sans problème sur une machine propre.
Affiche l'état de chaque service avec son URL et son statut.

---

## 📚 Documentation

La documentation complète est dans le dossier [documentation/](documentation/README.md), organisée en deux axes :

| Section | Contenu |
|---------|---------|
| [documentation/technique/](documentation/technique/README.md) | Explication des algorithmes, routes, composants, fonctions utilitaires |
| [documentation/utilisateurs/](documentation/utilisateurs/README.md) | Description des endpoints API (avec exemples cURL) + fonctionnalités de l'interface |

Chaque fichier est relié par une navigation `← Précédent / Suivant →`.

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

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez (`git commit -m 'Add some AmazingFeature'`)
4. Pushez (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT.
