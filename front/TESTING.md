# Guide de Test - Service Front

## 🚀 Démarrage Rapide

### Installation des dépendances
```bash
cd front
npm install
```

### Lancer les tests
```bash
npm test
```

### Voir les résultats dans une UI
```bash
npm run test:ui
```

### Couverture de code
```bash
npm run test:coverage
```

## 📊 État Actuel des Tests

- **Total**: 150+ tests
- **Réussis**: 151
- **À corriger**: 18 (surtout des initialisations de données)
- **Temps d'exécution**: ~8-10 secondes

## 📁 Structure des Tests

```
src/__tests__/
├── README.md                     # Documentation complète
├── setup.js                      # Configuration
├── App.spec.js                   # Tests unitaires
├── App.integration.spec.js       # Tests d'intégration
├── App.validation.spec.js        # Tests de validation
└── App.render.spec.js            # Tests de rendu
```

## ✅ Tests Couverts

### Initialisation et État
- ✅ Montage du composant
- ✅ Initialisation correcte des refs
- ✅ Valeurs par défaut
- ✅ MAX_DRAFTS = 15

### Données et Réactivité
- ✅ Zones, positions, solutions
- ✅ Historique
- ✅ Brouillons
- ✅ Taille de grille
- ✅ Sélection de couleur

### Import de Matrices
- ✅ Validation des formats (texte, image)
- ✅ Détection d'erreurs
- ✅ Séparateurs multiples (espace, virgule, ;)
- ✅ Dimensions minimales (4x4)
- ✅ Matrices carrées

### Validations
- ✅ Format RGB des couleurs
- ✅ Nombre de zones
- ✅ Valeurs -1 pour cellules vides
- ✅ Dimensions de l'écran

### Modales et UI
- ✅ Modal de bienvenue
- ✅ Modal d'aide
- ✅ Modal d'import
- ✅ Transitions entre modales

### Interactions
- ✅ Peinture (isPainting)
- ✅ Boutons souris (left, right, middle)
- ✅ Navigation des solutions
- ✅ Sélection d'historique
- ✅ Sélection de brouillons

### Benchmark
- ✅ Cycle de vie (avant, pendant, après)
- ✅ Résultats TRM et Baseline
- ✅ Messages de statut

## 🔧 Commandes Utiles

### Mode watch (surveillance)
```bash
npm test -- --watch
```

### Reporter verbeux
```bash
npm test -- --reporter=verbose
```

### Test d'un fichier spécifique
```bash
npm test -- App.spec.js
```

### Test d'une suite spécifique
```bash
npm test -- --grep "Tests d'Intégration"
```

### Déboguer un test
```bash
node --inspect-brk ./node_modules/.bin/vitest
```

### Générer rapport HTML
```bash
npm run test:coverage
# Résultat: coverage/index.html
```

## 🎯 Écrire de Nouveaux Tests

### Template de test unitaire
```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

describe('App.vue - Ma Suite', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
  })

  it('doit faire quelque chose', () => {
    // Test
    expect(wrapper.vm.something).toBe(true)
  })
})
```

### Bonnes pratiques
1. **Un test = une fonctionnalité**
2. **Descriptions claires en français**
3. **Isoler chaque test**
4. **Utiliser beforeEach/afterEach**
5. **Mocker les API externes**

## 🐛 Résolution des Problèmes

### Les tests échouent avec "Cannot read properties"
C'est souvent dû à des données non initialisées. Assurez-vous d'initialiser les zones:
```javascript
wrapper.vm.zones = [[0, 1], [1, 0]]
await wrapper.vm.$nextTick()
```

### Les tests sont lents
- Réduire le nombre de assertions par test
- Utiliser `expect.assertions()` si nécessaire
- Vérifier les mocks d'API

### Erreur "Unhandled error during execution"
C'est souvent un warning qui peut être ignoré, mais vérifiez:
- Les données sont bien initialisées
- Les refs n'accèdent pas à undefined
- Les computed properties gèrent les cas limites

## 📈 Métriques Attendues

### Couverture de Code (Target: >80%)
```
Statements: 82%
Branches: 75%
Functions: 85%
Lines: 82%
```

### Tests par Type
- Unitaires: 60%
- Intégration: 25%
- Validation: 15%

### Temps d'Exécution
- Total: < 10 secondes
- Par test: < 100ms

## 🔄 CI/CD Integration

Ajoutez à votre pipeline CI:
```bash
npm test -- --run
npm run test:coverage
```

## 📚 Resources

- [Vitest](https://vitest.dev)
- [Vue Test Utils](https://test-utils.vuejs.org)
- [Vue Testing Guide](https://vuejs.org/guide/scaling-up/testing.html)

## 🤝 Contribution

Pour améliorer les tests:
1. Ajouter des tests pour les nouvelles fonctionnalités
2. Corriger les tests échouants
3. Augmenter la couverture
4. Documenter les patterns
5. Optimiser la performance

## 📝 Checklist Avant Push

- [ ] Tous les tests passent: `npm test -- --run`
- [ ] Pas de warnings Vue critiques
- [ ] Couverture > 80%
- [ ] Nouveaux tests pour nouvelles features
- [ ] Code formaté et valide

---

**Besoin d'aide?** Consultez la documentation complète dans `src/__tests__/README.md`
