<script setup>
defineProps({
    history: {
        type: Array,
        required: true,
    },
    visible: {
        type: Boolean,
        required: true,
    },
    selectedIndex: {
        type: Number,
        required: true,
    },
});

const emit = defineEmits(["restore", "clear"]);

const formatTime = (seconds) => {
    if (seconds === null || seconds === undefined) return "—";
    if (seconds < 0.001) return `${(seconds * 1_000_000).toFixed(0)} µs`;
    if (seconds < 1) return `${(seconds * 1000).toFixed(3)} ms`;
    return `${seconds.toFixed(3)} s`;
};
</script>

<template>
    <div v-if="visible" class="history-panel">
        <h3>Historique</h3>
        <div v-if="history.length === 0" class="no-history">
            Aucune grille résolue
        </div>
        <div v-else class="history-list">
            <div
                v-for="(entry, index) in history"
                :key="index"
                class="history-entry"
                :class="{ selected: selectedIndex === index }"
                @click="emit('restore', { entry, index })"
            >
                <div class="history-entry-header">
                    <span class="history-entry-title">{{ entry.size }}x{{ entry.size }}</span>
                    <span class="history-entry-time">{{ entry.timestamp }}</span>
                </div>
                <div v-if="entry.patternName" class="history-entry-pattern">
                    {{ entry.patternName }}
                </div>
                <div class="history-entry-solutions">
                    {{ entry.solutions.length > 0 ? `${entry.solutions.length} solution${entry.solutions.length > 1 ? "s" : ""}` : "Aucune solution" }}
                </div>
                <div v-if="entry.trmTime !== undefined" class="history-entry-times">
                    <span class="entry-time-trm" title="TRM">TRM: {{ formatTime(entry.trmTime) }}</span>
                    <span v-if="entry.baselineTime !== null" class="entry-time-baseline" title="Baseline">Baseline: {{ formatTime(entry.baselineTime) }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.history-panel {
    background-color: #ffffff;
    padding: 0;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    max-height: calc(100vh - 6rem);
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
    align-self: start;
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

.history-entry-pattern {
    font-size: 11px;
    color: #9ca3af;
    font-style: italic;
    margin-top: 1px;
}

.history-entry-times {
    display: flex;
    gap: 8px;
    margin-top: 3px;
}

.entry-time-trm {
    font-size: 11px;
    color: #10b981;
    font-weight: 600;
}

.entry-time-baseline {
    font-size: 11px;
    color: #f59e0b;
    font-weight: 600;
}
</style>
