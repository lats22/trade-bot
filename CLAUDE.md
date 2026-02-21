# Trade_Bot

Stock backtesting system with web dashboard and TradingView signal export.

## Quick Reference

| Service | Local URL | Container Name |
|---------|-----------|----------------|
| Frontend | http://localhost:3100 | trade-bot-frontend |
| Backend | http://localhost:5100 | trade-bot-backend |
| Playwright | http://localhost:8934 | trade-bot-playwright |

## Playwright Testing

**From inside container, use Docker network URLs:**
- Frontend: `http://frontend:80`
- Backend: `http://backend:5000`

## Overview

- **Purpose:** Backtest stock trading strategies using multiple technical analysis strategies
- **Platform:** Python (Backtrader) + React PWA dashboard
- **Data Source:** Alpha Vantage API (hourly intraday data)
- **Output:** Performance metrics, equity curve, trade log, CSV export for TradingView

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React PWA |
| Backend | Python FastAPI |
| Backtesting | Backtrader |
| Charts | Plotly.js |
| Data | Alpha Vantage API |
| Testing | Playwright MCP (port 8934) |
| Deployment | Docker (local) → VPS (later with PIN auth) |

## Project Structure

```
Trade_Bot/
├── frontend/               # React PWA dashboard
│   ├── src/
│   │   ├── components/    # Settings card, charts, trade log
│   │   ├── pages/         # Dashboard, Compare
│   │   └── services/      # API client
│   └── Dockerfile
├── backend/                # Python FastAPI + Backtrader
│   ├── app/
│   │   ├── api/           # FastAPI endpoints
│   │   ├── strategies/    # Trading strategies (5 strategies)
│   │   └── backtest/      # Backtrader runner
│   └── Dockerfile
├── data/                   # Cached stock data (mounted volume)
├── docker-compose.yml
├── .env
├── .env.example
├── .mcp.json
└── CLAUDE.md
```

## Configurable Parameters (with Help Tooltips)

Every setting has a [?] icon that shows an explanation tooltip on hover/click.

### Stock Selection
| Setting | Description |
|---------|-------------|
| Ticker [?] | Searchable dropdown with 50 popular US stocks. Type to filter by ticker or company name. Full company names displayed (e.g., "AAPL - Apple Inc."). After backtest, company name shown in Performance Metrics header. |

### Timeframe
| Setting | Description |
|---------|-------------|
| Candle Interval [?] | Time period for each candlestick. Shorter intervals (15m, 30m) = more trades, more noise. Longer intervals (4h, daily) = fewer trades, clearer trends. |

### Backtest Period
| Setting | Description |
|---------|-------------|
| Start Date [?] | Beginning of backtest period. Earlier dates = more data but slower processing. |
| End Date [?] | End of backtest period. Use today's date for most recent data. |
| Last X Months [?] | Alternative to custom dates. Automatically calculates period from today backwards. |

### Strategy Direction
| Setting | Description |
|---------|-------------|
| Strategy Direction [?] | Trading direction mode. **Long Only**: Buy low, sell high (traditional). **Short Only**: Sell high, buy low (profit from price drops). **Long & Short**: Trade both directions based on signals. |

### Risk Management
| Setting | Description |
|---------|-------------|
| Risk per Trade [?] | Maximum percentage of capital risked on each trade. 1-2% is conservative, 5%+ is aggressive. Used for position sizing calculations. |
| Stop Loss [?] | Percentage below entry price to exit losing trade (long) or above entry (short). Protects capital. 2% = exit if price moves 2% against position. |
| Take Profit [?] | Percentage above entry price to exit winning trade (long) or below entry (short). Locks in gains. 4% = exit if price moves 4% in favor. |

### Position Sizing
| Setting | Description |
|---------|-------------|
| Fixed Lots [?] | Buy exact number of shares per trade regardless of price. Simple but doesn't account for varying stock prices. |
| % of Capital [?] | Buy shares worth X% of your total capital. Automatically adjusts position size as capital grows/shrinks. |

### Capital
| Setting | Description |
|---------|-------------|
| Starting Capital [?] | Initial account balance for backtest simulation. Results scale proportionally - $10K vs $100K shows same percentage returns. |

### Execution Modeling
| Setting | Description |
|---------|-------------|
| Slippage [?] | Simulates real-world price difference between signal and execution. 0.1% = if signal is $100, actual fill might be $100.10. Higher for volatile/illiquid stocks. |
| Commission [?] | Broker fee per trade. Most brokers charge $0-$1 per trade. Adds up significantly with frequent trading. |

### Save Options
| Setting | Description |
|---------|-------------|
| Don't Save [?] | View results only. Data lost when you close the page. Good for quick tests. |
| Save Locally [?] | Store in browser storage. Persists across sessions on same device. Limited by browser storage quota. |
| Export to File [?] | Download as JSON file. Can be shared, backed up, or imported on another device. |

