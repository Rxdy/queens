<script setup>
import { computed } from "vue";
import { DAILY_SIZES } from "../../composables/useDailyChallenge.js";

const props = defineProps({
    size: {
        type: Number,
        required: true,
    },
});

const LABELS = ["Facile", "Moyen", "Difficile", "Expert"];

const label = computed(() => {
    const idx = DAILY_SIZES.indexOf(props.size);
    return idx >= 0 && idx < LABELS.length ? LABELS[idx] : `${props.size}×${props.size}`;
});
</script>

<template>
    <span class="difficulty-badge" :class="`level-${DAILY_SIZES.indexOf(size)}`">
        {{ label }}
    </span>
</template>

<style scoped>
.difficulty-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}

.level-0 { background: #e8f5e9; color: #2e7d32; }
.level-1 { background: #e8f0ff; color: #1e3a8a; }
.level-2 { background: #fff3e0; color: #e65100; }
.level-3 { background: #ffebee; color: #c62828; }
</style>
