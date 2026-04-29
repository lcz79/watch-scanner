import axios from 'axios'
import type {
  WatchQuery, ScanResult, AgentStatus, AlertConfig, Alert,
  AnalysisResult, MarketStats, PriceSnapshot, ScoredListing, Recommendation,
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
