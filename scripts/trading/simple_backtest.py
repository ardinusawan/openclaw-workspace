#!/usr/bin/env python3
"""
Simple Backtesting Engine for Indonesian Banking Stocks
Implements backtesting framework with multiple momentum-based strategies

Backtesting Components:
1. Data Loader - Load historical data from yfinance
2. Strategy Implementation - Entry/exit logic for swing trading
3. Backtesting Engine - Run trades against historical data
4. Performance Metrics - Calculate ROI, Sharpe, Max DD, Win rate, etc.
5. Visualization - Plot equity curve, drawdown chart, trade distribution

Supported Strategies:
1. RSI Divergence - Momentum reversal strategy
2. MACD Histogram - Momentum confirmation
3. Bollinger Bands - Volatility breakout
4. ATR Trailing Stop - Risk management
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

class StockBacktester:
    """Simple backtesting engine for Indonesian stocks"""

    def __init__(self):
        self.data = pd.DataFrame()
        self.trades = pd.DataFrame()
        self.equity = pd.Series()
        self.drawdowns = pd.Series()

    def download_data(self, ticker, start_date="2015-01-01", end_date=datetime.now()):
        """Download historical data from Yahoo Finance"""
        print(f"📥 Downloading {ticker} from {start_date} to {end_date}")

        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            print(f"   ❌ No data found for {ticker}")
            return None

        # Add technical indicators
        hist['RSI'] = self.calculate_rsi(hist['Close'], period=14)
        hist['MACD'], hist['MACD_Signal'], hist['MACD_Hist'] = self.calculate_macd(hist['Close'])
        hist['BB_Upper'], hist['BB_Mid'], hist['BB_Lower'] = self.calculate_bollinger_bands(hist['Close'], period=20, std_dev=2)
        hist['ATR'] = self.calculate_atr(hist, period=14)

        print(f"   ✅ Downloaded {len(hist)} days of data")
        print(f"   Date range: {hist.index[0]} to {hist.index[-1]}")

        self.data = hist
        return hist

    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0).rolling(window=period).mean())
        loss = (-delta.where(delta < 0, 0).rolling(window=period).mean())

        rs = 100 - (100 / (1 + gain / loss))
        return rs

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return macd, signal_line, histogram

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        middle_band = sma

        return upper_band, middle_band, lower_band

    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range"""
        high_low = high - low
        high_low_ma = high_low.rolling(window=period).mean()

        return high_low_ma

    def run_backtest(self, strategy_name="rsi_divergence", initial_capital=100000000, position_size=None, stop_loss_pct=0.025, take_profit_pct=0.04):
        """Run backtest on historical data"""

        if self.data.empty:
            print("❌ No data available for backtesting")
            return None

        print(f"\n🔄 Running Backtest: {strategy_name}")
        print(f"   Initial Capital: Rp {initial_capital:,} ({initial_capital / 1e6:.2f} Juta)")
        print(f"   Stop Loss: {stop_loss_pct * 100:.1f}%")
        print(f"   Take Profit: {take_profit_pct * 100:.1f}%")

        # Initialize variables
        cash = initial_capital
        position = None  # 'long' or 'short' or None
        entry_price = 0
        quantity = 0
        trades = []

        # Strategy parameters
        if strategy_name == "rsi_divergence":
            rsi_oversold = 30
            rsi_overbought = 70
            rsi_period = 14
        else:
            rsi_oversold = 30
            rsi_overbought = 70
            rsi_period = 14

        # Run through each day
        for date, row in self.data.iterrows():
            price = row['Close']
            rsi = row['RSI']
            volume = row.get('Volume', 0)

            # Entry logic (Long)
            if position is None:
                # RSI Divergence strategy
                if rsi < rsi_oversold and (rsi > rsi_oversold):
                    # Enter long position
                    if position_size:
                        quantity = int((cash * position_size) / price)
                    else:
                        quantity = int(cash / price)

                    entry_price = price
                    cash = cash - (quantity * price)
                    position = 'long'
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': price,
                        'quantity': quantity,
                        'type': 'LONG',
                        'rsi': rsi
                    })
                elif rsi > rsi_overbought and (rsi < rsi_overbought):
                    # Enter short position (optional, for swing trading focus on long)
                    pass

            # Exit logic (Long)
            elif position == 'long':
                # RSI Overbought
                if rsi > rsi_overbought:
                    # Take profit
                    cash = cash + (quantity * price)
                    trades.append({
                        'date': date,
                        'action': 'SELL',
                        'price': price,
                        'quantity': quantity,
                        'type': 'PROFIT',
                        'pnl': (price - entry_price) * quantity,
                        'rsi': rsi
                    })
                    position = None
                    entry_price = 0
                    quantity = 0

                # Stop Loss
                elif price < (entry_price * (1 - stop_loss_pct)):
                    # Stop loss
                    cash = cash + (quantity * price)
                    trades.append({
                        'date': date,
                        'action': 'SELL',
                        'price': price,
                        'quantity': quantity,
                        'type': 'LOSS',
                        'pnl': (price - entry_price) * quantity,
                        'rsi': rsi
                    })
                    position = None
                    entry_price = 0
                    quantity = 0

                # Take Profit (aggressive)
                elif price > (entry_price * (1 + take_profit_pct)):
                    # Take profit
                    cash = cash + (quantity * price)
                    trades.append({
                        'date': date,
                        'action': 'SELL',
                        'price': price,
                        'quantity': quantity,
                        'type': 'PROFIT',
                        'pnl': (price - entry_price) * quantity,
                        'rsi': rsi
                    })
                    position = None
                    entry_price = 0
                    quantity = 0

        # Calculate performance metrics
        trades_df = pd.DataFrame(trades)

        if trades_df.empty:
            print("❌ No trades generated")
            return None

        # Calculate total P&L
        total_pnl = trades_df['pnl'].sum()

        # Calculate total return
        total_return = (total_pnl / initial_capital) * 100

        # Calculate win rate
        winning_trades = trades_df[trades_df['type'] == 'PROFIT']
        win_rate = (len(winning_trades) / len(trades_df)) * 100

        # Calculate maximum drawdown
        equity_curve = []
        equity = initial_capital

        for trade in trades_df:
            if trade['action'] == 'BUY':
                equity -= (trade['quantity'] * trade['price'])
            elif trade['action'] == 'SELL':
                equity += (trade['quantity'] * trade['price'])
                equity += trade['pnl']

            equity_curve.append(equity)

        equity_series = pd.Series(equity_curve)
        max_drawdown = 0

        for i in range(1, len(equity_series)):
            if equity_series[i] >= equity_series[i-1]:
                max_drawdown = max(max_drawdown, 0)
            elif equity_series[i] < equity_series[i-1]:
                dd = (equity_series[i-1] - equity_series[i]) / equity_series[i-1]
                max_drawdown = max(max_drawdown, dd)

        max_drawdown_pct = max_drawdown * 100

        # Calculate Sharpe ratio (simplified, assuming 0% risk-free rate)
        daily_returns = equity_series.pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)) if len(daily_returns) > 0 else 0

        # Calculate Profit Factor
        winning_trades_pnl = winning_trades['pnl'].sum()
        losing_trades_pnl = trades_df[trades_df['type'] == 'LOSS']['pnl'].sum()
        profit_factor = abs(winning_trades_pnl) / abs(losing_trades_pnl) if losing_trades_pnl != 0 else 0

        # Create equity curve dataframe
        equity_df = pd.DataFrame({
            'Date': [t['date'] for t in trades if t['action'] in ['SELL']],
            'Equity': [equity_series[i-1] for i in range(1, len(equity_series))]
        })

        # Print summary
        print(f"\n" + "=" * 60)
        print(f"📊 BACKTEST RESULTS: {strategy_name.upper()}")
        print("=" * 60)
        print(f"Initial Capital: Rp {initial_capital:,} ({initial_capital / 1e6:.2f} Juta)")
        print(f"Final Capital: Rp {cash:,} ({cash / 1e6:.2f} Juta)")
        print(f"Total P&L: Rp {total_pnl:,} ({total_pnl / 1e6:.2f} Juta)")
        print(f"Total Return: {total_return:.2f}%")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Max Drawdown: {max_drawdown_pct:.2f}%")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Total Trades: {len(trades)}")
        print(f"Winning Trades: {len(winning_trades)}")
        print(f"Losing Trades: {len(trades_df[trades_df['type'] == 'LOSS'])}")
        print("=" * 60)

        return {
            'initial_capital': initial_capital,
            'final_capital': cash,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': profit_factor,
            'trades': trades_df,
            'equity_curve': equity_df
        }

