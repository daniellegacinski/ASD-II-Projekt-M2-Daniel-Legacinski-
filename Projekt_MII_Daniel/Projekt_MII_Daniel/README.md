# Projekt M-II - Chaotyczne przeksztalcanie obrazu cyfrowego

Autor: **Daniel Legacinski**

Ten projekt jest gotowa aplikacja do eksperymentow z przeksztalcaniem obrazu cyfrowego. Program realizuje trzy wymagane etapy:

1. **Etap 1 - Naiwny scrambling**
2. **Etap 2 - Czysta permutacja sterowana kluczem**
3. **Etap 3 - Mechanizm wzmacniajacy: hybryda permutacji i substytucji**

Projekt ma pokazac roznice miedzy permutacja i substytucja oraz wyjasnic, dlaczego obraz wygladajacy losowo nie oznacza jeszcze bezpiecznego szyfrowania.

---

## 1. Jak uruchomic projekt

### Windows - najprosciej

1. Rozpakuj plik ZIP.
2. Wejdz do folderu `Projekt_MII_Daniel`.
3. Kliknij dwa razy plik:

```text
run.bat
```

Skrypt sam zainstaluje biblioteki z `requirements.txt` i uruchomi aplikacje.

### Windows - recznie przez terminal

Otworz terminal w folderze projektu i wpisz:

```bash
python -m pip install -r requirements.txt
python src/app.py
```

### Linux / macOS

```bash
chmod +x run.sh
./run.sh
```

---

## 2. Wymagane biblioteki

Projekt uzywa:

- `numpy` - operacje na tablicach pikseli,
- `Pillow` - wczytywanie i zapisywanie obrazow,
- `matplotlib` - opcjonalnie do rozszerzania eksperymentow,
- `tkinter` - GUI; zwykle jest w Pythonie domyslnie.

Plik `requirements.txt` zawiera biblioteki instalowane przez pip.

---

## 3. Struktura folderow

```text
Projekt_MII_Daniel/
│
├── src/
│   ├── app.py              # glowny interfejs graficzny GUI
│   └── algorithms.py       # wszystkie algorytmy Etap 1, Etap 2, Etap 3
│
├── sample_images/
│   ├── natural_like.png    # obraz naturalny wygenerowany lokalnie
│   ├── checker_text.png    # obraz o silnej strukturze: szachownica + tekst
│   └── gradient.png        # gradient + siatka
│
├── docs/
│   ├── DOKUMENTACJA_PROJEKT_MII.md
│   └── DOKUMENTACJA_PROJEKT_MII.pdf
│
├── outputs/                # tutaj zapisuje sie wyniki z GUI
├── requirements.txt
├── run.bat
├── run.sh
└── README.md
```

---

## 4. Co robi kazdy przycisk w GUI

### `Wczytaj obraz`

Pozwala wybrac wlasny obraz z dysku. Obslugiwane formaty:

- PNG,
- JPG / JPEG,
- BMP.

Program automatycznie konwertuje obraz do RGB. Jezeli obraz jest bardzo duzy, zostaje zmniejszony do maksymalnego boku okolo 700 px, zeby GUI dzialalo szybko.

### `Przyklad: naturalny`

Wczytuje obraz `natural_like.png` z folderu `sample_images`.

To nie jest zdjecie pobrane z internetu. Jest to lokalnie wygenerowany obraz przypominajacy naturalny krajobraz. Sluzy do eksperymentu wymaganego w projekcie: test na obrazie naturalnym.

### `Przyklad: struktura`

Wczytuje obraz `checker_text.png`.

Ten obraz ma mocna strukture: szachownice, kontrastowe pola i tekst. Jest potrzebny, poniewaz w PDF wymagany jest test na obrazie o silnej strukturze.

### `Przyklad: gradient`

Wczytuje obraz `gradient.png`.

Gradient dobrze pokazuje, czy algorytm niszczy gladkie przejscia i czy po blednym kluczu obraz da sie jeszcze rozpoznac.

---

## 5. Przyciski etapow

### `ETAP 1 - naiwny`

Wybiera pierwszy algorytm. Jest to najprostszy scrambling przez cykliczne przesuniecia wierszy.

Cel etapu 1: pokazac porazke prostej metody.

Dlaczego metoda jest slaba:

- obraz dalej moze miec widoczne pasy,
- lokalne struktury zostaja w wierszach,
- atakujacy moze domyslic sie, ze wystarczy cofac przesuniecia,
- metoda jest odwracalna, ale nie daje bezpieczenstwa.

### `ETAP 2 - permutacja`

Wybiera drugi algorytm. Jest to czysta permutacja pikseli Fisher-Yates sterowana kluczem.

W tym etapie zmienia sie tylko polozenie pikseli. Wartosci pikseli pozostaja takie same.

To jest wazne, bo pokazuje roznice:

- permutacja = zmiana miejsc,
- substytucja = zmiana wartosci.

### `ETAP 3 - hybryda`

Wybiera trzeci algorytm. Jest to mechanizm wzmacniajacy:

1. najpierw wykonywana jest permutacja,
2. potem wykonywana jest substytucja modulo 256.

Dla piksela `p` i maski `m`:

```text
scrambled = (p + m) mod 256
restored  = (scrambled - m) mod 256
```

