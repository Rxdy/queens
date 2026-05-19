from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, Any

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from .model import QueensBaseline, apply_fixed_constraints
from .metrics import count_conflicts, is_valid_solution


class QueensNPZDataset(Dataset):
    """
    Wrap test arrays from .npz:
      x: (N,8) int {-1..7}
      y: (N,8) int {0..7} (not mandatory for eval metrics, but present)
      fixed_mask: (N,8) bool
      k_fixed: (N,) int
    """

    def __init__(
        self, x: np.ndarray, y: np.ndarray, fixed_mask: np.ndarray, k_fixed: np.ndarray
    ):
        self.x = x.astype(np.int64, copy=False)
        self.y = y.astype(np.int64, copy=False)
        self.fixed_mask = fixed_mask.astype(bool, copy=False)
        self.k_fixed = k_fixed.astype(np.int64, copy=False)

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, idx: int):
        return (
            torch.from_numpy(self.x[idx]).long(),  # (8,)
            torch.from_numpy(self.y[idx]).long(),  # (8,)
            torch.from_numpy(self.fixed_mask[idx]).bool(),  # (8,)
            int(self.k_fixed[idx]),  # scalar
        )


def resolve_device(device: str) -> torch.device:
    if device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device == "cuda":
        return torch.device("cuda")
    return torch.device("cpu")


def parse_args():
    p = argparse.ArgumentParser(
        description="Evaluate baseline 8-Queens model on test split."
    )
    p.add_argument(
        "--data", type=str, default="outputs/dataset.npz", help="Path to dataset .npz"
    )
    p.add_argument(
        "--ckpt", type=str, default="outputs/best.pt", help="Path to checkpoint .pt"
    )
    p.add_argument(
        "--out", type=str, default="outputs/eval.json", help="Output JSON path"
    )
    p.add_argument("--batch", type=int, default=512, help="Batch size for evaluation")
    p.add_argument(
        "--device", type=str, default="auto", choices=["auto", "cpu", "cuda"]
    )
    p.add_argument("--num_workers", type=int, default=0)
    p.add_argument(
        "--pin_memory", action="store_true", help="Pin memory (useful on GPU)"
    )
    p.add_argument("--no-pin_memory", dest="pin_memory", action="store_false")
    p.set_defaults(pin_memory=True)
    return p.parse_args()


@torch.no_grad()
def run_eval(
    model: QueensBaseline, loader: DataLoader, device: torch.device
) -> Dict[str, Any]:
    model.eval()

    all_preds = []
    all_k = []

    # timing (rough)
    t_start = time.time()
    n_samples = 0

    for x, y, fixed_mask, k_fixed in loader:
        x = x.to(device)

        logits = model(x)  # (B,8,8)
        logits = apply_fixed_constraints(logits, x)  # enforce fixed rows
        pred = torch.argmax(logits, dim=-1)  # (B,8)

        pred_np = pred.detach().cpu().numpy().astype(int)
        all_preds.append(pred_np)

        # k_fixed from dataset (python ints); stack
        all_k.append(np.array(k_fixed, dtype=int))

        n_samples += pred_np.shape[0]

    t_total = time.time() - t_start

    preds = np.concatenate(all_preds, axis=0)  # (N,8)
    k_arr = np.concatenate(all_k, axis=0)  # (N,)

    # Metrics
    conflicts = count_conflicts(preds)  # (N,)
    valid = is_valid_solution(preds).astype(bool)  # (N,)

    overall = {
        "n_samples": int(preds.shape[0]),
        "solved_rate": float(valid.mean()),
        "conflicts_mean": float(np.mean(conflicts)),
        "conflicts_median": float(np.median(conflicts)),
        "conflicts_min": int(np.min(conflicts)),
        "conflicts_max": int(np.max(conflicts)),
        "inference_time_sec": float(t_total),
        "inference_samples_per_sec": float(n_samples / max(t_total, 1e-9)),
    }

    # Solved rate by number of fixed rows
    per_k = {}
    counts_per_k = {}
    unique_k = np.unique(k_arr)
    for k in unique_k:
        mask = k_arr == k
        counts_per_k[int(k)] = int(mask.sum())
        if mask.sum() > 0:
            per_k[int(k)] = float(valid[mask].mean())
        else:
            per_k[int(k)] = None

    # Also conflicts by k (mean)
    conflicts_by_k = {}
    for k in unique_k:
        mask = k_arr == k
        if mask.sum() > 0:
            conflicts_by_k[int(k)] = float(np.mean(conflicts[mask]))
        else:
            conflicts_by_k[int(k)] = None

    return {
        "overall": overall,
        "by_k_fixed": {str(k): v for k, v in sorted(per_k.items(), key=lambda x: x[0])},
        "by_k_fixed_counts": {
            str(k): v for k, v in sorted(counts_per_k.items(), key=lambda x: x[0])
        },
        "conflicts_mean_by_k_fixed": {
            str(k): v for k, v in sorted(conflicts_by_k.items(), key=lambda x: x[0])
        },
    }


def main():
    args = parse_args()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    device = resolve_device(args.device)
    print(f"[INFO] device = {device}")

    # Load dataset
    data = np.load(args.data)
    x_test = data["x_test"]
    y_test = data["y_test"]
    fixed_test = data["fixed_mask_test"]
    # k_fixed is stored by our generator
    if "k_fixed_test" in data:
        k_fixed_test = data["k_fixed_test"]
    else:
        # fallback if missing: compute from fixed mask
        k_fixed_test = fixed_test.sum(axis=1).astype(np.int64)

    test_ds = QueensNPZDataset(x_test, y_test, fixed_test, k_fixed_test)
    test_loader = DataLoader(
        test_ds,
        batch_size=args.batch,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=args.pin_memory and device.type == "cuda",
        drop_last=False,
    )

    # Load checkpoint
    ckpt = torch.load(args.ckpt, map_location="cpu")
    cfg = ckpt.get("config", {})

    model = QueensBaseline(
        d_model=int(cfg.get("d_model", 64)),
        hidden=int(cfg.get("hidden", 256)),
        depth=int(cfg.get("depth", 3)),
        dropout=float(cfg.get("dropout", 0.1)),
    ).to(device)

    model.load_state_dict(ckpt["model_state"], strict=True)

    results = run_eval(model, test_loader, device=device)

    # add metadata
    results["meta"] = {
        "data": args.data,
        "ckpt": args.ckpt,
        "device": str(device),
        "batch": int(args.batch),
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"[INFO] Saved eval results to: {args.out}")
    print("[INFO] Overall:")
    for k, v in results["overall"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
