# Dokumentacja projektu M-II

**Temat:** Chaotyczne przeksztalcanie obrazu cyfrowego  
**Autor:** Daniel Legacinski  
**Technologia:** Python, NumPy, Pillow, Tkinter  

## 1. Cel projektu

Celem projektu jest zbudowanie programu, ktory pokazuje w praktyce mechanizmy przeksztalcania obrazu cyfrowego. Projekt nie ma tworzyc bezpiecznego algorytmu szyfrowania. Najwazniejszym celem jest zrozumienie, czym rozni sie permutacja od substytucji oraz dlaczego obraz wygladajacy losowo nie oznacza automatycznie bezpieczenstwa danych.

Projekt realizuje trzy etapy. Etap pierwszy jest celowo prosty i ma pokazac porazke naiwnego podejscia. Etap drugi realizuje czysta permutacje pikseli sterowana kluczem. Etap trzeci dodaje mechanizm wzmacniajacy, czyli hybryde permutacji i substytucji.

W projekcie dla kazdego etapu istnieje osobny algorytm scramblingu i osobny algorytm unscramblingu. Odtworzenie obrazu jest mozliwe tylko na podstawie obrazu wynikowego oraz tego samego klucza i parametru. Program nie zapisuje dodatkowych map pomocniczych do odtwarzania obrazu.

## 2. Wybor technologii

Do wykonania projektu wybrano jezyk Python. Powod jest praktyczny: Python pozwala latwo operowac na obrazach jako tablicach pikseli i szybko zbudowac interfejs graficzny.

Wykorzystane biblioteki:

- NumPy - reprezentacja obrazu jako tablicy oraz szybkie operacje na pikselach,
- Pillow - wczytywanie i zapisywanie obrazow PNG, JPG i BMP,
- Tkinter - graficzny interfejs uzytkownika,
- hashlib - stabilne przeksztalcenie klucza tekstowego na liczbe seed.

Projekt nie korzysta z gotowych algorytmow kryptograficznych. Generator pseudolosowy LCG oraz permutacja Fisher-Yates zostaly zapisane jawnie w kodzie.

## 3. Reprezentacja obrazu

Obraz jest wczytywany jako obraz RGB. Po wczytaniu jest zamieniany na tablice NumPy o ksztalcie:

```text
wysokosc x szerokosc x 3
```

Trzeci wymiar oznacza kanaly koloru: R, G i B. Kazda wartosc piksela jest liczba calkowita z zakresu 0-255.

Taka reprezentacja pozwala latwo traktowac obraz jako zbior pikseli, ktory mozna przesuwac, permutowac albo modyfikowac matematycznie.

## 4. Klucz i seed

Uzytkownik wpisuje klucz tekstowy, na przyklad:

```text
Daniel-MII-2026
```

Klucz jest zamieniany na liczbe seed przy pomocy funkcji SHA-256. Uzycie SHA-256 nie oznacza, ze projekt staje sie kryptograficzny. Funkcja sluzy tutaj tylko do stabilnego przeksztalcenia napisu na liczbe.

Dla tego samego klucza program zawsze generuje ten sam seed. Dzieki temu permutacja i maska moga byc odtworzone podczas unscramblingu.

## 5. Generator pseudolosowy LCG

W projekcie zastosowano prosty generator LCG:

```text
state = (1664525 * state + 1013904223) mod 2^32
```

Generator ten jest deterministyczny. To znaczy, ze dla tego samego seeda generuje dokladnie taki sam ciag liczb. Jest to przydatne w projekcie, poniewaz algorytm odwrotny musi odtworzyc te same przesuniecia, permutacje i maski.

LCG nie jest bezpieczny kryptograficznie. Jest przewidywalny i nie powinien byc stosowany do ochrony prawdziwych danych. W projekcie jest uzyty tylko dydaktycznie.

## 6. Etap 1 - naiwny scrambling

Etap 1 polega na cyklicznym przesuwaniu kazdego wiersza obrazu. Dla kazdego wiersza obliczane jest przesuniecie zalezne od klucza i numeru wiersza.

Przyklad idei:

```text
wiersz y zostaje przesuniety o shift(y)
```

Algorytm scramblingu:

