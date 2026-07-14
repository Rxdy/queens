<script setup>
import PuzzleGrid from "./PuzzleGrid.vue";
import DifficultyBadge from "./DifficultyBadge.vue";
import PuzzleStatusBadge from "./PuzzleStatusBadge.vue";

defineProps({
    puzzle: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["toggle-cell", "back"]);
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
        </div>

        <p v-if="puzzle.status === 'solved'" class="solved-banner">
            <i class="ri-trophy-line" aria-hidden="true"></i> Résolu ! Vous pouvez continuer à explorer la grille ou revenir aux défis.
        </p>

        <PuzzleGrid
            :size="puzzle.size"
            :zones="puzzle.zones"
            :queens="puzzle.userQueens"
            @toggle-cell="emit('toggle-cell', $event)"
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
</style>
