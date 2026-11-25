import { describe, expect, it } from 'vitest'
import { colors } from '../utils/colors.js'

const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16))
const luminance = (hex) => {
  const [r, g, b] = rgb(hex).map((v) => {
    const c = v / 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}
const contrast = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (hi + 0.05) / (lo + 0.05)
}
const distance = (a, b) => Math.hypot(...rgb(a).map((v, i) => v - rgb(b)[i]))

describe('couleurs des zones', () => {
  it('12 couleurs, au format #rrggbb, sans doublon', () => {
    expect(colors).toHaveLength(12)
    for (const c of colors) expect(c).toMatch(/^#[0-9a-f]{6}$/)
    expect(new Set(colors).size).toBe(12)
  })

  it('toutes pastel : claires, jamais sombres', () => {
    for (const c of colors) expect(luminance(c), c).toBeGreaterThan(0.45)
  })

  it('deux zones voisines restent distinguables (distance RGB minimale)', () => {
    for (let i = 0; i < colors.length; i++)
      for (let j = i + 1; j < colors.length; j++)
        expect(distance(colors[i], colors[j]), `${colors[i]} / ${colors[j]}`).toBeGreaterThan(22)
  })

  it('la reine (#1a1e27) se lit sur chaque zone (contraste ≥ 7)', () => {
    for (const c of colors) expect(contrast('#1a1e27', c), c).toBeGreaterThanOrEqual(7)
  })
})
