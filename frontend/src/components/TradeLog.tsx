import { TradeRecord } from '../types/backtest'
import './TradeLog.css'

interface TradeLogProps {
  trades: TradeRecord[]
  onExportCSV: () => void
}

export function TradeLog({ trades, onExportCSV }: TradeLogProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const formatCurrency = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}$${Math.abs(value).toFixed(0)}`
  }

  if (trades.length === 0) {
    return (
      <div className="trade-log empty">
        <div className="trade-log-header">
          <h3>Trade Log</h3>
          <button disabled>Export CSV</button>
        </div>
        <p className="empty-message">No trades to display</p>
      </div>
    )
  }

  return (
    <div className="trade-log">
      <div className="trade-log-header">
        <h3>Trade Log ({trades.length} trades)</h3>
        <button onClick={onExportCSV}>Export CSV</button>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>P&L</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, index) => (
              <tr key={index}>
                <td>{formatDate(trade.entry_date)}</td>
                <td className="trade-type">{trade.trade_type}</td>
                <td>${trade.entry_price.toFixed(2)}</td>
                <td>${trade.exit_price.toFixed(2)}</td>
                <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                  {formatCurrency(trade.pnl)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
