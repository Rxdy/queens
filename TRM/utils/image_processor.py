"""
Processeur d'images pour extraire les matrices de grille
"""
import numpy as np
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger("image_processor")

# Les couleurs du frontend (RGB)
GRID_COLORS = [
    (223, 160, 191),  # 0 - Rose
    (150, 190, 255),  # 1 - Bleu clair
    (255, 201, 146),  # 2 - Orange
    (187, 163, 226),  # 3 - Violet
    (240, 240, 240),  # 4 - Gris très clair
    (139, 69, 19),    # 5 - Marron
    (255, 123, 96),   # 6 - Rouge/Orange
    (230, 243, 136),  # 7 - Jaune clair
    (179, 223, 160),  # 8 - Vert clair
    (85, 235, 226),   # 9 - Cyan
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


def find_closest_zone_color(rgb_color):
    """
    Trouve la couleur de zone la plus proche d'une couleur donnée.
    Retourne l'index de la zone (0-11) ou -1 si c'est du blanc (vide).
    """
    r, g, b = rgb_color
    
    # D'abord, trouver la zone la plus proche
    min_distance = float('inf')
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
    
    return closest_zone


def extract_matrix_from_image(image_data: bytes, expected_size: int = None):
    """
    Extrait une matrice de grille d'une image.
    
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
        image = Image.open(BytesIO(image_data)).convert('RGB')
        image_array = np.array(image)
        
        logger.info(f"Image reçue: {image_array.shape}")
        
        # Déterminer la taille de la grille en analysant les bordures noires
        grid_size = detect_grid_size(image_array)
        
        if grid_size is None:
            raise ValueError("Impossible de détecter la grille dans l'image")
        
        if expected_size and grid_size != expected_size:
            logger.warning(f"Taille détectée ({grid_size}) != attendue ({expected_size})")
        
        logger.info(f"Grille détectée: {grid_size}x{grid_size}")
        
        # Extraire les cellules
        zones = extract_grid_cells(image_array, grid_size)
        
        # Calculer la confiance
        confidence = calculate_confidence(zones)
        
        return {
            "size": grid_size,
            "zones": zones,
            "confidence": confidence
        }
    
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
        logger.warning(f"Pas assez de lignes détectées: rows={len(row_lines)}, cols={len(col_lines)}")
        return extract_grid_cells_fallback(image_array, grid_size)
    
    row_groups = np.split(row_lines, np.where(np.diff(row_lines) > 1)[0] + 1)
    col_groups = np.split(col_lines, np.where(np.diff(col_lines) > 1)[0] + 1)
    
    # Positions des lignes de grille (première position de chaque groupe)
    row_positions = [int(g[0]) for g in row_groups]
    col_positions = [int(g[0]) for g in col_groups]
    
    # S'assurer qu'on a assez de positions
    if len(row_positions) != grid_size + 1 or len(col_positions) != grid_size + 1:
        logger.warning(f"Mismatch positions: rows={len(row_positions)} (expected {grid_size+1}), cols={len(col_positions)} (expected {grid_size+1})")
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
                logger.debug(f"Cellule invalide à [{row}, {col}]: y=[{y_start}:{y_end}], x=[{x_start}:{x_end}]")
                zone_row.append(EMPTY_VALUE)
                continue
            
            cell_region = image_array[y_start:y_end, x_start:x_end]
            
            if cell_region.size == 0:
                logger.warning(f"Cellule vide à [{row}, {col}]")
                zone_row.append(EMPTY_VALUE)
                continue
            
            # Calculer la couleur moyenne de la cellule
            mean_color = np.mean(cell_region, axis=(0, 1)).astype(int)
            
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
            
            # Calculer la couleur moyenne de la cellule
            mean_color = np.mean(cell_region, axis=(0, 1)).astype(int)
            
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
