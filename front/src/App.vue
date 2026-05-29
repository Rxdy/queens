<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import axios from "axios";
import BenchmarkChart from "./BenchmarkChart.vue";

// Configuration axios sans timeout pour permettre les requêtes long-running
axios.defaults.timeout = 0; // 0 = pas de timeout

const currentView = ref("game");

const size = ref(8);
const zones = ref([]);
const positions = ref([]);
const solutions = ref([]);
const selectedColor = ref(0);
const errorMessage = ref("");
const history = ref([]);
const historyVisible = ref(true);
const trmPerformance = ref(null);
const baselineResult = ref(null);
const isBenchmarking = ref(false);
const benchmarkStatus = ref("");
const isImportModalOpen = ref(false);
const showWelcomeModal = ref(true);
const showHelpModal = ref(false);
const importMode = ref("text");
const importMatrixText = ref("");
const importError = ref("");
const importFile = ref(null);
const importImagePreviewUrl = ref("");
const importImageResult = ref(null);
const importImageExtractError = ref("");
const importImageLoading = ref(false);
const showImportLegend = ref(false);
const importPlaceholder = `Exemple :
0 0 1 1
0 2 2 1
3 2 2 1
3 3 3 1`;

const isMobile = computed(() => windowWidth.value < 600);
const currentSolutionIndex = ref(0);
const isPainting = ref(false);
const currentMouseButton = ref(null);
const selectedHistoryIndex = ref(-1);

// Brouillons (drafts)
const drafts = ref([]);
const currentDraftIndex = ref(-1);
const MAX_DRAFTS = 15;

// Dimensions de l'écran réactives
const screenWidth = ref(1200);
const screenHeight = ref(800);

// Debug: mesurer les vraies dimensions des cellules
const gridDebugInfo = ref({
    calculatedCellSize: 0,
    actualCellSize: 0,
    gridWidth: 0,
    gridHeight: 0,
    totalWidth: 0,
    totalHeight: 0,
    message: "",
});

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
        // On peut encore ajouter des couleurs, toutes sont disponibles
        return Array.from({ length: colors.length }, (_, i) => i);
    } else {
        // On a atteint la limite, seules les couleurs utilisées restent disponibles
        return Array.from(usedColorsInGrid).sort((a, b) => a - b);
    }
});

// Couleurs disponibles selon la taille de la grille et l'état actuel
const availableColors = computed(() => {
    return availableColorIndices.value.map(index => colors[index]);
});

const importLegendItems = computed(() => {
    const items = Array.from({ length: colors.length }, (_, value) => ({
        value,
        color: colors[value],
        label: `${value} = zone/couleur ${value + 1}`,
        isEmpty: false,
    }));
    items.push({
        value: -1,
        color: "#fff",
        label: "-1 = cellule vide",
        isEmpty: true,
    });
    return items;
});

const importMatrixParseResult = computed(() => {
    const lines = importMatrixText.value
        .split(/\r?\n/)
        .map((row) => row.trim())
        .filter((row) => row.length > 0);

    const previewRows = lines.map((line, rowIndex) => {
        const tokens = line.split(/[\s,;]+/).filter((token) => token.length > 0);
        return tokens.map((token) => {
            const isInteger = /^-?\d+$/.test(token);
            const value = isInteger ? Number(token) : null;
            const valid = isInteger && value >= -1;
            return {
                raw: token,
                value,
                valid,
                rowIndex,
            };
        });
    });

    const maxColumns = previewRows.reduce(
        (max, row) => Math.max(max, row.length),
        0
    );
    previewRows.forEach((row) => {
        while (row.length < maxColumns) {
            row.push({
                raw: "-1",
                value: -1,
                valid: true,
                rowIndex: row.rowIndex,
            });
        }
    });

    let error = null;
    if (lines.length === 0) {
        error = null;
    } else if (previewRows.some((row) => row.length === 0)) {
        error = "La matrice contient une ligne vide.";
    } else {
        const size = previewRows.length;
        const widths = previewRows.map((row) => row.length);
        const rowCount = previewRows.length;
        const colCount = widths[0] || 0;

        if (!widths.every((width) => width === colCount)) {
            error = "La matrice doit être carrée : le nombre de colonnes doit être égal au nombre de lignes.";
        } else if (rowCount !== colCount) {
            error = "La matrice doit être carrée : le nombre de colonnes doit être égal au nombre de lignes.";
        } else if (rowCount < 4) {
            error = "La matrice doit être d'au moins 4×4.";
        } else {
            const parsedValues = previewRows.flatMap((row) =>
                row.filter((cell) => cell.valid).map((cell) => cell.value)
            );
            const uniqueValues = [...new Set(parsedValues.filter((v) => v !== -1))];
            if (uniqueValues.length > rowCount) {
                error = "La matrice contient plus de zones distinctes que la taille de la grille.";
            } else if (uniqueValues.some((v) => v >= colors.length)) {
                error = `Les identifiants de zone doivent être inférieurs à ${colors.length}.`;
            } else if (previewRows.some((row) => row.some((cell) => !cell.valid))) {
                error = "La matrice contient des valeurs invalides. Utilisez uniquement des entiers >= -1.";
            }
        }
    }

    return {
        previewRows,
        isValid: error === null && previewRows.length > 0 && previewRows.every((row) => row.length > 0),
        error,
    };
});

const importPreviewMatrix = computed(() => importMatrixParseResult.value.previewRows);
const importImageMatrixPreview = computed(() => {
    if (!importImageResult.value?.zones) return null;
    return importImageResult.value.zones.map((row) =>
        row.map((cell) => ({
            raw: cell === -1 ? "-1" : String(cell),
            value: cell,
            valid: true,
        }))
    );
});
const activeImportPreviewMatrix = computed(() =>
    importMode.value === "text" ? importPreviewMatrix.value : importImageMatrixPreview.value
);
const importIsValid = computed(
    () =>
        importMode.value === "text"
            ? importMatrixText.value.trim().length > 0 && importMatrixParseResult.value.isValid
            : !!importImageResult.value?.zones
);
const importParseError = computed(
    () =>
        importMode.value === "text"
            ? importMatrixText.value.trim().length > 0
                ? importMatrixParseResult.value.error
                : null
            : importImageExtractError.value
);

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
    
    // Limiter le nombre de brouillons à MAX_DRAFTS
    // Si dépassement, supprimer les plus anciens
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
        // Clique gauche : peindre avec la couleur sélectionnée
        zones.value[row][col] = selectedColor.value;
    } else if (button === 2) {
        // Clique droit : effacer la case
        zones.value[row][col] = -1;
    }
    
    errorMessage.value = ""; // Vider le message d'erreur lors de modification
    positions.value = []; // Vider les positions des reines
    solutions.value = []; // Vider les solutions
    currentSolutionIndex.value = 0;
    selectedHistoryIndex.value = -1; // Désélectionner l'historique
    trmPerformance.value = null;
    baselineResult.value = null;
};

