# hand-play

Webcam hand tracking in the browser (MediaPipe Hand Landmarker), with a kids'
game and an experimental "control the computer with your hand" mode.

| Page | What it does |
|---|---|
| `game.html` | **Bubble Race** for two players: each player stands on one half of the screen and pops bubbles with any fingertip. ⭐ bubbles are worth 3. 60-second rounds. |
| `hand-side.html` | Shows left/right hand, palm/back, raised fingers and 12 gestures (✊ 🖐 ☝️ ✌️ 👍 👌 …). Can also drive the real mouse: right-hand ☝️ moves the cursor. |

## Run

```bash
python3 -m http.server 8000
```

Open http://localhost:8000/game.html or http://localhost:8000/hand-side.html in
**Chrome**. The camera needs `localhost` or `https`.

### Mouse control (optional, `hand-side.html` only)

A web page cannot move the real mouse, so a small local bridge does it:

```bash
python3 -m venv bridge/.venv && bridge/.venv/bin/pip install -r bridge/requirements.txt
bridge/.venv/bin/python bridge/server.py          # --dry-run prints instead of moving
```

- macOS: allow your terminal in System Settings → Privacy & Security → Accessibility.
- The bridge listens on 127.0.0.1 only, accepts pages from `localhost:8000` only,
  and lets one tab control the mouse at a time.
- Modes: **เมาส์ตรงนิ้ว** (absolute — press Calibrate once) or **trackpad** (relative).
- Keep the page visible; browsers pause camera work in hidden windows.

## Recorded voice (`voice.html` + `count.html`)

The counting game speaks with clips a family member records on `voice.html`.
Clips live in the browser (IndexedDB). To let someone else record from their own
phone, either send a voice-pack file (📦 export / 📥 import) or use the optional
Google Apps Script inbox below.

### Optional: voice inbox on Google Drive

1. Open https://script.google.com → **New project**, paste `apps-script/Code.gs`.
2. Change `KEY` to your own secret word, then **Deploy → New deployment → Web app**,
   *Execute as: Me*, *Who has access: Anyone* → **Deploy** → authorize.
3. Copy the **Web app URL**. On `voice.html` open **⚙️ ตั้งค่า server**, paste the URL
   and the key, **บันทึก**, then **🔗 คัดลอกลิงก์ให้คนอัด** and send that link.
4. Every clip the helper records is saved to the Drive folder `hand-play-voice`.
   `count.html` pulls the newest set each time it opens; ☁️ on `voice.html` pulls on demand.

Anyone holding the link can upload, so share it only with people you trust.
The server accepts only the 18 phrase ids, audio types and a size limit, and the
newest recording of a phrase replaces the old one.

## Notes

- Hand tracking model and WASM load from the MediaPipe CDN on first use.
- tasks-vision's handedness label already names the person's real hand for
  un-mirrored webcam frames — do not swap it.
- Finger up/down uses 3-D joint-bend angles with hysteresis; 2-D distance ratios flickered.
