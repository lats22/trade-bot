export interface BacktestRequest {
  ticker: string
  timeframe: string
  start_date: string
  end_date: string
  risk_per_trade: number
  stop_loss: number
  take_profit: number
  position_type: 'fixed' | 'percent'
  lot_size: number
  percent_capital: number
  starting_capital: number
  slippage: number
  commission: number
}

export interface TradeRecord {
  entry_date: string
  exit_date: string
  entry_price: number
  exit_price: number
  size: number
  pnl: number
  pnl_percent: number
  trade_type: string
}

export interface BacktestMetrics {
  total_return: number
  win_rate: number
  max_drawdown: number
  sharpe_ratio: number
  total_trades: number
  profit_factor: number
  risk_reward_ratio: number
  best_streak: number
  worst_streak: number
}

export interface EquityPoint {
  datetime: string
  equity: number
}

export interface BacktestResponse {
  request: BacktestRequest
  metrics: BacktestMetrics
  equity_curve: EquityPoint[]
  drawdown_curve: EquityPoint[]
  trades: TradeRecord[]
}

export interface Ticker {
  symbol: string
  name: string
}

export const DEFAULT_SETTINGS: BacktestRequest = {
  ticker: 'AAPL',
  timeframe: '60min',
  start_date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0],
  risk_per_trade: 2,
  stop_loss: 2,
  take_profit: 4,
  position_type: 'percent',
  lot_size: 50,
  percent_capital: 10,
  starting_capital: 10000,
  slippage: 0.1,
  commission: 1,
}
