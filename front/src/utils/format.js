const stripTrailingZeros = (value) => String(value).replace(/\.0+$/, "");

export const formatMs = (ms) => {
  if (ms === null || ms === undefined) return "—";
  if (ms < 0.001) return `${(ms * 1_000_000).toFixed(0)} ns`;
  if (ms < 1)     return `${(ms * 1000).toFixed(0)} µs`;
  if (ms < 1000)  return `${stripTrailingZeros(ms.toFixed(1))} ms`;
  return `${stripTrailingZeros((ms / 1000).toFixed(2))} s`;
};
