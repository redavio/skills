// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import { useState, type ReactNode } from 'react'
import type { PsPlanItem } from '../types'
import { CHILD_TYPES, settingsSummary, TYPE_LABELS } from './ui'

/**
 * Slots an editing app fills in around one node (the Client Portal: rename, settings, delete, add).
 * Left empty, the node is read only.
 */
export interface PlanNodeSlots {
  /** Replaces the name, e.g. a rename field. */
  name?: ReactNode
  /** Right-aligned actions on the node's line. */
  actions?: ReactNode
  /** Under the line, always shown, e.g. a settings form. */
  below?: ReactNode
  /** After the children, while open, e.g. add buttons. */
  after?: ReactNode
}

/** One plan item and, when open, its details and children. */
export function PlanTreeNode({ item, depth, slots = {}, renderChild }: {
  item: PsPlanItem
  depth: number
  slots?: PlanNodeSlots
  /** How to draw a child; defaults to a read-only node. */
  renderChild?: (child: PsPlanItem, depth: number) => ReactNode
}) {
  const [open, setOpen] = useState(depth < 2)  // campaigns and ad groups open
  const hasChildren = item.children.length > 0 || CHILD_TYPES[item.item_type].length > 0
  const child = renderChild ?? ((c: PsPlanItem, d: number) => <PlanTreeNode key={c.id} item={c} depth={d} />)

  return (
    <li className="py-1.5">
      <div className="flex flex-wrap items-center gap-2">
        {hasChildren ? (
          <button type="button" onClick={() => setOpen(!open)} className="w-4 text-xs text-zinc-400"
            aria-label={open ? 'Collapse' : 'Expand'}>{open ? '▾' : '▸'}</button>
        ) : <span className="w-4" />}
        <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-zinc-500 dark:bg-zinc-800">
          {TYPE_LABELS[item.item_type]}
        </span>
        {slots.name ?? <span className="text-sm text-zinc-900 dark:text-zinc-100">{item.name}</span>}
        {item.match_type && <span className="text-xs text-zinc-500">[{item.match_type}]</span>}
        {item.item_type === 'campaign' && (
          <span className="text-xs text-zinc-500">{settingsSummary(item.details)}</span>
        )}
        {item.final_url && item.item_type !== 'campaign' && (
          <span className="text-xs text-zinc-400 truncate max-w-64">{item.final_url}</span>
        )}
        {item.problems && (
          <span className={`text-xs ${item.problems.length ? 'text-amber-600' : 'text-emerald-600'}`}>
            {item.problems.length ? item.problems.join(' · ') : 'Complete'}
          </span>
        )}
        {slots.actions}
      </div>
      {slots.below}
      {open && (
        <div className="pl-6">
          {item.item_type === 'ad' && item.details && (
            <div className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
              {(item.details.headlines ?? []).map((h, i) => (
                <span key={i}>{i > 0 && ' | '}{h}{item.details?.headline_types?.[i] ? ` (${item.details.headline_types[i]})` : ''}</span>
              ))}
              {item.details.page_brief && (
                <details className="mt-1">
                  <summary className="cursor-pointer text-amber-700 dark:text-amber-400">No page for this theme yet: brief</summary>
                  <p className="mt-1"><b>{item.details.page_brief.headline}</b> {item.details.page_brief.subhead}</p>
                  <ul className="list-disc pl-5">{(item.details.page_brief.sections ?? []).map(s => <li key={s}>{s}</li>)}</ul>
                  <p>CTA: {item.details.page_brief.cta}</p>
                </details>
              )}
            </div>
          )}
          {item.item_type === 'sitelink' && item.details && (
            <div className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
              {item.details.description1} · {item.details.description2}
            </div>
          )}
          {item.item_type === 'snippet' && item.details && (
            <div className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">{(item.details.values ?? []).join(', ')}</div>
          )}
          {item.children.length > 0 && <ul>{item.children.map(c => child(c, depth + 1))}</ul>}
          {slots.after}
        </div>
      )}
    </li>
  )
}

/**
 * The build plan as a tree: campaigns, then account-level items (negative lists, sitelinks,
 * callouts, snippets). Campaign › ad group › keyword / negative / ad.
 */
export default function PlanTree({ campaigns, accountItems, renderNode }: {
  campaigns: PsPlanItem[]
  accountItems: PsPlanItem[]
  /** How to draw a top-level item; defaults to a read-only node. */
  renderNode?: (item: PsPlanItem) => ReactNode
}) {
  const node = renderNode ?? ((i: PsPlanItem) => <PlanTreeNode key={i.id} item={i} depth={0} />)
  return (
    <>
      {[{ label: 'Campaigns', items: campaigns }, { label: 'Account level', items: accountItems }]
        .filter(g => g.items.length > 0).map(g => (
          <div key={g.label} className="mt-3">
            <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500">{g.label}</h3>
            <ul>{g.items.map(node)}</ul>
          </div>
        ))}
    </>
  )
}
