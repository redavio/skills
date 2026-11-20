/**
 * Make results.json for this dashboard from the Redavio Client Portal's API answers for one client.
 *
 *   node scripts/from_portal.mjs <folder> [out.json] --client "<name>" --as-of YYYY-MM-DD
 *
 * <folder> holds the portal's JSON answers, saved as they come back (GET, read only):
 *   status.json          /portal/paid-search/status?client_id=…
 *   planning.json        /portal/paid-search/planning?client_id=…
 *   plan.json            /portal/paid-search/plan?client_id=…          (the build plan tree)
 *   changes.json         /portal/paid-search/changes?client_id=…
 *   audit.json           /portal/paid-search/audits/<id>?client_id=…   (optional: no audit yet)
 *   previous_audit.json  the audit before that one                     (optional)
 * Only the read-only views are kept: no keyword research, assumptions, approvals or outside-change
 * notes. The shape is src/types.ts `Results`; demo/portal/ is a made-up example.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const flag = (name) => {
  const i = args.indexOf(name);
  return i >= 0 ? args.splice(i, 2)[1] : undefined;
};
const client = flag("--client") ?? "";
const asOf = flag("--as-of") ?? new Date().toISOString().slice(0, 10);
const [dir, out = "results.json"] = args;
if (!dir) {
  console.error('Usage: node scripts/from_portal.mjs <folder> [out.json] --client "<name>" --as-of YYYY-MM-DD');
  process.exit(1);
}
const load = (name, optional = false) => {
  const p = path.join(dir, name);
  if (!existsSync(p)) {
    if (optional) return null;
    console.error(`Missing ${p}.`);
    process.exit(1);
  }
  return JSON.parse(readFileSync(p, "utf8"));
};

const planning = load("planning.json");
const changes = load("changes.json");
const previous = load("previous_audit.json", true);
const results = {
  tool: "Paid Search Manager",
  version: 1,
  client,
  as_of: asOf,
  status: load("status.json"),
  plan: { forecast: planning.forecast, budget: planning.budget, scenarios: planning.scenarios },
  audit: load("audit.json", true),
  previous_audit: previous ? { created_at: previous.created_at, setup_health: previous.setup_health } : null,
  build: { plan: load("plan.json") },
  changes: { recent: changes.recent, total: changes.total },
};
writeFileSync(out, JSON.stringify(results, null, 1) + "\n");
console.log(`Wrote ${out}`);
