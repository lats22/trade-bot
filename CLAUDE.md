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

- **Purpose:** Backtest stock trading strategies using VWAP, MA200, and Volume indicators
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
│   │   ├── strategies/    # Trading strategies (VWAP, MA, Volume)
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
| Ticker [?] | Stock symbol to backtest (e.g., AAPL, TSLA, MSFT). Only US stocks supported via Alpha Vantage. |

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

### Risk Management
| Setting | Description |
|---------|-------------|
| Risk per Trade [?] | Maximum percentage of capital risked on each trade. 1-2% is conservative, 5%+ is aggressive. Used for position sizing calculations. |
| Stop Loss [?] | Percentage below entry price to exit losing trade. Protects capital. 2% = sell if price drops 2% from entry. |
| Take Profit [?] | Percentage above entry price to exit winning trade. Locks in gains. 4% = sell if price rises 4% from entry. |

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
2. **Equity Curve** - Interactive Plotly chart with entry/exit markers
3. **Trade Log** - Table with entry/exit points, P&L, click to view trade chart
4. **Trade Visualization** - Individual trade charts showing indicators and entry/exit
5. **Save/Load Backtests** - Store and retrieve backtest results
6. **Strategy Comparison** - Compare two strategies side by side on same ticker
7. **CSV Export** - Download signals for TradingView overlay
8. **Dark Mode** - Toggle with OS preference detection
9. **Mobile Responsive** - Collapsible settings, stacked layout

### Advanced Features (From Industry Research)
| Feature | Description | Source |
|---------|-------------|--------|
| **Slippage Modeling** | Simulate real execution price differences | [NewTrading](https://www.newtrading.io/backtesting-software/) |
| **Commission/Fees** | Include broker fees in P&L calculation | [QuantConnect](https://www.quantconnect.com/) |
| **Monte Carlo Simulation** | Run 1000+ random variations to test strategy robustness | [QuantConnect](https://www.quantconnect.com/) |
| **Walk-Forward Testing** | Test on rolling windows to prevent overfitting | [LuxAlgo](https://www.luxalgo.com/blog/backtesting-software-ranked-for-retail-quants/) |
| **Paper Trading Mode** | Forward-test with live data before real money | [NewTrading](https://www.newtrading.io/backtesting-software/) |
| **Drawdown Chart** | Visual timeline of portfolio drawdowns | [NautilusTrader](https://nautilustrader.io/) |
| **Win/Loss Streaks** | Track consecutive wins/losses | [TuringTrader](https://www.turingtrader.org/) |
| **Profit Factor** | Gross profit / gross loss ratio | [QuantConnect](https://www.quantconnect.com/) |
| **Risk/Reward Ratio** | Average win / average loss | Standard metric |
| **Parameter Heatmap** | Visual grid showing which parameter combos work best | [QuantConnect](https://www.quantconnect.com/) |

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
│  STOCK                  │
│  Ticker: [AAPL  ▼] [?]  │  ← [?] shows tooltip on hover
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
│  [Run Backtest]         │
│  [Paper Trade]          │
└─────────────────────────┘
```

### Tooltip Behavior
- Desktop: Show on hover, hide on mouse leave
- Mobile: Show on tap, hide on tap elsewhere
- Include "Learn more" link to docs for complex topics

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/backtest` | POST | Run backtest with settings |
| `/api/backtest/monte-carlo` | POST | Run Monte Carlo simulation |
| `/api/backtest/walk-forward` | POST | Run walk-forward test |
| `/api/paper-trade/start` | POST | Start paper trading session |
| `/api/paper-trade/status` | GET | Get paper trading status |
| `/api/tickers` | GET | List available stock tickers |
| `/api/export/csv` | GET | Download signals CSV |
| `/api/health` | GET | Health check |

## Commands

```bash
# Start application
docker compose up -d

# View logs
docker compose logs -f

# Rebuild after code changes
docker compose up -d --build

# Stop all services
docker compose down

# Access dashboard
http://localhost:3000

# API endpoint
http://localhost:5000
```

## Environment Variables

Required in `.env`:
```
# Project
PROJECT_NAME=trade-bot

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=5000
PLAYWRIGHT_PORT=8934

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_key_here

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
- Pinned image versions
- Health checks on backend
- No database ports exposed (no database needed)

## Research Sources

Backtesting platform research used to identify features:
- [NewTrading - Best Backtesting Software 2026](https://www.newtrading.io/backtesting-software/)
- [LuxAlgo - Backtesting Software Ranked](https://www.luxalgo.com/blog/backtesting-software-ranked-for-retail-quants/)
- [QuantConnect - Open Source Trading Platform](https://www.quantconnect.com/)
- [NautilusTrader - High Performance Trading](https://nautilustrader.io/)
- [TuringTrader - Open Source Backtesting](https://www.turingtrader.org/)
