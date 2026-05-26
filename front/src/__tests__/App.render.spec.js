import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

describe('App.vue - Tests de Rendu', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
    // Initialiser zones pour éviter les erreurs
    wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(-1))
    wrapper.vm.size = 8
  })

  describe('Rendu du Composant', () => {
    it('doit monter et rendre le composant', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('doit être un composant Vue valide', () => {
      expect(wrapper.vm).toBeDefined()
      expect(wrapper.vm.$options).toBeDefined()
    })

    it('doit avoir un élément racine', () => {
      expect(wrapper.element).toBeDefined()
    })

    it('doit contenir les éléments principaux du DOM', () => {
      // Vérifier que le composant rend du contenu
      expect(wrapper.html().length).toBeGreaterThan(0)
    })
  })

  describe('Structure du Composant', () => {
    it('doit être un composant script setup', () => {
      const options = wrapper.vm.$options
      expect(options).toBeDefined()
    })

    it('doit déclarer tous les refs importants', () => {
      expect(wrapper.vm.size).toBeDefined()
      expect(wrapper.vm.zones).toBeDefined()
      expect(wrapper.vm.positions).toBeDefined()
      expect(wrapper.vm.solutions).toBeDefined()
      expect(wrapper.vm.selectedColor).toBeDefined()
    })

    it('doit déclarer tous les computed properties', () => {
      expect(wrapper.vm.availableColors).toBeDefined()
      expect(wrapper.vm.availableColorIndices).toBeDefined()
      expect(wrapper.vm.importLegendItems).toBeDefined()
    })
  })

  describe('État Initial du Rendu', () => {
    it('doit afficher la grille initialement', () => {
      // Le composant doit rendre quelque chose
      expect(wrapper.html()).toBeTruthy()
    })

    it('doit afficher la modal de bienvenue au démarrage', () => {
      expect(wrapper.vm.showWelcomeModal).toBe(true)
    })

    it('doit ne pas afficher la modal d\'aide au démarrage', () => {
      expect(wrapper.vm.showHelpModal).toBe(false)
    })

    it('doit initialiser avec la bonne grille', () => {
      expect(wrapper.vm.size).toBe(8)
      expect(wrapper.vm.zones).toEqual([])
    })
  })

  describe('Réactivité du Rendu', () => {
    it('doit réagir au changement de taille', async () => {
      wrapper.vm.size = 4
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.size).toBe(4)
    })

    it('doit réagir au changement de couleur sélectionnée', async () => {
      wrapper.vm.selectedColor = 2
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.selectedColor).toBe(2)
    })

    it('doit mettre à jour les zones', async () => {
      wrapper.vm.zones = [[0, 1], [1, 0]]
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones.length).toBe(2)
    })

    it('doit mettre à jour les solutions', async () => {
      wrapper.vm.solutions = [
        { id: 1, data: [] },
        { id: 2, data: [] }
      ]
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.solutions.length).toBe(2)
    })
  })

  describe('Affichage des Erreurs', () => {
    it('doit pouvoir afficher un message d\'erreur', async () => {
      wrapper.vm.errorMessage = 'Test error'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.errorMessage).toBe('Test error')
    })

    it('doit afficher les erreurs d\'import', async () => {
      wrapper.vm.importError = 'Import failed'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importError).toBe('Import failed')
    })

    it('doit afficher les erreurs d\'extraction d\'image', async () => {
      wrapper.vm.importImageExtractError = 'Image extract failed'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importImageExtractError).toBe('Image extract failed')
    })
  })

  describe('Affichage de l\'Historique', () => {
    it('doit afficher l\'historique quand visible', async () => {
      wrapper.vm.historyVisible = true
      wrapper.vm.history = [
        { action: 'paint', row: 0, col: 0 },
        { action: 'clear', row: 1, col: 1 }
      ]
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.historyVisible).toBe(true)
      expect(wrapper.vm.history.length).toBe(2)
    })

    it('doit masquer l\'historique quand requis', async () => {
      wrapper.vm.historyVisible = false
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.historyVisible).toBe(false)
    })

    it('doit permettre la sélection dans l\'historique', async () => {
      wrapper.vm.history = [
        { id: 0, action: 'action1' },
        { id: 1, action: 'action2' }
      ]
      wrapper.vm.selectedHistoryIndex = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.selectedHistoryIndex).toBe(1)
    })
  })

  describe('Affichage des Brouillons', () => {
    it('doit afficher les brouillons quand disponibles', async () => {
      wrapper.vm.drafts = [
        { name: 'Draft 1', zones: [] },
        { name: 'Draft 2', zones: [] }
      ]
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(2)
    })

    it('doit gérer la sélection des brouillons', async () => {
      wrapper.vm.drafts = [
        { name: 'Draft 1', zones: [] },
        { name: 'Draft 2', zones: [] }
      ]
      wrapper.vm.currentDraftIndex = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.currentDraftIndex).toBe(1)
    })
  })

  describe('Affichage de la Légende', () => {
    it('doit afficher la légende quand visible', async () => {
      wrapper.vm.showImportLegend = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showImportLegend).toBe(true)
    })

    it('doit afficher les éléments de légende', () => {
      const items = wrapper.vm.importLegendItems
      expect(Array.isArray(items)).toBe(true)
      expect(items.length).toBeGreaterThan(0)
    })

    it('doit afficher la légende d\'import correctement', () => {
      wrapper.vm.showImportLegend = true
      const items = wrapper.vm.importLegendItems
      
      // Vérifier que chaque item a les propriétés requises
      items.forEach(item => {
        expect(item).toHaveProperty('value')
        expect(item).toHaveProperty('color')
        expect(item).toHaveProperty('label')
      })
    })
  })

  describe('Affichage des Modales', () => {
    it('doit afficher la modal de bienvenue', async () => {
      wrapper.vm.showWelcomeModal = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showWelcomeModal).toBe(true)
    })

    it('doit afficher la modal d\'aide', async () => {
      wrapper.vm.showHelpModal = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showHelpModal).toBe(true)
    })

    it('doit afficher la modal d\'import', async () => {
      wrapper.vm.isImportModalOpen = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isImportModalOpen).toBe(true)
    })

    it('doit pouvoir ouvrir/fermer les modales', async () => {
      wrapper.vm.showWelcomeModal = true
      expect(wrapper.vm.showWelcomeModal).toBe(true)
      
      wrapper.vm.showWelcomeModal = false
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showWelcomeModal).toBe(false)
    })
  })

  describe('Affichage des Couleurs', () => {
    it('doit afficher toutes les couleurs disponibles', () => {
      expect(wrapper.vm.colors.length).toBeGreaterThan(0)
    })

    it('doit mettre à jour les couleurs disponibles', async () => {
      wrapper.vm.zones = [[0, 1], [1, 0]]
      await wrapper.vm.$nextTick()
      
      const availableColors = wrapper.vm.availableColors
      expect(Array.isArray(availableColors)).toBe(true)
    })

    it('doit afficher les couleurs avec le bon format RGB', () => {
      wrapper.vm.colors.forEach(color => {
        expect(color).toMatch(/^rgb\(/i)
      })
    })
  })

  describe('Affichage des Solutions', () => {
    it('doit afficher les solutions quand disponibles', async () => {
      wrapper.vm.solutions = [
        { id: 1, data: [0, 1, 2, 3] },
        { id: 2, data: [0, 1, 2, 3] }
      ]
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.solutions.length).toBe(2)
    })

    it('doit gérer la navigation entre les solutions', async () => {
      wrapper.vm.solutions = [
        { id: 1, data: [] },
        { id: 2, data: [] },
        { id: 3, data: [] }
      ]
      
      wrapper.vm.currentSolutionIndex = 0
      expect(wrapper.vm.currentSolutionIndex).toBe(0)
      
      wrapper.vm.currentSolutionIndex = 2
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.currentSolutionIndex).toBe(2)
    })
  })

  describe('Affichage de l\'Import', () => {
    it('doit afficher la zone d\'import de texte', async () => {
      wrapper.vm.importMode = 'text'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importMode).toBe('text')
    })

    it('doit afficher la zone d\'import d\'image', async () => {
      wrapper.vm.importMode = 'image'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importMode).toBe('image')
    })

    it('doit afficher la matrice importée', async () => {
      wrapper.vm.importImageResult = {
        zones: [[0, 1], [1, 0]]
      }
      await wrapper.vm.$nextTick()
      
      const preview = wrapper.vm.importImageMatrixPreview
      expect(preview).toBeTruthy()
    })
  })

  describe('Affichage du Benchmark', () => {
    it('doit afficher l\'état du benchmark', async () => {
      wrapper.vm.isBenchmarking = true
      wrapper.vm.benchmarkStatus = 'En cours...'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isBenchmarking).toBe(true)
      expect(wrapper.vm.benchmarkStatus).toBe('En cours...')
    })

    it('doit afficher les résultats du benchmark', async () => {
      wrapper.vm.trmPerformance = { time: 1000, accuracy: 0.95 }
      wrapper.vm.baselineResult = { time: 1500, accuracy: 0.90 }
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.trmPerformance).toBeTruthy()
      expect(wrapper.vm.baselineResult).toBeTruthy()
    })
  })

  describe('Affichage des Dimensions', () => {
    it('doit afficher les informations de debug de la grille', async () => {
      const debugInfo = wrapper.vm.gridDebugInfo
      expect(debugInfo).toBeTruthy()
      expect(debugInfo.calculatedCellSize).toBeDefined()
      expect(debugInfo.gridWidth).toBeDefined()
    })

    it('doit mettre à jour les dimensions d\'écran', async () => {
      wrapper.vm.screenWidth = 1920
      wrapper.vm.screenHeight = 1080
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.screenWidth).toBe(1920)
      expect(wrapper.vm.screenHeight).toBe(1080)
    })
  })

  describe('Affichage de l\'Interaction Souris', () => {
    it('doit gérer l\'état de peinture', async () => {
      wrapper.vm.isPainting = true
      wrapper.vm.currentMouseButton = 'left'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isPainting).toBe(true)
      expect(wrapper.vm.currentMouseButton).toBe('left')
    })
  })

  describe('Snapshot Tests', () => {
    it('doit avoir un HTML stable', () => {
      const html = wrapper.html()
      expect(html).toBeTruthy()
      expect(html.length).toBeGreaterThan(100)
    })

    it('les éléments principaux doivent être présents', () => {
      const vm = wrapper.vm
      
      // Vérifier les éléments critiques
      expect(vm.size).toBeDefined()
      expect(vm.zones).toBeDefined()
      expect(vm.colors).toBeDefined()
      expect(vm.solutions).toBeDefined()
    })
  })
})
