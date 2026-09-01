import json
import os
from datetime import datetime
from email.utils import formatdate

# Verzeichnisse
REPORTS_DIR = "reports"
OUTPUT_FILE = "feed.xml"

# RSS Feed Vorlage
RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Meldungen Feed</title>
    <link>https://github.com/[dein-username]/[repo-name]</link>
    <description>Automatisch generierter Feed aus JSON Reports</description>
    <language>de-de</language>
    {items}
  </channel>
</rss>
"""

# Item Template
ITEM_TEMPLATE = """    <item>
      <title>{title}</title>
      <description>{description}</description>
      <pubDate>{pubDate}</pubDate>
      <guid>{guid}</guid>
    </item>
"""

def convert_date_to_rfc2822(date_str):
    """Konvertiert YYYY-MM-DD zu RFC 2822 Format"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return formatdate(timeval=dt.timestamp(), localtime=False, usegmt=True)
    except:
        return formatdate(localtime=False, usegmt=True)

def generate_rss():
    """Generiert RSS Feed aus JSON Dateien"""
    items = []
    
    # Alle JSON-Dateien im reports/ Verzeichnis lesen
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        return
    
    for filename in sorted(os.listdir(REPORTS_DIR)):
        if filename.endswith(".json"):
            filepath = os.path.join(REPORTS_DIR, filename)
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                meldungen = data.get("meldungen", [])
                
                for meldung in meldungen:
                    # Felder extrahieren (mit Defaults)
                    id_val = meldung.get("id", "unknown")
                    betreff = meldung.get("betreff", "")
                    typ = meldung.get("typ", "")
                    absender = meldung.get("absender", "")
                    beschreibung = meldung.get("beschreibung", "")
                    status = meldung.get("status", "")
                    tags = meldung.get("tags", [])
                    datum = meldung.get("datum", "")
                    
                    # NEUE FELDER HIER EXTRAHIEREN
                    priorität = meldung.get("priorität", "")
                    zugeordnet_an = meldung.get("zugeordnet_an", "")
                    link = meldung.get("link", "")
                    
                    # Title zusammensetzen
                    title = f"{betreff} [{typ}]"
                    
                    # Description mit NEUEN FELDERN zusammensetzen
                    description_parts = []
                    
                    if absender:
                        description_parts.append(f"<b>Absender:</b> {absender}")
                    if typ:
                        description_parts.append(f"<b>Typ:</b> {typ}")
                    if beschreibung:
                        description_parts.append(f"<b>Beschreibung:</b> {beschreibung}")
                    if status:
                        description_parts.append(f"<b>Status:</b> {status}")
                    if priorität:
                        description_parts.append(f"<b>Priorität:</b> {priorität}")
                    if zugeordnet_an:
                        description_parts.append(f"<b>Zugeordnet an:</b> {zugeordnet_an}")
                    if link:
                        description_parts.append(f"<b>Link:</b> <a href='{link}'>{link}</a>")
                    if tags:
                        tags_str = ", ".join(tags)
                        description_parts.append(f"<b>Tags:</b> {tags_str}")
                    
                    description = "<br/>\n".join(description_parts)
                    
                    # Datum konvertieren
                    pubDate = convert_date_to_rfc2822(datum)
                    
                    # Item erstellen
                    item = ITEM_TEMPLATE.format(
                        title=title,
                        description=description,
                        pubDate=pubDate,
                        guid=id_val
                    )
                    items.append(item)
            
            except Exception as e:
                print(f"Fehler bei {filename}: {e}")
    
    # RSS-Datei schreiben
    rss_content = RSS_TEMPLATE.format(items="\n".join(items))
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)
    
    print(f"✅ RSS Feed generiert: {OUTPUT_FILE}")
    print(f"✅ {len(items)} Items verarbeitet")

if __name__ == "__main__":
    generate_rss()
