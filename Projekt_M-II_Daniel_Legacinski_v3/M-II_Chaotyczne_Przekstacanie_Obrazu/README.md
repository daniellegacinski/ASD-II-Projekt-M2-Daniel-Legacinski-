# Projekt M-II — Chaotyczne przekształcanie obrazu cyfrowego

**Autor:** Daniel Legaciński  
**Temat:** Projekt M-II — chaotyczne przekształcanie obrazu cyfrowego  
**Charakter projektu:** eksperyment dydaktyczny, a nie prawdziwy system kryptograficzny

---

## 1. Co zawiera projekt

Ten projekt jest kompletną aplikacją w Pythonie z graficznym interfejsem użytkownika. Program pozwala wczytać obraz, wykonać jego przekształcenie metodą scramblingu, a następnie spróbować odtworzyć obraz poprawnym albo błędnym kluczem.

Projekt realizuje wszystkie główne wymagania z instrukcji:

1. **Etap 1 — naiwny scrambling**  
   Proste, odwracalne przesuwanie wierszy i kolumn obrazu. Ten etap specjalnie pokazuje słabość prostej metody, bo część struktury obrazu może nadal zostać widoczna.

2. **Etap 2 — czysta permutacja sterowana kluczem**  
   Piksele są przestawiane za pomocą permutacji Fishera-Yatesa sterowanej własnym generatorem LCG. Wartości pikseli nie są zmieniane, zmienia się tylko ich pozycja.

3. **Etap 3 — mechanizm wzmacniający**  
   Hybryda: najpierw wykonywana jest permutacja pikseli, a potem dodatkowa odwracalna substytucja modularna wartości pikseli. Ten etap mocniej niszczy widoczną strukturę obrazu, ale nadal nie jest bezpiecznym szyfrem.

4. **Scrambling i unscrambling**  
   Każdy etap ma funkcję przekształcającą obraz oraz osobną funkcję odwracającą.

5. **Test poprawnego i błędnego klucza**  
   GUI pozwala odtworzyć obraz poprawnym kluczem oraz kluczem błędnym różniącym się dopiskiem `_blad`.

6. **Metryki eksperymentalne**  
   Program liczy korelację sąsiednich pikseli przed i po scramblingu oraz różnice między oryginałem i obrazem odtworzonym.

7. **Zapis wyników**  
   Wyniki można zapisać do folderu `outputs`.

8. **Gotowe obrazy testowe**  
   Program zawiera obraz strukturalny oraz obraz naturalny, aby można było szybko wykonać eksperyment bez szukania własnych plików.

---

## 2. Struktura folderów

Po rozpakowaniu ZIP powinieneś zobaczyć mniej więcej taką strukturę:

```text
M-II_Chaotyczne_Przekstacanie_Obrazu/
│
├── run_gui.py
├── run_experiments.py
├── test_reversibility.py
├── requirements.txt
├── START_WINDOWS.bat
├── START_LINUX_MAC.sh
├── README.md
│
├── scrambler/
│   ├── __init__.py
│   ├── algorithms.py
│   └── metrics.py
│
├── assets/
│   └── samples/
│       ├── sample_natural.png
│       └── sample_structured.png
│
├── outputs/
│   └── tutaj zapisują się wyniki
│
└── docs/
    ├── Dokumentacja_Projekt_M-II_Daniel_Legacinski.docx
    └── Dokumentacja_Projekt_M-II_Daniel_Legacinski.pdf
```

Najważniejsze pliki:

- `run_gui.py` — główny program z ładnym interfejsem graficznym.
- `scrambler/algorithms.py` — wszystkie algorytmy scramblingu i unscramblingu.
- `scrambler/metrics.py` — metryki do analizy wyników.
- `run_experiments.py` — uruchomienie pełnych eksperymentów bez GUI.
- `test_reversibility.py` — test, czy algorytmy są odwracalne.
- `README.md` — ten opis.
- `docs/` — dokumentacja projektu.

---

## 3. Instalacja i uruchomienie

### 3.1. Najprostszy sposób na Windows

1. Rozpakuj plik ZIP.
2. Wejdź do folderu projektu.
3. Kliknij dwa razy plik:

```text
START_WINDOWS.bat
```

Ten plik uruchamia aplikację GUI.

### 3.2. Uruchomienie ręczne