def main():
    """Main function to run backtest"""
    print("=" * 60)
    print("📈 Simple Backtesting Engine - Indonesian Banking Stocks")
    print("=" * 60)

    # Indonesian Banking Stocks to test
    tickers = ['BMRI.JK', 'BBRI.JK', 'BBCA.JK']

    initial_capital = 100000000  # 100 Juta Rupiah

    print(f"\n📊 Stocks to Backtest: {', '.join(tickers)}")
    print(f"📊 Initial Capital: Rp {initial_capital:,} ({initial_capital / 1e6:.2f} Juta)")
    print(f"📊 Time Range: 2015-01-01 to {datetime.now().strftime('%Y-%m-%d')}")

    # Initialize backtester
    backtester = StockBacktester()

    # Run backtest for each stock
    results = {}

    for ticker in tickers:
        print(f"\n{'=' * 60}")
        print(f"📥 Backtesting {ticker}")
        print(f"{'=' * 60}")

        # Download data
        data = backtester.download_data(ticker)

        if data is None:
            continue

        # Run backtest with RSI divergence strategy
        result = backtester.run_backtest(
            strategy_name="rsi_divergence",
            initial_capital=initial_capital,
            position_size=0.2  # 20% position sizing
            stop_loss_pct=0.025,  # 2.5% stop loss
            take_profit_pct=0.04  # 4% take profit
        )

        if result is None:
            continue

        results[ticker] = result

    # Print comparison summary
    print(f"\n" + "=" * 60)
    print("📊 BACKTEST COMPARISON SUMMARY")
    print("=" * 60)

    for ticker, result in results.items():
        if result:
            print(f"\n{ticker}:")
            print(f"  Total Return: {result['total_return']:.2f}%")
            print(f"  Win Rate: {result['win_rate']:.2f}%")
            print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
            print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")
            print(f"  Total Trades: {len(result['trades'])}")

    print("\n" + "=" * 60)
    print("✅ Backtest Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
