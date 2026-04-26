"""
Projekt M-II - Chaotyczne przeksztalcanie obrazu cyfrowego
Autor: Daniel Legacinski

Ten plik zawiera trzy etapy algorytmow:
Etap 1 - naiwny scrambling przez cykliczne przesuniecia wierszy.
Etap 2 - czysta permutacja pikseli Fisher-Yates sterowana kluczem.
Etap 3 - hybryda: permutacja + odwracalna substytucja modulo 256.

UWAGA: To NIE jest kryptografia. To projekt dydaktyczny.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from PIL import Image


@dataclass
class Metrics:
    corr_h_before: float
    corr_h_after: float
    corr_v_before: float
    corr_v_after: float
    mae_wrong_key: float
    mse_wrong_key: float
    exact_restored: bool


def image_to_array(img: Image.Image) -> np.ndarray:
    """Konwertuje obraz do RGB i tablicy uint8: H x W x 3."""
    return np.asarray(img.convert("RGB"), dtype=np.uint8)


def array_to_image(arr: np.ndarray) -> Image.Image:
    """Konwertuje tablice uint8 do obrazu PIL RGB."""
    arr = np.asarray(arr, dtype=np.uint8)
    return Image.fromarray(arr, mode="RGB")


def key_to_seed(key: str, extra: str = "") -> int:
    """Zamienia tekstowy klucz na stabilny seed 32-bitowy."""
    data = (str(key) + "|" + str(extra)).encode("utf-8")
    digest = hashlib.sha256(data).digest()
    return int.from_bytes(digest[:4], "little", signed=False)


class LCG:
    """Prosty generator pseudolosowy LCG. Nie jest bezpieczny kryptograficznie."""
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        # Parametry jak w Numerical Recipes, modulo 2^32.
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def randint(self, upper_inclusive: int) -> int:
        if upper_inclusive <= 0:
            return 0
        return self.next_u32() % (upper_inclusive + 1)


def fisher_yates_permutation(n: int, key: str, stage: str = "stage2") -> np.ndarray:
    """
    Tworzy permutacje P zbioru {0,...,N-1} algorytmem Fisher-Yates.
    P jest jednoznacznie odtwarzalna z tego samego klucza.
    """
    perm = np.arange(n, dtype=np.int64)
    rng = LCG(key_to_seed(key, stage))
    for i in range(n - 1, 0, -1):
        j = rng.randint(i)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def inverse_permutation(perm: np.ndarray) -> np.ndarray:
    inv = np.empty_like(perm)
    inv[perm] = np.arange(len(perm), dtype=perm.dtype)
    return inv


def stage1_scramble(arr: np.ndarray, key: str, strength: int = 1) -> np.ndarray:
    """Etap 1: naiwne cykliczne przesuniecia kazdego wiersza obrazu."""
    h, w, _ = arr.shape
    base = key_to_seed(key, "stage1") % max(w, 1)
    out = np.empty_like(arr)
    strength = max(1, int(strength))
    for y in range(h):
        shift = int((base + y * strength) % w)
        out[y] = np.roll(arr[y], shift=shift, axis=0)
    return out


def stage1_unscramble(arr: np.ndarray, key: str, strength: int = 1) -> np.ndarray:
    h, w, _ = arr.shape
    base = key_to_seed(key, "stage1") % max(w, 1)
    out = np.empty_like(arr)
    strength = max(1, int(strength))
    for y in range(h):
        shift = int((base + y * strength) % w)
        out[y] = np.roll(arr[y], shift=-shift, axis=0)
    return out


def stage2_scramble(arr: np.ndarray, key: str, block_size: int = 1) -> np.ndarray:
    """Etap 2: czysta permutacja pikseli. Wartosci pikseli nie sa zmieniane."""
    flat = arr.reshape(-1, arr.shape[2])
    perm = fisher_yates_permutation(flat.shape[0], key, "stage2")
    out = flat[perm].reshape(arr.shape)
    return out.astype(np.uint8)


def stage2_unscramble(arr: np.ndarray, key: str, block_size: int = 1) -> np.ndarray:
    flat = arr.reshape(-1, arr.shape[2])
    perm = fisher_yates_permutation(flat.shape[0], key, "stage2")
    inv = inverse_permutation(perm)
    out = flat[inv].reshape(arr.shape)
    return out.astype(np.uint8)


def lcg_mask(shape: Tuple[int, ...], key: str, stage: str = "stage3mask") -> np.ndarray:
    """Tworzy maske bajtowa 0..255 deterministycznie z klucza."""
    total = int(np.prod(shape))
    rng = LCG(key_to_seed(key, stage))
    data = np.empty(total, dtype=np.uint8)
    for i in range(total):
        data[i] = rng.next_u32() & 0xFF
    return data.reshape(shape)


def stage3_scramble(arr: np.ndarray, key: str, intensity: int = 1) -> np.ndarray:
    """Etap 3: hybryda. Najpierw permutacja, potem substytucja modulo 256."""
    permuted = stage2_scramble(arr, key + "|perm3")
    mask = lcg_mask(permuted.shape, key + f"|intensity={intensity}")
    out = (permuted.astype(np.uint16) + mask.astype(np.uint16)) % 256
    return out.astype(np.uint8)


def stage3_unscramble(arr: np.ndarray, key: str, intensity: int = 1) -> np.ndarray:
    """Algorytm odwrotny etapu 3: najpierw odjecie maski, potem odwrotna permutacja."""
    mask = lcg_mask(arr.shape, key + f"|intensity={intensity}")
    unmasked = (arr.astype(np.int16) - mask.astype(np.int16)) % 256
    restored = stage2_unscramble(unmasked.astype(np.uint8), key + "|perm3")
    return restored.astype(np.uint8)


def scramble(arr: np.ndarray, stage: int, key: str, param: int = 1) -> np.ndarray:
    if stage == 1:
        return stage1_scramble(arr, key, param)
    if stage == 2:
        return stage2_scramble(arr, key, param)
    if stage == 3:
        return stage3_scramble(arr, key, param)
    raise ValueError("Nieznany etap. Wybierz 1, 2 albo 3.")


def unscramble(arr: np.ndarray, stage: int, key: str, param: int = 1) -> np.ndarray:
    if stage == 1:
        return stage1_unscramble(arr, key, param)
    if stage == 2:
        return stage2_unscramble(arr, key, param)
    if stage == 3:
        return stage3_unscramble(arr, key, param)
    raise ValueError("Nieznany etap. Wybierz 1, 2 albo 3.")


def grayscale(arr: np.ndarray) -> np.ndarray:
    return (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.float64)


def adjacent_correlation(arr: np.ndarray, direction: str = "horizontal") -> float:
    """Korelacja sasiednich pikseli w skali szarosci."""
    g = grayscale(arr)
    if direction == "horizontal":
        a = g[:, :-1].ravel()
        b = g[:, 1:].ravel()
    else:
        a = g[:-1, :].ravel()
        b = g[1:, :].ravel()
    if a.size < 2 or np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def diff_stats(a: np.ndarray, b: np.ndarray) -> Tuple[float, float]:
    d = a.astype(np.float64) - b.astype(np.float64)
    return float(np.mean(np.abs(d))), float(np.mean(d * d))


def run_metrics(original: np.ndarray, scrambled: np.ndarray, restored: np.ndarray, stage: int, key: str, wrong_key: str, param: int) -> Metrics:
    wrong_restored = unscramble(scrambled, stage, wrong_key, param)
    mae, mse = diff_stats(original, wrong_restored)
    return Metrics(
        corr_h_before=adjacent_correlation(original, "horizontal"),
        corr_h_after=adjacent_correlation(scrambled, "horizontal"),
        corr_v_before=adjacent_correlation(original, "vertical"),
        corr_v_after=adjacent_correlation(scrambled, "vertical"),
        mae_wrong_key=mae,
        mse_wrong_key=mse,
        exact_restored=bool(np.array_equal(original, restored)),
    )
