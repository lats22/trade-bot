# Trade_Bot Design Document

**Date:** 2026-02-20
**Status:** Approved - Ready for Implementation Planning
**Next Step:** Invoke `writing-plans` skill to create implementation plan

---

## Executive Summary

Stock backtesting PWA with web dashboard. Users configure strategy parameters via a settings card, run backtests, visualize results with charts and trade logs, save/compare strategies, and export signals for TradingView overlay.

**Tech Stack:** React PWA + Python FastAPI + Backtrader + Plotly.js + Docker

---

## User Requirements (From Brainstorming Session)

1. Backtest stocks (not crypto/forex)
2. Use VWAP, MA200, and Volume indicators (strategy rules to be defined later)
3. Hourly timeframe (with adjustable options)
4. Data from Alpha Vantage API
5. Visual dashboard with charts (not just console output)
6. TradingView signal export (CSV)
7. Adjustable parameters: ticker, timeframe, period, risk, position size, capital
8. Save/load backtest results
9. Compare different strategies on same ticker
10. Deploy locally first, then VPS later
11. Help tooltips [?] on every setting

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Trade_Bot (Docker)                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│  React PWA      │   FastAPI       │   Playwright MCP        │
│  (Frontend)     │   (Backend)     │   (Testing)             │
│  Port 3000      │   Port 5000     │   Port 8934             │
└────────┬────────┴────────┬────────┴─────────────────────────┘
         │                 │
         │    REST API     │
         └────────┬────────┘
                  │
         ┌───────┴───────┐
         │   Backtrader  │
         │   Engine      │
         └───────┬───────┘
                  │
         ┌───────┴───────┐
         │ Alpha Vantage │
         │ API (Data)    │
         └───────────────┘
```

### Project Structure

```
Trade_Bot/
├── frontend/               # React PWA dashboard
│   ├── src/
│   │   ├── components/    # Settings card, charts, trade log, tooltips
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
├── docs/
│   └── plans/             # Design and implementation docs
├── docker-compose.yml
├── .env
├── .env.example
├── .mcp.json
└── CLAUDE.md
```

---

## Features

### Core Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | Settings Card | All parameters adjustable via web UI with [?] tooltips |
| 2 | Equity Curve | Interactive Plotly chart with entry/exit markers |
| 3 | Trade Log | Table with entry/exit points, P&L, click to view trade chart |
| 4 | Trade Visualization | Individual trade charts showing indicators and entry/exit |
| 5 | Save/Load Backtests | Store in localStorage or export to file |
| 6 | Strategy Comparison | Compare two strategies side by side on same ticker |
| 7 | CSV Export | Download signals for TradingView overlay |
| 8 | Dark Mode | Toggle with OS preference detection |
| 9 | Mobile Responsive | Collapsible settings, stacked layout |

### Advanced Features (From Industry Research)

| # | Feature | Description | Source |
|---|---------|-------------|--------|
| 10 | Slippage Modeling | Simulate real execution price differences | NewTrading |
| 11 | Commission/Fees | Include broker fees in P&L calculation | QuantConnect |
| 12 | Monte Carlo Simulation | Run 1000+ random variations to test robustness | QuantConnect |
| 13 | Walk-Forward Testing | Test on rolling windows to prevent overfitting | LuxAlgo |
| 14 | Paper Trading Mode | Forward-test with live data before real money | NewTrading |
| 15 | Drawdown Chart | Visual timeline of portfolio drawdowns | NautilusTrader |
| 16 | Win/Loss Streaks | Track consecutive wins/losses | TuringTrader |
| 17 | Profit Factor | Gross profit / gross loss ratio | QuantConnect |
| 18 | Risk/Reward Ratio | Average win / average loss | Standard |
| 19 | Parameter Heatmap | Visual grid showing which parameter combos work | QuantConnect |

---

## Configurable Parameters

### Settings Card Layout

```
┌─────────────────────────┐
│  ⚙️ SETTINGS            │
├─────────────────────────┤
│  STOCK                  │
│  Ticker: [AAPL  ▼] [?]  │
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

### Parameter Descriptions (for Tooltips)

