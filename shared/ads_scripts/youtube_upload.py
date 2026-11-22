"""Upload your video ads to YOUR YouTube channel as unlisted videos, then read them back. Dry run by default.

  python3 youtube_upload.py --client-secret client_secret.json --title "Acme ad" \
      --horizontal acme-16x9.mp4 --vertical acme-9x16.mp4 --square acme-1x1.mp4 [--description "..."] \
      [--out video.json] [--live]

Dry run = sign in, show which channel and what would be uploaded; nothing is uploaded. --live uploads,
only after the person says yes. Then wait until YouTube shows "processing: succeeded" (a few minutes)
before google_video_ad.py: Google Ads refuses a video that is still processing.
--out writes video.json for the dashboard (dashboard/scripts/from_portal.mjs). Setup: top of _youtube.py.
No Google Cloud project? The Redavio connector (https://app.redavio.com/mcp) does this with
paid_display_youtube and paid_display_youtube_upload.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _youtube as Y  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--client-secret"); ap.add_argument("--title", required=True); ap.add_argument("--description", default="")
ap.add_argument("--horizontal"); ap.add_argument("--vertical"); ap.add_argument("--square")
ap.add_argument("--out"); ap.add_argument("--live", action="store_true")
a = ap.parse_args()
files = {f: getattr(a, k) for f, k in (("video_horizontal", "horizontal"), ("video_vertical", "vertical"), ("video_square", "square"))
         if getattr(a, k)}
if not files:
    sys.exit("Give at least one of --horizontal (16:9), --vertical (9:16), --square (1:1).")
missing = [p for p in files.values() if not Path(p).is_file()]
if missing:
    sys.exit(f"Not found: {', '.join(missing)}")

yt = Y.service(a.client_secret)
ch = Y.channel(yt)
print(f"Channel: {ch['title']} ({ch['id']})")
if not a.live:
    for f, p in files.items():
        print(f"Would upload {p} as unlisted: {Y.video_body(a.title, f, a.description)['snippet']['title']}")
    print("Dry run: nothing uploaded. Add --live after the person says yes.")
    sys.exit(0)

from googleapiclient.http import MediaFileUpload  # noqa: E402

ids = {}
for f, p in files.items():
    req = yt.videos().insert(part="snippet,status", body=Y.video_body(a.title, f, a.description),
                             media_body=MediaFileUpload(p, mimetype="video/mp4", resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    ids[f] = resp["id"]
    print(f"Uploaded {p}: https://youtu.be/{resp['id']}")
print(Y.dump(Y.read_back(yt, list(ids.values()))))
if a.out:
    Path(a.out).write_text(json.dumps(Y.results(ch["id"], ids), indent=1) + "\n")
    print(f"Wrote {a.out}")
