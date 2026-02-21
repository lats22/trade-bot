import { TradeRecord } from '../types/backtest'
import { Tooltip } from './Tooltip'
import './TradeLog.css'

interface TradeLogProps {
  trades: TradeRecord[]
  onExportCSV: () => void
}

const COLUMN_TOOLTIPS = {
  date: 'Entry date when the position was opened.',
  type: 'LONG: bought stock expecting price to rise. SHORT: sold stock expecting price to fall.',
  entry: 'Price at which the position was opened.',
  exit: 'Price at which the position was closed.',
  pnl: 'Profit or Loss from this trade. Green = profit, Red = loss.',
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
          <h3>Trade Log <Tooltip text="Complete list of all trades executed during the backtest. Export to CSV for analysis in Excel or TradingView." /></h3>
          <button disabled>Export CSV</button>
        </div>
        <p className="empty-message">No trades to display. Run a backtest to see results.</p>
      </div>
    )
  }

  return (
    <div className="trade-log">
      <div className="trade-log-header">
        <h3>Trade Log ({trades.length} trades) <Tooltip text="Complete list of all trades executed during the backtest. Export to CSV for analysis in Excel or TradingView." /></h3>
        <button onClick={onExportCSV}>Export CSV</button>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date <Tooltip text={COLUMN_TOOLTIPS.date} /></th>
              <th>Type <Tooltip text={COLUMN_TOOLTIPS.type} /></th>
              <th>Entry <Tooltip text={COLUMN_TOOLTIPS.entry} /></th>
              <th>Exit <Tooltip text={COLUMN_TOOLTIPS.exit} /></th>
              <th>P&L <Tooltip text={COLUMN_TOOLTIPS.pnl} /></th>
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