1. Wczytaj obraz jako tablice pikseli.
2. Oblicz seed z klucza.
3. Dla kazdego wiersza oblicz przesuniecie.
4. Przesun wiersz cyklicznie w prawo.
5. Zwroc obraz wynikowy.

Algorytm odwrotny:

1. Wczytaj obraz scrambled.
2. Oblicz ten sam seed z klucza.
3. Dla kazdego wiersza oblicz to samo przesuniecie.
4. Przesun wiersz cyklicznie w lewo.
5. Zwroc obraz odtworzony.

Etap 1 jest w pelni odwracalny, poniewaz przesuniecie cykliczne mozna cofnac przesunieciem w przeciwna strone.

## 7. Slabosc Etapu 1

Etap 1 jest celowo slaby. W obrazie po przeksztalceniu czesto nadal widac strukture. Dzieje sie tak dlatego, ze piksele w ramach jednego wiersza pozostaja w tym samym wierszu. Zmieniana jest tylko ich pozycja pozioma.

W przypadku obrazu naturalnego moga dalej byc widoczne pasy kolorow albo ogolny uklad sceny. W przypadku obrazu o silnej strukturze, na przyklad szachownicy albo tekstu, fragmenty wzoru moga nadal byc rozpoznawalne.

Ten etap pokazuje, ze sama odwracalnosc nie oznacza bezpieczenstwa. Algorytm moze dzialac poprawnie technicznie, ale nadal byc bardzo slaby analitycznie.

## 8. Etap 2 - czysta permutacja sterowana kluczem

Etap 2 realizuje czysta permutacje pikseli. Oznacza to, ze wartosci pikseli nie sa zmieniane. Zmieniane sa tylko ich miejsca.

Obraz jest splaszczany do listy pikseli:

```text
0, 1, 2, ..., N-1
```

Nastepnie generowana jest permutacja P zbioru indeksow. Permutacja jest tworzona algorytmem Fisher-Yates sterowanym generatorem LCG z klucza.

Formalnie:

```text
P : {0, ..., N-1} -> {0, ..., N-1}
```

Scrambling polega na ustawieniu pikseli wedlug permutacji:

```text
scrambled[i] = original[P[i]]
```

## 9. Funkcja odwrotna Etapu 2

Dla permutacji P istnieje permutacja odwrotna P^-1. Program tworzy ja jawnie:

```text
inv[P[i]] = i
```

Unscrambling korzysta z tej samej permutacji wygenerowanej z klucza, a potem z permutacji odwrotnej. Dzieki temu:

```text
P^-1(P(i)) = i
```

Jezeli klucz jest poprawny, obraz zostaje odtworzony idealnie. Jezeli klucz rozni sie minimalnie, permutacja jest inna i odtworzenie nie dziala.

## 10. Analiza Etapu 2

Etap 2 niszczy lokalne sasiedztwo pikseli znacznie mocniej niz Etap 1. Korelacja sasiednich pikseli po scramblingu powinna spasc, poniewaz piksele obok siebie w obrazie wynikowym zwykle pochodza z odleglych miejsc obrazu oryginalnego.

Jednoczesnie sama permutacja nie zmienia wartosci pikseli. Histogram kolorow pozostaje taki sam jak w oryginale. To jest wazna wada z punktu widzenia bezpieczenstwa. Atakujacy moze dalej analizowac rozklad kolorow, dominujace barwy i inne cechy statystyczne.

Etap 2 moze miec efekt podobny do lawinowego wizualnie, bo mala zmiana klucza powoduje inna permutacje. Jednak nie jest to pelny kryptograficzny efekt lawinowy, bo wartosci pikseli nie sa mieszane bitowo w sposob kontrolowany jak w prawdziwych szyfrach.

## 11. Etap 3 - mechanizm wzmacniajacy

W Etapie 3 zastosowano hybryde:

1. permutacja pikseli,
2. substytucja wartosci pikseli modulo 256.

Najpierw obraz jest permutowany podobnie jak w Etapie 2. Potem dla kazdej wartosci kanalu RGB generowana jest maska bajtowa z zakresu 0-255. Maska zalezy od klucza i parametru.

Funkcja substytucji:

```text
f(p, k) = (p + m(k)) mod 256
```

Funkcja odwrotna:

```text
f^-1(c, k) = (c - m(k)) mod 256
```

Gdzie:

