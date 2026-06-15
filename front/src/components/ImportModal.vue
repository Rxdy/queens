<script setup>
import { ref, computed } from "vue";
import axios from "axios";
import { parseMatrixTextInput } from "../utils/parseMatrix.js";

const props = defineProps({
    colors: {
        type: Array,
        required: true,
    },
    visible: {
        type: Boolean,
        required: true,
    },
    trmBase: {
        type: String,
        required: true,
    },
});

const emit = defineEmits(["apply", "close"]);

const importMode = ref("text");
const importMatrixText = ref("");
const importError = ref("");
const importFile = ref(null);
const importImagePreviewUrl = ref("");
const importImageResult = ref(null);
const importImageExtractError = ref("");
const importImageLoading = ref(false);
const showImportLegend = ref(false);

const importPlaceholder = `Exemple :
0 0 1 1
0 2 2 1
3 2 2 1
3 3 3 1`;

const importLegendItems = computed(() => {
    const items = Array.from({ length: props.colors.length }, (_, value) => ({
        value,
        color: props.colors[value],
        label: `${value} = zone/couleur ${value + 1}`,
        isEmpty: false,
    }));
    items.push({
        value: -1,
        color: "#fff",
        label: "-1 = cellule vide",
        isEmpty: true,
    });
    return items;
});

const importMatrixParseResult = computed(() => {
    const lines = importMatrixText.value
        .split(/\r?\n/)
        .map((row) => row.trim())
        .filter((row) => row.length > 0);

    const previewRows = lines.map((line, rowIndex) => {
        const tokens = line.split(/[\s,;]+/).filter((token) => token.length > 0);
        return tokens.map((token) => {
            const isInteger = /^-?\d+$/.test(token);
            const value = isInteger ? Number(token) : null;
            const valid = isInteger && value >= -1;
            return {
                raw: token,
                value,
                valid,
                rowIndex,
            };
        });
    });

    const maxColumns = previewRows.reduce(
        (max, row) => Math.max(max, row.length),
        0
    );
    previewRows.forEach((row) => {
        while (row.length < maxColumns) {
            row.push({
                raw: "-1",
                value: -1,
                valid: true,
                rowIndex: row.rowIndex,
            });
        }
    });

    let error = null;
    if (lines.length === 0) {
        error = null;
    } else if (previewRows.some((row) => row.length === 0)) {
        error = "La matrice contient une ligne vide.";
    } else {
        const widths = previewRows.map((row) => row.length);
        const rowCount = previewRows.length;
        const colCount = widths[0] || 0;

        if (!widths.every((width) => width === colCount)) {
            error = "La matrice doit être carrée : le nombre de colonnes doit être égal au nombre de lignes.";
        } else if (rowCount !== colCount) {
            error = "La matrice doit être carrée : le nombre de colonnes doit être égal au nombre de lignes.";
        } else if (rowCount < 4) {
            error = "La matrice doit être d'au moins 4×4.";
        } else {
            const parsedValues = previewRows.flatMap((row) =>
                row.filter((cell) => cell.valid).map((cell) => cell.value)
            );
            const uniqueValues = [...new Set(parsedValues.filter((v) => v !== -1))];
            if (uniqueValues.length > rowCount) {
                error = "La matrice contient plus de zones distinctes que la taille de la grille.";
            } else if (uniqueValues.some((v) => v >= props.colors.length)) {
                error = `Les identifiants de zone doivent être inférieurs à ${props.colors.length}.`;
            } else if (previewRows.some((row) => row.some((cell) => !cell.valid))) {
                error = "La matrice contient des valeurs invalides. Utilisez uniquement des entiers >= -1.";
            }
        }
    }

    return {
        previewRows,
        isValid: error === null && previewRows.length > 0 && previewRows.every((row) => row.length > 0),
        error,
    };
});

