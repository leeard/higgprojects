```
 _   _ ___ ____ ____   ____  ____   ___      _ _____ ____ _____ ____
| | | |_ _/ ___|/ ___| |  _ \|  _ \ / _ \    | | ____/ ___|_   _/ ___|
| |_| || | |  _| |  _  | |_) | |_) | | | |_  | |  _|| |     | | \___ \
|  _  || | |_| | |_| | |  __/|  _ <| |_| | |_| | |__| |___  | |  ___) |
|_| |_|___\____|\____| |_|   |_| \_\\___/ \___/|_____\____| |_| |____/
```

> **Something broken? If I can fix it, you can too. Let's get it done!**

---

## About

Hey, I'm Lee! I fix tractors, riding mowers, 3D printers, and whatever else breaks. Sometimes it works, sometimes it doesn't - but we always learn something along the way.

My boys help out too — Luke makes his own videos, and James, Evan, and Jenna star in videos at times. It's a family affair!

---

## Links

- [YouTube Channel](https://www.youtube.com/@higgprojects)
- [Facebook](https://www.facebook.com/higgprojects)
- [Amazon Storefront](https://www.amazon.com/shop/higgprojects)
- [Live Site](https://higgprojects.com)

---

## Tech Stack

Static site, no framework and no build at runtime:

- **index.html**: the home page, with generated blocks between `<!-- name:start -->` markers
- **styles.css**: hand-written CSS, dark theme only
- **site.js**: click-to-play video, fix panel, live data, sticker form, share button
- **data/fixes.json**: the fix registry. Chips, panel, fix pages, footer list and sitemap all come from it
- **data/picks.json**: the "Stuff I actually use" shelves
- **scripts/build_site.py**: Python stdlib only. Writes `fix/<slug>/index.html`, `sitemap.xml`, `robots.txt` and the generated blocks in `index.html`. Header and footer on fix pages are copied from `index.html`
- **images/**: Lee and the Yukon, logo, favicon, OG card, shop sunset, sasquatch sighting

### Page order

Header, hero with chips and photo (`#fixes`), fix panel, Hey I'm Lee with comments (`#lee`), Stuff I actually use (`#picks`), Latest from the shop (`#videos`), On the bench (`#bench`), the crew (`#team`), free sticker (`#sticker`), collabs, footer. Subscribe appears exactly three times on the home page: nav, Lee section, footer.

### Add a fix or a pick

1. Add an entry to `data/fixes.json` or a row to a shelf in `data/picks.json`.
2. Run `python3 scripts/build_site.py`.
3. Commit the data and everything it generated. Rerunning with no data change produces no diff.

Don't edit between the markers in `index.html` or anything under `fix/` by hand.

### Disclosure and prices

Never put a price on the site, in the data or on the page. That is an Amazon Associates rule. Percent-off creator codes are fine, and dollar-off amounts stay off the page. Every Amazon link uses `rel="sponsored noopener"`, and "As an Amazon Associate I earn from qualifying purchases." sits under every kit list, under the shelves and in the footer. No Amazon product images.

Photos run at full brightness: no filter, opacity, scrim or overlay. Text goes beside or below.

### Data

`youtube.json` is refreshed daily by `.github/workflows/fetch-youtube.yml`:

- Video count (the only channel stat the page shows)
- Latest long-form videos, with `publishedAt`, `duration` and `skipLatest`
- Latest Shorts
- Gear from `scripts/parse_gear.py`: `[{id, title, items: [{name, link}], code?, deal?}]`, newest first, max 12 videos. `name` is the text before the colon on each product-link line. Empty or generic labels (Amazon, Amazon link, Link, Buy) use the video title. Storefront lines are skipped. Tests: `python3 scripts/test_parse_gear.py`

The page reads that file at load. The markup holds a working fallback if the fetch fails.

### Hero slot rules

The panel under the hero shows the newest video whose `skipLatest` is false. If every fetched video is flagged, it shows the newest one.

`skipLatest` is true when the description has **`#nofeature`**, or when the video has an affiliate product link (`a.co`, `amzn.to`, `geni.us`, `amazon.com`, storefront lines don't count), runs under 480 seconds, and has no **`#feature`**. So long repair videos with links take the hero, and short product reviews stay out.

Shorts stay out of the hero unless the description has `#feature`. A featured Short never takes a slot in the long-form grid.

The service records in `#bench` are hand-curated. New videos don't appear there on their own. Add an `<li>` to the ledger in `index.html`, then rerun `build_site.py`.

### Development

Asset paths are absolute, so serve the folder rather than opening the file:

```bash
python3 -m http.server
```

Manual YouTube refresh (needs repo secret `YOUTUBE_API_KEY`):

```bash
gh workflow run fetch-youtube.yml
```

---

<p align="center">
  <b>WARNING: I may be an idiot. Follow my advice at your own risk.</b>
</p>
