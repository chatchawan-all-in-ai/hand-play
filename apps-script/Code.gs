/**
 * Hand Play — voice inbox on Google Drive (Google Apps Script web app).
 *
 * voice.html POSTs each recording here; count.html / voice.html GET the whole set back.
 * Files live in a Drive folder named "hand-play-voice" in the account that deploys this.
 *
 * Setup: script.google.com → New project → paste this file → change KEY below →
 * Deploy → New deployment → type "Web app" → Execute as: Me, Who has access: Anyone →
 * Deploy → authorize → copy the Web app URL into voice.html (⚙️ ตั้งค่า server).
 */

// Change this to your own secret word. The recording link carries it; requests without it are refused.
const KEY = 'CHANGE-ME';

const FOLDER = 'hand-play-voice';
const MAX_B64 = 2000000;   // ~1.5 MB per clip, far more than a 4-second recording needs
const KNOWN = ['ask_1', 'ask_2', 'cheer_1', 'cheer_2', 'cheer_3',
  'num_1', 'num_2', 'num_3', 'num_4', 'num_5', 'num_6', 'num_7', 'num_8', 'num_9', 'num_10',
  'help_1', 'help_2', 'finish'];

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function folder_() {
  const it = DriveApp.getFoldersByName(FOLDER);
  return it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER);
}

// Save one clip. Body is sent as text/plain JSON (a "simple" request, so the browser skips CORS preflight).
function doPost(e) {
  let b;
  try { b = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: 'bad json' }); }
  if (b.k !== KEY) return json_({ ok: false, error: 'wrong key' });
  if (KNOWN.indexOf(b.id) < 0) return json_({ ok: false, error: 'unknown phrase' });
  if (!/^audio\//.test(b.type || '') || typeof b.data !== 'string' || b.data.length > MAX_B64) {
    return json_({ ok: false, error: 'bad audio' });
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const f = folder_(), name = b.id + '.webm';
    const old = f.getFilesByName(name);
    while (old.hasNext()) old.next().setTrashed(true);          // newest recording wins
    const blob = Utilities.newBlob(Utilities.base64Decode(b.data), b.type, name);
    f.createFile(blob).setDescription(b.type);
  } finally {
    lock.releaseLock();
  }
  return json_({ ok: true, id: b.id });
}

// Return every clip as one voice pack: { app, v, clips: [{ id, type, data }] }.
function doGet(e) {
  if ((e.parameter.k || '') !== KEY) return json_({ ok: false, error: 'wrong key' });
  const files = folder_().getFiles(), clips = [];
  while (files.hasNext()) {
    const file = files.next(), id = file.getName().replace(/\.webm$/, '');
    if (KNOWN.indexOf(id) < 0) continue;
    clips.push({ id: id, type: file.getDescription() || 'audio/webm', data: Utilities.base64Encode(file.getBlob().getBytes()) });
  }
  return json_({ ok: true, app: 'hand-play-voice', v: 1, clips: clips });
}
