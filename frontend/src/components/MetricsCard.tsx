import { BacktestMetrics } from '../types/backtest'
import './MetricsCard.css'

interface MetricsCardProps {
  metrics: BacktestMetrics | null
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
          <span className="metric-label">Return</span>
          <span className={`metric-value ${getColorClass(metrics.total_return)}`}>
            {formatPercent(metrics.total_return)}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Win Rate</span>
          <span className="metric-value">{metrics.win_rate.toFixed(1)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Max DD</span>
          <span className={`metric-value ${getColorClass(metrics.max_drawdown, true)}`}>
            {formatPercent(metrics.max_drawdown)}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Sharpe</span>
          <span className="metric-value">{metrics.sharpe_ratio.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Trades</span>
          <span className="metric-value">{metrics.total_trades}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Profit Factor</span>
          <span className="metric-value">{metrics.profit_factor.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">R:R Ratio</span>
          <span className="metric-value">{metrics.risk_reward_ratio.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Best Streak</span>
          <span className="metric-value positive">{metrics.best_streak}W</span>
        </div>
        <div className="metric">
          <span className="metric-label">Worst Streak</span>
          <span className="metric-value negative">{metrics.worst_streak}L</span>
        </div>
      </div>
    </div>
  )
}
