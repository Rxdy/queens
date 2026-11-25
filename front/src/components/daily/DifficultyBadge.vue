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

.level-0 { background: var(--color-success-bg); color: var(--color-success); }
.level-1 { background: var(--color-surface-alt); color: var(--color-primary-hover); }
.level-2 { background: var(--color-soon-bg); color: var(--color-soon); }
.level-3 { background: var(--color-danger-bg); color: var(--color-danger); }
</style>
