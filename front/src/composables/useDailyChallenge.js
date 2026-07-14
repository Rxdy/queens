import { computed, ref } from "vue";
import { useLocalStorage } from "@vueuse/core";
import axios from "axios";
import { generateRandomConnectedPattern } from "../utils/generateZones.js";
import { hasSolution, findConflictingQueens } from "../utils/queensSolver.js";
import { createSeededRng } from "../utils/seededRandom.js";

const TRM_BASE = import.meta.env.VITE_TRM_API_BASE ?? "";

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
                    userMarks: [],
                    startedAt: null,
                    solveTimeMs: null,
                    seedAttempt: attempt,
                };
            }
        }
        throw new Error(`Impossible de générer une grille solvable pour size=${size} (jour ${puzzleDay}).`);
    });

// State partagé au niveau module (singleton) : tous les composants qui
// appellent useDailyChallenge() lisent/écrivent le même state réactif.
const state = useLocalStorage(STORAGE_KEY, emptyState());

// Statistiques du défi quotidien partagées entre joueurs (nb de résolutions
// humaines + meilleur temps, par taille) — best-effort : un souci réseau ne
// doit jamais bloquer le jeu, qui reste jouable même hors-ligne/sans backend.
const globalDailyStats = ref({});

const fetchGlobalDailyStats = async () => {
    if (!state.value.puzzleDay) return;
    try {
        const { data } = await axios.get(`${TRM_BASE}/api/daily/stats/${state.value.puzzleDay}`);
        globalDailyStats.value = data;
    } catch {
        // Best-effort : le jeu reste jouable sans ces stats.
    }
};

const reportDailySolve = async (puzzleDay, size, timeMs) => {
    try {
        const { data } = await axios.post(`${TRM_BASE}/api/daily/solve`, {
            puzzle_day: puzzleDay,
            size,
            time_ms: timeMs,
        });
        globalDailyStats.value = { ...globalDailyStats.value, [String(size)]: data };
    } catch {
        // Best-effort : la progression locale du joueur reste valable même si
        // le signalement au serveur échoue.
    }
};

export const ensureTodaysPuzzles = () => {
    const today = getCurrentPuzzleDay();
    if (state.value.puzzleDay !== today) {
        state.value = {
            puzzleDay: today,
            generatedAt: new Date().toISOString(),
            puzzles: generatePuzzlesForDay(today),
        };
    } else {
        // Migration défensive : des puzzles déjà en cache (générés avant l'ajout
        // de ces champs) peuvent ne pas les avoir — on les complète sans tout régénérer.
        for (const puzzle of state.value.puzzles) {
            if (!puzzle.userMarks) puzzle.userMarks = [];
            if (puzzle.startedAt === undefined) puzzle.startedAt = null;
            if (puzzle.solveTimeMs === undefined) puzzle.solveTimeMs = null;
        }
    }
    fetchGlobalDailyStats();
};

// Génère immédiatement les grilles du jour dès le chargement du module, pour
// que les données soient prêtes même si l'utilisateur ouvre l'onglet "Jeu" en premier.
ensureTodaysPuzzles();

const findPuzzle = (puzzleId) => state.value.puzzles.find((p) => p.id === puzzleId);

// Démarre le chrono à la première ouverture du puzzle (idempotent : un retour
// sur un puzzle déjà commencé ne redémarre pas le temps).
const startPuzzle = (puzzleId) => {
    const puzzle = findPuzzle(puzzleId);
    if (!puzzle || puzzle.startedAt !== null) return;
    puzzle.startedAt = Date.now();
};

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

    // Reine et croix sont mutuellement exclusives sur une case : poser une
    // reine efface une croix éventuelle (l'utilisateur change d'avis).
    const markIdx = puzzle.userMarks.findIndex(([r, c]) => r === row && c === col);
    if (markIdx !== -1) puzzle.userMarks.splice(markIdx, 1);

    const idx = puzzle.userQueens.findIndex(([r, c]) => r === row && c === col);
    if (idx === -1) {
        puzzle.userQueens.push([row, col]);
    } else {
        puzzle.userQueens.splice(idx, 1);
    }

    const solved =
        puzzle.userQueens.length === puzzle.size &&
        findConflictingQueens(puzzle.zones, puzzle.userQueens).size === 0;
    if (solved) {
        const solveTimeMs = puzzle.startedAt !== null ? Date.now() - puzzle.startedAt : null;
        puzzle.solveTimeMs = solveTimeMs;
        markSolved(puzzleId);
        if (solveTimeMs !== null) {
            reportDailySolve(state.value.puzzleDay, puzzle.size, solveTimeMs);
        }
    }
};

// La croix est une simple annotation de réflexion ("pas une reine ici") —
// elle ne participe jamais à la détection de victoire.
const toggleMark = (puzzleId, row, col) => {
    const puzzle = findPuzzle(puzzleId);
    if (!puzzle || puzzle.status === "solved") return;

    const queenIdx = puzzle.userQueens.findIndex(([r, c]) => r === row && c === col);
    if (queenIdx !== -1) puzzle.userQueens.splice(queenIdx, 1);

    const idx = puzzle.userMarks.findIndex(([r, c]) => r === row && c === col);
    if (idx === -1) {
        puzzle.userMarks.push([row, col]);
    } else {
        puzzle.userMarks.splice(idx, 1);
    }
};

const resetPuzzleProgress = (puzzleId) => {
    const puzzle = findPuzzle(puzzleId);
    if (!puzzle) return;
    puzzle.userQueens = [];
    puzzle.userMarks = [];
    puzzle.status = "pending";
};

export function useDailyChallenge() {
    return {
        puzzleDay: computed(() => state.value.puzzleDay),
        puzzles: computed(() => state.value.puzzles),
        globalDailyStats: computed(() => globalDailyStats.value),
        ensureTodaysPuzzles,
        selectPuzzle: findPuzzle,
        startPuzzle,
        toggleQueen,
        toggleMark,
        resetPuzzleProgress,
        markSolved,
    };
}
