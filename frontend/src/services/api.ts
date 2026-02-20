import { BacktestRequest, BacktestResponse, Ticker } from '../types/backtest'

const API_BASE = '/api'

export async function runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
  const response = await fetch(`${API_BASE}/backtest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Backtest failed')
  }

  return response.json()
}

export async function getTickers(): Promise<{ popular: Ticker[] }> {
  const response = await fetch(`${API_BASE}/tickers`)

  if (!response.ok) {
    throw new Error('Failed to fetch tickers')
  }

  return response.json()
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`)
    return response.ok
  } catch {
    return false
  }
}