| Parameter | Tooltip Text |
|-----------|--------------|
| Ticker | Stock symbol to backtest (e.g., AAPL, TSLA). Only US stocks supported. |
| Candle Interval | Time period for each candlestick. Shorter = more trades, more noise. |
| Start Date | Beginning of backtest period. Earlier = more data but slower. |
| End Date | End of backtest period. Use today for most recent data. |
| Last X Months | Alternative to custom dates. Calculates from today backwards. |
| Risk per Trade | Max % of capital risked per trade. 1-2% conservative, 5%+ aggressive. |
| Stop Loss | % below entry to exit losing trade. 2% = sell if drops 2%. |
| Take Profit | % above entry to exit winning trade. 4% = sell if rises 4%. |
| Fixed Lots | Buy exact shares per trade regardless of price. |
| % of Capital | Buy shares worth X% of capital. Adjusts as capital changes. |
| Starting Capital | Initial balance. Results scale proportionally. |
| Slippage | Price difference between signal and execution. 0.1% typical. |
| Commission | Broker fee per trade. $0-$1 typical. |
| Don't Save | View only. Lost when page closes. |
| Save Locally | Browser storage. Persists on same device. |
| Export to File | Download JSON. Can share or backup. |

---

## Dashboard Layout

### Desktop View

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Trade_Bot Dashboard                    [Compare] [🌙/☀️]        [Run Backtest] │
├───────────────────────┬─────────────────────────────────────────────────────────┤
│                       │  [Equity] [Drawdown] [Monte Carlo] [Walk-Forward] [Heatmap]
│  ⚙️ SETTINGS          ├─────────────────────────────────────────────────────────┤
│  (See above)          │                                                         │
│                       │  📈 CHART (selected tab)                                │
│                       │                                                         │
│                       ├─────────────────────────────────────────────────────────┤
│                       │  📊 METRICS                                             │
│                       │  ┌───────┬───────┬───────┬───────┬───────┐             │
│                       │  │Return │Win %  │Max DD │Sharpe │Trades │             │
│                       │  │+24.5% │ 62%   │-8.2%  │ 1.45  │  28   │             │
│                       │  └───────┴───────┴───────┴───────┴───────┘             │
│                       │  ┌───────┬───────┬───────┬───────┐                     │
│                       │  │Profit │ R:R   │Best   │Worst  │                     │
│                       │  │Factor │ Ratio │Streak │Streak │                     │
│                       │  │ 1.85  │ 1.3:1 │  5W   │  3L   │                     │
│                       │  └───────┴───────┴───────┴───────┘                     │
│                       ├─────────────────────────────────────────────────────────┤
│                       │  📋 TRADE LOG                              [Export CSV] │
│                       │  Date     │ Type │ Entry  │ Exit   │  P&L  │ View      │
│                       │  Jan 5    │ BUY  │$182.50 │$188.20 │ +$285 │  👁️       │
│                       │  Jan 12   │ BUY  │$185.00 │$181.50 │ -$175 │  👁️       │
│                       ├─────────────────────────────────────────────────────────┤
│                       │  📂 SAVED BACKTESTS                                     │
│                       │  AAPL │ VWAP+MA │ +24.5% │ [Load] [Del]                 │
│                       │  AAPL │ RSI+Vol │ +18.2% │ [Load] [Del]                 │
└───────────────────────┴─────────────────────────────────────────────────────────┘
```

### Mobile View (Stacked)

```
┌─────────────────────────────┐
│ Trade_Bot        [🌙] [Run] │
├─────────────────────────────┤
│ ⚙️ Settings          [▼]    │  ← Collapsible
├─────────────────────────────┤
│ 📊 Metrics                  │
│ ┌──────┬──────┬──────┐     │
│ │+24.5%│ 62%  │-8.2% │     │
│ └──────┴──────┴──────┘     │
├─────────────────────────────┤
│ 📈 Chart (tabs above)      │
├─────────────────────────────┤
│ 📋 Trade Log         [CSV] │
├─────────────────────────────┤
│ 📂 Saved             [▼]   │
└─────────────────────────────┘
```

---

## Trade Visualization

### Individual Trade Chart (Modal)

When clicking 👁️ on a trade row:

```
┌─────────────────────────────────────────────────────────┐
│  AAPL Trade #1 - Jan 5-8, 2024                    [X]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Candlestick chart with:                               │
│  - VWAP line (purple)                                  │
│  - MA200 line (orange)                                 │
│  - Volume bars (bottom)                                │
│  - 🟢 Entry marker (green arrow)                       │
│  - 🔴 Exit marker (red arrow)                          │
│  - Shaded area between entry/exit                      │
│                                                         │
│  Entry Reason: Price above VWAP + MA200, volume spike  │
│  Exit Reason: Take profit hit (4%)                     │
│                                                         │
│  P&L: +$285 (+3.1%)   Duration: 3 days 4 hours         │
└─────────────────────────────────────────────────────────┘
```

---

## Strategy Comparison

### Side-by-Side View

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📊 Compare Strategies - AAPL                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┬─────────────────────────────┐         │
│  │  Strategy A: VWAP + MA200   │  Strategy B: RSI + Volume   │         │
│  ├─────────────────────────────┼─────────────────────────────┤         │
│  │  Return:     +24.5%         │  Return:     +18.2%         │         │
│  │  Win Rate:   62%            │  Win Rate:   58%            │         │
│  │  Drawdown:   -8.2%          │  Drawdown:   -12.4%         │         │
│  │  Sharpe:     1.45           │  Sharpe:     1.12           │         │
│  │  Trades:     28             │  Trades:     42             │         │
│  └─────────────────────────────┴─────────────────────────────┘         │
│                                                                         │
│  📈 Equity Curves Overlay (A=blue, B=orange)                           │
│                                                                         │
│  🏆 Winner: Strategy A (+6.3% better return, lower drawdown)           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

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

### Backtest Request

```json
{
  "ticker": "AAPL",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "risk_per_trade": 2,
  "stop_loss": 2,
  "take_profit": 4,
  "position_type": "fixed",
  "lot_size": 50,
  "starting_capital": 10000,
  "slippage": 0.1,
  "commission": 1.0
}
```

### Backtest Response

```json
{
  "metrics": {
    "total_return": 24.5,
    "win_rate": 62,
    "max_drawdown": -8.2,
    "sharpe_ratio": 1.45,
    "total_trades": 28,
    "profit_factor": 1.85,
    "risk_reward_ratio": 1.3,
    "best_streak": 5,
    "worst_streak": 3
  },
  "equity_curve": [...],
  "drawdown_curve": [...],
  "trades": [...]
}
```

---

## Docker Setup

### docker-compose.yml

```yaml
services:
  frontend:
    build: ./frontend
    container_name: trade-bot-frontend
    ports:
      - "${FRONTEND_PORT:-3000}:80"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - app-network

  backend:
    build: ./backend
    container_name: trade-bot-backend
    ports:
      - "${BACKEND_PORT:-5000}:5000"
    environment:
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY:?Required}
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  playwright:
    image: mcr.microsoft.com/playwright:v1.52.0-noble
    container_name: trade-bot-playwright
    working_dir: /app
    entrypoint: npx
    command: ["@playwright/mcp@latest", "--port", "8934", "--host", "0.0.0.0"]
    ports:
      - "8934:8934"
    depends_on:
      - frontend
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Environment Variables (.env)

