# Brouillons — Guide Utilisateur

Les brouillons permettent de travailler sur plusieurs configurations de grille en parallèle et de les retrouver après un rechargement de page.

---

## Comment ça marche

- Chaque brouillon mémorise : la **taille de la grille**, les **zones peintes** et la **couleur sélectionnée**
- Les brouillons sont **sauvegardés automatiquement** dans le navigateur (localStorage) — ils survivent au rechargement de la page
- Maximum **15 brouillons** simultanés

---

## Créer un brouillon

Clique sur le bouton **+** dans la liste des brouillons (panneau latéral gauche). Un nouveau brouillon vide 8×8 est créé et sélectionné immédiatement.

---

## Changer de brouillon

Clique sur un brouillon dans la liste pour le charger. Le brouillon courant est sauvegardé automatiquement avant le changement.

---

## Supprimer un brouillon

Clique sur le bouton de suppression (✕) à droite du brouillon. Si c'était le brouillon actif, le premier de la liste est chargé à la place. S'il ne restait qu'un seul brouillon, la grille se remet à zéro.

---

## Sauvegarde automatique

La grille est sauvegardée dans le brouillon actif à chaque modification de cellule. Il n'y a pas de bouton "Sauvegarder" — tout est automatique.

---

## Persistance

Les brouillons sont stockés dans le `localStorage` du navigateur sous la clé `queens-drafts`. Ils sont partagés entre les onglets du même navigateur sur le même domaine.

> Si tu effaces le cache ou les données du site, les brouillons sont perdus.

---

[← Grille](./grille.md) | [Import →](./import.md) | [Vue d'ensemble Frontend](./README.md)
