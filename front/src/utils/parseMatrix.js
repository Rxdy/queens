export const MAX_COLORS = 12;

export const parseMatrixTextInput = (text, maxColorId = MAX_COLORS) => {
  const lines = text
    .split(/\r?\n/)
    .map((row) => row.trim())
    .filter((row) => row.length > 0);

  if (lines.length === 0) {
    throw new Error("La matrice est vide.");
  }

  const matrix = lines.map((line, rowIndex) => {
    const tokens = line.split(/[\s,;]+/).filter((token) => token.length > 0);
    if (tokens.length === 0) {
      throw new Error(`La ligne ${rowIndex + 1} est vide.`);
    }
    return tokens.map((token) => {
      if (!/^[-]?\d+$/.test(token)) {
        throw new Error(`Valeur invalide : '${token}'. Utilisez uniquement des entiers.`);
      }
      const value = Number(token);
      if (value < -1) {
        throw new Error(`Les valeurs doivent être supérieures ou égales à -1. Valeur trouvée : ${value}.`);
      }
      return value;
    });
  });

  const size = matrix.length;
  if (!matrix.every((row) => row.length === size)) {
    throw new Error("La matrice doit être carrée : le nombre de colonnes doit être égal au nombre de lignes.");
  }
  if (size < 4) {
    throw new Error("La matrice doit être d'au moins 4×4.");
  }

  const allValues = matrix.flat();
  const uniqueValues = [...new Set(allValues.filter((v) => v !== -1))];
  if (uniqueValues.length > size) {
    throw new Error("La matrice contient plus de zones distinctes que la taille de la grille.");
  }

  const maxValue = uniqueValues.length > 0 ? Math.max(...uniqueValues) : -1;
  if (maxValue >= maxColorId) {
    throw new Error(`Les identifiants de zone doivent être inférieurs à ${maxColorId}.`);
  }

  const valueMap = new Map(uniqueValues.map((value, index) => [value, index]));
  return matrix.map((row) =>
    row.map((value) => (value === -1 ? -1 : valueMap.get(value)))
  );
};
