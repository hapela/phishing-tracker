import json
import os
from datetime import datetime
from email.utils import formatdate

REPORTS_DIR = "reports"
OUTPUT_FILE = "feed.xml"

RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Sicherheitsmeldungen Feed</title>
    <link>https://github.com/[dein-username]/[repo-name]</link>
    <description>Automatisch generierter Feed aus Sicherheitsmeldungen</description>
    <language>de-de</language>
    {items}
  </channel>
</rss>
"""

ITEM_TEMPLATE = """    <item>
      <title>{title}</title>
      <description>{description_text}</description>
      <content:encoded>&lt;![CDATA[{description_html}]]&gt;</content:encoded>
      <pubDate>{pubDate}</pubDate>
      <guid>{guid}</guid>
    </item>
"""

def escape_html(text):
    """Escapet HTML-Sonderzeichen"""
    if not text:
        return ""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;"))

def convert_date_to_rfc2822(date_str):
    """Konvertiert ISO 8601 oder YYYY-MM-DD zu RFC 2822 Format"""
    try:
        if "T" in date_str:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        return formatdate(timeval=dt.timestamp(), localtime=False, usegmt=True)
    except:
        return formatdate(localtime=False, usegmt=True)

def generate_rss():
    """Generiert RSS Feed aus JSON Dateien"""
    items = []
    
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
                    id_val = meldung.get("id", "unknown")
                    betreff = meldung.get("betreff", "")
                    typ = meldung.get("typ", "")
                    absender = meldung.get("absender", "")
                    beschreibung = meldung.get("beschreibung", "")
                    status = meldung.get("status", "")
                    tags = meldung.get("tags", [])
                    datum = meldung.get("datum", "")
                    gefaehrlicher_link = meldung.get("gefaehrlicher_link", "")
                    weitere_infos = meldung.get("weitere_infos", "")
                    screenshot = meldung.get("screenshot", "")
                    
                    title = f"⚠️ {betreff}"
                    
                    # HTML Description
                    description_html = f"""
<h2>⚠️ Angriffstyp:</h2>
<p><strong>{escape_html(typ)}</strong></p>

<h2>📧 Absender:</h2>
<p>{escape_html(absender)}</p>

{"<h2>🔗 Gefährlicher Link:</h2><p><code>" + escape_html(gefaehrlicher_link) + "</code></p>" if gefaehrlicher_link else ""}

<h2>ℹ️ Weitere Informationen zur Meldung:</h2>
<p>{escape_html(beschreibung)}</p>
{"<p><a href='" + escape_html(weitere_infos) + "'>Mehr Infos auf VirusTotal</a></p>" if weitere_infos else ""}

<h2>🗓️ Datum der Meldung:</h2>
<p>{escape_html(datum)}</p>

{"<h2>📸 Screenshot der Mail:</h2><p><img src='" + escape_html(screenshot) + "' style='max-width: 600px; border: 1px solid #ccc;' /></p>" if screenshot else ""}

<h2>Tags:</h2>
<p>{", ".join([f"<span style='background: #e0e0e0; padding: 2px 6px; border-radius: 3px; margin-right: 4px;'>{escape_html(tag)}</span>" for tag in tags])}</p>

<hr />
<p><strong>Status:</strong> {escape_html(status)}</p>
"""
                    
                    # Plaintext Description
                    description_text = f"""Angriffstyp: {typ}
Absender: {absender}
{"Gefährlicher Link: " + gefaehrlicher_link if gefaehrlicher_link else ""}
Beschreibung: {beschreibung}
{"Weitere Infos: " + weitere_infos if weitere_infos else ""}
Datum: {datum}
Tags: {", ".join(tags)}
Status: {status}"""
                    
                    pubDate = convert_date_to_rfc2822(datum)
                    
                    item = ITEM_TEMPLATE.format(
                        title=escape_html(title),
                        description_text=escape_html(description_text),
                        description_html=description_html,
                        pubDate=pubDate,
                        guid=id_val
                    )
                    items.append(item)
            
            except Exception as e:
                print(f"❌ Fehler bei {filename}: {e}")
    
    rss_content = RSS_TEMPLATE.format(items="\n".join(items))
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)
    
    print(f"✅ RSS Feed generiert: {OUTPUT_FILE}")
    print(f"✅ {len(items)} Meldungen verarbeitet")

if __name__ == "__main__":
    generate_rss()

