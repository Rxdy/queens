import { describe, it, expect } from 'vitest'
import { formatMs, formatDuration } from '../utils/format.js'

describe('formatMs', () => {
  it('retourne — pour null', () => {
    expect(formatMs(null)).toBe('—')
  })

  it('retourne — pour undefined', () => {
    expect(formatMs(undefined)).toBe('—')
  })

  describe('nanosecondes (ms < 0.001)', () => {
    it('formate 0.0005 ms → 500 ns', () => {
      expect(formatMs(0.0005)).toBe('500 ns')
    })

    it('formate 0.0001 ms → 100 ns', () => {
      expect(formatMs(0.0001)).toBe('100 ns')
    })

    it('formate 0.000001 ms → 1 ns', () => {
      expect(formatMs(0.000001)).toBe('1 ns') // 0.000001 * 1e6 = 1
    })
  })

  describe('microsecondes (0.001 ≤ ms < 1)', () => {
    it('formate 0.001 ms → 1 µs', () => {
      expect(formatMs(0.001)).toBe('1 µs')
    })

    it('formate 0.5 ms → 500 µs', () => {
      expect(formatMs(0.5)).toBe('500 µs')
    })

    it('formate 0.999 ms → 999 µs', () => {
      expect(formatMs(0.999)).toBe('999 µs')
    })
  })

  describe('millisecondes (1 ≤ ms < 1000)', () => {
    it('formate 1 ms → 1 ms (sans .0)', () => {
      expect(formatMs(1)).toBe('1 ms')
    })

    it('formate 100 ms → 100 ms (sans .0)', () => {
      expect(formatMs(100)).toBe('100 ms')
    })

    it('formate 100.1 ms → 100.1 ms (garde le .1)', () => {
      expect(formatMs(100.1)).toBe('100.1 ms')
    })

    it('formate 999.9 ms → 999.9 ms', () => {
      expect(formatMs(999.9)).toBe('999.9 ms')
    })
  })

  describe('secondes (ms ≥ 1000)', () => {
    it('formate 1000 ms → 1 s (sans .00)', () => {
      expect(formatMs(1000)).toBe('1 s')
    })

    it('formate 1500 ms → 1.50 s (garde .50)', () => {
      expect(formatMs(1500)).toBe('1.50 s')
    })

    it('formate 10000 ms → 10 s (sans .00)', () => {
      expect(formatMs(10000)).toBe('10 s')
    })

    it('formate 2100 ms → 2.10 s (garde .10)', () => {
      expect(formatMs(2100)).toBe('2.10 s')
    })
  })
})

describe('formatDuration', () => {
  it('retourne — pour null/undefined', () => {
    expect(formatDuration(null)).toBe('—')
    expect(formatDuration(undefined)).toBe('—')
  })

  it('formate moins d\'une minute en secondes', () => {
    expect(formatDuration(15000)).toBe('15s')
    expect(formatDuration(500)).toBe('1s')
    expect(formatDuration(0)).toBe('0s')
  })

  it('formate au-delà d\'une minute en m/s', () => {
    expect(formatDuration(90000)).toBe('1m 30s')
    expect(formatDuration(60000)).toBe('1m 00s')
    expect(formatDuration(125000)).toBe('2m 05s')
  })
})
