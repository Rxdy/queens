"""
Processeur d'images pour extraire les matrices de grille
"""

import logging
from io import BytesIO

import numpy as np
from PIL import Image

logger = logging.getLogger("image_processor")

# Les couleurs du frontend (RGB)
GRID_COLORS = [
    (223, 160, 191),  # 0 - Rose
    (150, 190, 255),  # 1 - Bleu clair
    (255, 201, 146),  # 2 - Orange
    (187, 163, 226),  # 3 - Violet
    (240, 240, 240),  # 4 - Gris très clair
    (139, 69, 19),  # 5 - Marron
    (255, 123, 96),  # 6 - Rouge/Orange
    (230, 243, 136),  # 7 - Jaune clair
    (179, 223, 160),  # 8 - Vert clair
    (85, 235, 226),  # 9 - Cyan
    (149, 203, 207),  # 10 - Bleu-vert
    (210, 180, 200),  # 11 - Mauve
]

# Couleur pour les cellules vides (blanc avec bordure noire)
WHITE_COLOR = (255, 255, 255)
EMPTY_VALUE = -1


def color_distance(color1, color2):
    """Calcule la distance Euclidienne entre deux couleurs RGB"""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def get_cell_color(cell_region):
    """
    Retourne la couleur représentative d'une cellule.
    On utilise la zone intérieure et la couleur médiane pour éviter les bords noirs.
    """
    if cell_region.size == 0:
        return None

    height, width = cell_region.shape[:2]
    margin = max(4, min(height, width) // 8)
    inner = cell_region[margin : height - margin, margin : width - margin]
    if inner.size == 0:
        inner = cell_region

    # Utiliser la médiane pour réduire l'influence des lignes de grille
    return np.median(inner.reshape(-1, 3), axis=0).astype(int)


def find_closest_zone_color(rgb_color):
    """
    Trouve la couleur de zone la plus proche d'une couleur donnée.
    Retourne l'index de la zone (0-11) ou -1 si c'est du blanc (vide) ou couleur trop indéterminée.

    Stratégie : Accepte les correspondances proches (distance < seuil) sans forcer
    une correspondance si la distance est trop grande.
    """
    # Seuil adaptatif : tolérance pour variations dues à compression/affichage
    # Cette valeur a été augmentée pour accepter des images avec des variations de couleur
    DISTANCE_THRESHOLD = 150

    r, g, b = rgb_color

    # D'abord, trouver la zone la plus proche
    min_distance = float("inf")
    closest_zone = 0

    for zone_idx, zone_color in enumerate(GRID_COLORS):
        dist = color_distance(rgb_color, zone_color)
        if dist < min_distance:
            min_distance = dist
            closest_zone = zone_idx

    # Vérifier si c'est vraiment blanc (et pas juste une zone gris clair)
    # Blanc pur = (255, 255, 255), on considère comme vide si TRÈS proche et NOT matching une zone
    is_white_like = abs(r - 255) < 30 and abs(g - 255) < 30 and abs(b - 255) < 30

    # Si c'est blanc ET la distance à la couleur gris clair (zone 4) est grande, c'est vide
    if is_white_like and min_distance > 20:
        return EMPTY_VALUE

    # Logique spéciale pour gris pur: si R ≈ G ≈ B, préférer zone 4 (gris clair)
    # Zone 4 = (240, 240, 240)
    if abs(r - g) < 20 and abs(g - b) < 20 and abs(r - b) < 20:
        gray_value = (r + g + b) // 3
        # Si c'est un gris (170-240), retourner zone 4
        if 170 <= gray_value <= 240:
            return 4

    # Appliquer le seuil : si aucune zone n'est assez proche, retourner vide
    # Cela évite les correspondances forcées vers une mauvaise zone
    if min_distance > DISTANCE_THRESHOLD:
        logger.debug(
            f"Couleur indéterminée RGB{rgb_color}: distance min={min_distance:.1f} > seuil={DISTANCE_THRESHOLD}"
        )
        return EMPTY_VALUE

    return closest_zone


def extract_matrix_from_image(image_data: bytes, expected_size: int = None):
    """
    Extrait une matrice de grille d'une image de manière robuste.

    Stratégie:
    1. Détecte la taille de grille
    2. Extrait les cellules avec correspondance aux couleurs frontend
    3. VALIDE: nombre de couleurs distinctes == taille de grille
    4. Si validation échoue, AMÉLIORE avec clustering intelligent

    Args:
        image_data: Les données binaires de l'image (PNG, JPG, etc.)
        expected_size: Taille attendue de la grille (n x n). Si None, détecte automatiquement.

    Returns:
        Dict avec:
        - size: Taille de la grille détectée
        - zones: Matrice de zones extraite
        - confidence: Score de confiance (0-1)
    """
    try:
        # Ouvrir l'image
        image = Image.open(BytesIO(image_data)).convert("RGB")
        image_array = np.array(image)

        logger.info(f"Image reçue: {image_array.shape}")

        # Déterminer la taille de la grille en analysant les bordures noires
        grid_size = detect_grid_size(image_array)

        if grid_size is None:
            raise ValueError("Impossible de détecter la grille dans l'image")

        if expected_size and grid_size != expected_size:
            logger.warning(f"Taille détectée ({grid_size}) != attendue ({expected_size})")

        logger.info(f"Grille détectée: {grid_size}x{grid_size}")

        # Extraire les cellules avec correspondance palette (1er essai rapide)
        zones = extract_grid_cells(image_array, grid_size)

        # VALIDER: vérifier que le nombre de zones DISTINCTES = taille de grille
        distinct_zones = len(set(z for row in zones for z in row if z != EMPTY_VALUE))
        empty_count = sum(1 for row in zones for z in row if z == EMPTY_VALUE)
        logger.info(
            f"Zones distinctes: {distinct_zones}, cellules vides: {empty_count}, attendu: {grid_size} zones"
        )

        # Si validation échoue (mauvais nombre de zones ou trop de vides), clustering K-means++
        too_many_empty = empty_count > (grid_size * grid_size * 0.15)  # > 15% vides = suspect
        wrong_zone_count = distinct_zones != grid_size

        if wrong_zone_count or too_many_empty:
            logger.warning(
                f"Validation échouée ({distinct_zones} zones distinctes, {empty_count} vides). Clustering K-means++..."
            )
            zones = refine_zones_with_clustering(image_array, grid_size)

        # Calculer la confiance
        confidence = calculate_confidence(zones)

        return {"size": grid_size, "zones": zones, "confidence": confidence}

    except Exception as e:
        logger.error(f"Erreur lors du traitement de l'image: {e}")
        raise


def detect_grid_size(image_array):
    """
    Détecte la taille de la grille en cherchant les lignes noires.
    """
    height, width = image_array.shape[:2]

    # Chercher les bordures noires (valeurs < 50)
    gray = np.mean(image_array, axis=2)
    black_pixels = gray < 50

    # Ratio de pixels noirs par ligne et par colonne
    row_black_ratio = np.mean(black_pixels, axis=1)
    col_black_ratio = np.mean(black_pixels, axis=0)

    row_lines = np.where(row_black_ratio > 0.15)[0]
    col_lines = np.where(col_black_ratio > 0.15)[0]

    if len(row_lines) < 2 or len(col_lines) < 2:
        return None

    row_groups = np.split(row_lines, np.where(np.diff(row_lines) > 1)[0] + 1)
    col_groups = np.split(col_lines, np.where(np.diff(col_lines) > 1)[0] + 1)

    grid_size_v = max(0, len(row_groups) - 1)
    grid_size_h = max(0, len(col_groups) - 1)

    if grid_size_v < 4 or grid_size_h < 4:
        return None

    grid_size = min(grid_size_v, grid_size_h)

    # Limiter entre 4 et 15
    grid_size = max(4, min(15, grid_size))

    logger.debug(f"Lignes détectées - V: {len(row_groups)}, H: {len(col_groups)}")
    logger.debug(f"Taille détectée: {grid_size}")

    return grid_size


def extract_grid_cells(image_array, grid_size):
    """
    Extrait les cellules de la grille en utilisant les vraies positions des lignes noires.
    """
    height, width = image_array.shape[:2]

    # Détecter les vraies positions des lignes de grille noires
    gray = np.mean(image_array, axis=2)
    black_pixels = gray < 50

    row_lines = np.where(np.mean(black_pixels, axis=1) > 0.15)[0]
    col_lines = np.where(np.mean(black_pixels, axis=0) > 0.15)[0]

    if len(row_lines) < 2 or len(col_lines) < 2:
        logger.warning(
            f"Pas assez de lignes détectées: rows={len(row_lines)}, cols={len(col_lines)}"
        )
        return extract_grid_cells_fallback(image_array, grid_size)

    row_groups = np.split(row_lines, np.where(np.diff(row_lines) > 1)[0] + 1)
    col_groups = np.split(col_lines, np.where(np.diff(col_lines) > 1)[0] + 1)

    # Positions des lignes de grille (première position de chaque groupe)
    row_positions = [int(g[0]) for g in row_groups]
    col_positions = [int(g[0]) for g in col_groups]

    # S'assurer qu'on a assez de positions
    if len(row_positions) != grid_size + 1 or len(col_positions) != grid_size + 1:
        logger.warning(
            f"Mismatch positions: rows={len(row_positions)} (expected {grid_size + 1}), cols={len(col_positions)} (expected {grid_size + 1})"
        )
        return extract_grid_cells_fallback(image_array, grid_size)

    zones = []

    for row in range(grid_size):
        zone_row = []

        # Limites de la ligne (entre deux lignes noires, sans les bordures)
        y_start = row_positions[row] + 3
        y_end = row_positions[row + 1] - 3

        for col in range(grid_size):
            # Limites de la colonne
            x_start = col_positions[col] + 3
            x_end = col_positions[col + 1] - 3

            # Extraire la région de la cellule
            if y_end <= y_start or x_end <= x_start:
                logger.debug(
                    f"Cellule invalide à [{row}, {col}]: y=[{y_start}:{y_end}], x=[{x_start}:{x_end}]"
                )
                zone_row.append(EMPTY_VALUE)
                continue

            cell_region = image_array[y_start:y_end, x_start:x_end]

            if cell_region.size == 0:
                logger.warning(f"Cellule vide à [{row}, {col}]")
                zone_row.append(EMPTY_VALUE)
                continue

            # Calculer la couleur représentative de la cellule
            mean_color = get_cell_color(cell_region)
            if mean_color is None:
                zone_row.append(EMPTY_VALUE)
                continue

            # Trouver la zone correspondante
            zone = find_closest_zone_color(tuple(mean_color))
            zone_row.append(zone)

        zones.append(zone_row)

    return zones


def extract_grid_cells_fallback(image_array, grid_size):
    """
    Fallback: extrait les cellules en divisant simplement l'image.
    """
    height, width = image_array.shape[:2]

    # Calculer la taille théorique d'une cellule
    cell_height = height / grid_size
    cell_width = width / grid_size

    logger.debug(f"Image: {width}x{height}, Cellule théorique: {cell_width}x{cell_height}")

    zones = []

    for row in range(grid_size):
        zone_row = []

        # Limites de la ligne
        y_start = int(row * cell_height + 5)
        y_end = int((row + 1) * cell_height - 5)

        for col in range(grid_size):
            # Limites de la colonne
            x_start = int(col * cell_width + 5)
            x_end = int((col + 1) * cell_width - 5)

            # Extraire la région de la cellule
            cell_region = image_array[y_start:y_end, x_start:x_end]

            if cell_region.size == 0:
                zone_row.append(EMPTY_VALUE)
                continue

            # Calculer la couleur représentative de la cellule
            mean_color = get_cell_color(cell_region)
            if mean_color is None:
                zone_row.append(EMPTY_VALUE)
                continue

            # Trouver la zone correspondante
            zone = find_closest_zone_color(tuple(mean_color))
            zone_row.append(zone)

        zones.append(zone_row)

    return zones


def calculate_confidence(zones):
    """
    Calcule un score de confiance pour l'extraction (0-1).
    Plus de zones vides et moins de zones différentes = moins de confiance.
    """
    flat_zones = [z for row in zones for z in row]
    empty_count = sum(1 for z in flat_zones if z == EMPTY_VALUE)
    unique_zones = len(set(flat_zones))

    # Au moins quelques zones et pas trop vides
    confidence = 1.0

    # Pénalité si trop vides
    empty_ratio = empty_count / len(flat_zones)
    if empty_ratio > 0.5:
        confidence -= 0.3

    # Bonus si zones variées
    if unique_zones >= 3:
        confidence += 0.1

    return max(0.0, min(1.0, confidence))


def refine_zones_with_clustering(image_array, grid_size):
    """
    Améliore la détection des zones en utilisant un clustering basé sur les couleurs réelles.

    Stratégie:
    1. Extrait les positions de grille
    2. Récupère les couleurs moyennes de chaque cellule
    3. Regroupe les cellules par similarité de couleur (K-means simple)
    4. Assigne les couleurs aux zones basées sur les clusters

    Cette approche est ROBUSTE: elle ne dépend pas de la palette frontend,
    mais plutôt de l'identification de régions de couleurs distinctes dans la grille.
    """
    height, width = image_array.shape[:2]

    # Détecter les vraies positions des lignes de grille noires
    gray = np.mean(image_array, axis=2)
    black_pixels = gray < 50

    row_lines = np.where(np.mean(black_pixels, axis=1) > 0.15)[0]
    col_lines = np.where(np.mean(black_pixels, axis=0) > 0.15)[0]

    if len(row_lines) < 2 or len(col_lines) < 2:
        logger.warning("Pas assez de lignes de grille pour clustering")
        return extract_grid_cells_fallback(image_array, grid_size)

    row_groups = np.split(row_lines, np.where(np.diff(row_lines) > 1)[0] + 1)
    col_groups = np.split(col_lines, np.where(np.diff(col_lines) > 1)[0] + 1)

    row_positions = [int(g[0]) for g in row_groups]
    col_positions = [int(g[0]) for g in col_groups]

    if len(row_positions) != grid_size + 1 or len(col_positions) != grid_size + 1:
        logger.warning("Mismatch lignes de grille, utilisation fallback")
        return extract_grid_cells_fallback(image_array, grid_size)

    # Étape 1: Extraire les couleurs moyennes de chaque cellule
    cell_colors = []
    cell_positions = []  # (row, col) pour chaque cellule

    for row in range(grid_size):
        for col in range(grid_size):
            y_start = row_positions[row] + 3
            y_end = row_positions[row + 1] - 3
            x_start = col_positions[col] + 3
            x_end = col_positions[col + 1] - 3

            if y_end <= y_start or x_end <= x_start:
                cell_colors.append(None)
                cell_positions.append((row, col))
                continue

            cell_region = image_array[y_start:y_end, x_start:x_end]
            if cell_region.size == 0:
                cell_colors.append(None)
                cell_positions.append((row, col))
                continue

            mean_color = get_cell_color(cell_region)
            cell_colors.append(mean_color)
            cell_positions.append((row, col))

    # Étape 2: regroupement couleur direct (base de couleurs réelles de cellules)
    valid_indices = [i for i, color in enumerate(cell_colors) if color is not None]
    if not valid_indices:
        logger.error("Aucune couleur valide trouvée")
        return extract_grid_cells_fallback(image_array, grid_size)

    num_clusters = grid_size
    color_features = [np.array(cell_colors[i], dtype=float) for i in valid_indices]

    # Regroupement initial par seuil de couleur
    cluster_centers = []
    threshold = 15.0
    for feature in color_features:
        if not cluster_centers:
            cluster_centers.append(feature)
            continue
        dists = [np.linalg.norm(feature - center) for center in cluster_centers]
        if min(dists) >= threshold:
            cluster_centers.append(feature)

    # Si on a plus de clusters que prévu, fusionner les deux plus proches
    while len(cluster_centers) > num_clusters:
        best_pair = None
        best_dist = float("inf")
        for i in range(len(cluster_centers)):
            for j in range(i + 1, len(cluster_centers)):
                d = np.linalg.norm(cluster_centers[i] - cluster_centers[j])
                if d < best_dist:
                    best_dist = d
                    best_pair = (i, j)
        i, j = best_pair
        merged = (cluster_centers[i] + cluster_centers[j]) / 2
        cluster_centers[i] = merged
        cluster_centers.pop(j)

    # Si on a moins de clusters que prévu, compléter avec K-means++
    if len(cluster_centers) < num_clusters:
        remaining = [
            f for f in color_features if not any(np.array_equal(f, c) for c in cluster_centers)
        ]
        for _ in range(num_clusters - len(cluster_centers)):
            if not remaining:
                break
            dists = [
                min(np.linalg.norm(feature - center) for center in cluster_centers)
                for feature in remaining
            ]
            next_idx = int(np.argmax(dists))
            cluster_centers.append(remaining[next_idx])
            remaining.pop(next_idx)

    assignments = [-1] * len(cell_colors)
    for i, color in enumerate(cell_colors):
        if color is None:
            assignments[i] = -1
        else:
            feature = np.array(color, dtype=float)
            dists = [np.linalg.norm(feature - center) for center in cluster_centers]
            assignments[i] = int(np.argmin(dists))

    # Assurer qu'il y a bien num_clusters labels utilisés
    used = sorted(set(a for a in assignments if a != -1))
    if len(used) != num_clusters:
        # Réassigner les clusters par K-means si le seuil direct échoue
        logger.warning("Regroupement direct insuffisant, fallback K-means")
        assignments = [-1] * len(cell_colors)
        cluster_centers = [np.array(color_features[0])]
        for _ in range(1, num_clusters):
            dists = [
                min(np.linalg.norm(feature - center) for center in cluster_centers)
                for feature in color_features
            ]
            cluster_centers.append(color_features[int(np.argmax(dists))])
        for _ in range(20):
            prev_assignments = assignments[:]
            for i, color in enumerate(cell_colors):
                if color is None:
                    assignments[i] = -1
                else:
                    feature = np.array(color, dtype=float)
                    dists = [np.linalg.norm(feature - center) for center in cluster_centers]
                    assignments[i] = int(np.argmin(dists))
            new_centers = []
            for cid in range(num_clusters):
                cluster_feats = [
                    np.array(cell_colors[i], dtype=float)
                    for i in valid_indices
                    if assignments[i] == cid
                ]
                if cluster_feats:
                    new_centers.append(np.mean(cluster_feats, axis=0))
                else:
                    new_centers.append(cluster_centers[cid])
            cluster_centers = new_centers
            if assignments == prev_assignments:
                break

    logger.info(
        f"K-means++ terminé: {num_clusters} clusters, {len(set(a for a in assignments if a != -1))} distincts"
    )

    # Remapper les clusters vers les indices de la palette frontend (assignment unique)
    cluster_centers = []
    for cluster_id in range(num_clusters):
        cluster_colors = [
            np.array(cell_colors[i], dtype=float)
            for i in valid_indices
            if assignments[i] == cluster_id
        ]
        if cluster_colors:
            cluster_centers.append(np.mean(cluster_colors, axis=0))
        else:
            cluster_centers.append(np.array([0.0, 0.0, 0.0]))

    # Construire toutes les paires (distance, cluster_id, palette_id) et assigner sans doublon
    dist_pairs = []
    for ci, center in enumerate(cluster_centers):
        for pi, palette_color in enumerate(GRID_COLORS):
            d = color_distance(tuple(np.clip(center, 0, 255).astype(int)), palette_color)
            dist_pairs.append((d, ci, pi))
    dist_pairs.sort()

    cluster_to_palette = {}
    assigned_palette = set()
    for _d, ci, pi in dist_pairs:
        if ci not in cluster_to_palette and pi not in assigned_palette:
            cluster_to_palette[ci] = pi
            assigned_palette.add(pi)
        if len(cluster_to_palette) == num_clusters:
            break

    zones = []
    for row in range(grid_size):
        zone_row = []
        for col in range(grid_size):
            cell_idx = row * grid_size + col
            cluster_id = assignments[cell_idx]
            if cluster_id == -1:
                zone_row.append(EMPTY_VALUE)
            else:
                zone_row.append(cluster_to_palette[cluster_id])
        zones.append(zone_row)

    return zones
