#!/usr/bin/env python3
"""
Génère un set d'images de test synthétiques pour valider l'algo d'extraction.
Utilise la VRAIE palette d'image_processor.py pour l'exactitude.
"""
from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path
from TRM.utils.image_processor import extract_matrix_from_image, GRID_COLORS

def create_grid_image(size, zones_data, cell_size=62, line_width=2):
    """
    Crée une image PNG d'une grille colorée.
    
    Args:
        size: dimension de la grille (5x5, 6x6, etc.)
        zones_data: liste 2D des index de zones (0-11)
        cell_size: taille d'une cellule en pixels
        line_width: épaisseur des lignes de séparation
    
    Returns:
        bytes: PNG image data
    """
    # Calculer les dimensions
    img_size = size * cell_size + (size + 1) * line_width
    
    # Créer image blanche
    img = Image.new('RGB', (img_size, img_size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Dessiner les cellules
    for row in range(size):
        for col in range(size):
            zone_idx = zones_data[row][col]
            color = GRID_COLORS[zone_idx]
            
            # Position du coin supérieur gauche
            x1 = col * (cell_size + line_width) + line_width
            y1 = row * (cell_size + line_width) + line_width
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            
            # Remplir la cellule
            draw.rectangle([x1, y1, x2, y2], fill=color)
    
    # Dessiner les lignes noires
    line_color = (0, 0, 0)
    for i in range(size + 1):
        pos = i * (cell_size + line_width)
        # Lignes horizontales
        draw.rectangle([0, pos, img_size, pos + line_width], fill=line_color)
        # Lignes verticales
        draw.rectangle([pos, 0, pos + line_width, img_size], fill=line_color)
    
    return img


def test_images():
    """Génère et teste un set d'images."""
    
    test_cases = [
        # (taille, données zones, description)
        # Note: Utilise la vraie palette d'image_processor.py
        # 0=Rose, 1=BleuClair, 2=Orange, 3=Violet, 4=GrisClair,
        # 5=Marron, 6=RougeFeu, 7=JauneVert, 8=VertClair, 9=Cyan, 10=BleuVert, 11=Mauve
        
        (5, [
            [1, 1, 1, 2, 7],
            [1, 1, 1, 2, 7],
            [2, 2, 2, 2, 7],
            [8, 8, 4, 4, 7],
            [8, 8, 8, 4, 4]
        ], "5x5 - Pattern réel (imageTEST)"),
        
        (6, [
            [0, 0, 1, 1, 2, 2],
            [0, 0, 1, 1, 2, 2],
            [3, 3, 4, 4, 7, 7],
            [3, 3, 4, 4, 7, 7],
            [8, 8, 9, 9, 10, 10],
            [8, 8, 9, 9, 10, 10]
        ], "6x6 - Blocs 2x2 bien espacés"),
        
        (7, [
            [0, 0, 1, 1, 2, 2, 3],
            [0, 0, 1, 1, 2, 2, 3],
            [4, 4, 5, 5, 7, 7, 8],
            [4, 4, 5, 5, 7, 7, 8],
            [9, 9, 10, 10, 11, 11, 0],
            [9, 9, 10, 10, 11, 11, 0],
            [1, 2, 3, 4, 7, 8, 9]
        ], "7x7 - Grille mixte"),
        
        (8, [
            [0, 1, 2, 3, 4, 7, 8, 9],
            [1, 2, 3, 4, 7, 8, 9, 0],
            [2, 3, 4, 7, 8, 9, 0, 1],
            [3, 4, 7, 8, 9, 0, 1, 2],
            [4, 7, 8, 9, 0, 1, 2, 3],
            [7, 8, 9, 0, 1, 2, 3, 4],
            [8, 9, 0, 1, 2, 3, 4, 7],
            [9, 0, 1, 2, 3, 4, 7, 8]
        ], "8x8 - Rotation + 8 zones"),
        
        (5, [
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 7],
            [2, 3, 4, 7, 8],
            [3, 4, 7, 8, 9],
            [4, 7, 8, 9, 10]
        ], "5x5 - Diagonale"),
        
        (6, [
            [0, 0, 0, 1, 1, 1],
            [0, 0, 0, 1, 1, 1],
            [2, 2, 2, 3, 3, 3],
            [2, 2, 2, 3, 3, 3],
            [4, 4, 4, 7, 7, 7],
            [4, 4, 4, 7, 7, 7]
        ], "6x6 - Blocs 2x2 simples"),
    ]
    
    test_dir = Path('test_images')
    test_dir.mkdir(exist_ok=True)
    
    results = []
    
    for size, zones_data, description in test_cases:
        print(f"\n🎯 Génération: {description}")
        
        # Créer l'image
        img = create_grid_image(size, zones_data)
        img_path = test_dir / f"test_{size}x{size}.png"
        img.save(img_path)
        print(f"   ✅ Image sauvegardée: {img_path}")
        
        # Tester l'extraction
        extracted = extract_matrix_from_image(img_path.read_bytes())
        extracted_zones = extracted['zones']
        confidence = extracted['confidence']
        
        # Comparer
        match = extracted_zones == zones_data
        status = "✅ PERFECT" if match else "❌ MISMATCH"
        
        print(f"   {status}")
        print(f"   Détecté: {size}x{size}, Confiance: {confidence:.1%}")
        
        if not match:
            print(f"   ⚠️  Attendu vs Extraction:")
            for row_idx, (expected_row, extracted_row) in enumerate(zip(zones_data, extracted_zones)):
                match_row = "✓" if expected_row == extracted_row else "✗"
                print(f"      Row {row_idx} {match_row}: {expected_row} vs {extracted_row}")
        
        results.append({
            'file': str(img_path),
            'size': size,
            'description': description,
            'match': match,
            'confidence': confidence
        })
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for r in results if r['match'])
    
    for r in results:
        status = "✅" if r['match'] else "❌"
        print(f"{status} {r['size']}x{r['size']:2d}  {r['description']:25s}  Conf: {r['confidence']:.1%}")
    
    print("="*70)
    print(f"Score: {passed}/{total} ({100*passed/total:.0f}%)")
    print(f"Images sauvegardées dans: {test_dir}/")


if __name__ == '__main__':
    test_images()
