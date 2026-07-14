<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { formatDuration } from "../../utils/format.js";

const props = defineProps({
    // Timestamp (Date.now()) du démarrage du chrono, ou null si pas encore démarré.
    startedAt: {
        type: Number,
        default: null,
    },
});

const now = ref(Date.now());
let timer = null;

onMounted(() => {
    timer = setInterval(() => {
        now.value = Date.now();
    }, 1000);
});

onUnmounted(() => {
    clearInterval(timer);
});

const elapsedMs = computed(() => (props.startedAt === null ? null : now.value - props.startedAt));
</script>

<template>
    <span class="elapsed-timer">
        <i class="ri-timer-line" aria-hidden="true"></i>
        {{ formatDuration(elapsedMs) }}
    </span>
</template>

<style scoped>
.elapsed-timer {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    color: #555;
}
</style>
