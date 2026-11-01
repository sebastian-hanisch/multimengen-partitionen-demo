# Multimengen und Partitionen – wenn die Reihenfolge egal ist – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-multimengen-partitionen-demo.streamlit.app/)** -->

Stück 5 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3) und `semiring-rekursion-demo` (Stück 4). Der Baukasten aus Stück 3 kennt Folge, Summe und Produkt; diese Demo fügt die **Multimenge** hinzu, bei der die Reihenfolge egal ist: Gibt es von jeder Größe k genau a_k verschiedene Bausteine, ist die Zahl der Multimengen der Gesamtgröße n der Koeffizient von zⁿ im Produkt der Faktoren 1/(1 − zᵏ)^(a_k) (die **Euler-Transformation**). Aus der Tabelle a_k werden Zahlpartitionen, Münzwechsel, Rucksack-Teilmengen, ebene Partitionen und Wurzelbäume ohne Reihenfolge. Die Zahlen kommen auf mehreren Rechenwegen heraus; der Aufwand ist sehr verschieden. Mit „Zahlpartition“ ist hier die Summe ohne Reihenfolge gemeint, nicht die Mengenpartition (Stück 6) und nicht das Partitionsproblem der Komplexitätstheorie.

## Warum dieses Problem

In Stück 3 hat die Reihenfolge der Bausteine eine Rolle gespielt (Folge), in Stück 4 stand sie schon im Münzwechsel im Weg: nach Beträgen zählt das Netz 128 Folgen, nach Münzarten 10 Multimengen. Hier wird daraus ein eigener Baustein mit fester Übersetzung in die erzeugende Funktion. Die Demo zeigt, was er kann (fünf bekannte Fragen mit einer Eingabe), wo er sich verschieden teuer rechnen lässt, und wo die Rechnung endet (die Reihe ist nicht mehr rational).

## Befunde und Korrekturen gegenüber dem Plan

- **Der Plan-Hook war nur zur Hälfte richtig.** „Euler-Produkt gegen Münzwechsel-DP, gleiche Zahlen, anderer Aufwand“: Produkt und Münzwechsel-DP sind derselbe Rechner (beide n(n+1)/2 Schritte bei den Partitionen). Einen echten Unterschied gibt es erst bei der **Fünfeckszahlen-Rekursion** (n = 1000: 33.475 statt 500.500 Schritte, etwa 15-mal weniger) und beim **Aufzählen** (so viele Schritte, wie p(n) groß ist, bei n = 1000 sind das 32 Stellen).
- **Erweitert gegenüber dem Plan:** Auch die Rekursion der logarithmischen Ableitung gilt mit „höchstens m gleiche Bausteine“ (Mengen, m = 1, und m = 2, 3); die App rechnet das Produkt und diese Rekursion auf demselben Eingabewert und vergleicht sie.
- **Statt eines Seeds eine Zufallstabelle:** Der Plan nannte einen Seed für Zufallsbausteine. Die App würfelt auf Klick eine Tabelle und trägt sie ein; so bleibt die Tabelle der einzige Zustand und steht im Permalink.
- **Raten der Rekursion für alle Partitionen:** Der Plan meldete Ordnung bis 60 ohne Treffer; die App rechnet die kürzeste Rekursion über Berlekamp–Massey mit Brüchen und findet bei 300 Termen die Länge 150 (die Hälfte der Terme: ein Rezept, das nur die Folge auswendig lernt). Die zweite, unabhängige Suche (ein Gleichungssystem) steht im Test.
- **Port:** Der Plan sah 9318 vor (9317 gehört `vorhersagen-demo`); die Demo läuft darauf.
- **Falsche Handrechnung (meine, nicht der Code):** Ich hatte die Wachstumsverhältnisse der Bäume mit Reihenfolge zuerst als 14/5 am falschen Index erwartet. Die Probe am Wert (a(3)/a(2) = 2 mit Reihenfolge) hat es korrigiert; der Test stand falsch, nicht der Code.

## Modell