Etap 3 jest bardziej odporny wizualnie niz etap 1 i etap 2, ale nadal nie jest bezpiecznym szyfrem.

---

## 6. Pola tekstowe i parametry

### `Klucz poprawny`

Tutaj wpisujesz klucz, ktory ma byc uzyty do poprawnego scramblingu i unscramblingu.

Przyklad:

```text
Daniel-MII-2026
```

Ten sam klucz musi byc uzyty do odtworzenia obrazu. Jezeli klucz jest taki sam, obraz po `UNSCRAMBLE` powinien byc identyczny jak oryginal.

### `Klucz bledny`

Tutaj wpisujesz klucz do testu blednego odtwarzania.

Przyklad:

```text
Daniel-MII-2027
```

Nawet mala zmiana klucza powinna dac inny wynik, szczegolnie w Etapie 2 i 3.

### `Parametr`

Dodatkowy parametr algorytmu.

W Etapie 1 oznacza sile przesuniecia wierszy.

W Etapie 2 parametr jest zostawiony dla spojnosci GUI, ale sama czysta permutacja zalezy glownie od klucza.

W Etapie 3 parametr jest dopisywany do generowania maski, wiec zmiana parametru zmienia wynik substytucji.

### `Unscramble blednym kluczem`

Jezeli zaznaczysz to pole, przycisk `UNSCRAMBLE` uzyje klucza blednego zamiast poprawnego.

To jest szybki test z PDF:

- poprawny klucz -> obraz wraca idealnie,
- bledny klucz -> obraz nie powinien wrocic poprawnie.

---

## 7. Przyciski akcji

### `SCRAMBLE`

Wykonuje przeksztalcenie obrazu dla wybranego etapu.

Wynik pojawia sie w panelu:

```text
2. Obraz przeksztalcony / scrambled
```

### `UNSCRAMBLE`

Odtwarza obraz z obrazu przeksztalconego.

Wynik pojawia sie w panelu:

```text
3. Obraz odtworzony / unscrambled
```

Jesli uzywasz poprawnego klucza, obraz powinien byc identyczny z oryginalem.

### `Test + metryki`

Automatycznie robi:

1. scramble,
2. unscramble poprawnym kluczem,
3. test blednego klucza,
4. obliczenie metryk.

Metryki pokazane w programie:

- korelacja pozioma przed i po,
- korelacja pionowa przed i po,
- MAE przy blednym kluczu,
- MSE przy blednym kluczu,
- czy odtworzenie poprawnym kluczem jest idealne.

### `Zapisz wyniki`

Zapisuje aktualny eksperyment do folderu `outputs`.

Tworzony jest nowy folder, np.:

```text
outputs/wynik_etap3_20260424_153012/
```

W srodku sa pliki:

```text
01_original.png
02_scrambled.png
03_restored.png
metryki_i_log.txt
```

---

## 8. Co pokazac na obronie

Najprostszy scenariusz obrony:

1. Uruchom `run.bat`.
2. Wczytaj `Przyklad: naturalny`.
3. Kliknij `ETAP 1 - naiwny`.
4. Kliknij `Test + metryki`.
5. Powiedz, ze struktura obrazu jeszcze moze byc widoczna.
6. Kliknij `ETAP 2 - permutacja`.
7. Kliknij `Test + metryki`.
8. Powiedz, ze wartosci pikseli nie sa zmieniane, tylko ich pozycje.
9. Kliknij `ETAP 3 - hybryda`.
10. Kliknij `Test + metryki`.
11. Zaznacz `Unscramble blednym kluczem` i kliknij `UNSCRAMBLE`.
12. Pokaz, ze bledny klucz nie odtwarza obrazu.
13. Kliknij `Zapisz wyniki`.
14. Pokaz pliki w folderze `outputs`.

---

## 9. Najwazniejsze wnioski

- Etap 1 jest celowo slaby, bo ma pokazac, ze proste mieszanie obrazu nie wystarcza.
- Etap 2 daje lepszy chaos wizualny, ale nie zmienia histogramu wartosci pikseli.
- Etap 3 zmienia i polozenia, i wartosci pikseli, ale dalej nie jest to kryptografia.
- Wizualny chaos nie oznacza bezpieczenstwa.
- Program jest narzedziem dydaktycznym, a nie systemem ochrony danych.

---

## 10. Najczestsze problemy

### Problem: `python` nie jest rozpoznawany

Zainstaluj Python z oficjalnej strony i zaznacz opcje:

```text
Add Python to PATH
```

### Problem: brakuje biblioteki Pillow albo numpy

Wpisz:

```bash
python -m pip install -r requirements.txt
```

### Problem: Tkinter sie nie uruchamia na Linuxie

Na Ubuntu/Debian:

```bash
sudo apt install python3-tk
```

### Problem: obraz jest za duzy i program dziala wolno

Program automatycznie zmniejsza obraz do okolo 700 px maksymalnego boku. Do projektu i obrony to wystarczy.

---

## 11. Ktore pliki oddac

Do systemu GID najlepiej wrzucic caly ZIP:

```text
Projekt_MII_Daniel.zip
```

W srodku jest kod zrodlowy, dokumentacja, przyklady obrazow oraz instrukcja uruchomienia.