Otwórz terminal w folderze projektu i wpisz:

```bash
pip install -r requirements.txt
python run_gui.py
```

Jeżeli na komputerze działa komenda `python3`, możesz użyć:

```bash
pip install -r requirements.txt
python3 run_gui.py
```

---

## 4. Wymagane biblioteki

Projekt używa:

- `Pillow` — wczytywanie i zapisywanie obrazów,
- `numpy` — szybka praca na tablicach pikseli,
- `matplotlib` — wykres korelacji w eksperymentach,
- `tkinter` — interfejs graficzny, zwykle jest razem z Pythonem.

Wszystko oprócz `tkinter` jest w pliku `requirements.txt`.

---

## 5. Dokładny opis interfejsu GUI

Po uruchomieniu programu zobaczysz aplikację podzieloną na kilka części.

Lewa część służy do sterowania eksperymentem. Prawa część pokazuje obrazy i wyniki metryk.

---

## 6. Opis każdego klawisza i pola w GUI

### 6.1. Klawisz `Wczytaj obraz PNG / JPEG / BMP`

Ten klawisz służy do wybrania własnego obrazu z komputera.

Obsługiwane formaty:

- PNG,
- JPG,
- JPEG,
- BMP.

Po kliknięciu otworzy się okno wyboru pliku. Po wybraniu obrazu program wczyta go jako obraz oryginalny. Obraz zostanie pokazany w pierwszym panelu po prawej stronie.

Program automatycznie zmniejsza bardzo duży obraz do rozmiaru roboczego, żeby eksperyment działał szybko nawet na słabszym komputerze. To nie psuje sensu projektu, bo algorytmy działają na pikselach tak samo.

---

### 6.2. Klawisz `Szachownica / tekst`

Ten klawisz wczytuje gotowy obraz testowy o silnej strukturze.

Ten obraz zawiera:

- szachownicę,
- linie pionowe i poziome,
- tekst,
- wyraźne krawędzie.

Jest to bardzo dobry obraz do pokazania, że proste metody scramblingu są słabe. Na przykład w Etapie 1 po przekształceniu nadal mogą być widoczne fragmenty struktury.

Ten obraz jest szczególnie przydatny do obrony projektu, bo łatwo wytłumaczyć, jakie informacje nadal może odzyskać osoba atakująca.

---

### 6.3. Klawisz `Obraz naturalny`

Ten klawisz wczytuje drugi gotowy obraz testowy, który bardziej przypomina naturalną fotografię.

Ten obraz ma:

- płynne przejścia kolorów,
- kształty,
- mniej regularną strukturę niż szachownica.

Ten obraz służy do porównania, jak algorytmy zachowują się na danych mniej regularnych.

W dokumentacji wymagane jest porównanie obrazu naturalnego i obrazu o silnej strukturze, dlatego te dwa przykłady są od razu dodane do projektu.

---

### 6.4. Pole `Etap algorytmu`

To pole wybiera, jaki algorytm ma zostać użyty.

Dostępne są trzy opcje:

#### `1 - naiwny scrambling`

To pierwszy etap projektu. Działa przez przesuwanie wierszy i kolumn obrazu.

Cechy:

- jest odwracalny,
- używa klucza i parametru,
- nie używa chaosu ani kryptografii,
- często pozostawia widoczne struktury obrazu.

Ten etap jest nazywany etapem porażki, bo pokazuje, że proste przekształcenie nie daje dobrego ukrycia struktury.

#### `2 - czysta permutacja`

To drugi etap projektu. Program tworzy permutację pikseli zależną od klucza.

Cechy:

- wartości pikseli nie zmieniają się,
- zmienia się tylko pozycja pikseli,
- permutacja jest sterowana kluczem,
- istnieje jawna funkcja odwrotna.

Ten etap jest lepszy niż Etap 1, ale nadal nie jest bezpiecznym szyfrem, bo histogram kolorów pozostaje taki sam.

#### `3 - hybryda permutacja + substytucja`

To trzeci etap projektu. Rozszerza Etap 2 o dodatkowy mechanizm wzmacniający.

Cechy:

- najpierw zmienia kolejność pikseli,
- potem zmienia wartości pikseli przez dodanie strumienia modulo 256,
- operacja jest odwracalna,
- błędny klucz powoduje wyraźnie błędny wynik.

