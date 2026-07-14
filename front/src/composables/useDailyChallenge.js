import { computed } from "vue";
import { useLocalStorage } from "@vueuse/core";
import { generateRandomConnectedPattern } from "../utils/generateZones.js";
import { hasSolution, findConflictingQueens } from "../utils/queensSolver.js";
import { createSeededRng } from "../utils/seededRandom.js";

export const DAILY_SIZES = [6, 7, 8, 9];
export const RESET_HOUR = 8;
const MAX_ATTEMPTS = 40;
const STORAGE_KEY = "queens-daily-challenge";

const emptyState = () => ({ puzzleDay: null, generatedAt: null, puzzles: [] });

// Jour "logique" du défi : avant RESET_HOUR (heure locale), on est encore sur
// le jour précédent — la grille du jour ne change qu'à 8h du matin, pas à minuit.
// Utilise les accesseurs locaux (getFullYear/getMonth/getDate), pas toISOString
// (UTC), pour éviter tout décalage de fuseau horaire.
export const getCurrentPuzzleDay = (now = new Date(), resetHour = RESET_HOUR) => {
    const d = new Date(now);
    if (d.getHours() < resetHour) {
        d.setDate(d.getDate() - 1);
    }
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
};

// Prochain instant de reset (8h du matin locale, aujourd'hui ou demain).
export const getNextResetAt = (now = new Date(), resetHour = RESET_HOUR) => {
    const d = new Date(now);
    d.setHours(resetHour, 0, 0, 0);
    if (d.getTime() <= now.getTime()) {
        d.setDate(d.getDate() + 1);
    }
    return d;
};

// Génère les 4 grilles du jour : seedées par (jour, taille, tentative), donc
// strictement identiques pour tous les navigateurs à une date donnée. Chaque
// grille est vérifiée solvable (hasSolution) ; sinon on retente avec la seed
// suivante, toujours de façon déterministe et reproductible.
const generatePuzzlesForDay = (puzzleDay) =>
    DAILY_SIZES.map((size) => {
        for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
            const rng = createSeededRng(`${puzzleDay}|${size}|${attempt}`);
            const zones = generateRandomConnectedPattern(size, rng);
            if (hasSolution(size, zones)) {
                return {
                    id: `daily-${size}`,
                    size,
                    zones,
                    status: "pending",
                    userQueens: [],
                    seedAttempt: attempt,
                };
            }
        }
        throw new Error(`Impossible de générer une grille solvable pour size=${size} (jour ${puzzleDay}).`);
    });

// State partagé au niveau module (singleton) : tous les composants qui
// appellent useDailyChallenge() lisent/écrivent le même state réactif.
const state = useLocalStorage(STORAGE_KEY, emptyState());

export const ensureTodaysPuzzles = () => {
    const today = getCurrentPuzzleDay();
    if (state.value.puzzleDay !== today) {
        state.value = {
            puzzleDay: today,
            generatedAt: new Date().toISOString(),
            puzzles: generatePuzzlesForDay(today),
        };
    }
};

// Génère immédiatement les grilles du jour dès le chargement du module, pour
// que les données soient prêtes même si l'utilisateur ouvre l'onglet "Jeu" en premier.
ensureTodaysPuzzles();

const findPuzzle = (puzzleId) => state.value.puzzles.find((p) => p.id === puzzleId);

const markSolved = (puzzleId) => {
    const puzzle = findPuzzle(puzzleId);
    if (!puzzle || puzzle.status === "solved") return;
    puzzle.status = "solved";
};

// Le toggle ET la détection de victoire doivent muter le state dans le même
// tick synchrone (pas via un watch()+emit() asynchrone) : useLocalStorage
// s'auto-notifie via un événement "storage" synthétique pour rester en phase
// avec d'autres instances, ce qui met son watcher de persistance en pause
// jusqu'au nextTick suivant. Une mutation de `status` survenant dans cette
// fenêtre (déclenchée par un watch() séparé) est silencieusement perdue par
// la persistance localStorage. En restant synchrone ici, une seule écriture
// couvre à la fois `userQueens` et `status`.
const toggleQueen = (puzzleId, row, col) => {
    const puzzle = findPuzzle(puzzleId);
    if (!puzzle || puzzle.status === "solved") return;

    const idx = puzzle.userQueens.findIndex(([r, c]) => r === row && c === col);
    if (idx === -1) {
        puzzle.userQueens.push([row, col]);
    } else {
        puzzle.userQueens.splice(idx, 1);
    }

    const solved =
        puzzle.userQueens.length === puzzle.size &&
        findConflictingQueens(puzzle.zones, puzzle.userQueens).size === 0;
    if (solved) markSolved(puzzleId);
};

const resetPuzzleProgress = (puzzleId) => {
    const puzzle = findPuzzle(puzzleId);
    if (!puzzle) return;
    puzzle.userQueens = [];
    puzzle.status = "pending";
};

export function useDailyChallenge() {
    return {
        puzzleDay: computed(() => state.value.puzzleDay),
        puzzles: computed(() => state.value.puzzles),
        ensureTodaysPuzzles,
        selectPuzzle: findPuzzle,
        toggleQueen,
        resetPuzzleProgress,
        markSolved,
    };
}
