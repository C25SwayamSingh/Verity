# Install & Share-to-App — The Giver

The Giver is an installable PWA with a single entry point: **Check any post**. You can open it from a home-screen icon and (on supported platforms) share content straight into it.

---

## What was added

- **Web manifest** (`public/manifest.webmanifest`) — installable app metadata + a Web **`share_target`** (GET).
- **App icons** (`public/icon.svg`, `public/icon-maskable.svg`) and PWA `<meta>` tags in `app/layout.tsx`.
- **Share-link handling** on `/`: reads `?title=`, `?text=`, `?url=` and pre-fills the box. If real shared text (≥40 chars) is present, it **auto-runs** the analysis.

The shared content lands in the same single input — no extra forms.

---

## Share URL format

Anything can deep-link into the checker:

```
https://YOUR_HOST/?text=<caption or selected text>&url=<link>&title=<title>
```

- `text` — caption / selected text (auto-runs analysis when ≥40 chars)
- `url` — source link (kept as context; not downloaded)
- `title` — optional heading

All values must be URL-encoded.

---

## Platform support for "Share → The Giver"

| Platform | How it works |
|----------|--------------|
| **Android (Chrome)** | Install the PWA → it appears in the system share sheet via `share_target`. Sharing a post opens `/` pre-filled. |
| **Desktop (Chrome/Edge)** | Install from the address bar; open from app icon. Paste into the single box. |
| **iOS (Safari)** | Safari does **not** support Web Share Target. Use the **Apple Shortcut** below to appear in the iOS share sheet, or "Add to Home Screen" and paste. |

> The Giver never downloads or scrapes Instagram/TikTok. A shared **link** is context only. To analyze a Reel’s spoken content, share/attach a **screen recording or its audio**, or paste a transcript.

---

## iOS: add "The Giver" to the share sheet (Apple Shortcut)

iOS Safari cannot register a web share target. You build a **Shortcut** once; it then appears in Instagram’s **Share** menu and opens The Giver in Safari with the Reel link already in the box.

Use your deployed `https://YOUR_HOST` in the steps below, or for LAN testing on this project: **`http://192.168.1.27:3000`** (see **Your local setup** — servers must be running).

---

## Your local setup (test on iPhone over Wi‑Fi)

Confirmed working host on this machine:

- Frontend: `http://192.168.1.27:3000`
- Backend: `http://192.168.1.27:8000`

Run servers bound to the LAN (phone + Mac on the same Wi‑Fi):

```bash
# backend
cd backend
CORS_ORIGINS="http://localhost:3000,http://192.168.1.27:3000" \
  .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

# frontend (points the browser at the LAN backend)
cd frontend
NEXT_PUBLIC_API_URL="http://192.168.1.27:8000" npm run dev -- --port 3000 --hostname 0.0.0.0
```

On the iPhone, open Safari → `http://192.168.1.27:3000` → Share → **Add to Home Screen**.

### iOS Shortcut — step-by-step (Instagram Reels)

**What success looks like**

1. Safari on your iPhone opens `http://192.168.1.27:3000` and shows **Check any post** with one large text box.
2. From Instagram: **Share → The Giver** → Safari opens again with the Reel URL **already inside** that box.
3. You tap **Analyze** (or **+ Attach audio / video** if you have a screen recording). A shared link alone does **not** auto-analyze — that is intentional.

If step 1 fails, do **Part A** below before building the Shortcut.

---

#### Part A — Pre-flight on iPhone (do this first)

| Step | What to do | If it fails |
|------|------------|-------------|
| A1 | iPhone on the **same Wi‑Fi** as your Mac (not cellular-only for this test). | Join the home Wi‑Fi. |
| A2 | Open **Safari**, type exactly: `http://192.168.1.27:3000` | Page won’t load → Mac servers off, wrong IP, or firewall. Start both servers (commands above). |
| A3 | Paste a long sentence in the box → tap **Analyze** | Error or spinner forever → frontend not using `NEXT_PUBLIC_API_URL=http://192.168.1.27:8000`. Restart frontend. |

**Check your Mac IP** (it can change after reconnect):

```bash
ipconfig getifaddr en0
```

If the number is not `192.168.1.27`, replace that address everywhere in the Shortcut and in the server commands.

---

#### Part B — Build the Shortcut (3 actions)

**B1 — Create and name**

1. Open the **Shortcuts** app (purple icon).
2. Bottom tab **Shortcuts** (not **Automation**).
3. Top-right **+**.
4. Tap **New Shortcut** at the top → rename to **The Giver** (exact spelling helps you find it in Instagram’s share list).

**B2 — Show in Share Sheet**

