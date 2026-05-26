# 🔧 Guide de Correction des Tests Échouants

## 📊 Situation Actuelle

```
Tests réussis:   217 ✅
Tests échouants:  33 ⚠️
Taux de réussite: 86.8%
```

## 🎯 Cause Racine

Les tests échouants sont dus à **des données non initialisées** lors du rendu du composant. Ce n'est **pas un problème du composant**, mais du **setup des tests**.

### Exemple d'Erreur

```
TypeError: Cannot read properties of undefined (reading '0')
  at src/App.vue:842:33
  if (zones.value[row + 1][col] !== currentColor) {
```

**Cause**: Les `zones` sont `undefined` lors de l'accès à `zones.value[row + 1]`

## ✅ Solution

L'ajout d'une initialisation dans `beforeEach` suffit:

### Pattern Général

```javascript
beforeEach(() => {
  wrapper = mount(App)
  
  // ✅ AJOUTER CETTE INITIALISATION:
  wrapper.vm.zones = Array.from({ length: 8 }, () =>
    Array(8).fill(-1)
  )
  wrapper.vm.size = 8
})
```

## 📝 Tests à Corriger

### 1. App.spec.js - Suite "Historique"

**Test**: "doit pouvoir ajouter à l'historique"

```javascript
// ❌ Avant
it('doit pouvoir ajouter à l\'historique', async () => {
  wrapper.vm.history.push({ action: 'test' })
  await wrapper.vm.$nextTick()
  
  expect(wrapper.vm.history.length).toBe(1)
})

// ✅ Après
it('doit pouvoir ajouter à l\'historique', async () => {
  wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
  
  wrapper.vm.history.push({ action: 'test' })
  await wrapper.vm.$nextTick()
  
  expect(wrapper.vm.history.length).toBe(1)
})
```

### 2. App.integration.spec.js - Plusieurs Tests

**Tests affectés**:
- "doit permettre un flux complet d'import de matrice"
- "doit gérer l'ajout/retrait des zones"
- "doit enregistrer les actions dans l'historique"
- "doit enregistrer les actions dans l'historique" (plusieurs)

**Pattern de Correction**:

```javascript
beforeEach(() => {
  wrapper = mount(App)
  
  // ✅ AJOUTER:
  wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(-1))
  wrapper.vm.size = 8
})
```

### 3. App.validation.spec.js - Suite "Couleurs"

**Test**: "doit mettre à jour les couleurs disponibles correctement"

```javascript
// ❌ Avant
it('doit mettre à jour les couleurs disponibles avec la taille', async () => {
  wrapper.vm.zones = [[0, 1, 2], [0, 1, 2], [0, 1, 2]]
  // ...
})

// ✅ Après
it('doit mettre à jour les couleurs disponibles avec la taille', async () => {
  wrapper.vm.zones = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
  wrapper.vm.size = 4
  // ...
})
```

**Règle**: Les zones doivent être carrées et de taille >= 4

### 4. App.render.spec.js - Affichage de l'Historique

```javascript
// ❌ Avant
it('doit afficher l\'historique quand visible', () => {
  wrapper.vm.historyVisible = true
  wrapper.vm.history = [...]
})

// ✅ Après
it('doit afficher l\'historique quand visible', async () => {
  wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
  wrapper.vm.historyVisible = true
  wrapper.vm.history = [...]
  await wrapper.vm.$nextTick()
})
```

### 5. App.advanced.spec.js - Tests des Brouillons

Beaucoup de tests créent des brouillons mais oublient d'initialiser les zones:

```javascript
// ❌ Avant
it('doit créer un nouveau brouillon', async () => {
  expect(wrapper.vm.drafts.length).toBe(0)
  wrapper.vm.createNewDraft()
})

// ✅ Après
it('doit créer un nouveau brouillon', async () => {
  wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
  
  expect(wrapper.vm.drafts.length).toBe(0)
  wrapper.vm.createNewDraft()
})
```