Ten etap najlepiej pokazuje efekt lawinowy w ramach projektu dydaktycznego, ale nadal nie jest prawdziwym szyfrem kryptograficznym.

---

### 6.5. Pole `Klucz tekstowy`

W tym polu wpisujesz klucz.

Przykład:

```text
Daniel-2026
```

Klucz wpływa na:

- przesunięcia w Etapie 1,
- permutację w Etapie 2,
- permutację i substytucję w Etapie 3.

W programie klucz jest zamieniany na liczbę `seed`. Na podstawie tego seedu generator LCG tworzy deterministyczną sekwencję wartości. To znaczy, że dla tego samego klucza i parametru wynik będzie zawsze taki sam.

Jeżeli zmienisz nawet mały fragment klucza, wynik może się zmienić. Właśnie dlatego w GUI jest osobny klawisz do testowania błędnego klucza.

---

### 6.6. Pole `Parametr`

To dodatkowa liczba, która zmienia zachowanie algorytmu.

W Etapie 1 parametr wpływa na sposób przesuwania wierszy i kolumn.

W Etapie 2 parametr wpływa na seed permutacji.

W Etapie 3 parametr wpływa na permutację i na strumień wartości używany przy substytucji.

Przykładowe wartości:

```text
7
13
25
123
```

Jeżeli zmienisz parametr, program może dać zupełnie inny wynik nawet przy tym samym kluczu.

---

### 6.7. Pole `Rundy Etapu 3`

To pole ma znaczenie głównie dla Etapu 3.

Rundy oznaczają, ile razy zostanie powtórzona sekwencja:

```text
permutacja → substytucja
```

Przykład:

- 1 runda — szybciej, ale słabiej miesza obraz,
- 2 rundy — domyślna wartość,
- 3 lub więcej rund — mocniejsze przekształcenie, ale wolniejsze działanie.

W programie liczba rund jest ograniczona, żeby przypadkowo nie spowolnić aplikacji.

---

### 6.8. Klawisz `Scramble — przekształć obraz`

To jeden z najważniejszych klawiszy.

Po kliknięciu program:

1. bierze obraz oryginalny,
2. sprawdza wybrany etap,
3. bierze klucz, parametr i liczbę rund,
4. wykonuje scrambling,
5. pokazuje wynik w środkowym panelu,
6. liczy metryki korelacji.

Po wykonaniu tej operacji w GUI widzisz:

- oryginał po lewej,
- obraz przekształcony w środku,
- pusty albo poprzedni obraz odtworzony po prawej.

Ten klawisz odpowiada funkcji `scramble_image()` z pliku `scrambler/algorithms.py`.

---

### 6.9. Klawisz `Unscramble — poprawny klucz`

Ten klawisz próbuje odtworzyć obraz z użyciem poprawnego klucza.

Po kliknięciu program:

1. bierze obraz przekształcony,
2. używa tego samego etapu,
3. używa tego samego klucza,
4. używa tego samego parametru,
5. wykonuje funkcję odwrotną,
6. pokazuje wynik w prawym panelu.

Jeżeli wszystko działa poprawnie, obraz odtworzony powinien być identyczny z oryginałem.

W metrykach powinno wtedy być:

```text
Obrazy identyczne: True
MSE: 0
MAE: 0
Maksymalna różnica piksela: 0
```

To jest najważniejszy dowód, że algorytm jest odwracalny.

---

### 6.10. Klawisz `Unscramble — błędny klucz`

Ten klawisz wykonuje bardzo ważny test z instrukcji projektu.

Program bierze poprawny klucz, ale dopisuje do niego:

```text
_blad
```

Przykład:

```text
Daniel-2026
```

zamienia się na:

```text
Daniel-2026_blad
```

Następnie program próbuje odtworzyć obraz tym błędnym kluczem.

Ten test pokazuje:

- jak algorytm reaguje na zmianę klucza,
- czy występuje efekt lawinowy,
- czy wynik przy błędnym kluczu mocno różni się od oryginału,
- dlaczego poprawny klucz jest konieczny do odtworzenia.

W Etapie 1 efekt może być słabszy, bo metoda jest bardzo prosta. W Etapie 2 i 3 różnica powinna być dużo bardziej widoczna.

---

### 6.11. Klawisz `Zapisz`

