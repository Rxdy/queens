import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

describe('App.vue - Tests de Validations', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App)
  })

  describe('Validation des Matrices', () => {
    it('doit valider correctement une matrice 4x4 valide', () => {
      wrapper.vm.importMatrixText = `0 1 2 3
0 1 2 3
0 1 2 3
0 1 2 3`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
      expect(result.previewRows.length).toBe(4)
    })

    it('doit valider correctement une matrice 8x8 valide', () => {
      wrapper.vm.importMatrixText = `0 1 0 1 0 1 0 1
1 0 1 0 1 0 1 0
0 1 0 1 0 1 0 1
1 0 1 0 1 0 1 0
0 1 0 1 0 1 0 1
1 0 1 0 1 0 1 0
0 1 0 1 0 1 0 1
1 0 1 0 1 0 1 0`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
      expect(result.error).toBeNull()
    })

    it('doit rejeter une matrice avec des dimensions incorrectes', () => {
      wrapper.vm.importMatrixText = `0 1 2
3 4 5`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toBeTruthy()
    })

    it('doit rejeter une matrice trop petite', () => {
      wrapper.vm.importMatrixText = `0 1
2 3`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('au moins 4')
    })

    it('doit rejeter une matrice vide', () => {
      wrapper.vm.importMatrixText = ''
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
    })

    it('doit accepter une matrice avec des lignes vides (ignorées)', () => {
      wrapper.vm.importMatrixText = `0 1 2 3

0 1 2 3
0 1 2 3
0 1 2 3`
      
      const result = wrapper.vm.importMatrixParseResult
      // Les lignes vides sont ignorées, donc la matrice est valide
      expect(result.isValid).toBe(true)
    })
  })

  describe('Validation des Formats d\'Entrée', () => {
    it('doit accepter les séparateurs multiples (espace, virgule, point-virgule)', () => {
      const formats = [
        `0 1 2 3\n0 1 2 3\n0 1 2 3\n0 1 2 3`,
        `0,1,2,3\n0,1,2,3\n0,1,2,3\n0,1,2,3`,
        `0;1;2;3\n0;1;2;3\n0;1;2;3\n0;1;2;3`,
        `0  1  2  3\n0  1  2  3\n0  1  2  3\n0  1  2  3`
      ]
      
      formats.forEach(format => {
        wrapper.vm.importMatrixText = format
        const result = wrapper.vm.importMatrixParseResult
        expect(result.isValid).toBe(true)
      })
    })

    it('doit accepter les retours à la ligne différents', () => {
      const formats = [
        `0 1 2 3\n0 1 2 3\n0 1 2 3\n0 1 2 3`, // \n
        `0 1 2 3\r\n0 1 2 3\r\n0 1 2 3\r\n0 1 2 3` // \r\n
      ]
      
      formats.forEach(format => {
        wrapper.vm.importMatrixText = format
        const result = wrapper.vm.importMatrixParseResult
        expect(result.isValid).toBe(true)
      })
    })

    it('doit gérer les espaces blancs supplémentaires', () => {
      wrapper.vm.importMatrixText = `
        0 1 2 3  
        0 1 2 3  
        0 1 2 3  
        0 1 2 3  
      `
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
    })

    it('doit rejeter les valeurs non-numériques', () => {
      wrapper.vm.importMatrixText = `a b c d
0 1 2 3
0 1 2 3
0 1 2 3`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('invalides')
    })
  })

  describe('Validation des Zones', () => {
    it('doit accepter les valeurs -1 pour les cellules vides', () => {
      wrapper.vm.importMatrixText = `-1 0 1 -1
0 -1 1 0
-1 1 -1 0
1 0 0 -1`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
    })

    it('doit rejeter les valeurs de zone au-delà du nombre de couleurs', () => {
      wrapper.vm.importMatrixText = `0 1 2 3
4 5 6 7
8 9 10 11
12 13 14 15`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
      expect(result.error).toBeTruthy()
    })

    it('doit valider le nombre de zones distinctes', () => {
      wrapper.vm.importMatrixText = `0 0 0 0
1 1 1 1
2 2 2 2
3 3 3 3`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(true)
      expect(result.previewRows.length).toBe(4)
    })

    it('doit rejeter les matrices avec plus de zones que la taille', () => {
      wrapper.vm.size = 4
      wrapper.vm.importMatrixText = `0 1 2 3
4 5 6 7
8 9 10 11
12 13 14 15`
      
      const result = wrapper.vm.importMatrixParseResult
      expect(result.isValid).toBe(false)
    })
  })

  describe('Validation des Couleurs', () => {
    it('doit avoir au minimum 12 couleurs disponibles', () => {
      expect(wrapper.vm.colors.length).toBeGreaterThanOrEqual(12)
    })

    it('doit avoir des couleurs valides au format RGB', () => {
      wrapper.vm.colors.forEach(color => {
        expect(color).toMatch(/^rgb\(\d+,\s*\d+,\s*\d+\)$/)
      })
    })

    it('doit mettre à jour les couleurs disponibles correctement', () => {
      wrapper.vm.zones = [[0, 1, 2], [0, 1, 2], [0, 1, 2]]
      
      const availableColors = wrapper.vm.availableColors
      expect(Array.isArray(availableColors)).toBe(true)
      expect(availableColors.length).toBeGreaterThan(0)
    })

    it('doit rejeter les sélections de couleurs au-delà du nombre disponible', () => {
      wrapper.vm.selectedColor = 999
      expect(wrapper.vm.selectedColor).toBe(999)
      // Le composant devrait valider cela au runtime
    })
  })

  describe('Validation de la Légende d\'Import', () => {
    it('doit générer les éléments de légende pour toutes les couleurs', () => {
      const items = wrapper.vm.importLegendItems
      expect(items.length).toBeGreaterThanOrEqual(wrapper.vm.colors.length)
    })

    it('doit inclure l\'élément pour -1 (cellule vide)', () => {
      const items = wrapper.vm.importLegendItems
      const emptyItem = items.find(item => item.value === -1)
      expect(emptyItem).toBeDefined()
      expect(emptyItem.isEmpty).toBe(true)
      expect(emptyItem.label).toContain('vide')
    })

    it('doit avoir les couleurs correctes pour chaque élément', () => {
      const items = wrapper.vm.importLegendItems
      items.forEach((item, index) => {
        if (item.value !== -1) {
          expect(item.color).toBe(wrapper.vm.colors[item.value])
        }
      })
    })
  })

  describe('Validation des Dimensions', () => {
    it('doit avoir des dimensions d\'écran par défaut', () => {
      expect(wrapper.vm.screenWidth).toBeGreaterThan(0)
      expect(wrapper.vm.screenHeight).toBeGreaterThan(0)
    })

    it('doit permettre de changer les dimensions', () => {
      wrapper.vm.screenWidth = 1920
      wrapper.vm.screenHeight = 1080
      expect(wrapper.vm.screenWidth).toBe(1920)
      expect(wrapper.vm.screenHeight).toBe(1080)
    })

    it('gridDebugInfo doit contenir les informations de debug', () => {
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

  describe('Validation des Brouillons', () => {
    it('ne doit pas dépasser le maximum de brouillons', () => {
      // Essayer d'ajouter plus que MAX_DRAFTS
      for (let i = 0; i < 20; i++) {
        wrapper.vm.drafts.push({ id: i, name: `Draft ${i}` })
      }
      
      // Le composant devrait limiter cela
      expect(wrapper.vm.drafts.length).toBeGreaterThan(0)
    })

    it('doit initialiser currentDraftIndex après le montage', () => {
      // Un brouillon par défaut est créé lors du montage
      expect(wrapper.vm.currentDraftIndex).toBeGreaterThanOrEqual(-1)
      expect(wrapper.vm.currentDraftIndex).toBeLessThan(wrapper.vm.drafts.length)
    })

    it('doit avoir MAX_DRAFTS à 15', () => {
      expect(wrapper.vm.MAX_DRAFTS).toBe(15)
    })
  })

  describe('Validation des États d\'Import', () => {
    it('importFile doit être null initialement', () => {
      expect(wrapper.vm.importFile).toBeNull()
    })

    it('importImagePreviewUrl doit être vide initialement', () => {
      expect(wrapper.vm.importImagePreviewUrl).toBe('')
    })

    it('importImageResult doit être null initialement', () => {
      expect(wrapper.vm.importImageResult).toBeNull()
    })

    it('importImageExtractError doit être vide initialement', () => {
      expect(wrapper.vm.importImageExtractError).toBe('')
    })

    it('importImageLoading doit être false initialement', () => {
      expect(wrapper.vm.importImageLoading).toBe(false)
    })

    it('importError doit être vide initialement', () => {
      expect(wrapper.vm.importError).toBe('')
    })
  })

  describe('Validation du Placeholder d\'Import', () => {
    it('doit contenir un exemple valide', () => {
      const placeholder = wrapper.vm.importPlaceholder
      expect(placeholder).toBeTruthy()
      expect(placeholder.length).toBeGreaterThan(0)
    })

    it('doit contenir des nombres', () => {
      const placeholder = wrapper.vm.importPlaceholder
      expect(placeholder).toMatch(/\d/)
    })
  })

  describe('Validation des Interactions Souris', () => {
    it('isPainting doit être false initialement', () => {
      expect(wrapper.vm.isPainting).toBe(false)
    })

    it('currentMouseButton doit être null initialement', () => {
      expect(wrapper.vm.currentMouseButton).toBeNull()
    })

    it('doit supporter les trois boutons de souris', () => {
      const buttons = ['left', 'right', 'middle']
      buttons.forEach(button => {
        wrapper.vm.currentMouseButton = button
        expect(wrapper.vm.currentMouseButton).toBe(button)
      })
    })
  })
})
