<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useDailyChallenge } from "../../composables/useDailyChallenge.js";
import DailyChallengePicker from "./DailyChallengePicker.vue";
import DailyPuzzlePlayer from "./DailyPuzzlePlayer.vue";

const { puzzles, ensureTodaysPuzzles, selectPuzzle, toggleQueen } = useDailyChallenge();

const selectedPuzzleId = ref(null);
const selectedPuzzle = computed(() =>
    selectedPuzzleId.value ? selectPuzzle(selectedPuzzleId.value) : null
);

const onSelect = (id) => {
    selectedPuzzleId.value = id;
};

const onBack = () => {
    selectedPuzzleId.value = null;
};

const onToggleCell = ({ row, col }) => {
    if (!selectedPuzzleId.value) return;
    toggleQueen(selectedPuzzleId.value, row, col);
};

// Si le jour change pendant que l'onglet reste ouvert (ex: laissé ouvert la
// nuit), on revérifie au retour de focus et on ramène au picker pour éviter
// de jouer sur une grille de la veille dont l'id pourrait ne plus exister.
const handleVisibility = () => {
    if (document.visibilityState === "visible") {
        ensureTodaysPuzzles();
    }
};

const onResetReached = () => {
    ensureTodaysPuzzles();
    selectedPuzzleId.value = null;
};

onMounted(() => {
    ensureTodaysPuzzles();
    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("focus", ensureTodaysPuzzles);
});

onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibility);
    window.removeEventListener("focus", ensureTodaysPuzzles);
});
</script>

<template>
    <div class="daily-challenge-panel">
        <DailyPuzzlePlayer
            v-if="selectedPuzzle"
            :puzzle="selectedPuzzle"
            @toggle-cell="onToggleCell"
            @back="onBack"
        />
        <DailyChallengePicker
            v-else
            :puzzles="puzzles"
            @select="onSelect"
            @reset-reached="onResetReached"
        />
    </div>
</template>

<style scoped>
.daily-challenge-panel {
    width: 100%;
    flex: 1;
    min-height: 0;
    overflow-y: auto;
}
</style>