Ten klawisz zapisuje aktualnie widoczne wyniki.

Po kliknięciu program tworzy folder w `outputs`, na przykład:

```text
outputs/manual_20260424_121500/
```

W tym folderze mogą znaleźć się pliki:

```text
original.png
scrambled.png
restored.png
metrics.txt
```

Znaczenie plików:

- `original.png` — obraz wejściowy,
- `scrambled.png` — obraz po przekształceniu,
- `restored.png` — obraz odtworzony,
- `metrics.txt` — wyniki metryk widoczne w GUI.

Ten klawisz jest przydatny, jeżeli chcesz zapisać konkretny przypadek do dokumentacji albo pokazać go wykładowcy.

---

### 6.12. Klawisz `Pełne eksperymenty`

Ten klawisz wykonuje automatycznie pełny zestaw testów.

Program testuje:

- obraz naturalny,
- obraz strukturalny,
- Etap 1,
- Etap 2,
- Etap 3,
- odtwarzanie poprawnym kluczem,
- odtwarzanie błędnym kluczem.

Po kliknięciu program tworzy folder w `outputs`, na przykład:

```text
outputs/experiments_20260424_121800/
```

W środku znajdują się:

- obrazy oryginalne,
- obrazy po scramblingu,
- obrazy odtworzone poprawnym kluczem,
- obrazy odtworzone błędnym kluczem,
- plik `metrics.csv`,
- wykres `correlation_chart.png`.

Ten klawisz jest najlepszy do szybkiego wygenerowania materiałów do dokumentacji.

---

### 6.13. Klawisz `Wyczyść wynik`

Ten klawisz usuwa obraz przekształcony i odtworzony z GUI, ale zostawia obraz oryginalny.

Użyj go, gdy chcesz wykonać nowy test na tym samym obrazie, ale z innymi parametrami.

Po kliknięciu:

- pierwszy panel zostaje bez zmian,
- drugi panel zostaje wyczyszczony,
- trzeci panel zostaje wyczyszczony,
- metryki są resetowane.

---

### 6.14. Klawisz `Otwórz outputs`

Ten klawisz próbuje otworzyć folder z wynikami.

Jeżeli wcześniej wykonano `Zapisz` albo `Pełne eksperymenty`, program otworzy ostatnio utworzony folder.

Jeżeli jeszcze nic nie zapisano, program otworzy ogólny folder:

```text
outputs
```

Jest to wygodne, bo nie trzeba ręcznie szukać plików wynikowych.

---

## 7. Co oznaczają trzy panele obrazów

### 7.1. `1. Obraz oryginalny`

To obraz wejściowy. Jest to punkt odniesienia do porównania wyników.

### 7.2. `2. Obraz przekształcony`

To obraz po wykonaniu funkcji scramblingu. Ten obraz powinien wyglądać mniej czytelnie niż oryginał.

W Etapie 1 może nadal przypominać oryginał albo zachowywać strukturę. To jest celowe i pokazuje słabość metody.

### 7.3. `3. Obraz odtworzony`

To wynik funkcji odwrotnej. Jeżeli użyto poprawnego klucza, obraz powinien wrócić do oryginału.

Jeżeli użyto błędnego klucza, obraz powinien być uszkodzony albo zupełnie niepodobny do oryginału.

---

## 8. Zakładka `Metryki i wynik`

W tej zakładce program pokazuje liczby potrzebne do analizy eksperymentalnej.

Najważniejsze wartości:

### `Korelacja pozioma przed scramblingiem`

Pokazuje, jak bardzo sąsiednie piksele w poziomie są podobne w obrazie oryginalnym.

W naturalnych obrazach ta wartość zwykle jest wysoka, bo sąsiednie piksele często mają podobne kolory.

### `Korelacja pozioma po scramblingu`

Pokazuje, czy po przekształceniu sąsiednie piksele nadal są podobne.

Jeżeli scrambling działa dobrze eksperymentalnie, ta wartość powinna spaść.

### `Korelacja pionowa przed scramblingiem`

Analogiczna metryka, ale dla sąsiadów pionowych.

### `Korelacja pionowa po scramblingu`

Pokazuje, czy struktura pionowa została zniszczona.

### `Obrazy identyczne`

Jeżeli użyto poprawnego klucza i algorytm jest dobrze odwracalny, powinno być:

