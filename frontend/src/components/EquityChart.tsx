import Plot from 'react-plotly.js'
import { EquityPoint, TradeRecord } from '../types/backtest'
import './EquityChart.css'

interface EquityChartProps {
  equityCurve: EquityPoint[]
  drawdownCurve: EquityPoint[]
  trades: TradeRecord[]
  activeTab: 'equity' | 'drawdown'
  onTabChange: (tab: 'equity' | 'drawdown') => void
  darkMode: boolean
}

export function EquityChart({
  equityCurve,
  drawdownCurve,
  trades,
  activeTab,
  onTabChange,
  darkMode,
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
      </div>
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
    </div>
  )
}
