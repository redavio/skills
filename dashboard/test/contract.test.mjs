// The dashboard's contract.
// - components/ and types.ts are copied from the Redavio Client Portal (the canonical copy): they take
//   the result as props, never fetch or write, never import brand.ts, and use no inline styles.
// - public/results.json (the demo) has exactly the fields types.ts says, and is what
//   scripts/from_portal.mjs makes from the portal's API answers in demo/portal/.
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";

const ROOT = new URL("../", import.meta.url).pathname;
const read = (p) => readFileSync(path.join(ROOT, p), "utf8");

function interfaceFields(name) {
  const body = read("src/types.ts").match(new RegExp(`export interface ${name} \\{([\\s\\S]*?)\\n\\}`))[1];
  return new Set([...body.matchAll(/^ {2}(\w+)\??:/gm)].map((m) => m[1]));
}

test("the demo results.json matches types.ts", () => {
  const res = JSON.parse(read("public/results.json"));
  assert.deepEqual(new Set(Object.keys(res)), interfaceFields("Results"));
});

test("from_portal.mjs turns the portal's API answers into the demo results.json", () => {
  const out = path.join(mkdtempSync(path.join(tmpdir(), "psm-")), "results.json");
  execFileSync(process.execPath, [path.join(ROOT, "scripts/from_portal.mjs"), path.join(ROOT, "demo/portal"), out,
    "--client", "Northwind Analytics", "--as-of", "2026-11-18"]);
  assert.deepEqual(JSON.parse(readFileSync(out, "utf8")), JSON.parse(read("public/results.json")));
});

test("components take props only: no fetching or writing, no brand.ts, no inline styles", () => {
  const files = readdirSync(path.join(ROOT, "src/components")).filter((f) => f.endsWith(".tsx"));
  assert.ok(files.length, "src/components/ is empty");
  for (const f of files) {
    const src = read(`src/components/${f}`);
    assert.ok(!/\bfetch\(|apiFetch|method: ['"]POST/.test(src), `${f} fetches or writes; pass the result in as props`);
    assert.ok(![...src.matchAll(/from ['"]([^'"]+)['"]/g)].some((m) => m[1].includes("brand")), `${f} imports brand.ts`);
    assert.ok(!src.includes("style={"), `${f} uses inline styles; use Tailwind classes`);
  }
});