```text
True
```

### `MSE`

Mean Squared Error, czyli średni błąd kwadratowy.

Dla poprawnie odtworzonego obrazu powinno być:

```text
0
```

Dla błędnego klucza powinno być więcej niż 0.

### `MAE`

Mean Absolute Error, czyli średni błąd bezwzględny.

Dla poprawnego odtworzenia powinno być:

```text
0
```

### `Maksymalna różnica piksela`

Pokazuje największą różnicę wartości pojedynczego kanału koloru.

Dla poprawnego odtworzenia powinno być:

```text
0
```

---

## 9. Zakładka `Opis klawiszy`

Ta zakładka jest krótką pomocą wbudowaną w program. Zawiera skrócony opis najważniejszych przycisków.

Pełny opis znajduje się w tym pliku README.

---

## 10. Opis algorytmów

### 10.1. Etap 1 — naiwny scrambling

Etap 1 wykonuje przesunięcia wierszy i kolumn.

Najpierw każdy wiersz jest przesuwany o określoną liczbę pozycji. Potem każda kolumna jest przesuwana o określoną liczbę pozycji.

Przesunięcie zależy od:

- klucza,
- parametru,
- numeru wiersza albo kolumny.

Funkcja odwrotna działa w odwrotnej kolejności:

1. najpierw cofa przesunięcia kolumn,
2. potem cofa przesunięcia wierszy.

To jest ważne, bo jeżeli operacje wykonano w kolejności A → B, to odwracanie musi iść w kolejności B⁻¹ → A⁻¹.

Słabość tej metody:

- zachowuje lokalne fragmenty obrazu,
- linie i regularne struktury mogą nadal być widoczne,
- nie daje dobrego efektu lawinowego,
- łatwo zauważyć, że to tylko przesunięcia.

---

### 10.2. Etap 2 — czysta permutacja

Etap 2 traktuje obraz jako listę pikseli.

Dla obrazu o wymiarach:

```text
szerokość = W
wysokość = H
```

liczba pikseli wynosi:

```text
N = W * H
```

Program tworzy permutację:

```text
P: {0, ..., N-1} -> {0, ..., N-1}
```

Następnie piksele są przestawiane według tej permutacji.

Do generowania permutacji użyto algorytmu Fishera-Yatesa i własnego prostego generatora LCG.

Funkcja odwrotna tworzy tę samą permutację z tego samego klucza, a potem odwraca pozycje pikseli.

Słabość tej metody:

- wartości pikseli nie zmieniają się,
- histogram kolorów zostaje taki sam,
- jeśli ktoś zna część oryginału, może próbować analizować odpowiadające piksele,
- nie jest to bezpieczny szyfr.

---

### 10.3. Etap 3 — mechanizm wzmacniający

Etap 3 jest hybrydą:

```text
permutacja + substytucja modularna
```

Dla każdej rundy program wykonuje:

1. permutację pikseli,
2. wygenerowanie strumienia wartości 0–255,
3. dodanie tego strumienia do wartości pikseli modulo 256.

Dodawanie modulo 256 oznacza, że wartości zawijają się w zakresie 0–255.

Przykład:

```text
250 + 10 = 260
260 mod 256 = 4
```

Funkcja odwrotna robi odwrotnie:

1. odejmuje strumień modulo 256,
2. odwraca permutację.

Ważna zasada:

Jeżeli w scramblingu było:

```text
P -> S
```

czyli permutacja, potem substytucja, to w unscramblingu musi być:

```text
S^-1 -> P^-1
```

czyli najpierw cofnięcie substytucji, a potem cofnięcie permutacji.

---

## 11. Dlaczego projekt NIE jest bezpiecznym szyfrem

Ten projekt nie jest kryptograficzny. To jest bardzo ważne i trzeba to powiedzieć podczas obrony.

Powody:

1. **LCG nie jest bezpiecznym generatorem losowym**  
   Generator LCG jest prosty i przewidywalny. Nadaje się do eksperymentu, ale nie do bezpieczeństwa.

2. **Etap 1 zachowuje dużo struktury**  
   Przesuwanie wierszy i kolumn nie niszczy całkowicie informacji o obrazie.

3. **Etap 2 nie zmienia wartości pikseli**  
   Histogram kolorów zostaje zachowany, więc część informacji statystycznej nadal istnieje.

