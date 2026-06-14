# Benchmark & Statistiques — Guide Utilisateur

---

## Lancer un benchmark

Clique sur l'icône graphique dans la barre d'outils pour lancer un benchmark automatique sur **toutes les tailles de grille de 4 à 12**.

Pour chaque taille, une grille de test est générée et résolue par les deux services (TRM et Baseline). Les résultats sont ajoutés à l'historique de session.

> Le benchmark peut prendre quelques secondes selon la puissance de la machine, notamment pour les grandes grilles avec le Baseline.

---

## Vue Statistiques

L'onglet **Statistiques** affiche un graphique comparatif TRM vs Baseline basé sur toutes les résolutions de la session (benchmark + résolutions manuelles).

### Lire le graphique

- **Barres bleues** → temps moyen TRM
- **Barres oranges** → temps moyen Baseline
- **Axe Y** → temps de résolution (échelle logarithmique — permet d'afficher µs et secondes sur le même graphe)
- **Axe X** → taille de grille
- **×N** au-dessus des barres → speedup (combien de fois le TRM est plus rapide)

### Tooltip

Survole une barre pour voir le détail : service, taille, temps moyen et nombre de mesures.

---

## Vue Historique

L'onglet **Historique** liste toutes les résolutions effectuées pendant la session.

| Colonne | Description |
|---|---|
| Taille | N×N |
| TRM | Temps de résolution TRM |
| Baseline | Temps de résolution Baseline |
| Solutions | Nombre de solutions trouvées |

Clique sur une entrée pour recharger la grille correspondante en vue Jeu.

---

## Réinitialiser les statistiques

L'historique est **en mémoire uniquement** — il disparaît au rechargement de la page. Pour repartir de zéro sans recharger, ferme et réouvre l'onglet.

---

[← Import](./import.md) | [Raccourcis →](./raccourcis.md) | [Vue d'ensemble Frontend](./README.md)