- p - wartosc piksela przed substytucja,
- c - wartosc po substytucji,
- m(k) - wartosc maski wygenerowana z klucza.

## 12. Algorytm odwrotny Etapu 3

Kolejnosc odwrotna jest bardzo wazna. Skoro scrambling wykonuje:

```text
permutacja -> substytucja
```

To unscrambling musi wykonac:

```text
odwrotna substytucja -> odwrotna permutacja
```

Algorytm odwrotny:

1. Wygeneruj te sama maske z klucza i parametru.
2. Odejmij maske modulo 256.
3. Wygeneruj ta sama permutacje z klucza.
4. Zastosuj permutacje odwrotna.
5. Otrzymaj obraz oryginalny.

Przy poprawnym kluczu obraz wraca idealnie. Przy blednym kluczu maska i permutacja sa inne, wiec obraz nie zostaje odtworzony.

## 13. Interfejs GUI

Aplikacja ma graficzny interfejs uzytkownika przygotowany do eksperymentow. GUI pozwala:

- wczytac obraz PNG, JPG lub BMP,
- wybrac Etap 1, Etap 2 albo Etap 3,
- wpisac klucz poprawny,
- wpisac klucz bledny,
- wpisac parametr,
- wykonac Scramble,
- wykonac Unscramble,
- szybko przelaczyc poprawny i bledny klucz,
- zobaczyc jednoczesnie obraz oryginalny, przeksztalcony i odtworzony,
- obliczyc metryki,
- zapisac wyniki eksperymentu.

GUI jest narzedziem analitycznym, poniewaz od razu pokazuje roznice miedzy etapami i umozliwia porownanie wynikow.

## 14. Obrazy testowe

W projekcie dodano trzy przykladowe obrazy:

1. `natural_like.png` - obraz przypominajacy naturalny krajobraz,
2. `checker_text.png` - obraz o silnej strukturze,
3. `gradient.png` - gradient z siatka.

Obraz naturalny pozwala sprawdzic, jak algorytm dziala na gladkich przejsciach i typowych strukturach wizualnych. Obraz strukturalny pozwala zobaczyc, czy metoda zostawia widoczne wzory. Gradient pomaga analizowac rozklad kolorow i lokalne przejscia.

## 15. Metryka: korelacja sasiednich pikseli

Jedna z obowiazkowych metryk to korelacja sasiednich pikseli. Program liczy korelacje pozioma i pionowa w skali szarosci.

Dla obrazu naturalnego korelacja przed scramblingiem zwykle jest wysoka, bo sasiednie piksele maja podobne kolory. Po skuteczniejszym mieszaniu korelacja powinna spasc.

Interpretacja:

- korelacja bliska 1 - sasiednie piksele sa bardzo podobne,
- korelacja bliska 0 - brak wyraznej zaleznosci,
- spadek korelacji po scramblingu oznacza utrate lokalnej struktury.

## 16. Metryka: roznica przy blednym kluczu

Druga metryka to roznica obrazu po probie odtworzenia blednym kluczem. Program liczy:

- MAE - sredni blad bezwzgledny,
- MSE - sredni blad kwadratowy.

Jezeli bledny klucz daje duzy blad, oznacza to, ze algorytm jest wrazliwy na klucz. Nie oznacza to jednak automatycznie bezpieczenstwa kryptograficznego.

## 17. Porownanie etapow

Etap 1:

- bardzo prosty,
- w pelni odwracalny,
- zostawia duzo struktury,
- slaby jako ochrona.

Etap 2:

- miesza polozenia pikseli,
- jest odwracalny przez permutacje odwrotna,
- mocniej niszczy strukture lokalna,
- nie zmienia wartosci pikseli.

Etap 3:

- laczy permutacje i substytucje,
- zmienia polozenia i wartosci pikseli,
- daje najlepszy efekt wizualny w projekcie,
- nadal nie jest prawdziwym szyfrem.

## 18. Dlaczego moje rozwiazanie NIE jest bezpiecznym szyfrem

### 18.1. Jakie informacje atakujacy nadal moze odzyskac?

W Etapie 1 atakujacy moze zobaczyc ogolne struktury obrazu, poniewaz wiersze pozostaja wierszami. Jezeli obraz zawiera tekst, krawedzie albo regularne wzory, czesc informacji moze byc rozpoznawalna.

