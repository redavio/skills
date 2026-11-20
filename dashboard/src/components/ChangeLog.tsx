// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { ReactNode } from 'react'
import type { PsChangeGroup } from '../types'
import { TD, TH } from './ui'

const WHO = { redavio: 'Redavio', outside: 'Outside Redavio', platform: 'Platform' }

/**
 * Changes grouped by day: platform, category, what, who and why. Read only; an app that records the
 * why on an outside change passes its own cell in whyCell (shown where no why is recorded yet).
 */
export default function ChangeLog({ groups, whyCell }: { groups: PsChangeGroup[]; whyCell?: (g: PsChangeGroup) => ReactNode }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr>{['Day', 'Platform', 'Category', 'What', 'Who', 'Why'].map(h => <th key={h} className={TH}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {groups.map(g => (
            <tr key={`${g.day}|${g.platform}|${g.category}|${g.item}|${g.operation}|${g.made_by}`} className="border-t border-zinc-100 dark:border-zinc-800">
              <td className={`${TD} whitespace-nowrap`}>{g.day}</td>
              <td className={TD}>{g.platform_label}</td>
              <td className={TD}>{g.category}</td>
              <td className={TD}>{g.changes > 1 ? `${g.changes.toLocaleString()} × ` : ''}{g.item}{g.operation ? ` (${g.operation.toLowerCase()})` : ''}</td>
              <td className={TD}>{WHO[g.made_by]}</td>
              <td className={TD}>{g.why ?? (whyCell ? whyCell(g) : '—')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
