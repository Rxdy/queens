import { describe, it, expect } from 'vitest'
import { getCurrentPuzzleDay, getNextResetAt, useDailyChallenge, DAILY_SIZES } from '../composables/useDailyChallenge.js'
import { hasSolution } from '../utils/queensSolver.js'

describe('getCurrentPuzzleDay', () => {
  it('reste sur le jour précédent avant 8h locale', () => {
    expect(getCurrentPuzzleDay(new Date(2026, 6, 14, 7, 59))).toBe('2026-07-13')
  })

  it('bascule sur le jour courant à partir de 8h locale', () => {
    expect(getCurrentPuzzleDay(new Date(2026, 6, 14, 8, 0))).toBe('2026-07-14')
  })

  it('gère correctement un changement de mois', () => {
    expect(getCurrentPuzzleDay(new Date(2026, 7, 1, 7, 0))).toBe('2026-07-31')
  })
})

describe('getNextResetAt', () => {
  it("pointe sur aujourd'hui 8h si on est avant 8h", () => {
    const next = getNextResetAt(new Date(2026, 6, 14, 6, 0))
    expect(next.getDate()).toBe(14)
    expect(next.getHours()).toBe(8)
  })

  it('pointe sur demain 8h si on est après 8h', () => {
    const next = getNextResetAt(new Date(2026, 6, 14, 9, 0))
    expect(next.getDate()).toBe(15)
    expect(next.getHours()).toBe(8)
  })
})

describe('useDailyChallenge', () => {
  it('génère 4 puzzles aux tailles attendues, tous solvables', () => {
    const { puzzles } = useDailyChallenge()
    expect(puzzles.value).toHaveLength(4)
    expect(puzzles.value.map((p) => p.size)).toEqual(DAILY_SIZES)
    for (const puzzle of puzzles.value) {
      expect(hasSolution(puzzle.size, puzzle.zones)).toBe(true)
      expect(puzzle.status).toBe('pending')
      expect(puzzle.userQueens).toEqual([])
    }
  })

  it('toggleQueen ajoute puis retire une reine', () => {
    const { puzzles, toggleQueen, selectPuzzle } = useDailyChallenge()
    const id = puzzles.value[0].id
    toggleQueen(id, 0, 0)
    expect(selectPuzzle(id).userQueens).toEqual([[0, 0]])
    toggleQueen(id, 0, 0)
    expect(selectPuzzle(id).userQueens).toEqual([])
  })

  it('markSolved passe le statut à solved', () => {
    const { puzzles, markSolved, selectPuzzle } = useDailyChallenge()
    const id = puzzles.value[1].id
    markSolved(id)
    expect(selectPuzzle(id).status).toBe('solved')
  })

  it('resetPuzzleProgress vide les reines, les croix et repasse en pending', () => {
    const { puzzles, toggleQueen, toggleMark, markSolved, resetPuzzleProgress, selectPuzzle } = useDailyChallenge()
    const id = puzzles.value[2].id
    toggleQueen(id, 1, 1)
    toggleMark(id, 2, 2)
    markSolved(id)
    resetPuzzleProgress(id)
    expect(selectPuzzle(id).userQueens).toEqual([])
    expect(selectPuzzle(id).userMarks).toEqual([])
    expect(selectPuzzle(id).status).toBe('pending')
  })

  it('toggleMark ajoute puis retire une croix', () => {
    const { puzzles, toggleMark, selectPuzzle } = useDailyChallenge()
    const id = puzzles.value[3].id
    toggleMark(id, 0, 1)
    expect(selectPuzzle(id).userMarks).toEqual([[0, 1]])
    toggleMark(id, 0, 1)
    expect(selectPuzzle(id).userMarks).toEqual([])
  })

  it('poser une reine efface une croix existante sur la même case, et inversement', () => {
    const { puzzles, toggleQueen, toggleMark, selectPuzzle } = useDailyChallenge()
    const id = puzzles.value[3].id
    toggleMark(id, 1, 2)
    toggleQueen(id, 1, 2)
    expect(selectPuzzle(id).userMarks).toEqual([])
    expect(selectPuzzle(id).userQueens).toEqual([[1, 2]])

    toggleMark(id, 1, 2)
    expect(selectPuzzle(id).userQueens).toEqual([])
    expect(selectPuzzle(id).userMarks).toEqual([[1, 2]])
  })

  it('startPuzzle démarre le chrono une seule fois (idempotent)', () => {
    const { puzzles, startPuzzle, selectPuzzle } = useDailyChallenge()
    const id = puzzles.value[3].id
    expect(selectPuzzle(id).startedAt).toBeNull()
    startPuzzle(id)
    const firstStart = selectPuzzle(id).startedAt
    expect(firstStart).not.toBeNull()
    startPuzzle(id)
    expect(selectPuzzle(id).startedAt).toBe(firstStart)
  })
})
