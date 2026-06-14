<script setup>
import { computed, ref } from "vue";
import { formatMs } from "./utils/format.js";

const props = defineProps({
  history: { type: Array, default: () => [] },
});

const avg = (arr) => arr.reduce((s, v) => s + v, 0) / arr.length;

const chartData = computed(() => {
  const bySize = {};
  for (const entry of props.history) {
    const s = entry.size;
    if (!bySize[s]) bySize[s] = { trm: [], baseline: [] };
    if (entry.trmTime != null)      bySize[s].trm.push(entry.trmTime * 1000);
    if (entry.baselineTime != null) bySize[s].baseline.push(entry.baselineTime * 1000);
  }
  return Object.entries(bySize)
    .sort(([a], [b]) => +a - +b)
    .map(([size, { trm, baseline }]) => {
      const trmAvg      = trm.length      ? avg(trm)      : null;
      const baselineAvg = baseline.length ? avg(baseline) : null;
      const speedup     = (trmAvg && baselineAvg)
                            ? (baselineAvg / trmAvg).toFixed(2) : null;
      return { size: +size, trm: trmAvg, baseline: baselineAvg,
               trmCount: trm.length, baselineCount: baseline.length, speedup };
    });
});

const hasData = computed(() => chartData.value.length > 0);

const ML = 72, MR = 24, MT = 28, MB = 52, W = 640, H = 340;
const PW = W - ML - MR, PH = H - MT - MB;

// ─── Échelle logarithmique ───────────────────────────────────────────────────
const LOG_FLOOR = 0.001; // 1 µs en ms

const yMin = computed(() => {
  if (!hasData.value) return LOG_FLOOR;
  const vals = chartData.value.flatMap((d) => [d.trm, d.baseline].filter((v) => v != null && v > 0));
  return vals.length ? Math.max(LOG_FLOOR, Math.min(...vals) * 0.5) : LOG_FLOOR;
});

const yMax = computed(() => {
  if (!hasData.value) return 1;
  const vals = chartData.value.flatMap((d) => [d.trm, d.baseline].filter((v) => v != null));
  return Math.max(...vals) * 2.5;
});

// Ticks aux puissances de 10 comprises dans la plage
const yTicks = computed(() => {
  const logMin = Math.log10(yMin.value);
  const logMax = Math.log10(yMax.value);
  const ticks = [];
  for (let exp = Math.floor(logMin); exp <= Math.ceil(logMax); exp++) {
    const val = Math.pow(10, exp);
    if (val >= yMin.value * 0.8 && val <= yMax.value * 1.1) ticks.push(val);
  }
  return ticks;
});

const yScale = (v) => {
  if (!v || v <= 0) return PH;
  const logMin = Math.log10(yMin.value);
  const logMax = Math.log10(yMax.value);
  const logV   = Math.log10(Math.max(v, yMin.value));
  return PH - ((logV - logMin) / (logMax - logMin)) * PH;
};

const groupCount = computed(() => chartData.value.length || 1);
const groupW     = computed(() => PW / groupCount.value);
const barW       = computed(() => Math.min(groupW.value * 0.3, 30));
const gap        = computed(() => barW.value * 0.25);
const groupX     = (i) => i * groupW.value + groupW.value / 2;

const tooltip = ref({ visible: false, x: 0, y: 0, lines: [] });

const showTooltip = (event, d, kind) => {
  const rect  = event.currentTarget.closest("svg").getBoundingClientRect();
  const time  = kind === "trm" ? d.trm  : d.baseline;
  const count = kind === "trm" ? d.trmCount : d.baselineCount;
  const label = kind === "trm" ? "TRM" : "Baseline";
  const lines = [
    `${label}  —  ${d.size}×${d.size}`,
    `Temps moyen : ${formatMs(time)}`,
    `Mesures : ${count}`,
  ];
  if (d.speedup !== null) lines.push(`Speedup TRM/Base : ×${d.speedup}`);
  tooltip.value = { visible: true, x: event.clientX - rect.left, y: event.clientY - rect.top, lines };
};

const moveTooltip = (event) => {
  if (!tooltip.value.visible) return;
  const svg = event.currentTarget.querySelector("svg");
  if (!svg) return;
  const rect = svg.getBoundingClientRect();
  tooltip.value.x = event.clientX - rect.left;
  tooltip.value.y = event.clientY - rect.top;
};

const hideTooltip = () => { tooltip.value.visible = false; };
</script>

