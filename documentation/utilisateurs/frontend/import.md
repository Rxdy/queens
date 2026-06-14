# Import de Grille — Guide Utilisateur

Deux façons d'importer une grille : **par texte** ou **depuis une photo**.

---

## Ouvrir le modal d'import

Clique sur l'icône d'import dans la barre d'outils, ou utilise le bouton **Importer une grille** en vue Jeu. La touche **Échap** ferme le modal à tout moment.

---

## Import par texte

Colle une matrice de nombres dans la zone de texte. Chaque ligne représente une rangée de la grille.

### Format accepté

- Séparateurs : espaces, virgules ou points-virgules
- Identifiants de zone : entiers ≥ 0 (0-based)
- Cellule vide : `-1`
- La grille doit être carrée (N×N)
- Taille minimale : 4×4
- Identifiants de zone : remappés automatiquement à partir de 0

### Exemple

```
0 0 1 1
0 2 2 1
3 2 2 1
3 3 3 1
```

### Preview live

La grille s'affiche en aperçu en temps réel pendant la saisie. Les erreurs de format sont signalées immédiatement sous la zone de texte.

### Erreurs courantes

| Erreur | Cause |
|---|---|
| *La matrice doit être carrée* | Nombre de colonnes ≠ nombre de lignes |
| *Au moins 4×4* | Taille insuffisante |
| *Valeur invalide* | Token non entier dans la matrice |
| *Trop de zones distinctes* | Plus de N zones différentes pour une grille N×N |

---

## Import par photo

> Nécessite que le service TRM soit en ligne.

1. Sélectionne l'onglet **Photo** dans le modal
2. Clique sur **Choisir une image** et sélectionne une capture d'écran du jeu Queens
3. Clique sur **Extraire la grille** — le service analyse l'image et propose une grille
4. Vérifie l'aperçu et clique sur **Valider** pour charger la grille

Le score de **confiance** indique la qualité de la détection (0 à 1).

---

## Exporter la grille courante

Le bouton **Copier** dans la barre d'outils copie la grille actuelle dans le presse-papier au format texte, prête à être collée dans le modal d'import ou partagée.

Le bouton **Télécharger** génère une image PNG de la grille actuelle.

---

[← Brouillons](./brouillons.md) | [Benchmark →](./benchmark.md) | [Vue d'ensemble Frontend](./README.md)
