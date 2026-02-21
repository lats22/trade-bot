# Trade_Bot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a stock backtesting PWA with React frontend, Python/FastAPI backend, and Backtrader engine that allows users to configure strategies, run backtests, visualize results, and export signals for TradingView.

**Architecture:** Docker-based microservices with React PWA (port 3000) communicating via REST API to FastAPI backend (port 5000). Backend uses Backtrader for strategy execution and Alpha Vantage for market data. Playwright MCP (port 8934) for testing.

**Tech Stack:** React 18 + TypeScript + Plotly.js | Python 3.11 + FastAPI + Backtrader | Docker Compose | Alpha Vantage API

---

## Phase 1: Project Scaffolding

### Task 1: Create Docker Infrastructure

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.env` (from example)
- Create: `.mcp.json`
- Create: `.gitignore`
- Create: `data/.gitkeep`

**Step 1: Create docker-compose.yml**

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
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY:?ALPHA_VANTAGE_API_KEY is required}
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5000/api/health"]
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
      - "${PLAYWRIGHT_PORT:-8934}:8934"
    depends_on:
      - frontend
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

**Step 2: Create .env.example**

```
# Project
PROJECT_NAME=trade-bot

# Ports
FRONTEND_PORT=3000
BACKEND_PORT=5000
PLAYWRIGHT_PORT=8934

# Alpha Vantage API (get free key at https://www.alphavantage.co/support/#api-key)
ALPHA_VANTAGE_API_KEY=your_api_key_here

# VPS only (for later deployment)
# PIN_CODE=your_pin_here
```

**Step 3: Create .env from example**

Copy `.env.example` to `.env` and set your Alpha Vantage API key.

**Step 4: Create .mcp.json**

```json
{
  "mcpServers": {
    "playwright": {
      "type": "http",
      "url": "http://localhost:8934/mcp"
    }
  }
}
```

**Step 5: Create .gitignore**

```
# Environment
.env
!.env.example

