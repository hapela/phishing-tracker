# RSS Feed Generator für JSON Reports

Automatisierte Generierung eines RSS-Feeds aus JSON-Berichten mittels GitHub Actions.

## Übersicht

Dieses Projekt konvertiert strukturierte JSON-Dateien in deinem `reports/`-Verzeichnis automatisch in einen standardkonformen RSS 2.0 Feed (`feed.xml`). Der Prozess läuft vollautomatisch über GitHub Actions und wird bei jedem Push getriggert.

## Projektstruktur
.
├── .github/workflows/
│   └── generate-rss.yml          # GitHub Actions Workflow
├── reports/
│   ├── JSON 08-middleware.json   # Beispiel: JSON Report
│   └── ...                        # Weitere JSON Dateien
├── scripts/
│   ├── generate_rss.py            # Python Script zur RSS-Generierung
│   └── index.html                 # Landingpage (optional)
├── feed.xml                       # Generierter RSS Feed (Auto-generiert)
└── README.md                      # Diese Datei




## Features

- ✅ **Automatische Konvertierung**: JSON → RSS 2.0
- ✅ **GitHub Actions Integration**: Automatisch bei jedem Push
- ✅ **Konfigurierbar**: Einfach neue JSON-Dateien hinzufügen
- ✅ **Zeitstempel-Konvertierung**: YYYY-MM-DD → RFC 2822 Format
- ✅ **Metadaten-Mapping**: Flexible Feldzuordnung



Best Practices
📝 Eindeutige IDs: Verwende Format "YYYY-MM-NNN"
📅 Konsistente Daten: Immer YYYY-MM-DD Format
🏷️ Tags nutzen: Hilft beim Filtern in RSS-Readern
🔄 Regelmäßig: Reports zeitnah hinzufügen
✍️ Aussagekräftige Beschreibungen: Wichtig für Lesbarkeit
Lizenz
[Deine Lizenz eintragen, z.B. MIT, Apache 2.0, etc.]

Support
Bei Fragen oder Problemen: [Dein Kontakt, z.B. Issues im Repo]

*
