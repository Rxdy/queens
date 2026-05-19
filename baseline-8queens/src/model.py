from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class QueensBaseline(nn.Module):
    """
    Baseline one-shot model for N-Queens completion (supports any grid size).

    Input:
      x: LongTensor (B, n) with values in {-1,0..n-1}
         -1 means "unknown row", 0..n-1 is the fixed column for that row.

    Output:
      logits: FloatTensor (B, n, n)
         logits[b, r, c] = score that row r has queen at column c.
    """

    def __init__(
        self,
        n: int = 8,
        d_model: int = 64,
        hidden: int = 256,
        depth: int = 3,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.n = n
        self.unknown_token = n  # we map -1 -> n
        vocab_size = n + 1  # columns 0..n-1 + unknown token

        # Embedding of the partial assignment per row (fixed col or unknown)
        self.val_emb = nn.Embedding(vocab_size, d_model)

        # Row positional embedding (row 0..n-1)
        self.row_emb = nn.Embedding(self.n, d_model)

        # Optional embedding for "is fixed?" flag (2 tokens: not fixed / fixed)
        self.fixed_emb = nn.Embedding(2, d_model)

        layers = []
        in_dim = self.n * d_model
        for i in range(depth):
            layers.append(nn.Linear(in_dim if i == 0 else hidden, hidden))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
        self.mlp = nn.Sequential(*layers)

        # Head to produce n×n logits
        self.head = nn.Linear(hidden, self.n * self.n)

        # init a little nicer
        nn.init.normal_(self.val_emb.weight, std=0.02)
        nn.init.normal_(self.row_emb.weight, std=0.02)
        nn.init.normal_(self.fixed_emb.weight, std=0.02)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (B, n) long with -1..n-1
        Returns: features (B, n*d_model)
        """
        if x.dtype != torch.long:
            x = x.long()

        # fixed mask
        fixed_mask = x != -1  # (B, n) bool
        fixed_token = fixed_mask.long()  # (B, n) in {0,1}

        # map -1 -> unknown_token (n), keep 0..n-1
        x_idx = x.clone()
        x_idx[x_idx == -1] = self.unknown_token  # now in 0..n

        # embeddings per row
        v = self.val_emb(x_idx)  # (B, n, d_model)

        rows = torch.arange(self.n, device=x.device).unsqueeze(0).expand(x.shape[0], -1)
        r = self.row_emb(rows)  # (B, n, d_model)

        f = self.fixed_emb(fixed_token)  # (B, n, d_model)

        # Combine and flatten
        h = v + r + f  # (B, n, d_model)
        h = h.reshape(x.shape[0], -1)  # (B, n*d_model)
        return h

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass (one-shot).
        """
        h = self.encode(x)  # (B, n*d_model)
        h = self.mlp(h)  # (B, hidden)
        logits = self.head(h).reshape(-1, self.n, self.n)  # (B, n, n)
        return logits

    @torch.no_grad()
    def predict(self, x: torch.Tensor, enforce_fixed: bool = True) -> torch.Tensor:
        """
        Returns predicted columns per row: (B, n) in 0..n-1
        If enforce_fixed=True, rows already fixed in x will be forced to that value.
        """
        logits = self.forward(x)  # (B, n, n)
        if enforce_fixed:
            logits = apply_fixed_constraints(logits, x)
        pred = torch.argmax(logits, dim=-1)  # (B, n)
        return pred


def apply_fixed_constraints(logits: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
    """
    Enforce fixed rows from x into logits by setting logits to -inf
    for columns that do not match the fixed column.

    logits: (B, n, n)
    x:      (B, n) values -1..n-1

    Returns new logits (same shape).
    """
    if x.dtype != torch.long:
        x = x.long()

    out = logits.clone()
    fixed_mask = x != -1  # (B, n)

    if fixed_mask.any():
        # For each fixed (b,r), keep only column x[b,r]
        b_idx, r_idx = torch.where(fixed_mask)
        fixed_cols = x[b_idx, r_idx]  # (K,)

        # set all columns to -inf
        out[b_idx, r_idx, :] = float("-inf")
        # restore fixed column to original value
        out[b_idx, r_idx, fixed_cols] = logits[b_idx, r_idx, fixed_cols]
    return out


def masked_ce_loss(
    logits: torch.Tensor, y: torch.Tensor, fixed_mask: torch.Tensor
) -> torch.Tensor:
    """
    Cross-entropy loss computed only on non-fixed rows.
    - logits: (B, n, n)
    - y:      (B, n) target columns in 0..n-1
    - fixed_mask: (B, n) bool where True = fixed in input, so we IGNORE those rows

    Returns: scalar loss
    """
    # We want mask of rows to TRAIN on = not fixed
    train_mask = ~fixed_mask  # (B, n)
    if train_mask.sum() == 0:
        # edge case: all rows fixed (rare), return zero
        return logits.sum() * 0.0

    # Flatten rows
    B, n = logits.shape[0], logits.shape[1]
    logits_flat = logits.reshape(B * n, n)
    y_flat = y.reshape(B * n)
    train_mask_flat = train_mask.reshape(B * n)

    # Select only rows to train
    logits_sel = logits_flat[train_mask_flat]
    y_sel = y_flat[train_mask_flat]

    return F.cross_entropy(logits_sel, y_sel)


if __name__ == "__main__":
    # Quick sanity check
    model = QueensBaseline()
    x = torch.tensor([[-1, -1, 3, -1, -1, -1, 1, -1]], dtype=torch.long)  # one example
    logits = model(x)
    print("logits shape:", logits.shape)  # (1,8,8)
    pred = model.predict(x)
    print("pred:", pred)
