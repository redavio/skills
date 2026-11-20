// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { ReactNode } from 'react'
import type { PsAudit } from '../types'
import { PLATFORM_LABELS, RESULT_CLASS } from './ui'

/**
 * Audit scorecard: setup health (and the last audit's), then the findings ranked by impact on goals,
 * then effort. Read only; an app that records the client's sign-off passes its form in signOff.
 */
export default function AuditSummary({ audit, previous, signOff }: {
  audit: PsAudit
  previous?: { created_at: string; setup_health: number | null } | null
  signOff?: ReactNode
}) {
  return (
    <section className="grid gap-4 sm:grid-cols-3">
      <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
        <p className="text-xs text-zinc-500">Setup health</p>
        <p className="text-2xl font-semibold tabular-nums text-zinc-900 dark:text-zinc-100">
          {audit.setup_health === null ? '–' : `${audit.setup_health}%`}
        </p>
        <p className="text-xs text-zinc-500">2 / 1 / 0 per item, Measurement counts double</p>
        {previous && (
          <p className="mt-1 text-xs text-zinc-500">
            Last audit ({new Date(previous.created_at).toLocaleDateString()}): {previous.setup_health === null ? '–' : `${previous.setup_health}%`}
          </p>
        )}
      </div>
      <div className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900 sm:col-span-2">
        <p className="text-xs text-zinc-500 mb-1">Findings, ranked by impact on goals, then effort</p>
        {audit.findings.length === 0 ? (
          <p className="text-sm text-zinc-500">No fails or partials yet.</p>
        ) : (
          <ol className="list-decimal pl-5 text-sm text-zinc-800 dark:text-zinc-200">
            {audit.findings.map(f => (
              <li key={`${f.code}-${f.platform}`}>
                <span className={RESULT_CLASS[f.result ?? 'fail']}>{f.code} {f.title}</span>
                <span className="text-zinc-500"> · {PLATFORM_LABELS[f.platform]}{f.impact ? ` · ${f.impact} impact` : ''}</span>
                {f.evidence && <span className="text-zinc-500">: {f.evidence}</span>}
                <span className="text-xs text-zinc-400"> (fix: {f.doc_ref})</span>
              </li>
            ))}
          </ol>
        )}
        {audit.findings.length > 0 && (
          <div className="mt-3 border-t border-zinc-100 pt-2 text-xs dark:border-zinc-800">
            {audit.fix_plan_signed_by ? (
              <p className="text-emerald-700 dark:text-emerald-400">
                Fix plan signed off by {audit.fix_plan_signed_by} on {new Date(audit.fix_plan_signed_at ?? '').toLocaleDateString()}.
              </p>
            ) : signOff}
          </div>
        )}
      </div>
    </section>
  )
}