W Etapie 2 wartosci pikseli nie sa zmieniane. Oznacza to, ze histogram kolorow pozostaje taki sam. Atakujacy moze analizowac dominujace kolory i rozklad jasnosci.

W Etapie 3 wartosci sa modyfikowane, ale generator LCG i prosta maska modulo 256 nie zapewniaja bezpieczenstwa kryptograficznego. Algorytm jest deterministyczny i zbyt prosty.

### 18.2. Co dzieje sie przy ataku known-plaintext?

Known-plaintext oznacza, ze atakujacy zna pare: obraz oryginalny i odpowiadajacy mu obraz przeksztalcony. W takim przypadku moze probowac odtworzyc permutacje albo maske.

Dla Etapu 2, jezeli atakujacy zna oryginal i wynik, moze analizowac, gdzie przeniesiono konkretne piksele. Przy obrazach z unikalnymi wartosciami pikseli odzyskanie duzej czesci permutacji jest latwiejsze.

Dla Etapu 3 znana para moze ujawnic maske po odjeciu wartosci przed i po substytucji, szczegolnie jezeli permutacja zostanie odgadnieta lub odtworzona.

### 18.3. Dlaczego zwiekszanie chaosu nie rozwiazuje problemu?

Chaos wizualny oznacza, ze obraz wyglada losowo. Nie oznacza to, ze algorytm spelnia wymagania kryptografii. Bezpieczny szyfr musi byc odporny na rozne ataki, miec dobrze zbadane wlasciwosci i nie ujawniac prostych zaleznosci.

W projekcie mechanizmy sa odwracalne i deterministyczne, ale sa zbyt proste. Wieksze mieszanie obrazu moze poprawic wyglad wyniku, ale nie usuwa problemow takich jak przewidywalny generator, brak uwierzytelniania, brak analizy kryptograficznej i mozliwosc ataku known-plaintext.

## 19. Wnioski koncowe

Projekt pokazuje, ze poprawne odtworzenie obrazu i losowy wyglad wyniku to za malo, aby mowic o bezpiecznym szyfrowaniu. Etap 1 pokazuje slabosc prostych przesuniec. Etap 2 pokazuje sile i ograniczenia czystej permutacji. Etap 3 pokazuje, ze dodanie substytucji poprawia efekt wizualny, ale nadal nie tworzy bezpiecznego szyfru.

Najwazniejszy wniosek brzmi: wizualny chaos nie jest rowny bezpieczenstwu. Projekt nalezy traktowac jako eksperyment dydaktyczny, ktory pomaga zrozumiec pojecia permutacji, substytucji, klucza, odwracalnosci i pseudo-losowosci.

## 20. Instrukcja testowania

1. Uruchomic aplikacje.
2. Wybrac obraz naturalny.
3. Dla Etapu 1 kliknac `Test + metryki`.
4. Zapisac obserwacje dotyczace widocznej struktury.
5. Powtorzyc test dla obrazu strukturalnego.
6. Wybrac Etap 2 i wykonac test z poprawnym kluczem.
7. Wykonac test z blednym kluczem.
8. Wybrac Etap 3 i powtorzyc eksperyment.
9. Porownac korelacje oraz MAE/MSE.
10. Zapisac wyniki przyciskiem `Zapisz wyniki`.

## 21. Zrodla internetowe

- Dokumentacja Python: https://docs.python.org/3/
- Dokumentacja NumPy: https://numpy.org/doc/
- Dokumentacja Pillow: https://pillow.readthedocs.io/
- Dokumentacja Tkinter: https://docs.python.org/3/library/tkinter.html
- Opis algorytmu Fisher-Yates: https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
- Pojecie korelacji: https://en.wikipedia.org/wiki/Correlation
- Linear congruential generator: https://en.wikipedia.org/wiki/Linear_congruential_generator

## 22. Opis pliku algorithms.py

Plik `algorithms.py` jest najwazniejsza czescia projektu. Znajduja sie w nim wszystkie funkcje odpowiedzialne za przeksztalcanie obrazu. Funkcja `image_to_array` zamienia obraz PIL na tablice NumPy, a funkcja `array_to_image` wykonuje operacje odwrotna. Dzieki temu GUI nie musi bezposrednio zajmowac sie szczegolami reprezentacji pikseli.

