# Redavio skills

Every Redavio Library skill in one repo, one folder per skill. Each folder follows the open
[Agent Skills](https://agentskills.io) standard: a `SKILL.md` with `name` and `description`, plus
optional `scripts/` and `references/`. They work in Claude (Claude.ai, Claude Code), and any client
that reads Agent Skills.

The first role is **paid search manager**: demand capture on Google Ads and Microsoft Ads (Search,
AI Max, Performance Max), from intake to audit. Every job skill works on its own; no earlier step
is required. Supports all four campaign objectives, one per campaign: conversions, CPA,
conversion value, ROAS.

The second role is **paid display manager** (Paid Display and Video Manager): demand creation on
Google Demand Gen (YouTube in-stream, in-feed and Shorts, Discover, Gmail, Display Network) and
Microsoft Audience ads with LinkedIn profile targeting, for awareness, prospecting and retargeting.
One scorecard for every display campaign: cost to reach, brand lift, pipeline.

## How to use it (the Library form factor)

1. **Through the Redavio MCP server** (easiest, no tokens). Add `https://app.redavio.com/mcp` as a
   connector in Claude or any MCP client, sign in, connect Google and/or Microsoft. The skills call
   tools like `paid_search_search_terms`, `paid_search_volume_gate` and `paid_search_diagnose`.
2. **From this repo, with your own API access.** Each skill bundles scripts for the Google Ads and
   Microsoft Advertising APIs. Direct API use needs **both a Google Ads developer token and a
   Microsoft Advertising developer token, plus your own OAuth app credentials for each**. Otherwise
   use the Redavio connector, which needs no tokens.
3. **From this repo, with your own data.** CSV exports, a Google Sheet, a warehouse: the math runs on
   plain files. The repo is MIT: fork it and build your own app (React or anything else) on top of
   `shared/perfos`.

Skills never write to an ad account without the person's explicit yes for that change. Builds
create everything PAUSED and confirm by reading the account back.

## Install

One skill at a time:

```
npx skills add redavio/skills --skill search-term-review
```

Claude.ai: download a skill's ZIP (or build them: `bash scripts/zip_skills.sh`, output in `dist/`)
and upload it in Settings > Capabilities > Skills. Each ZIP bundles the math and API scripts it needs.

Claude Code: copy a folder into `.claude/skills/` (keep the repo's `shared/` folder alongside, or
`pip install "git+https://github.com/redavio/skills#subdirectory=shared"`).

## Skills

### Role

| Skill | What it does |
|---|---|
| [`paid-search-manager`](skills/paid-search-manager/SKILL.md) | The role: what each skill does and which one to use, with the principles they share. |

### Status

| Skill | What it does |
|---|---|
| [`status`](skills/status/SKILL.md) | Every step as done / needs you / waiting on data / not set up, and the next skill to run. |

### Set up

| Skill | What it does |
|---|---|
| [`ad-copy`](skills/ad-copy/SKILL.md) | RSAs and assets written from the customer's own words, 15 headlines and 4 descriptions, limits checked. |
| [`build`](skills/build/SKILL.md) | Plan -> check -> Google dry run -> paused build -> read-back -> parity, with a yes before any write. |
| [`campaign-structure`](skills/campaign-structure/SKILL.md) | Brand / Non-brand / Competitor, one ad group per theme, portfolios per type, names that split cleanly in SQL. |
| [`forecast-and-budget`](skills/forecast-and-budget/SKILL.md) | Funnel forecast, starting budget split and spend scenarios; a directional guide, never a verdict. |
| [`intake`](skills/intake/SKILL.md) | The questions to answer and sign off before any build or audit recommendation. |
| [`keyword-research`](skills/keyword-research/SKILL.md) | Keywords chosen on sense from the offerings, brand and competitors; volume and CPC are context, never the decider. |
| [`launch-check`](skills/launch-check/SKILL.md) | Go/no-go checks, client approval, enable on a yes, read back, set read dates, watch week one. |
| [`negatives-and-fencing`](skills/negatives-and-fencing/SKILL.md) | Shared negative lists, campaign and ad-group fencing, login/support negatives, no broad negatives. |
| [`pmax-and-ai-max`](skills/pmax-and-ai-max/SKILL.md) | PMax and AI Max set up fenced and measured on the real goal; AI Max proven by experiment, never switched on blind. |
| [`target-math`](skills/target-math/SKILL.md) | Target CPA or ROAS backed out from LTV, CAC ratio and stage rates; stage values; when and how to add a target. |
| [`tracking-plan`](skills/tracking-plan/SKILL.md) | One primary conversion, every stage back by click ID with a value, a fallback, and a test lead read back on both platforms. |

### Run

| Skill | What it does |
|---|---|
| [`budget-rebalance`](skills/budget-rebalance/SKILL.md) | Budget moves per campaign on performance vs target and recoverable impression share, within the step limit. |
| [`change-safety`](skills/change-safety/SKILL.md) | Every change classified, approved, dry run, applied on a yes, read back and logged. |
| [`expansion-finder`](skills/expansion-finder/SKILL.md) | Micro adds from your own data; macro proposals when a theme outgrows its home, launched as tests. |
| [`pacing-and-alerts`](skills/pacing-and-alerts/SKILL.md) | Pacing vs budget and paced goals, plus alerts that say what broke, where, how bad and the fix. |
| [`parity-check`](skills/parity-check/SKILL.md) | Google vs Microsoft drift flagged entity by entity; budgets and targets deliberately not compared. |
| [`prune-promote`](skills/prune-promote/SKILL.md) | Every lever judged the same way against goal; cuts and promotes become a change list for approval. |
| [`search-term-review`](skills/search-term-review/SKILL.md) | Cut or promote search terms against goal, with the volume gate deciding when there's enough data. |
| [`test-design`](skills/test-design/SKILL.md) | Ranked idea bank, hypothesis card, clicks per arm and a read date, 50/50 with one variable. |
| [`test-read`](skills/test-read/SKILL.md) | Win at 95% confidence on the goal metric or it's learning; roll out, keep control, or log. |
| [`volume-gate`](skills/volume-gate/SKILL.md) | How many clicks before calling a keyword, term or any other lever: cut, promote, flag or watch. |

### Review

| Skill | What it does |
|---|---|
| [`audit`](skills/audit/SKILL.md) | Performance vs goals, one setup health score, ranked findings each tied to its fix. |
| [`diagnose`](skills/diagnose/SKILL.md) | Why a KPI moved: tracking first, mix vs rate, then a fair lever split and the one lever to pull. |
| [`exec-report`](skills/exec-report/SKILL.md) | Pipeline first, brand and non-brand apart, every number vs goal with the reason behind it. |
| [`handoff`](skills/handoff/SKILL.md) | Everything the next owner needs: state, settings, tracking, history, open work and access. |
| [`qbr`](skills/qbr/SKILL.md) | Quarter vs goals and last quarter, tests and learning, scenarios, and the next-quarter plan for sign-off. |

### Cadence (calls the job skills in order)

| Skill | What it does |
|---|---|
| [`daily`](skills/daily/SKILL.md) | Every morning: pacing, alerts, hygiene and flagrant spend. Look, don't act. |
| [`monthly`](skills/monthly/SKILL.md) | Once a month: diagnose every gap, the monthly report, rebalance budget. |
| [`quarterly`](skills/quarterly/SKILL.md) | Once a quarter: audit, QBR, expansion, back-test, re-plan, refresh estimates. |
| [`weekly`](skills/weekly/SKILL.md) | Once a week: the queue, search terms, AI Max and PMax, parity, tests, the weekly report. |

Every skill lists a recommended cadence (`metadata.cadence`). It's a recommendation: any skill can run any time.

## What's inside

| Path | What |
|---|---|
| `skills/<name>/SKILL.md` | The skill: needs, method (the playbook's actual rules and thresholds), output, getting the data |
| `skills/<name>/scripts/run.py` | Runs the math (`run.py perfos ...`) or an API script (`run.py ads ...`) |
| `shared/perfos/` | The deterministic math, standard library only: volume gate, Shapley diagnosis, mix vs rate, budget rebalance, target math, forecast and budget split, test sizing and reading, ICE, change safety, pacing and alerts, fencing, copy limits, audit scoring, naming, parity, report |
| `shared/ads_scripts/` | Google Ads and Microsoft Advertising scripts using your own credentials: snapshot, reports, keyword ideas, entity exports, paused build with read-back, one-change apply |
| `skills.json` | Machine-readable index (name, role, stage, cadence, description, needs, path), built from the SKILL.md files |
| `scripts/` | `build_index.py`, `zip_skills.sh`, `sync_run.sh` |
| `dashboard/` | A React app showing one client's Status, Plan, Audit, Build and Changes from a `results.json` (below) |

Tests: `cd shared && python3 -m pytest`.

The rules come from the open playbook at [github.com/redavio/performance-os](https://github.com/redavio/performance-os).

## Dashboard

`dashboard/` is a small React app (Vite + Tailwind) for one client's paid search: Status, Plan (forecast,
budget split, scenarios), Audit (setup health and ranked findings), Build (the plan tree) and Changes (the
log). It reads `results.json`; "Open results file" opens another. `public/results.json` is a made-up
example (Northwind Analytics, a fictional company).

```bash
cd dashboard && npm install && npm run dev
```

**Making results.json.** `scripts/from_portal.mjs` builds it from the Redavio Client Portal's API answers
for one client (status, planning, plan, changes, and optionally the latest audit), saved as JSON in a
folder; `demo/portal/` shows each file. The shape is `src/types.ts` (`Results`), so any source works if
you fill those fields.

```bash
node scripts/from_portal.mjs demo/portal results.json --client "Northwind Analytics" --as-of 2026-11-18
```

### Make it yours

- **Brand the dashboard.** It ships unbranded. Set your name and logo in `dashboard/src/brand.ts` and
  your brand color (one CSS variable, `--brand`) at the top of `dashboard/src/index.css`. It's styled
  with Tailwind and follows the system's light or dark mode.
- **Reuse the screens in your own app.** The screens in `dashboard/src/components/` take the result as
  props and load nothing themselves; `dashboard/src/App.tsx` is the only part that reads `results.json`.
  Copy the components and types into any React + Tailwind app (add a `brand` color to your Tailwind
  config). They are the same components the Redavio Client Portal uses, without its write controls,
  and are copied here from it, so change them there rather than here if you contribute back.
- **Fork it:** add views, plug in your own data source, or schedule the export.

Tests: `cd dashboard && npm test`.

## Paid display manager

| Skill | Stage | What it does |
|---|---|---|
| [`paid-display-manager`](skills/paid-display-manager/SKILL.md) | Role | Demand Gen, YouTube and Microsoft Audience ads, which skill to use, and the one scorecard. |
| [`display-build`](skills/display-build/SKILL.md) | Set up | Demand Gen and Microsoft Audience campaigns planned, creative made for every format, built paused after your yes. |
| [`display-review`](skills/display-review/SKILL.md) | Run | Placements, channels, audiences and assets through the volume gate; exclusions and budget moves to approve. |
| [`lift-test`](skills/lift-test/SKILL.md) | Run | Holdout sized before launch and read at 95%; honest "not enough to test" when it can't be. |
| [`display-report`](skills/display-report/SKILL.md) | Review | One scorecard for every display campaign: cost to reach, brand lift, pipeline. |

## Other roles

Other Library tools (account-hub, marketing-correlation, performance-marketing-playbook) live in
their own repos today and may move here later as their own roles. Skill names will then need to stay
unique across roles.

## License

MIT. See [LICENSE](LICENSE).
