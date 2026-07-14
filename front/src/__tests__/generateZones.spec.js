import { describe, it, expect } from 'vitest'
import { generateRandomConnectedPattern } from '../utils/generateZones.js'
import { createSeededRng } from '../utils/seededRandom.js'

describe('generateRandomConnectedPattern', () => {
  it('couvre toute la grille avec exactement `size` zones distinctes', () => {
    const size = 8
    const zones = generateRandomConnectedPattern(size)
    expect(zones).toHaveLength(size)
    expect(zones.every((row) => row.length === size)).toBe(true)
    expect(zones.flat().every((cell) => cell !== -1)).toBe(true)
    expect(new Set(zones.flat()).size).toBe(size)
  })

  it('est déterministe avec un rng seedé fixe', () => {
    const a = generateRandomConnectedPattern(7, createSeededRng('test-seed'))
    const b = generateRandomConnectedPattern(7, createSeededRng('test-seed'))
    expect(a).toEqual(b)
  })

  it('des seeds différentes produisent généralement des grilles différentes', () => {
    const a = generateRandomConnectedPattern(7, createSeededRng('seed-a'))
    const b = generateRandomConnectedPattern(7, createSeededRng('seed-b'))
    expect(a).not.toEqual(b)
  })
})
