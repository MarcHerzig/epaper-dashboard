# Porsche Taycan Widget Setup

## ✅ Was wurde erstellt

Ich habe ein spezielles **Taycan Widget** für dein Dashboard erstellt!

### Widget zeigt:
- 🖼️ **Bild deines Taycan** (von Home Assistant)
- 🔋 **Batteriestand** (in %) - GROSS und prominent
- 📊 **Batterie Balken** (visuell)
- 🛣️ **Reichweite** (in km)
- 🔌 **Ladestatus** ("Charging", "Not charging", etc.)
- 🏁 **KM-Stand** (Gesamtkilometer)

---

## 🔧 Setup - Schritt für Schritt

### 1. Home Assistant Token erstellen

1. Gehe zu deinem Home Assistant: **https://ha.maegu.be**
2. Klicke auf dein Profil (unten links)
3. Scrolle zu **"Long-Lived Access Tokens"**
4. Klicke **"Create Token"**
5. Name: "ePaper Dashboard"
6. **Kopiere den Token!** (wird nur einmal angezeigt)

### 2. Token in config.yaml einfügen

Öffne die Datei:
```bash
nano config.yaml
```

Suche nach:
```yaml
token: "DEIN_LONG_LIVED_ACCESS_TOKEN_HIER_EINFÜGEN"
```

Ersetze mit deinem Token:
```yaml
token: "eyJ0eXAiOiJKV1QiLCJhbG..."  # Dein echter Token
```

Speichern: `Ctrl+O`, dann `Enter`, dann `Ctrl+X`

### 3. Dashboard testen

```bash
# Widget testen
python3 test_widgets.py --test discovery

# Dashboard starten
./run_dashboard.sh
```

---

## 📋 Deine Konfiguration

Die config.yaml enthält bereits deine **exakten Entity IDs**:

```yaml
widgets:
  - name: porsche_taycan
    type: taycan
    enabled: true
    position: [20, 20]
    size: [440, 300]
    update_interval: 120  # Alle 2 Minuten
    config:
      url: "https://ha.maegu.be"
      token: "DEIN_TOKEN_HIER"

      # Deine Taycan Entities:
      battery_entity: "sensor.taycan_gts_sport_turismo_state_of_charge"
      range_entity: "sensor.taycan_gts_sport_turismo_remaining_range_electric"
      charging_entity: "sensor.taycan_gts_sport_turismo_charging_status"
      image_entity: "image.taycan_gts_sport_turismo_view_from_the_side"
      mileage_entity: "sensor.taycan_gts_sport_turismo_mileage"
```

---

## 🎨 Widget Layout

Das Widget zeigt:

```
┌────────────────────────────────────────┐
│ 🚗 PORSCHE TAYCAN                      │
│    🔌 Charging / Not charging          │
├────────────────────────────────────────┤
│                                        │
│  [Taycan Bild]    Batterie:           │
│   200x100 px        87%               │
│                   ████████████░░░░    │
│                                        │
│                  Reichweite:          │
│                   342 km              │
│                                        │
│  KM-Stand: 15,243 km                  │
└────────────────────────────────────────┘
```

---

## ⚙️ Anpassungen

### Position ändern
```yaml
position: [20, 20]  # x, y auf dem Display
```

### Größe ändern
```yaml
size: [440, 300]  # Breite, Höhe in Pixel
```

### Update-Intervall
```yaml
update_interval: 120  # Sekunden (120 = 2 Minuten)
```

### Bild ausblenden (wenn nicht gewünscht)
```yaml
image_entity: null  # oder einfach die Zeile löschen
```

---

## 🧪 Testen

### Widget Discovery testen
```bash
python3 test_widgets.py --test discovery
```

Sollte zeigen:
```
✓ Discovered 5 widgets:
  - taycan         ← Dein neues Widget!
  - homeassistant
  - weather
  - ubiquiti
  - clock
```

### Taycan Daten abrufen
```bash
python3 test_widgets.py --test fetch --widget taycan --verbose
```

Zeigt ob die Daten von Home Assistant korrekt abgerufen werden.

### Komplettes Rendering
```bash
python3 test_widgets.py --test render
```

Erstellt: `test_output/test_render_preview.png`

---

## 🔍 Troubleshooting

### "401 Unauthorized"
- Token ist falsch oder abgelaufen
- Neuen Token in Home Assistant erstellen
- Token in config.yaml aktualisieren

### "Failed to fetch sensor"
- Entity ID falsch geschrieben
- Sensor in Home Assistant prüfen
- HA URL korrekt? (https://ha.maegu.be)

### "No image available"
- `image_entity` Entity existiert in HA?
- Bild in HA verfügbar?
- Netzwerkverbindung OK?

### Widget zeigt "Loading..."
- Dashboard läuft?
- Token konfiguriert?
- Warte 2 Minuten (update_interval)
- Logs prüfen: `tail -f dashboard.log`

---

## 📊 Andere Widgets kombinieren

Das Taycan Widget funktioniert perfekt zusammen mit:

```yaml
widgets:
  - name: porsche_taycan     # Oben links
    position: [20, 20]
    size: [440, 300]

  - name: weather            # Mitte
    position: [480, 20]
    size: [440, 440]

  - name: clock              # Rechts oben
    position: [940, 20]
    size: [400, 200]

  - name: ubiquiti           # Rechts unten
    position: [940, 240]
    size: [400, 220]
```

---

## 🚀 Dashboard starten

```bash
# Dashboard mit Preview
./run_dashboard.sh

# Oder manuell
mv lib lib_disabled
python3 main_v2.py
open -a Preview emulator_output/preview.png
```

Preview aktualisiert automatisch alle 2 Minuten!

---

## 📝 Nächste Schritte

1. ✅ Token in config.yaml einfügen
2. ✅ `./run_dashboard.sh` ausführen
3. ✅ Preview öffnet sich automatisch
4. ✅ Warte 2-3 Minuten für erste Daten
5. ✅ Genieße deinen Taycan auf dem Dashboard! 🎉

---

Viel Erfolg! Bei Fragen einfach melden. 🚗⚡
