<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { formatMs } from "../utils/format.js";

const props = defineProps({
    trmBase: {
        type: String,
        required: true,
    },
});

const stats = ref(null);
const isLoading = ref(true);
const errorMessage = ref("");

const sortedSizes = () =>
    Object.entries(stats.value.by_size).sort(([a], [b]) => Number(a) - Number(b));

const formatSeconds = (seconds) => formatMs(seconds === null || seconds === undefined ? null : seconds * 1000);

const formatDate = (isoString) => {
    if (!isoString) return "—";
    return new Date(isoString).toLocaleString("fr-FR", {
        dateStyle: "medium",
        timeStyle: "short",
    });
};

onMounted(async () => {
    try {
        const { data } = await axios.get(`${props.trmBase}/api/stats`);
        stats.value = data;
    } catch {
        errorMessage.value = "Statistiques globales indisponibles pour le moment.";
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <div class="global-stats-panel">
        <h3>Statistiques globales</h3>

        <p v-if="isLoading" class="global-stats-status">Chargement…</p>
        <p v-else-if="errorMessage" class="global-stats-status">{{ errorMessage }}</p>

        <template v-else-if="stats && stats.total_solves > 0">
            <p class="global-stats-summary">
                <strong>{{ stats.total_solves }}</strong> grille{{ stats.total_solves > 1 ? "s" : "" }} résolue{{ stats.total_solves > 1 ? "s" : "" }}
                depuis le {{ formatDate(stats.since) }}
                — temps moyen <strong>{{ formatSeconds(stats.overall.avg_execution_time) }}</strong>.
            </p>
            <div class="global-stats-table-wrapper">
                <table class="global-stats-table">
                    <thead>
                        <tr>
                            <th>Taille</th>
                            <th>Résolutions</th>
                            <th>Temps moyen</th>
                            <th>Min</th>
                            <th>Max</th>
                            <th>Solutions moy.</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="[size, bucket] in sortedSizes()" :key="size">
                            <td>{{ size }}×{{ size }}</td>
                            <td>{{ bucket.count }}</td>
                            <td>{{ formatSeconds(bucket.avg_execution_time) }}</td>
                            <td>{{ formatSeconds(bucket.min_execution_time) }}</td>
                            <td>{{ formatSeconds(bucket.max_execution_time) }}</td>
                            <td>{{ bucket.avg_solutions_count.toFixed(1) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>

        <p v-else class="global-stats-status">Aucune résolution enregistrée pour le moment.</p>
    </div>
</template>

<style scoped>
.global-stats-panel {
    width: 100%;
    max-width: 900px;
    margin: 0 auto 2vh;
    padding: 1rem 1.2rem;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    box-sizing: border-box;
}

.global-stats-panel h3 {
    margin: 0 0 0.6rem;
    color: #333;
}

.global-stats-status {
    color: #666;
    font-size: 0.9rem;
    margin: 0;
}

.global-stats-summary {
    margin: 0 0 1rem;
    color: #444;
    font-size: 0.92rem;
}

.global-stats-table-wrapper {
    overflow-x: auto;
}

.global-stats-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}

.global-stats-table th,
.global-stats-table td {
    padding: 6px 10px;
    text-align: right;
    border-bottom: 1px solid #eee;
}

.global-stats-table th:first-child,
.global-stats-table td:first-child {
    text-align: left;
}

.global-stats-table th {
    color: #666;
    font-weight: 600;
}
</style>