1. Top-right tap **ⓘ** (circle with “i”) — on some iOS versions this is a **slider** icon instead.
2. Turn **ON**: **Show in Share Sheet**.
3. **Share Sheet Types** (or **Accepted Types**):
   - **ON**: **URLs**
   - **ON**: **Safari web pages** (if listed — helps Instagram links)
   - **OFF**: Images, Files, Music, etc. (less clutter)
4. Tap **Done** to return to the action editor.

**B3 — Action 1: Text**

1. Tap **Add Action** or the search field (“Search Actions”).
2. Search **Text** → add the **Text** action.
3. Tap inside the Text field → pick the blue variable **Shortcut Input**.  
   - Meaning: “whatever Instagram shared” (usually the Reel URL string).

**B4 — Action 2: URL Encode**

1. Below Text, tap **+** / **Add Action**.
2. Search **URL Encode** → add it.
3. On URL Encode, tap where it says **Text** or **Input** → choose **Text** from the previous step (the pill labeled **Text**, not Shortcut Input again).  
   - Instagram URLs contain `?` and `/`; encoding avoids breaking the query string.

**B5 — Action 3: Open URLs** (this is where most setups break)

1. Add action **Open URLs** (may appear as **Open URL**).
2. In the URL field:
   - Type this prefix exactly (use **http**, not https, for local dev):
     ```
     http://192.168.1.27:3000/?url=
     ```
   - Put the cursor **immediately after** the final `=` (nothing after it yet).
   - Tap the variable bar above the keyboard → select **URL Encoded Text** (from step B4).
3. The finished URL should look like one line, for example:
   ```
   http://192.168.1.27:3000/?url=https%3A%2F%2Fwww.instagram.com%2Freel%2F...
   ```
4. **Common mistakes**
   - Typing `[URL Encoded Text]` literally instead of inserting the variable pill.
   - Using `?text=` for a Reel share — Instagram usually shares a **URL**; use `?url=` as above.
   - Skipping the **Text** action and encoding **Shortcut Input** directly — works sometimes, but Text → Encode is more reliable.

**B6 — Save**

1. Tap **Done** (top right).
2. Your shortcut should show three blocks in order: **Text** → **URL Encode** → **Open URLs**.

**B7 — Test without Instagram**

1. In Shortcuts, tap **The Giver** to run it.
2. If asked for input, paste:
   ```
   https://www.instagram.com/reel/DXAOA0Wkj4I/
   ```
3. Safari should open The Giver with that link in the box. If this works, Instagram will work.

---

#### Part C — Share from Instagram

1. Open the **Reel** in Instagram.
2. Tap **Share** (paper plane).
3. Swipe the app row; if you don’t see **The Giver**, tap **More** (⋯).
4. Under **Shortcuts**, tap **The Giver** once.
5. Safari opens with the link pre-filled → tap **Analyze** when ready.

**If The Giver isn’t in the list**

- Share sheet → scroll → **Edit Actions** / **More** → enable **The Giver**.
- **Settings → Shortcuts** → allow Shortcuts to run.
- Re-open the shortcut → **ⓘ** → confirm **Show in Share Sheet** is ON.

---

#### Optional: auto-analyze when sharing long text

If you share a **caption or selected text** (not only a URL), change the Open URLs prefix to:

```
http://192.168.1.27:3000/?text=
```

plus the same **URL Encoded Text** variable. Text ≥40 characters can auto-run analysis on the homepage.

---

#### Troubleshooting

| Symptom | Likely cause | What to do |
|---------|----------------|------------|
| Safari can’t open `192.168.1.27:3000` | Dev server stopped or not on `0.0.0.0` | Run backend + frontend commands above; keep Terminal windows open. |
| Page loads, **Analyze** fails | API still `localhost` | Restart frontend with `NEXT_PUBLIC_API_URL=http://192.168.1.27:8000`. |
| Shortcut runs, blank or wrong page | Typo in URL, or literal `[URL Encoded Text]` | Re-do B5; only the variable pill after `?url=`. |
| Shortcut not in Instagram | Share sheet disabled | ⓘ → **Show in Share Sheet** ON; **URLs** ON. |
| Worked before, not now | Mac asleep / new IP | Wake Mac, rerun servers, `ipconfig getifaddr en0`, update Shortcut. |

**What Instagram share does not do:** download the Reel, transcribe from the link alone, or appear in the share row until this Shortcut exists. For spoken content: screen-record the Reel → **+ Attach audio / video** in The Giver.

> LAN testing only works while Mac servers run on the same Wi‑Fi. For use anywhere, deploy with HTTPS and put your real host in the Shortcut instead of `192.168.1.27`.

## Limitations

- iOS share-sheet entry requires the Shortcut (no native share extension yet).
- A bare link cannot be transcribed (no scraping/download) — share audio/video or text.
- Icons are SVG; swap in PNG `apple-touch-icon` for the crispest iOS home-screen icon.
- No offline service worker yet (not required for share-target GET).
