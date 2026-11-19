---
name: change-safety
description: Apply paid search changes safely on Google Ads and Microsoft Ads - classify each change as routine, material or destructive against the client's step limit, collect the approvals it needs (and a revert plan), dry run, apply one change at a time only on an explicit yes, confirm by API read-back, log it with a category and reason, and read before vs after later. Also reviews the change history for changes made outside the process. Use whenever a change is about to be made to an ad account, or someone asks what changed.
license: MIT
compatibility: Any Agent Skills client. Applying changes yourself needs google-ads / bingads and your own access; classification needs Python 3.10+.
metadata:
  role: paid-search-manager
  stage: run
  summary: Every change classified, approved, dry run, applied on a yes, read back and logged.
  needs: The proposed change with its reason and evidence; the client's step limit; who can approve for the client
---

# Change safety

Two goals: don't break accounts, and learn which kinds of changes work. Every change, however small, is
approved by a person before it's applied. Nothing is applied automatically.

## Needs
The change (what, where, from -> to), its reason and evidence, the client's step limit (biggest bid,
target or budget move allowed without them), and who approves for the client.

## If something is missing
No step limit agreed? Treat every bid, target or budget move as material and ask the client to set one.
No reason? Ask for one line; it goes in the log.

## Method
1. **Classify**:
   - **Routine**: negatives, keywords, ads, bid/budget/target moves within the step limit. Needs the operator's yes.
   - **Material**: moves over the step limit, new campaigns, pausing or enabling campaigns. Needs the client's approval too (who and when).
   - **Destructive**: deletes, structure changes, conversion action changes. Needs client approval and a written revert plan.
   A move that can't be sized against a limit is material.
2. **Dry run** where the platform allows (Google validate-only; Microsoft: find the target and stop).
3. **Ask for an explicit yes for this specific change.** Then apply via the API, one variable at a time where possible.
4. **Read back** from the API. Never trust the "success" response. Not confirmed = stop and report.
5. **Log** it: date, platform, entity, from -> to, category (bids, budget, keywords, negatives, ads/assets, audiences, structure, tracking/conversions, settings), safety level, approver, one-line why.
6. **Outside changes**: pull the platform change history; anything not made through this process is flagged "made outside" (client, another tool, the platform). Ask why; note it. A flag is not an error.
7. **Impact lookback**: compare the changed entity after vs an equal window before. Window = the longest of the learning period (up to 7 days), the conversion lag, and time to a minimum number of conversions. Observed, not proof of cause; "can't tell" is an answer, never read as "no change". Roll up by category over time.
8. If the intended path isn't available in the API: stop and report. Don't improvise.

## Output
For each change: level, what it needs, what's missing, the dry-run result, then after the yes the
read-back and the log line. For history reviews: a table of outside changes needing a why.

## Getting the data
1. **Redavio connector**: add `https://app.redavio.com/mcp`, sign in, connect Google and/or Microsoft. `paid_search_proposals` lists changes waiting with their safety level; approving happens in Redavio, which applies, reads back and logs.
2. **Your own API access** (direct API use needs both a Google Ads developer token and a Microsoft Advertising developer token, plus your own OAuth app credentials for each; otherwise use mode 1, which needs no tokens):
   ```
   python3 scripts/run.py perfos safety --kind budget --move-pct 0.25 --step-limit 15%
   python3 scripts/run.py ads google_apply budget --campaign "search|nonbrand|crm|us|en" --daily 115          # dry run
   python3 scripts/run.py ads google_apply budget --campaign "search|nonbrand|crm|us|en" --daily 115 --live   # after a yes
   python3 scripts/run.py ads google_report change_history --days 28
   ```
   `google_apply` / `microsoft_apply` support negative, keyword, pause, budget, target (Google), campaign-status.
3. **Your own data**: a change log sheet with the fields above; Google Ads change history export.
