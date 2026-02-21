export interface BacktestRequest {
  ticker: string
  strategy_direction: 'long' | 'short' | 'both'
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

export interface MonteCarloResult {
  simulations: number
  median_return: number
  best_return: number
  worst_return: number
  percentile_5: number
  percentile_95: number
  median_max_drawdown: number
  worst_max_drawdown: number
  return_distribution: {
    values: number[]
    labels: string[]
  }
}

export interface WalkForwardWindow {
  window: number
  start_date: string
  end_date: string
  train_size: number
  test_size: number
  return_pct: number
  profitable: boolean
}

export interface WalkForwardResult {
  num_windows: number
  windows: WalkForwardWindow[]
  overall_consistency: number
  avg_return: number
  profitable_windows: number
}

export interface BacktestResponse {
  request: BacktestRequest
  metrics: BacktestMetrics
  equity_curve: EquityPoint[]
  drawdown_curve: EquityPoint[]
  trades: TradeRecord[]
  monte_carlo?: MonteCarloResult
  walk_forward?: WalkForwardResult
}

export const DEFAULT_SETTINGS: BacktestRequest = {
  ticker: 'AAPL',
  strategy_direction: 'long',
  timeframe: 'daily',
  start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
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
