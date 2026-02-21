import { useState, useRef, useEffect } from 'react'
import './StockSelector.css'

const STOCKS = [
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'MSFT', name: 'Microsoft Corp.' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.' },
  { symbol: 'TSLA', name: 'Tesla Inc.' },
  { symbol: 'META', name: 'Meta Platforms Inc.' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.' },
  { symbol: 'JPM', name: 'JPMorgan Chase' },
  { symbol: 'V', name: 'Visa Inc.' },
  { symbol: 'JNJ', name: 'Johnson & Johnson' },
  { symbol: 'WMT', name: 'Walmart Inc.' },
  { symbol: 'PG', name: 'Procter & Gamble' },
  { symbol: 'MA', name: 'Mastercard Inc.' },
  { symbol: 'UNH', name: 'UnitedHealth Group' },
  { symbol: 'HD', name: 'Home Depot Inc.' },
  { symbol: 'DIS', name: 'Walt Disney Co.' },
  { symbol: 'BAC', name: 'Bank of America' },
  { symbol: 'XOM', name: 'Exxon Mobil Corp.' },
  { symbol: 'PFE', name: 'Pfizer Inc.' },
  { symbol: 'KO', name: 'Coca-Cola Co.' },
  { symbol: 'PEP', name: 'PepsiCo Inc.' },
  { symbol: 'CSCO', name: 'Cisco Systems' },
  { symbol: 'ABBV', name: 'AbbVie Inc.' },
  { symbol: 'CVX', name: 'Chevron Corp.' },
  { symbol: 'MRK', name: 'Merck & Co.' },
  { symbol: 'COST', name: 'Costco Wholesale' },
  { symbol: 'TMO', name: 'Thermo Fisher' },
  { symbol: 'ABT', name: 'Abbott Laboratories' },
  { symbol: 'AVGO', name: 'Broadcom Inc.' },
  { symbol: 'NKE', name: 'Nike Inc.' },
  { symbol: 'ACN', name: 'Accenture plc' },
  { symbol: 'MCD', name: 'McDonald\'s Corp.' },
  { symbol: 'NEE', name: 'NextEra Energy' },
  { symbol: 'LLY', name: 'Eli Lilly & Co.' },
  { symbol: 'DHR', name: 'Danaher Corp.' },
  { symbol: 'TXN', name: 'Texas Instruments' },
  { symbol: 'AMD', name: 'Advanced Micro Devices' },
  { symbol: 'INTC', name: 'Intel Corp.' },
  { symbol: 'PM', name: 'Philip Morris Intl' },
  { symbol: 'UPS', name: 'United Parcel Service' },
  { symbol: 'ORCL', name: 'Oracle Corp.' },
  { symbol: 'IBM', name: 'IBM Corp.' },
  { symbol: 'QCOM', name: 'Qualcomm Inc.' },
  { symbol: 'CAT', name: 'Caterpillar Inc.' },
  { symbol: 'GE', name: 'General Electric' },
  { symbol: 'BA', name: 'Boeing Co.' },
  { symbol: 'SBUX', name: 'Starbucks Corp.' },
  { symbol: 'GS', name: 'Goldman Sachs' },
  { symbol: 'BLK', name: 'BlackRock Inc.' },
  { symbol: 'AMGN', name: 'Amgen Inc.' },
]

// Export for use in MetricsCard
export const STOCK_NAMES: Record<string, string> = Object.fromEntries(
  STOCKS.map(s => [s.symbol, s.name])
)

interface StockSelectorProps {
  value: string
  onChange: (ticker: string) => void
}

export function StockSelector({ value, onChange }: StockSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const filtered = STOCKS.filter(
    s => s.symbol.toLowerCase().includes(search.toLowerCase()) ||
         s.name.toLowerCase().includes(search.toLowerCase())
  )

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false)
        setSearch('')
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (symbol: string) => {
    onChange(symbol)
    setIsOpen(false)
    setSearch('')
  }

  return (
    <div className="stock-selector" ref={containerRef}>
      <div
        className="stock-selector-display"
        onClick={() => {
          setIsOpen(!isOpen)
          setTimeout(() => inputRef.current?.focus(), 0)
        }}
      >
        <span>{value}</span>
        <span className="arrow">{isOpen ? '▲' : '▼'}</span>
      </div>

      {isOpen && (
        <div className="stock-selector-dropdown">
          <input
            ref={inputRef}
            type="text"
            className="stock-search"
            placeholder="Search ticker or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onClick={(e) => e.stopPropagation()}
          />
          <div className="stock-list">
            {filtered.map(stock => (
              <div
                key={stock.symbol}
                className={`stock-option ${stock.symbol === value ? 'selected' : ''}`}
                onClick={() => handleSelect(stock.symbol)}
              >
                <span className="stock-symbol">{stock.symbol}</span>
                <span className="stock-name">{stock.name}</span>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="stock-option no-results">No matches found</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
