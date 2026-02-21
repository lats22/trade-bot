import Plot from 'react-plotly.js'
import { EquityPoint, TradeRecord, MonteCarloResult, WalkForwardResult, HeatmapResult } from '../types/backtest'
import './EquityChart.css'

export type ChartTab = 'equity' | 'drawdown' | 'montecarlo' | 'walkforward' | 'heatmap'

interface EquityChartProps {
  equityCurve: EquityPoint[]
  drawdownCurve: EquityPoint[]
  trades: TradeRecord[]
  activeTab: ChartTab
  onTabChange: (tab: ChartTab) => void
  darkMode: boolean
  monteCarlo?: MonteCarloResult
  walkForward?: WalkForwardResult
  heatmap?: HeatmapResult
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
  heatmap,
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
          <button>Heatmap</button>
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

  const renderHeatmapContent = () => {
    if (!heatmap) {
      return <div className="tab-placeholder">Heatmap analysis not available. Run backtest with Heatmap enabled.</div>
    }

    // Build z-matrix for heatmap
    const stopLossValues = heatmap.stop_loss_values
    const takeProfitValues = heatmap.take_profit_values
    const zMatrix: number[][] = []

    for (let i = 0; i < stopLossValues.length; i++) {
      const row: number[] = []
      for (let j = 0; j < takeProfitValues.length; j++) {
        const point = heatmap.points.find(
          (p) => p.stop_loss === stopLossValues[i] && p.take_profit === takeProfitValues[j]
        )
        row.push(point?.return_pct ?? 0)
      }
      zMatrix.push(row)
    }

    return (
      <div className="heatmap-content">
        <div className="heatmap-stats">
          <div className="heatmap-stat">
            <span className="heatmap-label">Best Return</span>
            <span className={`heatmap-value ${heatmap.best_return >= 0 ? 'positive' : 'negative'}`}>
              {heatmap.best_return >= 0 ? '+' : ''}{heatmap.best_return.toFixed(2)}%
            </span>
          </div>
          <div className="heatmap-stat">
            <span className="heatmap-label">Best Stop Loss</span>
            <span className="heatmap-value">{heatmap.best_params.stop_loss}%</span>
          </div>
          <div className="heatmap-stat">
            <span className="heatmap-label">Best Take Profit</span>
            <span className="heatmap-value">{heatmap.best_params.take_profit}%</span>
          </div>
          <div className="heatmap-stat">
            <span className="heatmap-label">Tested</span>
            <span className="heatmap-value">{heatmap.parameters_tested} combos</span>
          </div>
        </div>

        <Plot
          data={[
            {
              z: zMatrix,
              x: takeProfitValues.map((v) => `${v}%`),
              y: stopLossValues.map((v) => `${v}%`),
              type: 'heatmap',
              colorscale: [
                [0, '#e74c3c'],
                [0.5, '#f39c12'],
                [1, '#27ae60'],
              ],
              colorbar: {
                title: { text: 'Return %' },
                ticksuffix: '%',
              },
              hovertemplate:
                'Take Profit: %{x}<br>Stop Loss: %{y}<br>Return: %{z:.2f}%<extra></extra>',
            },
          ]}
          layout={{
            autosize: true,
            margin: { l: 70, r: 20, t: 20, b: 50 },
            paper_bgcolor: colors.bg,
            plot_bgcolor: colors.bg,
            font: { color: colors.text },
            xaxis: {
              title: { text: 'Take Profit %' },
              tickangle: -45,
            },
            yaxis: {
              title: { text: 'Stop Loss %' },
            },
            annotations: [
              {
                x: `${heatmap.best_params.take_profit}%`,
                y: `${heatmap.best_params.stop_loss}%`,
                text: 'BEST',
                showarrow: true,
                arrowhead: 2,
                arrowcolor: colors.text,
                font: { color: colors.text, size: 12 },
              },
            ],
          }}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%', height: '300px' }}
        />
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

    if (activeTab === 'heatmap') {
      return renderHeatmapContent()
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
        <button
          className={activeTab === 'heatmap' ? 'active' : ''}
          onClick={() => onTabChange('heatmap')}
        >
          Heatmap
        </button>
      </div>
      {renderChartContent()}
    </div>
  )
}
