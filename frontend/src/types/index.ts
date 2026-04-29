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
