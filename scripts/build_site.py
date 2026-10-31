#!/usr/bin/env python3
"""Generate everything that comes from data/fixes.json and data/picks.json.

Writes fix/<slug>/index.html, sitemap.xml, robots.txt, and the generated blocks
between <!-- name:start --> markers in index.html. index.html's header and
footer are the source for the fix pages. Rerunning produces no diff.
"""
from __future__ import annotations

import json
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://higgprojects.com"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SUBSCRIBE = "https://www.youtube.com/@higgprojects?sub_confirmation=1"
ANALYTICS = """<!-- Cloudflare Web Analytics -->
<script defer src="https://static.cloudflareinsights.com/beacon.min.js"
  data-cf-beacon='{"token": "615b5ca398ab416fbdaf0584b4b9a62d"}'></script>
<!-- End Cloudflare Web Analytics -->"""


def e(text: str) -> str:
    return escape(text, quote=True)


def thumb(video_id: str, size: str = "hqdefault") -> str:
    return f"https://img.youtube.com/vi/{e(video_id)}/{size}.jpg"


def sponsored(item: dict) -> str:
    return f'<a href="{e(item["link"])}" rel="sponsored noopener" target="_blank">{e(item["name"])}</a>'


def facade(fix: dict) -> str:
    video, title = fix["video"], e(fix["title"])
    vid = e(video["id"])
    if video["short"]:
        img = f'<img src="{thumb(vid)}" alt="Video thumbnail: {title}" width="480" height="360">'
    else:
        fallback = f"this.onerror=null;this.src='{thumb(vid)}'"
        img = (
            f'<img src="{thumb(vid, "maxresdefault")}" onerror="{fallback}" '
            f'alt="Video thumbnail: {title}" width="1280" height="720">'
        )
    classes = "facade is-short" if video["short"] else "facade"
    return (
        f'<div class="{classes}">{img}'
        f'<button type="button" class="facade-play" data-video="{vid}" data-title="{title}" aria-label="Play: {title}">'
        '<span aria-hidden="true">&#9654;</span></button></div>'
    )


def kit_block(fix: dict) -> str:
    kit, note = fix.get("kit") or [], fix.get("kitNote")
    if not kit and not note:
        return ""
    parts = ['<div class="kit">', "<h3>What I used</h3>"]
    if kit:
        rows = "".join(f"<li>{sponsored(item)}</li>" for item in kit)
        parts.append(f'<ul class="kit-list">{rows}</ul>')
    if note:
        parts.append(f'<p class="kit-note">{e(note)}</p>')
    if kit:
        parts.append(f'<p class="disclosure">{DISCLOSURE}</p>')
    parts.append("</div>")
    return "\n".join(parts)


# ---- generated blocks in index.html ------------------------------------------
def chips_block(fixes: list[dict]) -> str:
    rows = ['<button type="button" class="chip chip-latest" data-chip="latest" aria-pressed="false">Show me the latest</button>']
    for i, fix in enumerate(fixes):
        current = ' aria-current="true"' if i == 0 else ""
        rows.append(
            f'<a class="chip" href="/fix/{e(fix["slug"])}/" data-chip="{e(fix["slug"])}"{current}>{e(fix["problem"])}</a>'
        )
    return "\n".join(rows)


def panel_block(fixes: list[dict]) -> str:
    fix = fixes[0]
    return "\n".join(
        [
            facade(fix),
            '<div class="panel-body">',
            f'<h2 class="panel-title" id="panel-title" tabindex="-1">{e(fix["title"])}</h2>',
            f'<p class="panel-summary">{e(fix["summary"])}</p>',
            kit_block(fix),
            f'<a class="btn btn-ghost" href="/fix/{e(fix["slug"])}/">See the steps</a>',
            "</div>",
        ]
    )


def picks_block(picks: dict) -> str:
    out = []
    for shelf in picks["shelves"]:
        rows = []
        for item in shelf["items"]:
            url = f'https://www.amazon.com/dp/{e(item["asin"])}?tag=leehigginson-20'
            how = f'<span class="pick-how">{e(item["how"])}</span> ' if item.get("how") else ""
            watch = (
                f'<a class="quiet-link" href="https://www.youtube.com/watch?v={e(item["video"])}">Watch the video</a>'
                if item.get("video")
                else ""
            )
            extra = f'<p class="pick-extra">{how}{watch}</p>' if how or watch else ""
            rows.append(
                '<li class="pick">'
                f'<a class="pick-name" href="{url}" rel="sponsored noopener" target="_blank">{e(item["name"])}</a>'
                f'<div class="pick-why"><p class="pick-line">&ldquo;{e(item["line"])}&rdquo;</p>{extra}</div>'
                "</li>"
            )
        out.append(
            f'<div class="shelf">\n<h3>{e(shelf["name"])}</h3>\n<ul class="shelf-list">\n' + "\n".join(rows) + "\n</ul>\n</div>"
        )
    return "\n".join(out)


def videos_block(fixes: list[dict]) -> str:
    out = []
    for fix in fixes:
        if fix["video"]["short"]:
            continue
        vid = e(fix["video"]["id"])
        kit = fix.get("kit") or []
        used = f'<p class="video-kit">What I used: {", ".join(sponsored(item) for item in kit)}</p>' if kit else ""
        out.append(
            '<article class="video">'
            f'<a class="video-link" href="https://www.youtube.com/watch?v={vid}">'
            f'<img src="{thumb(vid)}" alt="" loading="lazy" width="480" height="270">'
            f'<h3>{e(fix["title"])}</h3></a>{used}</article>'
        )
    return "\n".join(out)


