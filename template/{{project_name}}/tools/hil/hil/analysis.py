"""Reusable signal-processing assertions for HIL tests."""
from __future__ import annotations

import numpy as np


def rise_time(trace: np.ndarray, sample_rate: float,
              low_frac: float = 0.1, high_frac: float = 0.9) -> float:
    lo, hi = trace.min(), trace.max()
    low_t = lo + (hi - lo) * low_frac
    high_t = lo + (hi - lo) * high_frac
    i_lo = int(np.argmax(trace >= low_t))
    i_hi = int(np.argmax(trace >= high_t))
    return (i_hi - i_lo) / sample_rate


def overshoot_pct(trace: np.ndarray, target: float) -> float:
    peak = float(trace.max())
    return 100.0 * (peak - target) / target if target else 0.0


def settling_time(trace: np.ndarray, target: float,
                  tolerance: float, sample_rate: float) -> float:
    mask = np.abs(trace - target) > tolerance
    idx = np.where(mask)[0]
    return (int(idx[-1]) / sample_rate) if len(idx) else 0.0


def mean_current_ua(samples_ua: np.ndarray, settle_frac: float = 0.2) -> float:
    start = int(settle_frac * len(samples_ua))
    return float(samples_ua[start:].mean())