# Data
data/*
!data/.gitkeep

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node
node_modules/
dist/
build/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker
*.log
```

**Step 6: Create data directory**

```bash
mkdir -p data && touch data/.gitkeep
```

**Step 7: Commit**

```bash
git init
git add docker-compose.yml .env.example .mcp.json .gitignore data/.gitkeep
git commit -m "feat: add Docker infrastructure and project scaffolding"
```

---

### Task 2: Create Backend Scaffolding

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/health.py`

**Step 1: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install wget for healthcheck
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 5000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
```

**Step 2: Create backend/requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
backtrader==1.9.78.123
pandas==2.2.0
numpy==1.26.3
requests==2.31.0
pydantic==2.5.3
python-dotenv==1.0.0
```

**Step 3: Create backend/app/__init__.py**

```python
"""Trade_Bot Backend Application."""
```

**Step 4: Create backend/app/main.py**

```python
"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health

app = FastAPI(
    title="Trade_Bot API",
    description="Stock backtesting API with Backtrader",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Trade_Bot API", "version": "1.0.0"}
```

**Step 5: Create backend/app/api/__init__.py**

```python
"""API routers."""
```

**Step 6: Create backend/app/api/health.py**

```python
"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for Docker healthcheck."""
    return {"status": "healthy"}
```

**Step 7: Verify backend builds**

```bash
cd backend && docker build -t trade-bot-backend . && cd ..
```

Expected: Build succeeds without errors.

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: add FastAPI backend scaffolding with health check"
```

---

### Task 3: Create Frontend Scaffolding

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/App.css`
- Create: `frontend/src/index.css`
- Create: `frontend/src/vite-env.d.ts`

**Step 1: Create frontend/package.json**

```json
{
  "name": "trade-bot-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "plotly.js": "^2.29.0",
    "react-plotly.js": "^2.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@types/react-plotly.js": "^2.6.3",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.12"
  }
}
```

**Step 2: Create frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 3: Create frontend/tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Step 4: Create frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
})
```

**Step 5: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#121212" />
    <title>Trade_Bot</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 6: Create frontend/src/vite-env.d.ts**

```typescript
/// <reference types="vite/client" />
```

**Step 7: Create frontend/src/main.tsx**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**Step 8: Create frontend/src/index.css**

```css
:root {
  --bg-color: #ffffff;
  --text-color: #2c3e50;
  --card-bg: #f8f9fa;
  --border-color: #dee2e6;
  --primary-color: #3498db;
  --success-color: #27ae60;
  --danger-color: #e74c3c;
}

@media (prefers-color-scheme: dark) {
  :root:not(.light-mode) {
    --bg-color: #121212;
    --text-color: #e0e0e0;
    --card-bg: #1e1e1e;
    --border-color: #3d3d3d;
    --primary-color: #58a6ff;
    --success-color: #7dce82;
    --danger-color: #f08080;
  }
}

:root.dark-mode {
  --bg-color: #121212;
  --text-color: #e0e0e0;
  --card-bg: #1e1e1e;
  --border-color: #3d3d3d;
  --primary-color: #58a6ff;
  --success-color: #7dce82;
  --danger-color: #f08080;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  line-height: 1.6;
}
```

**Step 9: Create frontend/src/App.tsx**

```tsx
import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

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

  return (
    <div className="app">
      <header className="header">
        <h1>Trade_Bot</h1>
        <button
          className="theme-toggle"
          onClick={() => setDarkMode(!darkMode)}
          aria-label="Toggle dark mode"
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </header>
      <main className="main">
        <p>Dashboard coming soon...</p>
      </main>
    </div>
  )
}

export default App
```

**Step 10: Create frontend/src/App.css**

```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.header h1 {
  font-size: 1.5rem;
}

.theme-toggle {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.5rem;
  font-size: 1.25rem;
  cursor: pointer;
  min-width: 44px;
  min-height: 44px;
}

.main {
  flex: 1;
  padding: 1rem;
}
```

**Step 11: Create frontend/nginx.conf**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # SPA routing - serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Step 12: Create frontend/Dockerfile**

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Step 13: Verify frontend builds**

```bash
cd frontend && docker build -t trade-bot-frontend . && cd ..
```

Expected: Build succeeds without errors.

**Step 14: Commit**

```bash
git add frontend/
git commit -m "feat: add React frontend scaffolding with dark mode"
```

---

### Task 4: Verify Full Stack Starts

**Step 1: Start all containers**

```bash
docker compose up -d --build
```

**Step 2: Check containers are running**

```bash
docker compose ps
```

Expected: All 3 containers (frontend, backend, playwright) are running.

**Step 3: Test backend health**

```bash
curl http://localhost:5000/api/health
```

Expected: `{"status":"healthy"}`

**Step 4: Test frontend loads**

Open http://localhost:3000 in browser. Expected: See "Trade_Bot" header with dark mode toggle.

**Step 5: Commit**

```bash
git add .
git commit -m "chore: verify full stack starts successfully"
```

---

## Phase 2: Backend - Data Layer

### Task 5: Alpha Vantage Data Fetcher

**Files:**
- Create: `backend/app/data/__init__.py`
- Create: `backend/app/data/alpha_vantage.py`
- Create: `backend/app/data/schemas.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_alpha_vantage.py`

**Step 1: Create backend/app/data/__init__.py**

```python
"""Data fetching module."""
```

**Step 2: Create backend/app/data/schemas.py**

```python
"""Pydantic schemas for data models."""
from datetime import datetime
from pydantic import BaseModel


class OHLCVBar(BaseModel):
    """Single OHLCV bar."""
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockData(BaseModel):
    """Stock data response."""
    ticker: str
    timeframe: str
    bars: list[OHLCVBar]
```

**Step 3: Create backend/app/data/alpha_vantage.py**

```python
"""Alpha Vantage API client for fetching stock data."""
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

from app.data.schemas import OHLCVBar, StockData

CACHE_DIR = Path("/app/data/cache")


class AlphaVantageClient:
    """Client for Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self):
        self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY not set")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, ticker: str, timeframe: str, month: str) -> Path:
        """Get cache file path."""
        return CACHE_DIR / f"{ticker}_{timeframe}_{month}.csv"

    def _fetch_intraday(
        self, ticker: str, interval: str, month: str
    ) -> pd.DataFrame:
        """Fetch intraday data from API."""
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": ticker,
            "interval": interval,
            "month": month,
            "outputsize": "full",
            "apikey": self.api_key,
        }
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        time_series_key = f"Time Series ({interval})"
        if time_series_key not in data:
            if "Note" in data:
                raise ValueError(f"API limit reached: {data['Note']}")
            if "Error Message" in data:
                raise ValueError(f"API error: {data['Error Message']}")
            raise ValueError(f"Unexpected response: {data}")

        records = []
        for dt_str, values in data[time_series_key].items():
            records.append({
                "datetime": dt_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            })

        df = pd.DataFrame(records)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)
        return df

    def get_intraday_data(
        self,
        ticker: str,
        interval: str,
        start_date: datetime,
        end_date: datetime,
    ) -> StockData:
        """
        Get intraday data for a ticker.

        Args:
            ticker: Stock symbol (e.g., "AAPL")
            interval: Candle interval ("15min", "30min", "60min")
            start_date: Start of date range
            end_date: End of date range

        Returns:
            StockData with OHLCV bars
        """
        all_bars = []

        # Alpha Vantage uses month format YYYY-MM
        current = start_date.replace(day=1)
        end_month = end_date.replace(day=1)

        while current <= end_month:
            month_str = current.strftime("%Y-%m")
            cache_path = self._get_cache_path(ticker, interval, month_str)

            if cache_path.exists():
                df = pd.read_csv(cache_path, parse_dates=["datetime"])
            else:
                df = self._fetch_intraday(ticker, interval, month_str)
                df.to_csv(cache_path, index=False)

            all_bars.append(df)

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        if not all_bars:
            return StockData(ticker=ticker, timeframe=interval, bars=[])

        combined = pd.concat(all_bars, ignore_index=True)
        combined = combined[
            (combined["datetime"] >= start_date)
            & (combined["datetime"] <= end_date)
        ]
        combined = combined.drop_duplicates(subset=["datetime"])
        combined = combined.sort_values("datetime").reset_index(drop=True)

        bars = [
            OHLCVBar(
                datetime=row["datetime"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
            )
            for _, row in combined.iterrows()
        ]

        return StockData(ticker=ticker, timeframe=interval, bars=bars)
```

**Step 4: Create backend/tests/__init__.py**

```python
"""Tests package."""
```

**Step 5: Create backend/tests/test_alpha_vantage.py**

```python
"""Tests for Alpha Vantage client."""
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

from app.data.alpha_vantage import AlphaVantageClient


@pytest.fixture
def mock_api_key():
    """Set mock API key."""
    with patch.dict(os.environ, {"ALPHA_VANTAGE_API_KEY": "test_key"}):
        yield


@pytest.fixture
def mock_response():
    """Mock API response."""
    return {
        "Time Series (60min)": {
            "2024-01-02 10:00:00": {
                "1. open": "100.00",
                "2. high": "101.00",
                "3. low": "99.00",
                "4. close": "100.50",
                "5. volume": "1000000",
            },
            "2024-01-02 11:00:00": {
                "1. open": "100.50",
                "2. high": "102.00",
                "3. low": "100.00",
                "4. close": "101.50",
                "5. volume": "1200000",
            },
        }
    }


def test_client_requires_api_key():
    """Test client raises error without API key."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("ALPHA_VANTAGE_API_KEY", None)
        with pytest.raises(ValueError, match="ALPHA_VANTAGE_API_KEY not set"):
            AlphaVantageClient()


def test_fetch_intraday_parses_response(mock_api_key, mock_response, tmp_path):
    """Test API response is parsed correctly."""
    with patch("app.data.alpha_vantage.CACHE_DIR", tmp_path):
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
            )

            client = AlphaVantageClient()
            data = client.get_intraday_data(
                ticker="AAPL",
                interval="60min",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 31),
            )

            assert data.ticker == "AAPL"
            assert data.timeframe == "60min"
            assert len(data.bars) == 2
            assert data.bars[0].close == 100.50
            assert data.bars[1].close == 101.50
```

**Step 6: Add pytest to requirements.txt**

Edit `backend/requirements.txt` to add:

```
pytest==8.0.0
pytest-asyncio==0.23.3
```

**Step 7: Run tests**

```bash
docker compose exec backend pytest tests/ -v
```

Expected: All tests pass.

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: add Alpha Vantage data fetcher with caching"
```

---

### Task 6: Backtrader Strategy - VWAP + MA200 + Volume

**Files:**
- Create: `backend/app/strategies/__init__.py`
- Create: `backend/app/strategies/vwap_ma_volume.py`
- Create: `backend/app/strategies/indicators.py`
- Create: `backend/tests/test_strategy.py`

**Step 1: Create backend/app/strategies/__init__.py**

```python
"""Trading strategies module."""
```

**Step 2: Create backend/app/strategies/indicators.py**

```python
"""Custom Backtrader indicators."""
import backtrader as bt


class VWAP(bt.Indicator):
    """Volume Weighted Average Price indicator."""

    lines = ("vwap",)
    params = (("period", 14),)

    def __init__(self):
        cumvol = bt.ind.SumN(self.data.volume, period=self.p.period)
        cumtp = bt.ind.SumN(
            self.data.close * self.data.volume, period=self.p.period
        )
        self.lines.vwap = cumtp / cumvol
```

**Step 3: Create backend/app/strategies/vwap_ma_volume.py**

```python
"""VWAP + MA200 + Volume strategy."""
import backtrader as bt

from app.strategies.indicators import VWAP


class VWAPMAVolumeStrategy(bt.Strategy):
    """
    VWAP + MA200 + Volume Strategy.

    Entry conditions (BUY):
    - Price above VWAP
    - Price above MA200
    - Volume above average (volume spike)

    Exit conditions:
    - Stop loss hit
    - Take profit hit
    """

    params = (
        ("vwap_period", 14),
        ("ma_period", 200),
        ("volume_period", 20),
        ("volume_mult", 1.5),
        ("stop_loss", 0.02),
        ("take_profit", 0.04),
        ("risk_per_trade", 0.02),
        ("position_type", "percent"),  # "fixed" or "percent"
        ("lot_size", 50),
        ("percent_capital", 0.10),
    )

    def __init__(self):
        self.vwap = VWAP(self.data, period=self.p.vwap_period)
        self.ma200 = bt.ind.SMA(self.data.close, period=self.p.ma_period)
        self.volume_avg = bt.ind.SMA(self.data.volume, period=self.p.volume_period)

        self.order = None
        self.entry_price = None
        self.trades = []

    def log(self, txt):
        """Log message with datetime."""
        dt = self.data.datetime.datetime(0)
        print(f"{dt.isoformat()} - {txt}")

    def notify_order(self, order):
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                self.log(f"BUY EXECUTED @ {order.executed.price:.2f}")
            else:
                self.log(f"SELL EXECUTED @ {order.executed.price:.2f}")

        self.order = None

    def notify_trade(self, trade):
        """Handle trade notifications."""
        if trade.isclosed:
            self.trades.append({
                "entry_date": bt.num2date(trade.dtopen),
                "exit_date": bt.num2date(trade.dtclose),
                "entry_price": trade.price,
                "exit_price": trade.price + trade.pnl / trade.size,
                "size": trade.size,
                "pnl": trade.pnl,
                "pnl_percent": (trade.pnl / (trade.price * abs(trade.size))) * 100,
            })

    def next(self):
        """Execute strategy logic on each bar."""
        if self.order:
            return

        if not self.position:
            # Entry conditions
            price_above_vwap = self.data.close[0] > self.vwap[0]
            price_above_ma = self.data.close[0] > self.ma200[0]
            volume_spike = self.data.volume[0] > self.volume_avg[0] * self.p.volume_mult

            if price_above_vwap and price_above_ma and volume_spike:
                # Calculate position size
                if self.p.position_type == "fixed":
                    size = self.p.lot_size
                else:
                    value = self.broker.getvalue() * self.p.percent_capital
                    size = int(value / self.data.close[0])

                if size > 0:
                    self.order = self.buy(size=size)
        else:
            # Exit conditions
            pnl_pct = (self.data.close[0] - self.entry_price) / self.entry_price

            if pnl_pct <= -self.p.stop_loss:
                self.log(f"STOP LOSS HIT @ {pnl_pct*100:.2f}%")
                self.order = self.sell(size=self.position.size)
            elif pnl_pct >= self.p.take_profit:
                self.log(f"TAKE PROFIT HIT @ {pnl_pct*100:.2f}%")
                self.order = self.sell(size=self.position.size)
```

**Step 4: Create backend/tests/test_strategy.py**

```python
"""Tests for trading strategy."""
from datetime import datetime

import backtrader as bt
import pytest

from app.strategies.vwap_ma_volume import VWAPMAVolumeStrategy


class MockData(bt.feeds.PandasData):
    """Mock data feed for testing."""
    pass


def test_strategy_initializes():
    """Test strategy can be instantiated."""
    cerebro = bt.Cerebro()
    cerebro.addstrategy(VWAPMAVolumeStrategy)

    # Verify strategy is added
    assert len(cerebro.strats) == 1


def test_strategy_params():
    """Test strategy has correct default params."""
    strategy_cls = VWAPMAVolumeStrategy
    assert strategy_cls.params.stop_loss == 0.02
    assert strategy_cls.params.take_profit == 0.04
    assert strategy_cls.params.ma_period == 200
```

**Step 5: Run tests**

```bash
docker compose exec backend pytest tests/test_strategy.py -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add VWAP+MA200+Volume strategy for Backtrader"
```

---

### Task 7: Backtest Runner

**Files:**
- Create: `backend/app/backtest/__init__.py`
- Create: `backend/app/backtest/runner.py`
- Create: `backend/app/backtest/schemas.py`
- Create: `backend/tests/test_runner.py`

**Step 1: Create backend/app/backtest/__init__.py**

```python
"""Backtest runner module."""
```

**Step 2: Create backend/app/backtest/schemas.py**

```python
"""Backtest request/response schemas."""
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    """Backtest request parameters."""
    ticker: str = Field(..., description="Stock ticker symbol")
    timeframe: str = Field(default="60min", description="Candle interval")
    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    risk_per_trade: float = Field(default=2.0, ge=0.1, le=10.0)
    stop_loss: float = Field(default=2.0, ge=0.1, le=20.0)
    take_profit: float = Field(default=4.0, ge=0.1, le=50.0)
    position_type: Literal["fixed", "percent"] = Field(default="percent")
    lot_size: int = Field(default=50, ge=1)
    percent_capital: float = Field(default=10.0, ge=1.0, le=100.0)
    starting_capital: float = Field(default=10000.0, ge=100.0)
    slippage: float = Field(default=0.1, ge=0.0, le=5.0)
    commission: float = Field(default=1.0, ge=0.0, le=50.0)


class TradeRecord(BaseModel):
    """Single trade record."""
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    size: int
    pnl: float
    pnl_percent: float
    trade_type: str = "BUY"


class BacktestMetrics(BaseModel):
    """Backtest performance metrics."""
    total_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    total_trades: int
    profit_factor: float
    risk_reward_ratio: float
    best_streak: int
    worst_streak: int


class EquityPoint(BaseModel):
    """Single equity curve point."""
    datetime: datetime
    equity: float


class BacktestResponse(BaseModel):
    """Backtest results."""
    request: BacktestRequest
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]
    drawdown_curve: list[EquityPoint]
    trades: list[TradeRecord]
```

**Step 3: Create backend/app/backtest/runner.py**

```python
"""Backtest runner using Backtrader."""
from datetime import datetime
import math

import backtrader as bt
import pandas as pd

from app.backtest.schemas import (
    BacktestRequest,
    BacktestResponse,
    BacktestMetrics,
    EquityPoint,
    TradeRecord,
)
from app.data.alpha_vantage import AlphaVantageClient
from app.strategies.vwap_ma_volume import VWAPMAVolumeStrategy


class EquityObserver(bt.Observer):
    """Observer to track equity over time."""

    lines = ("equity",)

    def next(self):
        self.lines.equity[0] = self._owner.broker.getvalue()


def calculate_metrics(
    initial_capital: float,
    final_capital: float,
    trades: list[dict],
    equity_values: list[float],
) -> BacktestMetrics:
    """Calculate performance metrics."""
    total_return = ((final_capital - initial_capital) / initial_capital) * 100

    if not trades:
        return BacktestMetrics(
            total_return=total_return,
            win_rate=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            total_trades=0,
            profit_factor=0.0,
            risk_reward_ratio=0.0,
            best_streak=0,
            worst_streak=0,
        )

    # Win rate
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    win_rate = (len(wins) / len(trades)) * 100 if trades else 0.0

    # Profit factor
    gross_profit = sum(t["pnl"] for t in wins) if wins else 0.0
    gross_loss = abs(sum(t["pnl"] for t in losses)) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0

    # Risk/Reward ratio
    avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(t["pnl"] for t in losses) / len(losses)) if losses else 0.0
    risk_reward = avg_win / avg_loss if avg_loss > 0 else 0.0

    # Max drawdown
    peak = initial_capital
    max_dd = 0.0
    for equity in equity_values:
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd:
            max_dd = dd

    # Sharpe ratio (simplified - assumes risk-free rate of 0)
    if len(equity_values) > 1:
        returns = pd.Series(equity_values).pct_change().dropna()
        if returns.std() > 0:
            sharpe = (returns.mean() / returns.std()) * math.sqrt(252)
        else:
            sharpe = 0.0
    else:
        sharpe = 0.0

    # Win/Loss streaks
    best_streak = 0
    worst_streak = 0
    current_win = 0
    current_loss = 0
    for t in trades:
        if t["pnl"] > 0:
            current_win += 1
            current_loss = 0
            best_streak = max(best_streak, current_win)
        else:
            current_loss += 1
            current_win = 0
            worst_streak = max(worst_streak, current_loss)

    return BacktestMetrics(
        total_return=round(total_return, 2),
        win_rate=round(win_rate, 1),
        max_drawdown=round(-max_dd, 2),
        sharpe_ratio=round(sharpe, 2),
        total_trades=len(trades),
        profit_factor=round(profit_factor, 2),
        risk_reward_ratio=round(risk_reward, 2),
        best_streak=best_streak,
        worst_streak=worst_streak,
    )


def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run backtest with given parameters.

    Args:
        request: Backtest configuration

    Returns:
        BacktestResponse with metrics, equity curve, and trades
    """
    # Fetch data
    client = AlphaVantageClient()
    stock_data = client.get_intraday_data(
        ticker=request.ticker,
        interval=request.timeframe,
        start_date=datetime.combine(request.start_date, datetime.min.time()),
        end_date=datetime.combine(request.end_date, datetime.max.time()),
    )

    if not stock_data.bars:
        raise ValueError(f"No data found for {request.ticker}")

    # Convert to DataFrame
    df = pd.DataFrame([
        {
            "datetime": bar.datetime,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
        }
        for bar in stock_data.bars
    ])
    df.set_index("datetime", inplace=True)

    # Setup Backtrader
    cerebro = bt.Cerebro()

    # Add data feed
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # Add strategy
    cerebro.addstrategy(
        VWAPMAVolumeStrategy,
        stop_loss=request.stop_loss / 100,
        take_profit=request.take_profit / 100,
        risk_per_trade=request.risk_per_trade / 100,
        position_type=request.position_type,
        lot_size=request.lot_size,
        percent_capital=request.percent_capital / 100,
    )

    # Broker settings
    cerebro.broker.setcash(request.starting_capital)
    cerebro.broker.setcommission(commission=request.commission)
    cerebro.broker.set_slippage_perc(request.slippage / 100)

    # Add observer for equity tracking
    cerebro.addobserver(EquityObserver)

    # Run backtest
    results = cerebro.run()
    strategy = results[0]

    # Extract equity curve
    equity_values = []
    equity_curve = []
    for i, dt in enumerate(df.index):
        equity = strategy.observers[0].lines.equity[i - len(df)]
        if not math.isnan(equity):
            equity_values.append(equity)
            equity_curve.append(EquityPoint(datetime=dt, equity=equity))

    # Calculate drawdown curve
    drawdown_curve = []
    peak = request.starting_capital
    for point in equity_curve:
        if point.equity > peak:
            peak = point.equity
        dd = ((peak - point.equity) / peak) * 100
        drawdown_curve.append(EquityPoint(datetime=point.datetime, equity=-dd))

    # Convert trades
    trades = [
        TradeRecord(
            entry_date=t["entry_date"],
            exit_date=t["exit_date"],
            entry_price=t["entry_price"],
            exit_price=t["exit_price"],
            size=t["size"],
            pnl=round(t["pnl"], 2),
            pnl_percent=round(t["pnl_percent"], 2),
        )
        for t in strategy.trades
    ]

    # Calculate metrics
    final_capital = cerebro.broker.getvalue()
    metrics = calculate_metrics(
        request.starting_capital,
        final_capital,
        strategy.trades,
        equity_values,
    )

    return BacktestResponse(
        request=request,
        metrics=metrics,
        equity_curve=equity_curve,
        drawdown_curve=drawdown_curve,
        trades=trades,
    )
```

**Step 4: Create backend/tests/test_runner.py**

```python
"""Tests for backtest runner."""
from datetime import date

import pytest

from app.backtest.schemas import BacktestRequest, BacktestMetrics
from app.backtest.runner import calculate_metrics


def test_backtest_request_defaults():
    """Test BacktestRequest has correct defaults."""
    req = BacktestRequest(
        ticker="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
    )
    assert req.timeframe == "60min"
    assert req.stop_loss == 2.0
    assert req.take_profit == 4.0
    assert req.starting_capital == 10000.0


def test_calculate_metrics_no_trades():
    """Test metrics calculation with no trades."""
    metrics = calculate_metrics(
        initial_capital=10000,
        final_capital=10000,
        trades=[],
        equity_values=[10000],
    )
    assert metrics.total_return == 0.0
    assert metrics.total_trades == 0
    assert metrics.win_rate == 0.0


def test_calculate_metrics_with_trades():
    """Test metrics calculation with trades."""
    trades = [
        {"pnl": 100},
        {"pnl": 50},
        {"pnl": -30},
        {"pnl": 80},
    ]
    metrics = calculate_metrics(
        initial_capital=10000,
        final_capital=10200,
        trades=trades,
        equity_values=[10000, 10100, 10150, 10120, 10200],
    )
    assert metrics.total_return == 2.0
    assert metrics.total_trades == 4
    assert metrics.win_rate == 75.0
```

**Step 5: Run tests**

```bash
docker compose exec backend pytest tests/test_runner.py -v
```

Expected: All tests pass.

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add backtest runner with metrics calculation"
```

---

### Task 8: Backtest API Endpoint

**Files:**
- Create: `backend/app/api/backtest.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

**Step 1: Create backend/app/api/backtest.py**

```python
"""Backtest API endpoints."""
from fastapi import APIRouter, HTTPException

from app.backtest.runner import run_backtest
from app.backtest.schemas import BacktestRequest, BacktestResponse

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
async def create_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    Run a backtest with the given parameters.

    Returns metrics, equity curve, and trade log.
    """
    try:
        result = run_backtest(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/tickers")
async def list_tickers():
    """
    List popular stock tickers.

    Note: Alpha Vantage supports any US stock ticker.
    """
    return {
        "popular": [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "META", "name": "Meta Platforms Inc."},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
        ]
    }
```

**Step 2: Update backend/app/main.py**

```python
"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, backtest

app = FastAPI(
    title="Trade_Bot API",
    description="Stock backtesting API with Backtrader",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(backtest.router, prefix="/api", tags=["backtest"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Trade_Bot API", "version": "1.0.0"}
```

**Step 3: Create backend/tests/test_api.py**

```python
"""Tests for API endpoints."""
from datetime import date

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check returns healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_tickers_endpoint():
    """Test tickers list returns popular stocks."""
    response = client.get("/api/tickers")
    assert response.status_code == 200
    data = response.json()
    assert "popular" in data
    assert len(data["popular"]) > 0
    assert data["popular"][0]["symbol"] == "AAPL"


def test_backtest_validation():
    """Test backtest validates request."""
    response = client.post("/api/backtest", json={})
    assert response.status_code == 422  # Validation error
```

**Step 4: Run tests**

```bash
docker compose exec backend pytest tests/test_api.py -v
```

Expected: All tests pass.

**Step 5: Rebuild and test API**

```bash
docker compose up -d --build backend
curl -X POST http://localhost:5000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","start_date":"2024-01-01","end_date":"2024-03-31"}'
```

Expected: Returns JSON with metrics, equity_curve, and trades.

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: add backtest API endpoint"
```

---

## Phase 3: Frontend - Dashboard

### Task 9: API Service

**Files:**
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/types/backtest.ts`

**Step 1: Create frontend/src/types/backtest.ts**

```typescript
export interface BacktestRequest {
  ticker: string
  timeframe: string
  start_date: string
  end_date: string
  risk_per_trade: number
  stop_loss: number
  take_profit: number
  position_type: 'fixed' | 'percent'
  lot_size: number
  percent_capital: number
  starting_capital: number
  slippage: number
  commission: number
}

export interface TradeRecord {
  entry_date: string
  exit_date: string
  entry_price: number
  exit_price: number
  size: number
  pnl: number
  pnl_percent: number
  trade_type: string
}

export interface BacktestMetrics {
  total_return: number
  win_rate: number
  max_drawdown: number
  sharpe_ratio: number
  total_trades: number
  profit_factor: number
  risk_reward_ratio: number
  best_streak: number
  worst_streak: number
}

export interface EquityPoint {
  datetime: string
  equity: number
}

export interface BacktestResponse {
  request: BacktestRequest
  metrics: BacktestMetrics
  equity_curve: EquityPoint[]
  drawdown_curve: EquityPoint[]
  trades: TradeRecord[]
}

export interface Ticker {
  symbol: string
  name: string
}

export const DEFAULT_SETTINGS: BacktestRequest = {
  ticker: 'AAPL',
  timeframe: '60min',
  start_date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0],
  risk_per_trade: 2,
  stop_loss: 2,
  take_profit: 4,
  position_type: 'percent',
  lot_size: 50,
  percent_capital: 10,
  starting_capital: 10000,
  slippage: 0.1,
  commission: 1,
}
```

**Step 2: Create frontend/src/services/api.ts**

```typescript
import { BacktestRequest, BacktestResponse, Ticker } from '../types/backtest'

const API_BASE = '/api'

export async function runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
  const response = await fetch(`${API_BASE}/backtest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Backtest failed')
  }

  return response.json()
}

export async function getTickers(): Promise<{ popular: Ticker[] }> {
  const response = await fetch(`${API_BASE}/tickers`)

  if (!response.ok) {
    throw new Error('Failed to fetch tickers')
  }

  return response.json()
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`)
    return response.ok
  } catch {
    return false
  }
}
```

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add API service and TypeScript types"
```

---

### Task 10: Settings Card Component

**Files:**
- Create: `frontend/src/components/SettingsCard.tsx`
- Create: `frontend/src/components/SettingsCard.css`
- Create: `frontend/src/components/Tooltip.tsx`
- Create: `frontend/src/components/Tooltip.css`

**Step 1: Create frontend/src/components/Tooltip.tsx**

```tsx
import { useState, useRef, useEffect } from 'react'
import './Tooltip.css'

interface TooltipProps {
  text: string
}

export function Tooltip({ text }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const tooltipRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target as Node)) {
        setIsVisible(false)
      }
    }

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isVisible])

  return (
    <div className="tooltip-container" ref={tooltipRef}>
      <button
        className="tooltip-trigger"
        onClick={() => setIsVisible(!isVisible)}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        aria-label="Help"
      >
        ?
      </button>
      {isVisible && (
        <div className="tooltip-content">
          {text}
        </div>
      )}
    </div>
  )
}
```

**Step 2: Create frontend/src/components/Tooltip.css**

```css
.tooltip-container {
  position: relative;
  display: inline-block;
  margin-left: 0.5rem;
}

.tooltip-trigger {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  color: var(--text-color);
  font-size: 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tooltip-trigger:hover {
  background: var(--primary-color);
  color: white;
}

.tooltip-content {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.5rem;
  font-size: 0.875rem;
  width: 200px;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin-bottom: 0.5rem;
}

.tooltip-content::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--border-color);
}
```

**Step 3: Create frontend/src/components/SettingsCard.tsx**

```tsx
import { useState } from 'react'
import { BacktestRequest, DEFAULT_SETTINGS } from '../types/backtest'
import { Tooltip } from './Tooltip'
import './SettingsCard.css'

interface SettingsCardProps {
  settings: BacktestRequest
  onSettingsChange: (settings: BacktestRequest) => void
  onRunBacktest: () => void
  isLoading: boolean
}

const TOOLTIPS = {
  ticker: 'Stock symbol to backtest (e.g., AAPL, TSLA). Only US stocks supported.',
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

      {!isCollapsed && (
        <div className="settings-content">
          <div className="settings-section">
            <h3>Stock</h3>
            <div className="setting-row">
              <label>
                Ticker
                <Tooltip text={TOOLTIPS.ticker} />
              </label>
              <input
                type="text"
                value={settings.ticker}
                onChange={(e) => updateSetting('ticker', e.target.value.toUpperCase())}
              />
            </div>
          </div>

          <div className="settings-section">
            <h3>Timeframe</h3>
            <div className="setting-row">
              <label>
                Candle
                <Tooltip text={TOOLTIPS.timeframe} />
              </label>
              <select
                value={settings.timeframe}
                onChange={(e) => updateSetting('timeframe', e.target.value)}
              >
                <option value="15min">15 min</option>
                <option value="30min">30 min</option>
                <option value="60min">1 hour</option>
              </select>
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

      <button
        className="run-backtest-btn"
        onClick={onRunBacktest}
        disabled={isLoading}
      >
        {isLoading ? 'Running...' : 'Run Backtest'}
      </button>
    </div>
  )
}
```

**Step 4: Create frontend/src/components/SettingsCard.css**

```css
.settings-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  min-width: 280px;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  margin-bottom: 1rem;
}

.settings-header h2 {
  font-size: 1.25rem;
  margin: 0;
}

.collapse-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: var(--text-color);
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.settings-section h3 {
  font-size: 0.875rem;
  text-transform: uppercase;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.setting-row label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
}

.setting-row input[type="text"],
.setting-row input[type="number"],
.setting-row input[type="date"],
.setting-row select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 0.875rem;
  width: 120px;
}

.setting-row input[type="radio"] {
  margin-right: 0.25rem;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.input-with-unit input {
  width: 80px !important;
}

.input-with-unit span {
  font-size: 0.875rem;
  color: var(--text-color);
}

.run-backtest-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
  min-height: 44px;
}

.run-backtest-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.run-backtest-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media screen and (max-width: 768px) {
  .settings-card {
    min-width: 100%;
  }

  .setting-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .setting-row input,
  .setting-row select {
    width: 100% !important;
  }

  .input-with-unit {
    width: 100%;
  }

  .input-with-unit input {
    flex: 1;
  }
}
```

**Step 5: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add SettingsCard component with tooltips"
```

---

### Task 11: Metrics Display Component

**Files:**
- Create: `frontend/src/components/MetricsCard.tsx`
- Create: `frontend/src/components/MetricsCard.css`

**Step 1: Create frontend/src/components/MetricsCard.tsx**

```tsx
import { BacktestMetrics } from '../types/backtest'
import './MetricsCard.css'

interface MetricsCardProps {
  metrics: BacktestMetrics | null
}

export function MetricsCard({ metrics }: MetricsCardProps) {
  if (!metrics) {
    return (
      <div className="metrics-card empty">
        <p>Run a backtest to see metrics</p>
      </div>
    )
  }

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(1)}%`
  }

  const getColorClass = (value: number, inverse = false) => {
    if (inverse) {
      return value < 0 ? 'positive' : value > 0 ? 'negative' : ''
    }
    return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
  }

  return (
    <div className="metrics-card">
      <h3>Performance Metrics</h3>
      <div className="metrics-grid">
        <div className="metric">
          <span className="metric-label">Return</span>
          <span className={`metric-value ${getColorClass(metrics.total_return)}`}>
            {formatPercent(metrics.total_return)}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Win Rate</span>
          <span className="metric-value">{metrics.win_rate.toFixed(1)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Max DD</span>
          <span className={`metric-value ${getColorClass(metrics.max_drawdown, true)}`}>
            {formatPercent(metrics.max_drawdown)}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Sharpe</span>
          <span className="metric-value">{metrics.sharpe_ratio.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Trades</span>
          <span className="metric-value">{metrics.total_trades}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Profit Factor</span>
          <span className="metric-value">{metrics.profit_factor.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">R:R Ratio</span>
          <span className="metric-value">{metrics.risk_reward_ratio.toFixed(2)}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Best Streak</span>
          <span className="metric-value positive">{metrics.best_streak}W</span>
        </div>
        <div className="metric">
          <span className="metric-label">Worst Streak</span>
          <span className="metric-value negative">{metrics.worst_streak}L</span>
        </div>
      </div>
    </div>
  )
}
```

**Step 2: Create frontend/src/components/MetricsCard.css**

```css
.metrics-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
}

.metrics-card.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
  color: var(--text-color);
  opacity: 0.6;
}

.metrics-card h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.metric-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-color);
  opacity: 0.7;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: bold;
}

.metric-value.positive {
  color: var(--success-color);
}

.metric-value.negative {
  color: var(--danger-color);
}

@media screen and (max-width: 576px) {
  .metrics-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .metric-value {
    font-size: 1rem;
  }
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add MetricsCard component"
```

---

### Task 12: Equity Chart Component

**Files:**
- Create: `frontend/src/components/EquityChart.tsx`
- Create: `frontend/src/components/EquityChart.css`

**Step 1: Create frontend/src/components/EquityChart.tsx**

```tsx
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
```

**Step 2: Create frontend/src/components/EquityChart.css**

```css
.equity-chart {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
}

.equity-chart.empty {
  min-height: 300px;
  display: flex;
  flex-direction: column;
}

.empty-message {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-color);
  opacity: 0.6;
}

.chart-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.chart-tabs button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-color);
  color: var(--text-color);
  cursor: pointer;
  min-height: 44px;
}

.chart-tabs button.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.chart-tabs button:hover:not(.active) {
  background: var(--card-bg);
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add EquityChart component with Plotly"
```

---

### Task 13: Trade Log Component

**Files:**
- Create: `frontend/src/components/TradeLog.tsx`
- Create: `frontend/src/components/TradeLog.css`

**Step 1: Create frontend/src/components/TradeLog.tsx**

```tsx
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
```

**Step 2: Create frontend/src/components/TradeLog.css**

```css
.trade-log {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
}

.trade-log.empty {
  min-height: 150px;
}

.trade-log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.trade-log-header h3 {
  font-size: 1rem;
  margin: 0;
}

.trade-log-header button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-color);
  color: var(--text-color);
  cursor: pointer;
  min-height: 44px;
}

.trade-log-header button:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
}

.trade-log-header button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-message {
  color: var(--text-color);
  opacity: 0.6;
  text-align: center;
  padding: 2rem;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

th, td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  color: var(--text-color);
  opacity: 0.7;
}

.trade-type {
  color: var(--primary-color);
  font-weight: 600;
}

.positive {
  color: var(--success-color);
}

.negative {
  color: var(--danger-color);
}

@media screen and (max-width: 576px) {
  table {
    font-size: 0.75rem;
  }

  th, td {
    padding: 0.375rem;
  }
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/
git commit -m "feat: add TradeLog component with CSV export"
```

---

### Task 14: Dashboard Integration

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/App.css`

**Step 1: Update frontend/src/App.tsx**

```tsx
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
  const [chartTab, setChartTab] = useState<'equity' | 'drawdown'>('equity')

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
          <MetricsCard metrics={result?.metrics || null} />

          <EquityChart
            equityCurve={result?.equity_curve || []}
            drawdownCurve={result?.drawdown_curve || []}
            trades={result?.trades || []}
            activeTab={chartTab}
            onTabChange={setChartTab}
            darkMode={darkMode}
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
```

**Step 2: Update frontend/src/App.css**

```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background: var(--bg-color);
  z-index: 100;
}

.header h1 {
  font-size: 1.5rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.theme-toggle {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.5rem;
  font-size: 1.25rem;
  cursor: pointer;
  min-width: 44px;
  min-height: 44px;
}

.error-banner {
  background: var(--danger-color);
  color: white;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-banner button {
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
}

.dashboard {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1rem;
}

.sidebar {
  flex-shrink: 0;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

@media screen and (max-width: 992px) {
  .dashboard {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }
}
```

**Step 3: Rebuild and test**

```bash
docker compose up -d --build
```

Open http://localhost:3000 and verify:
- Settings card displays with all fields
- Dark mode toggle works
- Run Backtest button triggers API call (may fail without valid API key)

**Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: integrate dashboard with all components"
```

---

## Phase 4: Testing & Polish

### Task 15: Playwright E2E Tests

**Files:**
- Create: `tests/e2e/dashboard.spec.ts`
- Create: `tests/e2e/playwright.config.ts`

**Step 1: Verify Playwright MCP is running**

```bash
docker compose ps
```

Expected: trade-bot-playwright container is running.

**Step 2: Test with Playwright MCP**

Using the Playwright MCP tools:

```
Navigate to http://frontend:80
Verify page title contains "Trade_Bot"
Verify Settings card is visible
Verify Run Backtest button is visible
Click theme toggle
Verify dark mode class is applied
```

**Step 3: Commit**

```bash
git add tests/
git commit -m "test: add Playwright E2E test configuration"
```

---

### Task 16: Final Polish

**Files:**
- Verify all components work together
- Test responsive design
- Fix any issues

**Step 1: Test desktop layout**

Open http://localhost:3000 at 1200px width:
- Settings card on left sidebar
- Content area with metrics, chart, trade log on right

**Step 2: Test mobile layout**

Resize to 576px width:
- Single column layout
- Settings card collapses
- No horizontal scrolling

**Step 3: Test dark mode**

Toggle dark mode:
- All colors switch correctly
- Charts update with dark theme

**Step 4: Final commit**

```bash
git add .
git commit -m "chore: final polish and responsive design verification"
```

---

## Summary

This plan implements the Trade_Bot in 16 tasks:

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-4 | Docker infrastructure, backend/frontend scaffolding |
| 2 | 5-8 | Backend data layer, strategy, backtest runner, API |
| 3 | 9-14 | Frontend components and dashboard integration |
| 4 | 15-16 | E2E testing and polish |

**Key files created:**
- `docker-compose.yml` - Container orchestration
- `backend/app/` - FastAPI + Backtrader
- `frontend/src/` - React PWA dashboard
- `.mcp.json` - Playwright MCP configuration

**Dependencies:**
- Alpha Vantage API key required
- Docker and Docker Compose
- Node.js 20+ (for frontend build)
- Python 3.11+ (for backend)
