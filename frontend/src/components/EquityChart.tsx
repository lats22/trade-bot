import Plot from 'react-plotly.js'
import { EquityPoint, TradeRecord, MonteCarloResult, WalkForwardResult } from '../types/backtest'
import './EquityChart.css'

type ChartTab = 'equity' | 'drawdown' | 'montecarlo' | 'walkforward'

interface EquityChartProps {
  equityCurve: EquityPoint[]
  drawdownCurve: EquityPoint[]
  trades: TradeRecord[]
  activeTab: ChartTab
  onTabChange: (tab: ChartTab) => void
  darkMode: boolean
  monteCarlo?: MonteCarloResult
  walkForward?: WalkForwardResult
}

export function EquityChart({
  equityCurve,
  drawdownCurve,
  trades,
  activeTab,
  onTabChange,
  darkMode,
  monteCarlo,
  walkForward,
}: EquityChartProps) {
  const colors = {
    bg: darkMode ? '#1e1e1e' : '#ffffff',
    text: darkMode ? '#e0e0e0' : '#2c3e50',
    grid: darkMode ? '#3d3d3d' : '#dee2e6',
    line: darkMode ? '#58a6ff' : '#3498db',
    profit: '#27ae60',
    loss: '#e74c3c',
  }

  const isEmpty = equityCurve.length === 0

  if (isEmpty) {
    return (
      <div className="equity-chart empty">
        <div className="chart-tabs">
          <button className="active">Equity</button>
          <button>Drawdown</button>
          <button>Monte Carlo</button>
          <button>Walk-Forward</button>
        </div>
        <div className="empty-message">Run a backtest to see charts</div>
      </div>
    )
  }

  const data = activeTab === 'equity' ? equityCurve : drawdownCurve
  const x = data.map((p) => p.datetime)
  const y = data.map((p) => p.equity)

  // Add trade markers for equity chart
  const buyMarkers = trades.map((t) => ({
    x: t.entry_date,
    y: equityCurve.find((p) => p.datetime >= t.entry_date)?.equity || 0,
  }))

  const sellMarkers = trades.map((t) => ({
    x: t.exit_date,
    y: equityCurve.find((p) => p.datetime >= t.exit_date)?.equity || 0,
    profit: t.pnl > 0,
  }))

  const renderMonteCarloContent = () => {
    if (!monteCarlo) {
      return <div className="tab-placeholder">Monte Carlo simulation not available. Run backtest with Monte Carlo enabled.</div>
    }

    return (
      <div className="monte-carlo-content">
        <div className="mc-header">
          <span className="mc-simulations">{monteCarlo.simulations.toLocaleString()} Simulations</span>
        </div>

        <div className="mc-stats-grid">
          <div className="mc-stat">
            <span className="mc-label">Median Return</span>
            <span className={`mc-value ${monteCarlo.median_return >= 0 ? 'positive' : 'negative'}`}>
              {monteCarlo.median_return >= 0 ? '+' : ''}{monteCarlo.median_return.toFixed(2)}%
            </span>
          </div>
          <div className="mc-stat">
            <span className="mc-label">Best Case</span>
            <span className="mc-value positive">+{monteCarlo.best_return.toFixed(2)}%</span>
          </div>
          <div className="mc-stat">
            <span className="mc-label">Worst Case</span>
            <span className="mc-value negative">{monteCarlo.worst_return.toFixed(2)}%</span>
          </div>
          <div className="mc-stat">
            <span className="mc-label">Median Max DD</span>
            <span className="mc-value negative">{monteCarlo.median_max_drawdown.toFixed(2)}%</span>
          </div>
        </div>

        <div className="mc-range">
          <div className="mc-range-header">
            <span>90% Confidence Range</span>
          </div>
          <div className="mc-range-bar">
            <div className="mc-range-fill" style={{
              left: `${Math.max(0, (monteCarlo.percentile_5 - monteCarlo.worst_return) / (monteCarlo.best_return - monteCarlo.worst_return) * 100)}%`,
              right: `${Math.max(0, 100 - (monteCarlo.percentile_95 - monteCarlo.worst_return) / (monteCarlo.best_return - monteCarlo.worst_return) * 100)}%`
            }}></div>
            <div className="mc-range-median" style={{
              left: `${(monteCarlo.median_return - monteCarlo.worst_return) / (monteCarlo.best_return - monteCarlo.worst_return) * 100}%`
            }}></div>
          </div>
          <div className="mc-range-labels">
            <span className="mc-range-label">{monteCarlo.percentile_5.toFixed(1)}% (5th)</span>
            <span className="mc-range-label">{monteCarlo.percentile_95.toFixed(1)}% (95th)</span>
          </div>
        </div>

        <div className="mc-worst-dd">
          <span className="mc-label">Worst Max Drawdown (across all simulations)</span>
          <span className="mc-value negative">{monteCarlo.worst_max_drawdown.toFixed(2)}%</span>
        </div>
      </div>
    )
  }

  const renderWalkForwardContent = () => {
    if (!walkForward) {
      return <div className="tab-placeholder">Walk-Forward analysis not available. Run backtest with Walk-Forward enabled.</div>
    }

    return (
      <div className="walk-forward-content">
        <div className="wf-summary">
          <div className="wf-stat">
            <span className="wf-label">Overall Consistency</span>
            <span className={`wf-value ${walkForward.overall_consistency >= 50 ? 'positive' : 'negative'}`}>
              {walkForward.overall_consistency.toFixed(1)}%
            </span>
          </div>
          <div className="wf-stat">
            <span className="wf-label">Average Return</span>
            <span className={`wf-value ${walkForward.avg_return >= 0 ? 'positive' : 'negative'}`}>
              {walkForward.avg_return >= 0 ? '+' : ''}{walkForward.avg_return.toFixed(2)}%
            </span>
          </div>
          <div className="wf-stat">
            <span className="wf-label">Profitable Windows</span>
            <span className="wf-value">
              {walkForward.profitable_windows}/{walkForward.num_windows}
            </span>
          </div>
        </div>

        <div className="wf-table-wrapper">
          <table className="wf-table">
            <thead>
              <tr>
                <th>Window</th>
                <th>Date Range</th>
                <th>Return %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {walkForward.windows.map((w) => (
                <tr key={w.window}>
                  <td>{w.window}</td>
                  <td>{w.start_date} - {w.end_date}</td>
                  <td className={w.return_pct >= 0 ? 'positive' : 'negative'}>
                    {w.return_pct >= 0 ? '+' : ''}{w.return_pct.toFixed(2)}%
                  </td>
                  <td className={w.profitable ? 'status-profit' : 'status-loss'}>
                    {w.profitable ? '✓' : '✗'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  const renderChartContent = () => {
    if (activeTab === 'montecarlo') {
      return renderMonteCarloContent()
    }

    if (activeTab === 'walkforward') {
      return renderWalkForwardContent()
    }

    return (
      <Plot
        data={[
          {
            x,
            y,
            type: 'scatter',
            mode: 'lines',
            line: { color: colors.line, width: 2 },
            name: activeTab === 'equity' ? 'Equity' : 'Drawdown',
          },
          ...(activeTab === 'equity'
            ? [
                {
                  x: buyMarkers.map((m) => m.x),
                  y: buyMarkers.map((m) => m.y),
                  type: 'scatter' as const,
                  mode: 'markers' as const,
                  marker: { color: colors.profit, size: 10, symbol: 'triangle-up' },
                  name: 'Buy',
                },
                {
                  x: sellMarkers.map((m) => m.x),
                  y: sellMarkers.map((m) => m.y),
                  type: 'scatter' as const,
                  mode: 'markers' as const,
                  marker: {
                    color: sellMarkers.map((m) => (m.profit ? colors.profit : colors.loss)),
                    size: 10,
                    symbol: 'triangle-down',
                  },
                  name: 'Sell',
                },
              ]
            : []),
        ]}
        layout={{
          autosize: true,
          margin: { l: 60, r: 20, t: 20, b: 40 },
          paper_bgcolor: colors.bg,
          plot_bgcolor: colors.bg,
          font: { color: colors.text },
          xaxis: {
            gridcolor: colors.grid,
            tickformat: '%b %d',
          },
          yaxis: {
            gridcolor: colors.grid,
            tickprefix: activeTab === 'equity' ? '$' : '',
            ticksuffix: activeTab === 'drawdown' ? '%' : '',
          },
          showlegend: false,
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%', height: '300px' }}
      />
    )
  }

  return (
    <div className="equity-chart">
      <div className="chart-tabs">
        <button
          className={activeTab === 'equity' ? 'active' : ''}
          onClick={() => onTabChange('equity')}
        >
          Equity
        </button>
        <button
          className={activeTab === 'drawdown' ? 'active' : ''}
          onClick={() => onTabChange('drawdown')}
        >
          Drawdown
        </button>
        <button
          className={activeTab === 'montecarlo' ? 'active' : ''}
          onClick={() => onTabChange('montecarlo')}
        >
          Monte Carlo
        </button>
        <button
          className={activeTab === 'walkforward' ? 'active' : ''}
          onClick={() => onTabChange('walkforward')}
        >
          Walk-Forward
        </button>
      </div>
      {renderChartContent()}
    </div>
  )
}
