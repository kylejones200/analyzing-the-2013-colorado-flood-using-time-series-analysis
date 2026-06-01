"""Block maximum aggregation."""

from __future__ import annotations

import numpy as np


def block_max(values: np.ndarray, period: int) -> np.ndarray:
    v = np.asarray(values, dtype=float)
    if period <= 0 or len(v) == 0:
        return np.empty(0, dtype=float)
    n_blocks = int(np.ceil(len(v) / period))
    out = np.empty(n_blocks, dtype=float)
    for b in range(n_blocks):
        sl = v[b * period : (b + 1) * period]
        out[b] = sl.max()
    return out
