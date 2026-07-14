#!/usr/bin/env python3
"""Extract gear items (product links + coupon codes) from YouTube video details.

Reads JSON on stdin — either:
  { "items": [ {id, title, description}, ... ] }
or a bare array of those objects.

Writes JSON array on stdout:
  [{ id, title, link, code?, deal? }, ...]  (newest first, max 6)
"""
from __future__ import annotations

import json
import re
import sys

LINK_RE = re.compile(
    r"https?://(?:a\.co|amzn\.to|geni\.us|www\.amazon\.com)/(?!shop/)[^\s)\"<>]+",
    re.I,
)
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


def parse_items(items: list) -> list[dict]:
    gear: list[dict] = []
    for item in items:
        if not item:
            continue
        desc = item.get("description") or ""
        m = LINK_RE.search(desc)
        if not m:
            continue
        link = clean_url(m.group(0))
        # Skip channel storefront if it ever matches
        if re.search(r"amazon\.com/shop/", link, re.I):
            continue
        entry = {
            "id": item.get("id") or "",
            "title": (item.get("title") or "").strip(),
            "link": link,
        }
        code = extract_code(desc)
        deal = extract_deal(desc)
        if code:
            entry["code"] = code
        if deal:
            entry["deal"] = deal
        if entry["id"]:
            gear.append(entry)
        if len(gear) >= 6:
            break
    return gear


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        print("[]")
        return
    payload = json.loads(raw)
    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("videos") or []
    else:
        items = payload
    print(json.dumps(parse_items(items), ensure_ascii=False))


if __name__ == "__main__":
    main()
