#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает три статические страницы из scripts/content.py.

    python3 scripts/build.py

На выходе: index.html (ru), en/index.html, uz/index.html и sitemap.xml.
Разделы без данных (например «Отзывы», пока нет цитат) не выводятся.
"""

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import (DATA, LANGS, SITE, PHONE, PHONE_TEXT, EMAIL,  # noqa: E402
                     INSTAGRAM, LINKEDIN, FACEBOOK, TRACK_YEARS,
                     PHOTOS_WORK, PHOTOS_TEAM, CAREER, CAREER_YEARS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_VERSION = 7

URLS = {code: url for code, _, url in LANGS}

# Официальные глифы соцсетей. Логотипы, а не рисованные иконки.
GLYPHS = {
    "Instagram": "M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z",
    "LinkedIn": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z",
    "Facebook": "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z",
}


def e(text):
    """Экранирует текст для вставки в HTML."""
    return html.escape(str(text), quote=True)


def out_path(lang):
    return "index.html" if lang == "ru" else f"{lang}/index.html"


DEPTH = 0  # 0 — страница в своей языковой папке, 1 — вложенная (media/)


def asset(lang, path):
    """Путь к файлу в корне сайта относительно текущей страницы."""
    up = (0 if lang == "ru" else 1) + DEPTH
    return ("../" * up) + path


def src_link(item, label):
    if not item.get("href"):
        return ""
    return (f'<a class="src" href="{e(item["href"])}" target="_blank" rel="noopener">'
            f'{e(label)}</a>')


def glyph(name, href):
    return (f'<a class="glyph" href="{href}" target="_blank" rel="noopener me" '
            f'aria-label="{name}" title="{name}">'
            f'<svg viewBox="0 0 24 24" role="img" aria-hidden="true">'
            f'<path d="{GLYPHS[name]}"/></svg></a>')


# ── блоки страницы ───────────────────────────────────────────────────────────

def head(lang, t, page=""):
    suffix = "media/" if page == "media" else ""
    canonical = SITE + URLS[lang] + suffix
    alts = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}{u}{suffix}">'
                     for c, _, u in LANGS)
    return f"""<!DOCTYPE html>
<html lang="{t['htmlLang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['mediaPageTitle'] + ' — ' + t['name']) if page == 'media' else e(t['title'])}</title>
<meta name="description" content="{e(t['description'])}">
<meta name="theme-color" content="#101114">
<meta name="color-scheme" content="dark">

<meta property="og:type" content="profile">
<meta property="og:title" content="{e(t['title'])}">
<meta property="og:description" content="{e(t['description'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/img/speaker-taf26.webp">
<meta property="og:locale" content="{t['ogLocale']}">
<meta name="twitter:card" content="summary_large_image">

{alts}
<link rel="alternate" hreflang="x-default" href="{SITE}/">
<link rel="canonical" href="{canonical}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

<link rel="stylesheet" href="{asset(lang, 'site.css')}?v={CSS_VERSION}">
</head>
<body>
<a class="skip" href="#main">{e(t['skipLink'])}</a>
<div class="wrap">
"""


def header(lang, t):
    current = ' aria-current="page"'
    langs = "\n".join(
        f'      <a href="{u}" hreflang="{c}"{current if c == lang else ""}>{lb}</a>'
        for c, lb, u in LANGS)
    return f"""  <header class="top">
    <a class="brand" href="{URLS[lang]}">{e(t['name'])} &nbsp;<span>{e(t['jobTitle'])}</span></a>
    <a class="tel mono" href="tel:{PHONE}">{e(PHONE_TEXT)}</a>
    <nav class="langs mono" aria-label="{e(t['langLabel'])}">
{langs}
    </nav>
  </header>
"""


def intro(lang, t):
    posts = "\n".join(
        f'        <li><i class="mono">{i:02d}</i><span>{e(s)}</span></li>'
        for i, s in enumerate(t["statuses"][:3], 1))
    return f"""
  <main id="main">
  <section class="intro">
    <figure>
      <img src="{asset(lang, 'img/speaker-taf26.webp')}" width="1000" height="1000"
           alt="{e(t['photoAlt'])}" fetchpriority="high">
    </figure>
    <div>
      <h1>{e(t['name'])}</h1>
      <div class="post">{e(t['kicker'])}</div>
      <p class="lede">{e(t['lede'])}</p>
    </div>
    <ul class="posts">
{posts}
    </ul>
  </section>
