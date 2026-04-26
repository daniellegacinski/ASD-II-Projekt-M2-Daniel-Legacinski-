from pathlib import Path
import csv, datetime
from PIL import Image
import matplotlib.pyplot as plt
from run_gui import make_sample_images
from scrambler.algorithms import scramble_image, unscramble_image, pil_to_array
from scrambler.metrics import metrics_summary

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)

def main(key="Daniel-2026", parameter=7, rounds=2):
    natural, structured = make_sample_images()
    folder = OUT / f"experiments_cli_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    folder.mkdir(exist_ok=True)
    rows = []
    for img_path in [natural, structured]:
        img = Image.open(img_path).convert("RGB")
        name = img_path.stem
        img.save(folder / f"{name}_original.png")
        for stage in [1,2,3]:
            scr = scramble_image(img, stage, key, parameter, rounds)
            ok = unscramble_image(scr, stage, key, parameter, rounds)
            wrong = unscramble_image(scr, stage, key + "_blad", parameter, rounds)
            scr.save(folder / f"{name}_stage{stage}_scrambled.png")
            ok.save(folder / f"{name}_stage{stage}_restored_ok.png")
            wrong.save(folder / f"{name}_stage{stage}_restored_wrong_key.png")
            row = metrics_summary(pil_to_array(img), pil_to_array(scr), pil_to_array(ok), pil_to_array(wrong))
            row.update({"image": name, "stage": stage, "key": key, "parameter": parameter, "rounds": rounds})
            rows.append(row)
    with open(folder / "metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    labels = [f"{r['image']} E{r['stage']}" for r in rows]
    values = [r["corr_scrambled_horizontal"] for r in rows]
    plt.figure(figsize=(10,4))
    plt.bar(labels, values)
    plt.ylabel("Korelacja pozioma po scramblingu")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(folder / "correlation_chart.png", dpi=150)
    plt.close()
    print(folder)

if __name__ == "__main__":
    main()
