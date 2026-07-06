<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useLocalStorage } from "@vueuse/core";
import axios from "axios";
import BenchmarkChart from "./BenchmarkChart.vue";
import HelpWelcomeModal from "./components/HelpWelcomeModal.vue";
import HistoryPanel from "./components/HistoryPanel.vue";
import ImportModal from "./components/ImportModal.vue";

const TRM_BASE = import.meta.env.VITE_TRM_API_BASE ?? "";
const BASELINE_BASE = import.meta.env.VITE_BASELINE_API_BASE ?? "";

// Configuration axios sans timeout pour permettre les requêtes long-running
axios.defaults.timeout = 0; // 0 = pas de timeout

const currentView = ref("game");

const size = ref(8);
const zones = ref([]);
const positions = ref([]);
const solutions = ref([]);
const selectedColor = ref(0);
const errorMessage = ref("");
const MAX_HISTORY = 100;
const history = useLocalStorage("queens-history", []);
const historyVisible = ref(true);
const trmPerformance = ref(null);
const baselineResult = ref(null);
const isBenchmarking = ref(false);
const isSolving = ref(false);
const benchmarkStatus = ref("");
const isImportModalOpen = ref(false);
const importModalRef = ref(null);
const showWelcomeModal = ref(true);
const showHelpModal = ref(false);

const isMobile = computed(() => screenWidth.value < 600);
// Nombre de solutions visualisables : 3 max sur mobile, 5 sur desktop.
const maxSolButtons = computed(() => (screenWidth.value <= 600 ? 3 : 5));
const currentSolutionIndex = ref(0);
const isPainting = ref(false);
const currentMouseButton = ref(null);
const paintHistory = ref([]);
const MAX_UNDO = 20;
const selectedHistoryIndex = ref(-1);

// Brouillons (drafts) — persistés dans localStorage
const drafts = useLocalStorage("queens-drafts", []);
const currentDraftIndex = useLocalStorage("queens-draft-index", -1);
const MAX_DRAFTS = 15;

// Dimensions de l'écran réactives
const screenWidth = ref(1200);
const screenHeight = ref(800);

const colors = [
    "rgb(223, 160, 191)",
    "rgb(150, 190, 255)",
    "rgb(255, 201, 146)",
    "rgb(187, 163, 226)",
    "rgb(240, 240, 240)",
    "rgb(139, 69, 19)",
    "rgb(255, 123, 96)",
    "rgb(230, 243, 136)",
    "rgb(179, 223, 160)",
    "rgb(85, 235, 226)",
    "rgb(149, 203, 207)",
    "rgb(210, 180, 200)",
];

// Couleurs disponibles et leurs indices
const availableColorIndices = computed(() => {
    if (!zones.value) return [];

    const usedColorsInGrid = new Set(
        zones.value.flat().filter((cell) => cell !== -1)
    );
    const maxColors = size.value;

    if (usedColorsInGrid.size < maxColors) {
        return Array.from({ length: colors.length }, (_, i) => i);
    } else {
        return Array.from(usedColorsInGrid).sort((a, b) => a - b);
    }
});

const initializeZones = () => {
    zones.value = Array.from({ length: size.value }, () =>
        Array(size.value).fill(-1)
    );
    positions.value = [];
    solutions.value = [];
    selectedHistoryIndex.value = -1;
    trmPerformance.value = null;
    baselineResult.value = null;
    errorMessage.value = "";
    isPainting.value = false;
    paintHistory.value = [];
    if (selectedColor.value >= size.value) {
        selectedColor.value = 0;
    }
};

const saveDraft = () => {
    if (currentDraftIndex.value >= 0 && drafts.value[currentDraftIndex.value]) {
        drafts.value[currentDraftIndex.value] = {
            ...drafts.value[currentDraftIndex.value],
            size: size.value,
            zones: zones.value.map((row) => [...row]),
            selectedColor: selectedColor.value,
            updatedAt: new Date().toLocaleString("fr-FR"),
        };
    }
};

const createNewDraft = () => {
    saveDraft();

    const newDraft = {
        id: Date.now(),
        size: 8,
        zones: Array.from({ length: 8 }, () => Array(8).fill(-1)),
        selectedColor: 0,
        createdAt: new Date().toLocaleString("fr-FR"),
        updatedAt: new Date().toLocaleString("fr-FR"),
    };

    drafts.value.unshift(newDraft);

    if (drafts.value.length > MAX_DRAFTS) {
        const excess = drafts.value.length - MAX_DRAFTS;
        drafts.value.splice(-excess);
    }

    currentDraftIndex.value = 0;
    size.value = newDraft.size;
    zones.value = newDraft.zones.map((row) => [...row]);
    selectedColor.value = newDraft.selectedColor;
    initializeZones();
};

const switchDraft = (index) => {
    if (index === currentDraftIndex.value) return;

    saveDraft();

    const draft = drafts.value[index];
    if (!draft) return;

    currentDraftIndex.value = index;
    size.value = draft.size;
    zones.value = draft.zones.map((row) => [...row]);
    selectedColor.value = draft.selectedColor;
    positions.value = [];
    solutions.value = [];
    selectedHistoryIndex.value = -1;
    trmPerformance.value = null;
    baselineResult.value = null;
    errorMessage.value = "";
};

const deleteDraft = (index) => {
    drafts.value.splice(index, 1);
    if (currentDraftIndex.value === index) {
        if (drafts.value.length > 0) {
            switchDraft(0);
        } else {
            currentDraftIndex.value = -1;
            initializeZones();
        }
    } else if (currentDraftIndex.value > index) {
        currentDraftIndex.value--;
    }
};

const clearForNewGrid = () => {
    createNewDraft();
};

const clickCell = (row, col, button) => {
    if (isViewingHistory.value) return;

    if (button === 0) {
        zones.value[row][col] = selectedColor.value;
    } else if (button === 2) {
        zones.value[row][col] = -1;
    }

    errorMessage.value = "";
    positions.value = [];
    solutions.value = [];
    currentSolutionIndex.value = 0;
    selectedHistoryIndex.value = -1;
    trmPerformance.value = null;
    baselineResult.value = null;
};

const snapshotPaintState = () => {
    paintHistory.value.push(zones.value.map((row) => [...row]));
    if (paintHistory.value.length > MAX_UNDO) paintHistory.value.shift();
};

const undoPaint = () => {
    if (paintHistory.value.length === 0) return;
    zones.value = paintHistory.value.pop();
    positions.value = [];
    solutions.value = [];
    currentSolutionIndex.value = 0;
    trmPerformance.value = null;
    baselineResult.value = null;
    errorMessage.value = "";
};

const onMouseDown = (row, col, event) => {
    event.preventDefault();
    currentMouseButton.value = event.button;
    isPainting.value = true;
    snapshotPaintState();
    clickCell(row, col, event.button);
};

const onMouseEnter = (row, col) => {
    if (isPainting.value && currentMouseButton.value !== null) {
        clickCell(row, col, currentMouseButton.value);
    }
};

const onMouseUp = () => {
    isPainting.value = false;
    currentMouseButton.value = null;
};

const formatTime = (seconds) => {
    if (seconds === null || seconds === undefined) return "—";
    if (seconds < 0.001) return `${(seconds * 1_000_000).toFixed(0)} µs`;
    if (seconds < 1) return `${(seconds * 1000).toFixed(3)} ms`;
    return `${seconds.toFixed(3)} s`;
};