<template>
  <div class="chart-wrapper">
    <h2 class="chart-title">Temps de résolution moyen — session</h2>

    <div class="chart-legend">
      <span class="legend-item"><span class="legend-dot trm-dot"></span>TRM</span>
      <span class="legend-item"><span class="legend-dot baseline-dot"></span>Baseline</span>
      <span class="legend-count">{{ props.history.length }} résolution{{ props.history.length > 1 ? 's' : '' }}</span>
    </div>

    <div v-if="!hasData" class="no-data">
      Aucune donnée — lancez le benchmark
      <span class="kbd"><i class="ri-bar-chart-line"></i></span>
      pour remplir ce graphique.
    </div>

    <div v-else class="svg-container" @mousemove="moveTooltip">
      <svg :viewBox="`0 0 ${W} ${H}`" class="chart-svg" preserveAspectRatio="xMidYMid meet">
        <line v-for="tick in yTicks" :key="'g'+tick" :x1="ML" :y1="MT+yScale(tick)" :x2="ML+PW" :y2="MT+yScale(tick)" class="grid-line"/>
        <text v-for="tick in yTicks" :key="'y'+tick" :x="ML-8" :y="MT+yScale(tick)+4" class="axis-label y-label">{{ formatMs(tick) }}</text>
        <text :x="14" :y="MT+PH/2" class="axis-title" :transform="`rotate(-90,14,${MT+PH/2})`">Temps moyen (log)</text>
        <text v-for="(d,i) in chartData" :key="'x'+d.size" :x="ML+groupX(i)" :y="MT+PH+22" class="axis-label x-label">{{ d.size }}×{{ d.size }}</text>
        <text :x="ML+PW/2" :y="H-4" class="axis-title">Taille de grille</text>

        <g v-for="(d,i) in chartData" :key="'b'+d.size">
          <rect v-if="d.trm!==null" :x="ML+groupX(i)-gap/2-barW" :y="MT+yScale(d.trm)" :width="barW" :height="PH-yScale(d.trm)" class="bar trm-bar" rx="3" @mouseenter="(e)=>showTooltip(e,d,'trm')" @mouseleave="hideTooltip"/>
          <rect v-if="d.baseline!==null" :x="ML+groupX(i)+gap/2" :y="MT+yScale(d.baseline)" :width="barW" :height="PH-yScale(d.baseline)" class="bar baseline-bar" rx="3" @mouseenter="(e)=>showTooltip(e,d,'baseline')" @mouseleave="hideTooltip"/>
          <text v-if="d.trm!==null&&PH-yScale(d.trm)>16" :x="ML+groupX(i)-gap/2-barW/2" :y="MT+yScale(d.trm)-5" class="bar-value">{{ formatMs(d.trm) }}</text>
          <text v-if="d.baseline!==null&&PH-yScale(d.baseline)>16" :x="ML+groupX(i)+gap/2+barW/2" :y="MT+yScale(d.baseline)-5" class="bar-value">{{ formatMs(d.baseline) }}</text>
          <text v-if="d.speedup!==null" :x="ML+groupX(i)" :y="MT+Math.min(yScale(d.trm??0),yScale(d.baseline??0))-16" class="speedup-label">×{{ d.speedup }}</text>
        </g>

        <line :x1="ML" :y1="MT" :x2="ML" :y2="MT+PH" class="axis-line"/>
        <line :x1="ML" :y1="MT+PH" :x2="ML+PW" :y2="MT+PH" class="axis-line"/>

        <g v-if="tooltip.visible">
          <rect :x="tooltip.x+10" :y="tooltip.y-14" :width="tooltip.lines.reduce((m,l)=>Math.max(m,l.length*6.6),0)+20" :height="tooltip.lines.length*18+10" class="tooltip-bg" rx="5"/>
          <text v-for="(line,li) in tooltip.lines" :key="li" :x="tooltip.x+20" :y="tooltip.y+4+li*18" class="tooltip-text" :class="{'tooltip-header':li===0}">{{ line }}</text>
        </g>
      </svg>
    </div>

    <p class="chart-note">
      Moyennes calculées sur toutes les résolutions de la session.
      Relancez le benchmark <span class="kbd"><i class="ri-bar-chart-line"></i></span> pour accumuler des données.
    </p>
  </div>
</template>

<style scoped>
.chart-wrapper { width:100%; max-width:880px; margin:0 auto; padding:24px 16px 16px; display:flex; flex-direction:column; align-items:center; gap:12px; }
.chart-title { font-size:1.15rem; font-weight:700; color:#333; margin:0; text-align:center; }
.chart-legend { display:flex; align-items:center; gap:20px; font-size:0.88rem; color:#444; }
.legend-item { display:flex; align-items:center; gap:7px; }
.legend-dot { width:14px; height:14px; border-radius:3px; display:inline-block; }
.trm-dot { background:#5b9cf6; }
.baseline-dot { background:#f4a55a; }
.legend-count { font-size:0.78rem; color:#999; margin-left:8px; }
.svg-container { width:100%; position:relative; cursor:crosshair; }
.chart-svg { width:100%; height:auto; display:block; }
.grid-line { stroke:#e0e0e0; stroke-width:1; stroke-dasharray:4 3; }
.axis-line { stroke:#555; stroke-width:1.5; }
.axis-label { font-size:11px; fill:#555; }
.y-label { text-anchor:end; }
.x-label { text-anchor:middle; font-size:12px; font-weight:600; fill:#333; }
.axis-title { font-size:11px; fill:#777; text-anchor:middle; }
.bar { cursor:pointer; transition:opacity 0.15s; }
.bar:hover { opacity:0.75; }
.trm-bar { fill:#5b9cf6; }
.baseline-bar { fill:#f4a55a; }
.bar-value { font-size:9px; fill:#444; text-anchor:middle; pointer-events:none; }
.speedup-label { font-size:9.5px; fill:#2e7d32; font-weight:700; text-anchor:middle; pointer-events:none; }
.tooltip-bg { fill:rgba(28,28,28,0.9); filter:drop-shadow(0 2px 6px rgba(0,0,0,0.3)); }
.tooltip-text { fill:#f0f0f0; font-size:11.5px; pointer-events:none; }
.tooltip-header { font-weight:700; fill:#fff; font-size:12px; }
.no-data { color:#888; font-size:0.9rem; text-align:center; padding:40px 20px; border:2px dashed #ccc; border-radius:10px; width:100%; }
.kbd { display:inline-flex; align-items:center; background:#eee; border-radius:4px; padding:1px 5px; font-size:0.85em; color:#333; }
.chart-note { font-size:0.78rem; color:#999; text-align:center; margin:0; max-width:600px; }
</style>