const importPreviewMatrix = computed(() => importMatrixParseResult.value.previewRows);
const importImageMatrixPreview = computed(() => {
    if (!importImageResult.value?.zones) return null;
    return importImageResult.value.zones.map((row) =>
        row.map((cell) => ({
            raw: cell === -1 ? "-1" : String(cell),
            value: cell,
            valid: true,
        }))
    );
});
const activeImportPreviewMatrix = computed(() =>
    importMode.value === "text" ? importPreviewMatrix.value : importImageMatrixPreview.value
);
const importIsValid = computed(
    () =>
        importMode.value === "text"
            ? importMatrixText.value.trim().length > 0 && importMatrixParseResult.value.isValid
            : !!importImageResult.value?.zones
);
const importParseError = computed(
    () =>
        importMode.value === "text"
            ? importMatrixText.value.trim().length > 0
                ? importMatrixParseResult.value.error
                : null
            : importImageExtractError.value
);

const resetImportImageState = () => {
    if (importImagePreviewUrl.value) {
        URL.revokeObjectURL(importImagePreviewUrl.value);
    }
    importFile.value = null;
    importImagePreviewUrl.value = "";
    importImageResult.value = null;
    importImageExtractError.value = "";
    importImageLoading.value = false;
};

const selectImportMode = (mode) => {
    importMode.value = mode;
    importError.value = "";
    importImageExtractError.value = "";
    if (mode === "photo") {
        importMatrixText.value = "";
    } else {
        resetImportImageState();
    }
};

const handleImportFileChange = (event) => {
    const file = event.target.files?.[0] ?? null;
    if (!file) return;
    resetImportImageState();
    importFile.value = file;
    importImagePreviewUrl.value = URL.createObjectURL(file);
};