4. **Etap 3 jest lepszy wizualnie, ale nadal nie jest standardem kryptografii**  
   Nie ma formalnego dowodu bezpieczeństwa. Nie używa sprawdzonych algorytmów takich jak AES.

5. **Atak known-plaintext może pomóc odzyskać strukturę**  
   Jeżeli atakujący zna oryginalny obraz i jego wersję przekształconą, może próbować odtworzyć permutację albo strumień wartości.

6. **Wizualny chaos nie oznacza bezpieczeństwa**  
   Obraz może wyglądać losowo, ale algorytm może być matematycznie słaby.

---

## 12. Co powiedzieć na obronie projektu

Możesz powiedzieć tak:

> Projekt pokazuje trzy poziomy przekształcania obrazu cyfrowego. Pierwszy etap jest bardzo prosty i celowo słaby, bo przesuwa tylko wiersze i kolumny. Drugi etap używa permutacji pikseli sterowanej kluczem, więc lepiej miesza obraz, ale nie zmienia wartości kolorów. Trzeci etap dodaje mechanizm wzmacniający, czyli substytucję modularną wartości pikseli. Każdy etap jest odwracalny przy poprawnym kluczu. Program pozwala też sprawdzić błędny klucz i porównać metryki, takie jak korelacja sąsiednich pikseli oraz różnica między obrazem oryginalnym i odtworzonym. Najważniejszy wniosek jest taki, że wizualny chaos nie oznacza bezpieczeństwa kryptograficznego.

---

## 13. Jak wykonać eksperyment krok po kroku

1. Uruchom `run_gui.py`.
2. Kliknij `Szachownica / tekst`.
3. Wybierz `1 - naiwny scrambling`.
4. Kliknij `Scramble`.
5. Zobacz, czy struktura obrazu nadal jest widoczna.
6. Kliknij `Unscramble — poprawny klucz`.
7. Sprawdź, czy obraz wrócił do oryginału.
8. Kliknij `Unscramble — błędny klucz`.
9. Zobacz, jak zmienił się wynik.
10. Powtórz dla Etapu 2 i Etapu 3.
11. Kliknij `Pełne eksperymenty`.
12. Otwórz folder `outputs`.
13. Użyj zapisanych obrazów i metryk w dokumentacji albo przy obronie.

---

## 14. Uruchomienie eksperymentów bez GUI

Można też uruchomić testy bez interfejsu:

```bash
python run_experiments.py
```

Wyniki pojawią się w folderze:

```text
outputs/experiments_cli_*
```

Ten tryb jest dobry, jeżeli chcesz szybko wygenerować komplet wyników automatycznie.

---

## 15. Test odwracalności

Aby sprawdzić, czy wszystkie etapy poprawnie odtwarzają obraz, uruchom:

```bash
python test_reversibility.py
```

Test powinien potwierdzić, że:

```text
unscramble(scramble(image)) == image
```

przy poprawnym kluczu.

---

## 16. Najczęstsze problemy

### Problem: `ModuleNotFoundError: No module named PIL`

Rozwiązanie:

```bash
pip install -r requirements.txt
```

### Problem: program się nie uruchamia po dwukliku

Uruchom przez terminal:

```bash
python run_gui.py
```

Wtedy zobaczysz dokładny błąd.

### Problem: obraz jest bardzo duży i program działa wolno

Program zmniejsza obraz roboczo, ale przy bardzo dużych plikach nadal może chwilę działać. Najlepiej używać obrazów testowych albo zdjęć średniej wielkości.

### Problem: folder outputs jest pusty

Musisz kliknąć `Zapisz` albo `Pełne eksperymenty`. Dopiero wtedy program zapisze pliki wynikowe.

---

## 17. Krótkie podsumowanie

Projekt jest gotowym narzędziem do pokazania:

- różnicy między prostym scramblingiem i permutacją,
- roli klucza i parametru,
- działania funkcji odwrotnej,
- wpływu błędnego klucza,
- różnicy między chaosem wizualnym a prawdziwym bezpieczeństwem,
- metryk eksperymentalnych dla obrazu cyfrowego.

Najważniejszy wniosek:

**To, że obraz wygląda losowo, nie oznacza, że algorytm jest bezpiecznym szyfrem.**
