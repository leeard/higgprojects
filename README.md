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
- **styles.css** — hand-written CSS ("Varsity Shop" design system)
- **fonts/varsity-team.woff2** — Varsity Team Bold, the badge logo's letterforms, used as the display face
- **Google Fonts** — Bitter (body), Archivo (utility), IBM Plex Mono (ledger/spec plate)
- **Vanilla JS** — live channel stats from `youtube.json`, sticker form AJAX

### Data

`youtube.json` is refreshed daily by the GitHub Action in `.github/workflows/fetch-youtube.yml` (channel stats + latest shorts). The page reads `stats` at load and falls back to the numbers baked into the markup.

### Development

No build. Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server
```

---

<p align="center">
  <b>WARNING: I may be an idiot. Follow my advice at your own risk.</b>
</p>
