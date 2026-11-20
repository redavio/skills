// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { ReactNode } from 'react'
import type { PsBudget, PsBudgetLine } from '../types'
import { CAMPAIGN_TYPE, NOTE, PLATFORM, TD, TH, usd } from './ui'

/** The heading text for a budget split: "$X of $Y a month" when channels are picked. */
export const budgetTitle = (b: PsBudget) =>
  `${b.selected_monthly != null ? `${usd(b.selected_monthly, 2)} of ` : ''}${usd(b.monthly_budget, 2)} a month`

/**
 * Budget split per platform and campaign. Read only; an app that edits the daily budget passes
 * its own cell in dailyCell.
 */
export default function BudgetTable({ budget, dailyCell }: { budget: PsBudget; dailyCell?: (line: PsBudgetLine) => ReactNode }) {
  return (
    <div className="overflow-x-auto"><table className="w-full">
      <thead><tr>{['Platform', 'Campaign', 'Monthly', 'Daily', ''].map(h => <th key={h} className={TH}>{h}</th>)}</tr></thead>
      <tbody>{budget.lines.map(l => (
        <tr key={`${l.platform}-${l.campaign_type}`}>
          <td className={TD}>{PLATFORM[l.platform] ?? l.platform}</td><td className={TD}>{CAMPAIGN_TYPE[l.campaign_type]}</td>
          <td className={TD}>{usd(l.monthly, 2)}</td>
          <td className={TD}>{dailyCell ? dailyCell(l) : usd(l.daily, 2)}</td>
          <td className={TD}>{l.set_by_you ? <span className={NOTE}>set by you</span> : l.at_minimum && <span className={NOTE}>at the minimum</span>}</td>
        </tr>))}</tbody>
    </table></div>
  )
}
