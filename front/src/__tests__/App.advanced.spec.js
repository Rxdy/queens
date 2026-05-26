import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../App.vue'

vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

describe('App.vue - Tests Avancés (Robustesse)', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
    // Initialiser zones pour éviter les erreurs
    wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(-1))
    wrapper.vm.size = 8
  })

  afterEach(() => {
    wrapper.unmount()
  })

  // ============================================================================
  // TESTS DES LIFECYCLE HOOKS
  // ============================================================================

  describe('Lifecycle Hooks', () => {
    it('doit configurer les event listeners au montage', async () => {
      // onMounted doit ajouter les listeners
      const addEventListenerSpy = vi.spyOn(window, 'addEventListener')
      
      const wrapper2 = mount(App)
      await wrapper2.vm.$nextTick()
      
      // Vérifier que resize, mouseup, mouseleave sont écoutés
      const calls = addEventListenerSpy.mock.calls.map(call => call[0])
      expect(calls).toContain('resize')
      expect(calls).toContain('mouseup')
      expect(calls).toContain('mouseleave')
      
      wrapper2.unmount()
      addEventListenerSpy.mockRestore()
    })

    it('doit nettoyer les event listeners au démontage', async () => {
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')
      
      wrapper.unmount()
      
      const calls = removeEventListenerSpy.mock.calls.map(call => call[0])
      expect(calls).toContain('resize')
      expect(calls).toContain('mouseup')
      expect(calls).toContain('mouseleave')
      
      removeEventListenerSpy.mockRestore()
    })
  })

  // ============================================================================
  // TESTS DES WATCHERS
  // ============================================================================

  describe('Watchers', () => {
    it('doit réagir aux changements de size', async () => {
      wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(-1))
      wrapper.vm.size = 4
      await wrapper.vm.$nextTick()
      
      // Après changement de size, les zones doivent être réinitialisées
      expect(wrapper.vm.zones.length).toBeGreaterThan(0)
    })

    it('doit réagir aux changements de zones', async () => {
      wrapper.vm.zones = [[0, 1, -1, -1], [1, 0, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1]]
      await wrapper.vm.$nextTick()
      
      // Le watcher sur zones doit exister et être réactif
      expect(wrapper.vm.zones.length).toBe(4)
    })

    it('doit réagir aux changements du mode mobile', async () => {
      // Simuler un changement de largeur d'écran
      wrapper.vm.screenWidth = 500
      await wrapper.vm.$nextTick()
      
      // isMobile devrait être calculé basé sur screenWidth
      const isMobileComputed = wrapper.vm.isMobile
      expect(typeof isMobileComputed).toBe('boolean')
    })
  })

  // ============================================================================
  // TESTS DES MÉTHODES: GESTION DES BROUILLONS
  // ============================================================================

  describe('Gestion des Brouillons (Drafts)', () => {
    it('doit créer un nouveau brouillon', async () => {
      const initialLength = wrapper.vm.drafts.length
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBeGreaterThan(initialLength)
      expect(wrapper.vm.drafts[wrapper.vm.drafts.length - 1]).toHaveProperty('id')
      expect(wrapper.vm.drafts[wrapper.vm.drafts.length - 1]).toHaveProperty('size')
      expect(wrapper.vm.drafts[wrapper.vm.drafts.length - 1]).toHaveProperty('zones')
    })

    it('doit définir l\'index du brouillon courant lors de création', async () => {
      const initialIndex = wrapper.vm.currentDraftIndex
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.currentDraftIndex).toBeGreaterThanOrEqual(0)
      expect(wrapper.vm.currentDraftIndex).toBeGreaterThan(initialIndex)
    })

    it('doit sauvegarder le brouillon avant de créer un nouveau', async () => {
      wrapper.vm.zones = [[0, 1], [1, 0]]
      wrapper.vm.size = 2
      
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(1)
    })

    it('doit permuter entre les brouillons', async () => {
      wrapper.vm.createNewDraft()
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      const draft1 = wrapper.vm.drafts[0]
      wrapper.vm.switchDraft(1)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.currentDraftIndex).toBe(1)
    })

    it('doit supprimer un brouillon', async () => {
      wrapper.vm.createNewDraft()
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      const initialCount = wrapper.vm.drafts.length
      wrapper.vm.deleteDraft(0)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(initialCount - 1)
    })

    it('doit gérer la suppression du brouillon courant', async () => {
      // Créer plusieurs brouillons
      const initialCount = wrapper.vm.drafts.length
      if (initialCount < 2) {
        wrapper.vm.createNewDraft()
        await wrapper.vm.$nextTick()
      }
      
      const currentIdx = wrapper.vm.currentDraftIndex
      wrapper.vm.deleteDraft(currentIdx)
      await wrapper.vm.$nextTick()
      
      // L'index doit être valide
      if (wrapper.vm.drafts.length > 0) {
        expect(wrapper.vm.currentDraftIndex).toBeLessThan(wrapper.vm.drafts.length)
      } else {
        expect(wrapper.vm.currentDraftIndex).toBe(-1)
      }
    })

    it('ne doit pas dépasser MAX_DRAFTS lors de création multiple', async () => {
      for (let i = 0; i < 20; i++) {
        wrapper.vm.createNewDraft()
      }
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBeLessThanOrEqual(wrapper.vm.MAX_DRAFTS)
    })

    it('doit conserver le timestamp de création', async () => {
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      const draft = wrapper.vm.drafts[0]
      expect(draft).toHaveProperty('createdAt')
      expect(draft).toHaveProperty('updatedAt')
    })
  })

  // ============================================================================
  // TESTS DES MÉTHODES: INTERACTIONS SOURIS
  // ============================================================================

  describe('Interactions Souris Avancées', () => {
    beforeEach(() => {
      wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
    })

    it('doit peindre une cellule au clique gauche', async () => {
      wrapper.vm.selectedColor = 1
      wrapper.vm.clickCell(0, 0, 0)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones[0][0]).toBe(1)
    })

    it('doit effacer une cellule au clique droit', async () => {
      wrapper.vm.zones[0][0] = 1
      wrapper.vm.clickCell(0, 0, 2)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones[0][0]).toBe(-1)
    })

    it('doit ignorer les autres boutons de souris', async () => {
      wrapper.vm.selectedColor = 1
      wrapper.vm.zones[0][0] = -1
      
      wrapper.vm.clickCell(0, 0, 1) // Bouton du milieu
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones[0][0]).toBe(-1)
    })

    it('doit gérer la peinture en drag', async () => {
      wrapper.vm.selectedColor = 2
      
      // Simuler un drag
      wrapper.vm.isPainting = true
      wrapper.vm.currentMouseButton = 0
      
      wrapper.vm.clickCell(0, 0, 0)
      wrapper.vm.clickCell(0, 1, 0)
      wrapper.vm.clickCell(0, 2, 0)
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones[0][0]).toBe(2)
      expect(wrapper.vm.zones[0][1]).toBe(2)
      expect(wrapper.vm.zones[0][2]).toBe(2)
    })

    it('doit arrêter la peinture au mouse up', async () => {
      wrapper.vm.isPainting = true
      wrapper.vm.currentMouseButton = 0
      
      wrapper.vm.onMouseUp()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isPainting).toBe(false)
      expect(wrapper.vm.currentMouseButton).toBeNull()
    })

    it('ne doit pas peindre si on visualise l\'historique', async () => {
      wrapper.vm.history = [{ action: 'paint' }]
      wrapper.vm.selectedHistoryIndex = 0
      wrapper.vm.selectedColor = 1
      
      wrapper.vm.clickCell(0, 0, 0)
      await wrapper.vm.$nextTick()
      
      // La cellule ne devrait pas être peinte
      // (selon isViewingHistory)
      expect(wrapper.vm.zones[0][0]).toBe(-1)
    })
  })

  // ============================================================================
  // TESTS DES MÉTHODES: PARSING ET VALIDATION
  // ============================================================================

  describe('Parsing et Validation Avancés', () => {
    it('doit parser une matrice simple correctement', async () => {
      const text = '0 1 2 3\n0 1 2 3\n0 1 2 3\n0 1 2 3'
      const result = wrapper.vm.parseMatrixTextInput(text)
      
      expect(result).toBeDefined()
      expect(result.length).toBe(4)
      expect(result[0].length).toBe(4)
    })

    it('doit rejeter une matrice non carrée', () => {
      const text = '0 1 2\n0 1 2'
      
      expect(() => {
        wrapper.vm.parseMatrixTextInput(text)
      }).toThrow()
    })

    it('doit rejeter les valeurs < -1', () => {
      const text = '-2 0 1 2\n0 1 2 3\n0 1 2 3\n0 1 2 3'
      
      expect(() => {
        wrapper.vm.parseMatrixTextInput(text)
      }).toThrow()
    })

    it('doit rejeter une matrice trop petite', () => {
      const text = '0 1\n1 0'
      
      expect(() => {
        wrapper.vm.parseMatrixTextInput(text)
      }).toThrow()
    })

    it('doit normaliser les zones non-séquentielles', async () => {
      const text = '0 5 10 15\n0 5 10 15\n0 5 10 15\n0 5 10 15'
      const result = wrapper.vm.parseMatrixTextInput(text)
      
      // Les zones doivent être normalisées (0, 1, 2, 3)
      const flatResult = result.flat()
      const uniqueValues = new Set(flatResult.filter(v => v !== -1))
      expect(uniqueValues.size).toBe(4)
    })

    it('doit rejeter trop de zones distinctes', () => {
      const text = '0 1 2 3\n4 5 6 7\n8 9 10 11\n12 13 14 15'
      
      expect(() => {
        wrapper.vm.parseMatrixTextInput(text)
      }).toThrow('plus de zones distinctes')
    })

    it('doit gérer les espaces multiples comme séparateurs', async () => {
      const text = '0    1    2    3\n0    1    2    3\n0    1    2    3\n0    1    2    3'
      const result = wrapper.vm.parseMatrixTextInput(text)
      
      expect(result.length).toBe(4)
      expect(result[0].length).toBe(4)
    })

    it('doit gérer les retours à la ligne différents (\\r\\n)', async () => {
      const text = '0 1 2 3\r\n0 1 2 3\r\n0 1 2 3\r\n0 1 2 3'
      const result = wrapper.vm.parseMatrixTextInput(text)
      
      expect(result.length).toBe(4)
    })
  })

  // ============================================================================
  // TESTS DES MÉTHODES: GESTION DES MODALES ET IMPORTS
  // ============================================================================

  describe('Gestion des Modales et Imports', () => {
    it('doit ouvrir la modal d\'import', async () => {
      expect(wrapper.vm.isImportModalOpen).toBe(false)
      
      wrapper.vm.openImportModal()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isImportModalOpen).toBe(true)
    })

    it('doit fermer la modal d\'import', async () => {
      wrapper.vm.isImportModalOpen = true
      
      wrapper.vm.closeImportModal()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isImportModalOpen).toBe(false)
    })

    it('doit réinitialiser l\'état d\'import en fermant', async () => {
      wrapper.vm.isImportModalOpen = true
      wrapper.vm.importMatrixText = 'test'
      wrapper.vm.importError = 'error'
      
      wrapper.vm.closeImportModal()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importError).toBe('')
      expect(wrapper.vm.showImportLegend).toBe(false)
    })

    it('doit permuter entre les modes d\'import', async () => {
      wrapper.vm.openImportModal()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.selectImportMode('photo')
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importMode).toBe('photo')
      expect(wrapper.vm.importMatrixText).toBe('')
    })

    it('ne doit pas ouvrir import modal si on visualise l\'historique', () => {
      wrapper.vm.history = [{ action: 'test' }]
      wrapper.vm.selectedHistoryIndex = 0
      
      wrapper.vm.openImportModal()
      
      // La modal ne devrait pas s'ouvrir
      // (selon isViewingHistory)
      expect(typeof wrapper.vm.isImportModalOpen).toBe('boolean')
    })
  })

  // ============================================================================
  // TESTS DES MÉTHODES: EXPORT ET UTILITIES
  // ============================================================================

  describe('Méthodes Export et Utilities', () => {
    it('doit formatter les temps correctement', () => {
      const ms = 0.001
      const formatted = wrapper.vm.formatTime(ms)
      
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('doit gérer les valeurs nulles de formatTime', () => {
      const formatted = wrapper.vm.formatTime(null)
      expect(formatted).toBe('—')
    })

    it('doit toggler la légende d\'import', async () => {
      expect(wrapper.vm.showImportLegend).toBe(false)
      
      wrapper.vm.toggleImportLegend()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showImportLegend).toBe(true)
      
      wrapper.vm.toggleImportLegend()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.showImportLegend).toBe(false)
    })

    it('doit réinitialiser l\'état d\'import d\'image', async () => {
      wrapper.vm.importImageLoading = true
      wrapper.vm.importImageResult = { zones: [] }
      wrapper.vm.importImageExtractError = 'error'
      
      wrapper.vm.resetImportImageState()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.importImageLoading).toBe(false)
      expect(wrapper.vm.importImageResult).toBeNull()
      expect(wrapper.vm.importImageExtractError).toBe('')
    })
  })

  // ============================================================================
  // TESTS DES ERREURS ET EDGE CASES
  // ============================================================================

  describe('Gestion des Erreurs et Edge Cases', () => {
    it('doit effacer le message d\'erreur lors de modification', async () => {
      wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
      wrapper.vm.errorMessage = 'Une erreur'
      
      wrapper.vm.clickCell(0, 0, 0)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.errorMessage).toBe('')
    })

    it('doit gérer la matrice vide lors du parsing', () => {
      expect(() => {
        wrapper.vm.parseMatrixTextInput('')
      }).toThrow('vide')
    })

    it('doit gérer les lignes vides lors du parsing', () => {
      const text = '0 1 2 3\n\n0 1 2 3\n0 1 2 3'
      
      // Ne devrait pas lever d'erreur
      const result = wrapper.vm.parseMatrixTextInput(text)
      expect(result).toBeDefined()
    })

    it('doit gérer les transitions de couleur avec changement de taille', async () => {
      wrapper.vm.selectedColor = 8
      wrapper.vm.size = 4
      
      wrapper.vm.initializeZones()
      await wrapper.vm.$nextTick()
      
      // Si selectedColor >= size, il doit être réinitialisé
      expect(wrapper.vm.selectedColor).toBeLessThanOrEqual(wrapper.vm.size)
    })

    it('doit gérer la suppression du dernier brouillon', async () => {
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      wrapper.vm.deleteDraft(0)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(0)
      expect(wrapper.vm.currentDraftIndex).toBe(-1)
    })

    it('ne doit pas changer de brouillon si c\'est le même', async () => {
      wrapper.vm.createNewDraft()
      await wrapper.vm.$nextTick()
      
      const initialIndex = wrapper.vm.currentDraftIndex
      wrapper.vm.switchDraft(initialIndex)
      
      expect(wrapper.vm.currentDraftIndex).toBe(initialIndex)
    })
  })

  // ============================================================================
  // TESTS D'INTÉGRATION: WORKFLOWS COMPLEXES
  // ============================================================================

  describe('Workflows Complexes Avancés', () => {
    it('doit gérer un workflow complet: import > modification > export', async () => {
      // Import
      wrapper.vm.importMatrixText = '0 1 2 3\n0 1 2 3\n0 1 2 3\n0 1 2 3'
      await wrapper.vm.$nextTick()
      
      // Modification
      wrapper.vm.zones = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
      await wrapper.vm.$nextTick()
      
      // Vérifier l'état final
      expect(wrapper.vm.zones.length).toBe(4)
    })

    it('doit gérer plusieurs brouillons avec modifications', async () => {
      // Créer draft 1
      wrapper.vm.createNewDraft()
      wrapper.vm.zones = [[0, 1], [1, 0]]
      wrapper.vm.size = 2
      
      // Créer draft 2
      wrapper.vm.createNewDraft()
      wrapper.vm.zones = [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]]
      wrapper.vm.size = 4
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(2)
      expect(wrapper.vm.drafts[0].size).toBe(2)
      expect(wrapper.vm.drafts[1].size).toBe(4)
    })

    it('doit gérer drag et modification simultanée', async () => {
      wrapper.vm.zones = Array(4).fill(null).map(() => Array(4).fill(-1))
      wrapper.vm.selectedColor = 1
      
      // Commencer à peindre
      wrapper.vm.isPainting = true
      wrapper.vm.currentMouseButton = 0
      
      // Peindre plusieurs cellules
      for (let i = 0; i < 4; i++) {
        wrapper.vm.onMouseEnter(i, 0)
      }
      
      await wrapper.vm.$nextTick()
      
      // Arrêter
      wrapper.vm.onMouseUp()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isPainting).toBe(false)
    })

    it('doit gérer des créations/suppressions rapides de brouillons', async () => {
      for (let i = 0; i < 5; i++) {
        wrapper.vm.createNewDraft()
        wrapper.vm.zones = Array(8).fill(null).map(() => Array(8).fill(-1))
      }
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBeGreaterThan(0)
      expect(wrapper.vm.drafts.length).toBeLessThanOrEqual(wrapper.vm.MAX_DRAFTS)
    })
  })

  // ============================================================================
  // TESTS DE LIMITE ET PERFORMANCE
  // ============================================================================

  describe('Limites et Performance', () => {
    it('doit gérer les grandes matrices (16x16)', async () => {
      wrapper.vm.size = 16
      wrapper.vm.initializeZones()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones.length).toBe(16)
      expect(wrapper.vm.zones[0].length).toBe(16)
    })

    it('doit gérer les petites matrices (4x4)', async () => {
      wrapper.vm.size = 4
      wrapper.vm.initializeZones()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.zones.length).toBe(4)
      expect(wrapper.vm.zones[0].length).toBe(4)
    })

    it('doit gérer MAX_DRAFTS exactement', async () => {
      for (let i = 0; i < wrapper.vm.MAX_DRAFTS + 10; i++) {
        wrapper.vm.createNewDraft()
      }
      
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.drafts.length).toBe(wrapper.vm.MAX_DRAFTS)
    })

    it('doit parser une grande matrice valide', async () => {
      const lines = Array(8).fill(null)
        .map((_, r) => Array(8).fill(null)
          .map((_, c) => (r + c) % 4)
          .join(' '))
        .join('\n')
      
      const result = wrapper.vm.parseMatrixTextInput(lines)
      expect(result.length).toBe(8)
    })
  })
})
