# La Grille — Guide Utilisateur

---

## Peindre les zones

La grille affiche N×N cellules. L'objectif est de colorier chaque cellule pour délimiter N zones, puis de résoudre.

### Changer la taille de la grille

Un sélecteur en haut de la vue **Jeu** permet de choisir la taille (4 à 12). **Changer la taille remet la grille à zéro.**

### Peindre à la souris

| Action | Effet |
|---|---|
| Clic gauche | Peint la cellule avec la couleur sélectionnée |
| Clic droit | Efface la cellule (retour à l'état vide) |
| Maintenir + glisser | Continue l'action sur toutes les cellules survolées |

### Peindre sur mobile (tactile)

| Geste | Effet |
|---|---|
| Appui | Peint la cellule touchée |
| Glisser le doigt | Continue de peindre sur les cellules suivantes |

---

## Choisir une couleur

La palette de couleurs est affichée à droite de la grille. Clique sur une couleur pour la sélectionner avant de peindre.

Le nombre de couleurs utilisables est limité à N (taille de la grille) — une couleur par zone.

---

## Annuler une action

- **Ctrl+Z** (ou **Cmd+Z** sur Mac) annule le dernier geste de peinture
- L'annulation remonte jusqu'à 20 étapes en arrière
- L'historique d'annulation est remis à zéro lors d'une réinitialisation de grille

---

## Résoudre

Le bouton **Résoudre** (ou la touche **Entrée** / **Espace**) se déverrouille quand toutes les cellules sont peintes (`isGridComplete`).

Deux services sont appelés en parallèle :
- **TRM** — retourne toutes les solutions rapidement
- **Baseline** — retourne le nombre de solutions et la première (plus lent)

### Naviguer entre les solutions

Si plusieurs solutions existent, des boutons `←` et `→` apparaissent.

| Action | Effet |
|---|---|
| Clic `→` | Solution suivante |
| Clic `←` | Solution précédente |
| Touche `→` | Solution suivante |
| Touche `←` | Solution précédente |

Les reines sont affichées sur la grille avec une couronne **♛**.

---

## Réinitialiser

Le bouton **Nouvelle grille** (ou le sélecteur de taille) remet la grille à zéro et crée un nouveau brouillon.

---

[← Vue d'ensemble Frontend](./README.md) | [Brouillons →](./brouillons.md) | [Raccourcis](./raccourcis.md)
