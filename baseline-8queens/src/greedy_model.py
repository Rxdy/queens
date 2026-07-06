"""
Modèle baseline — backtracking naïf exhaustif pour le problème des N-Reines.
"""


class QueensGreedyBaseline:
    """
    Solveur de référence : backtracking exhaustif sans optimisations.
    Intentionnellement naïf pour servir de baseline de comparaison avec le TRM.
    """

    def solve_exhaustive(self, n: int, zones: list, max_iterations: int = 10**18) -> tuple:
        """
        Backtracking naïf exhaustif : compte TOUTES les solutions sans les stocker en RAM.
        Seule la première solution est gardée pour l'affichage.

        Contraintes :
        - Une seule reine par colonne (used_cols)
        - Une seule reine par zone (used_zones)
        - Adjacence O(n) : boucle sur toutes les lignes précédentes
        """
        placement = [-1] * n
        used_cols = [False] * n
        used_zones = set()
        solution_count = [0]
        first_solution = [None]

        def backtrack(row: int):
            if row == n:
                solution_count[0] += 1
                if first_solution[0] is None:
                    first_solution[0] = [[i, placement[i]] for i in range(n)]
                return
            for col in range(n):
                if used_cols[col]:
                    continue
                zone = (
                    zones[row][col] if zones and row < len(zones) and col < len(zones[row]) else -1
                )
                if zone != -1 and zone in used_zones:
                    continue
                # Contrainte d'adjacence naïve : vérifie toutes les lignes précédentes (O(n))
                valid = True
                for prev_row in range(row):
                    if placement[prev_row] == -1:
                        continue
                    if max(abs(placement[prev_row] - col), abs(prev_row - row)) <= 1:
                        valid = False
                        break
                if not valid:
                    continue
                placement[row] = col
                used_cols[col] = True
                zone_added = zone != -1
                if zone_added:
                    used_zones.add(zone)
                backtrack(row + 1)
                placement[row] = -1
                used_cols[col] = False
                if zone_added:
                    used_zones.discard(zone)

        backtrack(0)
        sol = first_solution[0] if first_solution[0] is not None else []
        return sol, solution_count[0]
