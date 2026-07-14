<script setup>
import { computed } from "vue";
import { colors } from "../../utils/colors.js";
import { findConflictingQueens } from "../../utils/queensSolver.js";
import QueenIcon from "../QueenIcon.vue";

const props = defineProps({
    size: {
        type: Number,
        required: true,
    },
    zones: {
        type: Array,
        required: true,
    },
    // [[row, col], ...] — l'état des reines posées est possédé par le parent
    // (composant contrôlé, aucun state interne dupliqué). La détection de
    // victoire elle-même vit dans useDailyChallenge.toggleQueen (synchrone
    // avec la mutation), pas ici — voir le commentaire à cet endroit.
    queens: {
        type: Array,
        required: true,
    },
    // [[row, col], ...] — croix posées par l'utilisateur pour éliminer des
    // cases par réflexion ; simple annotation, sans effet sur la victoire.
    marks: {
        type: Array,
        default: () => [],
    },
});

const emit = defineEmits(["toggle-cell", "toggle-mark"]);

const key = (r, c) => `${r},${c}`;

const queenSet = computed(() => new Set(props.queens.map(([r, c]) => key(r, c))));
const markSet = computed(() => new Set(props.marks.map(([r, c]) => key(r, c))));

// Surbrillance uniquement (même règle que useDailyChallenge.toggleQueen, via
// le même utilitaire partagé pour ne pas dupliquer la logique de conflit).
const conflictCells = computed(() => findConflictingQueens(props.zones, props.queens));

const queenSize = computed(() => Math.round(Math.max(16, Math.min(32, 260 / props.size))));

// Clic gauche = reine, clic droit = croix (élimination par réflexion).
const onCellClick = (row, col) => emit("toggle-cell", { row, col });
const onCellRightClick = (row, col) => emit("toggle-mark", { row, col });
</script>

<template>
    <div class="puzzle-grid" :style="{ gridTemplateColumns: `repeat(${size}, 1fr)` }">
        <template v-for="(row, r) in zones" :key="r">
            <button
                v-for="(cell, c) in row"
                :key="c"
                type="button"
                class="puzzle-cell"
                :class="{ conflict: conflictCells.has(key(r, c)) }"
                :style="{ backgroundColor: colors[cell] }"
                :aria-label="`Ligne ${r + 1}, colonne ${c + 1}`"
                @click="onCellClick(r, c)"
                @contextmenu.prevent="onCellRightClick(r, c)"
            >
                <QueenIcon v-if="queenSet.has(key(r, c))" :size="queenSize" />
                <span v-else-if="markSet.has(key(r, c))" class="mark-x" :style="{ fontSize: queenSize + 'px' }">✕</span>
            </button>
        </template>
    </div>
</template>

<style scoped>
.puzzle-grid {
    display: grid;
    gap: 2px;
    width: min(90vw, 480px);
    aspect-ratio: 1;
    background: #000;
    border: 3px solid #000;
    border-radius: 4px;
    box-sizing: border-box;
    overflow: hidden;
}

.puzzle-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    aspect-ratio: 1;
    border: none;
    padding: 0;
    cursor: pointer;
    transition: outline 0.1s ease;
}

.puzzle-cell:hover {
    opacity: 0.85;
}

.puzzle-cell.conflict {
    outline: 3px solid #e53935;
    outline-offset: -3px;
    z-index: 1;
}

.mark-x {
    color: rgba(0, 0, 0, 0.45);
    font-weight: 700;
    line-height: 1;
    user-select: none;
}
</style>
