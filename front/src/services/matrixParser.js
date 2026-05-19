export function parseMatrix(input) {
  if (!input || input.trim() === "") {
    throw new Error("La matrice est vide");
  }

  const rows = input.trim().split("\n");

  const matrix = rows.map((row, rowIndex) => {
    const values = row
      .trim()
      .split(/[\s,]+/)
      .filter((v) => v !== "")
      .map((v) => {
        const num = Number(v);
        if (isNaN(num)) {
          throw new Error(`Valeur invalide à la ligne ${rowIndex + 1}: "${v}"`);
        }
        return num;
      });

    return values;
  });

  const colCount = matrix[0].length;
  for (let i = 0; i < matrix.length; i++) {
    if (matrix[i].length !== colCount) {
      throw new Error(
        "Toutes les lignes doivent avoir le même nombre de colonnes",
      );
    }
  }

  return {
    matrix,
    rows: matrix.length,
    cols: colCount,
  };
}
``;
