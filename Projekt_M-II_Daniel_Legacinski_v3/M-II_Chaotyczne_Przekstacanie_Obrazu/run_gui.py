from __future__ import annotations

import csv
import datetime
import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageTk

from scrambler.algorithms import scramble_image, unscramble_image, pil_to_array
from scrambler.metrics import metrics_summary, neighbor_correlation, compare_images

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
SAMPLES = BASE / "assets" / "samples"
OUT.mkdir(exist_ok=True)
SAMPLES.mkdir(parents=True, exist_ok=True)

COLORS = {
    "bg": "#10141f",
    "panel": "#171d2b",
    "panel2": "#1f2638",
    "card": "#222a3d",
    "accent": "#8b2434",
    "accent2": "#c64b5f",
    "text": "#eef2ff",
    "muted": "#aeb7cc",
    "ok": "#58c78a",
    "warn": "#f2b84b",
    "line": "#384057",
}


def make_sample_images() -> tuple[Path, Path]:
    """Tworzy dwa obrazy testowe: naturalny i strukturalny."""
    natural = SAMPLES / "sample_natural.png"
    structured = SAMPLES / "sample_structured.png"

    if not natural.exists():
        w, h = 520, 340
        y, x = np.mgrid[0:h, 0:w]
        r = (120 + 80 * np.sin(x / 28) + 40 * np.cos(y / 19)).clip(0, 255)
        g = (100 + 90 * np.sin((x + y) / 45) + 45 * np.cos(x / 37)).clip(0, 255)
        b = (140 + 70 * np.cos(y / 25) + 40 * np.sin((x - y) / 31)).clip(0, 255)
        img = np.dstack([r, g, b]).astype(np.uint8)
        im = Image.fromarray(img, "RGB")
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse((45, 35, 255, 255), fill=(255, 210, 80, 95))
        d.rectangle((305, 90, 485, 290), fill=(50, 160, 240, 90))
        d.polygon([(0, 340), (180, 210), (340, 340)], fill=(35, 120, 70, 100))
        d.text((28, 292), "obraz naturalny - test M-II", fill=(245, 245, 245, 210))
        im.save(natural)

    if not structured.exists():
        w, h = 520, 340
        im = Image.new("RGB", (w, h), "white")
        d = ImageDraw.Draw(im)
        cell = 34
        for yy in range(0, h, cell):
            for xx in range(0, w, cell):
                fill = (25, 25, 25) if ((xx // cell + yy // cell) % 2 == 0) else (235, 235, 235)
                d.rectangle((xx, yy, xx + cell - 1, yy + cell - 1), fill=fill)
        for i in range(0, w, 17):
            d.line((i, 0, i, h), fill=(150, 0, 25), width=1)
        for j in range(0, h, 17):
            d.line((0, j, w, j), fill=(0, 0, 150), width=1)
        d.rectangle((105, 120, 415, 218), fill=(255, 255, 255), outline=(139, 36, 52), width=3)
        d.text((130, 145), "M-II  DANIEL LEGACINSKI", fill=(139, 36, 52))
        d.text((172, 180), "tekst / gradient / szachownica", fill=(10, 10, 10))
        im.save(structured)

    return natural, structured


class PrettyButton(ttk.Button):
    """Mała klasa pomocnicza tylko po to, żeby kod GUI był czytelniejszy."""


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Projekt M-II - Chaotyczne przekształcanie obrazu cyfrowego")
        self.root.geometry("1280x820")
        self.root.minsize(980, 680)

        self.original: Image.Image | None = None
        self.scrambled: Image.Image | None = None
        self.restored: Image.Image | None = None
        self.current_image_path: str = ""
        self.last_output_folder: Path | None = None
        self.photo_refs: list[ImageTk.PhotoImage] = []

        make_sample_images()
        self._style()
        self._build()
        self.load_image(SAMPLES / "sample_structured.png")

    # ---------- wygląd ----------

    def _style(self) -> None:
        self.root.configure(bg=COLORS["bg"])
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 9))
        style.configure("Panel.TLabel", background=COLORS["panel"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background=COLORS["bg"], foreground=COLORS["muted"], font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=COLORS["panel"], foreground=COLORS["accent2"], font=("Segoe UI", 12, "bold"))
        style.configure("ImageTitle.TLabel", background=COLORS["card"], foreground=COLORS["text"], font=("Segoe UI", 11, "bold"))
        style.configure("ImageBox.TLabel", background=COLORS["card"], foreground=COLORS["muted"], anchor="center")
        style.configure("Status.TLabel", background=COLORS["panel2"], foreground=COLORS["muted"], font=("Segoe UI", 9))

        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 8), background=COLORS["panel2"], foreground=COLORS["text"], borderwidth=0)
        style.map("TButton", background=[("active", COLORS["accent"]), ("pressed", COLORS["accent2"])] )
        style.configure("Accent.TButton", background=COLORS["accent"], foreground="white", font=("Segoe UI", 10, "bold"), padding=(12, 9))
        style.map("Accent.TButton", background=[("active", COLORS["accent2"]), ("pressed", COLORS["accent2"])] )
        style.configure("Danger.TButton", background="#5d1f2c", foreground="white", font=("Segoe UI", 10, "bold"), padding=(12, 9))
        style.map("Danger.TButton", background=[("active", "#8b2434"), ("pressed", "#c64b5f")] )

        style.configure("TCombobox", fieldbackground=COLORS["panel2"], background=COLORS["panel2"], foreground=COLORS["text"], arrowcolor=COLORS["text"])
        style.configure("TSpinbox", fieldbackground=COLORS["panel2"], background=COLORS["panel2"], foreground=COLORS["text"], arrowcolor=COLORS["text"])
        style.configure("TEntry", fieldbackground=COLORS["panel2"], foreground=COLORS["text"], insertcolor=COLORS["text"])
        style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=COLORS["panel2"], foreground=COLORS["muted"], padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COLORS["accent"])], foreground=[("selected", "white")])

    def _build(self) -> None:
        header = ttk.Frame(self.root, padding=(18, 14, 18, 8))
        header.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(header, text="Projekt M-II", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Chaotyczne przekształcanie obrazu cyfrowego — GUI do eksperymentów, testów klucza i analizy metryk",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        main = ttk.Frame(self.root, padding=(14, 6, 14, 10))
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main, style="Panel.TFrame", padding=14, width=360)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        left.pack_propagate(False)

        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_controls(left)
        self._build_preview(right)

        self.status = tk.StringVar(value="Gotowe. Wczytano projekt M-II.")
        status_bar = ttk.Frame(self.root, style="Panel.TFrame", padding=(12, 6))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_bar, textvariable=self.status, style="Status.TLabel").pack(anchor="w")

    def _build_controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Sterowanie", style="Section.TLabel").pack(anchor="w")
        ttk.Label(parent, text="Wczytaj obraz, wybierz etap, ustaw klucz i wykonaj eksperyment.", style="Panel.TLabel", wraplength=330).pack(anchor="w", pady=(4, 12))

        ttk.Button(parent, text="📂  Wczytaj obraz PNG / JPEG / BMP", style="Accent.TButton", command=self.open_image).pack(fill=tk.X, pady=4)
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill=tk.X, pady=4)
        ttk.Button(row, text="Szachownica / tekst", command=lambda: self.load_image(SAMPLES / "sample_structured.png")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row, text="Obraz naturalny", command=lambda: self.load_image(SAMPLES / "sample_natural.png")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        self._line(parent)
        ttk.Label(parent, text="Parametry algorytmu", style="Section.TLabel").pack(anchor="w", pady=(4, 8))

        ttk.Label(parent, text="Etap algorytmu", style="Panel.TLabel").pack(anchor="w")
        self.stage = tk.StringVar(value="1")
        stage_box = ttk.Combobox(parent, textvariable=self.stage, values=["1 - naiwny scrambling", "2 - czysta permutacja", "3 - hybryda permutacja + substytucja"], state="readonly")
        stage_box.pack(fill=tk.X, pady=(3, 8))
        stage_box.bind("<<ComboboxSelected>>", lambda _e: self._stage_description())

        ttk.Label(parent, text="Klucz tekstowy", style="Panel.TLabel").pack(anchor="w")
        self.key = tk.StringVar(value="Daniel-2026")
        ttk.Entry(parent, textvariable=self.key).pack(fill=tk.X, pady=(3, 8))

        spin_row = ttk.Frame(parent, style="Panel.TFrame")
        spin_row.pack(fill=tk.X)
        left_col = ttk.Frame(spin_row, style="Panel.TFrame")
        right_col = ttk.Frame(spin_row, style="Panel.TFrame")
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        right_col.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        ttk.Label(left_col, text="Parametr", style="Panel.TLabel").pack(anchor="w")
        self.param = tk.IntVar(value=7)
        ttk.Spinbox(left_col, from_=1, to=9999, textvariable=self.param).pack(fill=tk.X, pady=(3, 8))
        ttk.Label(right_col, text="Rundy Etapu 3", style="Panel.TLabel").pack(anchor="w")
        self.rounds = tk.IntVar(value=2)
        ttk.Spinbox(right_col, from_=1, to=8, textvariable=self.rounds).pack(fill=tk.X, pady=(3, 8))

        self.stage_info = tk.StringVar()
        ttk.Label(parent, textvariable=self.stage_info, style="Panel.TLabel", wraplength=340, justify=tk.LEFT).pack(anchor="w", pady=(0, 6))
        self._stage_description()

        self._line(parent)
        ttk.Label(parent, text="Operacje", style="Section.TLabel").pack(anchor="w", pady=(4, 8))
        ttk.Button(parent, text="🔥  Scramble — przekształć obraz", style="Accent.TButton", command=self.do_scramble).pack(fill=tk.X, pady=4)
        ttk.Button(parent, text="✅  Unscramble — poprawny klucz", command=self.do_unscramble_ok).pack(fill=tk.X, pady=4)
        ttk.Button(parent, text="⚠️  Unscramble — błędny klucz", style="Danger.TButton", command=self.do_unscramble_wrong).pack(fill=tk.X, pady=4)

        row2 = ttk.Frame(parent, style="Panel.TFrame")
        row2.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(row2, text="💾 Zapisz", command=self.save_current).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row2, text="📊 Pełne eksperymenty", command=self.run_experiments).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        row3 = ttk.Frame(parent, style="Panel.TFrame")
        row3.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(row3, text="🧹 Wyczyść wynik", command=self.reset_results).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Button(row3, text="📁 Otwórz outputs", command=self.open_outputs).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

    def _build_preview(self, parent: ttk.Frame) -> None:
        self.preview_top = ttk.Frame(parent)
        self.preview_top.pack(fill=tk.BOTH, expand=True)
        self.preview_cols = 3

        self.image_cards: list[ttk.Frame] = []
        self.labels: list[ttk.Label] = []
        for title, caption in [
            ("1. Obraz oryginalny", "wejście do algorytmu"),
            ("2. Obraz przekształcony", "wynik funkcji scrambling"),
            ("3. Obraz odtworzony", "wynik funkcji unscrambling"),
        ]:
            card = ttk.Frame(self.preview_top, style="Card.TFrame", padding=12)
            ttk.Label(card, text=title, style="ImageTitle.TLabel").pack(anchor="w")
            ttk.Label(card, text=caption, background=COLORS["card"], foreground=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 8))
            lab = ttk.Label(card, text="Brak obrazu", style="ImageBox.TLabel")
            lab.pack(fill=tk.BOTH, expand=True)
            self.image_cards.append(card)
            self.labels.append(lab)

        self.preview_top.bind("<Configure>", self._on_preview_resize)
        self.root.after(100, self._layout_preview_cards)

        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=False, pady=(12, 0))

        metrics_frame = ttk.Frame(notebook, style="Panel.TFrame", padding=10)
        help_frame = ttk.Frame(notebook, style="Panel.TFrame", padding=10)
        notebook.add(metrics_frame, text="Metryki i wynik")
        notebook.add(help_frame, text="Opis klawiszy")

        self.metrics_text = tk.Text(metrics_frame, height=11, wrap="word", bg=COLORS["panel2"], fg=COLORS["text"], insertbackground=COLORS["text"], relief="flat", padx=10, pady=10, font=("Consolas", 10))
        self.metrics_text.pack(fill=tk.BOTH, expand=True)

        help_text = (
            "Wczytaj obraz — wybiera własny plik PNG, JPG/JPEG albo BMP.\n"
            "Szachownica / tekst — ładuje obraz z mocną strukturą, dobry do pokazania słabości etapu 1.\n"
            "Obraz naturalny — ładuje przykładowy obraz bardziej podobny do fotografii.\n"
            "Etap algorytmu — przełącza między trzema wymaganymi metodami.\n"
            "Klucz tekstowy — decyduje o przesunięciach, permutacji i strumieniu wartości.\n"
            "Parametr — dodatkowa liczba zmieniająca seed i zachowanie algorytmu.\n"
            "Rundy Etapu 3 — liczba powtórzeń hybrydy permutacja + substytucja.\n"
            "Scramble — tworzy obraz przekształcony.\n"
            "Unscramble poprawny — odtwarza obraz z poprawnym kluczem.\n"
            "Unscramble błędny — pokazuje, co dzieje się przy minimalnie złym kluczu.\n"
            "Zapisz — zapisuje widoczne obrazy i metryki do outputs/manual_*.\n"
            "Pełne eksperymenty — automatycznie testuje oba obrazy i wszystkie 3 etapy.\n"
            "Otwórz outputs — otwiera folder z wynikami."
        )
        txt = tk.Text(help_frame, height=11, wrap="word", bg=COLORS["panel2"], fg=COLORS["text"], relief="flat", padx=10, pady=10, font=("Segoe UI", 10))
        txt.insert(tk.END, help_text)
        txt.configure(state="disabled")
        txt.pack(fill=tk.BOTH, expand=True)


    def _line(self, parent: ttk.Frame) -> None:
        line = tk.Frame(parent, height=1, bg=COLORS["line"])
        line.pack(fill=tk.X, pady=12)

    def _on_preview_resize(self, _event=None) -> None:
        self._layout_preview_cards()
        self.show_images()

    def _layout_preview_cards(self) -> None:
        width = max(self.preview_top.winfo_width(), 1)

        if width < 760:
            cols = 1
        elif width < 1080:
            cols = 2
        else:
            cols = 3

        if cols == self.preview_cols and any(card.winfo_manager() for card in self.image_cards):
            return

        self.preview_cols = cols

        for i in range(3):
            self.preview_top.grid_columnconfigure(i, weight=0)
            self.preview_top.grid_rowconfigure(i, weight=0)

        for card in self.image_cards:
            card.grid_forget()

        if cols == 3:
            for i, card in enumerate(self.image_cards):
                self.preview_top.grid_columnconfigure(i, weight=1, uniform="preview")
                card.grid(row=0, column=i, sticky="nsew", padx=6, pady=6)
            self.preview_top.grid_rowconfigure(0, weight=1)
        elif cols == 2:
            self.preview_top.grid_columnconfigure(0, weight=1, uniform="preview")
            self.preview_top.grid_columnconfigure(1, weight=1, uniform="preview")
            self.image_cards[0].grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
            self.image_cards[1].grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
            self.image_cards[2].grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
            self.preview_top.grid_rowconfigure(0, weight=1)
            self.preview_top.grid_rowconfigure(1, weight=1)
        else:
            self.preview_top.grid_columnconfigure(0, weight=1)
            for i, card in enumerate(self.image_cards):
                card.grid(row=i, column=0, sticky="nsew", padx=6, pady=6)
                self.preview_top.grid_rowconfigure(i, weight=1)

    def _current_thumbnail_size(self) -> tuple[int, int]:
        width = max(self.preview_top.winfo_width(), 900)
        cols = max(self.preview_cols, 1)
        available = max(220, width - (cols * 18) - 12)
        thumb_w = max(220, min(420, available // cols - 26))
        if cols == 1:
            thumb_h = 420
        elif cols == 2:
            thumb_h = 330
        else:
            thumb_h = 260
        return thumb_w, thumb_h

    # ---------- logika GUI ----------

    def _stage_number(self) -> int:
        return int(str(self.stage.get()).split()[0])

    def _stage_description(self) -> None:
        n = self._stage_number()
        if n == 1:
            text = "Etap 1: przesunięcia wierszy i kolumn. Odwracalny, ale słaby — struktura obrazu często zostaje widoczna."
        elif n == 2:
            text = "Etap 2: czysta permutacja pikseli Fisher-Yates. Wartości pikseli się nie zmieniają, zmieniają się tylko pozycje."
        else:
            text = "Etap 3: hybryda. Najpierw permutacja, potem substytucja modularna; operację można odwrócić tylko poprawnym kluczem."
        self.stage_info.set(text)

    def open_image(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.png *.jpg *.jpeg *.bmp"), ("Wszystkie pliki", "*.*")])
        if path:
            self.load_image(path)

    def load_image(self, path: str | Path) -> None:
        self.original = Image.open(path).convert("RGB")
        # Celowo zmniejszamy obraz w pamięci programu, aby operacje działały szybko na komputerze studenckim.
        self.original.thumbnail((620, 620))
        self.scrambled = None
        self.restored = None
        self.current_image_path = str(path)
        self.show_images()
        self.write_metrics(
            "Wczytano obraz:\n"
            f"{path}\n\n"
            f"Rozmiar roboczy: {self.original.size[0]} x {self.original.size[1]} px\n"
            "Teraz wybierz etap, wpisz klucz i kliknij Scramble."
        )
        self.status.set(f"Wczytano obraz: {Path(path).name}")

    def show_images(self) -> None:
        imgs = [self.original, self.scrambled, self.restored]
        thumb_size = self._current_thumbnail_size()
        self.photo_refs.clear()
        for lab, img in zip(self.labels, imgs):
            if img is None:
                lab.configure(image="", text="Brak obrazu")
                continue
            display = img.copy()
            display.thumbnail(thumb_size)
            photo = ImageTk.PhotoImage(display)
            self.photo_refs.append(photo)
            lab.configure(image=photo, text="")

    def do_scramble(self) -> None:
        if self.original is None:
            messagebox.showwarning("Brak obrazu", "Najpierw wczytaj obraz.")
            return
        self.scrambled = scramble_image(self.original, self._stage_number(), self.key.get(), self.param.get(), self.rounds.get())
        self.restored = None
        self.show_images()
        self.update_metrics()
        self.status.set("Wykonano Scramble. Obraz przekształcony jest widoczny w środkowym panelu.")

    def do_unscramble_ok(self) -> None:
        if self.scrambled is None:
            self.do_scramble()
        if self.scrambled is None:
            return
        self.restored = unscramble_image(self.scrambled, self._stage_number(), self.key.get(), self.param.get(), self.rounds.get())
        self.show_images()
        self.update_metrics()
        self.status.set("Wykonano Unscramble poprawnym kluczem.")

    def do_unscramble_wrong(self) -> None:
        if self.scrambled is None:
            self.do_scramble()
        if self.scrambled is None:
            return
        wrong_key = self.key.get() + "_blad"
        self.restored = unscramble_image(self.scrambled, self._stage_number(), wrong_key, self.param.get(), self.rounds.get())
        self.show_images()
        self.update_metrics(wrong=True)
        self.status.set("Wykonano test błędnego klucza. To pokazuje wrażliwość algorytmu na klucz.")

    def update_metrics(self, wrong: bool = False) -> None:
        if self.original is None or self.scrambled is None:
            return
        org = pil_to_array(self.original)
        scr = pil_to_array(self.scrambled)
        c1 = neighbor_correlation(org)
        c2 = neighbor_correlation(scr)

        lines = [
            "PARAMETRY EKSPERYMENTU",
            "=" * 58,
            f"Etap: {self._stage_number()}",
            f"Klucz: {self.key.get()}",
            f"Parametr: {self.param.get()}",
            f"Rundy: {self.rounds.get()}",
            f"Obraz: {self.current_image_path}",
            "",
            "KORELACJA SĄSIEDNICH PIKSELI",
            "=" * 58,
            f"Pozioma przed scramblingiem: {c1['horizontal_avg']:.6f}",
            f"Pozioma po scramblingu:     {c2['horizontal_avg']:.6f}",
            f"Pionowa przed scramblingiem: {c1['vertical_avg']:.6f}",
            f"Pionowa po scramblingu:      {c2['vertical_avg']:.6f}",
            "",
            "INTERPRETACJA",
            "=" * 58,
            "Im niższa korelacja po scramblingu, tym mniej widoczna jest lokalna struktura obrazu.",
        ]

        if self.restored is not None:
            cmp = compare_images(org, pil_to_array(self.restored))
            lines += [
                "",
                "PORÓWNANIE: ORYGINAŁ VS OBRAZ ODTWORZONY",
                "=" * 58,
                f"Obrazy identyczne: {cmp['identical']}",
                f"MSE: {cmp['mse']:.6f}",
                f"MAE: {cmp['mae']:.6f}",
                f"Maksymalna różnica piksela: {cmp['max_diff']}",
            ]
        if wrong:
            lines += [
                "",
                "UWAGA",
                "=" * 58,
                "Odtwarzanie wykonano błędnym kluczem: klucz + '_blad'.",
                "Ten test jest wymagany w projekcie i pokazuje wpływ minimalnej zmiany klucza.",
            ]
        self.write_metrics("\n".join(lines))

    def write_metrics(self, text: str) -> None:
        self.metrics_text.configure(state="normal")
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, text)
        self.metrics_text.configure(state="normal")

    def reset_results(self) -> None:
        self.scrambled = None
        self.restored = None
        self.show_images()
        self.write_metrics("Wyczyszczono wynik. Oryginał został zachowany. Kliknij Scramble, aby wykonać nową próbę.")
        self.status.set("Wyczyszczono obraz przekształcony i odtworzony.")

    def save_current(self) -> None:
        if self.original is None:
            messagebox.showwarning("Brak obrazu", "Nie ma czego zapisać. Najpierw wczytaj obraz.")
            return
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = OUT / f"manual_{stamp}"
        folder.mkdir(exist_ok=True)
        self.original.save(folder / "original.png")
        if self.scrambled:
            self.scrambled.save(folder / "scrambled.png")
        if self.restored:
            self.restored.save(folder / "restored.png")
        with open(folder / "metrics.txt", "w", encoding="utf-8") as f:
            f.write(self.metrics_text.get("1.0", tk.END))
        self.last_output_folder = folder
        self.status.set(f"Zapisano aktualne wyniki: {folder}")
        messagebox.showinfo("Zapisano", f"Wyniki zapisane w folderze:\n{folder}")

    def run_experiments(self) -> None:
        natural, structured = make_sample_images()
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = OUT / f"experiments_{stamp}"
        folder.mkdir(exist_ok=True)
        rows = []

        for img_path in [natural, structured]:
            img_name = img_path.stem
            img = Image.open(img_path).convert("RGB")
            img.save(folder / f"{img_name}_original.png")
            for stage in [1, 2, 3]:
                key = self.key.get()
                param = self.param.get()
                rounds = self.rounds.get()
                scr = scramble_image(img, stage, key, param, rounds)
                ok = unscramble_image(scr, stage, key, param, rounds)
                wrong = unscramble_image(scr, stage, key + "_blad", param, rounds)
                scr.save(folder / f"{img_name}_stage{stage}_scrambled.png")
                ok.save(folder / f"{img_name}_stage{stage}_restored_ok.png")
                wrong.save(folder / f"{img_name}_stage{stage}_restored_wrong_key.png")
                summary = metrics_summary(pil_to_array(img), pil_to_array(scr), pil_to_array(ok), pil_to_array(wrong))
                summary.update({"image": img_name, "stage": stage, "key": key, "parameter": param, "rounds": rounds})
                rows.append(summary)

        csv_path = folder / "metrics.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        labels = [f"{r['image']} E{r['stage']}" for r in rows]
        vals = [r["corr_scrambled_horizontal"] for r in rows]
        plt.figure(figsize=(11, 4.8))
        plt.bar(labels, vals)
        plt.xticks(rotation=35, ha="right")
        plt.ylabel("Korelacja pozioma po scramblingu")
        plt.title("Porównanie etapów projektu M-II")
        plt.tight_layout()
        plt.savefig(folder / "correlation_chart.png", dpi=160)
        plt.close()

        self.last_output_folder = folder
        self.status.set(f"Pełne eksperymenty zakończone: {folder}")
        self.write_metrics(
            "WYKONANO PEŁNE EKSPERYMENTY\n"
            "=" * 58 + "\n"
            f"Folder wyników: {folder}\n"
            f"Plik metryk CSV: {csv_path}\n\n"
            "Zapisano obrazy oryginalne, scrambled, restored_ok, restored_wrong_key oraz wykres korelacji."
        )
        messagebox.showinfo("Eksperymenty zakończone", f"Zapisano komplet wyników w:\n{folder}")

    def open_outputs(self) -> None:
        target = self.last_output_folder if self.last_output_folder and self.last_output_folder.exists() else OUT
        try:
            if sys.platform.startswith("win"):
                os.startfile(target)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(target)], check=False)
            else:
                subprocess.run(["xdg-open", str(target)], check=False)
            self.status.set(f"Otwieram folder: {target}")
        except Exception as exc:
            messagebox.showinfo("Folder outputs", f"Folder z wynikami znajduje się tutaj:\n{target}\n\nNie udało się otworzyć automatycznie: {exc}")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
