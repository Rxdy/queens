// Vérifie si une grille de zones admet au moins une solution valide au jeu des
// Reines (une reine par ligne, par colonne, par zone, aucune adjacence — y
// compris diagonale — entre deux reines). Contrairement au solveur backend
// (TRM), on s'arrête dès la première solution trouvée : c'est un simple
// booléen de solvabilité, pas une énumération, donc rapide même dans le
// navigateur pour des grilles générées (zones déjà 0..size-1 contiguës).
export const hasSolution = (size, zones) => {
  if (!Number.isInteger(size) || size <= 0) return false;
  if (!Array.isArray(zones) || zones.length !== size) return false;
  if (zones.some((row) => !Array.isArray(row) || row.length !== size)) return false;

  const flat = zones.flat();
  if (flat.some((cell) => cell === -1)) return false;

  const distinctZones = [...new Set(flat)];
  if (distinctZones.length !== size) return false;

  const zoneIndex = new Map(distinctZones.map((z, i) => [z, i]));
  const colUsed = new Array(size).fill(false);
  const zoneUsed = new Array(size).fill(false);

  const place = (row, prevCol) => {
    if (row === size) return true;
    for (let c = 0; c < size; c++) {
      if (colUsed[c]) continue;
      if (prevCol !== -1 && Math.abs(c - prevCol) <= 1) continue;
      const zIdx = zoneIndex.get(zones[row][c]);
      if (zoneUsed[zIdx]) continue;

      colUsed[c] = true;
      zoneUsed[zIdx] = true;
      if (place(row + 1, c)) return true;
      colUsed[c] = false;
      zoneUsed[zIdx] = false;
    }
    return false;
  };

  return place(0, -1);
};

// Calcule l'ensemble des cases en conflit parmi des reines posées par
// l'utilisateur (même ligne, colonne, zone, ou adjacence y compris diagonale).
// Utilisé à la fois pour la surbrillance UI (PuzzleGrid) et la détection de
// victoire (useDailyChallenge), pour ne pas dupliquer la règle à deux endroits.
export const findConflictingQueens = (zones, queens) => {
  const conflicts = new Set();
  for (let i = 0; i < queens.length; i++) {
    for (let j = i + 1; j < queens.length; j++) {
      const [r1, c1] = queens[i];
      const [r2, c2] = queens[j];
      const sameRow = r1 === r2;
      const sameCol = c1 === c2;
      const sameZone = zones[r1][c1] === zones[r2][c2];
      const adjacent = Math.abs(r1 - r2) <= 1 && Math.abs(c1 - c2) <= 1;
      if (sameRow || sameCol || sameZone || adjacent) {
        conflicts.add(`${r1},${c1}`);
        conflicts.add(`${r2},${c2}`);
      }
    }
  }
  return conflicts;
};
