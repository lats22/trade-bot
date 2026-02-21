import { useState, useEffect, useCallback } from 'react'
import { PaperTradeResult, BacktestRequest } from '../types/backtest'
import { startPaperTrade, stopPaperTrade, getPaperTradeStatus } from '../services/api'
import './PaperTrading.css'

interface PaperTradingProps {
  settings: BacktestRequest
  darkMode: boolean
}

export function PaperTrading({ settings, darkMode }: PaperTradingProps) {
  const [paperTrade, setPaperTrade] = useState<PaperTradeResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isCollapsed, setIsCollapsed] = useState(false)

  const fetchStatus = useCallback(async () => {
    try {
      const status = await getPaperTradeStatus()
      setPaperTrade(status)
    } catch {
      // Paper trading not active
      setPaperTrade(null)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    // Refresh status every 30 seconds when active
    const interval = setInterval(() => {
      if (paperTrade?.is_active) {
        fetchStatus()
      }
    }, 30000)
    return () => clearInterval(interval)
  }, [fetchStatus, paperTrade?.is_active])

  const handleStart = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await startPaperTrade(settings)
      setPaperTrade(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start paper trading')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStop = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await stopPaperTrade()
      setPaperTrade(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop paper trading')
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  return (
    <div className={`paper-trading ${darkMode ? 'dark' : ''}`}>
      <div className="paper-trading-header" onClick={() => setIsCollapsed(!isCollapsed)}>
        <h3>
          Paper Trading
          {paperTrade?.is_active && <span className="status-badge active">ACTIVE</span>}
        </h3>
        <button className="collapse-btn">{isCollapsed ? '+' : '-'}</button>
      </div>

      {error && (
        <div className="paper-trading-error">
          {error}
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {!isCollapsed && (
        <div className="paper-trading-content">
          {/* Controls */}
          <div className="paper-trading-controls">
            {!paperTrade?.is_active ? (
              <button
                className="start-btn"
                onClick={handleStart}
                disabled={isLoading}
              >
                {isLoading ? 'Starting...' : 'Start Paper Trading'}
              </button>
            ) : (
              <button
                className="stop-btn"
                onClick={handleStop}
                disabled={isLoading}
              >
                {isLoading ? 'Stopping...' : 'Stop Paper Trading'}
              </button>
            )}
            <button
              className="refresh-btn"
              onClick={fetchStatus}
              disabled={isLoading}
              title="Refresh status"
            >
              Refresh
            </button>
          </div>

          {/* Current Position */}
          {paperTrade?.current_position && (
            <div className="current-position">
              <h4>Current Position</h4>
              <div className="position-details">
                <div className="position-row">
                  <span className="position-label">Ticker</span>
                  <span className="position-value">{paperTrade.current_position.ticker}</span>
                </div>
                <div className="position-row">
                  <span className="position-label">Direction</span>
                  <span className={`position-value direction-${paperTrade.current_position.direction}`}>
                    {paperTrade.current_position.direction.toUpperCase()}
                  </span>
                </div>
                <div className="position-row">
                  <span className="position-label">Entry Price</span>
                  <span className="position-value">
                    {formatCurrency(paperTrade.current_position.entry_price)}
                  </span>
                </div>
                <div className="position-row">
                  <span className="position-label">Current Price</span>
                  <span className="position-value">
                    {formatCurrency(paperTrade.current_position.current_price)}
                  </span>
                </div>
                <div className="position-row">
                  <span className="position-label">Size</span>
                  <span className="position-value">{paperTrade.current_position.size} shares</span>
                </div>
                <div className="position-row">
                  <span className="position-label">Unrealized P&L</span>
                  <span className={`position-value ${paperTrade.current_position.unrealized_pnl >= 0 ? 'positive' : 'negative'}`}>
                    {formatCurrency(paperTrade.current_position.unrealized_pnl)}
                    ({formatPercent(paperTrade.current_position.unrealized_pnl_percent)})
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Account Summary */}
          {paperTrade && (
            <div className="account-summary">
              <h4>Account Summary</h4>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Starting Capital</span>
                  <span className="summary-value">{formatCurrency(paperTrade.starting_capital)}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Current Capital</span>
                  <span className="summary-value">{formatCurrency(paperTrade.current_capital)}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total P&L</span>
                  <span className={`summary-value ${paperTrade.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                    {formatCurrency(paperTrade.total_pnl)}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Total Trades</span>
                  <span className="summary-value">{paperTrade.total_trades}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Win Rate</span>
                  <span className="summary-value">{paperTrade.win_rate.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}

          {/* Trade History */}
          {paperTrade && paperTrade.history.length > 0 && (
            <div className="trade-history">
              <h4>Trade History</h4>
              <div className="history-table-wrapper">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Ticker</th>
                      <th>Direction</th>
                      <th>Entry</th>
                      <th>Exit</th>
                      <th>P&L</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paperTrade.history.slice().reverse().map((trade, index) => (
                      <tr key={index}>
                        <td>{trade.ticker}</td>
                        <td className={`direction-${trade.direction}`}>
                          {trade.direction.toUpperCase()}
                        </td>
                        <td>
                          {formatCurrency(trade.entry_price)}
                          <span className="trade-date">{trade.entry_date}</span>
                        </td>
                        <td>
                          {formatCurrency(trade.exit_price)}
                          <span className="trade-date">{trade.exit_date}</span>
                        </td>
                        <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                          {formatCurrency(trade.pnl)}
                          <span className="trade-percent">({formatPercent(trade.pnl_percent)})</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* No Data */}
          {!paperTrade && !error && (
            <div className="paper-trading-empty">
              Start paper trading to simulate real-time trading without risking real money.
              Uses the current strategy settings to generate signals.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
