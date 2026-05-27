/**
 * Currency utilities — WatchScanner
 *
 * Prices are stored in CHF in the backend DB.
 * The scrapers used FX_TO_CHF["EUR"] = 0.95, meaning:
 *   price_EUR × 0.95 = price_CHF
 *   price_CHF ÷ 0.95 = price_EUR
 */

const CHF_TO_EUR = 1 / 0.95 // ≈ 1.0526

export function chfToEur(chf: number): number {
  return chf * CHF_TO_EUR
}

/** Format CHF value as EUR string — "€ 10.953" */
export function fmtEur(chf: number | null | undefined): string {
  if (chf == null || isNaN(chf) || chf === 0) return '—'
  const eur = Math.round(chf * CHF_TO_EUR)
  return `€ ${eur.toLocaleString('it-IT')}`
}

/** Compact format — "€ 11K", "€ 1.2M" */
export function fmtEurCompact(chf: number | null | undefined): string {
  if (chf == null || isNaN(chf) || chf === 0) return '—'
  const eur = chf * CHF_TO_EUR
  if (eur >= 1_000_000) return `€ ${(eur / 1_000_000).toFixed(2)}M`
  if (eur >= 1_000) return `€ ${Math.round(eur / 1_000)}K`
  return `€ ${Math.round(eur).toLocaleString('it-IT')}`
}

/** Range — "€ 8.000 – € 12.000" */
export function fmtEurRange(
  low: number | null | undefined,
  high: number | null | undefined,
): string {
  if (!low && !high) return '—'
  const lo = Math.round((low ?? 0) * CHF_TO_EUR).toLocaleString('it-IT')
  const hi = Math.round((high ?? 0) * CHF_TO_EUR).toLocaleString('it-IT')
  return `€ ${lo} – € ${hi}`
}

/** Raw EUR number (for CountUp etc.) */
export function toEur(chf: number | null | undefined): number {
  if (chf == null || isNaN(chf)) return 0
  return Math.round(chf * CHF_TO_EUR)
}
