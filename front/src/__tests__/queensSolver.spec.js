import { describe, it, expect } from 'vitest'
import { hasSolution } from '../utils/queensSolver.js'
import { generateRandomConnectedPattern } from '../utils/generateZones.js'
import { createSeededRng } from '../utils/seededRandom.js'

describe('hasSolution', () => {
  it('grille 1×1 : trivialement solvable', () => {
    expect(hasSolution(1, [[0]])).toBe(true)
  })

  it('grille 2×2 : jamais solvable (2 colonnes → toute paire de reines est adjacente)', () => {
    expect(hasSolution(2, [[0, 1], [1, 0]])).toBe(false)
  })

  it('une seule zone couvrant toute la grille (pas assez de zones distinctes) : insolvable', () => {
    const zones = [
      [0, 0, 0],
      [0, 0, 0],
      [0, 0, 0],
    ]
    expect(hasSolution(3, zones)).toBe(false)
  })

  it('grille contenant une case vide (-1) : insolvable par construction', () => {
    const zones = [
      [0, 1, 2],
      [0, 1, -1],
      [0, 1, 2],
    ]
    expect(hasSolution(3, zones)).toBe(false)
  })

  it('taille/format invalides : retourne false sans lever', () => {
    expect(hasSolution(0, [])).toBe(false)
    expect(hasSolution(3, [[0, 1, 2]])).toBe(false)
  })

  it('une grille générée avec une seed fixe est reproductiblement évaluée', () => {
    const zones = generateRandomConnectedPattern(6, createSeededRng('queensSolver-fixture'))
    const result = hasSolution(6, zones)
    expect(typeof result).toBe('boolean')
    // Même entrée → même sortie (déterminisme du solveur lui-même).
    expect(hasSolution(6, zones)).toBe(result)
  })
})