const openImportModal = () => {
    if (isViewingHistory.value) return;
    isImportModalOpen.value = true;
    importModalRef.value?.open();
};

const closeImportModal = () => {
    isImportModalOpen.value = false;
};

const openHelpModal = () => {
    showHelpModal.value = true;
};

const closeCurrentModal = () => {
    if (showWelcomeModal.value) {
        showWelcomeModal.value = false;
    } else if (showHelpModal.value) {
        showHelpModal.value = false;
    }
};

const copyMatrixToClipboard = async () => {
    if (!zones.value || zones.value.length === 0) {
        return;
    }

    const matrixText = zones.value
        .map((row) => row.join(" "))
        .join("\n");

    try {
        await navigator.clipboard.writeText(matrixText);
    } catch (err) {
        console.error("Erreur lors de la copie:", err);
    }
};

const downloadGridAsImage = () => {
    if (!zones.value || zones.value.length === 0) {
        return;
    }

    const gridSize = zones.value.length;
    const cellSize = 60;
    const borderWidth = 5;
    const margin = 20;
    const gridTotalSize = gridSize * cellSize + 2 * borderWidth;
    const canvasSize = gridTotalSize + 2 * margin;

    const canvas = document.createElement("canvas");
    canvas.width = canvasSize;
    canvas.height = canvasSize;
    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvasSize, canvasSize);

    zones.value.forEach((row, r) => {
        row.forEach((cellColor, c) => {
            const x = margin + borderWidth + c * cellSize;
            const y = margin + borderWidth + r * cellSize;

            const color = cellColor === -1 ? "#fff" : colors[cellColor];
            ctx.fillStyle = color;
            ctx.fillRect(x, y, cellSize, cellSize);

            ctx.strokeStyle = "#000";
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, cellSize, cellSize);
        });
    });

    ctx.strokeStyle = "#000";
    ctx.lineWidth = borderWidth;
    ctx.strokeRect(
        margin + borderWidth / 2,
        margin + borderWidth / 2,
        gridSize * cellSize,
        gridSize * cellSize
    );

    canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `queens-grid-${gridSize}x${gridSize}-${new Date().toISOString().slice(0, 10)}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
};

const onMatrixApplied = (matrix) => {
    size.value = matrix.length;
    zones.value = matrix;
    positions.value = [];
    solutions.value = [];
    selectedHistoryIndex.value = -1;
    trmPerformance.value = null;
    baselineResult.value = null;
    errorMessage.value = "";
    selectedColor.value = 0;
    isImportModalOpen.value = false;
};

// speedup > 1 → TRM plus rapide, speedup < 1 → baseline plus rapide
const speedup = computed(() => {
    const trmTime = trmPerformance.value?.execution_time;
    const baseTime = baselineResult.value?.performance?.execution_time;
    if (!trmTime || !baseTime || !baselineResult.value?.supported) return null;
    return (baseTime / trmTime).toFixed(1);
});

const submit = async () => {
    const usedColors = new Set(
        zones.value.flat().filter((cell) => cell !== -1)
    );
    const colorToZoneMap = new Map();
    let zoneId = 0;

    Array.from(usedColors)
        .sort((a, b) => a - b)
        .forEach((color) => {
            colorToZoneMap.set(color, zoneId++);
        });

    const zoneGrid = zones.value.map((row) =>
        row.map((cell) => (cell === -1 ? -1 : colorToZoneMap.get(cell)))
    );

    const payload = {
        size: size.value,
        zones: zoneGrid,
    };

    trmPerformance.value = null;
    baselineResult.value = null;
    isSolving.value = true;

    const trmPromise = axios.post(`${TRM_BASE}/api/solve`, payload);
    const baselinePromise = axios.post(`${BASELINE_BASE}/api/solve`, payload);

    let historyEntry = null;
    try {
        const trmRes = await trmPromise;
        const data = trmRes.data;
        solutions.value = data.solutions;
        trmPerformance.value = data.performance;

        if (solutions.value.length === 0) {
            errorMessage.value =
                "Aucune solution trouvée pour cette configuration de zones. Essayez de modifier la disposition des couleurs.";
            positions.value = [];
        } else {
            errorMessage.value = "";
            currentSolutionIndex.value = 0;
            positions.value = solutions.value[0];

            historyEntry = {
                grid: zones.value.map((row) => [...row]),
                solutions: solutions.value.map((sol) => [...sol]),
                timestamp: new Date().toLocaleString("fr-FR"),
                size: size.value,
                trmTime: trmPerformance.value?.execution_time,
                baselineTime: null,
                baselineValid: false,
                baselineSolutionsCount: 0,
            };
            history.value.unshift(historyEntry);
            if (history.value.length > MAX_HISTORY) history.value.splice(MAX_HISTORY);
        }
    } catch (err) {
        console.error(err);
        positions.value = [];
        solutions.value = [];
        errorMessage.value =
            "Erreur lors de la résolution. Vérifiez que le serveur backend fonctionne.";
    }

    try {
        const baselineRes = await baselinePromise;
        baselineResult.value = baselineRes.data;
        const perf = baselineRes.data?.performance;
        if (historyEntry && perf) {
            historyEntry.baselineTime = perf.execution_time ?? null;
            historyEntry.baselineValid = perf.valid ?? false;
            historyEntry.baselineSolutionsCount = perf.solutions_count ?? 0;
        }
    } catch {
        /* baseline optionnel */
    } finally {
        isSolving.value = false;
    }
};

const isGridComplete = computed(() => {
    if (!zones.value || zones.value.length !== size.value) {
        return false;
    }

    return zones.value.every(
        (row) =>
            Array.isArray(row) &&
            row.length === size.value &&
            row.every((cell) => cell !== -1)
    );
});

const hasGridData = computed(() => {
    if (!zones.value || zones.value.length !== size.value) {
        return false;
    }

    return zones.value.some(
        (row) => Array.isArray(row) && row.some((cell) => cell !== -1)
    );
});

const isViewingHistory = computed(() => selectedHistoryIndex.value !== -1);

const emptyCellsCount = computed(() => {
    if (!zones.value) return 0;
    return zones.value.flat().filter((cell) => cell === -1).length;
});

const onTouchStart = (row, col, event) => {
    event.preventDefault();
    currentMouseButton.value = 0;
    isPainting.value = true;
    snapshotPaintState();
    clickCell(row, col, 0);
};

const onTouchMove = (event) => {
    event.preventDefault();
    if (!isPainting.value) return;
    const touch = event.touches[0];
    const el = document.elementFromPoint(touch.clientX, touch.clientY);
    if (!el) return;
    const cell = el.closest("[data-row]");
    if (!cell) return;
    clickCell(parseInt(cell.dataset.row), parseInt(cell.dataset.col), currentMouseButton.value ?? 0);
};

const getCellStyle = (row, col) => {
    if (!zones.value || !zones.value[row] || zones.value[row][col] === undefined) {
        return {
            backgroundColor: "white",
            borderTop: "1px solid #000",
            borderLeft: "1px solid #000",
            borderBottom: "1px solid #000",
            borderRight: "1px solid #000",
            boxSizing: "border-box",
        };
    }

    const currentColor = zones.value[row][col];

    if (currentColor === -1) {
        return {
            backgroundColor: "white",
            borderTop: "1px solid #000",
            borderLeft: "1px solid #000",
            borderBottom: "1px solid #000",
            borderRight: "1px solid #000",
            boxSizing: "border-box",
        };
    }

    let borderTop = "1px solid #000";
    let borderLeft = "1px solid #000";
    let borderBottom = "1px solid #000";
    let borderRight = "1px solid #000";

    if (row > 0) {
        if (zones.value[row - 1][col] !== currentColor) {
            borderTop = "3px solid #000";
        }
    }

    if (col > 0) {
        if (zones.value[row][col - 1] !== currentColor) {
            borderLeft = "3px solid #000";
        }
    }

    if (row < size.value - 1) {
        if (zones.value[row + 1][col] !== currentColor) {
            borderBottom = "3px solid #000";
        }
    }

    if (col < size.value - 1) {
        if (zones.value[row][col + 1] !== currentColor) {
            borderRight = "3px solid #000";
        }
    }

    return {
        backgroundColor: colors[currentColor],
        borderTop,
        borderLeft,
        borderBottom,
        borderRight,
        boxSizing: "border-box",
    };
};

const resetGrid = () => {
    initializeZones();
    solutions.value = [];
    positions.value = [];
    errorMessage.value = "";
    currentSolutionIndex.value = 0;
    selectedHistoryIndex.value = -1;
    isPainting.value = false;
    trmPerformance.value = null;
    baselineResult.value = null;
};

const generateRandomPattern = () => {
    if (isViewingHistory.value) return;
    zones.value = generateRandomConnectedPattern(size.value);
    positions.value = [];
    solutions.value = [];
    errorMessage.value = "";
    currentSolutionIndex.value = 0;
    selectedHistoryIndex.value = -1;
    trmPerformance.value = null;
    baselineResult.value = null;
    isPainting.value = false;
};

const loadSolution = (index) => {
    currentSolutionIndex.value = index;
    positions.value = solutions.value[index];
};

const loadFromHistory = (entry, index) => {
    zones.value = entry.grid.map((row) => [...row]);
    solutions.value = entry.solutions.map((sol) => [...sol]);
    size.value = entry.size;
    positions.value = solutions.value[0] || [];
    currentSolutionIndex.value = 0;
    errorMessage.value = "";
    selectedHistoryIndex.value = index;
    isPainting.value = false;

    if (entry.trmTime !== undefined) {
        trmPerformance.value = {
            execution_time: entry.trmTime,
            solutions_count: solutions.value.length,
        };
    } else {
        trmPerformance.value = null;
    }

    if (entry.baselineTime !== undefined) {
        baselineResult.value = {
            supported: true,
            performance: {
                execution_time: entry.baselineTime,
                valid: entry.baselineValid,
                conflicts: entry.baselineValid ? 0 : 1,
                solutions_count: entry.baselineSolutionsCount ?? 0,
            },
        };
    } else {
        baselineResult.value = null;
    }
};

const toggleHistorySelection = (entry, index) => {
    if (selectedHistoryIndex.value === index) {
        initializeZones();
        selectedHistoryIndex.value = -1;
        solutions.value = [];
        positions.value = [];
        errorMessage.value = "";
        currentSolutionIndex.value = 0;
        trmPerformance.value = null;
        baselineResult.value = null;
    } else {
        loadFromHistory(entry, index);
    }
};

// Mobile : restaurer depuis l'onglet Historique puis revenir à la grille pour la voir.
const restoreFromHistory = (payload) => {
    toggleHistorySelection(payload.entry, payload.index);
    currentView.value = "game";
};

// Génère N zones connexes aléatoires couvrant toutes les cellules (règle du jeu).
// Algorithme : croissance régionale depuis N graines aléatoires (flood-fill)
// → garantit que chaque zone est d'un seul tenant.
const generateRandomConnectedPattern = (size) => {
    const zones = Array.from({ length: size }, () => Array(size).fill(-1));
    const dirs = [[0,1],[0,-1],[1,0],[-1,0]];
    const shuffle = arr => {
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        return arr;
    };

    const seeds = [];
    const minSep = Math.max(1, Math.floor(size / Math.sqrt(size)));
    for (let color = 0; color < size; color++) {
        let placed = false;
        for (let attempt = 0; attempt < 400 && !placed; attempt++) {
            const r = Math.floor(Math.random() * size);
            const c = Math.floor(Math.random() * size);
            if (zones[r][c] !== -1) continue;
            const tooClose = seeds.some(([sr, sc]) => Math.abs(r - sr) + Math.abs(c - sc) < minSep);
            if (!tooClose) {
                zones[r][c] = color;
                seeds.push([r, c]);
                placed = true;
            }
        }
        if (!placed) {
            outer: for (let r = 0; r < size; r++)
                for (let c = 0; c < size; c++)
                    if (zones[r][c] === -1) { zones[r][c] = color; seeds.push([r, c]); placed = true; break outer; }
        }
    }

    const frontiers = seeds.map(([r, c]) => [[r, c]]);
    let remaining = size * size - size;
    let guard = size * size * 10;

    while (remaining > 0 && guard-- > 0) {
        const colorOrder = shuffle(Array.from({ length: size }, (_, i) => i));
        for (const color of colorOrder) {
            if (remaining <= 0) break;
            const frontier = frontiers[color];
            if (frontier.length === 0) continue;
            const fi = Math.floor(Math.random() * frontier.length);
            const [r, c] = frontier[fi];
            const sdirs = shuffle([...dirs]);
            let expanded = false;
            for (const [dr, dc] of sdirs) {
                const nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < size && nc >= 0 && nc < size && zones[nr][nc] === -1) {
                    zones[nr][nc] = color;
                    frontier.push([nr, nc]);
                    remaining--;
                    expanded = true;
                    break;
                }
            }
            if (!expanded) frontier.splice(fi, 1);
        }
    }

    for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
            if (zones[r][c] !== -1) continue;
            let best = 0, bestDist = Infinity;
            for (let rr = 0; rr < size; rr++)
                for (let cc = 0; cc < size; cc++)
                    if (zones[rr][cc] !== -1) {
                        const d = Math.abs(r - rr) + Math.abs(c - cc);
                        if (d < bestDist) { bestDist = d; best = zones[rr][cc]; }
                    }
            zones[r][c] = best;
        }
    }

    const usedColors = new Set(zones.flat());
    if (usedColors.size !== size) {
        for (let r = 0; r < size; r++)
            for (let c = 0; c < size; c++)
                zones[r][c] = r;
    }

    return zones;
};

const benchmarkAllSizes = async () => {
    isBenchmarking.value = true;
    benchmarkStatus.value = "Lancement du benchmark...";
    const benchmarkSizes = [4, 5, 6, 7, 8, 9, 10, 11, 12];
    let successCount = 0;

    for (let idx = 0; idx < benchmarkSizes.length; idx++) {
        const testSize = benchmarkSizes[idx];
        if (!isBenchmarking.value) break;

        const patternName = "Zones aléatoires";
        benchmarkStatus.value = `Test ${testSize}×${testSize} — ${patternName} (${idx + 1}/${benchmarkSizes.length})`;

        const testZones = generateRandomConnectedPattern(testSize);

        const payload = {
            size: testSize,
            zones: testZones,
        };

        const [trmRes, baselineRes] = await Promise.allSettled([
            axios.post(`${TRM_BASE}/api/solve`, payload),
            axios.post(`${BASELINE_BASE}/api/solve`, payload),
        ]);

        let resultSolutions = [];
        let trm_solutions_count = 0;
        if (trmRes.status === "fulfilled") {
            resultSolutions = trmRes.value.data.solutions;
            trm_solutions_count = trmRes.value.data.performance.solutions_count;
            successCount++;
        }

        if (trmRes.status === "fulfilled") {
            history.value.unshift({
                grid: testZones.map((row) => [...row]),
                solutions: resultSolutions.map((sol) => [...sol]),
                timestamp: new Date().toLocaleString("fr-FR"),
                size: testSize,
                patternName,
                trmTime: trmRes.value.data.performance.execution_time,
                trmSolutionsCount: trm_solutions_count,
                baselineTime: baselineRes.status === "fulfilled" ? baselineRes.value.data.performance.execution_time : null,
                baselineValid: baselineRes.status === "fulfilled" ? baselineRes.value.data.performance.valid : false,
                baselineSolutionsCount: baselineRes.status === "fulfilled" ? baselineRes.value.data.performance.solutions_count : 0,
            });
            if (history.value.length > MAX_HISTORY) history.value.splice(MAX_HISTORY);
        }
    }

    benchmarkStatus.value = `Benchmark terminé! ${successCount}/${benchmarkSizes.length} tests réussis`;
    isBenchmarking.value = false;
    setTimeout(() => {
        benchmarkStatus.value = "";
    }, 3000);
};

const toggleHistory = () => {
    historyVisible.value = !historyVisible.value;
};

// Calculer la taille optimale des cases en fonction de l'écran disponible
const cellSize = computed(() => {
    const isMobile = screenWidth.value <= 600;
    // Mobile : grille à gauche + bande palette fine à droite. On réserve la largeur
    // de la bande palette et la hauteur du titre/onglets/barre d'outils/sélecteur.
    const paletteStrip = isMobile ? 56 : 0;
    const availableWidth =
        screenWidth.value * (isMobile ? 0.96 : 0.7) - paletteStrip;
    // Quand un résultat s'affiche (solutions + stats des 2 modèles), on réduit la
    // grille sur mobile pour laisser la place au panneau de résultats sans scroll.
    const hasResults =
        solutions.value.length > 0 ||
        trmPerformance.value !== null ||
        baselineResult.value !== null;
    const availableHeight = isMobile
        ? screenHeight.value - (hasResults ? 360 : 200)
        : screenHeight.value * 0.6;
    const borderSpace = (size.value - 1) * 1;
    const maxCellSizeWidth = (availableWidth - borderSpace - 6) / size.value;
    const maxCellSizeHeight = (availableHeight - borderSpace - 6) / size.value;
    const maxCellSize = Math.min(maxCellSizeWidth, maxCellSizeHeight);
    return Math.max(20, Math.min(60, Math.floor(maxCellSize)));
});

const queenIconSize = computed(() =>
    Math.max(16, Math.min(40, cellSize.value - 8))
);

const updateScreenSize = () => {
    if (typeof window !== "undefined") {
        screenWidth.value = window.innerWidth;
        screenHeight.value = window.innerHeight;
    }
};

const handleKeyDown = (event) => {
    if (event.key === "Escape") {
        if (isImportModalOpen.value) { closeImportModal(); return; }
        if (showHelpModal.value || showWelcomeModal.value) { closeCurrentModal(); return; }
    }
    if (["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)) return;

    switch (event.key) {
        case "Enter":
        case " ":
            if (isGridComplete.value && !isViewingHistory.value) {
                event.preventDefault();
                submit();
            }
            break;
        case "ArrowRight":
            if (solutions.value.length > 1) {
                event.preventDefault();
                loadSolution((currentSolutionIndex.value + 1) % solutions.value.length);
            }
            break;
        case "ArrowLeft":
            if (solutions.value.length > 1) {
                event.preventDefault();
                loadSolution((currentSolutionIndex.value - 1 + solutions.value.length) % solutions.value.length);
            }
            break;
        case "z":
        case "Z":
            if (event.ctrlKey || event.metaKey) {
                event.preventDefault();
                undoPaint();
            }
            break;
    }
};

onMounted(() => {
    updateScreenSize();
    window.addEventListener("resize", updateScreenSize);
    window.addEventListener("mouseup", onMouseUp);
    window.addEventListener("mouseleave", onMouseUp);
    window.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
    window.removeEventListener("resize", updateScreenSize);
    window.removeEventListener("mouseup", onMouseUp);
    window.removeEventListener("mouseleave", onMouseUp);
    window.removeEventListener("keydown", handleKeyDown);
});

const initializeHistoryVisibility = () => {
    if (isMobile.value && historyVisible.value) {
        historyVisible.value = false;
    } else if (!isMobile.value && !historyVisible.value) {
        historyVisible.value = true;
    }
};

watch(isMobile, (newIsMobile) => {
    if (newIsMobile && historyVisible.value) {
        historyVisible.value = false;
    } else if (!newIsMobile && !historyVisible.value) {
        historyVisible.value = true;
    }
});

watch(zones, () => {
    if (currentDraftIndex.value >= 0) {
        saveDraft();
    }
}, { deep: true });

initializeZones();
initializeHistoryVisibility();
if (drafts.value.length === 0) {
    createNewDraft();
}

defineExpose({
    zones,
    size,
    paintHistory,
    selectedColor,
    isGridComplete,
    emptyCellsCount,
    drafts,
    currentDraftIndex,
    errorMessage,
    solutions,
    initializeZones,
    undoPaint,
    snapshotPaintState,
});
</script>

<template>
    <div class="app">
        <h1 class="title">Queens Game Solveur</h1>
        <nav class="view-tabs">
            <button
                class="view-tab"
                :class="{ active: currentView === 'game' }"
                @click="currentView = 'game'"
            >
                <i class="ri-grid-line" aria-hidden="true"></i> Jeu
            </button>
            <button
                v-if="screenWidth <= 600"
                class="view-tab"
                :class="{ active: currentView === 'history' }"
                @click="currentView = 'history'"
            >
                <i class="ri-history-line" aria-hidden="true"></i> Historique
            </button>
            <button
                class="view-tab"
                :class="{ active: currentView === 'stats' }"
                @click="currentView = 'stats'"
            >
                <i class="ri-bar-chart-grouped-line" aria-hidden="true"></i> Statistiques
            </button>
        </nav>

        <HelpWelcomeModal
            :model-value="showWelcomeModal || showHelpModal"
            :mode="showWelcomeModal ? 'welcome' : 'help'"
            @close="closeCurrentModal"
        />

        <BenchmarkChart v-if="currentView === 'stats'" :history="history" />

        <div v-if="currentView === 'history'" class="history-view">
            <HistoryPanel
                :history="history"
                :visible="true"
                :selected-index="selectedHistoryIndex"
                @restore="restoreFromHistory"
            />
        </div>

        <div v-if="currentView === 'game'" class="main-layout" :class="{ 'history-hidden': !historyVisible }">
            <div class="history-slot">
                <HistoryPanel
                    :history="history"
                    :visible="historyVisible"
                    :selected-index="selectedHistoryIndex"
                    @restore="toggleHistorySelection($event.entry, $event.index)"
                />
            </div>
            <div class="grid-container">
                <div class="grid-header">
                    <div class="grid-toolbar" role="toolbar" aria-label="Actions sur la grille">
                        <button
                            @click="clearForNewGrid"
                            class="icon-btn new-icon-btn"
                            title="Nouvelle grille"
                            aria-label="Nouvelle grille"
                        >
                            <i class="ri-add-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="submit"
                            :disabled="!isGridComplete || isViewingHistory || isSolving"
                            class="icon-btn solve-icon-btn"
                            :title="isGridComplete ? 'Résoudre' : `${emptyCellsCount} case${emptyCellsCount > 1 ? 's' : ''} vide${emptyCellsCount > 1 ? 's' : ''}`"
                            :aria-label="isGridComplete ? 'Résoudre' : `${emptyCellsCount} case${emptyCellsCount > 1 ? 's' : ''} vide${emptyCellsCount > 1 ? 's' : ''}`"
                        >
                            <i
                                :class="isSolving ? 'ri-loader-4-line spin' : 'ri-check-line'"
                                aria-hidden="true"
                            ></i>
                        </button>
                        <button
                            @click="resetGrid"
                            :disabled="!hasGridData || isViewingHistory"
                            class="icon-btn reset-icon-btn"
                            title="Réinitialiser la grille"
                            aria-label="Réinitialiser la grille"
                        >
                            <i class="ri-refresh-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="generateRandomPattern"
                            :disabled="isViewingHistory"
                            class="icon-btn random-icon-btn"
                            title="Remplir aléatoirement la grille"
                            aria-label="Remplir aléatoirement la grille"
                        >
                            <i class="ri-shuffle-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="benchmarkAllSizes"
                            class="icon-btn benchmark-icon-btn"
                            :disabled="isBenchmarking"
                            title="Benchmark 1 grille/taille (4→12)"
                            aria-label="Benchmark 1 grille/taille (4→12)"
                        >
                            <i class="ri-bar-chart-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="openImportModal"
                            class="icon-btn import-icon-btn"
                            :disabled="isViewingHistory"
                            title="Importer une image"
                            aria-label="Importer une image"
                        >
                            <i class="ri-upload-cloud-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="copyMatrixToClipboard"
                            class="icon-btn copy-icon-btn"
                            title="Copier la matrice"
                            aria-label="Copier la matrice"
                        >
                            <i class="ri-file-copy-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="downloadGridAsImage"
                            class="icon-btn download-icon-btn"
                            title="Télécharger la grille en image"
                            aria-label="Télécharger la grille en image"
                        >
                            <i class="ri-download-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="openHelpModal"
                            class="icon-btn help-icon-btn"
                            title="Afficher l'aide"
                            aria-label="Afficher l'aide"
                        >
                            <i class="ri-question-line" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div v-if="screenWidth <= 600" class="mobile-size-selector">
                        <label>Taille</label>
                        <select v-model.number="size" @change="initializeZones">
                            <option
                                v-for="s in [4, 5, 6, 7, 8, 9, 10, 11, 12]"
                                :key="s"
                                :value="s"
                            >
                                {{ s }}×{{ s }}
                            </option>
                        </select>
                    </div>
                    <div v-if="benchmarkStatus" class="benchmark-status header-status">
                        {{ benchmarkStatus }}
                    </div>
                    <button
                        v-if="screenWidth < 600"
                        @click="toggleHistory"
                        class="toggle-history-btn"
                    >
                        {{ historyVisible ? "Masquer" : "Afficher" }}
                        l'historique
                    </button>
                </div>
                <div
                    class="grid"
                    :style="{
                        gridTemplateColumns: `repeat(${size}, ${cellSize}px)`,
                        width: `${cellSize * size + 10}px`,
                        height: `${cellSize * size + 10}px`,
                    }"
                    @mouseup="onMouseUp"
                    @touchmove.prevent="onTouchMove"
                    @touchend="onMouseUp"
                >
                    <div
                        v-for="(row, r) in zones"
                        :key="r"
                        style="display: contents"
                    >
                        <div
                            v-for="(_, c) in row"
                            :key="c"
                            class="cell"
                            :data-row="r"
                            :data-col="c"
                            :style="getCellStyle(r, c)"
                            @mousedown="onMouseDown(r, c, $event)"
                            @mouseenter="onMouseEnter(r, c)"
                            @mouseup="onMouseUp"
                            @touchstart.prevent="onTouchStart(r, c, $event)"
                            @contextmenu.prevent
                        >
                            <svg
                                v-if="
                                    positions.some(
                                        (p) => p[0] === r && p[1] === c
                                    )
                                "
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 640 640"
                                class="queen-icon"
                                :style="{
                                    width: queenIconSize + 'px',
                                    height: queenIconSize + 'px',
                                }"
                            >
                                <path
                                    d="M320 144C346.5 144 368 122.5 368 96C368 69.5 346.5 48 320 48C293.5 48 272 69.5 272 96C272 122.5 293.5 144 320 144zM69.5 249L192 448L135.8 518.3C130.8 524.6 128 532.4 128 540.5C128 560.1 143.9 576 163.5 576L476.4 576C496 576 511.9 560.1 511.9 540.5C511.9 532.4 509.2 524.6 504.1 518.3L448 448L570.5 249C574.1 243.1 576 236.3 576 229.4L576 228.8C576 208.5 559.5 192 539.2 192C531.9 192 524.8 194.2 518.8 198.2L501.9 209.5C489.2 218 472.3 216.3 461.5 205.5L427.4 171.4C420.1 164.1 410.2 160 400 160C389.8 160 379.9 164.1 372.7 171.3L342.6 201.4C330.1 213.9 309.8 213.9 297.3 201.4L267.2 171.3C260.1 164.1 250.2 160 240 160C229.8 160 219.9 164.1 212.7 171.3L178.6 205.4C167.8 216.2 150.9 217.9 138.2 209.4L121.3 198.2C115.2 194.2 108.1 192 100.9 192C80.6 192 64.1 208.5 64.1 228.8L64.1 229.4C64.1 236.3 66 243.1 69.6 249z"
                                />
                            </svg>
                        </div>
                    </div>
                </div>
                <div v-if="solutions.length > 0" class="solutions-info">
                    <p>
                        Nombre de solutions:
                        <strong>{{ solutions.length }}</strong>
                    </p>
                    <div v-if="solutions.length > 1" class="solution-buttons">
                        <button
                            v-for="(_, idx) in solutions.slice(0, maxSolButtons)"
                            :key="idx"
                            @click="loadSolution(idx)"
                            class="solution-btn"
                            :class="{ active: currentSolutionIndex === idx }"
                        >
                            Solution {{ idx + 1 }}
                        </button>
                        <span v-if="solutions.length > maxSolButtons" class="more-solutions"
                            >... et {{ solutions.length - maxSolButtons }} autres</span
                        >
                    </div>
                </div>

                <!-- Panneau de comparaison des modèles -->
                <div v-if="trmPerformance || baselineResult" class="comparison-panel">
                    <h4 class="comparison-title">⚡ Comparaison des modèles</h4>
                    <div class="comparison-rows">
                        <div class="comparison-row">
                            <span class="model-label trm-label">TRM (récursif optimisé)</span>
                            <span class="model-time">{{ formatTime(trmPerformance?.execution_time) }}</span>
                            <span class="model-badge valid-badge">
                                ✓ {{ trmPerformance?.solutions_count ?? 0 }} sol.
                            </span>
                        </div>
                        <div class="comparison-row">
                            <span class="model-label baseline-label">Baseline (backtracking naïvement)</span>
                            <template v-if="baselineResult?.supported === false">
                                <span class="model-time muted">N/A</span>
                                <span class="model-badge unsupported-badge">❌ Erreur</span>
                            </template>
                            <template v-else-if="baselineResult?.performance">
                                <span class="model-time">{{ formatTime(baselineResult.performance.execution_time) }}</span>
                                <span
                                    class="model-badge"
                                    :class="baselineResult.performance.solutions_count === 0 ? 'neutral-badge' : 'valid-badge'"
                                >
                                    {{ baselineResult.performance.solutions_count === 0
                                        ? `0 sol.`
                                        : `✓ ${baselineResult.performance.solutions_count} sol.` }}
                                </span>
                            </template>
                            <template v-else>
                                <span class="model-time muted">—</span>
                            </template>
                        </div>
                    </div>
                    <div v-if="speedup !== null" class="speedup-info">
                        <template v-if="Number(speedup) >= 1">
                            TRM est <strong>{{ speedup }}×</strong> plus rapide que le baseline
                        </template>
                        <template v-else>
                            Le baseline est <strong>{{ (1 / Number(speedup)).toFixed(1) }}×</strong> plus rapide que TRM
                        </template>
                    </div>
                </div>

                <div v-if="errorMessage" class="error-message">
                    {{ errorMessage }}
                </div>
            </div>
            <div class="sidebar">
                <div class="size-selector">
                    <label>Taille:</label>
                    <select v-model.number="size" @change="initializeZones">
                        <option
                            v-for="s in [4, 5, 6, 7, 8, 9, 10, 11, 12]"
                            :key="s"
                            :value="s"
                        >
                            {{ s }}x{{ s }}
                        </option>
                    </select>
                </div>
                <div class="palette">
                    <div
                        v-for="colorIndex in availableColorIndices"
                        :key="colorIndex"
                        class="color-btn"
                        :class="{ selected: selectedColor === colorIndex }"
                        :style="{ backgroundColor: colors[colorIndex] }"
                        @click="selectedColor = colorIndex"
                    ></div>
                </div>
            </div>
        </div>

        <!-- Onglets de brouillons - FIXE en bas -->
        <div v-if="currentView !== 'stats' && drafts.length > 0" class="drafts-panel">
            <div class="drafts-tabs">
                <div
                    v-for="(draft, index) in drafts"
                    :key="draft.id"
                    class="draft-tab"
                    :class="{ active: currentDraftIndex === index }"
                    @click="switchDraft(index)"
                    :title="draft.updatedAt"
                >
                    <span class="draft-size">{{ draft.size }}×{{ draft.size }}</span>
                    <button
                        @click.stop="deleteDraft(index)"
                        class="draft-delete-btn"
                        title="Supprimer ce brouillon"
                    >×</button>
                </div>
            </div>
        </div>

        <ImportModal
            ref="importModalRef"
            :visible="isImportModalOpen"
            :colors="colors"
            :trm-base="TRM_BASE"
            @apply="onMatrixApplied"
            @close="closeImportModal"
        />

        <!-- Loader de résolution : montre que les solveurs réfléchissent -->
        <div v-if="isSolving" class="solving-overlay" role="status" aria-live="polite">
            <div class="solving-card">
                <div class="solving-spinner"></div>
                <p class="solving-title">Résolution en cours…</p>
                <p class="solving-sub">
                    Les deux solveurs explorent la grille{{ size >= 11 ? " — les grandes grilles peuvent prendre quelques secondes" : "" }}.
                </p>
            </div>
        </div>
    </div>
</template>

<style>
/* Reset et dimensions globales */
* {
    box-sizing: border-box;
}

html,
body,
#app {
    width: 100%;
    height: 100dvh;
    margin: 0;
    padding: 0;
    overflow: hidden;
    overscroll-behavior: none;
    font-family: Arial, sans-serif;
}
</style>

<style scoped>
.app {
    width: 100%;
    height: 100dvh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0;
    margin: 0;
    background-color: #f5f5f5;
    overflow: hidden;
    box-sizing: border-box;
}

.title {
    text-align: center;
    margin-bottom: 0.5vh;
    margin-top: 0.5vh;
    color: #333;
    font-size: 2rem;
    font-weight: bold;
    flex-shrink: 0;
}

.view-tabs {
    display: flex;
    gap: 6px;
    margin-bottom: 1vh;
    background: #e8e8e8;
    padding: 4px;
    border-radius: 10px;
    flex-shrink: 0;
}

.view-tab {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 18px;
    border: none;
    border-radius: 7px;
    font-size: 0.88rem;
    font-weight: 600;
    cursor: pointer;
    background: transparent;
    color: #666;
    transition: background 0.15s, color 0.15s;
}

.view-tab:hover {
    background: rgba(255, 255, 255, 0.7);
    color: #333;
}

.view-tab.active {
    background: #fff;
    color: #333;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

.main-layout {
    display: grid;
    grid-template-columns: 20vw 1fr 18vw;
    justify-content: center;
    align-items: flex-start;
    gap: 2vw;
    width: 100%;
    padding: 1vh 1vw;
    flex: 1;
    min-height: 0;
    max-width: 1400px;
    overflow-y: auto;
    box-sizing: border-box;
}

.main-layout.history-hidden {
    grid-template-columns: 0 1fr 18vw;
}

.main-layout.history-hidden .history-slot {
    display: none;
}

@media (max-width: 1200px) {
    .main-layout {
        grid-template-columns: 20vw 1fr 18vw;
        gap: 2vw;
    }

    .main-layout.history-hidden {
        grid-template-columns: 0 1fr 18vw;
    }
}

@media (max-width: 900px) {
    .main-layout {
        grid-template-columns: 1fr;
        gap: 2vw;
    }

    .main-layout.history-hidden {
        grid-template-columns: 1fr;
    }

    .history-slot {
        order: -1;
        max-width: none;
        width: 100%;
    }

    .sidebar {
        order: 1;
        min-width: auto;
        width: 100%;
        max-width: 400px;
    }

    .grid-container {
        order: 0;
        max-width: none;
        width: 100%;
    }
}

@media (max-width: 400px) {
    .queen-icon {
        width: 18px;
        height: 18px;
    }
}

.grid-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    width: 100%;
    padding: 0;
    box-sizing: border-box;
    overflow: visible;
}

.grid-header {
    position: relative;
    z-index: 1;
}

.toggle-history-btn {
    padding: 0.5vh 1vw;
    font-size: 0.9rem;
    cursor: pointer;
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 6px;
    transition: background-color 0.3s;
}

.toggle-history-btn:hover {
    background-color: #5a6268;
}

.grid-header {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 10px;
}

.grid-toolbar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.icon-btn {
    width: 40px;
    height: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    background: #fff;
    color: #333;
    cursor: pointer;
    transition: box-shadow 0.15s ease, background-color 0.15s ease;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.icon-btn:hover:not(:disabled) {
    background-color: #f4f4f4;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.14);
}

.icon-btn:disabled {
    opacity: 0.65;
    cursor: not-allowed;
    background-color: #bdbdbd;
    color: #fff;
    box-shadow: none;
}

.icon-btn svg,
.icon-btn i {
    width: 20px;
    height: 20px;
    line-height: 1;
    font-size: 1.2rem;
    color: currentColor;
}

.solve-icon-btn {
    background-color: #4caf50 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(76, 175, 80, 0.3);
}

.solve-icon-btn:hover:not(:disabled) {
    background-color: #45a049 !important;
    box-shadow: 0 3px 8px rgba(76, 175, 80, 0.5);
}

.solve-icon-btn:disabled {
    background-color: #8bc34a !important;
    color: #fff !important;
    opacity: 0.65;
    cursor: not-allowed;
    box-shadow: none;
}

.reset-icon-btn {
    background-color: #d32f2f !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
}

.reset-icon-btn:hover:not(:disabled) {
    background-color: #c62828 !important;
    box-shadow: 0 3px 8px rgba(211, 47, 47, 0.5);
}

.reset-icon-btn:disabled {
    background-color: #ef9a9a !important;
    color: #fff !important;
    opacity: 0.65;
    cursor: not-allowed;
    box-shadow: none;
}

.grid {
    display: grid;
    gap: 0;
    border: 5px solid #000;
    background-color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    aspect-ratio: 1;
    box-sizing: border-box;
    overflow: hidden;
    flex-shrink: 0;
    min-width: 0;
    touch-action: none;
}

.cell {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-weight: bold;
    font-size: 24px;
    transition: opacity 0.2s;
    box-sizing: border-box;
}

.cell:hover {
    opacity: 0.8;
}

.queen-icon {
    fill: #000;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}

.error-message {
    margin-top: 1vh;
    padding: 1vh 1.5vw;
    background-color: #ffebee;
    color: #c62828;
    border: 1px solid #ef5350;
    border-radius: 6px;
    font-size: 0.9rem;
    text-align: center;
    max-width: 80vw;
}

.drafts-panel {
    width: 100%;
    max-width: none;
    padding: 3px 8px 0;
    background-color: #f0f0f0;
    border-top: 1px solid #ccc;
    flex-shrink: 0;
    margin-top: 0;
    overflow: visible;
    box-sizing: border-box;
}

.drafts-tabs {
    display: flex;
    gap: 2px;
    overflow-x: auto;
    align-items: flex-end;
    scrollbar-width: thin;
}

.draft-tab {
    flex-shrink: 0;
    padding: 3px 8px 3px 10px;
    background-color: #e0e0e0;
    border: 1px solid #bbb;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    cursor: pointer;
    transition: background 0.15s;
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.78rem;
    color: #555;
    line-height: 1;
    height: 26px;
}

.draft-tab:hover {
    background-color: #f0f0f0;
    color: #222;
}

.draft-tab.active {
    background-color: #fff;
    border-color: #aaa;
    color: #111;
    font-weight: 600;
    height: 28px;
}

.draft-size {
    font-weight: inherit;
    font-size: inherit;
    white-space: nowrap;
}

.draft-delete-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.85rem;
    color: #999;
    padding: 0;
    width: 14px;
    height: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 2px;
    line-height: 1;
    transition: color 0.15s, background 0.15s;
}

.draft-delete-btn:hover {
    color: #d32f2f;
    background: rgba(211,47,47,0.1);
}

.icon-btn svg {
    width: 20px;
    height: 20px;
    fill: currentColor;
}

.benchmark-icon-btn {
    background-color: #1565c0;
    color: #fff;
    border: none;
    box-shadow: 0 2px 6px rgba(21, 101, 192, 0.3);
}

.benchmark-icon-btn:hover:not(:disabled) {
    background-color: #1144a0;
    box-shadow: 0 3px 8px rgba(21, 101, 192, 0.5);
}

.import-icon-btn {
    background-color: #9c27b0;
    color: #fff;
    border: none;
    box-shadow: 0 2px 6px rgba(156, 39, 176, 0.3);
}

.import-icon-btn:hover:not(:disabled) {
    background-color: #7b1fa2;
    box-shadow: 0 3px 8px rgba(156, 39, 176, 0.5);
}

.help-icon-btn {
    background-color: #00bcd4 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(0, 188, 212, 0.3);
}

.help-icon-btn:hover:not(:disabled) {
    background-color: #0097a7 !important;
    box-shadow: 0 3px 8px rgba(0, 188, 212, 0.5);
}

.copy-icon-btn {
    background-color: #2196f3 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(33, 150, 243, 0.3);
}

.copy-icon-btn:hover:not(:disabled) {
    background-color: #1976d2 !important;
    box-shadow: 0 3px 8px rgba(33, 150, 243, 0.5);
}

.download-icon-btn {
    background-color: #ff6f00 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(255, 111, 0, 0.3);
}

.download-icon-btn:hover:not(:disabled) {
    background-color: #e65100 !important;
    box-shadow: 0 3px 8px rgba(255, 111, 0, 0.5);
}

.new-icon-btn {
    background-color: #ff9800 !important;
    color: #fff !important;
    border: none;
    box-shadow: 0 2px 6px rgba(255, 152, 0, 0.3);
}

.new-icon-btn:hover:not(:disabled) {
    background-color: #f57c00 !important;
    box-shadow: 0 3px 8px rgba(255, 152, 0, 0.5);
}

.benchmark-status {
    margin-top: 1vh;
    padding: 0.8vh 1.5vw;
    background-color: #e3f2fd;
    color: #1565c0;
    border: 1px solid #90caf9;
    border-radius: 6px;
    font-size: 0.85rem;
    text-align: center;
    font-weight: 500;
}

.header-status {
    width: 100%;
    margin-top: 0.75rem;
}

/* --- Panneau de comparaison des modèles --- */
.comparison-panel {
    margin-top: 1.2vh;
    padding: 1vh 1.2vw;
    background: #f0f4ff;
    border: 1px solid #c5cfe8;
    border-radius: 8px;
    min-width: 260px;
    max-width: 420px;
}

.comparison-title {
    margin: 0 0 0.8vh 0;
    font-size: 0.85rem;
    font-weight: 700;
    color: #3a3a3a;
}

.comparison-rows {
    display: flex;
    flex-direction: column;
    gap: 0.5vh;
}

.comparison-row {
    display: flex;
    align-items: center;
    gap: 0.5vw;
    font-size: 0.82rem;
}

.model-label {
    flex: 0 0 140px;
    font-weight: 600;
    white-space: nowrap;
}

.trm-label { color: #1565c0; }
.baseline-label { color: #6a1b9a; }

.model-time {
    flex: 0 0 80px;
    font-family: monospace;
    font-size: 0.85rem;
    text-align: right;
    color: #222;
}

.model-time.muted { color: #999; }

.model-badge {
    flex: 1;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}

.valid-badge     { background: #e8f5e9; color: #2e7d32; }
.neutral-badge   { background: #e8f0ff; color: #1e3a8a; }
.invalid-badge   { background: #ffebee; color: #c62828; }
.unsupported-badge { background: #fff3e0; color: #e65100; }

.speedup-info {
    margin-top: 0.8vh;
    font-size: 0.78rem;
    color: #555;
    border-top: 1px solid #d0d8f0;
    padding-top: 0.6vh;
}

.sidebar {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    min-width: 200px;
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.size-selector {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    width: 100%;
}

.size-selector label {
    font-weight: bold;
    color: #333;
}

.size-selector select {
    padding: 0.5vh 1vw;
    border-radius: 8px;
    border: 0.2vw solid #333;
    background-color: #f9f9f9;
    font-size: 1rem;
    cursor: pointer;
    min-width: 10vw;
    width: 100%;
}

.palette {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    max-height: none;
    overflow-y: auto;
}

.color-btn {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin: 0 auto;
    position: relative;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1);
    border: 3px solid rgba(255, 255, 255, 0.8);
}

.color-btn:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2), 0 4px 8px rgba(0, 0, 0, 0.15);
    border-color: rgba(255, 255, 255, 1);
}

.color-btn.selected {
    transform: translateY(-2px) scale(1.08);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25), 0 4px 12px rgba(0, 0, 0, 0.2);
    border: 4px solid #fff;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25),
            0 4px 12px rgba(0, 0, 0, 0.2), 0 0 0 0 rgba(59, 130, 246, 0.5);
    }
    50% {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25),
            0 4px 12px rgba(0, 0, 0, 0.2), 0 0 0 8px rgba(59, 130, 246, 0);
    }
    100% {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25),
            0 4px 12px rgba(0, 0, 0, 0.2), 0 0 0 0 rgba(59, 130, 246, 0);
    }
}

.solutions-info {
    margin-top: 3vh;
    text-align: center;
}

.solutions-info p {
    margin: 0 0 1vh 0;
    font-size: 1rem;
    color: #333;
}

.solution-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 1vw;
    justify-content: center;
}

.solution-btn {
    padding: 0.5vh 1vw;
    font-size: 0.9rem;
    cursor: pointer;
    background-color: #2196f3;
    color: white;
    border: none;
    border-radius: 6px;
    transition: background-color 0.3s;
}

.solution-btn:hover {
    background-color: #1976d2;
}

.solution-btn.active {
    background-color: #4caf50;
}

.more-solutions {
    font-size: 0.9rem;
    color: #666;
    margin-left: 1vw;
    align-self: center;
}

/* ===== Loader de résolution ===== */
.solving-overlay {
    position: fixed;
    inset: 0;
    z-index: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(20, 24, 40, 0.55);
    backdrop-filter: blur(2px);
    padding: 1rem;
}

.solving-card {
    background: #fff;
    border-radius: 16px;
    padding: 1.6rem 2rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
    text-align: center;
    max-width: 320px;
}

.solving-spinner {
    width: 46px;
    height: 46px;
    margin: 0 auto 1rem;
    border: 5px solid #e3e8f0;
    border-top-color: #1565c0;
    border-radius: 50%;
    animation: solving-spin 0.8s linear infinite;
}

.solving-title {
    margin: 0 0 0.4rem;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a2b4a;
}

.solving-sub {
    margin: 0;
    font-size: 0.85rem;
    color: #667085;
    line-height: 1.4;
}

.spin {
    display: inline-block;
    animation: solving-spin 0.8s linear infinite;
}

@keyframes solving-spin {
    to {
        transform: rotate(360deg);
    }
}

/* ============================================================
   MOBILE — placé en dernier pour l'emporter sur les règles de
   base (même spécificité => l'ordre source décide).
   Disposition : grille à gauche + bande palette fine à droite.
   ============================================================ */
.mobile-size-selector {
    display: none;
}

@media (max-width: 600px) {
    .app {
        padding: 0.4vh 2vw;
        overflow: hidden;
        justify-content: flex-start;
    }

    .title {
        font-size: 1.05rem;
        margin: 0.2vh 0;
    }

    .view-tabs {
        margin-bottom: 0.4vh;
    }

    /* Historique masqué sur mobile pour tenir sur un écran */
    .history-slot,
    .toggle-history-btn {
        display: none !important;
    }

    /* Grille | palette côte à côte */
    .main-layout,
    .main-layout.history-hidden {
        display: flex;
        flex-direction: row;
        align-items: stretch;
        justify-content: center;
        flex: 1;
        min-height: 0;
        width: 100%;
        gap: 2vw;
        padding: 0;
        overflow: hidden;
    }

    .grid-container {
        flex: 1 1 auto;
        min-width: 0;
        min-height: 0;
        justify-content: flex-start;
        gap: 0.5vh;
        overflow: hidden;
    }

    .grid-header {
        width: 100%;
    }

    /* Actions : barre fixe en bas de l'écran (elles ne tiennent plus en haut) */
    .grid-toolbar {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 60;
        display: flex;
        flex-flow: row nowrap;
        gap: 4px;
        justify-content: space-around;
        align-items: center;
        padding: 6px 4px;
        background: #fff;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.15);
    }

    .grid-toolbar .icon-btn {
        width: 32px;
        height: 32px;
        font-size: 0.85rem;
        flex: 0 0 auto;
    }

    /* On réserve la place de la barre d'actions fixe */
    .main-layout,
    .main-layout.history-hidden {
        padding-bottom: 52px;
    }

    /* Brouillons masqués sur mobile (évite le chevauchement avec la barre) */
    .drafts-panel {
        display: none;
    }

    /* Vue Historique plein écran (onglet mobile) */
    .history-view {
        flex: 1;
        min-height: 0;
        width: 100%;
        overflow-y: auto;
        padding: 0 1vw 52px;
    }

    /* Sélecteur de taille compact, en haut sous la barre d'outils */
    .mobile-size-selector {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-top: 0.4vh;
        font-size: 0.85rem;
    }

    .mobile-size-selector label {
        font-weight: 600;
        color: #333;
    }

    .mobile-size-selector select {
        padding: 3px 8px;
        border-radius: 6px;
        border: 2px solid #333;
        background: #f9f9f9;
        font-size: 0.9rem;
    }

    /* Bande palette fine, verticale, à droite */
    .sidebar {
        flex: 0 0 auto;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: auto;
        min-width: 0;
        gap: 0;
        padding: 6px 5px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
    }

    /* Le sélecteur de taille n'est plus dans la bande palette sur mobile */
    .sidebar .size-selector {
        display: none;
    }

    .palette {
        display: flex;
        flex-direction: column;
        flex-wrap: nowrap;
        justify-content: center;
        gap: 5px;
        height: 100%;
        width: auto;
        padding: 0;
        background: none;
        box-shadow: none;
        overflow: visible;
    }

    .color-btn {
        flex: 0 1 auto;
        width: 30px;
        height: 30px;
        max-height: 34px;
        aspect-ratio: 1;
        margin: 0;
        border-width: 2px;
    }

    .color-btn.selected {
        animation: none;
        transform: none;
        outline: 3px solid #3b82f6;
        outline-offset: 1px;
    }

    /* Résultats sous la grille : compacts pour rester sur un écran */
    .grid-container {
        overflow: visible;
    }

    .solutions-info {
        margin-top: 0.6vh;
        width: 100%;
    }

    .solutions-info p {
        margin: 0 0 4px 0;
        font-size: 0.85rem;
    }

    .solution-buttons {
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        gap: 5px;
    }

    .solution-btn {
        padding: 4px 8px;
        font-size: 0.78rem;
    }

    .more-solutions {
        font-size: 0.78rem;
        margin-left: 0;
    }

    /* Stats des 2 modèles : panneau compact pleine largeur */
    .comparison-panel {
        margin-top: 0.6vh;
        width: 100%;
        min-width: 0;
        max-width: none;
        padding: 8px 10px;
    }

    .comparison-title {
        font-size: 0.8rem;
        margin-bottom: 6px;
    }

    .comparison-row {
        gap: 6px;
        font-size: 0.75rem;
    }

    .model-label {
        flex: 1 1 auto;
        min-width: 0;
        white-space: normal;
        font-size: 0.72rem;
        line-height: 1.2;
    }

    .model-time {
        flex: 0 0 auto;
        font-size: 0.72rem;
    }

    .model-badge {
        flex: 0 0 auto;
        font-size: 0.68rem;
    }

    .speedup-info {
        font-size: 0.72rem;
    }
}

@media (max-width: 380px) {
    .color-btn {
        width: 26px;
        height: 26px;
    }
}
</style>
