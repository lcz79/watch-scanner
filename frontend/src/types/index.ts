export interface WatchQuery {
  reference: string
  brand?: string
  max_price?: number
  currency?: string
}

export interface WatchListing {
  source: string
  reference: string
  price: number
  currency: string
  seller: string
  url: string
  condition: 'new' | 'mint' | 'good' | 'fair' | 'unknown'
  scraped_at: string
  image_url?: string
  location?: string
  description?: string
}

export interface ScanResult {
  scan_id: string
  query: WatchQuery
  listings: WatchListing[]
  best_price?: number
  best_listing?: WatchListing
  total_found: number
  scanned_at: string
  agents_used: string[]
  duration_seconds: number
}

export interface AgentStatus {
  name: string
  status: 'ok' | 'error' | 'mock'
  mock_mode: boolean
  last_run?: string
  error?: string
}

export interface AlertConfig {
  reference: string
  brand?: string
  max_price: number
  currency?: string
  notify_email?: string
  notify_whatsapp?: string
  notify_telegram_chat_id?: string
}

export interface Alert {
  alert_id: string
  config: AlertConfig
  created_at: string
  active: boolean
  last_triggered?: string
}

export interface MarketStats {
  reference: string
  min_price: number
  max_price: number
  median_price: number
  mean_price: number
  p25: number
  p75: number
  fair_price: number
  sample_size: number
}

export interface PriceDistribution {
  bins: Array<{ range: string; count: number; percentage: number }>
  percentile_bands: { p10: number; p25: number; p50: number; p75: number; p90: number }
}

export interface ScoredListing extends WatchListing {
  deal_score: number
  price_advantage: number
  is_best_deal: boolean
  discount_pct: number
  completeness_score: number
}

export interface InvestmentScore {
  investment_score: number
  trend: 'up' | 'down' | 'stable'
  volatility: number
  liquidity: 'high' | 'medium' | 'low'
  signal: 'buy' | 'hold' | 'avoid'
}

export interface PriceSnapshot {
  date: string
  median_price: number
  min_price: number
  max_price: number
  sample_size: number
}

export interface Recommendation {
  reference: string
  global_score: number
  top_deal: ScoredListing | null
  market_stats: MarketStats
  investment: InvestmentScore
}

export interface AnalysisResult {
  reference: string
  market_stats: MarketStats
  distribution: PriceDistribution
  scored_listings: ScoredListing[]
  investment: InvestmentScore
  top_deal: ScoredListing | null
}

// ── Encyclopedia ──────────────────────────────────────────────────────────────

export interface WatchStory {
  id: number
  reference: string
  category: string | null
  title: string
  content: string
  source_url: string | null
}

export interface WatchImage {
  id: number
  reference: string
  url: string
  source: string | null
  is_primary: boolean
  local_path: string | null
}

export interface WatchVariant {
  id: number
  parent_reference: string
  variant_reference: string
  description: string | null
}

export interface EncyclopediaWatch {
  id: number
  brand: string
  model: string
  reference: string
  collection: string | null
  year_introduced: number | null
  year_discontinued: number | null
  case_material: string | null
  case_diameter_mm: number | null
  case_thickness_mm: number | null
  water_resistance_m: number | null
  movement_type: string | null
  movement_caliber: string | null
  power_reserve_h: number | null
  frequency_vph: number | null
  jewels: number | null
  dial_color: string | null
  dial_material: string | null
  bracelet_type: string | null
  clasp_type: string | null
  retail_price_eur: number | null
  avg_market_price_eur: number | null
  description: string | null
  technical_notes: string | null
  is_discontinued: boolean
  is_limited_edition: boolean
  production_numbers: number | null
  images: WatchImage[]
  variants: WatchVariant[]
  stories: WatchStory[]
}

export interface EncyclopediaSearchResult {
  reference: string
  brand: string
  model: string
  collection: string | null
  case_material: string | null
  dial_color: string | null
  retail_price_eur: number | null
  avg_market_price_eur: number | null
  description: string | null
  is_discontinued: boolean
}

// ── Auctions ──────────────────────────────────────────────────────────────────

export interface AuctionResult {
  id: number | null
  auction_house: string
  sale_name: string | null
  sale_location: string | null
  sale_date: string
  lot_number: string | null
  brand: string
  model: string
  reference: string | null
  description: string | null
  year_made: string | null
  condition: string | null
  estimate_low_chf: number | null
  estimate_high_chf: number | null
  hammer_price_chf: number | null
  buyer_premium_pct: number
  total_price_chf: number | null
  currency: string
  lot_url: string | null
  image_url: string | null
  notes: string | null
  is_record: boolean
  hammer_to_estimate_ratio: number | null
  estimate_midpoint_chf: number | null
}

export interface AuctionSentiment {
  reference: string
  brand: string
  calculation_date: string
  total_lots: number | null
  avg_hammer_to_estimate_ratio: number | null
  sell_through_rate: number | null
  price_trend_12m: number | null
  price_trend_36m: number | null
  sentiment_score: number | null
  sentiment_label: string | null
  notes: string | null
}

export interface UpcomingAuction {
  house: string
  sale_name: string
  location: string
  date: string
  preview_date: string | null
  url: string | null
  focus: string | null
  highlights: string[] | null
}

// ── Verification ──────────────────────────────────────────────────────────────

export interface VerificationCheck {
  check: string
  description: string
  result: 'pass' | 'fail' | 'warning' | 'unknown'
  details: string | null
}

export interface AuthenticityReport {
  brand: string
  model: string | null
  reference: string | null
  serial_number: string | null
  overall_verdict: 'authentic' | 'suspicious' | 'likely_fake' | 'inconclusive'
  confidence: number
  authenticity_score: number
  checks: VerificationCheck[]
  serial_info: {
    valid: boolean
    year_range: string | null
    production_period: string | null
    notes: string | null
  } | null
  fake_patterns_found: string[]
  recommendations: string[]
  analyzed_at: string
}