"""


def timeline(segments, years_range, title, note=""):
    """Лента карьеры: отрезки позиционируются в долях года, поэтому
    периоды не наслаиваются друг на друга даже при смене работы в середине года."""
    first, last = years_range[0], years_range[-1] + 1
    span = last - first
    n = len(years_range)
    years = "".join(f'<span>{y if i % 2 == 0 else ""}</span>'
                    for i, y in enumerate(years_range))
    lanes = []
    for seg in segments:
        left = (seg["from"] - first) / span * 100
        width = (seg["to"] - seg["from"]) / span * 100
        cls = "seg key" if seg.get("key") else "seg"
        lanes.append(f'        <div class="lane abs">'
                     f'<div class="{cls}" style="left: {left:.2f}%; width: {width:.2f}%">'
                     f'<span>{e(seg["org"])}</span></div></div>')
    return f"""
  <section class="track-scroll">
    <div class="track track-inner" style="--col: calc(100% / {n})">
      <div class="track-h">
        <h2 class="cap">{e(title)}</h2>
        <div class="note mono">{e(note) if note else f"{years_range[0]} — {years_range[-1]}"}</div>
      </div>
      <div class="years" style="grid-template-columns: repeat({n}, 1fr)">{years}</div>
      <div class="lanes">
{chr(10).join(lanes)}
      </div>
    </div>
  </section>
"""


def scale(segments, years_range, title, labels=None, every=1):
    """Шкала: реальные интервалы, а не декоративные полосы.

    every — шаг подписей по годам (для длинной шкалы карьеры подписываем не каждый год).
    """
    n = len(years_range)
    years = "".join(
        f'<span>{y if i % every == 0 else ""}</span>' for i, y in enumerate(years_range))
    lanes = []
    for i, seg in enumerate(segments):
        start = years_range.index(seg["from"]) + 1
        end = years_range.index(seg["to"]) + 2 if seg.get("to") else -1
        cls = "seg key" if seg.get("key") else "seg"
        label = labels[i] if labels else seg["label"]
        lanes.append(f'        <div class="lane" style="grid-template-columns: repeat({n}, 1fr)">'
                     f'<div class="{cls}" style="grid-column: {start} / {end}">'
                     f'{e(label)}</div></div>')
    return f"""
  <section class="track-scroll">
    <div class="track track-inner" style="--col: calc(100% / {n})">
      <div class="track-h">
        <h2 class="cap">{e(title)}</h2>
        <div class="note mono">{years_range[0]} — {years_range[-1]}</div>
      </div>
      <div class="years" style="grid-template-columns: repeat({n}, 1fr)">{years}</div>
      <div class="lanes">
{chr(10).join(lanes)}
      </div>
    </div>
  </section>
"""


def section(title, body, count=None):
    if not body:
        return ""
    meta = f'      <div class="count mono">{e(count)}</div>\n' if count else ""
    return f"""
  <section class="sec">
    <div class="sec-h">
      <h2>{e(title)}</h2>
{meta}    </div>
{body}
  </section>
