# Silikon-Dichtungsform (O-Ring 20 × 3 mm)

Zweiteilige 3D-Druck-Gießform, mit der sich ein O-Ring direkt aus einer Silikonkartusche spritzen lässt.
Die Form hat drei Entlüftungslöcher, die Sie nacheinander mit dem Finger verschließen. So wird der Ring ohne Lufteinschlüsse gefüllt.

> 🤖 **KI-Test:** Dieses Repository ist ein Experiment. Form, 3D-Modell, Animation und Webseite hat eine KI (GitHub Copilot CLI) aus einem einzigen Prompt erzeugt. Die Prompts stehen in [`prompt.md`](prompt.md). Die Form ist nicht real gedruckt und getestet.

**Demo:** [Interaktives 3D-Modell mit Animation des Ablaufs](https://raw.githack.com/stefaneicher/silikon-dichtung-form/master/index.html) (gehostet über githack.com). Lokal reicht es, `index.html` im Browser zu öffnen.

## Aufbau
| Merkmal | Wert |
|---|---|
| O-Ring | Innen-Ø 20 mm, Schnur-Ø 3 mm (Mitten-Ø 23 mm) |
| Form | 50 × 50 mm, 2 × 8 mm hoch, Trennebene in der Ringmitte |
| Anguss | Kegeltrichter Ø 18 → 5,5 mm, 10 mm tief, für die Spitze (ca. Ø 5 mm) einer Standard-Kartuschendüse, danach Kanal Ø 2,5 mm, bei 0° |
| Entlüftung | 3 × Ø 1,6 mm am höchsten Punkt des Rings: Loch 1 = 90°, Loch 2 = 270°, Loch 3 = 180° |
| Ausrichtung | Passstifte Ø 5 und Ø 4 mm, unterschiedlich groß, damit das Oberteil nicht verdreht aufgesetzt wird |
| Verschluss | 4 × M4-Schrauben mit Mutterfallen im Unterteil |
| Öffnen | Hebelschlitze links und rechts |

## Ablauf
1. Hohlraum dünn mit Trennmittel (Vaseline oder Spülmittel) einstreichen, Form schließen und verschrauben.
2. Kartuschendüse auf ca. Ø 5 mm abschneiden und in den Trichter drücken. Dann Silikon einspritzen.
3. Silikon tritt zuerst an **Loch 1 und Loch 2** aus. Beide mit dem Finger verschließen und weiter einspritzen.
4. Danach tritt Silikon an **Loch 3** aus, wo sich die beiden Fronten treffen. Auch dieses Loch verschließen. Der Ring ist jetzt ohne Lufteinschlüsse gefüllt.
5. Silikon aushärten lassen, Form öffnen und Grat sowie Angussreste abschneiden.

> ⚠️ Sanitärsilikon (1K) härtet durch Luftfeuchte nur etwa 2–3 mm pro Tag aus. In einer geschlossenen Form dauert das mehrere Tage.
> Besser geeignet ist 2K-Abformsilikon. Alternativ können Sie dem Sanitärsilikon ein paar Tropfen Wasser oder etwas Speisestärke beimischen.

## Druck
`stl/form_unterteil.stl` und `stl/form_oberteil.stl` sind bereits richtig ausgerichtet: Die Trennfläche zeigt jeweils nach oben, Stützstrukturen sind nicht nötig.
Dateien im Ordner `stl/`:

| Datei | Inhalt |
|---|---|
| `form_unterteil.stl`, `form_oberteil.stl` | Die beiden Formhälften einzeln |
| `druckplatte.3mf` | Beide Hälften nebeneinander als zwei Objekte, für einen Druck auf einer Platte |
| `druckplatte.stl` | Dieselbe Platte als einzelne STL, falls der Slicer kein 3MF liest |
| `o_ring_vorschau.stl` | Nur Vorschau des fertigen Rings, nicht drucken |

Empfohlen: PETG, Schichthöhe 0,12–0,16 mm, 4 Wände, 30 % Infill.

## Andere Maße
Die Parameter stehen oben in `generate.py`, z. B. `RING_ID` und `CORD`. So erzeugen Sie die Dateien neu:
```powershell
py -m venv .venv
.\.venv\Scripts\pip install trimesh manifold3d numpy networkx lxml
.\.venv\Scripts\python generate.py
```
Das Skript schreibt die Dateien `stl/*.stl`, `stl/druckplatte.3mf` und `web/models.js`, die von der Webseite verwendet wird.
