"""Hand Control bridge: receives gesture commands from control.html over a
local WebSocket and drives the real mouse with pynput.

Run:  bridge/.venv/bin/python bridge/server.py           (controls the mouse)
      bridge/.venv/bin/python bridge/server.py --dry-run (prints only)

Security: listens on 127.0.0.1 only and accepts connections only from the
origins in ALLOWED_ORIGINS, so no other website can move your mouse.
"""
import argparse
import asyncio
import json
import sys

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

HOST, PORT = "127.0.0.1", 8765
ALLOWED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]


def screen_size():
    if sys.platform == "darwin":
        import Quartz  # ships with pynput's pyobjc dependency on macOS
        b = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
        return int(b.size.width), int(b.size.height)
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    size = root.winfo_screenwidth(), root.winfo_screenheight()
    root.destroy()
    return size


class Mouse:
    def __init__(self, dry_run):
        self.dry = dry_run
        self.w, self.h = screen_size()
        if not dry_run:
            from pynput.mouse import Button, Controller
            self.ctl, self.Button = Controller(), Button
        self.down_button = None

    def _btn(self, name):
        return self.Button.right if name == "right" else self.Button.left

    def move(self, x, y):
        px = round(min(max(x, 0.0), 1.0) * (self.w - 1))
        py = round(min(max(y, 0.0), 1.0) * (self.h - 1))
        if not self.dry:
            self.ctl.position = (px, py)

    def move_by(self, dx, dy):
        # relative move in screen points (trackpad style); clamp each step so a bad
        # message can never fling the cursor across the screen
        dx = max(-200, min(200, round(dx)))
        dy = max(-200, min(200, round(dy)))
        if self.dry:
            print("rel", dx, dy)
        elif dx or dy:
            self.ctl.move(dx, dy)

    def down(self, b):
        self.down_button = b
        if self.dry:
            print("down", b)
        else:
            self.ctl.press(self._btn(b))

    def up(self):
        if self.down_button is None:
            return
        b, self.down_button = self.down_button, None
        if self.dry:
            print("up", b)
        else:
            self.ctl.release(self._btn(b))

    def click(self, b):
        if self.dry:
            print("click", b)
        else:
            self.ctl.click(self._btn(b))

    def scroll(self, dy):
        if self.dry:
            print("scroll", dy)
        else:
            self.ctl.scroll(0, dy)


REPLACED = 4000          # close code telling an older page that a newer one took over
current = None           # only one page may drive the mouse; two pages fighting = cursor jumps


async def handler(ws, mouse):
    global current
    if current is not None:
        mouse.up()
        await current.close(REPLACED, "another page took over")
        print("older page disconnected (replaced)")
    current = ws
    print("connected:", ws.request.headers.get("Origin"))
    try:
        async for raw in ws:
            try:
                m = json.loads(raw)
                t = m.get("t")
                if t == "move":
                    mouse.move(float(m["x"]), float(m["y"]))
                elif t == "rel":
                    mouse.move_by(float(m["dx"]), float(m["dy"]))
                elif t == "down":
                    mouse.down(m.get("b", "left"))
                elif t == "up":
                    mouse.up()
                elif t == "click":
                    mouse.click(m.get("b", "left"))
                elif t == "scroll":
                    mouse.scroll(int(m["dy"]))
                elif t == "hello":
                    await ws.send(json.dumps({"t": "hello", "screen": [mouse.w, mouse.h]}))
            except (ValueError, KeyError, TypeError) as e:
                print("bad message:", raw, e)
    except ConnectionClosed:
        pass                 # page closed or was replaced; nothing to report
    finally:
        if current is ws:
            current = None
            mouse.up()  # never leave a button held down when the page goes away
        print("disconnected")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print commands, do not move the mouse")
    args = ap.parse_args()
    mouse = Mouse(args.dry_run)
    async with serve(lambda ws: handler(ws, mouse), HOST, PORT, origins=ALLOWED_ORIGINS):
        mode = "DRY RUN" if args.dry_run else "LIVE"
        print(f"[{mode}] ws://{HOST}:{PORT}  screen={mouse.w}x{mouse.h}  Ctrl+C to stop")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