"""


def rows(items, t, main_key, sub_key, meta_key):
    if not items:
        return ""
    out = []
    for it in items:
        sub = (f'\n        <div class="s">{e(it[sub_key])}</div>'
               if sub_key and it.get(sub_key) else "")
        out.append(f"""    <div class="row">
      <div><div class="t">{e(it[main_key])}</div>{sub}</div>
      <div class="m">{e(it.get(meta_key, ""))}</div>
      {src_link(it, t["proof"])}
    </div>""")
    return "\n".join(out)


def photos(lang, t, files, title_key, caption_key):
    """Кадры с подписями. Подпись — часть факта, а не украшение."""
    captions = t[caption_key]
    if not files or not captions:
        return ""
    cells = "\n".join(f"""      <figure class="shot">
        <img src="{asset(lang, 'img/' + f)}" alt="{e(c)}" loading="lazy" decoding="async">
        <figcaption class="mono">{e(c)}</figcaption>
      </figure>""" for f, c in zip(files, captions))
    return section(t[title_key], f'    <div class="shots">\n{cells}\n    </div>')


def career(t):
    if not t["jobs"]:
        return ""
    rows_html = []
    for job, place in zip(t["jobs"], CAREER):
        rows_html.append(f"""    <div class="row job">
      <div>
        <div class="t">{e(place["org"])}</div>
        <div class="s">{e(job["role"])}</div>
        <p class="note">{e(job["note"])}</p>
      </div>
      <div class="m">{e(job["when"])}</div>
    </div>""")
    return section(t["careerTitle"], "\n".join(rows_html), t["careerNote"])


def person(t):
    if not t["person"]:
        return ""
    body = "\n".join(f"""    <div class="skill">
      <div class="g">{e(f["k"])}</div>
      <div class="v">{e(f["v"])}</div>
    </div>""" for f in t["person"])
    return section(t["personTitle"], body)


def about(t):
    body = "\n".join(f'      <p>{e(p)}</p>' for p in t["about"])
    return section(t["aboutTitle"], f'    <div class="prose">\n{body}\n    </div>')


def awards(t):
    if not t["awards"]:
        return ""
    cards = "\n".join(f"""      <div class="award">
        <div class="y">{e(a['year'])}</div>
        <div class="t">{e(a['title'])}</div>
        <p>{e(a['desc'])}</p>
        {src_link(a, t['proof'])}
      </div>""" for a in t["awards"])
    return section(t["awardsTitle"], f'    <div class="awards">\n{cards}\n    </div>')


def skills(t):
    if not t["skills"]:
        return ""
    body = "\n".join(f"""    <div class="skill">
      <div class="g">{e(s['group'])}</div>
      <div class="v">{e(s['items'])}</div>
    </div>""" for s in t["skills"])
    return section(t["skillsTitle"], body)


def quotes(t):
    if not t["quotes"]:
        return ""
    body = "\n".join(f"""    <div class="row">
      <div><div class="t">{e(q['text'])}</div>
        <div class="s">{e(q['author'])}</div></div>
      <div class="m"></div>
    </div>""" for q in t["quotes"])
    return section(t["quotesTitle"], body)


def contact(t):
    glyphs = [glyph("Instagram", INSTAGRAM), glyph("LinkedIn", LINKEDIN)]
    if FACEBOOK:
        glyphs.append(glyph("Facebook", FACEBOOK))
    return f"""
  <section class="contact">
    <div>
      <h2 class="cap">{e(t['contactKicker'])}</h2>
      <div class="lines">
        <a href="tel:{PHONE}">
          <b>{e(t['phoneLabel'])}</b>
          <span class="v mono">{e(PHONE_TEXT)}</span>
        </a>
        <a href="mailto:{EMAIL}">
          <b>{e(t['emailLabel'])}</b>
          <span class="v">{EMAIL}</span>
        </a>
      </div>
    </div>
    <div class="glyphs">
      {"".join(glyphs)}
    </div>
  </section>
  </main>
"""


def json_ld(lang, t):
    same_as = [INSTAGRAM, LINKEDIN] + ([FACEBOOK] if FACEBOOK else []) + [
        "https://marketing.uz/about/board/kim-igor.htm",
        "https://uz.kursiv.media/expert/igor-kim/",
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": t["name"],
        "url": SITE + URLS[lang],
        "image": f"{SITE}/img/speaker-taf26.webp",
        "jobTitle": t["jobTitle"],
        "telephone": PHONE,
        "email": EMAIL,
        "worksFor": {"@type": "Organization", "name": "Wunder Digital Uzbekistan",
                     "url": "https://wunder-digital.uz/"},
        "memberOf": {"@type": "Organization", "name": "Marketing Association of Uzbekistan",
                     "url": "https://marketing.uz/"},
        "address": {"@type": "PostalAddress", "addressLocality": "Tashkent", "addressCountry": "UZ"},
        "knowsAbout": [s["items"] for s in t["skills"]],
        "sameAs": same_as,
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def footer(lang, t):
    return f"""
  <div class="copy">
    <span>© 2026 {e(t['name'])}</span>
    <span>{e(t['place'])}</span>
  </div>