Funkcja `key_to_seed` przeksztalca klucz tekstowy na liczbe. Jest to potrzebne, poniewaz algorytmy pseudolosowe wymagaja liczbowego ziarna. Dla tego samego klucza powstaje zawsze ten sam seed. Dla innego klucza seed jest inny, dlatego generowana permutacja albo maska tez jest inna.

Klasa `LCG` implementuje prosty generator pseudolosowy. Metoda `next_u32` zwraca kolejna liczbe 32-bitowa, a metoda `randint` zwraca liczbe z podanego zakresu. Ten generator zostal napisany recznie, aby w dokumentacji mozna bylo pokazac, jak powstaje deterministyczny ciag liczb.

Funkcja `fisher_yates_permutation` tworzy permutacje indeksow. Jest ona uzywana w Etapie 2 oraz w Etapie 3. Funkcja `inverse_permutation` tworzy permutacje odwrotna. To jest kluczowe dla poprawnego unscramblingu.

Funkcje `stage1_scramble`, `stage1_unscramble`, `stage2_scramble`, `stage2_unscramble`, `stage3_scramble` oraz `stage3_unscramble` odpowiadaja bezposrednio trzem etapom wymaganym w projekcie.

## 23. Opis pliku app.py

Plik `app.py` tworzy interfejs graficzny. W aplikacji znajduje sie glowne okno, panel przyciskow, pola do wpisywania kluczy, przyciski etapow oraz trzy panele obrazow.

Klasa `ImagePanel` odpowiada za wyswietlanie pojedynczego obrazu. Program tworzy trzy takie panele:

- obraz oryginalny,
- obraz przeksztalcony,
- obraz odtworzony.

Klasa `App` zawiera logike GUI. Metoda `load_image` pozwala wybrac obraz z dysku. Metoda `do_scramble` wykonuje scrambling. Metoda `do_unscramble` wykonuje odtwarzanie. Metoda `do_metrics` wykonuje caly test oraz wypisuje metryki. Metoda `save_results` zapisuje obrazy i log eksperymentu.

Dzieki rozdzieleniu plikow projekt jest czytelny. Algorytmy sa w osobnym pliku, a GUI w osobnym pliku. To ulatwia prezentacje projektu, bo mozna oddzielnie omawiac czesc matematyczna i czesc interfejsu.

## 24. Przykladowy przebieg eksperymentu na obrazie naturalnym

Najpierw wczytano obraz naturalny. W Etapie 1 po kliknieciu `Test + metryki` widac, ze obraz zostal poprzesuwany w poziomych wierszach. Ogolny rozklad kolorow i fragmenty struktury moga pozostac widoczne. To potwierdza slabosc metody.

W Etapie 2 obraz wyglada bardziej chaotycznie, bo piksele zostaja rozrzucone po calym obrazie. Korelacja sasiednich pikseli spada, poniewaz sasiednie piksele w wyniku nie pochodza juz z sasiednich miejsc oryginalu. Jednak histogram kolorow pozostaje bez zmian.

W Etapie 3 obraz wyglada najmniej podobnie do oryginalu, poniewaz zmieniane sa nie tylko polozenia pikseli, ale takze ich wartosci. Po poprawnym kluczu obraz wraca idealnie. Po blednym kluczu wynik jest niepoprawny.

## 25. Przykladowy przebieg eksperymentu na obrazie strukturalnym

Obraz strukturalny zawiera szachownice i tekst. Taki obraz jest trudnym testem dla slabych metod, poniewaz regularne wzory latwo pozostaja widoczne.

W Etapie 1 widac, ze przesuniecia wierszy nie niszcza calkowicie charakteru obrazu. Linie i fragmenty tekstu moga nadal sugerowac, co bylo na obrazie. To jest bardzo dobry przyklad naiwnego scramblingu.

W Etapie 2 struktura zostaje mocniej rozbita, ale wartosci czarnych i bialych pikseli nadal istnieja w tej samej liczbie. Atakujacy moze wiedziec, ze obraz sklada sie z silnego kontrastu.

W Etapie 3 kontrast tez zostaje zamaskowany przez substytucje. Jednak wciaz jest to metoda edukacyjna, a nie bezpieczny szyfr.

## 26. Test poprawnej odwracalnosci

