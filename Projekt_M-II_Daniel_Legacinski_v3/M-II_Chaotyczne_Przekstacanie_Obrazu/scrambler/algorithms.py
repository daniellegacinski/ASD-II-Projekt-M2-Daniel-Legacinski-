"""
Projekt M-II: Chaotyczne przeksztalcanie obrazu cyfrowego.
Autor: Daniel Legacinski

UWAGA: to nie jest szyfr kryptograficzny. Kod sluzy do eksperymentow dydaktycznych.
"""
from __future__ import annotations
import numpy as np
from PIL import Image

MOD32 = 2 ** 32


def key_to_seed(key: str, parameter: int = 0) -> int:
    """Prosta deterministyczna funkcja zamiany klucza tekstowego na seed.
    Nie uzywamy gotowych funkcji kryptograficznych - to tylko seed eksperymentalny.
    """
    if key is None:
        key = ""
    seed = 2166136261  # stala startowa FNV-like, ale implementacja jest jawna i prosta
    for ch in str(key):
        seed = (seed ^ ord(ch)) * 16777619
        seed %= MOD32
    seed = (seed + int(parameter) * 2654435761 + len(str(key)) * 97) % MOD32
    if seed == 0:
        seed = 123456789
    return int(seed)


class LCG:
    """Jawny generator pseudo-losowy LCG. Nie jest bezpieczny kryptograficznie."""
    def __init__(self, seed: int):
        self.state = int(seed) % MOD32
        if self.state == 0:
            self.state = 1

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) % MOD32
        return self.state

    def randint(self, low: int, high: int) -> int:
        # przedzial domkniety [low, high]
        return low + (self.next_u32() % (high - low + 1))


def pil_to_array(image: Image.Image) -> np.ndarray:
    return np.array(image.convert("RGB"), dtype=np.uint8)


def array_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def fisher_yates_permutation(n: int, seed: int) -> np.ndarray:
    """Permutacja Fishera-Yatesa sterowana naszym jawnym LCG."""
    perm = np.arange(n, dtype=np.int64)
    rng = LCG(seed)
    for i in range(n - 1, 0, -1):
        j = rng.randint(0, i)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def keystream(shape: tuple[int, ...], seed: int) -> np.ndarray:
    """Strumien wartosci 0..255 tworzony przez LCG. Jawny, odwracalny jako dodawanie mod 256."""
    total = int(np.prod(shape))
    rng = LCG(seed)
    data = np.empty(total, dtype=np.uint8)
    for i in range(total):
        data[i] = (rng.next_u32() >> 16) & 0xFF
    return data.reshape(shape)


# ---------------- ETAP 1: naiwny scrambling ----------------

def stage1_scramble(arr: np.ndarray, key: str, parameter: int = 7) -> np.ndarray:
    """Naiwne przesuniecia wierszy i kolumn. W pelni odwracalne, ale struktury zostaja widoczne."""
    h, w, _ = arr.shape
    seed = key_to_seed(key, parameter)
    row_base = seed % max(1, w)
    col_base = (seed // 97) % max(1, h)
    step = max(1, int(parameter))

    out = arr.copy()
    for r in range(h):
        out[r] = np.roll(out[r], (row_base + r * step) % w, axis=0)
    for c in range(w):
        out[:, c] = np.roll(out[:, c], (col_base + c * step) % h, axis=0)
    return out.astype(np.uint8)


def stage1_unscramble(arr: np.ndarray, key: str, parameter: int = 7) -> np.ndarray:
    h, w, _ = arr.shape
    seed = key_to_seed(key, parameter)
    row_base = seed % max(1, w)
    col_base = (seed // 97) % max(1, h)
    step = max(1, int(parameter))

    out = arr.copy()
    for c in range(w - 1, -1, -1):
        out[:, c] = np.roll(out[:, c], -((col_base + c * step) % h), axis=0)
    for r in range(h - 1, -1, -1):
        out[r] = np.roll(out[r], -((row_base + r * step) % w), axis=0)
    return out.astype(np.uint8)


# ---------------- ETAP 2: czysta permutacja ----------------

def stage2_scramble(arr: np.ndarray, key: str, parameter: int = 7) -> np.ndarray:
    """Czysta permutacja pikseli. Nie zmienia wartosci pikseli, tylko ich polozenie."""
    h, w, c = arr.shape
    n = h * w
    seed = key_to_seed(key, parameter)
    perm = fisher_yates_permutation(n, seed)
    flat = arr.reshape(n, c)
    out = flat[perm].reshape(h, w, c)
    return out.astype(np.uint8)


def stage2_unscramble(arr: np.ndarray, key: str, parameter: int = 7) -> np.ndarray:
    h, w, c = arr.shape
    n = h * w
    seed = key_to_seed(key, parameter)
    perm = fisher_yates_permutation(n, seed)
    flat = arr.reshape(n, c)
    restored = np.empty_like(flat)
    restored[perm] = flat  # jawna funkcja odwrotna P^{-1}
    return restored.reshape(h, w, c).astype(np.uint8)


# ---------------- ETAP 3: mechanizm wzmacniajacy ----------------

def stage3_scramble(arr: np.ndarray, key: str, parameter: int = 7, rounds: int = 2) -> np.ndarray:
    """Hybryda: permutacja + substytucja modularna.
    Operacja jest odwracalna: najpierw P, potem dodanie strumienia mod 256.
    """
    out = arr.copy().astype(np.uint8)
    rounds = max(1, min(int(rounds), 8))
    for r in range(rounds):
        round_param = int(parameter) + r * 17
        out = stage2_scramble(out, key + f"|round={r}", round_param)
        seed = key_to_seed(key + f"|sub={r}", round_param + 31)
        stream = keystream(out.shape, seed)
        out = ((out.astype(np.uint16) + stream.astype(np.uint16)) % 256).astype(np.uint8)
    return out


def stage3_unscramble(arr: np.ndarray, key: str, parameter: int = 7, rounds: int = 2) -> np.ndarray:
    out = arr.copy().astype(np.uint8)
    rounds = max(1, min(int(rounds), 8))
    for r in range(rounds - 1, -1, -1):
        round_param = int(parameter) + r * 17
        seed = key_to_seed(key + f"|sub={r}", round_param + 31)
        stream = keystream(out.shape, seed)
        out = ((out.astype(np.int16) - stream.astype(np.int16)) % 256).astype(np.uint8)
        out = stage2_unscramble(out, key + f"|round={r}", round_param)
    return out


def scramble_image(image: Image.Image, stage: int, key: str, parameter: int = 7, rounds: int = 2) -> Image.Image:
    arr = pil_to_array(image)
    if int(stage) == 1:
        return array_to_pil(stage1_scramble(arr, key, parameter))
    if int(stage) == 2:
        return array_to_pil(stage2_scramble(arr, key, parameter))
    if int(stage) == 3:
        return array_to_pil(stage3_scramble(arr, key, parameter, rounds))
    raise ValueError("Etap musi miec wartosc 1, 2 albo 3")


def unscramble_image(image: Image.Image, stage: int, key: str, parameter: int = 7, rounds: int = 2) -> Image.Image:
    arr = pil_to_array(image)
    if int(stage) == 1:
        return array_to_pil(stage1_unscramble(arr, key, parameter))
    if int(stage) == 2:
        return array_to_pil(stage2_unscramble(arr, key, parameter))
    if int(stage) == 3:
        return array_to_pil(stage3_unscramble(arr, key, parameter, rounds))
    raise ValueError("Etap musi miec wartosc 1, 2 albo 3")
