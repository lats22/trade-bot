import { useState } from 'react'
import { BacktestRequest } from '../types/backtest'
import { Tooltip } from './Tooltip'
import { StockSelector } from './StockSelector'
import './SettingsCard.css'

interface SettingsCardProps {
  settings: BacktestRequest
  onSettingsChange: (settings: BacktestRequest) => void
  onRunBacktest: () => void
  isLoading: boolean
}

const TOOLTIPS = {
  ticker: 'Stock symbol to backtest (e.g., AAPL, TSLA). Only US stocks supported.',
  strategyDirection: 'Long: profit when price rises. Short: profit when price falls. Both: trade in either direction based on market conditions.',
  timeframe: 'Time period for each candlestick. Shorter = more trades, more noise.',
  startDate: 'Beginning of backtest period. Earlier = more data but slower.',
  endDate: 'End of backtest period. Use today for most recent data.',
  riskPerTrade: 'Max % of capital risked per trade. 1-2% conservative, 5%+ aggressive.',
  stopLoss: '% below entry to exit losing trade. 2% = sell if drops 2%.',
  takeProfit: '% above entry to exit winning trade. 4% = sell if rises 4%.',
  fixedLots: 'Buy exact shares per trade regardless of price.',
  percentCapital: 'Buy shares worth X% of capital. Adjusts as capital changes.',
  startingCapital: 'Initial balance. Results scale proportionally.',
  slippage: 'Price difference between signal and execution. 0.1% typical.',
  commission: 'Broker fee per trade. $0-$1 typical.',
}

export function SettingsCard({
  settings,
  onSettingsChange,
  onRunBacktest,
  isLoading,
}: SettingsCardProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const updateSetting = <K extends keyof BacktestRequest>(
    key: K,
    value: BacktestRequest[K]
  ) => {
    onSettingsChange({ ...settings, [key]: value })
  }

  return (
    <div className="settings-card">
      <div className="settings-header" onClick={() => setIsCollapsed(!isCollapsed)}>
        <h2>Settings</h2>
        <button className="collapse-btn">{isCollapsed ? '▼' : '▲'}</button>
      </div>

      <button
        className="run-backtest-btn"
        onClick={onRunBacktest}
        disabled={isLoading}
      >
        {isLoading ? 'Running...' : 'Run Backtest'}
      </button>

      {!isCollapsed && (
        <div className="settings-content">
          <div className="settings-section">
            <h3>Stock</h3>
            <div className="setting-row">
              <label>
                Ticker
                <Tooltip text={TOOLTIPS.ticker} />
              </label>
              <StockSelector
                value={settings.ticker}
                onChange={(ticker) => updateSetting('ticker', ticker)}
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Strategy</h3>
            <div className="setting-row">
              <label>
                Direction
                <Tooltip text={TOOLTIPS.strategyDirection} />
              </label>
              <select
                value={settings.strategy_direction}
                onChange={(e) => updateSetting('strategy_direction', e.target.value as 'long' | 'short' | 'both')}
              >
                <option value="long">Long Only</option>
                <option value="short">Short Only</option>
                <option value="both">Long & Short</option>
              </select>
            </div>
          </div>

          <div className="settings-section">
            <h3>Timeframe</h3>
            <div className="setting-row">
              <label>
                Candle
                <Tooltip text="Only daily timeframe available with Alpha Vantage free tier. Upgrade API for intraday data." />
              </label>
              <span className="timeframe-value">Daily</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Period</h3>
            <div className="setting-row">
              <label>
                Start
                <Tooltip text={TOOLTIPS.startDate} />
              </label>
              <input
                type="date"
                value={settings.start_date}
                onChange={(e) => updateSetting('start_date', e.target.value)}
              />
            </div>
            <div className="setting-row">
              <label>
                End
                <Tooltip text={TOOLTIPS.endDate} />
              </label>
              <input
                type="date"
                value={settings.end_date}
                onChange={(e) => updateSetting('end_date', e.target.value)}
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Risk Management</h3>
            <div className="setting-row">
              <label>
                Risk/Trade
                <Tooltip text={TOOLTIPS.riskPerTrade} />
              </label>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="0.1"
                  max="10"
                  step="0.1"
                  value={settings.risk_per_trade}
                  onChange={(e) => updateSetting('risk_per_trade', parseFloat(e.target.value))}
                />
                <span>%</span>
              </div>
            </div>
            <div className="setting-row">
              <label>
                Stop Loss
                <Tooltip text={TOOLTIPS.stopLoss} />
              </label>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="0.1"
                  max="20"
                  step="0.1"
                  value={settings.stop_loss}
                  onChange={(e) => updateSetting('stop_loss', parseFloat(e.target.value))}
                />
                <span>%</span>
              </div>
            </div>
            <div className="setting-row">
              <label>
                Take Profit
                <Tooltip text={TOOLTIPS.takeProfit} />
              </label>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="0.1"
                  max="50"
                  step="0.1"
                  value={settings.take_profit}
                  onChange={(e) => updateSetting('take_profit', parseFloat(e.target.value))}
                />
                <span>%</span>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>Position Sizing</h3>
            <div className="setting-row">
              <label>
                <input
                  type="radio"
                  name="position_type"
                  checked={settings.position_type === 'fixed'}
                  onChange={() => updateSetting('position_type', 'fixed')}
                />
                Fixed lots
                <Tooltip text={TOOLTIPS.fixedLots} />
              </label>
              <input
                type="number"
                min="1"
                value={settings.lot_size}
                onChange={(e) => updateSetting('lot_size', parseInt(e.target.value))}
                disabled={settings.position_type !== 'fixed'}
              />
            </div>
            <div className="setting-row">
              <label>
                <input
                  type="radio"
                  name="position_type"
                  checked={settings.position_type === 'percent'}
                  onChange={() => updateSetting('position_type', 'percent')}
                />
                % of capital
                <Tooltip text={TOOLTIPS.percentCapital} />
              </label>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={settings.percent_capital}
                  onChange={(e) => updateSetting('percent_capital', parseFloat(e.target.value))}
                  disabled={settings.position_type !== 'percent'}
                />
                <span>%</span>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>Capital</h3>
            <div className="setting-row">
              <label>
                Starting
                <Tooltip text={TOOLTIPS.startingCapital} />
              </label>
              <div className="input-with-unit">
                <span>$</span>
                <input
                  type="number"
                  min="100"
                  value={settings.starting_capital}
                  onChange={(e) => updateSetting('starting_capital', parseFloat(e.target.value))}
                />
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>Execution Modeling</h3>
            <div className="setting-row">
              <label>
                Slippage
                <Tooltip text={TOOLTIPS.slippage} />
              </label>
              <div className="input-with-unit">
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.01"
                  value={settings.slippage}
                  onChange={(e) => updateSetting('slippage', parseFloat(e.target.value))}
                />
                <span>%</span>
              </div>
            </div>
            <div className="setting-row">
              <label>
                Commission
                <Tooltip text={TOOLTIPS.commission} />
              </label>
              <div className="input-with-unit">
                <span>$</span>
                <input
                  type="number"
                  min="0"
                  max="50"
                  step="0.1"
                  value={settings.commission}
                  onChange={(e) => updateSetting('commission', parseFloat(e.target.value))}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