const onMouseDown = (row, col, event) => {
    event.preventDefault(); // Prévenir le menu contextuel pour clique droit
    currentMouseButton.value = event.button;
    isPainting.value = true;
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

const resetImportImageState = () => {
    if (importImagePreviewUrl.value) {
        URL.revokeObjectURL(importImagePreviewUrl.value);
    }
    importFile.value = null;
    importImagePreviewUrl.value = "";
    importImageResult.value = null;
    importImageExtractError.value = "";
    importImageLoading.value = false;
};

const openImportModal = () => {
    if (isViewingHistory.value) return; // Empêcher d'ouvrir si on visualise un historique
    isImportModalOpen.value = true;
    importMode.value = "text";
    importMatrixText.value = "";
    importError.value = "";
    showImportLegend.value = false;
    resetImportImageState();
};

const closeImportModal = () => {
    isImportModalOpen.value = false;
    importError.value = "";
    showImportLegend.value = false;
    resetImportImageState();
};

const closeWelcomeModal = () => {
    showWelcomeModal.value = false;
};

const openHelpModal = () => {
    showHelpModal.value = true;
};

const closeHelpModal = () => {
    showHelpModal.value = false;
};

const closeCurrentModal = () => {
    if (showWelcomeModal.value) {
        showWelcomeModal.value = false;
    } else if (showHelpModal.value) {
        showHelpModal.value = false;
    }
};

const selectImportMode = (mode) => {
    importMode.value = mode;
    importError.value = "";
    importImageExtractError.value = "";
    if (mode === "photo") {
        importMatrixText.value = "";
    } else {
        resetImportImageState();
    }
};

const handleImportFileChange = (event) => {
    const file = event.target.files?.[0] ?? null;
    if (!file) return;
    resetImportImageState();
    importFile.value = file;
    importImagePreviewUrl.value = URL.createObjectURL(file);
};

const uploadImportImage = async () => {
    if (!importFile.value) return;
    importImageExtractError.value = "";
    importImageLoading.value = true;
    try {
        const formData = new FormData();
        formData.append("file", importFile.value);

        const response = await axios.post(
            "http://localhost:8000/api/extract-matrix",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        importImageResult.value = response.data;
    } catch (err) {
        importImageExtractError.value =
            err?.response?.data?.detail || err.message || "Erreur lors de l'import de l'image.";
    } finally {
        importImageLoading.value = false;
    }
};

const toggleImportLegend = () => {
    showImportLegend.value = !showImportLegend.value;
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

    // Créer un canvas
    const canvas = document.createElement("canvas");
    canvas.width = canvasSize;
    canvas.height = canvasSize;
    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    // Fond blanc (incluant la marge)
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvasSize, canvasSize);

    // Dessiner les cellules
    zones.value.forEach((row, r) => {
        row.forEach((cellColor, c) => {
            const x = margin + borderWidth + c * cellSize;
            const y = margin + borderWidth + r * cellSize;

            // Remplir avec la couleur
            const color = cellColor === -1 ? "#fff" : colors[cellColor];
            ctx.fillStyle = color;
            ctx.fillRect(x, y, cellSize, cellSize);

            // Bordure de la cellule (traits noirs)
            ctx.strokeStyle = "#000";
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, cellSize, cellSize);
        });
    });

    // Bordure noire de 5px autour de la grille
    ctx.strokeStyle = "#000";
    ctx.lineWidth = borderWidth;
    ctx.strokeRect(
        margin + borderWidth / 2,
        margin + borderWidth / 2,
        gridSize * cellSize,
        gridSize * cellSize
    );

    // Télécharger l'image
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
        
        // Aussi enregistrer dans le dossier test_images/ via API
        canvas.toBlob((testBlob) => {
            const formData = new FormData();
            formData.append('file', testBlob, `test_${gridSize}x${gridSize}.png`);
            fetch('/api/save-test-image', {
                method: 'POST',
                body: formData
            }).catch(() => {
                // Silencieusement ignorer si l'endpoint n'existe pas
            });
        });
    });
};

const parseMatrixTextInput = (text) => {
    const lines = text
        .split(/\r?\n/)
        .map((row) => row.trim())
        .filter((row) => row.length > 0);

    if (lines.length === 0) {
        throw new Error("La matrice est vide.");
    }

    const matrix = lines.map((line, rowIndex) => {
        const tokens = line.split(/[\s,;]+/).filter((token) => token.length > 0);
        if (tokens.length === 0) {
            throw new Error(`La ligne ${rowIndex + 1} est vide.`);
        }

        return tokens.map((token) => {
            if (!/^[-]?\d+$/.test(token)) {
                throw new Error(`Valeur invalide : '${token}'. Utilisez uniquement des entiers.`);
            }
            const value = Number(token);
            if (value < -1) {
                throw new Error(`Les valeurs doivent être supérieures ou égales à -1. Valeur trouvée : ${value}.`);
            }
            return value;
        });
    });

    const size = matrix.length;
    if (!matrix.every((row) => row.length === size)) {
        throw new Error("La matrice doit être carrée : le nombre de colonnes doit être égal au nombre de lignes.");
    }
    if (size < 4) {
        throw new Error("La matrice doit être d'au moins 4×4.");
    }

    const allValues = matrix.flat();
    const uniqueValues = [...new Set(allValues.filter((v) => v !== -1))];
    if (uniqueValues.length > size) {
        throw new Error("La matrice contient plus de zones distinctes que la taille de la grille.");
    }

    const maxValue = uniqueValues.length > 0 ? Math.max(...uniqueValues) : -1;
    if (maxValue >= colors.length) {
        throw new Error(`Les identifiants de zone doivent être inférieurs à ${colors.length}.`);
    }

    const valueMap = new Map(uniqueValues.map((value, index) => [value, index]));
    const normalized = matrix.map((row) =>
        row.map((value) => (value === -1 ? -1 : valueMap.get(value)))
    );

    return normalized;
};

