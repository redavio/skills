// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { PsForecast, PsPlanStep } from '../types'
import { CAMPAIGN_TYPE, GREY, num, PLATFORM, TD, TH, usd } from './ui'

function stepCells(s: PsPlanStep) {
  if (s.used === false) return [0, 1, 2].map(i => <td key={`${s.name}-${i}`} className={GREY}>—</td>)
  return [
    <td key={`${s.name}-v`} className={TD}>{num(s.volume, 2)}</td>,
    <td key={`${s.name}-c`} className={TD}>{usd(s.cpa)}</td>,
    <td key={`${s.name}-r`} className={TD}>{s.roas == null ? '—' : `${num(s.roas, 2)}x`}</td>]
}

/** Funnel forecast per month: searches to cost, then every conversion point with CPA and ROAS. */
export default function ForecastTable({ forecast }: { forecast: PsForecast }) {
  return (
    <div className="overflow-x-auto"><table className="w-full">
      <thead><tr>{['Platform', 'Campaign', 'Searches', 'Clicks', 'CPC', 'CPC from', 'Cost'].map(h => <th key={h} className={TH}>{h}</th>)}
        {forecast.total.steps.flatMap(s => [s.name, `CPA ${s.name}`, `ROAS ${s.name}`].map(h => (
          <th key={h} className={s.used === false ? `${TH} text-zinc-300 dark:text-zinc-600` : TH}>{h}</th>)))}</tr></thead>
      <tbody>
        {forecast.rows.map(r => (
          <tr key={`${r.platform}-${r.campaign_type}`}>
            <td className={TD}>{PLATFORM[r.platform] ?? r.platform}</td><td className={TD}>{CAMPAIGN_TYPE[r.campaign_type]}</td>
            <td className={TD}>{num(r.searches, 0)}</td><td className={TD}>{num(r.clicks)}</td>
            <td className={TD}>{usd(r.cpc, 2)}</td><td className={TD}>{r.cpc_source}</td><td className={TD}>{usd(r.cost)}</td>
            {r.steps.flatMap(s => stepCells(s))}
          </tr>
        ))}
        <tr className="font-medium">
          <td className={TD}>Total</td><td className={TD} /><td className={TD}>{num(forecast.total.searches, 0)}</td>
          <td className={TD}>{num(forecast.total.clicks)}</td><td className={TD} /><td className={TD} /><td className={TD}>{usd(forecast.total.cost)}</td>
          {forecast.total.steps.flatMap(s => stepCells(s))}
        </tr>
      </tbody>
    </table></div>
  )
}
