#!/usr/bin/env python3
"""Python vs Rust kernel benchmark."""

from __future__ import annotations

import time
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from compute_kernel import block_max  # noqa: E402

def main() -> None:
    v = np.ascontiguousarray(np.sin(np.arange(10000) * 0.01)); p = 7
    t0 = time.perf_counter()
    for _ in range(200):
        block_max(v, p)
    py_s = time.perf_counter() - t0
    try:
        import analyzing_the_2013_colorado_flood_using_time_series_analysis_rs as rs
    except ImportError:
        print("Build: maturin develop --release -m rust/py/Cargo.toml")
        print(f"Python {py_s:.3f}s")
        return
    rs_s = rs.bench_kernel_py(v, p, 2000)
    print(f"Python {py_s:.3f}s Rust {rs_s:.3f}s speedup {py_s / max(rs_s, 1e-9):.1f}x")
    np.testing.assert_allclose(block_max(v, p), np.asarray(rs.block_max_py(v, p)), rtol=1e-10)
    print("Correctness: OK")

if __name__ == "__main__":
    main()
