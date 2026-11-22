"""Add ONE Demand Gen video ad (in-stream, in-feed, Shorts) to an existing ad group, then read it back.
Dry run by default.

  python3 google_video_ad.py --campaign "youtube|prospecting|core|us|en" --ad-group all_youtube \
      --video-id AAAAAAAAAAA --video-id BBBBBBBBBBB --headline "Budgets that move themselves" \
      --long-headline "..." --description "..." --business-name Acme --final-url https://acme.com \
      [--logo-file logo.png] [--customer-id 1234567890] [--live]

The videos must already be on YouTube (youtube_upload.py) and finished processing. Dry run = Google
validates the whole ad without saving it. --live only after the person's yes for THIS ad; the campaign's
own status (keep it PAUSED until launch) decides whether it serves. Success = the read-back.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _google as G  # noqa: E402
import _youtube as Y  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--customer-id"); ap.add_argument("--campaign", required=True); ap.add_argument("--ad-group", required=True)
ap.add_argument("--video-id", action="append", default=[]); ap.add_argument("--headline", action="append", default=[])
ap.add_argument("--long-headline", action="append", default=[]); ap.add_argument("--description", action="append", default=[])
ap.add_argument("--business-name", default=""); ap.add_argument("--final-url", default=""); ap.add_argument("--logo-file")
ap.add_argument("--live", action="store_true")
a = ap.parse_args()
problems = Y.video_ad_problems(a.video_id, a.headline, a.long_headline, a.description, a.business_name, a.final_url)
if a.logo_file and not Path(a.logo_file).is_file():
    problems.append(f"Not found: {a.logo_file}")
if problems:
    sys.exit("\n".join(problems))

g = G.client()
cid = G.customer_id(a.customer_id)
rows = G.query(g, cid, f"SELECT ad_group.resource_name FROM ad_group WHERE campaign.name = '{G.esc(a.campaign)}' "
                      f"AND ad_group.name = '{G.esc(a.ad_group)}' AND ad_group.status != 'REMOVED'")
if not rows:
    sys.exit(f"No ad group '{a.ad_group}' in campaign '{a.campaign}'.")
ag = rows[0].ad_group.resource_name

ops, n = [], iter(range(-1, -100, -1))


def create(kind):
    m = g.get_type("MutateOperation"); ops.append(m)
    return getattr(m, f"{kind}_operation").create


videos = []
for vid in a.video_id:
    rn = f"customers/{cid}/assets/{next(n)}"
    x = create("asset"); x.resource_name = rn; x.name = f"Video {vid}"; x.youtube_video_asset.youtube_video_id = vid
    videos.append(rn)
logo = None
if a.logo_file:
    logo = f"customers/{cid}/assets/{next(n)}"
    x = create("asset"); x.resource_name = logo; x.name = f"Logo {Path(a.logo_file).name}"
    x.type_ = g.enums.AssetTypeEnum.IMAGE; x.image_asset.data = Path(a.logo_file).read_bytes()
aga = create("ad_group_ad"); aga.ad_group = ag; aga.status = g.enums.AdGroupAdStatusEnum.ENABLED
ad = aga.ad; ad.name = f"{a.campaign} {a.ad_group} video"; ad.final_urls.append(a.final_url)
v = ad.demand_gen_video_responsive_ad
for rn in videos:
    x = g.get_type("AdVideoAsset"); x.asset = rn; v.videos.append(x)
for field, items in (("headlines", a.headline), ("long_headlines", a.long_headline), ("descriptions", a.description)):
    for t in items:
        x = g.get_type("AdTextAsset"); x.text = t; getattr(v, field).append(x)
if logo:
    x = g.get_type("AdImageAsset"); x.asset = logo; v.logo_images.append(x)
bn = g.get_type("AdTextAsset"); bn.text = a.business_name; v.business_name = bn

req = g.get_type("MutateGoogleAdsRequest"); req.customer_id = cid
req.mutate_operations.extend(ops); req.validate_only = not a.live
try:
    g.get_service("GoogleAdsService").mutate(request=req)
except Exception as e:  # noqa: BLE001
    errs = getattr(getattr(e, "failure", None), "errors", None)
    msgs = [f"{x.message} ({x.error_code})" for x in errs] if errs else [str(e)[:300]]
    if any("YOUTUBE_VIDEO_DURATION_NOT_DEFINED" in m for m in msgs):
        msgs = ["YouTube is still processing the videos. Try again in a few minutes."]
    sys.exit("Google refused it:\n" + "\n".join(dict.fromkeys(msgs)))
if not a.live:
    print(f"Dry run passed: {len(ops)} operations. Nothing saved. Add --live after the person says yes.")
    sys.exit(0)
back = G.query(g, cid, f"SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad WHERE ad_group.resource_name = '{ag}' "
                      "AND ad_group_ad.ad.type = 'DEMAND_GEN_VIDEO_RESPONSIVE_AD' AND ad_group_ad.status != 'REMOVED'")
print(f"Read back: {len(back)} video ad(s) in {a.campaign} / {a.ad_group}.")
