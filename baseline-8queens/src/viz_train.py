from __future__ import annotations

import argparse
import json
import os

import matplotlib.pyplot as plt


def parse_args():
    p = argparse.ArgumentParser(
        description="Visualize training curves from train_log.json"
    )
    p.add_argument(
        "--log",
        type=str,
        default="outputs/train_log.json",
        help="Path to train_log.json",
    )
    p.add_argument("--outdir", type=str, default="outputs", help="Where to save PNGs")
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    with open(args.log, "r", encoding="utf-8") as f:
        log = json.load(f)

    history = log.get("history", [])
    if not history:
        raise ValueError("No 'history' found in train_log.json")

    epochs = [h["epoch"] for h in history]
    train_loss = [h.get("train_loss") for h in history]
    val_solved = [h.get("val_solved_rate") for h in history]
    val_conf = [h.get("val_conflicts_mean") for h in history]
    is_best = [h.get("is_best", False) for h in history]

    # Identify best epoch
    best_epoch = log.get("best_epoch", None)
    if best_epoch is None:
        # fallback: first True is_best
        for e, b in zip(epochs, is_best):
            if b:
                best_epoch = e
                break

    def mark_best(ax, y_values, title):
        if best_epoch is None:
            ax.set_title(title)
            return
        # find index
        if best_epoch in epochs:
            idx = epochs.index(best_epoch)
            ax.scatter([best_epoch], [y_values[idx]], color="red", zorder=5)
            ax.annotate(
                "best",
                (best_epoch, y_values[idx]),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
            )
        ax.set_title(title)

    # 1) Train loss
    plt.figure(figsize=(8, 4.5))
    plt.plot(epochs, train_loss, marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Train loss")
    plt.grid(True, alpha=0.3)
    mark_best(plt.gca(), train_loss, "Train loss vs epoch")
    plt.tight_layout()
    out1 = os.path.join(args.outdir, "train_loss.png")
    plt.savefig(out1, dpi=160)
    plt.close()

    # 2) Val solved rate
    plt.figure(figsize=(8, 4.5))
    plt.plot(epochs, val_solved, marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Val solved rate")
    plt.grid(True, alpha=0.3)
    mark_best(plt.gca(), val_solved, "Validation solved rate vs epoch")
    plt.tight_layout()
    out2 = os.path.join(args.outdir, "val_solved_rate.png")
    plt.savefig(out2, dpi=160)
    plt.close()

    # 3) Val conflicts mean
    plt.figure(figsize=(8, 4.5))
    plt.plot(epochs, val_conf, marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Val conflicts mean")
    plt.grid(True, alpha=0.3)
    mark_best(plt.gca(), val_conf, "Validation conflicts mean vs epoch")
    plt.tight_layout()
    out3 = os.path.join(args.outdir, "val_conflicts_mean.png")
    plt.savefig(out3, dpi=160)
    plt.close()

    print(f"[INFO] Saved: {out1}")
    print(f"[INFO] Saved: {out2}")
    print(f"[INFO] Saved: {out3}")


if __name__ == "__main__":
    main()