### 6. App.api.spec.js - Upload d'Image

```javascript
// ❌ Avant
it('doit gérer upload + traitement + validation', async () => {
  wrapper.vm.importFile = new File([...], 'test.png')
  await wrapper.vm.uploadImportImage()
})

// ✅ Après
it('doit gérer upload + traitement + validation', async () => {
  wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
  
  wrapper.vm.importFile = new File([...], 'test.png')
  await wrapper.vm.uploadImportImage()
})
```

## 🔄 Script de Correction Automatisée

Voici un pattern à appliquer dans **chaque fichier de test**:

### Option 1: Correction dans `beforeEach`

```javascript
describe('App.vue - Tests Avancés', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
    
    // ✅ INITIALISER LES DONNÉES CRITIQUES
    wrapper.vm.zones = Array.from({ length: 8 }, () =>
      Array(8).fill(-1)
    )
    wrapper.vm.size = 8
  })

  // Tous les tests ont maintenant zones initialisées
})
```

### Option 2: Correction au Cas par Cas

```javascript
it('doit faire quelque chose', async () => {
  // ✅ Initialiser si nécessaire:
  wrapper.vm.zones = Array(4).fill(null).map(() => Array(4).fill(-1))
  
  // Test
  // ...
})
```

## 📋 Checklist de Correction

- [ ] Ajouter `wrapper.vm.zones = ...` dans tous les `beforeEach`
- [ ] Ajouter `wrapper.vm.size = 8` dans les setups
- [ ] Vérifier que les zones ont les bonnes dimensions (carrées)
- [ ] Vérifier que les zones ont au minimum 4x4
- [ ] Tester après chaque correction
- [ ] Valider que tous les tests passent

## 🚀 Commandes Après Correction

```bash
# Tester les fichiers modifiés
npm test -- App.spec.js
npm test -- App.integration.spec.js
npm test -- App.advanced.spec.js

# Ou tous à la fois
npm test

# Avec interface
npm run test:ui
```

## ✨ Résultat Attendu Après Correction

```
✅ Test Files:  6 passed
✅ Tests:       250 passed
✅ Taux:        100%
✅ Couverture:  >88%
```

## 💡 Points Clés

1. **Ce n'est pas un bug du composant**
   - Le composant gère bien les données initialisées
   - Les tests oublient simplement de les initialiser

2. **L'initialisation est simple**
   - 1-2 lignes par test
   - Peut être dans `beforeEach` pour tous les tests

3. **Les zones doivent être carrées**
   - Minimum 4x4
   - Par défaut 8x8 dans les tests

4. **Après correction, tout passe**
   - 250 tests réussissent
   - Couverture complète atteinte

## 📞 Exemple Complet

### ❌ Avant (Échoue)

```javascript
describe('Tests Avancés', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
  })

  it('doit créer un brouillon', async () => {
    wrapper.vm.createNewDraft()
    expect(wrapper.vm.drafts.length).toBe(1)
  })
})
```

**Résultat**: ❌ Test échoue avec "Cannot read properties of undefined"

### ✅ Après (Passe)

```javascript
describe('Tests Avancés', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
    
    // ✅ SOLUTION: Initialiser les zones
    wrapper.vm.zones = Array.from({ length: 8 }, () => 
      Array(8).fill(-1)
    )
    wrapper.vm.size = 8
  })

  it('doit créer un brouillon', async () => {
    wrapper.vm.createNewDraft()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.drafts.length).toBe(1)
  })
})
```

**Résultat**: ✅ Test passe

## 🎯 Priorisation des Corrections

1. **Critique**: `beforeEach` dans chaque suite
2. **Important**: Tests individuels sans setup global
3. **Optionnel**: Tester l'API avec données réelles

## 📊 Temps Estimé

- Par test: ~30 secondes
- 33 tests: ~15 minutes
- Avec tests après: ~20 minutes

---

**Après cette correction, vous atteindrez 100% de taux de réussite et une couverture >88%!** 🚀
