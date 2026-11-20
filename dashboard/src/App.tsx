import { useEffect, useState } from "react";
import { BRAND } from "./brand";
import PaidSearchManager, { VIEWS, type View } from "./components/PaidSearchManager";
import type { Results } from "./types";

/**
 * The loader: reads results.json (or ?src=other.json) and lets you open another results file.
 * Everything on screen is drawn by components/, which only take the result as props.
 */
export default function App() {
  const params = new URLSearchParams(location.search);
  const viewParam = params.get("view");
  const initialView: View = viewParam && viewParam in VIEWS ? (viewParam as View) : "status";
  const [res, setRes] = useState<Results | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const src = params.get("src") || "results.json";
    fetch(src)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`Couldn't load ${src}.`))))
      .then(setRes)
      .catch((e: Error) => setError(e.message));
  }, []);

  const open = (file: File) =>
    file.text().then((t) => {
      try {
        setRes(JSON.parse(t));
        setError("");
      } catch {
        setError("That file isn't a Paid Search Manager results file.");
      }
    });

  return (
    <div className="mx-auto max-w-6xl px-4 pb-16 pt-6">
      <header className="mb-1 flex flex-wrap items-start justify-between gap-4">
        <h1 className="flex items-center gap-2.5 text-2xl font-semibold">
          {BRAND.logo && <img src={BRAND.logo} alt="" className="h-7" />}
          {BRAND.name}
        </h1>
        <label className="cursor-pointer rounded-lg border border-zinc-200 px-3 py-2 text-sm hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-800">
          Open results file
          <input
            type="file"
            accept=".json"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && open(e.target.files[0])}
          />
        </label>
      </header>
      {error && <p className="mt-3 rounded-lg bg-brand/10 px-3 py-2.5 text-sm">{error} Make one with scripts/from_portal.mjs, then open it here.</p>}
      {res && <PaidSearchManager res={res} initialView={initialView} />}
    </div>
  );
}
