<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { getNextResetAt, getCurrentPuzzleDay } from "../../composables/useDailyChallenge.js";

const emit = defineEmits(["reset-reached"]);

const now = ref(new Date());
let lastPuzzleDay = getCurrentPuzzleDay(now.value);
let timer = null;

const tick = () => {
    now.value = new Date();
    const today = getCurrentPuzzleDay(now.value);
    if (today !== lastPuzzleDay) {
        lastPuzzleDay = today;
        emit("reset-reached");
    }
};

onMounted(() => {
    timer = setInterval(tick, 1000);
});
onUnmounted(() => {
    clearInterval(timer);
});

const remainingLabel = computed(() => {
    const diffMs = Math.max(0, getNextResetAt(now.value).getTime() - now.value.getTime());
    const totalSeconds = Math.floor(diffMs / 1000);
    const pad = (n) => String(n).padStart(2, "0");
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    return `${pad(h)}:${pad(m)}:${pad(s)}`;
});
</script>

<template>
    <span class="countdown-badge">
        <i class="ri-time-line" aria-hidden="true"></i>
        Prochaine grille dans {{ remainingLabel }}
    </span>
</template>

<style scoped>
.countdown-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    background: #eef2ff;
    color: #3730a3;
    font-size: 0.85rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}
</style>
