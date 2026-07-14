import { describe, it, expect } from 'vitest'
import { hashStringToInt, mulberry32, createSeededRng } from '../utils/seededRandom.js'

describe('hashStringToInt', () => {
  it('est déterministe pour une même chaîne', () => {
    expect(hashStringToInt('2026-07-14|6|0')).toBe(hashStringToInt('2026-07-14|6|0'))
  })

  it('donne des résultats différents pour des seeds différentes', () => {
    expect(hashStringToInt('2026-07-14|6|0')).not.toBe(hashStringToInt('2026-07-14|6|1'))
  })
})

describe('mulberry32', () => {
  it('produit toujours des floats dans [0, 1)', () => {
    const rng = mulberry32(42)
    for (let i = 0; i < 50; i++) {
      const v = rng()
      expect(v).toBeGreaterThanOrEqual(0)
      expect(v).toBeLessThan(1)
    }
  })

  it('deux générateurs avec la même seed produisent la même séquence', () => {
    const a = mulberry32(1234)
    const b = mulberry32(1234)
    const seqA = Array.from({ length: 20 }, () => a())
    const seqB = Array.from({ length: 20 }, () => b())
    expect(seqA).toEqual(seqB)
  })
})

describe('createSeededRng', () => {
  it('même seed string → même séquence, sur deux instances indépendantes', () => {
    const seq = (rng) => Array.from({ length: 20 }, () => rng())
    expect(seq(createSeededRng('2026-07-14|8|0'))).toEqual(seq(createSeededRng('2026-07-14|8|0')))
  })

  it('seed strings différentes → séquences différentes', () => {
    const seq = (rng) => Array.from({ length: 5 }, () => rng())
    expect(seq(createSeededRng('2026-07-14|8|0'))).not.toEqual(seq(createSeededRng('2026-07-15|8|0')))
  })
})