</div>
{json_ld(lang, t)}
</body>
</html>
"""


# ── сборка ───────────────────────────────────────────────────────────────────

def build_page(lang):
    t = DATA[lang]
    n = lambda items, word: f"{len(items)} {word}"  # noqa: E731
    return "".join([
        head(lang, t),
        header(lang, t),
        intro(lang, t),
        scale(t["track"], TRACK_YEARS, t["trackTitle"]),
        photos(lang, t, PHOTOS_WORK, "workTitle", "work"),
        about(t),
        person(t),
        timeline(CAREER, CAREER_YEARS, t["careerTitle"], t["careerNote"]),
        career(t),
        section(t["rolesTitle"], rows(t["roles"], t, "title", "org", "period")),
        awards(t),
        section(t["talksTitle"], rows(t["talks"], t, "event", "sub", "meta"),
                n(t["talks"], t["unitEvents"])),
        section(t["juryTitle"], rows(t["jury"], t, "event", "sub", "meta"),
                n(t["jury"], t["unitJury"])),
        skills(t),
        section(t["mediaTitle"], rows(t["media"][:6], t, "title", None, "outlet")
                + more_link(lang, t), n(t["media"] + t["pages"], t["unitMedia"])),
        quotes(t),
        photos(lang, t, PHOTOS_TEAM, "teamTitle", "team"),
        contact(t),
        footer(lang, t),
    ])


def more_link(lang, t):
    """Ссылка на полный список — он живёт отдельной страницей."""
    return (f'\n    <a class="more" href="{media_url(lang)}">'
            f'{e(t["mediaAll"])} →</a>')


def media_url(lang):
    return URLS[lang] + "media/"


def build_media_page(lang):
    """Отдельная страница: все публикации и официальные страницы."""
    t = DATA[lang]
    body = (head(lang, t, page="media")
            + header(lang, t)
            + f'\n  <main id="main">\n  <section class="sec first">\n'
              f'    <div class="sec-h"><h2>{e(t["mediaTitle"])}</h2>'
              f'<div class="count mono">{len(t["media"])} {e(t["unitMedia"])}</div></div>\n'
            + rows(t["media"], t, "title", None, "outlet")
            + "\n  </section>\n"
            + section(t["pagesTitle"], rows(t["pages"], t, "title", None, "outlet"),
                      f'{len(t["pages"])} {t["unitPages"]}')
            + f'\n  <p class="back"><a href="{URLS[lang]}">← {e(t["backHome"])}</a></p>\n'
              f'  </main>\n'
            + footer(lang, t))
    return body


def build_sitemap():
    items = [(u, "1.0" if u == "/" else "0.8") for _, _, u in LANGS]
    items += [(u + "media/", "0.5") for _, _, u in LANGS]
    urls = "\n".join(
        f"  <url>\n    <loc>{SITE}{u}</loc>\n    <changefreq>monthly</changefreq>\n"
        f"    <priority>{pr}</priority>\n  </url>" for u, pr in items)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + urls + "\n</urlset>\n")


def main():
    global DEPTH
    for lang, _, _ in LANGS:
        DEPTH = 0
        path = os.path.join(ROOT, out_path(lang))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_page(lang))
        print(f"  {out_path(lang)}")

        DEPTH = 1
        mpath = os.path.join(ROOT, media_url(lang).strip("/"), "index.html")
        os.makedirs(os.path.dirname(mpath), exist_ok=True)
        with open(mpath, "w", encoding="utf-8") as f:
            f.write(build_media_page(lang))
        print(f"  {media_url(lang).strip('/')}/index.html")
    DEPTH = 0

    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap())
    print("  sitemap.xml")


if __name__ == "__main__":
    main()
