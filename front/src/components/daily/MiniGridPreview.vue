<script setup>
import { colors } from "../../utils/colors.js";

defineProps({
    zones: {
        type: Array,
        required: true,
    },
    size: {
        type: Number,
        required: true,
    },
});
</script>

<template>
    <div class="mini-grid" :style="{ gridTemplateColumns: `repeat(${size}, 1fr)` }">
        <template v-for="(row, r) in zones" :key="r">
            <div
                v-for="(cell, c) in row"
                :key="c"
                class="mini-cell"
                :style="{ backgroundColor: colors[cell] }"
            ></div>
        </template>
    </div>
</template>

<style scoped>
.mini-grid {
    display: grid;
    gap: 1px;
    width: 100%;
    aspect-ratio: 1;
    background: #222;
    border: 2px solid #222;
    border-radius: 4px;
    overflow: hidden;
}

.mini-cell {
    aspect-ratio: 1;
}
</style>
