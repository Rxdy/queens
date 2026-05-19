from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Dict, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from .model import QueensBaseline, masked_ce_loss, apply_fixed_constraints
from .metrics import solved_rate, count_conflicts


@dataclass
class TrainConfig:
    data: str = "outputs/dataset.npz"
    outdir: str = "outputs"
    epochs: int = 20
    batch: int = 256
    lr: float = 1e-3
    weight_decay: float = 0.0
    seed: int = 42
    device: str = "auto"  # auto | cpu | cuda
    num_workers: int = 0
    pin_memory: bool = True

    # model hyperparams
    d_model: int = 64
    hidden: int = 256
    depth: int = 3
    dropout: float = 0.1

    # how to pick best model
    best_metric: str = "val_solved_rate"  # or val_conflicts_mean
    maximize_best_metric: bool = True  # True for solved_rate, False for conflicts_mean


class QueensNPZDataset(Dataset):
    """
    Wraps arrays from the .npz dataset.
    x: (N,8) int8 values in {-1..7}
    y: (N,8) int8 values in {0..7}
    fixed_mask: (N,8) bool
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, fixed_mask: np.ndarray):
        assert x.shape == y.shape, "x and y must have same shape"
        assert x.shape[1] == 8, "Expected shape (N,8)"
        self.x = x.astype(np.int64, copy=False)
        self.y = y.astype(np.int64, copy=False)
        self.fixed_mask = fixed_mask.astype(bool, copy=False)

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, idx: int):
        return (
            torch.from_numpy(self.x[idx]).long(),  # (8,)
            torch.from_numpy(self.y[idx]).long(),  # (8,)
            torch.from_numpy(self.fixed_mask[idx]).bool(),  # (8,)
        )


def set_seed(seed: int):
    import random

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # deterministic-ish (can slow down)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def resolve_device(device: str) -> torch.device:
    if device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device == "cuda":
        return torch.device("cuda")
    return torch.device("cpu")


@torch.no_grad()
def evaluate(
    model: QueensBaseline, loader: DataLoader, device: torch.device
) -> Dict[str, float]:
    model.eval()

    all_preds = []
    all_conflicts = []

    for x, y, fixed_mask in loader:
        x = x.to(device)
        # forward
        logits = model(x)  # (B,8,8)
        # enforce fixed constraints at inference for fairness
        logits = apply_fixed_constraints(logits, x)
        pred = torch.argmax(logits, dim=-1)  # (B,8)

        pred_np = pred.detach().cpu().numpy().astype(int)
        all_preds.append(pred_np)

        conf_np = count_conflicts(pred_np)  # returns (B,)
        all_conflicts.append(conf_np)

    preds = np.concatenate(all_preds, axis=0)
    conflicts = np.concatenate(all_conflicts, axis=0)

    return {
        "solved_rate": float(solved_rate(preds)),
        "conflicts_mean": float(np.mean(conflicts)),
        "conflicts_median": float(np.median(conflicts)),
    }


def parse_args() -> TrainConfig:
    p = argparse.ArgumentParser(
        description="Train baseline one-shot model for 8-Queens completion."
    )
    p.add_argument(
        "--data", type=str, default="outputs/dataset.npz", help="Path to dataset .npz"
    )
    p.add_argument("--outdir", type=str, default="outputs", help="Output directory")
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--batch", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight_decay", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--device", type=str, default="auto", choices=["auto", "cpu", "cuda"]
    )
    p.add_argument("--num_workers", type=int, default=0)
    p.add_argument(
        "--pin_memory", action="store_true", help="Pin memory for DataLoader (GPU)"
    )
    p.add_argument("--no-pin_memory", dest="pin_memory", action="store_false")
    p.set_defaults(pin_memory=True)

    # model params
    p.add_argument("--d_model", type=int, default=64)
    p.add_argument("--hidden", type=int, default=256)
    p.add_argument("--depth", type=int, default=3)
    p.add_argument("--dropout", type=float, default=0.1)

    args = p.parse_args()
    cfg = TrainConfig(
        data=args.data,
        outdir=args.outdir,
        epochs=args.epochs,
        batch=args.batch,
        lr=args.lr,
        weight_decay=args.weight_decay,
        seed=args.seed,
        device=args.device,
        num_workers=args.num_workers,
        pin_memory=args.pin_memory,
        d_model=args.d_model,
        hidden=args.hidden,
        depth=args.depth,
        dropout=args.dropout,
    )
    # Choose best metric automatically
    cfg.best_metric = "val_solved_rate"
    cfg.maximize_best_metric = True
    return cfg


def main():
    cfg = parse_args()
    os.makedirs(cfg.outdir, exist_ok=True)

    set_seed(cfg.seed)
    device = resolve_device(cfg.device)
    print(f"[INFO] device = {device}")

    # Load dataset
    data = np.load(cfg.data)
    x_train = data["x_train"]
    y_train = data["y_train"]
    fixed_train = data["fixed_mask_train"]

    x_val = data["x_val"]
    y_val = data["y_val"]
    fixed_val = data["fixed_mask_val"]

    train_ds = QueensNPZDataset(x_train, y_train, fixed_train)
    val_ds = QueensNPZDataset(x_val, y_val, fixed_val)

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg.batch,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory and device.type == "cuda",
        drop_last=False,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg.batch,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=cfg.pin_memory and device.type == "cuda",
        drop_last=False,
    )

    # Model
    model = QueensBaseline(
        d_model=cfg.d_model,
        hidden=cfg.hidden,
        depth=cfg.depth,
        dropout=cfg.dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay
    )

    history = []
    best_value = -1e9 if cfg.maximize_best_metric else 1e9
    best_epoch = -1
    best_path = os.path.join(cfg.outdir, "best.pt")

    start_time = time.time()
    print("[INFO] Starting training...")

    for epoch in range(1, cfg.epochs + 1):
        model.train()
        epoch_loss = 0.0
        n_batches = 0

        t0 = time.time()
        for x, y, fixed_mask in train_loader:
            x = x.to(device)
            y = y.to(device)
            fixed_mask = fixed_mask.to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(x)  # (B,8,8)

            loss = masked_ce_loss(logits, y, fixed_mask)
            loss.backward()
            optimizer.step()

            epoch_loss += float(loss.item())
            n_batches += 1

        train_loss = epoch_loss / max(1, n_batches)

        # Validation
        val_metrics = evaluate(model, val_loader, device=device)

        # Decide if best
        val_solved = val_metrics["solved_rate"]
        val_conf_mean = val_metrics["conflicts_mean"]
        metric_value = (
            val_solved if cfg.best_metric == "val_solved_rate" else val_conf_mean
        )

        is_better = (
            metric_value > best_value
            if cfg.maximize_best_metric
            else metric_value < best_value
        )
        if is_better:
            best_value = metric_value
            best_epoch = epoch
            # Save checkpoint
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "config": asdict(cfg),
                    "epoch": epoch,
                    "best_metric": cfg.best_metric,
                    "best_value": best_value,
                },
                best_path,
            )

        dt = time.time() - t0

        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_solved_rate": float(val_solved),
            "val_conflicts_mean": float(val_conf_mean),
            "val_conflicts_median": float(val_metrics["conflicts_median"]),
            "epoch_time_sec": dt,
            "is_best": bool(is_better),
        }
        history.append(row)

        print(
            f"[E{epoch:03d}] loss={train_loss:.4f} | "
            f"val_solved={val_solved:.4f} | val_conf_mean={val_conf_mean:.3f} | "
            f"time={dt:.1f}s {'<BEST>' if is_better else ''}"
        )

    total_time = time.time() - start_time
    print(f"[INFO] Training finished in {total_time:.1f}s")
    print(
        f"[INFO] Best epoch = {best_epoch}, best_value({cfg.best_metric}) = {best_value:.6f}"
    )
    print(f"[INFO] Saved best checkpoint to: {best_path}")

    # Write logs
    log = {
        "config": asdict(cfg),
        "device": str(device),
        "best_epoch": best_epoch,
        "best_metric": cfg.best_metric,
        "best_value": float(best_value),
        "history": history,
        "total_time_sec": float(total_time),
    }
    log_path = os.path.join(cfg.outdir, "train_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    print(f"[INFO] Saved training log to: {log_path}")


if __name__ == "__main__":
    main()
