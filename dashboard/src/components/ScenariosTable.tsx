// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { PsPlanStep, PsScenario } from '../types'
import { campaignLabel, GREY, NOTE, num, TD, TH, usd } from './ui'

/** The plan at the base budget and each scenario budget, against the monthly goals. */
export default function ScenariosTable({ scenarios, steps }: { scenarios: PsScenario[]; steps: PsPlanStep[] }) {
  return (
    <>
      <div className="overflow-x-auto"><table className="w-full">
        <thead><tr>{['Scenario', 'Budget', 'Forecast spend', 'Not forecast'].map(h => <th key={h} className={TH}>{h}</th>)}
          {steps.flatMap(s => [s.name, `Goal ${s.name}`, `CPA ${s.name}`].map(h => (
            <th key={h} className={s.used === false ? `${TH} text-zinc-300 dark:text-zinc-600` : TH}>{h}</th>)))}</tr></thead>
        <tbody>{scenarios.map(s => (
          <tr key={s.scenario}>
            <td className={TD}>{s.scenario}</td><td className={TD}>{usd(s.budget)}</td>
            <td className={TD}>{usd(s.spend_forecast)}</td><td className={TD}>{usd(s.spend_not_forecast)}</td>
            {s.steps.flatMap(x => x.used === false
              ? [0, 1, 2].map(i => <td key={`${x.name}-${i}`} className={GREY}>—</td>)
              : [
              <td key={`${x.name}-v`} className={TD}>{num(x.volume, 2)}</td>,
              <td key={`${x.name}-g`} className={TD}>{x.goal == null ? '—' : `${num(x.goal, 0)} (${x.vs_goal != null && x.vs_goal > 0 ? '+' : ''}${num((x.vs_goal ?? 0) * 100, 0)}%)`}</td>,
              <td key={`${x.name}-c`} className={TD}>{usd(x.cpa)}</td>])}
          </tr>))}</tbody>
      </table></div>
      {scenarios.some(s => s.capped_by_demand.length > 0) && (
        <p className={NOTE}>Capped by demand: {Array.from(new Set(scenarios.flatMap(s => s.capped_by_demand))).map(campaignLabel).join(', ')}.</p>
      )}
    </>
  )
}
