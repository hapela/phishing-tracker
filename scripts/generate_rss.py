import json
import os
from datetime import datetime
from email.utils import formatdate

REPORTS_DIR = "reports"
OUTPUT_FILE = "feed.xml"
BASE_URL = "https://hapela.github.io/phishing-tracker"  # Anpassen!

RSS_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Sicherheitsmeldungen</title>
    <link>{base_url}</link>
    <description>Automatisch generierter Feed aus Sicherheitsmeldungen</description>
    <language>de-de</language>
    <lastBuildDate>{lastBuildDate}</lastBuildDate>
"""

RSS_FOOTER = """  </channel>
</rss>
"""

ITEM_TEMPLATE = """    <item>
      <title>{title}</title>
      <pubDate>{pubDate}</pubDate>
      <guid>{guid}</guid>
      <description>
<![CDATA[
<table width="100%" cellpadding="10" cellspacing="0" border="0" 
       style="font-family:Segoe UI,Arial,sans-serif;border:1px solid #cccccc;">
    <tr>
       <td bgcolor="#c62828" style="color:white;font-size:22px;font-weight:bold;">
        🚨 SICHERHEITSWARNUNG
       </td>
    </tr>

    <tr>
       <td>
           <h2 style="margin:0;"> {typ} </h2>
       </td>
    </tr>

    <tr>
       <td bgcolor="#fff4e5">
           <strong>Risiko:</strong> KRITISCH<br>
           <strong>Datum:</strong> {datum} <br>
           <strong>gemeldet von: </strong> Heinz Herrmann
       </td>
    </tr>

    <tr>
       <td>
           <strong>📧 Absender </strong> (kann sich ggf. ändern)<br>
           {absender}
       </td>
    </tr>

    <tr>
       <td>
           <strong>🔗 Gefährlicher Link </strong>(kann sich ggf. ändern)<br>
           <code> {gefaehrlicher_link_block} </code>
       </td>
    </tr>

    <tr>
       <td align="center">
           <img
           src=" {screenshot_block} "
           width="600"
           alt="Screenshot der Phishing-Mail">
       </td>
    </tr>

    <tr>
       <td>
           <strong>ℹ Beschreibung</strong><br>
           {beschreibung}
       </td>
    </tr>

    <tr>
       <td bgcolor="#e8f5e9">
           <strong>ℹ Weitere Infos zu dieser Meldung</strong><br>
           <a href="https://www.virustotal.com/gui/url/0ebfae129a2dd74e55a06f698a273d94763592f54f227eb5b35677e2bfb9dd41">
              bei VirusTotal öffnen
           </a>
       </td>
    </tr>

    <tr>
       <td bgcolor="#f5f5f5">
           <strong>🎯 Empfohlene Maßnahmen</strong>
           </li>
             <li>Mail umgehend löschen</li>
             <li>IT-Security informieren</li>
           </ul>
       </td>
    </tr>

</table>
]]>
      </description>
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
    
    for filename in sorted(os.listdir(REPORTS_DIR), reverse=True):
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
                    datum = meldung.get("datum", "")
                    gefaehrlicher_link = meldung.get("gefaehrlicher_link", "")
                    screenshot = meldung.get("screenshot", "")
                    
                    title = escape_html(betreff)
                    typ_escaped = escape_html(typ)
                    absender_escaped = escape_html(absender)
                    beschreibung_escaped = escape_html(beschreibung)
                    datum_escaped = escape_html(datum)
                    
                    # Gefährlicher Link Block (optional)
                    if gefaehrlicher_link:
                        gefaehrlicher_link_block = f"""<p style="margin: 0 0 8px 0;"><strong>🔗 Gefährlicher Link:</strong></p>
          <blockquote style="margin: 0 0 12px 24px; padding: 0;">
             {escape_html(gefaehrlicher_link)}
          </blockquote>
          """
                    else:
                        gefaehrlicher_link_block = ""
                    
                    # Screenshot Block (optional)
                    if screenshot:
                        screenshot_url = f"{BASE_URL}/{screenshot}" if not screenshot.startswith("http") else screenshot
                        screenshot_block = f"""<p><strong>Screenshot der Mail:</strong></p>
          <p>
           <img
            src="{escape_html(screenshot_url)}"
            alt="Screenshot"
            style="max-width:600px;" />
          </p>"""
                    else:
                        screenshot_block = ""
                    
                    pubDate = convert_date_to_rfc2822(datum)
                    
                    item = ITEM_TEMPLATE.format(
                        title=title,
                        pubDate=pubDate,
                        guid=escape_html(id_val),
                        typ=typ_escaped,
                        absender=absender_escaped,
                        beschreibung=beschreibung_escaped,
                        datum=datum_escaped,
                        gefaehrlicher_link_block=gefaehrlicher_link_block,
                        screenshot_block=screenshot_block
                    )
                    items.append(item)
            
            except Exception as e:
                print(f"❌ Fehler bei {filename}: {e}")
    
    # Aktuelles Datum für lastBuildDate
    lastBuildDate = formatdate(localtime=False, usegmt=True)
    
    rss_content = RSS_HEADER.format(
        base_url=BASE_URL,
        lastBuildDate=lastBuildDate
    )
    rss_content += "\n".join(items)
    rss_content += RSS_FOOTER
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)
    
    print(f"✅ RSS Feed generiert: {OUTPUT_FILE}")
    print(f"✅ {len(items)} Meldungen verarbeitet")
    print(f"✅ Letzte Aktualisierung: {lastBuildDate}")

if __name__ == "__main__":
    generate_rss()
