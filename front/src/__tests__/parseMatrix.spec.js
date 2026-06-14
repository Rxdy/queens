import { describe, it, expect } from 'vitest'
import { parseMatrixTextInput } from '../utils/parseMatrix.js'

const grid4 = `0 0 1 1
0 2 2 1
3 2 2 1
3 3 3 1`

describe('parseMatrixTextInput', () => {
  describe('cas valides', () => {
    it('parse une matrice 4×4 sans erreur', () => {
      const result = parseMatrixTextInput(grid4)
      expect(result).toHaveLength(4)
      expect(result[0]).toHaveLength(4)
    })

    it('normalise les identifiants de zone à partir de 0', () => {
      const result = parseMatrixTextInput(grid4)
      const flat = result.flat()
      const zones = [...new Set(flat.filter(v => v !== -1))].sort((a, b) => a - b)
      expect(zones).toEqual([0, 1, 2, 3])
    })

    it('remet les identifiants à zéro même si les valeurs sources sont espacées', () => {
      // Valeurs 5, 6, 7, 8 → doivent être normalisées en 0, 1, 2, 3
      const text = `5 5 6 6
5 7 7 6
8 7 7 6
8 8 8 6`
      const result = parseMatrixTextInput(text)
      const flat = result.flat()
      const zones = [...new Set(flat)].sort((a, b) => a - b)
      expect(zones).toEqual([0, 1, 2, 3])
    })

    it('conserve les cellules vides (-1)', () => {
      const text = `-1 0 1 1
0 2 2 1
3 2 2 1
3 3 3 1`
      const result = parseMatrixTextInput(text)
      expect(result[0][0]).toBe(-1)
    })

    it('accepte les séparateurs virgule et point-virgule', () => {
      const text = `0,0,1,1
0;2;2;1
3 2 2 1
3 3 3 1`
      expect(() => parseMatrixTextInput(text)).not.toThrow()
    })
  })

  describe('erreurs de structure', () => {
    it('lève une erreur si la matrice est vide', () => {
      expect(() => parseMatrixTextInput('')).toThrow('vide')
      expect(() => parseMatrixTextInput('   \n  ')).toThrow('vide')
    })

    it('lève une erreur si non carrée (4 lignes, 3 colonnes)', () => {
      const text = `0 1 2
0 1 2
0 1 2
0 1 2`
      expect(() => parseMatrixTextInput(text)).toThrow('carrée')
    })

    it('lève une erreur si taille < 4', () => {
      const text = `0 1 2
0 1 2
0 1 2`
      expect(() => parseMatrixTextInput(text)).toThrow('4×4')
    })

    it('lève une erreur si trop de zones distinctes', () => {
      // Grille 4×4 avec 5 zones différentes → impossible
      const text = `0 0 1 1
2 2 3 3
4 4 0 0
1 1 2 2`
      expect(() => parseMatrixTextInput(text)).toThrow('zones distinctes')
    })
  })

  describe('erreurs de valeurs', () => {
    it('lève une erreur pour un token non entier', () => {
      const text = `0 0 abc 1
0 2 2 1
3 2 2 1
3 3 3 1`
      expect(() => parseMatrixTextInput(text)).toThrow('invalide')
    })

    it('lève une erreur pour une valeur < -1', () => {
      const text = `0 0 1 1
0 -2 2 1
3 2 2 1
3 3 3 1`
      expect(() => parseMatrixTextInput(text)).toThrow('supérieures ou égales à -1')
    })

    it('lève une erreur si identifiant >= maxColorId', () => {
      const text = `0 0 1 1
0 2 2 1
3 2 2 1
3 3 3 1`
      // maxColorId = 2 → zone 3 est invalide
      expect(() => parseMatrixTextInput(text, 2)).toThrow('inférieurs à 2')
    })
  })
})
