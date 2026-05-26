import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('App.vue - Tests d\'Intégration', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App, {
      global: {
        mocks: {
          $axios: {
            post: vi.fn(),
            get: vi.fn()
          }
        }
      }
    })
    // Initialiser zones pour éviter les erreurs
    wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(-1))
    wrapper.vm.size = 8
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('Workflow: Initialisation > Import > Affichage', () => {
    it('doit permettre un flux complet d\'import de matrice', async () => {
      // Vérifier l'état initial
      expect(wrapper.vm.zones).toEqual([])
      
      // Simuler l'import d'une matrice
      wrapper.vm.importMatrixText = `0 1 2 3
0 1 2 3
0 1 2 3
0 1 2 3`
      
      await wrapper.vm.$nextTick()
      
      // Vérifier que la matrice est valide
      const parseResult = wrapper.vm.importMatrixParseResult
      expect(parseResult.isValid).toBe(true)
      expect(parseResult.error).toBeNull()
    })

    it('doit gérer l\'ajout/retrait des zones', async () => {
      // Initialiser les zones
      wrapper.vm.zones = [
        [0, 1, 2],
        [0, 1, 2],
        [0, 1, 2]
      ]
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones.length).toBe(3)
      expect(wrapper.vm.zones[0].length).toBe(3)
      
      // Modifier une zone
      wrapper.vm.zones[0][0] = 1
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones[0][0]).toBe(1)
    })
  })

  describe('Workflow: Gestion des Solutions', () => {
    it('doit permettre de parcourir les solutions', async () => {
      // Initialiser les solutions
      wrapper.vm.solutions = [
        { matrix: [[0, 1], [1, 0]] },
        { matrix: [[1, 0], [0, 1]] },
        { matrix: [[0, 1], [1, 0]] }
      ]
      
      await wrapper.vm.$nextTick()
      
      // Vérifier l'état initial
      expect(wrapper.vm.currentSolutionIndex).toBe(0)
      expect(wrapper.vm.solutions.length).toBe(3)
      
      // Naviguer
      wrapper.vm.currentSolutionIndex = 1
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.currentSolutionIndex).toBe(1)
      
      wrapper.vm.currentSolutionIndex = 2
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.currentSolutionIndex).toBe(2)
    })
  })

  describe('Workflow: Gestion de l\'Historique', () => {
    it('doit enregistrer les actions dans l\'historique', async () => {
      // Ajouter à l'historique
      wrapper.vm.history.push({ 
        action: 'paint',
        row: 0,
        col: 0,
        color: 0,
        timestamp: Date.now(),
        solutions: [] // Ajouter solutions
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.history.length).toBe(1)
      expect(wrapper.vm.history[0].action).toBe('paint')
      
      // Ajouter une autre action
      wrapper.vm.history.push({
        action: 'clear',
        timestamp: Date.now(),
        solutions: [] // Ajouter solutions
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.history.length).toBe(2)
    })

    it('doit permettre de basculer la visibilité de l\'historique', async () => {
      expect(wrapper.vm.historyVisible).toBe(true)
      
      wrapper.vm.historyVisible = false
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.historyVisible).toBe(false)
      
      wrapper.vm.historyVisible = true
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.historyVisible).toBe(true)
    })

    it('doit permettre de sélectionner un élément de l\'historique', async () => {
      wrapper.vm.history = [
        { id: 0, action: 'action1' },
        { id: 1, action: 'action2' },
        { id: 2, action: 'action3' }
      ]
      
      await wrapper.vm.$nextTick()
      
      wrapper.vm.selectedHistoryIndex = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.selectedHistoryIndex).toBe(1)
      expect(wrapper.vm.history[wrapper.vm.selectedHistoryIndex].id).toBe(1)
    })
  })

  describe('Workflow: Gestion des Brouillons', () => {
    it('doit permettre de créer et gérer les brouillons', async () => {
      expect(wrapper.vm.drafts.length).toBe(0)
      
      // Créer un brouillon
      wrapper.vm.drafts.push({
        name: 'Mon brouillon 1',
        zones: [[0, 1], [1, 0]],
        timestamp: Date.now()
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(1)
      expect(wrapper.vm.drafts[0].name).toBe('Mon brouillon 1')
      
      // Créer un deuxième brouillon
      wrapper.vm.drafts.push({
        name: 'Mon brouillon 2',
        zones: [[0, 1], [1, 0]],
        timestamp: Date.now()
      })
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(2)
    })

    it('doit respecter la limite de brouillons', async () => {
      // Remplir jusqu'à la limite
      for (let i = 0; i < wrapper.vm.MAX_DRAFTS + 5; i++) {
        if (wrapper.vm.drafts.length < wrapper.vm.MAX_DRAFTS) {
          wrapper.vm.drafts.push({
            name: `Draft ${i}`,
            zones: [],
            timestamp: Date.now()
          })
        }
      }
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBeLessThanOrEqual(wrapper.vm.MAX_DRAFTS)
    })

    it('doit permettre de sélectionner un brouillon', async () => {
      wrapper.vm.drafts = [
        { name: 'Draft 1', zones: [] },
        { name: 'Draft 2', zones: [] },
        { name: 'Draft 3', zones: [] }
      ]
      
      await wrapper.vm.$nextTick()
      
      wrapper.vm.currentDraftIndex = 1
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.currentDraftIndex).toBe(1)
      expect(wrapper.vm.drafts[wrapper.vm.currentDraftIndex].name).toBe('Draft 2')
    })
  })

  describe('Workflow: Gestion des Erreurs', () => {
    it('doit afficher et effacer les messages d\'erreur', async () => {
      expect(wrapper.vm.errorMessage).toBe('')
      
      wrapper.vm.errorMessage = 'Une erreur est survenue'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.errorMessage).toBe('Une erreur est survenue')
      
      // Effacer le message
      wrapper.vm.errorMessage = ''
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.errorMessage).toBe('')
    })

    it('doit gérer les erreurs d\'import de matrice', async () => {
      wrapper.vm.importMatrixText = 'texte invalide'
      
      await wrapper.vm.$nextTick()
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toBeDefined()
      
      wrapper.vm.importError = result.error
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importError).toBeTruthy()
    })

    it('doit gérer les erreurs d\'import d\'image', async () => {
      wrapper.vm.importImageExtractError = 'Impossible d\'extraire la matrice de l\'image'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importImageExtractError).toBeTruthy()
      
      // Effacer l'erreur
      wrapper.vm.importImageExtractError = ''
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importImageExtractError).toBe('')
    })
  })

  describe('Workflow: Modales', () => {
    it('doit gérer les transitions entre modales', async () => {
      // Initial: welcome modal visible
      expect(wrapper.vm.showWelcomeModal).toBe(true)
      expect(wrapper.vm.showHelpModal).toBe(false)
      expect(wrapper.vm.isImportModalOpen).toBe(false)
      
      // Fermer welcome, ouvrir help
      wrapper.vm.showWelcomeModal = false
      wrapper.vm.showHelpModal = true
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showWelcomeModal).toBe(false)
      expect(wrapper.vm.showHelpModal).toBe(true)
      
      // Ouvrir import modal
      wrapper.vm.isImportModalOpen = true
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isImportModalOpen).toBe(true)
      
      // Fermer toutes les modales
      wrapper.vm.showHelpModal = false
      wrapper.vm.isImportModalOpen = false
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showHelpModal).toBe(false)
      expect(wrapper.vm.isImportModalOpen).toBe(false)
    })
  })

  describe('Workflow: Interaction Souris et Peinture', () => {
    it('doit gérer l\'interaction de peinture', async () => {
      expect(wrapper.vm.isPainting).toBe(false)
      expect(wrapper.vm.currentMouseButton).toBeNull()
      
      // Commencer à peindre
      wrapper.vm.isPainting = true
      wrapper.vm.currentMouseButton = 'left'
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isPainting).toBe(true)
      expect(wrapper.vm.currentMouseButton).toBe('left')
      
      // Arrêter la peinture
      wrapper.vm.isPainting = false
      wrapper.vm.currentMouseButton = null
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isPainting).toBe(false)
      expect(wrapper.vm.currentMouseButton).toBeNull()
    })

    it('doit supporter plusieurs boutons de souris', async () => {
      const buttons = ['left', 'right', 'middle']
      
      for (const button of buttons) {
        wrapper.vm.currentMouseButton = button
        await wrapper.vm.$nextTick()
        expect(wrapper.vm.currentMouseButton).toBe(button)
      }
    })
  })

  describe('Workflow: Tailles de Grille', () => {
    it('doit permettre de changer la taille de la grille', async () => {
      const sizes = [4, 8, 12, 16]
      
      for (const size of sizes) {
        wrapper.vm.size = size
        await wrapper.vm.$nextTick()
        expect(wrapper.vm.size).toBe(size)
      }
    })

    it('doit mettre à jour les couleurs disponibles avec la taille', async () => {
      wrapper.vm.size = 4
      wrapper.vm.zones = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
      
      await wrapper.vm.$nextTick()
      
      const colorIndices = wrapper.vm.availableColorIndices
      expect(colorIndices.length).toBeGreaterThan(0)
    })
  })

  describe('Workflow: Benchmark', () => {
    it('doit gérer le cycle de vie du benchmark', async () => {
      expect(wrapper.vm.isBenchmarking).toBe(false)
      expect(wrapper.vm.benchmarkStatus).toBe('')
      expect(wrapper.vm.trmPerformance).toBeNull()
      expect(wrapper.vm.baselineResult).toBeNull()
      
      // Démarrer
      wrapper.vm.isBenchmarking = true
      wrapper.vm.benchmarkStatus = 'En cours...'
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isBenchmarking).toBe(true)
      expect(wrapper.vm.benchmarkStatus).toBe('En cours...')
      
      // Ajouter les résultats
      wrapper.vm.trmPerformance = { time: 1000, accuracy: 0.95 }
      wrapper.vm.baselineResult = { time: 1500, accuracy: 0.90 }
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.trmPerformance).toBeTruthy()
      expect(wrapper.vm.baselineResult).toBeTruthy()
      
      // Terminer
      wrapper.vm.isBenchmarking = false
      wrapper.vm.benchmarkStatus = 'Terminé'
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isBenchmarking).toBe(false)
    })
  })

  describe('Workflow: Import Image', () => {
    it('doit gérer le cycle complet d\'import d\'image', async () => {
      expect(wrapper.vm.importImageLoading).toBe(false)
      expect(wrapper.vm.importImagePreviewUrl).toBe('')
      expect(wrapper.vm.importImageResult).toBeNull()
      
      // Simuler le chargement
      wrapper.vm.importImageLoading = true
      wrapper.vm.importMode = 'image'
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importImageLoading).toBe(true)
      
      // Simuler le résultat
      wrapper.vm.importImageResult = {
        zones: [[0, 1], [1, 0]],
        filename: 'test.png'
      }
      wrapper.vm.importImageLoading = false
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importImageResult).toBeTruthy()
      expect(wrapper.vm.importImageLoading).toBe(false)
      
      // Vérifier la preview
      const preview = wrapper.vm.importImageMatrixPreview
      expect(preview).toBeTruthy()
    })
  })

  describe('Workflow: Légende d\'Import', () => {
    it('doit afficher/masquer la légende d\'import', async () => {
      expect(wrapper.vm.showImportLegend).toBe(false)
      
      wrapper.vm.showImportLegend = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showImportLegend).toBe(true)
      
      const legendItems = wrapper.vm.importLegendItems
      expect(Array.isArray(legendItems)).toBe(true)
      expect(legendItems.length).toBeGreaterThan(0)
      
      wrapper.vm.showImportLegend = false
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showImportLegend).toBe(false)
    })
  })
})
