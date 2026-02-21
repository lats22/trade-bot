import {
  BacktestRequest,
  BacktestResponse,
  HeatmapResult,
  PaperTradeResult,
  StrategyInfo,
} from '../types/backtest'

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

export async function runHeatmap(request: BacktestRequest): Promise<HeatmapResult> {
  const response = await fetch(`${API_BASE}/backtest/heatmap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Heatmap analysis failed')
  }

  return response.json()
}

export async function startPaperTrade(request: BacktestRequest): Promise<PaperTradeResult> {
  const response = await fetch(`${API_BASE}/paper-trade/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to start paper trading')
  }

  return response.json()
}

export async function stopPaperTrade(): Promise<PaperTradeResult> {
  const response = await fetch(`${API_BASE}/paper-trade/stop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to stop paper trading')
  }

  return response.json()
}

export async function getPaperTradeStatus(): Promise<PaperTradeResult> {
  const response = await fetch(`${API_BASE}/paper-trade/status`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get paper trade status')
  }

  return response.json()
}

export async function getStrategies(): Promise<StrategyInfo[]> {
  const response = await fetch(`${API_BASE}/strategies`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get strategies')
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