def footer_fixes_block(fixes: list[dict]) -> str:
    return "\n".join(f'<li><a href="/fix/{e(fix["slug"])}/">{e(fix["problem"])}</a></li>' for fix in fixes)


def replace_block(html: str, name: str, body: str) -> str:
    pattern = re.compile(rf"([ \t]*)<!-- {name}:start -->.*?<!-- {name}:end -->", re.S)
    if not pattern.search(html):
        raise SystemExit(f"index.html is missing the {name} markers")

    def fill(m: re.Match) -> str:
        pad = m.group(1)
        lines = "\n".join(pad + line for line in body.split("\n"))
        return f"{pad}<!-- {name}:start -->\n{lines}\n{pad}<!-- {name}:end -->"

    return pattern.sub(fill, html)


# ---- fix pages ----------------------------------------------------------------
def steps_block(fix: dict) -> str:
    vid = e(fix["video"]["id"])
    rows = []
    for step in fix["steps"]:
        link = (
            f' <a class="quiet-link" href="https://youtu.be/{vid}?t={int(step["t"])}" target="_blank" rel="noopener">Watch this part</a>'
            if "t" in step
            else ""
        )
        rows.append(f'<li>{e(step["text"])}{link}</li>')
    return '<ol class="steps">\n' + "\n".join(rows) + "\n</ol>"


def also_block(fix: dict) -> str:
    also = fix.get("also") or []
    if not also:
        return ""
    rows = "".join(
        f'<a class="also-real" href="https://www.youtube.com/watch?v={e(v["id"])}">'
        f'<img src="{thumb(v["id"], "mqdefault")}" alt="" loading="lazy" width="120" height="68">'
        f'<span class="also-real-text"><strong>{e(v["title"])}</strong></span></a>'
        for v in also
    )
    return f'<div class="also">\n<h2>Watch this too</h2>\n{rows}\n</div>'


def fix_page(fix: dict, header: str, footer: str) -> str:
    slug, video = fix["slug"], fix["video"]
    url = f"{SITE}/fix/{slug}/"
    title = e(f'{fix["title"]} | Higg Projects')
    desc = e(fix["summary"])
    image = thumb(video["id"])
    ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": fix["title"],
            "description": fix["summary"],
            "thumbnailUrl": f'https://img.youtube.com/vi/{video["id"]}/hqdefault.jpg',
            "uploadDate": video["uploadDate"],
            "duration": video["duration"],
            "embedUrl": f'https://www.youtube.com/embed/{video["id"]}',
        },
        ensure_ascii=False,
        indent=2,
    ).replace("</", "<\\/")
    caution = f'<p class="tape-chip tape-note">{e(fix["caution"])}</p>' if fix.get("caution") else ""
    body = "\n".join(
        part
        for part in [
            f'<h1 class="fix-title">{e(fix["problem"])}</h1>',
            f'<p class="lede">{e(fix["title"])}</p>',
            f'<p class="fix-story">{e(fix["story"])}</p>',
            facade(fix),
            "<h2>What I did</h2>",
            steps_block(fix),
            caution,
            kit_block(fix),
            also_block(fix),
            '<div class="share"><button type="button" class="btn btn-ghost share-btn">Send this to someone who needs it</button>'
            '<p class="share-status" role="status"></p></div>',
            '<p class="fix-more"><a href="/#fixes">Stuck on something else?</a></p>',
            f'<p class="fix-subscribe"><a class="subscribe-link" href="{SUBSCRIBE}">Subscribe</a></p>',
        ]
        if part
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#131020">
<meta property="og:title" content="{e(fix["title"])}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(fix["title"])}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<link rel="icon" type="image/png" href="/images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Karla:ital,wght@0,400..800;1,400..700&family=Lora:ital,wght@0,500..600;1,400..600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{header}
<main id="main">
<article class="wrap fix-page">
{body}
</article>
</main>
{footer}
<script defer src="/site.js"></script>
{ANALYTICS}
</body>
</html>
"""


def shared_chrome(html: str, tag: str) -> str:
    chrome = re.search(rf"<{tag} class=[^>]*>.*?</{tag}>", html, re.S).group(0)
    return re.sub(r'href="#', 'href="/#', chrome)


def main() -> None:
    fixes = json.loads((ROOT / "data/fixes.json").read_text(encoding="utf-8"))
    picks = json.loads((ROOT / "data/picks.json").read_text(encoding="utf-8"))
    for fix in fixes:
        if not re.fullmatch(r"[a-z0-9-]+", fix["slug"]):
            raise SystemExit(f'bad slug: {fix["slug"]!r}')

    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")
    for name, body in (
        ("fixes", chips_block(fixes)),
        ("panel", panel_block(fixes)),
        ("picks", picks_block(picks)),
        ("videos", videos_block(fixes)),
        ("footer-fixes", footer_fixes_block(fixes)),
    ):
        html = replace_block(html, name, body)
    index.write_text(html, encoding="utf-8")

    header, footer = shared_chrome(html, "header"), shared_chrome(html, "footer")
    shutil.rmtree(ROOT / "fix", ignore_errors=True)
    for fix in fixes:
        page = ROOT / "fix" / fix["slug"] / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text(fix_page(fix, header, footer), encoding="utf-8")

    urls = [f"{SITE}/"] + [f'{SITE}/fix/{fix["slug"]}/' for fix in fixes]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    main()
