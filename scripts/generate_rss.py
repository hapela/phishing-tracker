#!/usr/bin/env python3
"""
RSS-Feed Generator für Schadhafte Mails
Liest JSON-Dateien aus dem reports/ Ordner und generiert feed.xml
"""

import json
import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import sys

def generate_rss():
    """Generiert RSS-Feed aus JSON-Dateien"""
    
    # RSS-Root-Element
    rss = Element('rss', {
        'version': '2.0',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    
    channel = SubElement(rss, 'channel')
    
    # Channel-Metadaten
    SubElement(channel, 'title').text = 'Meldungen verdächtiger E-Mails'
    SubElement(channel, 'link').text = 'https://github.com/dein-username/mail-reports'
    SubElement(channel, 'description').text = 'Zentrales Tracking von Phishing-, Spam- und Malware-Mails'
    SubElement(channel, 'language').text = 'de'
    SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    # Alle JSON-Dateien einlesen (neueste zuerst)
    reports_dir = 'reports'
    if not os.path.exists(reports_dir):
        print(f"⚠️ Ordner '{reports_dir}' nicht gefunden. Leeren Feed erstellen.")
        files = []
    else:
        files = sorted(
            [f for f in os.listdir(reports_dir) if f.endswith('.json')],
            reverse=True
        )
    
    item_count = 0
    
    for filename in files:
        filepath = os.path.join(reports_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if 'meldungen' in data:
                    for mail in data['meldungen']:
                        # Neue RSS-Item für jede Meldung
                        item = SubElement(channel, 'item')
                        
                        # Titel mit Typ-Indikator
                        typ = mail.get('typ', 'unbekannt').upper()
                        title = f"[{typ}] {mail.get('betreff', 'Keine Betreffzeile')}"
                        SubElement(item, 'title').text = title
                        
                        # Beschreibung mit allen Details
                        description = f"""
Von: {mail.get('absender', 'N/A')}
Typ: {mail.get('typ', 'unbekannt').upper()}
Status: {mail.get('status', 'unbekannt')}

{mail.get('beschreibung', 'Keine Beschreibung')}

Tags: {', '.join(mail.get('tags', []))}
"""
                        SubElement(item, 'description').text = description.strip()
                        
                        # Datum (RFC 822 Format für RSS)
                        # Annahme: Datum im Format YYYY-MM-DD
                        try:
                            date_obj = datetime.strptime(mail.get('datum', ''), '%Y-%m-%d')
                            pub_date = date_obj.strftime('%a, %d %b %Y 12:00:00 +0000')
                        except:
                            pub_date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
                        
                        SubElement(item, 'pubDate').text = pub_date
                        
                        # Eindeutige ID
                        SubElement(item, 'guid', {'isPermaLink': 'false'}).text = mail.get('id', 'no-id')
                        
                        # Kategorie
                        for tag in mail.get('tags', []):
                            SubElement(item, 'category').text = tag
                        
                        item_count += 1
        
        except json.JSONDecodeError as e:
            print(f"❌ Fehler beim Parsen von {filename}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Fehler bei {filename}: {e}", file=sys.stderr)
    
    # XML in Datei schreiben
    xml_str = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(rss, encoding='UTF-8')
    
    with open('feed.xml', 'wb') as f:
        f.write(xml_str)
    
    print(f"✅ RSS-Feed erfolgreich generiert: {item_count} Meldungen")
    return item_count

if __name__ == '__main__':
    generate_rss()
