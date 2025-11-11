<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import axios from "axios";

const size = ref(8);
const zones = ref([]);
const positions = ref([]);
const solutions = ref([]);
const selectedColor = ref(0);
const errorMessage = ref("");
const history = ref([]);
const historyVisible = ref(true);

const isMobile = computed(() => windowWidth.value < 600);
const currentSolutionIndex = ref(0);
const isPainting = ref(false);
const selectedHistoryIndex = ref(-1);

// Dimensions de l'écran réactives
const screenWidth = ref(1200);
const screenHeight = ref(800);
const colors = [
    "rgb(223, 160, 191)",
    "rgb(150, 190, 255)",
    "rgb(255, 201, 146)",
    "rgb(187, 163, 226)",
    "rgb(240, 240, 240)", // Gris très clair pour la couleur par défaut
    "rgb(139, 69, 19)", // Marron pour remplacer le beige
    "rgb(255, 123, 96)",
    "rgb(230, 243, 136)",
    "rgb(179, 223, 160)",
    "rgb(85, 235, 226)",
    "rgb(149, 203, 207)",
    "rgb(210, 180, 200)",
];

// Couleurs disponibles selon la taille de la grille et l'état actuel
const availableColors = computed(() => {
    if (!zones.value) return [];

    const usedColorsInGrid = new Set(
        zones.value.flat().filter((cell) => cell !== -1)
    );
    const maxColors = size.value;

    if (usedColorsInGrid.size < maxColors) {
        // On peut encore ajouter des couleurs, toutes sont disponibles
        return colors;
    } else {
        // On a atteint la limite, seules les couleurs utilisées restent disponibles
        return colors.filter((_, index) => usedColorsInGrid.has(index));
    }
});

const initializeZones = () => {
    zones.value = Array.from({ length: size.value }, () =>
        Array(size.value).fill(-1)
    ); // -1 pour cases vides
    positions.value = [];
    errorMessage.value = ""; // Vider le message d'erreur
    // Réinitialiser la couleur sélectionnée si elle dépasse la limite
    if (selectedColor.value >= size.value) {
        selectedColor.value = 0;
    }
};

const clickCell = (row, col) => {
    if (zones.value[row][col] === selectedColor.value) {
        zones.value[row][col] = -1; // Remettre à vide
    } else {
        zones.value[row][col] = selectedColor.value;
    }
    errorMessage.value = ""; // Vider le message d'erreur lors de modification
    positions.value = []; // Vider les positions des reines
    solutions.value = []; // Vider les solutions
    currentSolutionIndex.value = 0;
    selectedHistoryIndex.value = -1; // Désélectionner l'historique
};

const onMouseDown = (row, col) => {
    isPainting.value = true;
    clickCell(row, col);
};

const onMouseEnter = (row, col) => {
    if (isPainting.value) {
        clickCell(row, col);
    }
};

const onMouseUp = () => {
    isPainting.value = false;
};

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

    try {
        const response = await axios.post(
            "http://localhost:8000/api/solve",
            payload
        );
        solutions.value = response.data.solutions;

        if (solutions.value.length === 0) {
            errorMessage.value =
                "Aucune solution trouvée pour cette configuration de zones. Essayez de modifier la disposition des couleurs.";
            positions.value = [];
        } else {
            errorMessage.value = "";
            currentSolutionIndex.value = 0;
            positions.value = solutions.value[0]; // Charger la première solution par défaut
            // Ajouter à l'historique
            history.value.unshift({
                grid: zones.value.map((row) => [...row]), // Copie profonde
                solutions: solutions.value.map((sol) => [...sol]), // Copie
                timestamp: new Date().toLocaleString("fr-FR"),
                size: size.value,
            });
        }
    } catch (error) {
        console.error(error);
        positions.value = [];
        solutions.value = [];
        errorMessage.value =
            "Erreur lors de la résolution. Vérifiez que le serveur backend fonctionne.";
    }
};

// Vérifier si la grille est complètement remplie et utilise le bon nombre de couleurs
const isGridComplete = computed(() => {
    if (!zones.value) return false;

    const allCellsFilled = zones.value.flat().every((cell) => cell !== -1);
    const usedColorsCount = new Set(
        zones.value.flat().filter((cell) => cell !== -1)
    ).size;
    const requiredColors = size.value;

    return allCellsFilled && usedColorsCount === requiredColors;
});

const getCellStyle = (row, col) => {
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

// Lifecycle hooks pour gérer les event listeners
onMounted(() => {
    updateScreenSize();
    window.addEventListener("resize", updateScreenSize);
    // Ajouter un listener global pour mouseup pour éviter que isPainting reste bloqué
    window.addEventListener("mouseup", onMouseUp);
    window.addEventListener("mouseleave", onMouseUp);
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

initializeZones();
initializeHistoryVisibility();
</script>

<template>
    <div class="app">
        <h1 class="title">Queens Game Solveur</h1>
        <div class="main-layout" :class="{ 'history-hidden': !historyVisible }">
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
                        @click="loadFromHistory(entry, index)"
                    >
                        <div class="history-entry-header">
                            <span class="history-entry-title"
                                >{{ entry.size }}x{{ entry.size }}</span
                            >
                            <span class="history-entry-time">{{
                                entry.timestamp
                            }}</span>
                        </div>
                        <div class="history-entry-solutions">
                            {{ entry.solutions.length }} solution{{
                                entry.solutions.length > 1 ? "s" : ""
                            }}
                        </div>
                    </div>
                </div>
            </div>
            <div class="grid-container">
                <div class="grid-header">
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
                        width: `${cellSize * size}px`,
                        height: `${cellSize * size}px`,
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
                            @mousedown="onMouseDown(r, c)"
                            @mouseenter="onMouseEnter(r, c)"
                            @mouseup="onMouseUp"
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
                <button
                    @click="submit"
                    class="solve-btn"
                    :disabled="!isGridComplete"
                >
                    Résoudre
                </button>
                <button @click="resetGrid" class="reset-btn">
                    Réinitialiser la grille
                </button>
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
                        v-for="(color, index) in availableColors"
                        :key="index"
                        class="color-btn"
                        :class="{ selected: selectedColor === index }"
                        :style="{ backgroundColor: color }"
                        @click="selectedColor = index"
                    ></div>
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
body {
    width: 100vw;
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
    padding: 1vh 1vw;
    background-color: #f5f5f5;
    overflow: hidden;
}

.title {
    text-align: center;
    margin-bottom: 2vh;
    color: #333;
    font-size: 2rem;
    font-weight: bold;
}

.main-layout {
    display: grid;
    grid-template-columns: 20vw 1fr 18vw;
    justify-content: center;
    align-items: flex-start;
    gap: 2vw;
    width: 98vw;
    height: 75vh;
    max-width: 1400px;
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
        width: 99vw;
        gap: 1vw;
        height: 90vh;
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
    overflow: hidden;
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
    grid-template-rows: repeat(6, 1fr);
    gap: 12px;
    width: 100%;
    padding: 20px;
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

.history-panel {
    background-color: #ffffff;
    padding: 0;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #e5e7eb;
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
