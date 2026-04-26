from pathlib import Path
from PIL import Image
from run_gui import make_sample_images
from scrambler.algorithms import scramble_image, unscramble_image, pil_to_array
import numpy as np


def test_all_stages():
    paths = make_sample_images()
    for path in paths:
        img = Image.open(path).convert("RGB")
        for stage in [1, 2, 3]:
            scr = scramble_image(img, stage, "Daniel-2026", 7, 2)
            rec = unscramble_image(scr, stage, "Daniel-2026", 7, 2)
            assert np.array_equal(pil_to_array(img), pil_to_array(rec)), f"Blad odwracalnosci: {path}, etap {stage}"
    print("OK - wszystkie etapy sa odwracalne przy poprawnym kluczu.")

if __name__ == "__main__":
    test_all_stages()