Poprawna odwracalnosc oznacza, ze po wykonaniu:

```text
original -> scramble -> unscramble
```

wynik musi byc identyczny z obrazem oryginalnym.

Program sprawdza to funkcja `np.array_equal`. Jezeli zwrocona wartosc to `True`, oznacza to, ze wszystkie piksele i wszystkie kanaly RGB sa identyczne. Nie chodzi tylko o podobienstwo wizualne, ale o dokladna zgodnosc wartosci.

To jest wazne, poniewaz projekt wymaga pelnej odwracalnosci. Nawet mala utrata informacji, na przyklad przez zaokraglenia albo kompresje stratna, bylaby bledem. Dlatego program operuje na wartosciach calkowitych `uint8` i zapisuje wyniki jako PNG, gdy potrzebny jest bezstratny zapis eksperymentu.

## 27. Test blednego klucza

Test blednego klucza polega na tym, ze obraz jest najpierw przeksztalcany poprawnym kluczem, a potem odtwarzany innym kluczem. W GUI sluzy do tego pole `Klucz bledny` oraz opcja `Unscramble blednym kluczem`.

W Etapie 1 bledny klucz moze czasami nadal pokazac czesc struktury, bo metoda jest prosta. W Etapie 2 bledny klucz generuje inna permutacje, wiec piksele trafiaja w zle miejsca. W Etapie 3 bledny klucz generuje inna permutacje i inna maske, wiec wynik jest jeszcze bardziej odlegly od oryginalu.

Wynik blednego klucza jest oceniany przez MAE i MSE. Im wieksze wartosci, tym wieksza srednia roznica wzgledem oryginalu. Nie jest to jednak dowod bezpieczenstwa, tylko miara eksperymentalna.

## 28. Ograniczenia techniczne projektu

Program zostal przygotowany jako aplikacja dydaktyczna. Dla bardzo duzych obrazow operacje moga trwac dluzej, poniewaz permutacja obejmuje kazdy piksel. Z tego powodu GUI automatycznie zmniejsza bardzo duze obrazy do rozmiaru wygodnego do eksperymentow.

Aplikacja zapisuje wyniki do folderu `outputs`. Jezeli uzytkownik zapisuje obraz JPG, nalezy pamietac, ze JPG jest formatem stratnym. Do porownan idealnej odwracalnosci najlepiej uzywac PNG.

Projekt nie zawiera logowania uzytkownikow, bazy danych ani prawdziwego systemu szyfrowania. Nie jest to potrzebne, poniewaz wymaganiem projektu jest analiza algorytmow przeksztalcania obrazu, a nie budowa aplikacji do ochrony plikow.

## 29. Mozliwe rozszerzenia projektu

Projekt mozna rozszerzyc o dodatkowe wykresy, na przyklad histogramy kolorow przed i po scramblingu. Szczegolnie dla Etapu 2 byloby widac, ze histogram pozostaje taki sam. Dla Etapu 3 histogram zmienilby sie, poniewaz wartosci pikseli sa modyfikowane.

Innym rozszerzeniem moglaby byc analiza korelacji diagonalnej. Obecnie program liczy korelacje pozioma i pionowa, co wystarcza do podstawowej analizy, ale korelacja diagonalna pokazalaby jeszcze jeden kierunek zaleznosci.

Mozna tez dodac eksport raportu z GUI do pliku PDF. Obecna wersja zapisuje obrazy oraz plik tekstowy z logiem i metrykami, co jest proste i czytelne do obrony projektu.

## 30. Podsumowanie do prezentacji ustnej

Podczas prezentacji nalezy podkreslic, ze projekt jest eksperymentem dydaktycznym. Najpierw pokazujemy Etap 1, ktory jest odwracalny, ale slaby. Potem pokazujemy Etap 2, ktory jest czysta permutacja i dobrze wyjasnia funkcje P oraz P^-1. Na koncu pokazujemy Etap 3, ktory dodaje substytucje i lepiej ukrywa obraz wizualnie.

Najwazniejsze zdanie do powiedzenia na koncu: Moje rozwiazanie pokazuje chaos wizualny, ale nie jest bezpiecznym szyfrem, poniewaz zastosowane mechanizmy sa zbyt proste i nie byly projektowane jako kryptografia.
