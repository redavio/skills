// copied from the Redavio Client Portal (growth-genie-core), do not edit here, run scripts/sync_library.mjs there
// Paid Search Manager: the shapes its read-only views take. Canonical here, in the Client Portal
// (frontend/src/api/paidSearch.ts re-exports them); copied out to the public app in
// github.com/redavio/skills (dashboard/) by scripts/sync_library.mjs.

export type PsPlatform = 'google_ads' | 'bing_ads'

// ── Status ────────────────────────────────────────────────────────────────────
export interface PsStatusItem {
  step: string
  tab: string
  state: 'done' | 'todo' | 'waiting' | 'not_set_up'
  detail: string
  gating: boolean
}

export interface PsStatus {
  items: PsStatusItem[]
  done: boolean
  gating_done: number
  gating_total: number
}

// ── Plan: forecast, budget split, scenarios ───────────────────────────────────
export interface PsPlanStep {
  name: string
  used?: boolean                 // false = a standard funnel stage this client doesn't use (shown greyed)
  volume: number | null
  cpa: number | null
  roas: number | null
  rate?: number
  rate_source?: string
  goal?: number | null
  vs_goal?: number | null
}

export interface PsPlanForecastRow {
  platform: string
  campaign_type: string
  searches: number
  clicks: number
  cpc: number
  cpc_source: string
  cost: number
  steps: PsPlanStep[]
}

export interface PsForecast {
  rows: PsPlanForecastRow[]
  total: { searches: number; clicks: number; cost: number; steps: PsPlanStep[] }
}

export interface PsBudgetLine {
  platform: string
  campaign_type: string
  monthly: number
  daily: number
  at_minimum: boolean
  set_by_you: boolean
}

export interface PsBudget {
  monthly_budget: number
  selected_monthly?: number
  lines: PsBudgetLine[]
}

export interface PsScenario {
  scenario: string
  budget: number
  spend_forecast: number
  spend_not_forecast: number
  capped_by_demand: string[]
  steps: PsPlanStep[]
}

// ── Audit ─────────────────────────────────────────────────────────────────────
export type PsAuditResult = 'pass' | 'partial' | 'fail' | 'not_applicable'
export type PsLevel = 'high' | 'medium' | 'low'

export interface PsAuditRow {
  code: string
  part: 'setup' | 'performance'
  title: string
  summary: string
  doc_ref: string
  weight: number
  platform: PsPlatform
  result: PsAuditResult | null
  evidence: string | null
  impact: PsLevel | null
  effort: PsLevel | null
}

export interface PsAudit {
  id: number
  note: string | null
  created_at: string
  fix_plan_signed_by?: string | null
  fix_plan_signed_at?: string | null
  rows: PsAuditRow[]
  setup_health: number | null
  findings: PsAuditRow[]
}

// ── Build: the plan tree ──────────────────────────────────────────────────────
export type PsPlanItemType = 'campaign' | 'ad_group' | 'keyword' | 'negative' | 'ad'
  | 'negative_list' | 'sitelink' | 'callout' | 'snippet' | 'asset_group'
export type PsMatchType = 'exact' | 'phrase' | 'broad'

export interface PsAdDetails {
  headlines?: string[]
  descriptions?: string[]
  paths?: string[]
  headline_types?: (string | null)[]
  page_brief?: { headline?: string; subhead?: string; sections?: string[]; cta?: string }
  // account-level assets
  description1?: string
  description2?: string
  values?: string[]
}

export interface PsCampaignSettings {
  daily_budget?: number
  bidding?: 'max_conversions' | 'max_conversion_value'
  locations?: string[]
  languages?: string[]
  ai_max?: boolean
  url_exclusions?: string[]
  microsoft_locations?: string[]
  microsoft_languages?: string[]
  negative_lists?: number[]
  channel?: 'pmax'
  images?: { landscape?: string[]; square?: string[]; portrait?: string[] }
  microsoft_daily_budget?: number
}

export interface PsPlanItem {
  id: number
  parent_id: number | null
  item_type: PsPlanItemType
  name: string
  match_type: PsMatchType | null
  final_url: string | null
  details: (PsAdDetails & PsCampaignSettings) | null
  problems?: string[]
  children: PsPlanItem[]
}

// ── Changes: the log ──────────────────────────────────────────────────────────
export interface PsChangeGroup {
  day: string
  platform: string
  platform_label: string
  category: string
  item: string
  operation: string | null
  made_by: 'redavio' | 'outside' | 'platform'
  changes: number
  changed_by: string | null
  why: string | null
}

// ── The public app's results.json: one client's five views in one file ───────
export interface Results {
  tool: string
  version: number
  client: string
  as_of: string
  status: PsStatus
  plan: { forecast: PsForecast; budget: PsBudget; scenarios: PsScenario[] }
  audit: PsAudit | null
  previous_audit: { created_at: string; setup_health: number | null } | null
  build: { plan: PsPlanItem[] }
  changes: { recent: PsChangeGroup[]; total: number }
}
