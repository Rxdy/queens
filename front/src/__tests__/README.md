# Suite de Tests - Service Front

Cette suite de tests couvre tous les composants et fonctionnalités du service front de l'application Queens.

## Structure des Tests

```
src/__tests__/
├── setup.js                      # Configuration globale des tests
├── App.spec.js                   # Tests unitaires du composant App
├── App.integration.spec.js       # Tests d'intégration
├── App.validation.spec.js        # Tests de validation des données
└── App.render.spec.js            # Tests de rendu et snapshot
```

## Types de Tests

### 1. **Tests Unitaires (App.spec.js)**
- Tests d'initialisation du composant
- Tests des états et références (refs)
- Tests des propriétés calculées (computed properties)
- Tests de réactivité des données
- Tests des brouillons (drafts)
- Tests de l'historique
- Tests de l'état du benchmark
- Tests des modales
- Tests de l'import de matrice
- Tests des interactions souris

**Couverture**: 60+ tests

### 2. **Tests d'Intégration (App.integration.spec.js)**
- Workflows complets:
  - Initialisation → Import → Affichage
  - Gestion des solutions
  - Gestion de l'historique
  - Gestion des brouillons
  - Gestion des erreurs
  - Transitions entre modales
  - Interactions souris et peinture
  - Changements de taille de grille
  - Cycle de vie du benchmark
  - Import d'images

**Couverture**: 20+ workflows

### 3. **Tests de Validation (App.validation.spec.js)**
- Validation des matrices:
  - Dimensions correctes
  - Format des données
  - Zones distinctes
  - Nombre de zones
  - Valeurs -1 pour cellules vides
- Validation des formats d'entrée:
  - Séparateurs multiples (espace, virgule, point-virgule)
  - Retours à la ligne différents (\n, \r\n)
  - Espaces blancs supplémentaires
- Validation des couleurs
- Validation des dimensions
- Validation des brouillons
- Validation des interactions

**Couverture**: 35+ tests de validation

### 4. **Tests de Rendu (App.render.spec.js)**
- Rendu du composant
- Structure du composant
- État initial du rendu
- Réactivité du rendu
- Affichage des erreurs
- Affichage de l'historique
- Affichage des brouillons
- Affichage de la légende
- Affichage des modales
- Tests de snapshot

**Couverture**: 40+ tests de rendu

## Fonctionnalités Testées

### État et Initialisation
- ✅ Initialisation correcte du composant
- ✅ États par défaut des refs
- ✅ Propriétés calculées

### Gestion des Données
- ✅ Zones/positions/solutions
- ✅ Historique et sélection
- ✅ Brouillons (MAX_DRAFTS = 15)
- ✅ Taille de la grille

### Import de Matrices
- ✅ Import via texte
- ✅ Validation de format
- ✅ Validation de dimensions (min 4x4)
- ✅ Détection d'erreurs
- ✅ Import d'images

### Couleurs et Affichage
- ✅ 12 couleurs disponibles
- ✅ Format RGB valide
- ✅ Couleurs dynamiques selon la grille
- ✅ Légende d'import

### Modales
- ✅ Modal de bienvenue
- ✅ Modal d'aide
- ✅ Modal d'import
- ✅ Transitions entre modales

### Interactions
- ✅ Peinture sur la grille
- ✅ Sélection de couleur
- ✅ Changement de taille
- ✅ Navigation des solutions
- ✅ Gestion de l'historique

### Benchmark
- ✅ État du benchmark
- ✅ Résultats TRM et Baseline
- ✅ Messages de statut

## Commandes

### Exécuter tous les tests
```bash
npm test
```

### Interface de tests avec UI
```bash
npm run test:ui
```

### Couverture de code
```bash
npm run test:coverage
```

### Tests en mode watch (surveillance)
```bash
npm test -- --watch
```

### Tests d'un fichier spécifique
```bash
npm test -- App.spec.js
```

### Tests avec reporter détaillé
```bash
npm test -- --reporter=verbose
```

## Configuration

### Fichier `vitest.config.js`
- Environnement: jsdom (DOM simulé)
- Framework: Vue 3
- Setup files: `src/__tests__/setup.js`
- Coverage provider: v8
- Reporters: text, json, html

### Fichier `setup.js`
- Configuration Vue Test Utils globale
- Mocks pour window.matchMedia
- Mock pour IntersectionObserver
- Mocks pour axios

## Metrics

- **Nombre total de tests**: 150+
- **Fichiers testés**: App.vue
- **Couverture cible**: >80%
- **Suites de tests**: 4 (spec, integration, validation, render)

## Assertions Principales

Les tests utilisent principalement:
- `expect().toBe()` - Égalité stricte
- `expect().toEqual()` - Égalité profonde
- `expect().toBeDefined()` - Vérifier la définition
- `expect().toBeTruthy()/toBeFalsy()` - Valeurs truthy/falsy
- `expect().toMatch()` - Regex matching
- `expect().toContain()` - Contient un élément
- `expect().toBeGreaterThan()` - Comparaisons numériques
- `expect().toHaveProperty()` - Vérifier les propriétés

## Mocking

Les dépendances externes sont mockées:
- `axios` - Requests HTTP
- `window.matchMedia` - Media queries
- `IntersectionObserver` - Observations DOM

## Bonnes Pratiques

1. **Isolation**: Chaque test est indépendant
2. **Nettoyage**: Utilisation de `beforeEach` et `afterEach`
3. **Lisibilité**: Descriptions claires des tests
4. **Couverture**: Tests des happy paths et edge cases
5. **Performance**: Tests rapides avec jsdom

## Dépendances

```json
{
  "devDependencies": {
    "vitest": "^1.x",
    "@vue/test-utils": "^2.x",
    "jsdom": "^23.x",
    "@vitejs/plugin-vue": "^6.x",
    "@vitest/ui": "^1.x"
  }
}
```

## Résolution des Problèmes

### Les tests ne trouvent pas le composant
Vérifier que `@vitejs/plugin-vue` est installé et configuré.

### Erreurs sur les mocks
Assurez-vous que le fichier `setup.js` est chargé avant les tests.

### Erreurs de "window is not defined"
L'environnement jsdom devrait les gérer automatiquement.

### Couverture faible
Ajouter des tests pour les branches non testées dans `App.vue`.

## Contribution

Pour ajouter de nouveaux tests:
1. Identifier la fonctionnalité à tester
2. Créer un test dans le fichier approprié
3. Utiliser les mêmes conventions de nommage
4. Lancer `npm test` pour vérifier
5. Mesurer la couverture avec `npm run test:coverage`

## Ressources

- [Vitest Documentation](https://vitest.dev)
- [Vue Test Utils](https://test-utils.vuejs.org)
- [Vue 3 Testing Guide](https://vuejs.org/guide/scaling-up/testing.html)
- [Testing Library Best Practices](https://testing-library.com/docs)

## Maintenance

Ces tests doivent être maintenus à jour avec:
- Nouvelles fonctionnalités du composant
- Changements d'API
- Refactorisations du code
- Mises à jour des dépendances

---

**Dernière mise à jour**: 2026-05-26
**Responsable**: Équipe Front
