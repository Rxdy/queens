<script setup>
defineProps({
    status: {
        type: String,
        required: true,
        validator: (v) => ["pending", "solved"].includes(v),
    },
});
</script>

<template>
    <span class="status-badge" :class="status">
        <i :class="status === 'solved' ? 'ri-check-line' : 'ri-time-line'" aria-hidden="true"></i>
        {{ status === "solved" ? "Résolu" : "À jouer" }}
    </span>
</template>

<style scoped>
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-badge.pending {
    background: #eceff1;
    color: #455a64;
}

.status-badge.solved {
    background: #e8f5e9;
    color: #2e7d32;
}
</style>
