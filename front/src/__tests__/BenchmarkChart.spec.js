import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BenchmarkChart from '../BenchmarkChart.vue'

const oneEntry = [{ size: 4, trmTime: 0.001, baselineTime: 0.01 }]
const twoEntries = [
  { size: 4, trmTime: 0.001, baselineTime: 0.01 },
  { size: 4, trmTime: 0.002, baselineTime: 0.02 },
]
const multiSize = [
  { size: 4, trmTime: 0.001, baselineTime: 0.01 },
  { size: 8, trmTime: 0.05,  baselineTime: null },
]

describe('BenchmarkChart', () => {
  describe('sans données', () => {
    it('affiche le message no-data quand history est vide', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: [] } })
      expect(wrapper.find('.no-data').exists()).toBe(true)
    })

    it('ne rend pas le SVG quand history est vide', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: [] } })
      expect(wrapper.find('.svg-container').exists()).toBe(false)
    })

    it('affiche "0 résolution" sans "s"', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: [] } })
      expect(wrapper.find('.legend-count').text()).toContain('0 résolution')
      expect(wrapper.find('.legend-count').text()).not.toContain('résolutions')
    })
  })

  describe('avec données', () => {
    it('affiche le SVG et cache le no-data', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: oneEntry } })
      expect(wrapper.find('.svg-container').exists()).toBe(true)
      expect(wrapper.find('.no-data').exists()).toBe(false)
    })

    it('affiche "1 résolution" (singulier)', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: oneEntry } })
      expect(wrapper.find('.legend-count').text()).toContain('1 résolution')
      expect(wrapper.find('.legend-count').text()).not.toContain('résolutions')
    })

    it('affiche "2 résolutions" (pluriel)', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: twoEntries } })
      expect(wrapper.find('.legend-count').text()).toContain('2 résolutions')
    })

    it('rend une barre TRM par taille de grille', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: multiSize } })
      expect(wrapper.findAll('.trm-bar')).toHaveLength(2)
    })

    it('rend une barre baseline seulement quand baselineTime est présent', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: multiSize } })
      // size 4 a baseline, size 8 n'en a pas
      expect(wrapper.findAll('.baseline-bar')).toHaveLength(1)
    })

    it('affiche le label de speedup quand TRM et baseline sont tous deux présents', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: oneEntry } })
      expect(wrapper.find('.speedup-label').exists()).toBe(true)
    })

    it('n\'affiche pas de speedup si baseline absent', () => {
      const wrapper = mount(BenchmarkChart, {
        props: { history: [{ size: 8, trmTime: 0.05, baselineTime: null }] },
      })
      expect(wrapper.find('.speedup-label').exists()).toBe(false)
    })

    it('calcule la moyenne sur plusieurs mesures de la même taille', () => {
      // 2 mesures size 4 : trm 1ms et 3ms → moyenne 2ms
      const history = [
        { size: 4, trmTime: 0.001, baselineTime: null },
        { size: 4, trmTime: 0.003, baselineTime: null },
      ]
      const wrapper = mount(BenchmarkChart, { props: { history } })
      // Un seul groupe de barres (une seule taille)
      expect(wrapper.findAll('.trm-bar')).toHaveLength(1)
    })

    it('trie les groupes par taille de grille croissante', () => {
      const history = [
        { size: 8, trmTime: 0.05, baselineTime: null },
        { size: 4, trmTime: 0.001, baselineTime: null },
      ]
      const wrapper = mount(BenchmarkChart, { props: { history } })
      const xLabels = wrapper.findAll('.x-label').map(el => el.text())
      expect(xLabels[0]).toContain('4')
      expect(xLabels[1]).toContain('8')
    })
  })

  describe('tooltip', () => {
    it('tooltip est invisible par défaut', () => {
      const wrapper = mount(BenchmarkChart, { props: { history: oneEntry } })
      expect(wrapper.find('.tooltip-box').exists()).toBe(false)
    })

    it('tooltip apparaît au mouseenter sur une barre TRM', async () => {
      const wrapper = mount(BenchmarkChart, {
        props: { history: oneEntry },
        attachTo: document.body,
      })
      await wrapper.find('.trm-bar').trigger('mouseenter', { clientX: 200, clientY: 150 })
      expect(wrapper.find('.tooltip-box').exists()).toBe(true)
      wrapper.unmount()
    })

    it('tooltip disparaît au mouseleave', async () => {
      const wrapper = mount(BenchmarkChart, {
        props: { history: oneEntry },
        attachTo: document.body,
      })
      const bar = wrapper.find('.trm-bar')
      await bar.trigger('mouseenter', { clientX: 200, clientY: 150 })
      await bar.trigger('mouseleave')
      expect(wrapper.find('.tooltip-box').exists()).toBe(false)
      wrapper.unmount()
    })

    it('tooltip contient le label "TRM" pour une barre TRM', async () => {
      const wrapper = mount(BenchmarkChart, {
        props: { history: oneEntry },
        attachTo: document.body,
      })
      await wrapper.find('.trm-bar').trigger('mouseenter', { clientX: 200, clientY: 150 })
      const texts = wrapper.findAll('.tooltip-box div').map(el => el.text())
      expect(texts.some(t => t.includes('TRM'))).toBe(true)
      wrapper.unmount()
    })

    it('tooltip contient "Baseline" pour une barre baseline', async () => {
      const wrapper = mount(BenchmarkChart, {
        props: { history: oneEntry },
        attachTo: document.body,
      })
      await wrapper.find('.baseline-bar').trigger('mouseenter', { clientX: 200, clientY: 150 })
      const texts = wrapper.findAll('.tooltip-box div').map(el => el.text())
      expect(texts.some(t => t.includes('Baseline'))).toBe(true)
      wrapper.unmount()
    })
  })
})
