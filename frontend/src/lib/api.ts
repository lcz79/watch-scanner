import axios from 'axios'
import type {
  WatchQuery, ScanResult, AgentStatus, AlertConfig, Alert,
  AnalysisResult, MarketStats, PriceSnapshot, ScoredListing, Recommendation,
  EncyclopediaWatch, EncyclopediaSearchResult,
  AuctionResult, AuctionSentiment, UpcomingAuction,
  AuthenticityReport,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,  // 2 minuti — la scan reale prende 40-60s
})

export const scanWatch = (query: WatchQuery): Promise<ScanResult> =>
  api.post('/scan', query).then(r => r.data)

export const getAgentsStatus = (): Promise<AgentStatus[]> =>
  api.get('/agents/status').then(r => r.data)

export const createAlert = (config: AlertConfig): Promise<Alert> =>
  api.post('/alerts', config).then(r => r.data)

export const getAlerts = (): Promise<Alert[]> =>
  api.get('/alerts').then(r => r.data)

export const deleteAlert = (alertId: string): Promise<void> =>
  api.delete(`/alerts/${alertId}`).then(r => r.data)

export const analyzeReference = (reference: string) =>
  api.post<AnalysisResult>(`/analyze/${reference}`).then(r => r.data)

export const getMarketStats = (reference: string) =>
  api.get<MarketStats>(`/market/${reference}`).then(r => r.data)

export const getPriceHistory = (reference: string, days = 30) =>
  api.get<{ snapshots: PriceSnapshot[] }>(`/price-history/${reference}`, { params: { days } })
    .then(r => r.data.snapshots ?? [])

export const getBestDeals = (minDiscount = 0.05) =>
  api.get<ScoredListing[]>('/best-deals', { params: { min_discount: minDiscount } }).then(r => r.data)

export const getRecommendations = () =>
  api.get<{ recommendations: Recommendation[] }>('/recommendations')
    .then(r => r.data.recommendations ?? [])

export const identifyWatchFromImage = async (file: File): Promise<{
  identified: boolean
  brand: string | null
  model: string | null
  reference: string | null
  year_estimate: string | null
  confidence: number
  notes: string | null
}> => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await axios.post('/api/identify', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  })
  return response.data
}

export interface CatalogWatch {
  id: string
  brand: string
  model: string
  reference: string
  canonical_name: string
  year_range: string
  movement?: string
  case_size?: string
  image_url: string
  tags: string[]
  avg_price_eur: number
}

export const getCatalog = (params?: { brand?: string; search?: string }) =>
  api.get<{ watches: CatalogWatch[]; total: number; brands: string[] }>('/catalog', { params })
    .then(r => r.data)

// ── Encyclopedia ──────────────────────────────────────────────────────────────

export const searchEncyclopedia = (params: { brand?: string; model?: string; reference?: string; collection?: string; limit?: number }) =>
  api.get<{ watches: EncyclopediaSearchResult[]; total: number; brands: string[] }>('/encyclopedia/search', { params })
    .then(r => r.data)

export const getEncyclopediaWatch = (reference: string) =>
  api.get<EncyclopediaWatch>(`/encyclopedia/reference/${encodeURIComponent(reference)}`).then(r => r.data)

export const getEncyclopediaBrand = (brand: string) =>
  api.get<{ brand: string; watches: EncyclopediaSearchResult[]; total: number }>(`/encyclopedia/brand/${encodeURIComponent(brand)}`).then(r => r.data)

export const getEncyclopediaPopular = (limit = 20) =>
  api.get<EncyclopediaSearchResult[]>('/encyclopedia/popular', { params: { limit } }).then(r => r.data)

// ── Auctions ──────────────────────────────────────────────────────────────────

export const getAuctionResults = (reference: string, params?: { limit?: number; auction_house?: string }) =>
  api.get<{ reference: string; results: AuctionResult[]; total: number; record?: AuctionResult }>(
    `/auctions/results/${encodeURIComponent(reference)}`, { params }
  ).then(r => r.data)

export const getAuctionSentiment = (reference: string) =>
  api.get<AuctionSentiment>(`/auctions/sentiment/${encodeURIComponent(reference)}`).then(r => r.data)

export const getAuctionRecords = (params?: { limit?: number; brand?: string }) =>
  api.get<AuctionResult[]>('/auctions/records', { params }).then(r => r.data)

export const getAuctionCalendar = () =>
  api.get<UpcomingAuction[]>('/auctions/calendar').then(r => r.data)

// ── Verification ──────────────────────────────────────────────────────────────

export const verifyWatch = async (data: {
  brand: string
  model: string
  reference?: string
  serial_number?: string
  image?: File
}): Promise<Record<string, unknown>> => {
  const params: Record<string, string> = { brand: data.brand, model: data.model }
  if (data.reference) params.reference = data.reference
  if (data.serial_number) params.serial_number = data.serial_number

  const formData = new FormData()
  if (data.image) formData.append('image', data.image)

  const response = await axios.post('/api/verify/analyze', data.image ? formData : null, {
    params,
    headers: data.image ? { 'Content-Type': 'multipart/form-data' } : {},
    timeout: 30000,
  })
  return response.data
}

export const validateSerial = (brand: string, serial: string) =>
  api.get<{
    brand: string
    serial: string
    is_valid_format: boolean
    plausible: boolean
    estimated_year: number | null
    year_range: [number, number] | null
    notes: string
    warnings: string[]
  }>(`/verify/serial/${encodeURIComponent(brand)}`, { params: { serial } }).then(r => r.data)

export const getAuthRules = (brand: string, model: string) =>
  api.get<{
    brand: string
    model: string
    references: string[]
    total_checks: number
    critical_checks: number
    checklist: unknown[]
    serial_ranges: Record<string, unknown>
  }>(`/verify/rules/${encodeURIComponent(brand)}/${encodeURIComponent(model)}`).then(r => r.data)

export const getKnownFakes = (brand: string, model?: string) =>
  api.get<{ brand: string; model: string | null; total_patterns: number; risk_summary: unknown; patterns: unknown[] }>(
    `/verify/known-fakes/${encodeURIComponent(brand)}`,
    model ? { params: { model } } : undefined
  ).then(r => r.data)

export const getAuctionStats = () =>
  api.get<{ total_lots_in_db: number; auction_houses: number; houses_breakdown: unknown[] }>('/auctions/stats')
    .then(r => r.data)
