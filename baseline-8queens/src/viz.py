from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Any, List, Tuple

import matplotlib.pyplot as plt


def parse_args():
    p = argparse.ArgumentParser(
        description="Visualize eval metrics for 8-Queens baseline."
    )
    p.add_argument(
        "--eval", type=str, default="outputs/eval.json", help="Path to eval.json"
    )
    p.add_argument(
        "--outdir", type=str, default="outputs", help="Output directory for PNGs"
    )
    return p.parse_args()


def _sorted_kv(d: Dict[str, Any]) -> List[Tuple[int, float]]:
    """
    Convert dict with string keys ("2","3",...) to sorted list of (int_k, float_value).
    Ignore None values.
    """
    out = []
    for k_str, v in d.items():
        try:
            k_int = int(k_str)
        except ValueError:
            continue
        if v is None:
            continue
        out.append((k_int, float(v)))
    out.sort(key=lambda x: x[0])
    return out


def plot_solved_rate_by_fixed(results: Dict[str, Any], outpath: str):
    by_k = results.get("by_k_fixed", {})
    counts = results.get("by_k_fixed_counts", {})

    kv = _sorted_kv(by_k)
    if not kv:
        raise ValueError("No 'by_k_fixed' data found in eval.json")

    ks = [k for k, _ in kv]
    rates = [v for _, v in kv]
    ncounts = [int(counts.get(str(k), 0)) for k in ks]

    plt.figure(figsize=(8, 4.5))
    plt.plot(ks, rates, marker="o")
    plt.title("Solved rate vs nombre de reines fixées (k_fixed)")
    plt.xlabel("k_fixed (lignes déjà fixées)")
    plt.ylabel("Solved rate (fraction solutions valides)")
    plt.xticks(ks)

    # annotate counts
    for k, r, n in zip(ks, rates, ncounts):
        plt.annotate(
            f"n={n}",
            (k, r),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8,
        )

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath, dpi=160)
    plt.close()


def plot_conflicts(results: Dict[str, Any], outpath: str):
    """
    If eval.json contains a list of per-sample conflicts (key 'conflicts'), plot histogram.
    Otherwise plot mean conflicts by k_fixed (bar chart).
    """
    # Case A: if we have full list of conflicts, do histogram
    conflicts_list = results.get("conflicts", None)
    if isinstance(conflicts_list, list) and len(conflicts_list) > 0:
        plt.figure(figsize=(8, 4.5))
        plt.hist(
            conflicts_list,
            bins=range(0, max(conflicts_list) + 2),
            edgecolor="black",
            alpha=0.85,
        )
        plt.title("Histogramme des conflits (paires en conflit)")
        plt.xlabel("Nombre de conflits")
        plt.ylabel("Nombre d'exemples")
        plt.grid(True, alpha=0.25, axis="y")
        plt.tight_layout()
        plt.savefig(outpath, dpi=160)
        plt.close()
        return

    # Case B: default -> mean conflicts by k_fixed
    by_k_conf = results.get("conflicts_mean_by_k_fixed", {})
    counts = results.get("by_k_fixed_counts", {})

    kv = _sorted_kv(by_k_conf)
    if not kv:
        # fallback to overall only
        overall = results.get("overall", {})
        mean_conf = overall.get("conflicts_mean", None)
        if mean_conf is None:
            raise ValueError("No conflicts info found in eval.json")
        plt.figure(figsize=(6, 4))
        plt.bar([0], [float(mean_conf)])
        plt.title("Conflits moyens (global)")
        plt.ylabel("Conflits moyens")
        plt.xticks([0], ["global"])
        plt.tight_layout()
        plt.savefig(outpath, dpi=160)
        plt.close()
        return

    ks = [k for k, _ in kv]
    means = [v for _, v in kv]
    ncounts = [int(counts.get(str(k), 0)) for k in ks]

    plt.figure(figsize=(8, 4.5))
    plt.bar(ks, means, alpha=0.9)
    plt.title("Conflits moyens vs nombre de reines fixées (k_fixed)")
    plt.xlabel("k_fixed (lignes déjà fixées)")
    plt.ylabel("Conflits moyens (paires en conflit)")
    plt.xticks(ks)

    # annotate counts
    for k, m, n in zip(ks, means, ncounts):
        plt.annotate(
            f"n={n}",
            (k, m),
            textcoords="offset points",
            xytext=(0, 5),
            ha="center",
            fontsize=8,
        )

    plt.grid(True, alpha=0.25, axis="y")
    plt.tight_layout()
    plt.savefig(outpath, dpi=160)
    plt.close()


def main():
    args = parse_args()