const uploadImportImage = async () => {
    if (!importFile.value) return;
    importImageExtractError.value = "";
    importImageLoading.value = true;
    try {
        const formData = new FormData();
        formData.append("file", importFile.value);

        const response = await axios.post(
            `${props.trmBase}/api/extract-matrix`,
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        importImageResult.value = response.data;
    } catch (err) {
        importImageExtractError.value =
            err?.response?.data?.detail || err.message || "Erreur lors de l'import de l'image.";
    } finally {
        importImageLoading.value = false;
    }
};

const toggleImportLegend = () => {
    showImportLegend.value = !showImportLegend.value;
};

const handleClose = () => {
    importError.value = "";
    showImportLegend.value = false;
    resetImportImageState();
    emit("close");
};

const applyImportedMatrix = async () => {
    if (importMode.value === "photo") {
        if (!importImageResult.value?.zones) {
            importImageExtractError.value =
                "Aucune matrice extraite. Importez une photo valide avant de valider.";
            return;
        }
        emit("apply", importImageResult.value.zones);
        handleClose();
        return;
    }

    try {
        const matrix = parseMatrixTextInput(importMatrixText.value, props.colors.length);
        emit("apply", matrix);
        handleClose();
    } catch (err) {
        importError.value = err instanceof Error ? err.message : "Format de matrice invalide.";
    }
};

const open = () => {
    importMode.value = "text";
    importMatrixText.value = "";
    importError.value = "";
    showImportLegend.value = false;
    resetImportImageState();
};

defineExpose({ open });
</script>

<template>
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="modal-window">
            <h3>Importer une image</h3>
            <p v-if="importMode === 'text'">
                Collez une matrice carrée de taille minimale 4×4. Séparateurs supportés&nbsp;: espace, virgule ou point-virgule.
            </p>
            <p v-else>
                Importez une image de grille. Le backend analysera l'image et en extraira une matrice de zones.
            </p>
            <p class="modal-note">
                Une zone est définie par un même identifiant entier :
                <strong>0, 1, 2, ...</strong>. Le même nombre signifie la même zone/couleur.
                Utilisez <strong>-1</strong> pour une cellule vide.
            </p>
            <div class="import-mode-switch">
                <button
                    type="button"
                    class="mode-btn"
                    :class="{ active: importMode === 'text' }"
                    @click="selectImportMode('text')"
                >
                    Matrice
                </button>
                <button
                    type="button"
                    class="mode-btn"
                    :class="{ active: importMode === 'photo' }"
                    @click="selectImportMode('photo')"
                >
                    Image
                </button>
            </div>
            <div class="modal-import-content">
                <div v-if="importMode === 'text'" class="import-textarea-panel">
                    <textarea
                        v-model="importMatrixText"
                        class="matrix-textarea"
                        :class="{ invalid: importParseError }"
                        :placeholder="importPlaceholder"
                    ></textarea>
                    <button
                        class="legend-toggle-btn"
                        type="button"
                        @click="toggleImportLegend"
                    >
                        {{ showImportLegend ? "Masquer la légende" : "Afficher la légende" }}
                    </button>
                    <div v-if="showImportLegend" class="modal-legend">
                        <div class="legend-title">Légende de la matrice</div>
                        <div
                            v-for="item in importLegendItems"
                            :key="item.value"
                            class="legend-row"
                        >
                            <span
                                class="legend-color"
                                :class="{ 'empty-cell': item.isEmpty }"
                                :style="{
                                    backgroundColor: item.isEmpty ? '#fff' : item.color,
                                }"
                            ></span>
                            <span>{{ item.label }}</span>
                        </div>
                    </div>
                </div>
                <div v-else class="import-image-panel">
                    <label class="file-input-label" for="photo-upload">
                        Choisissez un fichier image
                    </label>
                    <input
                        id="photo-upload"
                        type="file"
                        accept="image/png,image/jpeg,image/jpg,image/gif"
                        @change="handleImportFileChange"
                    />
                    <div class="image-input-note">
                        Formats supportés : PNG, JPG, GIF.
                    </div>
                    <button
                        class="solve-btn"
                        type="button"
                        @click="uploadImportImage"
                        :disabled="!importFile || importImageLoading"
                    >
                        {{ importImageLoading ? 'Extraction...' : 'Extraire depuis l'image' }}
                    </button>
                    <div v-if="importImagePreviewUrl" class="image-preview">
                        <img
                            :src="importImagePreviewUrl"
                            alt="Aperçu de l'image importée"
                        />
                    </div>
                    <div v-if="importImageResult" class="image-result">
                        <div>
                            <strong>Taille :</strong> {{ importImageResult.size }}×{{ importImageResult.size }}
                        </div>
                        <div>
                            <strong>Confiance :</strong> {{ (importImageResult.confidence * 100).toFixed(0) }}%
                        </div>
                    </div>
                </div>
                <div class="import-preview">
                    <div class="legend-title">Prévisualisation</div>
                    <div v-if="activeImportPreviewMatrix" class="import-preview-grid">
                        <div
                            v-for="(row, rowIndex) in activeImportPreviewMatrix"
                            :key="rowIndex"
                            class="import-preview-row"
                            :style="{ gridTemplateColumns: `repeat(${row.length}, minmax(18px, 1fr))` }"
                        >
                            <div
                                v-for="(cell, colIndex) in row"
                                :key="colIndex"
                                class="import-preview-cell"
                                :style="{
                                    backgroundColor:
                                        cell.value === -1 ? '#fff' : colors[cell.value],
                                    color: cell.value === -1 ? '#999' : '#000',
                                    borderColor: cell.value === -1 ? '#ccc' : '#000'
                                }"
                            >
                                {{ cell.raw === '' ? '-' : cell.raw }}
                            </div>
                        </div>
                    </div>
                    <div v-else class="preview-empty">
                        {{ importMode === 'text'
                            ? 'Entrez une matrice valide pour voir l'aperçu.'
                            : 'Importez une photo et extrayez la matrice pour voir l'aperçu.' }}
                    </div>
                </div>
            </div>
            <div v-if="importError || importParseError" class="modal-error">
                {{ importError || importParseError }}
            </div>
            <div class="modal-actions">
                <button class="reset-btn" @click="handleClose">
                    Annuler
                </button>
                <button
                    class="solve-btn"
                    @click="applyImportedMatrix"
                    :disabled="!importIsValid"
                >
                    Valider
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    z-index: 999;
}

.modal-window {
    width: min(100%, 700px);
    background: white;
    border-radius: 16px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
    padding: 1.5rem;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-window h3 {
    margin-top: 0;
    margin-bottom: 0.75rem;
}

.modal-window p {
    margin: 0 0 1rem 0;
    color: #444;
    line-height: 1.5;
}

.matrix-textarea {
    width: 100%;
    min-height: 180px;
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    font-size: 0.95rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    resize: vertical;
}

.matrix-textarea.invalid {
    border: 1px solid #d32f2f;
    box-shadow: 0 0 0 3px rgba(211, 47, 47, 0.18);
}

.modal-error {
    margin-top: 1rem;
    padding: 0.85rem 1rem;
    background: #ffebee;
    color: #c62828;
    border: 1px solid #f8bdbd;
    border-radius: 8px;
    font-size: 0.9rem;
}

.modal-actions {
    margin-top: 1.25rem;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.75rem;
}

.modal-actions button {
    min-width: 130px;
    margin-top: 0;
    margin-left: 0;
    flex: 1;
}

.modal-actions .solve-btn,
.modal-actions .reset-btn {
    width: auto;
}

.import-mode-switch {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.mode-btn {
    flex: 1;
    border: 1px solid #c5cfe8;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    background: #fff;
    color: #1f2937;
    cursor: pointer;
    font-weight: 700;
}

.mode-btn.active {
    background: #1976d2;
    color: #fff;
    border-color: #115293;
}

.import-image-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.file-input-label {
    font-weight: 700;
}

.image-input-note {
    font-size: 0.9rem;
    color: #555;
}

.image-preview {
    border: 1px solid #d0d8f0;
    border-radius: 12px;
    padding: 0.75rem;
    background: #fff;
}

.image-preview img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 10px;
}

.image-result {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    padding: 0.85rem 1rem;
    border: 1px solid #d5dcef;
    border-radius: 10px;
    background: #f7f9ff;
}

.legend-toggle-btn {
    background: #1976d2;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 1rem;
    cursor: pointer;
    font-weight: 700;
}

.legend-toggle-btn:hover {
    background: #115293;
}

.modal-import-content {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 1rem;
    align-items: start;
}

.import-textarea-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.import-preview {
    background: #f7f9ff;
    border: 1px solid #d0d8f0;
    border-radius: 12px;
    padding: 1rem;
    min-width: 220px;
    max-height: 400px;
    overflow: auto;
}

.import-preview-grid {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
    overflow-x: auto;
}

.import-preview-row {
    display: grid;
    gap: 0.15rem;
    width: 100%;
}

.import-preview-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    min-height: 18px;
    aspect-ratio: 1 / 1;
    padding: 0.2rem;
    font-size: 0.75rem;
    border: 1px solid #000;
    border-radius: 6px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.preview-empty {
    color: #555;
    font-size: 0.95rem;
    min-height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.modal-legend {
    padding: 1rem;
    background: #f4f7ff;
    border: 1px solid #d5dcef;
    border-radius: 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
}

.modal-legend .legend-title {
    width: 100%;
    margin-bottom: 0.5rem;
}

.modal-legend .legend-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.75rem;
    background: white;
    border: 1px solid #d0d8f0;
    border-radius: 12px;
    margin-bottom: 0;
    white-space: nowrap;
}

.modal-legend .legend-color.empty-cell {
    background: #ffffff;
    border-color: #999;
}

.legend-title {
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
    color: #333;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
    color: #333;
}

.legend-color {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #bbb;
    display: inline-block;
}

.solve-btn {
    padding: 1vh 2vw;
    font-size: 1rem;
    cursor: pointer;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s;
    margin-top: 2vh;
    font-weight: bold;
}

.solve-btn:hover:not(:disabled) {
    background-color: #45a049;
}

.solve-btn:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.reset-btn {
    padding: 1vh 2vw;
    font-size: 1rem;
    cursor: pointer;
    background-color: #d32f2f;
    color: white;
    border: none;
    border-radius: 8px;
    transition: background-color 0.3s;
    margin-top: 1vh;
    margin-left: 1vw;
    font-weight: bold;
}

.reset-btn:hover {
    background-color: #b71c1c;
}
</style>
