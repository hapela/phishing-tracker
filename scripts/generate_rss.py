import html
import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import quote

REPORTS_DIR = "reports"
BASE_URL = "https://hapela.github.io/phishing-tracker"

ISB_FEED = "feed_isb.xml"
USER_FEED = "feed_user.xml"


def text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)

    return html.escape(str(value))


def cdata(value):
    value = str(value or "")
    return value.replace("]]>", "]]]]><![CDATA[>")


def parse_date(value):
    if not value:
        return datetime.now(timezone.utc)

    try:
        value = str(value).replace("Z", "+00:00")
        result = datetime.fromisoformat(value)

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result
    except ValueError:
        return datetime.now(timezone.utc)


def load_reports():
    reports = []

    if not os.path.isdir(REPORTS_DIR):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        return reports

    for filename in sorted(os.listdir(REPORTS_DIR)):
        if not filename.lower().endswith(".json"):
            continue

        path = os.path.join(REPORTS_DIR, filename)

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = json.load(file)

            entries = content.get("meldungen", [])

            if isinstance(entries, dict):
                entries = [entries]

            for entry in entries:
                if isinstance(entry, dict):
                    reports.append(entry)

        except Exception as error:
            print(f"Fehler beim Lesen von {filename}: {error}")

    return reports


def screenshot_url(report):
    screenshot = str(report.get("screenshot", "")).strip()

    if not screenshot:
        return ""

    if screenshot.startswith(("http://", "https://")):
        return screenshot

    return f"{BASE_URL}/{screenshot.lstrip('/')}"


def report_description(report, audience):
    screenshot = screenshot_url(report)

    image_html = ""

    if screenshot:
        image_html = f"""
<p>
  <img
    src="{html.escape(screenshot, quote=True)}"
    alt="Screenshot zur Meldung"
    style="max-width:100%;height:auto;border-radius:12px;"
  >
</p>
"""

    link_html = ""

    if audience == "isb" and report.get("gefaehrlicher_link"):
        link = text(report["gefaehrlicher_link"])
        link_html = f"""
<p>
  <strong>Gefährlicher Link:</strong><br>
  <code>{link}</code>
</p>
"""

    if audience == "isb":
        main_description = report.get("beschreibung_ISB", "")
        additional = f"""
<p>
  <strong>Maßnahmen des Nutzers:</strong><br>
  {text(report.get("Maßnahmen_nutzer", ""))}
</p>
"""
    else:
        main_description = report.get("beschreibung_nutzer", "")
        additional = ""

    return f"""<![CDATA[
<div style="font-family:Arial,sans-serif;line-height:1.6;color:#172033;">
  <h2>{text(report.get("betreff", "Sicherheitsmeldung"))}</h2>

  <p>
    <strong>Meldungs-ID:</strong> {text(report.get("id"))}<br>
    <strong>Status:</strong> {text(report.get("status"))}<br>
    <strong>Gemeldet von:</strong> {text(report.get("melder"))}<br>
    <strong>Datum der Meldung:</strong> {text(report.get("datum_meldung"))}<br>
    <strong>Datum der E-Mail:</strong> {text(report.get("datum_mail"))}<br>
    <strong>Absender:</strong> {text(report.get("absender"))}
  </p>

  {link_html}

  <p>
    <strong>Beschreibung:</strong><br>
    {text(main_description)}
  </p>

  {additional}

  {image_html}
</div>
]]>"""


def build_item(report, audience):
    report_id = str(report.get("id", "unbekannt"))
    subject = str(report.get("betreff", "Sicherheitsmeldung"))
    date = parse_date(report.get("datum_mail") or report.get("datum_meldung"))

    return f"""
<item>
  <title>{text(subject)}</title>
  <link>{BASE_URL}/#meldung-{quote(report_id)}</link>
  <guid isPermaLink="false">{text(report_id)}-{audience}</guid>
  <pubDate>{format_datetime(date, usegmt=True)}</pubDate>
  <description>{report_description(report, audience)}</description>
</item>
"""


def build_feed(reports, audience, title, filename):
    items = sorted(
        reports,
        key=lambda item: parse_date(
            item.get("datum_mail") or item.get("datum_meldung")
        ),
        reverse=True,
    )

    now = format_datetime(datetime.now(timezone.utc), usegmt=True)

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{html.escape(title)}</title>
    <link>{BASE_URL}</link>
    <description>Automatisch generierter Sicherheitsmeldungs-Feed</description>
    <language>de-de</language>
    <lastBuildDate>{now}</lastBuildDate>
    {''.join(build_item(item, audience) for item in items)}
  </channel>
</rss>
"""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(xml)

    print(f"{filename}: {len(items)} Meldungen verarbeitet")


def main():
    reports = load_reports()

    build_feed(
        reports,
        "isb",
        "Sicherheitsmeldungen für ISB",
        ISB_FEED,
    )

    build_feed(
        reports,
        "user",
        "Sicherheitsmeldungen für Nutzer",
        USER_FEED,
    )


if __name__ == "__main__":
    main()