const parseMatrixTextInputPreview = (text) => {
    const lines = text
        .split(/\r?\n/)
        .map((row) => row.trim())
        .filter((row) => row.length > 0);

    if (lines.length === 0) {
        return null;
    }

    const matrix = lines.map((line) => {
        const tokens = line.split(/[\s,;]+/).filter((token) => token.length > 0);
        return tokens.map((token) => {
            if (!/^[-]?\d+$/.test(token)) {
                return null;
            }
            const value = Number(token);
            return value;
        });
    });

    const maxCols = Math.max(...matrix.map((row) => row.length));
    return matrix.map((row) => [
        ...row,
        ...Array(Math.max(0, maxCols - row.length)).fill(-1),
    ]);
};

const applyImportedMatrix = async () => {
    if (importMode.value === "photo") {
        if (!importImageResult.value?.zones) {
            importImageExtractError.value =
                "Aucune matrice extraite. Importez une photo valide avant de valider.";
            return;
        }

        const matrix = importImageResult.value.zones;
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
        return;
    }

    try {
        const matrix = parseMatrixTextInput(importMatrixText.value);
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
    } catch (err) {
        importError.value = err instanceof Error ? err.message : "Format de matrice invalide.";
    }
};

// speedup > 1 → TRM plus rapide, speedup < 1 → baseline plus rapide
// Affiché comme "TRM est X× plus rapide" ou "Baseline est X× plus rapide"
const speedup = computed(() => {
    const trmTime = trmPerformance.value?.execution_time;
    const baseTime = baselineResult.value?.performance?.execution_time;
    if (!trmTime || !baseTime || !baselineResult.value?.supported) return null;
    // ratio = baseTime / trmTime : >1 signifie TRM plus rapide
    return (baseTime / trmTime).toFixed(1);
});

const submit = async () => {
    // Créer un mapping des couleurs utilisées vers des identifiants de zones
    const usedColors = new Set(
        zones.value.flat().filter((cell) => cell !== -1)
    );
    const colorToZoneMap = new Map();
    let zoneId = 0;

    // Trier les couleurs pour un mapping déterministe
    Array.from(usedColors)
        .sort((a, b) => a - b)
        .forEach((color) => {
            colorToZoneMap.set(color, zoneId++);
        });

    // Transformer la grille en utilisant les identifiants de zones
    const zoneGrid = zones.value.map((row) =>
        row.map((cell) => (cell === -1 ? -1 : colorToZoneMap.get(cell)))
    );

    const payload = {
        size: size.value,
        zones: zoneGrid,
    };

    // Réinitialiser les données de comparaison
    trmPerformance.value = null;
    baselineResult.value = null;

    // Lancer TRM et Baseline indépendamment (ne pas attendre le baseline pour afficher)
    const trmPromise = axios.post("http://localhost:8000/api/solve", payload);
    const baselinePromise = axios.post("http://localhost:8001/api/solve", payload);

    // Afficher le résultat TRM dès qu'il arrive
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
        }
    } catch (err) {
        console.error(err);
        positions.value = [];
        solutions.value = [];
        errorMessage.value =
            "Erreur lors de la résolution. Vérifiez que le serveur backend fonctionne.";
    }

    // Mettre à jour avec le baseline quand il répond (sans bloquer l'UI)
    baselinePromise.then((baselineRes) => {
        baselineResult.value = baselineRes.data;
        const perf = baselineRes.data?.performance;
        if (historyEntry && perf) {
            historyEntry.baselineTime = perf.execution_time ?? null;
            historyEntry.baselineValid = perf.valid ?? false;
            historyEntry.baselineSolutionsCount = perf.solutions_count ?? 0;
        }
    }).catch(() => { /* baseline optionnel */ });
};

// Vérifier si la grille est complètement remplie et utilise le bon nombre de couleurs
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

