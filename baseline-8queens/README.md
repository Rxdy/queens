# Baseline 8-Queens (One-shot)

Objectif : construire un **modèle baseline "classique" one-shot** pour le problème des **8 reines** :
à partir d'un plateau **partiel** (quelques reines déjà placées sans conflit), le modèle prédit en **une seule passe**
un placement complet (1 reine par ligne) et on mesure la validité (conflits lignes/colonnes/diagonales).

## Installation

### 1) Créer un environnement virtuel

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

overall :

solved_rate (global)
conflicts_mean, conflicts_median
inference_samples_per_sec

by_k_fixed :

taux de réussite en fonction du nombre de reines fixées

conflicts_mean_by_k_fixed :

conflits moyens en fonction de k_fixed

train_log.json (courbes d’entraînement)

history: liste des epochs avec :

train_loss
val_solved_rate
val_conflicts_mean
is_best

best_epoch + best_value

python -m src.data --out outputs/dataset.npz --train 5000 --val 1000 --test 1000 --kmin 2 --kmax 6 --seed 42

python -m src.train --data outputs/dataset.npz --outdir outputs --epochs 10 --batch 256 --lr 1e-3 --seed 42

python -m src.eval --data outputs/dataset.npz --ckpt outputs/best.pt --out outputs/eval.json

python -m src.viz --eval outputs/eval.json --outdir outputs
