<script setup>
import PuzzleCard from "./PuzzleCard.vue";
import CountdownBadge from "./CountdownBadge.vue";

defineProps({
    puzzles: {
        type: Array,
        required: true,
    },
});

const emit = defineEmits(["select", "reset-reached"]);
</script>

<template>
    <div class="daily-picker">
        <div class="daily-picker-header">
            <h2>Grille du jour</h2>
            <CountdownBadge @reset-reached="emit('reset-reached')" />
        </div>
        <p class="daily-picker-subtitle">
            4 grilles à résoudre en posant les reines vous-même — une seule par ligne, colonne et zone, sans jamais se toucher.
        </p>
        <div class="daily-picker-grid">
            <PuzzleCard
                v-for="puzzle in puzzles"
                :key="puzzle.id"
                :puzzle="puzzle"
                @play="emit('select', $event)"
            />
        </div>
    </div>
</template>

<style scoped>
.daily-picker {
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    padding: 1vh 1vw;
    box-sizing: border-box;
}

.daily-picker-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.daily-picker-header h2 {
    margin: 0;
    color: #333;
}

.daily-picker-subtitle {
    margin: 8px 0 20px;
    color: #666;
    font-size: 0.9rem;
}

.daily-picker-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
}
</style>