const getCellStyle = (row, col) => {
    // Garde contre les grilles non initialisées
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

    // Bordure du haut - épaisse si voisin différent (case vide ou autre couleur)
    if (row > 0) {
        if (zones.value[row - 1][col] !== currentColor) {
            borderTop = "3px solid #000";
        }
    } else {
        // Première ligne - bordure épaisse car c'est le bord de la grille (déjà géré par .grid)
    }

    // Bordure de gauche - épaisse si voisin différent
    if (col > 0) {
        if (zones.value[row][col - 1] !== currentColor) {
            borderLeft = "3px solid #000";
        }
    }

    // Bordure du bas - épaisse si voisin différent
    if (row < size.value - 1) {
        if (zones.value[row + 1][col] !== currentColor) {
            borderBottom = "3px solid #000";
        }
    }

    // Bordure de droite - épaisse si voisin différent
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
    // Restaurer la grille depuis l'historique
    zones.value = entry.grid.map((row) => [...row]);
    solutions.value = entry.solutions.map((sol) => [...sol]);
    size.value = entry.size;
    positions.value = solutions.value[0] || [];
    currentSolutionIndex.value = 0;
    errorMessage.value = "";
    selectedHistoryIndex.value = index;
    isPainting.value = false; // Réinitialiser l'état de painting
    
    // Charger les times de comparaison s'ils existent (du benchmark)
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
        // Déselectionner et vider la grille
        initializeZones();
        selectedHistoryIndex.value = -1;
        solutions.value = [];
        positions.value = [];
        errorMessage.value = "";
        currentSolutionIndex.value = 0;
        trmPerformance.value = null;
        baselineResult.value = null;
    } else {
        // Charger l'historique
        loadFromHistory(entry, index);
    }
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

    // Étape 1 : placer N graines en essayant de les espacer
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
        // Fallback : n'importe quelle cellule libre
        if (!placed) {
            outer: for (let r = 0; r < size; r++)
                for (let c = 0; c < size; c++)
                    if (zones[r][c] === -1) { zones[r][c] = color; seeds.push([r, c]); placed = true; break outer; }
        }
    }

    // Étape 2 : croissance simultanée des régions (BFS aléatoire)
    // frontiers[i] = cellules de la couleur i encore capables de s'étendre
    const frontiers = seeds.map(([r, c]) => [[r, c]]);
    let remaining = size * size - size;
    let guard = size * size * 10;

    while (remaining > 0 && guard-- > 0) {
        // Ordre des couleurs aléatoire à chaque tour
        const colorOrder = shuffle(Array.from({ length: size }, (_, i) => i));
        for (const color of colorOrder) {
            if (remaining <= 0) break;
            const frontier = frontiers[color];
            if (frontier.length === 0) continue;
            // Cellule aléatoire du front
            const fi = Math.floor(Math.random() * frontier.length);
            const [r, c] = frontier[fi];
            // Direction aléatoire vers une cellule libre
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

    // Sécurité : remplir les cellules orphelines avec la couleur voisine la plus proche
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

    // Vérification finale : toutes les N couleurs présentes
    const usedColors = new Set(zones.flat());
    if (usedColors.size !== size) {
        // Fallback ultime : bandes horizontales
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
        
        // Lancer les deux modèles en parallèle
        const [trmRes, baselineRes] = await Promise.allSettled([
            axios.post("http://localhost:8000/api/solve", payload),
            axios.post("http://localhost:8001/api/solve", payload),
        ]);
        
        // Extraire les solutions du TRM
        let resultSolutions = [];
        let trm_solutions_count = 0;
        if (trmRes.status === "fulfilled") {
            resultSolutions = trmRes.value.data.solutions;
            trm_solutions_count = trmRes.value.data.performance.solutions_count;
            successCount++;
        }
        
        // Ajouter à l'historique (même si 0 solutions, pour montrer les temps)
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
        }
        
        // Petit délai pour éviter de surcharger les serveurs
        await new Promise(resolve => setTimeout(resolve, 500));
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

const windowWidth = computed(() => screenWidth.value);
const windowHeight = computed(() => screenHeight.value);

// Calculer la taille optimale des cases en fonction de l'écran disponible
const cellSize = computed(() => {
    // Espace disponible pour la grille (environ 70% de la largeur et 60% de la hauteur)
    const availableWidth = windowWidth.value * 0.7;
    const availableHeight = windowHeight.value * 0.6;

    // Calculer l'espace nécessaire pour les bordures
    // Bordure extérieure de la grille: 3px * 2 = 6px (avec box-sizing: border-box, c'est déjà inclus)
    // Bordures intermédiaires des cellules: environ (n-1) * 1px pour chaque dimension
    const borderSpace = (size.value - 1) * 1;

    // Taille maximale possible pour une case en tenant compte des bordures
    const maxCellSizeWidth = (availableWidth - borderSpace - 6) / size.value;
    const maxCellSizeHeight = (availableHeight - borderSpace - 6) / size.value;
    const maxCellSize = Math.min(maxCellSizeWidth, maxCellSizeHeight);

    // Limiter entre 20px et 60px pour une bonne lisibilité
    return Math.max(20, Math.min(60, Math.floor(maxCellSize)));
});

// Taille des icônes de reine proportionnelle à la taille des cases
const queenIconSize = computed(() =>
    Math.max(16, Math.min(40, cellSize.value - 8))
);

// Fonction pour mettre à jour les dimensions de l'écran
const updateScreenSize = () => {
    if (typeof window !== "undefined") {
        screenWidth.value = window.innerWidth;
        screenHeight.value = window.innerHeight;
    }
};

// Fonction pour mesurer les vraies dimensions des cellules du DOM
const measureGridCells = () => {
    setTimeout(() => {
        const gridEl = document.querySelector(".grid");
        if (!gridEl) return;
        
        const gridRect = gridEl.getBoundingClientRect();
        const firstCell = gridEl.querySelector(".cell");
        
        if (firstCell) {
            const cellRect = firstCell.getBoundingClientRect();
            const actualCellSize = cellRect.width;
            const diff = cellSize.value - actualCellSize;
            
            gridDebugInfo.value = {
                calculatedCellSize: cellSize.value,
                actualCellSize: Math.round(actualCellSize * 100) / 100,
                gridWidth: Math.round(gridRect.width),
                gridHeight: Math.round(gridRect.height),
                totalWidth: Math.round(gridRect.width),
                totalHeight: Math.round(gridRect.height),
                message: diff > 2 ? "WARNING: cells smaller than calculated!" : "OK",
            };
            
            console.log("Grid Debug:", gridDebugInfo.value);
        }
    }, 10);
};

// Watcher pour mesurer les cellules quand la taille change
watch(() => [size.value, cellSize.value], () => {
    measureGridCells();
});

// Lifecycle hooks pour gérer les event listeners
onMounted(() => {
    updateScreenSize();
    window.addEventListener("resize", updateScreenSize);
    // Ajouter un listener global pour mouseup pour éviter que isPainting reste bloqué
    window.addEventListener("mouseup", onMouseUp);
    window.addEventListener("mouseleave", onMouseUp);
    // Mesurer les cellules au montage
    measureGridCells();
});

onUnmounted(() => {
    window.removeEventListener("resize", updateScreenSize);
    window.removeEventListener("mouseup", onMouseUp);
    window.removeEventListener("mouseleave", onMouseUp);
});

// Masquer l'historique par défaut sur mobile
const initializeHistoryVisibility = () => {
    if (isMobile.value && historyVisible.value) {
        historyVisible.value = false;
    } else if (!isMobile.value && !historyVisible.value) {
        historyVisible.value = true;
    }
};

// Watcher pour réagir aux changements de taille d'écran
watch(isMobile, (newIsMobile) => {
    if (newIsMobile && historyVisible.value) {
        historyVisible.value = false;
    } else if (!newIsMobile && !historyVisible.value) {
        historyVisible.value = true;
    }
});

// Auto-save des brouillons
watch(zones, () => {
    if (currentDraftIndex.value >= 0) {
        saveDraft();
    }
}, { deep: true });

initializeZones();
initializeHistoryVisibility();
// Créer le premier brouillon
if (drafts.value.length === 0) {
    createNewDraft();
}
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
                class="view-tab"
                :class="{ active: currentView === 'stats' }"
                @click="currentView = 'stats'"
            >
                <i class="ri-bar-chart-grouped-line" aria-hidden="true"></i> Statistiques
            </button>
        </nav>
        <div v-if="showWelcomeModal || showHelpModal" class="modal-overlay" @click.self="closeCurrentModal">
            <div class="modal-window welcome-window">
                <h3>{{ showWelcomeModal ? 'Bienvenue dans le solveur' : 'Aide' }}</h3>
                <p class="welcome-intro">
                    Ce guide vous aide à démarrer : colorier les zones, choisir la taille,
                    utiliser les boutons, consulter l'historique et importer une grille par matrice ou photo.
                </p>
                <div class="welcome-section">
                    <h4>1. Colorier la grille</h4>
                    <p>
                        Choisissez une couleur dans la palette à droite, puis utilisez les cliques pour remplir la grille :
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li><strong>Clique gauche</strong> : peint la case avec la couleur sélectionnée</li>
                            <li><strong>Clique droit</strong> : efface la case</li>
                            <li><strong>Rester enfoncé et glisser</strong> : continue l'action sur plusieurs cases</li>
                        </ul>
                        Chaque couleur représente une zone. Le sélecteur <strong>Taille</strong> permet de définir
                        la taille de la grille avant de commencer.
                    </p>
                </div>
                <div class="welcome-section">
                    <h4>2. Historique</h4>
                    <p>
                        Chaque grille résolue est sauvegardée dans l'<strong>historique</strong> de votre session.
                        L'historique affiche le nombre de solutions trouvées et les temps d'exécution du TRM et du baseline.
                        Cliquez sur une entrée de l'historique pour visualiser les solutions d'une grille antérieure.
                    </p>
                </div>
                <div class="welcome-section">
                    <h4>3. Boutons principaux</h4>
                    <div class="welcome-buttons">
                        <div class="welcome-action">
                            <button class="guide-btn new-icon-btn" disabled>
                                <i class="ri-add-line"></i>
                            </button>
                            <div>
                                <strong>Nouvelle grille</strong><br />Crée une grille vide pour repartir à zéro.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn solve-icon-btn">
                                <i class="ri-check-line"></i>
                            </button>
                            <div>
                                <strong>Résoudre</strong><br />Lance le solveur et compare TRM / baseline.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn reset-icon-btn">
                                <i class="ri-refresh-line"></i>
                            </button>
                            <div>
                                <strong>Réinitialiser</strong><br />Vide la grille actuelle sans changer la taille.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn random-icon-btn" disabled>
                                <i class="ri-shuffle-line"></i>
                            </button>
                            <div>
                                <strong>Schéma aléatoire</strong><br />Remplit automatiquement la grille avec un motif de zones aléatoire selon la taille sélectionnée.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn benchmark-icon-btn" disabled>
                                <i class="ri-bar-chart-line"></i>
                            </button>
                            <div>
                                <strong>Benchmark aléatoire</strong><br />Lance plusieurs résolutions aléatoires pour comparer TRM et Baseline.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn import-icon-btn" disabled>
                                <i class="ri-upload-cloud-line"></i>
                            </button>
                            <div>
                                <strong>Importer</strong><br />Ouvre le panneau pour charger une matrice ou une image.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn copy-icon-btn" disabled>
                                <i class="ri-file-copy-line"></i>
                            </button>
                            <div>
                                <strong>Copier la matrice</strong><br />Copie la configuration actuelle de la grille au presse-papiers.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn download-icon-btn" disabled>
                                <i class="ri-download-line"></i>
                            </button>
                            <div>
                                <strong>Télécharger en image</strong><br />Télécharge la grille actuelle au format PNG pour la partager ou l'importer plus tard.
                            </div>
                        </div>
                        <div class="welcome-action">
                            <button class="guide-btn help-icon-btn">
                                <i class="ri-question-line"></i>
                            </button>
                            <div>
                                <strong>Afficher l'aide</strong><br />Ouvre ce guide pour consulter l'aide.
                            </div>
                        </div>
                    </div>
                </div>
                <div class="welcome-section">
                    <h4>4. Statistiques</h4>
                    <p>
                        L'onglet <strong>Statistiques</strong> affiche un graphique de performance pour la session actuelle.
                        Vous y voyez les temps moyens de TRM et de Baseline par taille de grille, présentés sur une échelle logarithmique.
                    </p>
                    <ul>
                        <li>Le graphique agrège uniquement les résolutions de la session en cours.</li>
                        <li>Les petites valeurs en microsecondes et les grandes valeurs en secondes sont affichées proportionnellement.</li>
                    </ul>
                </div>
                <div class="welcome-section">
                    <h4>5. Système d'import</h4>
                    <p>
                        Deux modes sont disponibles : <strong>Matrice</strong> et <strong>Image</strong>.
                    </p>
                    <ul>
                        <li>
                            <strong>Matrice</strong> : collez un tableau carré de nombres comme
                            <code>0 0 1 1</code> ou <code>0,1,-1,2</code>.
                            <em>-1</em> signifie case vide, les autres nombres définissent les zones.
                        </li>
                        <li>
                            <strong>Image</strong> : sélectionnez une photo de la grille.
                            Le backend analyse l'image et en extrait automatiquement la matrice de zones.
                        </li>
                    </ul>
                </div>
                <div class="welcome-section">
                    <h4>6. Brouillons</h4>
                    <p>
                        Chaque nouvelle grille crée un brouillon enregistré en bas de l'écran.
                        Vous pouvez basculer entre plusieurs brouillons comme des onglets,
                        et supprimer ceux dont vous n'avez plus besoin.
                    </p>
                    <ul>
                        <li>
                            Les brouillons sont visibles dans le panneau en bas, en tant qu'onglets.
                        </li>
                        <li>
                            La grille en cours est automatiquement sauvegardée lorsque vous changez de brouillon.
                        </li>
                        <li>
                            Il y a une limite de <strong>15 brouillons</strong> maximum,
                            les plus anciens sont supprimés au-delà de ce nombre.
                        </li>
                    </ul>
                </div>
                <div class="welcome-actions">
                    <button class="solve-btn" type="button" @click="closeCurrentModal">
                        {{ showWelcomeModal ? 'J\'ai compris, continuer' : 'Fermer l\'aide' }}
                    </button>
                </div>
            </div>
        </div>
        <BenchmarkChart v-if="currentView === 'stats'" :history="history" />
        <div v-if="currentView === 'game'" class="main-layout" :class="{ 'history-hidden': !historyVisible }">
            <div v-if="historyVisible" class="history-panel">
                <h3>Historique</h3>
                <div v-if="history.length === 0" class="no-history">
                    Aucune grille résolue
                </div>
                <div v-else class="history-list">
                    <div
                        v-for="(entry, index) in history"
                        :key="index"
                        class="history-entry"
                        :class="{ selected: selectedHistoryIndex === index }"
                        @click="toggleHistorySelection(entry, index)"
                    >
                        <div class="history-entry-header">
                            <span class="history-entry-title"
                                >{{ entry.size }}x{{ entry.size }}</span
                            >
                            <span class="history-entry-time">{{
                                entry.timestamp
                            }}</span>
                        </div>
                        <div v-if="entry.patternName" class="history-entry-pattern">
                            {{ entry.patternName }}
                        </div>
                        <div class="history-entry-solutions">
                            {{ entry.solutions.length > 0 ? `${entry.solutions.length} solution${entry.solutions.length > 1 ? "s" : ""}` : "Aucune solution" }}
                        </div>
                        <div v-if="entry.trmTime !== undefined" class="history-entry-times">
                            <span class="entry-time-trm" title="TRM">TRM: {{ formatTime(entry.trmTime) }}</span>
                            <span v-if="entry.baselineTime !== null" class="entry-time-baseline" title="Baseline">Baseline: {{ formatTime(entry.baselineTime) }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="grid-container">
                <div class="grid-header">
                    <div class="grid-toolbar">
                        <button
                            @click="clearForNewGrid"
                            class="icon-btn new-icon-btn"
                            title="Nouvelle grille"
                        >
                            <i class="ri-add-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="submit"
                            :disabled="!isGridComplete || isViewingHistory"
                            class="icon-btn solve-icon-btn"
                            title="Résoudre"
                        >
                            <i class="ri-check-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="resetGrid"
                            :disabled="!hasGridData || isViewingHistory"
                            class="icon-btn reset-icon-btn"
                            title="Réinitialiser la grille"
                        >
                            <i class="ri-refresh-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="generateRandomPattern"
                            :disabled="isViewingHistory"
                            class="icon-btn random-icon-btn"
                            title="Remplir aléatoirement la grille"
                        >
                            <i class="ri-shuffle-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="benchmarkAllSizes"
                            class="icon-btn benchmark-icon-btn"
                            :disabled="isBenchmarking"
                            title="Benchmark 1 grille/taille (4→12)"
                        >
                            <i class="ri-bar-chart-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="openImportModal"
                            class="icon-btn import-icon-btn"
                            :disabled="isViewingHistory"
                            title="Importer une image"
                        >
                            <i class="ri-upload-cloud-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="copyMatrixToClipboard"
                            class="icon-btn copy-icon-btn"
                            title="Copier la matrice"
                        >
                            <i class="ri-file-copy-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="downloadGridAsImage"
                            class="icon-btn download-icon-btn"
                            title="Télécharger la grille en image"
                        >
                            <i class="ri-download-line" aria-hidden="true"></i>
                        </button>
                        <button
                            @click="openHelpModal"
                            class="icon-btn help-icon-btn"
                            title="Afficher l'aide"
                        >
                            <i class="ri-question-line" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div v-if="benchmarkStatus" class="benchmark-status header-status">
                        {{ benchmarkStatus }}
                    </div>
                    <button
                        v-if="windowWidth < 600"
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
                >
                    <div
                        v-for="(row, r) in zones"
                        :key="r"
                        style="display: contents"
                    >
                        <div
                            v-for="(cell, c) in row"
                            :key="c"
                            class="cell"
                            :style="getCellStyle(r, c)"
                            @mousedown="onMouseDown(r, c, $event)"
                            @mouseenter="onMouseEnter(r, c)"
                            @mouseup="onMouseUp"
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
                            v-for="(sol, idx) in solutions.slice(0, 5)"
                            :key="idx"
                            @click="loadSolution(idx)"
                            class="solution-btn"
                            :class="{ active: currentSolutionIndex === idx }"
                        >
                            Solution {{ idx + 1 }}
                        </button>
                        <span v-if="solutions.length > 5" class="more-solutions"
                            >... et {{ solutions.length - 5 }} autres</span
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
                        v-for="(colorIndex, visibleIndex) in availableColorIndices"
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

        <div v-if="isImportModalOpen" class="modal-overlay" @click.self="closeImportModal">
            <div class="modal-window">
                <h3>Importer une image</h3>
                <p v-if="importMode === 'text'">
                    Collez une matrice carrée de taille minimale 4×4. Séparateurs supportés&nbsp;: espace, virgule ou point-virgule.
                </p>
                <p v-else>
                    Importez une image de grille. Le backend analysera l'image et en extraira une matrice de zones.
                </p>
                <p class="modal-note">
                    Une zone est définie par un même identifiant entier :
                    <strong>0, 1, 2, ...</strong>. Le même nombre signifie la même zone/couleur.
                    Utilisez <strong>-1</strong> pour une cellule vide.
                </p>
                <div class="import-mode-switch">
                    <button
                        type="button"
                        class="mode-btn"
                        :class="{ active: importMode === 'text' }"
                        @click="selectImportMode('text')"
                    >
                        Matrice
                    </button>
                    <button
                        type="button"
                        class="mode-btn"
                        :class="{ active: importMode === 'photo' }"
                        @click="selectImportMode('photo')"
                    >
                        Image
                    </button>
                </div>
                <div class="modal-import-content">
                    <div v-if="importMode === 'text'" class="import-textarea-panel">
                        <textarea
                            v-model="importMatrixText"
                            class="matrix-textarea"
                            :class="{ invalid: importParseError }"
                            :placeholder="importPlaceholder"
                        ></textarea>
                        <button
                            class="legend-toggle-btn"
                            type="button"
                            @click="toggleImportLegend"
                        >
                            {{ showImportLegend ? "Masquer la légende" : "Afficher la légende" }}
                        </button>
                        <div v-if="showImportLegend" class="modal-legend">
                            <div class="legend-title">Légende de la matrice</div>
                            <div
                                v-for="item in importLegendItems"
                                :key="item.value"
                                class="legend-row"
                            >
                                <span
                                    class="legend-color"
                                    :class="{ 'empty-cell': item.isEmpty }"
                                    :style="{
                                        backgroundColor: item.isEmpty ? '#fff' : item.color,
                                    }"
                                ></span>
                                <span>{{ item.label }}</span>
                            </div>
                        </div>
                    </div>
                    <div v-else class="import-image-panel">
                        <label class="file-input-label" for="photo-upload">
                            Choisissez un fichier image
                        </label>
                        <input
                            id="photo-upload"
                            type="file"
                            accept="image/png,image/jpeg,image/jpg,image/gif"
                            @change="handleImportFileChange"
                        />
                        <div class="image-input-note">
                            Formats supportés : PNG, JPG, GIF.
                        </div>
                        <button
                            class="solve-btn"
                            type="button"
                            @click="uploadImportImage"
                            :disabled="!importFile || importImageLoading"
                        >
                            {{ importImageLoading ? 'Extraction...' : 'Extraire depuis l’image' }}
                        </button>
                        <div v-if="importImagePreviewUrl" class="image-preview">
                            <img
                                :src="importImagePreviewUrl"
                                alt="Aperçu de l'image importée"
                            />
                        </div>
                        <div v-if="importImageResult" class="image-result">
                            <div>
                                <strong>Taille :</strong> {{ importImageResult.size }}×{{ importImageResult.size }}
                            </div>
                            <div>
                                <strong>Confiance :</strong> {{ (importImageResult.confidence * 100).toFixed(0) }}%
                            </div>
                        </div>
                    </div>
                    <div class="import-preview">
                        <div class="legend-title">Prévisualisation</div>
                        <div v-if="activeImportPreviewMatrix" class="import-preview-grid">
                            <div
                                v-for="(row, rowIndex) in activeImportPreviewMatrix"
                                :key="rowIndex"
                                class="import-preview-row"
                                :style="{ gridTemplateColumns: `repeat(${row.length}, minmax(18px, 1fr))` }"
                            >
                                <div
                                    v-for="(cell, colIndex) in row"
                                    :key="colIndex"
                                    class="import-preview-cell"
                                    :style="{
                                        backgroundColor:
                                            cell.value === -1 ? '#fff' : colors[cell.value],
                                        color: cell.value === -1 ? '#999' : '#000',
                                        borderColor: cell.value === -1 ? '#ccc' : '#000'
                                    }"
                                >
                                    {{ cell.raw === '' ? '-' : cell.raw }}
                                </div>
                            </div>
                        </div>
                        <div v-else class="preview-empty">
                            {{ importMode === 'text'
                                ? 'Entrez une matrice valide pour voir l’aperçu.'
                                : 'Importez une photo et extrayez la matrice pour voir l’aperçu.' }}
                        </div>
                    </div>
                </div>
                <div v-if="importError || importParseError" class="modal-error">
                    {{ importError || importParseError }}
                </div>
                <div class="modal-actions">
                    <button class="reset-btn" @click="closeImportModal">
                        Annuler
                    </button>
                    <button
                        class="solve-btn"
                        @click="applyImportedMatrix"
                        :disabled="!importIsValid"
                    >
                        Valider
                    </button>
                </div>
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
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
</style>

<style scoped>
.app {
    width: 100vw;
    height: 100vh;
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
    grid-template-columns: 0 1fr 20vw;
}

.main-layout.history-hidden {
    grid-template-columns: 0 1fr 250px;
}

.main-layout.history-hidden .history-panel {
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

    .history-panel {
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

@media (max-width: 600px) {
    .app {
        padding: 0.5vh 0.5vw;
    }

    .title {
        font-size: 1.5rem;
        margin-bottom: 1vh;
    }

    .main-layout {
        width: 100%;
        gap: 1vw;
        height: auto;
        max-height: none;
    }

    .palette {
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(6, 1fr);
        gap: 8px;
        padding: 15px;
        max-height: none;
    }

    .color-btn {
        width: 40px;
        height: 40px;
    }

    .solution-buttons {
        flex-direction: column;
        align-items: center;
    }

    .sidebar {
        flex-direction: row;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2vw;
        padding: 2vw;
    }

    .size-selector {
        flex: 0 0 auto;
        min-width: 12vw;
    }

    .palette {
        flex: 1;
        min-width: 0;
    }
}

@media (max-width: 480px) {
    .palette {
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: repeat(6, 1fr);
        gap: 6px;
        padding: 10px;
        max-height: none;
    }

    .color-btn {
        width: 35px;
        height: 35px;
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

@media (max-width: 600px) {
    .cell {
        width: 35px;
        height: 35px;
    }
}

.cell:hover {
    opacity: 0.8;
}

.queen-icon {
    fill: #000;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}

.solve-btn {
    padding: 1vh 2vw;
    font-size: 1rem;
    cursor: pointer;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s;
    margin-top: 2vh;
    font-weight: bold;
}

.solve-btn:hover:not(:disabled) {
    background-color: #45a049;
}

.solve-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
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
    width: 100vw;
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

.reset-btn {
    padding: 1vh 2vw;
    font-size: 1rem;
    cursor: pointer;
    background-color: #d32f2f;
    color: white;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s;
    margin-top: 1vh;
    margin-left: 1vw;
    font-weight: bold;
}

.reset-btn:hover {
    background-color: #b71c1c;
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


.modal-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    z-index: 999;
}

.modal-window {
    width: min(100%, 700px);
    background: white;
    border-radius: 16px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
    padding: 1.5rem;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-window h3 {
    margin-top: 0;
    margin-bottom: 0.75rem;
}

.welcome-window {
    max-width: 760px;
}

.welcome-intro {
    margin-bottom: 1rem;
    color: #444;
    font-size: 0.98rem;
}

.welcome-section {
    margin-bottom: 1.2rem;
}

.welcome-section h4 {
    margin-bottom: 0.5rem;
    font-size: 1rem;
    color: #111;
}

.welcome-section p,
.welcome-section ul {
    margin: 0;
    color: #444;
    line-height: 1.55;
    font-size: 0.95rem;
}

.welcome-section ul {
    padding-left: 1.2rem;
    margin-top: 0.7rem;
}

.welcome-section li {
    margin-bottom: 0.7rem;
}

.welcome-buttons {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
}

.welcome-action {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
    padding: 1rem;
    border: 1px solid #e3e8f0;
    border-radius: 14px;
    background: #fbfbff;
}

.guide-btn {
    width: 40px;
    height: 40px;
    min-width: 40px;
    min-height: 40px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    border: none;
    color: #111;
    cursor: default;
    opacity: 1;
}

.welcome-action .guide-btn i {
    font-size: 1.1rem;
    color: inherit;
}

.welcome-action .guide-btn.benchmark-icon-btn,
.welcome-action .guide-btn.import-icon-btn {
    color: #fff;
}

.welcome-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
}

.welcome-actions .solve-btn {
    padding: 0.95rem 1.5rem;
}

.welcome-window code {
    background: #f1f5f9;
    color: #1f2937;
    padding: 0.15rem 0.4rem;
    border-radius: 6px;
    font-size: 0.92rem;
}

@media (max-width: 800px) {
    .welcome-buttons {
        grid-template-columns: 1fr;
    }
}

.modal-window p {
    margin: 0 0 1rem 0;
    color: #444;
    line-height: 1.5;
}

.matrix-textarea {
    width: 100%;
    min-height: 180px;
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    font-size: 0.95rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    resize: vertical;
}

.matrix-textarea.invalid {
    border: 1px solid #d32f2f;
    box-shadow: 0 0 0 3px rgba(211, 47, 47, 0.18);
}

.modal-error {
    margin-top: 1rem;
    padding: 0.85rem 1rem;
    background: #ffebee;
    color: #c62828;
    border: 1px solid #f8bdbd;
    border-radius: 8px;
    font-size: 0.9rem;
}

.modal-actions {
    margin-top: 1.25rem;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.75rem;
}

.modal-actions button {
    min-width: 130px;
    margin-top: 0;
    margin-left: 0;
    flex: 1;
}

.modal-actions .solve-btn,
.modal-actions .reset-btn {
    width: auto;
}

.import-mode-switch {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.mode-btn {
    flex: 1;
    border: 1px solid #c5cfe8;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    background: #fff;
    color: #1f2937;
    cursor: pointer;
    font-weight: 700;
}

.mode-btn.active {
    background: #1976d2;
    color: #fff;
    border-color: #115293;
}

.import-image-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.file-input-label {
    font-weight: 700;
}

.image-input-note {
    font-size: 0.9rem;
    color: #555;
}

.image-preview {
    border: 1px solid #d0d8f0;
    border-radius: 12px;
    padding: 0.75rem;
    background: #fff;
}

.image-preview img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 10px;
}

.image-result {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    padding: 0.85rem 1rem;
    border: 1px solid #d5dcef;
    border-radius: 10px;
    background: #f7f9ff;
}

.legend-toggle-btn {
    background: #1976d2;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 1rem;
    cursor: pointer;
    font-weight: 700;
}

.legend-toggle-btn:hover {
    background: #115293;
}

.modal-import-content {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 1rem;
    align-items: start;
}

.import-textarea-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.import-preview {
    background: #f7f9ff;
    border: 1px solid #d0d8f0;
    border-radius: 12px;
    padding: 1rem;
    min-width: 220px;
    max-height: 400px;
    overflow: auto;
}

.import-preview-grid {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
    overflow-x: auto;
}

.import-preview-row {
    display: grid;
    gap: 0.15rem;
    width: 100%;
}

.import-preview-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    min-height: 18px;
    aspect-ratio: 1 / 1;
    padding: 0.2rem;
    font-size: 0.75rem;
    border: 1px solid #000;
    border-radius: 6px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.preview-empty {
    color: #555;
    font-size: 0.95rem;
    min-height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.modal-legend {
    padding: 1rem;
    background: #f4f7ff;
    border: 1px solid #d5dcef;
    border-radius: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
}

.modal-legend .legend-title {
    width: 100%;
    margin-bottom: 0.5rem;
}

.modal-legend .legend-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.75rem;
    background: white;
    border: 1px solid #d0d8f0;
    border-radius: 12px;
    margin-bottom: 0;
    white-space: nowrap;
}

.modal-legend .legend-color.empty-cell {
    background: #ffffff;
    border-color: #999;
}

.header-status {
    width: 100%;
    margin-top: 0.75rem;
}

.sidebar-status {
    width: 100%;
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

.legend-panel {
    width: 100%;
    margin-top: 1rem;
    padding: 1rem;
    background: #ffffff;
    border: 1px solid #dfe3e8;
    border-radius: 12px;
}

.legend-title {
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    color: #333;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #444;
}

.legend-color {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #bbb;
    display: inline-block;
}

.legend-toggle-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
    background: #f0f4ff;
    color: #1565c0;
    border: 1px solid #90caf9;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    width: 100%;
    text-align: center;
}

.legend-toggle-btn:hover {
    background: #e3f2fd;
}

.modal-legend {
    margin-bottom: 1rem;
    padding: 0.8rem 1rem;
    background: #f3f6ff;
    border-radius: 10px;
    border: 1px solid #d0d8f0;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
    color: #333;
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

.history-panel {
    background-color: #ffffff;
    padding: 0;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    max-height: calc(100vh - 6rem);
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
    align-self: start;
}

.history-panel h3 {
    margin: 0;
    padding: 20px;
    color: #111827;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 1px solid #e5e7eb;
    background-color: #f9fafb;
    border-radius: 8px 8px 0 0;
}

.no-history {
    color: #6b7280;
    font-style: italic;
    text-align: center;
    padding: 40px 20px;
    font-size: 14px;
}

.history-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.history-entry {
    padding: 16px 20px;
    background-color: white;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.history-entry:hover {
    background-color: #f3f4f6;
}

.history-entry.selected {
    background-color: #dbeafe;
    border-left: 4px solid #3b82f6;
}

.history-entry:last-child {
    border-bottom: none;
}

.history-entry-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}

.history-entry-title {
    font-weight: 600;
    color: #111827;
}

.history-entry-time {
    font-size: 12px;
    color: #9ca3af;
}

.history-entry-solutions {
    color: #6b7280;
    font-size: 13px;
}

.history-entry-pattern {
    font-size: 11px;
    color: #9ca3af;
    font-style: italic;
    margin-top: 1px;
}

.history-entry-times {
    display: flex;
    gap: 8px;
    margin-top: 3px;
}

.entry-time-trm {
    font-size: 11px;
    color: #10b981;
    font-weight: 600;
}

.entry-time-baseline {
    font-size: 11px;
    color: #f59e0b;
    font-weight: 600;
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

.reset-btn {
    padding: 0.8vh 1.5vw;
    font-size: 0.9rem;
    cursor: pointer;
    background-color: #f44336;
    color: white;
    border: none;
    border-radius: 6px;
    transition: background-color 0.3s;
    margin-top: 1vh;
}

.queens-display {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}

.queen-svg {
    width: 40px;
    height: 40px;
    fill: #000;
}
</style>