## Key Features

### Core Features (Original Design)
1. **Settings Card** - Adjust all parameters via web UI with [?] tooltips
   - Searchable stock dropdown with 50 popular US stocks (type to filter)
   - Full company names displayed in dropdown and Performance Metrics
   - Run Backtest button positioned at top of Settings panel for quick access
   - Solid tooltip backgrounds for better readability
2. **Equity Curve** - Interactive Plotly chart with entry/exit markers
3. **Trade Log** - Table with entry/exit points, P&L, click to view trade chart
4. **Trade Visualization** - Individual trade charts showing indicators and entry/exit
5. **Save/Load Backtests** - Store and retrieve backtest results
6. **Strategy Comparison** - Compare two strategies side by side on same ticker
7. **CSV Export** - Download signals for TradingView overlay
8. **Dark Mode** - Toggle with OS preference detection
9. **Mobile Responsive** - Collapsible settings, stacked layout

### Implemented Advanced Features
| Feature | Description | Status |
|---------|-------------|--------|
| **Multiple Strategies** | 5 trading strategies available: VWAP+MA+Volume, SMA Crossover, RSI, MACD, Bollinger Bands. Each with description and strategy-specific indicators. | ✅ Implemented |
| **Short Selling** | Trade both directions - Long Only, Short Only, or Long & Short. Entry/exit logic varies by strategy. | ✅ Implemented |
| **Monte Carlo Simulation** | Runs 1000 randomized trade sequence simulations. Shows median, best, worst case returns with 5th/95th percentile confidence interval. Displays max drawdown distribution. | ✅ Implemented |
| **Walk-Forward Testing** | Splits data into 5 rolling windows. Tests strategy consistency across time periods. Shows per-window returns and overall consistency %. Helps detect overfitting. | ✅ Implemented |
| **Parameter Heatmap** | Visual 2D grid showing Stop Loss vs Take Profit parameter combinations. Color-coded by return (red=loss, yellow=neutral, green=profit). Highlights best parameter combination. | ✅ Implemented |
| **Paper Trading Mode** | Simulated forward-testing with recent historical data. Tracks virtual positions, unrealized P&L, and trade history. Start/Stop buttons with session status display. | ✅ Implemented |
| **Slippage Modeling** | Simulate real execution price differences | ✅ Implemented |
| **Commission/Fees** | Include broker fees in P&L calculation | ✅ Implemented |

### Performance Metrics Displayed
| Metric | Description |
|--------|-------------|
| Total Return | Percentage gain/loss over backtest period |
| Win Rate | Percentage of trades that were profitable |
| Max Drawdown | Largest peak-to-trough decline |
| Sharpe Ratio | Risk-adjusted return (higher = better) |
| Total Trades | Number of completed trades |
| Profit Factor | Gross profits / gross losses (>1 = profitable) |
| Risk/Reward | Average winner / average loser |
| Best Streak | Longest consecutive winning trades |
| Worst Streak | Longest consecutive losing trades |

### Dashboard Tabs
| Tab | Content |
|-----|---------|
| Equity | Main equity curve with trade markers |
| Drawdown | Drawdown chart over time |
| Monte Carlo | Distribution of simulated outcomes |
| Walk-Forward | Rolling window test results |
| Heatmap | Parameter optimization visualization |

## UI Components

### Settings Card with Help Tooltips
```
┌─────────────────────────┐
│  ⚙️ SETTINGS            │
├─────────────────────────┤
│  [Run Backtest]         │  ← Button at top for quick access
│                         │
│  STOCK                  │
│  [🔍 Search stocks...  ]│  ← Searchable dropdown (50 stocks)
│  [AAPL - Apple Inc. ▼]  │
│                    [?]  │
│                         │
│  STRATEGY DIRECTION     │
│  ○ Long Only       [?]  │
│  ○ Short Only      [?]  │
│  ● Long & Short    [?]  │
│                         │
│  TIMEFRAME              │
│  Candle: [1h ▼]    [?]  │
│                         │
│  PERIOD                 │
│  Start: [📅]       [?]  │
│  End:   [📅]       [?]  │
│  ─── OR ───             │
│  Last [12] months  [?]  │
│                         │
│  RISK MANAGEMENT        │
│  Risk/Trade: [2]%  [?]  │
│  Stop Loss:  [2]%  [?]  │
│  Take Profit:[4]%  [?]  │
│                         │
│  POSITION SIZING        │
│  ○ Fixed lots [50] [?]  │
│  ○ % capital [10]% [?]  │
│                         │
│  CAPITAL                │
│  Starting: [$10K]  [?]  │
│                         │
│  EXECUTION MODELING     │
│  Slippage: [0.1]%  [?]  │
│  Commission: [$1]  [?]  │
│                         │
│  SAVE OPTIONS           │
│  ○ Don't save      [?]  │
│  ○ Save locally    [?]  │
│  ○ Export to file  [?]  │
│                         │
│  [Paper Trade]          │
└─────────────────────────┘
```

