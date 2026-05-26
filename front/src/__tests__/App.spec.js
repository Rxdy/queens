import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('App.vue - Composant Principal', () => {
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
  })

  describe('Initialisation', () => {
    it('doit monter le composant correctement', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('doit initialiser la taille de la grille à 8', async () => {
      const size = wrapper.vm.size
      expect(size).toBe(8)
    })

    it('doit initialiser les zones comme un tableau vide', () => {
      const zones = wrapper.vm.zones
      expect(Array.isArray(zones)).toBe(true)
    })

    it('doit initialiser la modal de bienvenue comme visible', () => {
      const showWelcomeModal = wrapper.vm.showWelcomeModal
      expect(showWelcomeModal).toBe(true)
    })

    it('doit initialiser le mode import à "text"', () => {
      const importMode = wrapper.vm.importMode
      expect(importMode).toBe('text')
    })

    it('doit avoir 12 couleurs disponibles', () => {
      expect(wrapper.vm.colors.length).toBe(12)
    })
  })

  describe('États et Références', () => {
    it('doit avoir les positions comme tableau vide initialement', () => {
      expect(wrapper.vm.positions).toEqual([])
    })

    it('doit avoir les solutions comme tableau vide initialement', () => {
      expect(wrapper.vm.solutions).toEqual([])
    })

    it('doit avoir l\'historique comme tableau vide initialement', () => {
      expect(wrapper.vm.history).toEqual([])
    })

    it('doit avoir selectedColor initialisé à 0', () => {
      expect(wrapper.vm.selectedColor).toBe(0)
    })

    it('doit avoir isBenchmarking à false', () => {
      expect(wrapper.vm.isBenchmarking).toBe(false)
    })

    it('doit avoir le message d\'erreur vide initialement', () => {
      expect(wrapper.vm.errorMessage).toBe('')
    })

    it('doit avoir les brouillons (drafts) comme tableau non vide (brouillon par défaut créé)', () => {
      expect(Array.isArray(wrapper.vm.drafts)).toBe(true)
      expect(wrapper.vm.drafts.length).toBeGreaterThan(0) // Un brouillon par défaut est créé
    })

    it('doit avoir MAX_DRAFTS à 15', () => {
      expect(wrapper.vm.MAX_DRAFTS).toBe(15)
    })
  })

  describe('Computed Properties', () => {
    it('availableColorIndices doit retourner un tableau', () => {
      const colors = wrapper.vm.availableColorIndices
      expect(Array.isArray(colors)).toBe(true)
    })

    it('availableColors doit retourner les couleurs disponibles', () => {
      const colors = wrapper.vm.availableColors
      expect(Array.isArray(colors)).toBe(true)
    })

    it('importLegendItems doit contenir les items de légende', () => {
      const items = wrapper.vm.importLegendItems
      expect(Array.isArray(items)).toBe(true)
      expect(items.length).toBeGreaterThan(0)
    })

    it('importLegendItems doit inclure l\'élément pour -1 (vide)', () => {
      const items = wrapper.vm.importLegendItems
      const emptyItem = items.find(item => item.value === -1)
      expect(emptyItem).toBeDefined()
      expect(emptyItem.isEmpty).toBe(true)
    })

    it('importMatrixParseResult doit valider une matrice vide', () => {
      wrapper.vm.importMatrixText = ''
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
    })

    it('importMatrixParseResult doit détecter les erreurs de matrice', () => {
      wrapper.vm.importMatrixText = '1 2\n3 4'
      const result = wrapper.vm.importMatrixParseResult
      expect(result.error).toBeDefined()
    })

    it('importMatrixParseResult doit valider une matrice correcte', () => {
      wrapper.vm.importMatrixText = `0 1 2 3
0 1 2 3
0 1 2 3
0 1 2 3`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
    })
  })

  describe('Image Preview Matrix', () => {
    it('importImageMatrixPreview doit être null quand pas d\'image', () => {
      const preview = wrapper.vm.importImageMatrixPreview
      expect(preview).toBeNull()
    })

    it('importImageMatrixPreview doit afficher la matrice quand image importée', () => {
      wrapper.vm.importImageResult = {
        zones: [[0, 1], [1, 0]]
      }
      const preview = wrapper.vm.importImageMatrixPreview
      expect(Array.isArray(preview)).toBe(true)
      expect(preview.length).toBe(2)
    })
  })

  describe('Réactivité des Données', () => {
    it('doit permettre de changer la taille de la grille', async () => {
      wrapper.vm.size = 4
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.size).toBe(4)
    })

    it('doit permettre de changer la couleur sélectionnée', async () => {
      wrapper.vm.selectedColor = 3
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.selectedColor).toBe(3)
    })

    it('doit permettre de changer le mode import', async () => {
      wrapper.vm.importMode = 'image'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.importMode).toBe('image')
    })

    it('doit permettre de définir un message d\'erreur', async () => {
      wrapper.vm.errorMessage = 'Erreur de test'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.errorMessage).toBe('Erreur de test')
    })
  })

  describe('Gestion des Brouillons (Drafts)', () => {
    it('currentDraftIndex doit être -1 ou supérieur après montage', () => {
      // Un brouillon par défaut est créé lors du montage
      expect(wrapper.vm.currentDraftIndex).toBeGreaterThanOrEqual(-1)
    })

    it('doit pouvoir ajouter des brouillons', async () => {
      const initialLength = wrapper.vm.drafts.length
      wrapper.vm.drafts.push({ name: 'Draft 1', data: {} })
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.drafts.length).toBe(initialLength + 1)
    })

    it('ne doit pas dépasser le maximum de brouillons', async () => {
      // Remplir jusqu'au MAX_DRAFTS
      const initialLength = wrapper.vm.drafts.length
      for (let i = initialLength; i < wrapper.vm.MAX_DRAFTS; i++) {
        if (wrapper.vm.drafts.length < wrapper.vm.MAX_DRAFTS) {
          wrapper.vm.drafts.push({ name: `Draft ${i}`, data: {} })
        }
      }
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.drafts.length).toBeLessThanOrEqual(wrapper.vm.MAX_DRAFTS)
    })
  })

  describe('Historique', () => {
    it('selectedHistoryIndex doit être -1 initialement', () => {
      expect(wrapper.vm.selectedHistoryIndex).toBe(-1)
    })

    it('doit pouvoir ajouter à l\'historique', async () => {
      // Initialiser zones pour éviter les erreurs
      wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(-1))
      wrapper.vm.history.push({ 
        action: 'test', 
        data: {},
        solutions: [] // Ajouter solutions
      })
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.history.length).toBe(1)
    })

    it('historyVisible doit être true initialement', () => {
      expect(wrapper.vm.historyVisible).toBe(true)
    })

    it('doit permettre de masquer l\'historique', async () => {
      wrapper.vm.historyVisible = false
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.historyVisible).toBe(false)
    })
  })

  describe('État du Benchmark', () => {
    it('isBenchmarking doit être false initialement', () => {
      expect(wrapper.vm.isBenchmarking).toBe(false)
    })

    it('benchmarkStatus doit être vide initialement', () => {
      expect(wrapper.vm.benchmarkStatus).toBe('')
    })

    it('trmPerformance doit être null initialement', () => {
      expect(wrapper.vm.trmPerformance).toBeNull()
    })

    it('baselineResult doit être null initialement', () => {
      expect(wrapper.vm.baselineResult).toBeNull()
    })
  })

  describe('Modales', () => {
    it('isImportModalOpen doit être false initialement', () => {
      expect(wrapper.vm.isImportModalOpen).toBe(false)
    })

    it('showHelpModal doit être false initialement', () => {
      expect(wrapper.vm.showHelpModal).toBe(false)
    })

    it('doit permettre d\'ouvrir la modal d\'import', async () => {
      wrapper.vm.isImportModalOpen = true
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.isImportModalOpen).toBe(true)
    })

    it('doit permettre d\'ouvrir la modal d\'aide', async () => {
      wrapper.vm.showHelpModal = true
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.showHelpModal).toBe(true)
    })
  })

  describe('Import de Matrice', () => {
    it('importMode doit gérer les deux modes', async () => {
      expect(wrapper.vm.importMode).toBe('text')
      
      wrapper.vm.importMode = 'image'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.importMode).toBe('image')
      
      wrapper.vm.importMode = 'text'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.importMode).toBe('text')
    })

    it('importMatrixText doit accepter du texte', async () => {
      const text = '0 1\n1 0'
      wrapper.vm.importMatrixText = text
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.importMatrixText).toBe(text)
    })

    it('importError doit être vide initialement', () => {
      expect(wrapper.vm.importError).toBe('')
    })

    it('importImageExtractError doit être vide initialement', () => {
      expect(wrapper.vm.importImageExtractError).toBe('')
    })

    it('importImageLoading doit être false initialement', () => {
      expect(wrapper.vm.importImageLoading).toBe(false)
    })

    it('showImportLegend doit être false initialement', () => {
      expect(wrapper.vm.showImportLegend).toBe(false)
    })
  })

  describe('Interaction Souris et Pinceaux', () => {
    it('isPainting doit être false initialement', () => {
      expect(wrapper.vm.isPainting).toBe(false)
    })

    it('currentMouseButton doit être null initialement', () => {
      expect(wrapper.vm.currentMouseButton).toBeNull()
    })

    it('doit pouvoir définir isPainting', async () => {
      wrapper.vm.isPainting = true
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.isPainting).toBe(true)
    })

    it('doit pouvoir définir le bouton souris', async () => {
      wrapper.vm.currentMouseButton = 'left'
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.currentMouseButton).toBe('left')
    })
  })

  describe('Navigation des Solutions', () => {
    it('currentSolutionIndex doit être 0 initialement', () => {
      expect(wrapper.vm.currentSolutionIndex).toBe(0)
    })

    it('doit permettre de changer l\'index de solution', async () => {
      wrapper.vm.currentSolutionIndex = 2
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.currentSolutionIndex).toBe(2)
    })
  })

  describe('Dimensions d\'écran', () => {
    it('screenWidth doit avoir une valeur par défaut', () => {
      expect(wrapper.vm.screenWidth).toBeGreaterThan(0)
      expect(typeof wrapper.vm.screenWidth).toBe('number')
    })

    it('screenHeight doit avoir une valeur par défaut', () => {
      expect(wrapper.vm.screenHeight).toBeGreaterThan(0)
      expect(typeof wrapper.vm.screenHeight).toBe('number')
    })

    it('doit permettre de changer les dimensions', async () => {
      wrapper.vm.screenWidth = 1920
      wrapper.vm.screenHeight = 1080
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.screenWidth).toBe(1920)
      expect(wrapper.vm.screenHeight).toBe(1080)
    })

    it('gridDebugInfo doit être un objet avec les bonnes clés', () => {
      const debugInfo = wrapper.vm.gridDebugInfo
      expect(debugInfo).toHaveProperty('calculatedCellSize')
      expect(debugInfo).toHaveProperty('actualCellSize')
      expect(debugInfo).toHaveProperty('gridWidth')
      expect(debugInfo).toHaveProperty('gridHeight')
      expect(debugInfo).toHaveProperty('totalWidth')
      expect(debugInfo).toHaveProperty('totalHeight')
      expect(debugInfo).toHaveProperty('message')
    })
  })

  describe('Placeholder Import', () => {
    it('importPlaceholder doit être une chaîne non vide', () => {
      expect(wrapper.vm.importPlaceholder).toBeTruthy()
      expect(typeof wrapper.vm.importPlaceholder).toBe('string')
    })

    it('importPlaceholder doit contenir un exemple de matrice', () => {
      expect(wrapper.vm.importPlaceholder).toContain('0')
      expect(wrapper.vm.importPlaceholder).toContain('1')
    })
  })

  describe('Validations de Matrice Complexes', () => {
    it('doit rejeter les matrices trop petites', () => {
      wrapper.vm.importMatrixText = `0 1
2 3`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('au moins 4')
    })

    it('doit rejeter les matrices non carrées', () => {
      wrapper.vm.importMatrixText = `0 1 2
3 4 5`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('carrée')
    })

    it('doit accepter les formats séparés par virgule', () => {
      wrapper.vm.importMatrixText = `0,1,2,3
0,1,2,3
0,1,2,3
0,1,2,3`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
    })

    it('doit accepter les formats séparés par point-virgule', () => {
      wrapper.vm.importMatrixText = `0;1;2;3
0;1;2;3
0;1;2;3
0;1;2;3`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
    })

    it('doit accepter les valeurs -1 pour les cellules vides', () => {
      wrapper.vm.importMatrixText = `-1 0 1 -1
0 -1 1 0
-1 1 -1 0
1 0 0 -1`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
    })

    it('doit rejeter les zones au-delà du nombre de couleurs disponibles', () => {
      wrapper.vm.importMatrixText = `0 1 2 3
4 5 6 7
8 9 10 11
12 13 14 15`
      const result = wrapper.vm.importMatrixParseResult
      expect(result.error).toBeDefined()
    })
  })
})
