import { useState, useEffect } from 'react'
import { SettingsCard } from './components/SettingsCard'
import { MetricsCard } from './components/MetricsCard'
import { EquityChart } from './components/EquityChart'
import { TradeLog } from './components/TradeLog'
import { runBacktest } from './services/api'
import { BacktestRequest, BacktestResponse, DEFAULT_SETTINGS } from './types/backtest'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })
  const [settings, setSettings] = useState<BacktestRequest>(DEFAULT_SETTINGS)
  const [result, setResult] = useState<BacktestResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [chartTab, setChartTab] = useState<'equity' | 'drawdown' | 'montecarlo' | 'walkforward'>('equity')

  useEffect(() => {
    const root = document.documentElement
    if (darkMode) {
      root.classList.add('dark-mode')
      root.classList.remove('light-mode')
    } else {
      root.classList.add('light-mode')
      root.classList.remove('dark-mode')
    }
    localStorage.setItem('theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const handleRunBacktest = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await runBacktest(settings)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Backtest failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExportCSV = () => {
    if (!result) return

    const headers = ['Date', 'Type', 'Entry Price', 'Exit Price', 'Size', 'P&L', 'P&L %']
    const rows = result.trades.map((t) => [
      t.entry_date,
      t.trade_type,
      t.entry_price.toFixed(2),
      t.exit_price.toFixed(2),
      t.size,
      t.pnl.toFixed(2),
      t.pnl_percent.toFixed(2),
    ])

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${settings.ticker}_trades_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Trade_Bot</h1>
        <div className="header-actions">
          <button
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle dark mode"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <main className="dashboard">
        <aside className="sidebar">
          <SettingsCard
            settings={settings}
            onSettingsChange={setSettings}
            onRunBacktest={handleRunBacktest}
            isLoading={isLoading}
          />
        </aside>

        <section className="content">
          <MetricsCard metrics={result?.metrics || null} ticker={result ? settings.ticker : undefined} />

          <EquityChart
            equityCurve={result?.equity_curve || []}
            drawdownCurve={result?.drawdown_curve || []}
            trades={result?.trades || []}
            activeTab={chartTab}
            onTabChange={setChartTab}
            darkMode={darkMode}
            monteCarlo={result?.monte_carlo}
            walkForward={result?.walk_forward}
          />

          <TradeLog
            trades={result?.trades || []}
            onExportCSV={handleExportCSV}
          />
        </section>
      </main>
    </div>
  )
}

export default App
