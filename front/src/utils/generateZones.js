// Génère N zones connexes aléatoires couvrant toutes les cellules (règle du jeu).
// Algorithme : croissance régionale depuis N graines aléatoires (flood-fill)
// → garantit que chaque zone est d'un seul tenant.
// `rng` est injectable (float dans [0, 1), même contrat que Math.random) pour
// permettre une génération déterministe (défi quotidien seedé par date).
export const generateRandomConnectedPattern = (size, rng = Math.random) => {
  const zones = Array.from({ length: size }, () => Array(size).fill(-1));
  const dirs = [[0, 1], [0, -1], [1, 0], [-1, 0]];
  const shuffle = (arr) => {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  };

  const seeds = [];
  const minSep = Math.max(1, Math.floor(size / Math.sqrt(size)));
  for (let color = 0; color < size; color++) {
    let placed = false;
    for (let attempt = 0; attempt < 400 && !placed; attempt++) {
      const r = Math.floor(rng() * size);
      const c = Math.floor(rng() * size);
      if (zones[r][c] !== -1) continue;
      const tooClose = seeds.some(([sr, sc]) => Math.abs(r - sr) + Math.abs(c - sc) < minSep);
      if (!tooClose) {
        zones[r][c] = color;
        seeds.push([r, c]);
        placed = true;
      }
    }
    if (!placed) {
      outer: for (let r = 0; r < size; r++)
        for (let c = 0; c < size; c++)
          if (zones[r][c] === -1) { zones[r][c] = color; seeds.push([r, c]); placed = true; break outer; }
    }
  }

  const frontiers = seeds.map(([r, c]) => [[r, c]]);
  let remaining = size * size - size;
  let guard = size * size * 10;

  while (remaining > 0 && guard-- > 0) {
    const colorOrder = shuffle(Array.from({ length: size }, (_, i) => i));
    for (const color of colorOrder) {
      if (remaining <= 0) break;
      const frontier = frontiers[color];
      if (frontier.length === 0) continue;
      const fi = Math.floor(rng() * frontier.length);
      const [r, c] = frontier[fi];
      const sdirs = shuffle([...dirs]);
      let expanded = false;
      for (const [dr, dc] of sdirs) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < size && nc >= 0 && nc < size && zones[nr][nc] === -1) {
          zones[nr][nc] = color;
          frontier.push([nr, nc]);
          remaining--;
          expanded = true;
          break;
        }
      }
      if (!expanded) frontier.splice(fi, 1);
    }
  }

  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (zones[r][c] !== -1) continue;
      let best = 0, bestDist = Infinity;
      for (let rr = 0; rr < size; rr++)
        for (let cc = 0; cc < size; cc++)
          if (zones[rr][cc] !== -1) {
            const d = Math.abs(r - rr) + Math.abs(c - cc);
            if (d < bestDist) { bestDist = d; best = zones[rr][cc]; }
          }
      zones[r][c] = best;
    }
  }

  const usedColors = new Set(zones.flat());
  if (usedColors.size !== size) {
    for (let r = 0; r < size; r++)
      for (let c = 0; c < size; c++)
        zones[r][c] = r;
  }

  return zones;
};