Eine **Spezifikation** ist eine Tabelle `a`: Größe k → Zahl der verschiedenen Bausteine. `m` ist die Höchstzahl gleicher Bausteine (beliebig = Multimenge, 1 = Menge). `series_product` multipliziert die Faktoren (ein Durchlauf je Baustein), `series_log` rechnet n·c_n = Σ b_k·c_(n−k) mit b_k = Σ_(d|k) d·a_d (bei endlichem m mit Abzug für (m+1)·d | k), `partitions_pentagonal` die Partitionszahl über Eulers Fünfeckszahlen, `rooted_trees` die Wurzelbäume ohne Reihenfolge über die Rückkopplung T = z·MSET(T). `series_brute`, `partitions` und `trees_canonical_count` zählen durch Aufzählen. `linear_complexity` rät die kürzeste Rekursion mit festen Koeffizienten (Berlekamp–Massey über Brüchen). Familien: Partitionen (a_k = 1), ebene Partitionen (a_k = k), Wurzelbäume und eigene Bausteine (Tabelle bis Größe 12, je Größe 0 bis 9 Bausteine). Die Formeln stehen im 📐-Expander der App.

## Methodik

- **Rechenwege in der App** (Experiment 1): Produkt, Rekursion der logarithmischen Ableitung, bei Partitionen ohne Höchstzahl die Fünfeckszahlen-Rekursion, und Aufzählen, solange es klein ist (Partitionen bis n = 40; sonst bis n = 12 und 200.000 Auswahlen; Wurzelbäume bis n = 11). Das Produkt entfällt über 3.000.000 Schritten. Bei Abweichung zeigt die App einen Fehler statt einer Zahl.
- **Aufwand** wird als Zahl der Additionen gezählt (exakt, getestet); die Zeit steht nur als Messung auf Klick.
- **Wurzelbäume** werden bis n = 11 gegen kanonische Formen geprüft (alle Bäume mit Reihenfolge erzeugen, die Kinder sortieren, gleiche Formen zusammenfassen), auch mit „höchstens m gleiche Geschwister“.
- **Eingabe:** Familie, Zielgröße N (je Familie begrenzt), Höchstzahl gleicher Bausteine, Tabelle. Die Adresszeile spiegelt die Einstellung.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_mmp.py`. Zeiten stehen in keinem Test; sie sind gemessen und gekennzeichnet.

| Frage | Befund |
|---|---|
| Handinstanzen | p(1) bis p(10) = 1, 2, 3, 5, 7, 11, 15, 22, 30, 42; Münzen 1, 2, 5 und Betrag 5: 4 Multimengen (5; 2+2+1; 2+1+1+1; fünfmal 1); Partitionen von 8 in verschiedene Teile: 6, gleich der Zahl der Partitionen in ungerade Teile |
| Partitionszahlen | p(10) = 42, p(50) = 204.226, p(100) = 190.569.292, p(200) = 3.972.999.029.388, p(1000) = 24.061.467.864.032.622.473.692.149.727.991 (32 Stellen); Summe von p(0) bis p(50) = 1.295.971. Die Werte sind in den Tests durch mehrere Wege bestätigt (Produkt, Rekursion, Fünfeckszahlen, eine eigene Rekursion über Partitionen in genau k Teile und Aufzählen bis n = 35); eine Quelle habe ich dafür nicht gelesen |
| Verschiedene Teile | q(10) = 10, q(50) = 3.658, q(100) = 444.793, gleich der Zahl der Partitionen in ungerade Teile (bis n = 100); Summe von q(0) bis q(50) = 31.583 |
| Aufwand für p(n) (Experiment 2) | Schritte des Produkts n(n+1)/2: 1.275, 5.050, 20.100, 125.250, 500.500 für n = 50, 100, 200, 500, 1000; Fünfeckszahlen: 345, 1.004, 2.904, 11.709, 33.475; Verhältnis 3,7, 5,0, 6,9, 10,7, 15,0. Aufzählen braucht p(n) Schritte, das sind Zahlen mit 6, 9, 13, 22 und 32 Stellen |
| Folge gegen Multimenge (Experiment 3) | Münzen 1, 2, 5, Beträge 5, 10, 15, 20, 50, 100: Folgen 9, 128, 1.843, 26.547, 237.139.442.616, 91.197.869.007.632.925.819.218; Multimengen 4, 10, 18, 29, 146, 541 (die ersten vier gleich Stück 4). Zusammensetzungen 2ⁿ⁻¹ gegen Partitionen: n = 10: 512 gegen 42, n = 30: 536.870.912 gegen 5.604, n = 50: 562.949.953.421.312 gegen 204.226, n = 100: 2⁹⁹ gegen 190.569.292 |
| Rucksack aus Stück 4 | Gewichte 2, 2, 3, 5, 5, 6, 9, 9, 9, 10, Kapazität 30, jeder Gegenstand höchstens einmal: 38 Teilmengen mit Gewicht genau 30, **531** bis Gewicht 30 (gleich Stück 4). Dieselben Gegenstände beliebig oft: 8.387; höchstens zweimal: 2.580; höchstens dreimal: 4.573 |
| Wurzelbäume (Experiment 4) | Ohne Reihenfolge n = 1 bis 14: 1, 1, 2, 4, 9, 20, 48, 115, 286, 719, 1.842, 4.766, 12.486, 32.973; mit Reihenfolge (Catalan, Stück 3) n = 1 bis 12: 1, 1, 2, 5, 14, 42, 132, 429, 1.430, 4.862, 16.796, 58.786. Alle Geschwister verschieden (m = 1) n = 1 bis 10: 1, 1, 1, 2, 3, 6, 12, 25, 52, 113. Verhältnis a(n+1)/a(n) bei n = 50, 100, 199: 2,8691, 2,9119, 2,9336 (mit Reihenfolge 3,8824, 3,9406, 3,9700); a(200) hat 91 Stellen. Rekursion gleich dem Aufzählen kanonischer Formen für n = 1 bis 10 (m beliebig) und n = 1 bis 9 (m = 1, 2, 3) |
| Ebene Partitionen | a_k = k: 1, 1, 3, 6, 13, 24, 48, 86, 160, 282, 500, 859, 1.479, 2.485, 4.167, 6.879; bis n = 10 gleich dem Aufzählen der Zeilenfolgen (Test); die App zählt die Auswahlen bis n = 12 auf |
| Rationale Reihen (Experiment 5) | Teile bis k = 1 bis 6: geratenes Rezept der Ordnung 1, 3, 6, 10, 15, 21 = Grad von ∏(1 − zʲ); Teile bis 2 = ⌊n/2⌋ + 1 und Teile bis 3 = Rundung von (n+3)²/12 gelten bis n = 400. p(n) bei 300 Termen: kürzestes Rezept 150, also keins. p_k(1000) gegen n^(k−1)/(k!·(k−1)!): 1,0060 (k = 3), 1,0151 (k = 4), 1,0303 (k = 5) |
| Wachstum von p(n) | p(n) gegen exp(π√(2n/3))/(4n√3): Relativfehler −0,1269 (n = 10), −0,0437 (n = 100), −0,0140 (n = 1000); nur gemessen, das Thema von Stück 9 |
| Presets | Partitionen von 50: 204.226; verschiedene Teile von 100: 444.793; Münzen 1, 2, 5 und Betrag 100: 541; Rucksack aus Stück 4: 531; ebene Partitionen von 12: 1.479 (Summe bis 12: 3.462); Wurzelbäume mit 11 Knoten: 1.842 (mit Reihenfolge 16.796); Wurzelbäume mit 500 Knoten: 231 Stellen (mit Reihenfolge 297), 124.750 Schritte; p(1000): 500.500 Schritte |
| Zeit (nur gemessen, **nicht getestet**) | Auf dem Entwicklungsrechner (Phase 0): n = 1000, 2000, 5000: Produkt 0,11 s, 0,41 s, 2,8 s; Fünfeckszahlen 0,02 s, 0,05 s, 0,19 s; die App misst n = 1000, 2000, 3000 auf Klick |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** p(1000), die Folgen der Wurzelbäume und der ebenen Partitionen wurden nicht an einer Quelle gelesen. Mehrere unabhängige Rechenwege stimmen überein; das ersetzt keine Quelle.
- **Das Wachstumsverhältnis der Bäume (2,93 bei n = 199)** ist ein Zahlenwert auf dem Weg zu einem Grenzwert; die Demo nennt keinen Grenzwert.
- **Die Fünfeckszahlen-Rekursion gilt nur für die Partitionszahl** (ohne Höchstzahl); für andere Tabellen gibt es sie nicht.
- **Schritte sind Additionen großer Zahlen**, die mit n wachsen (32 Stellen bei p(1000)): „Schritte“, nicht „Zeit“.
- **Aufzählen als Prüfer ist begrenzt** (Partitionen n ≤ 40; sonst n ≤ 12 und 200.000 Auswahlen; Bäume n ≤ 11); darüber prüfen sich nur Produkt und Rekursion gegenseitig. Für Wurzelbäume gibt es über n = 11 nur die Rekursion.
- **Gleiche Bausteine sind austauschbar, verschiedene nicht:** zwei Gegenstände gleichen Gewichts sind zwei Bausteine (Eintrag 2), zwei Münzen gleichen Werts ein Baustein (Eintrag 1).
- **Keine Symmetrie außer dem Vertauschen gleicher Bausteine:** Halsketten und Graphen bis auf Isomorphie braucht Stück 11.
- **Ohne Beschriftung:** beschriftete Strukturen (Stirling, Bell, Derangements) sind Stück 6.
- **Zielgröße begrenzt** (Partitionen 1000, ebene Partitionen 150, Wurzelbäume 500, eigene Bausteine 1000); darüber wird gekappt und das gesagt.
- **Zeiten** sind Python-Messungen dieses Rechners; zwei Läufe unterscheiden sich.
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, die Spielwiese und die Zeitmessung im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (Münzen, Rucksack aus Stück 4, Partitionen von 5, Bäume mit vier Knoten), Produkt gegen Rekursion gegen Aufzählen an 80 Zufallsspezifikationen (und mit m = 1, 2, 3 an je 60), eine eigene Partitionsrekursion, Aufzählen der Partitionen, kanonische Formen der Bäume (auch mit m), Aufzählen ebener Partitionen, ein zweites Raten über ein Gleichungssystem, festgeschriebene Zahlen aus Stück 4.
- **Eigenschaften:** Koeffizienten wachsen, wenn es einen Baustein der Größe 1 gibt; Menge ≤ Multimenge ≤ Folgen; ein Baustein mehr senkt keinen Koeffizienten; Skalieren aller Größen verschiebt nur den Index; Reihenfolge der Eingabe ohne Wirkung; mehr erlaubte Exemplare senken nichts; die Rekursion geht ohne Rest auf; Bäume ohne Reihenfolge höchstens so viele wie mit; Tabelle lesen und schreiben, Zufallstabelle unabhängig vom `PYTHONHASHSEED`.
- **Randfälle:** Größe 0, leere Spezifikation, Bausteine größer als N, ein Baustein der Größe 1, viele Kopien, Bäume mit einem und zwei Knoten, Zahlen über der 4300-Stellen-Grenze von `str`, fehlerhafte Tabellen, jede Familie bei den kleinsten Größen, Aufzählen oder Produkt übersprungen.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), alle Experimente, Permalink mit Müll und Grenzwerten, Deckelung mit Hinweis, unlesbare Tabelle, jede Familie mit jedem m, jedes Preset, Spielwiese, PDF an den Rändern; Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

797 Tests (`pytest tests`), zuletzt in etwa zwei Minuten auf dem Entwicklungsrechner (Messung, nicht getestet).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `mmp_algorithm.py` | Kern: Produkt, Rekursion, Fünfeckszahlen, Aufzählen, Wurzelbäume, Raten der Rekursion |
| `mmp_constants.py` | Regler-Grenzen, Schwellen, Farben, Presets |
| `mmp_evaluation.py` | Analyse, Experimente, Verdikte, Formatierung |
| `mmp_layout.py` | Fester Kopf (Stylesheet) |
| `mmp_pdf_export.py` | PDF der aktuellen Aufgabe (fpdf2) |
| `mmp_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufallstabelle |
| `mmp_scenario.py` | Bausteintabelle lesen, Spezifikation je Familie |
| `mmp_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Verdikte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Beschriftete Strukturen (exponentielle erzeugende Funktion), Stirling- und Bell-Zahlen:** Stück 6.
- **Zählen nach Parameter (Partitionen in genau k Teile, bivariat):** Stück 8; die Spielwiese zeigt nur die Zählung nach größtem Teil und nach Zahl der Teile.
- **Asymptotik von p(n) (Hardy–Ramanujan):** Stück 9; hier nur die Messung des Relativfehlers im README.
- **Bis auf Symmetrie zählen (Burnside, Pólya):** Stück 11.
- **q-Reihen, Rogers–Ramanujan, Gitterpunkte in Polytopen:** nicht Teil der Linie.
- **Ein Computer-Algebra-System als zweite Gegenprobe:** nicht gebaut; die Gegenproben sind die eigene Partitionsrekursion, das Aufzählen und die kanonischen Formen.
- **Verwandte Demos:** `semiring-rekursion-demo` (dieselben Münzen und der Rucksack als Netz mit Optimierung), `dynamic-programming-demo` (Rucksack-DP), `symbolische-methode-demo` (Bäume mit Reihenfolge); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
