#!/usr/bin/env python3
"""Extract gear from YouTube video details for the page's "What I used" lists.

Reads JSON on stdin, either {"items": [{id, title, description}, ...]} or a bare
array of those objects.

Writes a JSON array on stdout, newest first, max 12 videos:
  [{id, title, items: [{name, link}, ...], code?, deal?}, ...]
"""
from __future__ import annotations

import json
import re
import sys

MAX_VIDEOS = 12
LINK_RE = re.compile(
    r"https?://(?:a\.co|amzn\.to|geni\.us|www\.amazon\.com)/[^\s)\"<>]+",
    re.I,
)
GENERIC_LABELS = {"", "amazon", "amazon link", "link", "buy"}
STOREFRONT_RE = re.compile(r"storefront|/shop/", re.I)
# "code HIGGPROJECTS", "code: HIGGPROJECTS", "with code HIGGPROJECTS"
CODE_RE = re.compile(
    r"(?i)\b(?:discount\s*code|promo\s*code|coupon(?:\s*code)?|"
    r"(?:with\s+)?code)\s*[:=\-–]?\s*"
    r"([A-Za-z0-9][A-Za-z0-9&%_.-]{2,32})"
)
# "10% off", "Get 10% off", "$5 off"
DEAL_RE = re.compile(r"(?i)(\$\d+\s*off|\d+\s*%\s*off)")


def clean_url(u: str) -> str:
    return re.sub(r"[\.,;]+$", "", u)


def normalize_deal(text: str) -> str:
    d = re.sub(r"\s+", " ", text.strip())
    d = re.sub(r"(?i)(\$\d+)\s*off", r"\1 OFF", d)
    d = re.sub(r"(?i)(\d+)\s*%\s*off", r"\1% OFF", d)
    return d


def extract_code(desc: str) -> str | None:
    m = CODE_RE.search(desc or "")
    if not m:
        return None
    code = m.group(1).rstrip(".,;")
    if code.lower() in {"code", "for", "off", "the", "this", "using", "link", "with"}:
        return None
    return code


def extract_deal(desc: str) -> str | None:
    m = DEAL_RE.search(desc or "")
    return normalize_deal(m.group(1)) if m else None


def extract_items(desc: str, title: str) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    for line in (desc or "").splitlines():
        m = LINK_RE.search(line)
        if not m or STOREFRONT_RE.search(line):
            continue
        link = clean_url(m.group(0))
        if link in seen:
            continue
        seen.add(link)
        label = line[: m.start()].strip().rstrip(":").strip()
        name = title if label.lower() in GENERIC_LABELS else label
        items.append({"name": name, "link": link})
    return items


def parse_items(videos: list) -> list[dict]:
    gear: list[dict] = []
    for video in videos:
        if not video or not video.get("id"):
            continue
        desc = video.get("description") or ""
        title = (video.get("title") or "").strip()
        items = extract_items(desc, title)
        if not items:
            continue
        entry = {"id": video["id"], "title": title, "items": items}
        code = extract_code(desc)
        deal = extract_deal(desc)
        if code:
            entry["code"] = code
        if deal:
            entry["deal"] = deal
        gear.append(entry)
        if len(gear) >= MAX_VIDEOS:
            break
    return gear


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        print("[]")
        return
    payload = json.loads(raw)
    if isinstance(payload, dict):
        videos = payload.get("items") or payload.get("videos") or []
    else:
        videos = payload
    print(json.dumps(parse_items(videos), ensure_ascii=False))


if __name__ == "__main__":
    main()
