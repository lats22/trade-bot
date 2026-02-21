import { BacktestMetrics } from '../types/backtest'
import { Tooltip } from './Tooltip'
import './MetricsCard.css'

interface MetricsCardProps {
  metrics: BacktestMetrics | null
}

const METRIC_TOOLTIPS = {
  return: 'Total Return: Overall percentage gain or loss on your starting capital. Positive = profit, negative = loss.',
  winRate: 'Win Rate: Percentage of trades that were profitable. 50%+ is generally good, but depends on your risk/reward ratio.',
  maxDrawdown: 'Maximum Drawdown: Largest peak-to-trough decline in portfolio value. Shows worst-case scenario you would have experienced.',
  sharpe: 'Sharpe Ratio: Risk-adjusted return measure. Higher = better. Above 1.0 is good, above 2.0 is excellent. Negative means you lost money.',
  trades: 'Total Trades: Number of completed round-trip trades (buy + sell). More trades = more data points for statistical significance.',
  profitFactor: 'Profit Factor: Gross profits divided by gross losses. Above 1.0 = profitable. 1.5+ is good, 2.0+ is excellent.',
  riskReward: 'Risk/Reward Ratio: Average winning trade divided by average losing trade. Higher = better. 2:1 means wins are twice as large as losses.',
  bestStreak: 'Best Streak: Longest consecutive winning trades. Shows your best run of successful trades.',
  worstStreak: 'Worst Streak: Longest consecutive losing trades. Shows the maximum number of losses in a row you experienced.',
}

export function MetricsCard({ metrics }: MetricsCardProps) {
  if (!metrics) {
    return (
      <div className="metrics-card empty">
        <p>Run a backtest to see metrics</p>
      </div>
    )
  }

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }

  const getColorClass = (value: number, inverse = false) => {
    if (inverse) {
      return value < 0 ? 'positive' : value > 0 ? 'negative' : ''
    }
    return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
  }

  return (
    <div className="metrics-card">
      <h3>Performance Metrics</h3>
      <div className="metrics-grid">
        <div className="metric">
          <span className="metric-label">
            Return
            <Tooltip text={METRIC_TOOLTIPS.return} />
          </span>
          <span className={`metric-value ${getColorClass(metrics.total_return)}`}>
            {formatPercent(metrics.total_return)}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Win Rate
            <Tooltip text={METRIC_TOOLTIPS.winRate} />
          </span>
          <span className="metric-value">{metrics.win_rate.toFixed(1)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Max DD
            <Tooltip text={METRIC_TOOLTIPS.maxDrawdown} />
          </span>
          <span className={`metric-value ${getColorClass(metrics.max_drawdown, true)}`}>
            {formatPercent(metrics.max_drawdown)}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Sharpe
            <Tooltip text={METRIC_TOOLTIPS.sharpe} />
          </span>
          <span className="metric-value">{metrics.sharpe_ratio.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Trades
            <Tooltip text={METRIC_TOOLTIPS.trades} />
          </span>
          <span className="metric-value">{metrics.total_trades}</span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Profit Factor
            <Tooltip text={METRIC_TOOLTIPS.profitFactor} />
          </span>
          <span className="metric-value">{metrics.profit_factor.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">
            R:R Ratio
            <Tooltip text={METRIC_TOOLTIPS.riskReward} />
          </span>
          <span className="metric-value">{metrics.risk_reward_ratio.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Best Streak
            <Tooltip text={METRIC_TOOLTIPS.bestStreak} />
          </span>
          <span className="metric-value positive">{metrics.best_streak}W</span>
        </div>
        <div className="metric">
          <span className="metric-label">
            Worst Streak
            <Tooltip text={METRIC_TOOLTIPS.worstStreak} />
          </span>
          <span className="metric-value negative">{metrics.worst_streak}L</span>
        </div>
      </div>
    </div>
  )
}
