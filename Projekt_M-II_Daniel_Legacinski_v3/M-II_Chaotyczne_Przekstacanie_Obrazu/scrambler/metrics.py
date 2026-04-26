from __future__ import annotations
import numpy as np


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(np.float64).ravel()
    b = b.astype(np.float64).ravel()
    if a.size < 2 or np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def neighbor_correlation(arr: np.ndarray) -> dict:
    """Korelacja sasiadujacych pikseli: poziomo, pionowo i ukosnie."""
    arr = arr.astype(np.float64)
    result = {}
    names = ["R", "G", "B"]
    for ch, name in enumerate(names):
        channel = arr[:, :, ch]
        result[f"horizontal_{name}"] = _corr(channel[:, :-1], channel[:, 1:])
        result[f"vertical_{name}"] = _corr(channel[:-1, :], channel[1:, :])
        result[f"diagonal_{name}"] = _corr(channel[:-1, :-1], channel[1:, 1:])
    result["horizontal_avg"] = float(np.mean([result[f"horizontal_{x}"] for x in names]))
    result["vertical_avg"] = float(np.mean([result[f"vertical_{x}"] for x in names]))
    result["diagonal_avg"] = float(np.mean([result[f"diagonal_{x}"] for x in names]))
    return result


def compare_images(a: np.ndarray, b: np.ndarray) -> dict:
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    diff = a - b
    mse = float(np.mean(diff ** 2))
    mae = float(np.mean(np.abs(diff)))
    max_diff = int(np.max(np.abs(diff)))
    identical = bool(np.array_equal(a.astype(np.uint8), b.astype(np.uint8)))
    psnr = float("inf") if mse == 0 else float(20 * np.log10(255.0 / np.sqrt(mse)))
    return {"identical": identical, "mse": mse, "mae": mae, "max_diff": max_diff, "psnr": psnr}


def metrics_summary(original: np.ndarray, scrambled: np.ndarray, restored: np.ndarray, wrong_restored: np.ndarray | None = None) -> dict:
    before = neighbor_correlation(original)
    after = neighbor_correlation(scrambled)
    ok = compare_images(original, restored)
    summary = {
        "corr_original_horizontal": before["horizontal_avg"],
        "corr_scrambled_horizontal": after["horizontal_avg"],
        "corr_original_vertical": before["vertical_avg"],
        "corr_scrambled_vertical": after["vertical_avg"],
        "restore_identical": ok["identical"],
        "restore_mse": ok["mse"],
        "restore_mae": ok["mae"],
        "restore_max_diff": ok["max_diff"],
    }
    if wrong_restored is not None:
        wrong = compare_images(original, wrong_restored)
        summary.update({
            "wrong_key_mse": wrong["mse"],
            "wrong_key_mae": wrong["mae"],
            "wrong_key_max_diff": wrong["max_diff"],
        })
    return summary
