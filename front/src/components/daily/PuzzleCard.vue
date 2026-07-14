<script setup>
import MiniGridPreview from "./MiniGridPreview.vue";
import DifficultyBadge from "./DifficultyBadge.vue";
import PuzzleStatusBadge from "./PuzzleStatusBadge.vue";
import { formatDuration } from "../../utils/format.js";

defineProps({
    puzzle: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(["play"]);
</script>

<template>
    <button type="button" class="puzzle-card" @click="emit('play', puzzle.id)">
        <MiniGridPreview :zones="puzzle.zones" :size="puzzle.size" />
        <div class="puzzle-card-footer">
            <span class="puzzle-card-size">{{ puzzle.size }}×{{ puzzle.size }}</span>
            <DifficultyBadge :size="puzzle.size" />
        </div>
        <PuzzleStatusBadge :status="puzzle.status" />
        <span v-if="puzzle.status === 'solved'" class="puzzle-card-time">
            Votre temps : {{ formatDuration(puzzle.solveTimeMs) }}
        </span>
        <span class="puzzle-card-cta">
            {{ puzzle.status === "solved" ? "Rejouer" : "Jouer" }}
            <i class="ri-arrow-right-line" aria-hidden="true"></i>
        </span>
    </button>
</template>

<style scoped>
.puzzle-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 14px;
    background: #fff;
    border: none;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: box-shadow 0.15s ease, transform 0.15s ease;
    font-family: inherit;
}

.puzzle-card:hover {
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.16);
    transform: translateY(-2px);
}

.puzzle-card-footer {
    display: flex;
    align-items: center;
    gap: 8px;
}

.puzzle-card-size {
    font-weight: 700;
    color: #333;
}

.puzzle-card-cta {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #3730a3;
}

.puzzle-card-time {
    font-size: 0.78rem;
    color: #666;
}
</style>
