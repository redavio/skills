// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import { useState, type ReactNode } from 'react'
import type { Results } from '../types'
import AuditSummary from './AuditSummary'
import BudgetTable, { budgetTitle } from './BudgetTable'
import ChangeLog from './ChangeLog'
import ForecastTable from './ForecastTable'
import PlanTree from './PlanTree'
import ScenariosTable from './ScenariosTable'
import StatusList from './StatusList'
import VideoAds from './VideoAds'
import { NOTE } from './ui'

export const VIEWS = { status: 'Status', plan: 'Plan', audit: 'Audit', build: 'Build', changes: 'Changes', video: 'Video' } as const
export type View = keyof typeof VIEWS

const CARD = 'flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900'

function Card({ title, help, children }: { title: string; help?: string; children: ReactNode }) {
  return (
    <section className={CARD}>
      <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">{title}</h2>
      {help && <p className={NOTE}>{help}</p>}
      {children}
    </section>
  )
}

/**
 * The Paid Search Manager's read-only views for one client's results.json: Status, Plan (forecast,
 * budget split, scenarios), Audit (scorecard and ranked findings), Build (the plan tree) and Changes
 * (the log). The same components the Redavio Client Portal draws, without its write controls. Takes
 * the result as props and loads nothing itself.
 */
export default function PaidSearchManager({ res, initialView = 'status' }: { res: Results; initialView?: View }) {
  const [view, setView] = useState<View>(initialView)
  const plan = res.build.plan
  return (
    <div>
      <p className="text-sm text-zinc-500 dark:text-zinc-400">{res.client}. Data as of {res.as_of}.</p>
      <nav className="mb-4 mt-4 flex flex-wrap gap-1.5">
        {(Object.keys(VIEWS) as View[]).filter(v => v !== 'video' || res.video).map(v => (
          <button key={v} type="button" onClick={() => setView(v)}
            className={`rounded-full border px-3.5 py-1.5 text-sm ${view === v
              ? 'border-brand bg-brand text-white'
              : 'border-zinc-200 hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-800'}`}>
            {VIEWS[v]}
          </button>
        ))}
      </nav>

      {view === 'video' && res.video && (
        <section className={CARD}><VideoAds video={res.video} /></section>
      )}

      {view === 'status' && <div data-shot="1"><StatusList status={res.status} /></div>}

      {view === 'plan' && (
        <div className="flex flex-col gap-5" data-shot="2">
          <Card title="Funnel forecast (per month)" help="A directional guide, never a verdict: searches to clicks to cost, then each conversion point with CPA and ROAS.">
            <ForecastTable forecast={res.plan.forecast} />
          </Card>
          <Card title={`Budget split · ${budgetTitle(res.plan.budget)}`}>
            <BudgetTable budget={res.plan.budget} />
          </Card>
          <Card title="Scenarios (per month)" help="The same plan at the base budget and each scenario budget, against the monthly goals.">
            <ScenariosTable scenarios={res.plan.scenarios} steps={res.plan.forecast.total.steps} />
          </Card>
        </div>
      )}

      {view === 'audit' && (
        <div data-shot="3">
          {res.audit
            ? <AuditSummary audit={res.audit} previous={res.previous_audit} />
            : <p className={NOTE}>No audit yet.</p>}
        </div>
      )}

      {view === 'build' && (
        <Card title="Build plan" help="Campaign names follow channel|type|theme|geo|language.">
          {plan.length === 0 ? <p className={NOTE}>No build plan yet.</p> : (
            <PlanTree campaigns={plan.filter(i => i.item_type === 'campaign')}
              accountItems={plan.filter(i => i.item_type !== 'campaign')} />
          )}
        </Card>
      )}

      {view === 'changes' && (
        <Card title="Change log" help={`${res.changes.total.toLocaleString()} changes, grouped by day.`}>
          <ChangeLog groups={res.changes.recent} />
        </Card>
      )}
    </div>
  )
}
