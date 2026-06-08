"""Reference FVE metric + synthetic phantom self-check.

FVE (fraction of variance explained) is the round-trip fidelity used to validate
a Natural Language Autoencoder: how much of the variance in the original
activations the reconstruction recovers.

    FVE = 1 - E||x - x_hat||^2 / E||x - mean(x)||^2

This module pins the definition and validates the implementation against
synthetic activations with an analytically known FVE — calibrate the instrument
on a known answer before running it on real model activations. Runs locally,
no GPU:  `python eval/fve.py`.
"""
from __future__ import annotations

import numpy as np


def fve(original: np.ndarray, reconstructed: np.ndarray) -> float:
    """Fraction of variance explained over a batch of activation vectors.

    original, reconstructed: arrays of shape (n_samples, d_model).
    Returns 1.0 for perfect reconstruction, ~0.0 for predicting the mean.
    """
    original = np.asarray(original, dtype=np.float64)
    reconstructed = np.asarray(reconstructed, dtype=np.float64)
    if original.shape != reconstructed.shape:
        raise ValueError(f"shape mismatch: {original.shape} vs {reconstructed.shape}")
    ss_res = np.mean(np.sum((original - reconstructed) ** 2, axis=1))
    ss_tot = np.mean(np.sum((original - original.mean(axis=0)) ** 2, axis=1))
    if ss_tot == 0:
        raise ValueError("zero variance in original activations")
    return 1.0 - ss_res / ss_tot


def synthetic_phantom(
    target_fve: float, n: int, d: int, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    """(original, reconstructed) with an analytically known FVE.

    For standard-normal x, E||x - mean||^2 -> d. Adding noise eps = c * N(0,1)
    gives E||eps||^2 = c^2 * d, so FVE -> 1 - c^2. Set c = sqrt(1 - target_fve).
    """
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, d))
    c = np.sqrt(max(0.0, 1.0 - target_fve))
    x_hat = x + c * rng.standard_normal((n, d))
    return x, x_hat


def _self_check() -> None:
    n, d = 4000, 64
    for target in (1.0, 0.7, 0.3, 0.0):
        x, x_hat = synthetic_phantom(target, n, d, seed=0)
        got = fve(x, x_hat)
        assert abs(got - target) < 0.03, f"target {target}, got {got:.3f}"
        print(f"  target FVE {target:.2f}  ->  measured {got:.3f}   OK")
    x, _ = synthetic_phantom(1.0, n, d, seed=1)
    assert abs(fve(x, x) - 1.0) < 1e-9
    mean_pred = np.broadcast_to(x.mean(axis=0), x.shape)
    assert abs(fve(x, mean_pred)) < 0.02
    print("  perfect reconstruction -> 1.0,  mean predictor -> ~0.0   OK")


if __name__ == "__main__":
    print("FVE phantom self-check:")
    _self_check()
    print("all checks passed")
