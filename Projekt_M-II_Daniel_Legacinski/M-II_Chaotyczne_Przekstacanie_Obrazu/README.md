# Projekt M-II - Chaotyczne przeksztalcanie obrazu cyfrowego

Autor: Daniel Legacinski

Projekt zawiera gotowa aplikacje GUI w Pythonie oraz dokumentacje. Program pokazuje trzy etapy wymagane w zadaniu:

1. Etap 1 - naiwny scrambling: deterministyczne przesuniecia wierszy i kolumn.
2. Etap 2 - czysta permutacja sterowana kluczem: Fisher-Yates + jawny generator LCG.
3. Etap 3 - mechanizm wzmacniajacy: hybryda permutacja + substytucja modularna.

To nie jest bezpieczny szyfr. Projekt jest eksperymentem dydaktycznym.

## Jak uruchomic

1. Zainstaluj Python 3.10 lub nowszy.
2. Otworz terminal w folderze projektu.
3. Wpisz:

```bash
pip install -r requirements.txt
python run_gui.py
```

## Co robi GUI

- wczytuje PNG / JPEG / BMP,
- pozwala wybrac etap 1 / 2 / 3,
- pozwala wpisac klucz i parametr,
- wykonuje Scramble i Unscramble,
- pokazuje obraz oryginalny, przeksztalcony i odtworzony,
- liczy korelacje sasiadujacych pikseli,
- testuje poprawny i bledny klucz,
- zapisuje wyniki do folderu `outputs`.

## Uruchomienie eksperymentow bez GUI

```bash
python run_experiments.py
```

Wyniki pojawia sie w folderze `outputs/experiments_cli_*`.
