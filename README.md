# RSS Feed Generator für JSON Reports

Automatisierte Generierung eines RSS-Feeds aus JSON-Berichten mittels GitHub Actions.

## Übersicht

Dieses Projekt konvertiert strukturierte JSON-Dateien in deinem `reports/`-Verzeichnis automatisch in einen standardkonformen RSS 2.0 Feed (`feed.xml`). Der Prozess läuft vollautomatisch über GitHub Actions und wird bei jedem Push getriggert.


## Features

- ✅ **Automatische Konvertierung**: JSON → RSS 2.0
- ✅ **GitHub Actions Integration**: Automatisch bei jedem Push
- ✅ **Konfigurierbar**: Einfach neue JSON-Dateien hinzufügen
- ✅ **Zeitstempel-Konvertierung**: YYYY-MM-DD → RFC 2822 Format
- ✅ **Metadaten-Mapping**: Flexible Feldzuordnung

