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

## Notes

- Hand tracking model and WASM load from the MediaPipe CDN on first use.
- tasks-vision's handedness label already names the person's real hand for
  un-mirrored webcam frames — do not swap it.
- Finger up/down uses 3-D joint-bend angles with hysteresis; 2-D distance ratios flickered.
