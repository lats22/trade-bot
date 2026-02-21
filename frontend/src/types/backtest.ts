export interface BacktestRequest {
  ticker: string
  strategy_name: StrategyName
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

export type StrategyName =
  | 'vwap_ma_volume'
  | 'sma_crossover'
  | 'rsi'
  | 'macd'
  | 'bollinger_bands'

export interface StrategyInfo {
  name: StrategyName
  display_name: string
  description: string
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

// Heatmap types
export interface HeatmapPoint {
  stop_loss: number
  take_profit: number
  return_pct: number
}

export interface HeatmapResult {
  points: HeatmapPoint[]
  stop_loss_values: number[]
  take_profit_values: number[]
  best_return: number
  best_params: {
    stop_loss: number
    take_profit: number
  }
  parameters_tested: number
}

// Paper trading types
export interface PaperTradePosition {
  ticker: string
  entry_price: number
  entry_date: string
  size: number
  direction: 'long' | 'short'
  current_price: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
}

export interface PaperTradeHistoryItem {
  ticker: string
  entry_date: string
  exit_date: string
  entry_price: number
  exit_price: number
  size: number
  direction: 'long' | 'short'
  pnl: number
  pnl_percent: number
}

export interface PaperTradeResult {
  is_active: boolean
  current_position: PaperTradePosition | null
  starting_capital: number
  current_capital: number
  total_pnl: number
  total_trades: number
  win_rate: number
  history: PaperTradeHistoryItem[]
}

export interface BacktestResponse {
  request: BacktestRequest
  metrics: BacktestMetrics
  equity_curve: EquityPoint[]
  drawdown_curve: EquityPoint[]
  trades: TradeRecord[]
  monte_carlo?: MonteCarloResult
  walk_forward?: WalkForwardResult
  heatmap?: HeatmapResult
  paper_trade?: PaperTradeResult
}

export const DEFAULT_SETTINGS: BacktestRequest = {
  ticker: 'AAPL',
  strategy_name: 'vwap_ma_volume',
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

export const STRATEGIES: StrategyInfo[] = [
  {
    name: 'vwap_ma_volume',
    display_name: 'VWAP + MA + Volume',
    description: 'Combines Volume Weighted Average Price with 200-day Moving Average and volume confirmation. Best for trending markets with high liquidity.',
  },
  {
    name: 'sma_crossover',
    display_name: 'SMA Crossover',
    description: 'Classic strategy using 50/200 Simple Moving Average crossover. Buy when fast MA crosses above slow MA, sell when it crosses below.',
  },
  {
    name: 'rsi',
    display_name: 'RSI Strategy',
    description: 'Relative Strength Index momentum strategy. Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought).',
  },
  {
    name: 'macd',
    display_name: 'MACD Strategy',
    description: 'Moving Average Convergence Divergence. Trades based on MACD line crossing signal line with histogram confirmation.',
  },
  {
    name: 'bollinger_bands',
    display_name: 'Bollinger Bands',
    description: 'Mean reversion strategy using Bollinger Bands. Buy at lower band, sell at upper band, with middle band as the mean.',
  },
]
