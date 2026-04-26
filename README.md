# Projekt M-II — Chaotyczne przekształcanie obrazu cyfrowego

Autor: Daniel Legacinski  
Temat: Chaotyczne przekształcanie obrazu cyfrowego  
Technologia: Python, NumPy, Pillow, Tkinter, Matplotlib

---

## 1. Opis projektu

Projekt przedstawia działanie trzech etapów chaotycznego przekształcania obrazu cyfrowego.

Celem projektu nie jest stworzenie bezpiecznego szyfru kryptograficznego, ale pokazanie, jak działają proste metody scramblingu obrazu oraz jakie mają ograniczenia.

Program pozwala:

- wczytać obraz PNG, JPG, JPEG lub BMP,
- wybrać jeden z trzech etapów przekształcania,
- wpisać klucz,
- wykonać operację Scramble,
- wykonać operację Unscramble,
- porównać obraz oryginalny, przekształcony i odtworzony,
- sprawdzić działanie poprawnego i błędnego klucza,
- zapisać wyniki eksperymentów.

---

## 2. Struktura projektu

Po rozpakowaniu projektu powinny znajdować się takie pliki i foldery:

```text
Projekt_M_II_Chaotyczne_Obrazy/
│
├── main.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── algorithms.py
│   ├── gui.py
│   ├── metrics.py
│   └── utils.py
│
├── samples/
│   ├── natural.png
│   └── structured.png
│
├── outputs/
│   ├── metryki.csv
│   └── wyniki_obrazow/
│
└── docs/
    └── Dokumentacja_Projekt_M_II.pdf


```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

cd desktop/Projekt_M_II_Chaotyczne_Obrazy_gotowy/Projekt_M_II_Chaotyczne_Obrazy

python main.py