```
PROJECT_NAME=trade-bot
FRONTEND_PORT=3000
BACKEND_PORT=5000
PLAYWRIGHT_PORT=8934
ALPHA_VANTAGE_API_KEY=your_key_here
PIN_CODE=your_pin_here  # VPS only
```

---

## Deployment

### Phase 1: Local Development
- Run in Docker on local machine
- Test and refine strategy
- No authentication needed

### Phase 2: VPS Deployment (Later)
- Deploy to VPS (72.62.64.54)
- Add PIN authentication
- Accessible from anywhere

---

## UI Compliance (Global Rules)

- **Mobile responsive** - No horizontal scrolling, collapsible sections
- **Dark mode** - CSS variables, toggle switch, OS preference detection
- **Touch targets** - Minimum 44x44px
- **Accessibility** - WCAG AA contrast ratios
- **Help tooltips** - [?] icon on every setting

---

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

---

## Research Sources

- [NewTrading - Best Backtesting Software 2026](https://www.newtrading.io/backtesting-software/)
- [LuxAlgo - Backtesting Software Ranked](https://www.luxalgo.com/blog/backtesting-software-ranked-for-retail-quants/)
- [QuantConnect - Open Source Trading Platform](https://www.quantconnect.com/)
- [NautilusTrader - High Performance Trading](https://nautilustrader.io/)
- [TuringTrader - Open Source Backtesting](https://www.turingtrader.org/)

---

## Next Steps

1. **Invoke `writing-plans` skill** to create detailed implementation plan
2. **PM-Patrick** will coordinate agents to build the system
3. **Test locally** before VPS deployment
