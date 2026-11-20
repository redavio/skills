// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
import type { PsAuditResult, PsCampaignSettings, PsPlanItemType, PsStatusItem } from '../types'

// Labels, formatting and Tailwind classes shared by the Paid Search Manager views. Display only:
// every number comes from the backend.

export const TH = 'px-2 py-1.5 text-left text-xs font-medium text-zinc-500'
export const TD = 'px-2 py-1.5 text-sm tabular-nums text-zinc-800 dark:text-zinc-200'
export const NOTE = 'text-xs text-zinc-500 dark:text-zinc-400'
export const GREY = 'px-2 py-1.5 text-sm text-zinc-300 dark:text-zinc-600'

export const CAMPAIGN_TYPE: Record<string, string> = { brand: 'Brand', nonbrand: 'Non-brand', competitor: 'Competitor', pmax: 'PMax' }
export const PLATFORM: Record<string, string> = { google_ads: 'Google', bing_ads: 'Microsoft' }
export const PLATFORM_LABELS = { google_ads: 'Google', bing_ads: 'Microsoft' } as const

export const usd = (n: number | null | undefined, digits = 0) =>
  n == null ? '—' : `$${n.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits })}`
export const num = (n: number | null | undefined, digits = 1) =>
  n == null ? '—' : n.toLocaleString(undefined, { maximumFractionDigits: digits })

/** "google_ads nonbrand" -> "Google Non-brand" */
export const campaignLabel = (key: string) => {
  const [p, t] = key.split(' ')
  return `${PLATFORM[p] ?? p} ${CAMPAIGN_TYPE[t] ?? t}`
}

export const STATUS_DOT: Record<PsStatusItem['state'], string> = {
  done: 'bg-emerald-500', todo: 'bg-amber-500', waiting: 'bg-zinc-300 dark:bg-zinc-600', not_set_up: 'bg-zinc-300 dark:bg-zinc-600',
}
export const STATUS_TIP: Record<PsStatusItem['state'], string> = {
  done: 'Done', todo: 'Needs you', waiting: 'Waiting on real data or time', not_set_up: 'Not set up yet',
}

export const RESULT_CLASS: Record<PsAuditResult, string> = {
  pass: 'text-emerald-600 dark:text-emerald-400', partial: 'text-amber-600 dark:text-amber-400',
  fail: 'text-red-600 dark:text-red-400', not_applicable: 'text-zinc-500',
}

export const TYPE_LABELS: Record<PsPlanItemType, string> = {
  campaign: 'Campaign', ad_group: 'Ad group', keyword: 'Keyword', negative: 'Negative', ad: 'Ad',
  negative_list: 'Negative list', sitelink: 'Sitelink', callout: 'Callout', snippet: 'Snippet',
  asset_group: 'Asset group',
}
/** Which items can sit under which. */
export const CHILD_TYPES: Record<PsPlanItemType, PsPlanItemType[]> = {
  campaign: ['ad_group', 'negative'], ad_group: ['keyword', 'negative', 'ad'], keyword: [], negative: [], ad: [],
  negative_list: ['negative'], sitelink: [], callout: [], snippet: [], asset_group: [],
}
export const BIDDING_LABELS: Record<NonNullable<PsCampaignSettings['bidding']>, string> = {
  max_conversions: 'Maximize conversions', max_conversion_value: 'Maximize conversion value',
}
export function settingsSummary(d: PsCampaignSettings | null): string {
  if (!d || d.daily_budget === undefined) return 'Settings needed'
  return [
    `$${d.daily_budget}/day`,
    d.bidding ? BIDDING_LABELS[d.bidding] : 'no bid strategy',
    `${(d.locations ?? []).length} location(s)`,
    `${(d.languages ?? []).length} language(s)`,
    d.ai_max ? 'AI Max on' : 'AI Max off',
  ].join(' · ')
}
