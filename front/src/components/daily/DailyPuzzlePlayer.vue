<script setup>
import PuzzleGrid from "./PuzzleGrid.vue";
import DifficultyBadge from "./DifficultyBadge.vue";
import PuzzleStatusBadge from "./PuzzleStatusBadge.vue";
import ElapsedTimer from "./ElapsedTimer.vue";
import { formatDuration } from "../../utils/format.js";

defineProps({
    puzzle: {
        type: Object,
        required: true,
    },
    // { count, best_time_ms } | undefined — stats globales (anonymes,
    // partagées entre joueurs) pour cette taille de grille aujourd'hui.
    globalStats: {
        type: Object,
        default: null,
    },
});

const emit = defineEmits(["toggle-cell", "toggle-mark", "back"]);
</script>

<template>
    <div class="daily-player">
        <div class="daily-player-header">
            <button type="button" class="back-btn" @click="emit('back')">
                <i class="ri-arrow-left-line" aria-hidden="true"></i> Défis
            </button>
            <span class="daily-player-size">{{ puzzle.size }}×{{ puzzle.size }}</span>
            <DifficultyBadge :size="puzzle.size" />
            <PuzzleStatusBadge :status="puzzle.status" />
            <ElapsedTimer v-if="puzzle.status !== 'solved'" :started-at="puzzle.startedAt" />
        </div>

        <p v-if="puzzle.status === 'solved'" class="solved-banner">
            <i class="ri-trophy-line" aria-hidden="true"></i> Résolu en <strong>{{ formatDuration(puzzle.solveTimeMs) }}</strong> !
            Vous pouvez continuer à explorer la grille ou revenir aux défis.
        </p>
        <p v-else class="interaction-hint">
            Clic gauche : poser une reine — clic droit (ou appui long) : poser une croix pour éliminer une case.
        </p>

        <p v-if="globalStats && globalStats.count > 0" class="global-daily-stats">
            <i class="ri-group-line" aria-hidden="true"></i>
            {{ globalStats.count }} joueur{{ globalStats.count > 1 ? "s" : "" }} {{ globalStats.count > 1 ? "ont" : "a" }} résolu cette grille aujourd'hui
            — meilleur temps : <strong>{{ formatDuration(globalStats.best_time_ms) }}</strong>
        </p>

        <PuzzleGrid
            :size="puzzle.size"
            :zones="puzzle.zones"
            :queens="puzzle.userQueens"
            :marks="puzzle.userMarks"
            @toggle-cell="emit('toggle-cell', $event)"
            @toggle-mark="emit('toggle-mark', $event)"
        />
    </div>
</template>

<style scoped>
.daily-player {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    width: 100%;
    padding: 1vh 1vw;
    box-sizing: border-box;
}

.daily-player-header {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    max-width: 480px;
}

.daily-player-size {
    font-weight: 700;
    color: #333;
    margin-left: auto;
}

.back-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border: none;
    border-radius: 8px;
    background: #eceff1;
    color: #333;
    font-weight: 600;
    cursor: pointer;
}

.back-btn:hover {
    background: #dde3e6;
}

.solved-banner {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0;
    padding: 8px 14px;
    background: #e8f5e9;
    color: #2e7d32;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
}

.interaction-hint {
    margin: 0;
    color: #777;
    font-size: 0.8rem;
    text-align: center;
}

.global-daily-stats {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0;
    padding: 6px 14px;
    background: #eef2ff;
    color: #3730a3;
    border-radius: 8px;
    font-size: 0.82rem;
}
</style>