### Tooltip Behavior
- Desktop: Show on hover, hide on mouse leave
- Mobile: Show on tap, hide on tap elsewhere
- Solid background color (no transparency) for better readability
- Include "Learn more" link to docs for complex topics

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/backtest` | POST | Run backtest with settings (includes Monte Carlo & Walk-Forward) |
| `/api/backtest/heatmap` | POST | Run parameter optimization grid search |
| `/api/paper-trade/start` | POST | Start paper trading session |
| `/api/paper-trade/status/{id}` | GET | Get paper trading status |
| `/api/paper-trade/sessions` | GET | List all paper trade sessions |
| `/api/paper-trade/stop/{id}` | POST | Stop paper trading session |
| `/api/strategies` | GET | List available trading strategies |
| `/api/strategies/{name}` | GET | Get strategy details |
| `/api/tickers` | GET | List popular stock tickers |
| `/api/health` | GET | Health check |

## Commands

```bash
# Start application
docker compose up -d

# View logs
docker compose logs -f

# Rebuild after code changes
docker compose up -d --build

# Full rebuild (clear cache)
docker compose down && docker compose build --no-cache && docker compose up -d

# Stop all services
docker compose down

# Access dashboard
http://localhost:3100

# API endpoint
http://localhost:5100
```

## Environment Variables

Required in `.env`:
```
# Project
PROJECT_NAME=trade-bot

# Ports
FRONTEND_PORT=3100
BACKEND_PORT=5100
PLAYWRIGHT_PORT=8934

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_key_here

# CORS (optional - defaults to localhost:3000,3100)
ALLOWED_ORIGINS=http://localhost:3100

# VPS only (for later deployment)
PIN_CODE=your_pin_here
```

## Team Structure (Agents)

| # | Name | Role |
|---|------|------|
| 0 | PM-Patrick | Project Manager (coordinator) |
| 1 | Frontend-Felix | React PWA dashboard |
| 2 | Backend-Bruno | Python FastAPI + Backtrader |
| 4 | Tester-Tina | Playwright testing |
| 5 | Reviewer-Ray | Code review |
| 6 | GitHub-Grace | Git operations |
| 7 | VPS-Victor | Deployment |

## UI Compliance

- **Mobile responsive** - No horizontal scrolling, collapsible sections
- **Dark mode** - CSS variables, toggle switch, OS preference detection
- **Touch targets** - Minimum 44x44px
- **Accessibility** - WCAG AA contrast ratios
- **Help tooltips** - [?] icon on every setting with explanation

## Docker Security

- No hardcoded credentials (use required env vars)
- Pinned image versions (node:20.11-alpine, python:3.11.7-slim, nginx:1.27-alpine)
- Health checks on backend
- CSP security headers in nginx configuration
- CORS environment configuration via ALLOWED_ORIGINS
- No database ports exposed (no database needed)

## Development Notes

### Stock Data
- Uses 50 popular US stocks built into StockSelector component
- No external tickers API call needed (removed getTickers function)
- Company names displayed in both dropdown and metrics header

### Available Trading Strategies
| Strategy | Indicators | Entry Logic |
|----------|------------|-------------|
| VWAP + MA + Volume | VWAP, SMA(20), Volume SMA | Long: Price > VWAP + MA + Volume spike. Short: Price < VWAP + MA + Volume spike |
| SMA Crossover | SMA(10), SMA(30) | Long: Fast MA crosses above Slow MA. Short: Fast MA crosses below Slow MA |
| RSI Strategy | RSI(14) | Long: RSI < 30 (oversold). Short: RSI > 70 (overbought) |
| MACD Strategy | MACD(12,26,9) | Long: MACD crosses above Signal. Short: MACD crosses below Signal |
| Bollinger Bands | BB(20,2) | Long: Price touches lower band. Short: Price touches upper band |

## Research Sources

Backtesting platform research used to identify features:
- [NewTrading - Best Backtesting Software 2026](https://www.newtrading.io/backtesting-software/)
- [LuxAlgo - Backtesting Software Ranked](https://www.luxalgo.com/blog/backtesting-software-ranked-for-retail-quants/)
- [QuantConnect - Open Source Trading Platform](https://www.quantconnect.com/)
- [NautilusTrader - High Performance Trading](https://nautilustrader.io/)
- [TuringTrader - Open Source Backtesting](https://www.turingtrader.org/)
