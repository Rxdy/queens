import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { nextTick } from 'vue'
import App from '../App.vue'

vi.mock('axios', () => ({
  default: {
    defaults: { timeout: 0 },
    post: vi.fn().mockResolvedValue({
      data: {
        solutions: [[[0, 0], [1, 2], [2, 1], [3, 3]]],
        performance: { execution_time: 0.001, iterations: 42, solutions_count: 1, solutions_per_second: 1000 },
        supported: true,
      },
    }),
    get: vi.fn().mockResolvedValue({ data: {} }),
  },
}))

const mountApp = () => shallowMount(App, { attachTo: document.body })

describe('App.vue — état initial', () => {
  it('monte sans erreur', () => {
    expect(() => mountApp()).not.toThrow()
  })

  it('initialise une grille 8×8 de -1', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.zones).toHaveLength(8)
    wrapper.vm.zones.forEach(row => {
      expect(row).toHaveLength(8)
      row.forEach(cell => expect(cell).toBe(-1))
    })
    wrapper.unmount()
  })

  it('isGridComplete est false au départ', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.isGridComplete).toBe(false)
    wrapper.unmount()
  })

  it('emptyCellsCount est 64 au départ (8×8)', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.emptyCellsCount).toBe(64)
    wrapper.unmount()
  })

  it('crée automatiquement un premier brouillon', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.drafts.length).toBeGreaterThanOrEqual(1)
    wrapper.unmount()
  })
})

describe('App.vue — initializeZones', () => {
  it('crée une grille N×N de -1 pour la taille courante', async () => {
    const wrapper = mountApp()
    wrapper.vm.size = 5
    wrapper.vm.initializeZones()
    await nextTick()
    expect(wrapper.vm.zones).toHaveLength(5)
    wrapper.vm.zones.forEach(row => {
      expect(row).toHaveLength(5)
      row.forEach(cell => expect(cell).toBe(-1))
    })
    wrapper.unmount()
  })

  it('vide paintHistory lors d\'une réinitialisation', async () => {
    const wrapper = mountApp()
    wrapper.vm.snapshotPaintState()
    expect(wrapper.vm.paintHistory.length).toBe(1)
    wrapper.vm.initializeZones()
    await nextTick()
    expect(wrapper.vm.paintHistory.length).toBe(0)
    wrapper.unmount()
  })
})

describe('App.vue — isGridComplete & emptyCellsCount', () => {
  it('isGridComplete devient true quand toutes les cellules sont remplies', async () => {
    const wrapper = mountApp()
    // Remplir toutes les cellules
    wrapper.vm.zones = Array.from({ length: 8 }, () => Array(8).fill(0))
    await nextTick()
    expect(wrapper.vm.isGridComplete).toBe(true)
    wrapper.unmount()
  })

  it('emptyCellsCount diminue à mesure que des cellules sont peintes', async () => {
    const wrapper = mountApp()
    const zones = wrapper.vm.zones.map(row => [...row])
    zones[0][0] = 0
    wrapper.vm.zones = zones
    await nextTick()
    expect(wrapper.vm.emptyCellsCount).toBe(63)
    wrapper.unmount()
  })
})

describe('App.vue — undo / redo', () => {
  it('snapshotPaintState enregistre l\'état courant dans paintHistory', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.paintHistory.length).toBe(0)
    wrapper.vm.snapshotPaintState()
    expect(wrapper.vm.paintHistory.length).toBe(1)
    wrapper.unmount()
  })

  it('undoPaint restaure l\'état précédent des zones', async () => {
    const wrapper = mountApp()
    // Snapshot de la grille vide
    wrapper.vm.snapshotPaintState()
    // Peindre une cellule
    const modifiedZones = wrapper.vm.zones.map(row => [...row])
    modifiedZones[0][0] = 2
    wrapper.vm.zones = modifiedZones
    await nextTick()
    expect(wrapper.vm.zones[0][0]).toBe(2)
    // Undo
    wrapper.vm.undoPaint()
    await nextTick()
    expect(wrapper.vm.zones[0][0]).toBe(-1)
    wrapper.unmount()
  })

  it('undoPaint ne fait rien si paintHistory est vide', async () => {
    const wrapper = mountApp()
    const zonesBefore = wrapper.vm.zones.map(row => [...row])
    wrapper.vm.undoPaint()
    await nextTick()
    expect(wrapper.vm.zones).toEqual(zonesBefore)
    wrapper.unmount()
  })

  it('respecte MAX_UNDO : ne garde que les 20 derniers snapshots', () => {
    const wrapper = mountApp()
    for (let i = 0; i < 25; i++) {
      wrapper.vm.snapshotPaintState()
    }
    expect(wrapper.vm.paintHistory.length).toBe(20)
    wrapper.unmount()
  })
})

describe('App.vue — brouillons', () => {
  beforeEach(() => {
    // Vider le localStorage entre chaque test pour l'isolation
    localStorage.clear()
  })

  it('crée un brouillon initial si aucun n\'existe', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.drafts.length).toBeGreaterThanOrEqual(1)
    wrapper.unmount()
  })
})

describe('App.vue — état initial', () => {
  it('errorMessage est vide au départ', () => {
    const wrapper = mountApp()
    expect(wrapper.vm.errorMessage).toBe('')
    wrapper.unmount()
  })
})
