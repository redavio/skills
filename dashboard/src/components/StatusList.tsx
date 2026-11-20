// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { PsStatus, PsStatusItem } from '../types'
import { STATUS_DOT, STATUS_TIP } from './ui'

/**
 * Status: what's done and what's needed across every step, what needs doing first. Read only.
 * With onOpen, each line is a button that opens its tab (the Client Portal); without, plain lines.
 */
export default function StatusList({ status, onOpen }: { status: PsStatus; onOpen?: (tab: string) => void }) {
  const order = (i: PsStatusItem) => (i.state === 'todo' ? (i.gating ? 0 : 1) : i.state === 'done' ? 3 : 2)
  const rows = [...status.items].sort((a, b) => order(a) - order(b))
  const line = 'w-full flex items-center gap-3 px-4 py-2.5 text-left'
  return (
    <div className="flex flex-col gap-4">
      <div>
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          {status.done ? 'Launched and running' : `${status.gating_done} of ${status.gating_total} done to launch`}
        </h2>
        {onOpen && (
          <p className="text-xs text-zinc-500" title="Items marked 'not needed to launch' never hold a client up.">
            Click a line to open its tab.
          </p>
        )}
      </div>
      <ul className="rounded-lg border border-zinc-200 bg-white divide-y divide-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:divide-zinc-800">
        {rows.map(i => {
          const body = (
            <>
              <span className={`h-2 w-2 shrink-0 rounded-full ${STATUS_DOT[i.state]}`} title={STATUS_TIP[i.state]} />
              <span className="whitespace-nowrap text-sm text-zinc-900 dark:text-zinc-100">{i.step}</span>
              {!i.gating && <span className="text-[10px] uppercase tracking-wide text-zinc-400" title="Not needed to launch">optional</span>}
              <span className="ml-auto truncate text-xs text-zinc-500" title={i.detail}>{i.detail}</span>
            </>
          )
          return (
            <li key={i.step}>
              {onOpen ? (
                <button type="button" onClick={() => onOpen(i.tab)} className={`${line} hover:bg-zinc-50 dark:hover:bg-zinc-800`}>{body}</button>
              ) : (
                <div className={line}>{body}</div>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
