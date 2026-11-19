---
name: launch-check
description: Final go/no-go before switching on paused Google Ads or Microsoft Ads campaigns - tracking confirmed end to end, setup checklist verified on both platforms, client approval recorded, then campaigns enabled only on the person's yes, read back, logged, with read dates set and a first-week watch plan. Use when someone is ready to launch, go live, enable campaigns, or asks what to check before launching paid search.
license: MIT
compatibility: Any Agent Skills client. Enabling via your own API needs google-ads / bingads and your own access; checks need Python 3.10+.
metadata:
  role: paid-search-manager
  stage: set-up
  summary: Go/no-go checks, client approval, enable on a yes, read back, set read dates, watch week one.
  needs: The built (paused) campaigns; proof a test conversion landed on both platforms; client approval; the goals and budget
---

# Launch check

## Needs
The paused build, a test conversion seen on both platforms, the client's approval (launch is a material
change: new campaigns), the goals and monthly budget.

## If something is missing
No test conversion yet? Stop: launching without tracking wastes the learning period. No client approval?
Ask who approves and record it. Everything else can be a known risk with an owner.

## Method
1. **Tracking end to end**: a test lead reached the CRM with its click ID and the conversion shows in Google and Microsoft (read back from the API). Exactly one primary conversion, the same on every campaign type.
2. **Checklist verified on both platforms**: settings (Search only, presence, auto-apply off, assets at account level, verification started), structure and naming, all match types, fencing and shared lists, 15/4 RSAs with no errors or disapprovals, landing pages live with click IDs surviving, smart bidding with no target on new campaigns, portfolios per type, budgets per the plan (no campaign under the minimum daily), 24/7 no adjustments, PMax brand-excluded with URL exclusions, AI Max copies paused, Microsoft tracking built natively.
3. **Client approval** recorded: who and when.
4. **Enable** only after the person's explicit yes, one campaign at a time, then read back that each is ENABLED. AI Max copies stay paused (tested later as experiments); PMax launches day one as a test.
5. **Log** the launch in the change log (what, when, who approved).
6. **Read dates**: PMax test read date (whole weeks, sized to volume); the first target decision at ~30 conversions in 30 days.
7. **First week**: watch, don't react. Smart bidding is learning (up to 7 days). Daily: pacing, tracking, disapprovals, flagrant spend only.

## Output
A go/no-go table (check, Google, Microsoft, evidence), blockers first, then the enable plan, and after
the yes, the read-back and the read dates.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_status` (launch items left), `paid_search_audit` (checklist), `paid_search_snapshot` (settings), `paid_search_proposals` (queue the enable for approval).
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py ads google_snapshot --out snapshot.json
   python3 scripts/run.py ads google_apply campaign-status --campaign "search|brand|core|us|en" --status ENABLED          # dry run
   python3 scripts/run.py ads google_apply campaign-status --campaign "search|brand|core|us|en" --status ENABLED --live   # after a yes
   python3 scripts/run.py ads microsoft_apply campaign-status --campaign "..." --status Active --live                    # after a yes
   ```
3. **Your own data**: screenshots or exports of settings and conversions; enable in the UI yourself after the checks pass.
