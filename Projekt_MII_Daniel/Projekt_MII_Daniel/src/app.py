from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import Image, ImageTk, ImageDraw

from algorithms import (
    image_to_array,
    array_to_image,
    scramble,
    unscramble,
    run_metrics,
    diff_stats,
)

APP_TITLE = "Projekt M-II - Chaotyczne przeksztalcanie obrazu cyfrowego"
ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs"
SAMPLE_DIR = ROOT_DIR / "sample_images"
OUTPUT_DIR.mkdir(exist_ok=True)


class ModernButton(ttk.Button):
    pass


class ImagePanel(ttk.Frame):
    def __init__(self, master, title: str):
        super().__init__(master, style="Panel.TFrame", padding=10)
        self.title_label = ttk.Label(self, text=title, style="PanelTitle.TLabel")
        self.title_label.pack(anchor="w", pady=(0, 8))
        self.canvas = tk.Canvas(self, width=310, height=250, bg="#111827", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.info = ttk.Label(self, text="Brak obrazu", style="Small.TLabel")
        self.info.pack(anchor="w", pady=(8, 0))
        self._tk_img = None

    def set_image(self, img: Image.Image | None):
        self.canvas.delete("all")
        if img is None:
            self._tk_img = None
            self.canvas.create_text(155, 125, text="Brak obrazu", fill="#9ca3af", font=("Segoe UI", 13))
            self.info.config(text="Brak obrazu")
            return
        w = max(self.canvas.winfo_width(), 310)
        h = max(self.canvas.winfo_height(), 250)
        preview = img.copy()
        preview.thumbnail((w - 18, h - 18), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(preview)
        self.canvas.create_image(w // 2, h // 2, image=self._tk_img, anchor="center")
        self.info.config(text=f"{img.width} x {img.height}px")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1250x820")
        self.minsize(1060, 720)
        self.configure(bg="#0b1020")

        self.original_arr: np.ndarray | None = None
        self.scrambled_arr: np.ndarray | None = None
        self.restored_arr: np.ndarray | None = None
        self.original_path: Path | None = None
        self.stage = tk.IntVar(value=1)
        self.key = tk.StringVar(value="Daniel-MII-2026")
        self.wrong_key = tk.StringVar(value="Daniel-MII-2027")
        self.param = tk.IntVar(value=3)
        self.use_wrong_key = tk.BooleanVar(value=False)

        self._setup_style()
        self._build_ui()
        self._load_default_sample()

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Root.TFrame", background="#0b1020")
        style.configure("Panel.TFrame", background="#121a2f", relief="flat")
        style.configure("Header.TLabel", background="#0b1020", foreground="#f8fafc", font=("Segoe UI", 20, "bold"))
        style.configure("Sub.TLabel", background="#0b1020", foreground="#a5b4fc", font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background="#121a2f", foreground="#f8fafc", font=("Segoe UI", 12, "bold"))
        style.configure("Small.TLabel", background="#121a2f", foreground="#9ca3af", font=("Segoe UI", 9))
        style.configure("Text.TLabel", background="#0b1020", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#0f172a", foreground="#f8fafc", bordercolor="#334155")
        style.configure("TSpinbox", fieldbackground="#0f172a", foreground="#f8fafc", bordercolor="#334155")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Stage.TButton", font=("Segoe UI", 11, "bold"), padding=12)
        style.configure("SelectedStage.TButton", font=("Segoe UI", 11, "bold"), padding=12)
        style.map("Accent.TButton", background=[("active", "#4f46e5")])

    def _build_ui(self):
        root = ttk.Frame(self, style="Root.TFrame", padding=18)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root, style="Root.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Projekt M-II: Chaotyczne przeksztalcanie obrazu cyfrowego", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="GUI do eksperymentow: Etap 1 / Etap 2 / Etap 3, poprawny i bledny klucz, metryki oraz zapis wynikow", style="Sub.TLabel").pack(anchor="w", pady=(2, 12))

        controls = ttk.Frame(root, style="Panel.TFrame", padding=14)
        controls.pack(fill="x", pady=(0, 14))
        controls.columnconfigure(10, weight=1)

        ttk.Button(controls, text="Wczytaj obraz", command=self.load_image, style="Accent.TButton").grid(row=0, column=0, padx=5, pady=4)
        ttk.Button(controls, text="Przyklad: naturalny", command=lambda: self.load_sample("natural_like.png"), style="Accent.TButton").grid(row=0, column=1, padx=5, pady=4)
        ttk.Button(controls, text="Przyklad: struktura", command=lambda: self.load_sample("checker_text.png"), style="Accent.TButton").grid(row=0, column=2, padx=5, pady=4)
        ttk.Button(controls, text="Przyklad: gradient", command=lambda: self.load_sample("gradient.png"), style="Accent.TButton").grid(row=0, column=3, padx=5, pady=4)

        stage_frame = ttk.Frame(controls, style="Panel.TFrame")
        stage_frame.grid(row=1, column=0, columnspan=4, sticky="w", pady=(10, 2))
        self.stage_buttons = []
        for num, label in [(1, "ETAP 1 - naiwny"), (2, "ETAP 2 - permutacja"), (3, "ETAP 3 - hybryda")]:
            btn = ttk.Button(stage_frame, text=label, command=lambda n=num: self.set_stage(n), style="Stage.TButton")
            btn.pack(side="left", padx=(0, 8))
            self.stage_buttons.append(btn)
        self._refresh_stage_buttons()

        params = ttk.Frame(controls, style="Panel.TFrame")
        params.grid(row=0, column=4, rowspan=2, sticky="nw", padx=(20, 0))
        ttk.Label(params, text="Klucz poprawny:", style="Small.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.key, width=26).grid(row=1, column=0, padx=(0, 12), pady=(2, 8))
        ttk.Label(params, text="Klucz bledny:", style="Small.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Entry(params, textvariable=self.wrong_key, width=26).grid(row=1, column=1, padx=(0, 12), pady=(2, 8))
        ttk.Label(params, text="Parametr:", style="Small.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(params, from_=1, to=1000, textvariable=self.param, width=8).grid(row=1, column=2, pady=(2, 8))
        ttk.Checkbutton(params, text="Unscramble blednym kluczem", variable=self.use_wrong_key).grid(row=2, column=0, columnspan=2, sticky="w")

        actions = ttk.Frame(controls, style="Panel.TFrame")
        actions.grid(row=0, column=8, rowspan=2, sticky="e", padx=(18, 0))
        ttk.Button(actions, text="SCRAMBLE", command=self.do_scramble, style="Accent.TButton").grid(row=0, column=0, padx=5, pady=4, sticky="ew")
        ttk.Button(actions, text="UNSCRAMBLE", command=self.do_unscramble, style="Accent.TButton").grid(row=0, column=1, padx=5, pady=4, sticky="ew")
        ttk.Button(actions, text="Test + metryki", command=self.do_metrics, style="Accent.TButton").grid(row=1, column=0, padx=5, pady=4, sticky="ew")
        ttk.Button(actions, text="Zapisz wyniki", command=self.save_results, style="Accent.TButton").grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        main = ttk.Frame(root, style="Root.TFrame")
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(0, weight=3)
        main.rowconfigure(1, weight=1)

        self.panel_original = ImagePanel(main, "1. Obraz oryginalny")
        self.panel_scrambled = ImagePanel(main, "2. Obraz przeksztalcony / scrambled")
        self.panel_restored = ImagePanel(main, "3. Obraz odtworzony / unscrambled")
        self.panel_original.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        self.panel_scrambled.grid(row=0, column=1, sticky="nsew", padx=8, pady=(0, 10))
        self.panel_restored.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=(0, 10))

        metrics_box = ttk.Frame(main, style="Panel.TFrame", padding=12)
        metrics_box.grid(row=1, column=0, columnspan=3, sticky="nsew")
        ttk.Label(metrics_box, text="Wyniki eksperymentu i komentarz", style="PanelTitle.TLabel").pack(anchor="w")
        self.text = tk.Text(metrics_box, height=9, bg="#0f172a", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat", wrap="word", font=("Consolas", 10))
        self.text.pack(fill="both", expand=True, pady=(8, 0))
        self.log("Gotowe. Wczytaj obraz albo wybierz przyklad. Najpierw kliknij ETAP, potem SCRAMBLE i UNSCRAMBLE.")

    def set_stage(self, n: int):
        self.stage.set(n)
        self._refresh_stage_buttons()
        descr = {
            1: "Etap 1: proste przesuniecia wierszy. Widac slabosc, bo struktura obrazu czesto zostaje.",
            2: "Etap 2: czysta permutacja pikseli Fisher-Yates. Wartosci pikseli nie sa zmieniane.",
            3: "Etap 3: hybryda - permutacja + substytucja modulo 256. Nadal nie jest to bezpieczny szyfr.",
        }[n]
        self.log(descr)

    def _refresh_stage_buttons(self):
        for i, btn in enumerate(getattr(self, "stage_buttons", []), start=1):
            btn.configure(style="SelectedStage.TButton" if self.stage.get() == i else "Stage.TButton")

    def log(self, msg: str):
        self.text.insert("end", msg + "\n")
        self.text.see("end")

    def _load_default_sample(self):
        sample = SAMPLE_DIR / "natural_like.png"
        if sample.exists():
            self.load_sample("natural_like.png")
        else:
            self.panel_original.set_image(None)
            self.panel_scrambled.set_image(None)
            self.panel_restored.set_image(None)

    def load_sample(self, name: str):
        path = SAMPLE_DIR / name
        if not path.exists():
            messagebox.showerror("Brak pliku", f"Nie znaleziono {path}")
            return
        self._open_image(path)

    def load_image(self):
        path = filedialog.askopenfilename(
            title="Wybierz obraz",
            filetypes=[("Obrazy", "*.png *.jpg *.jpeg *.bmp"), ("Wszystkie pliki", "*.*")],
        )
        if path:
            self._open_image(Path(path))

    def _open_image(self, path: Path):
        img = Image.open(path).convert("RGB")
        # Ograniczenie rozmiaru dla plynnej pracy GUI.
        max_side = 700
        if max(img.size) > max_side:
            img.thumbnail((max_side, max_side), Image.LANCZOS)
        self.original_arr = image_to_array(img)
        self.scrambled_arr = None
        self.restored_arr = None
        self.original_path = path
        self.panel_original.set_image(array_to_image(self.original_arr))
        self.panel_scrambled.set_image(None)
        self.panel_restored.set_image(None)
        self.log(f"Wczytano obraz: {path.name}, rozmiar po ewentualnym zmniejszeniu: {self.original_arr.shape[1]}x{self.original_arr.shape[0]}")

    def do_scramble(self):
        if self.original_arr is None:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return
        try:
            self.scrambled_arr = scramble(self.original_arr, self.stage.get(), self.key.get(), self.param.get())
            self.restored_arr = None
            self.panel_scrambled.set_image(array_to_image(self.scrambled_arr))
            self.panel_restored.set_image(None)
            self.log(f"SCRAMBLE wykonany dla Etapu {self.stage.get()} z kluczem poprawnym.")
        except Exception as e:
            messagebox.showerror("Blad", str(e))

    def do_unscramble(self):
        if self.scrambled_arr is None:
            messagebox.showwarning("Brak obrazu", "Najpierw wykonaj SCRAMBLE.")
            return
        used_key = self.wrong_key.get() if self.use_wrong_key.get() else self.key.get()
        try:
            self.restored_arr = unscramble(self.scrambled_arr, self.stage.get(), used_key, self.param.get())
            self.panel_restored.set_image(array_to_image(self.restored_arr))
            if self.original_arr is not None:
                mae, mse = diff_stats(self.original_arr, self.restored_arr)
                exact = np.array_equal(self.original_arr, self.restored_arr)
                self.log(f"UNSCRAMBLE wykonany kluczem: {'BLEDNYM' if self.use_wrong_key.get() else 'POPRAWNYM'} | zgodnosc idealna: {exact} | MAE={mae:.3f}, MSE={mse:.3f}")
        except Exception as e:
            messagebox.showerror("Blad", str(e))

    def do_metrics(self):
        if self.original_arr is None:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return
        scrambled = scramble(self.original_arr, self.stage.get(), self.key.get(), self.param.get())
        restored = unscramble(scrambled, self.stage.get(), self.key.get(), self.param.get())
        self.scrambled_arr = scrambled
        self.restored_arr = restored
        self.panel_scrambled.set_image(array_to_image(scrambled))
        self.panel_restored.set_image(array_to_image(restored))
        m = run_metrics(self.original_arr, scrambled, restored, self.stage.get(), self.key.get(), self.wrong_key.get(), self.param.get())
        self.log("=" * 76)
        self.log(f"TEST ETAPU {self.stage.get()} | klucz='{self.key.get()}' | bledny='{self.wrong_key.get()}' | parametr={self.param.get()}")
        self.log(f"Odtworzenie poprawnym kluczem idealne: {m.exact_restored}")
        self.log(f"Korelacja pozioma: przed={m.corr_h_before:.4f}, po={m.corr_h_after:.4f}")
        self.log(f"Korelacja pionowa:  przed={m.corr_v_before:.4f}, po={m.corr_v_after:.4f}")
        self.log(f"Roznica przy blednym kluczu: MAE={m.mae_wrong_key:.3f}, MSE={m.mse_wrong_key:.3f}")
        if self.stage.get() == 1:
            self.log("Wniosek: Etap 1 jest odwracalny, ale slaby - przesuniecia wierszy zostawiaja duzo widocznej struktury.")
        elif self.stage.get() == 2:
            self.log("Wniosek: Etap 2 mocniej miesza pozycje, ale histogram i wartosci pikseli zostaja takie same.")
        else:
            self.log("Wniosek: Etap 3 maskuje takze wartosci pikseli, ale nadal jest dydaktyczny, nie kryptograficzny.")

    def save_results(self):
        if self.original_arr is None:
            messagebox.showwarning("Brak obrazu", "Nie ma czego zapisac.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = OUTPUT_DIR / f"wynik_etap{self.stage.get()}_{ts}"
        base.mkdir(parents=True, exist_ok=True)
        array_to_image(self.original_arr).save(base / "01_original.png")
        if self.scrambled_arr is not None:
            array_to_image(self.scrambled_arr).save(base / "02_scrambled.png")
        if self.restored_arr is not None:
            array_to_image(self.restored_arr).save(base / "03_restored.png")
        with open(base / "metryki_i_log.txt", "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", "end"))
        self.log(f"Zapisano wyniki do: {base}")
        messagebox.showinfo("Zapisano", f"Wyniki zapisane w folderze:\n{base}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
