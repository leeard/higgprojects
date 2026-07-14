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

Static site, no build step:

- **index.html** — the page
- **styles.css** — hand-written CSS ("Golden Hour" design system)
- **images/** — logo, shop-sunset hero, OG card, sasquatch sighting
- **Google Fonts** — Bricolage Grotesque (display), Karla (body), Lora (serif accents)
- **Vanilla JS** — live channel data from `youtube.json`, sticker form AJAX

### Data

`youtube.json` is refreshed daily by the GitHub Action in `.github/workflows/fetch-youtube.yml`:

- Channel stats (subs, video count, views)
- Latest long-form videos (from the channel uploads playlist, Shorts filtered out)
- Latest Shorts (from the dedicated Shorts playlist)
- Gear links **and coupon codes** from recent long-form descriptions (`scripts/parse_gear.py` — e.g. “10% off with code HIGGPROJECTS”)

The page reads that file at load and falls back to the numbers and cards baked into the markup if the fetch fails or returns a thin list.

### Development

No build. Open `index.html` in a browser, or serve the folder:

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
