#!/usr/bin/env python3
"""
Simple Backtesting Engine for Indonesian Banking Stocks (FIXED - CSV OUTPUT)
Implements backtesting framework with CSV export for all results

Backtesting Components:
1. Data Loader - Load historical data from yfinance
2. Strategy Implementation - Entry/exit logic for swing trading
3. Backtesting Engine - Run trades against historical data
4. Performance Metrics - Calculate ROI, Sharpe, Max DD, Win rate, etc.
5. CSV Export - Save all results to CSV files
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
import sys
import os

class StockBacktester:
    """Simple backtesting engine for Indonesian stocks with CSV export"""

    def __init__(self):
        self.data = pd.DataFrame()
        self.trades = pd.DataFrame()
        self.equity_curve = pd.DataFrame()
        self.drawdowns = pd.Series()
        self.output_dir = "/tmp"

    def download_data(self, ticker, start_date="2015-01-01", end_date=datetime.now()):
        """Download historical data from Yahoo Finance"""
        print(f"📥 Downloading {ticker} from {start_date} to {end_date}")

        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)

            if hist.empty:
                print(f"   ❌ No data found for {ticker}")
                return None

            # Reset index
            hist.index = hist.index.tz_localize(None).tz_localize('Asia/Jakarta')

            # Ensure OHLCV columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in hist.columns]

            if missing_columns:
                print(f"   ⚠️  Missing columns: {missing_columns}")
                return None

            # Remove NaN values
            hist = hist[required_columns].dropna()

            # Remove zero volume rows (possible data errors)
            hist = hist[hist['Volume'] > 0]

            print(f"   ✅ Downloaded {len(hist)} days of data")
            print(f"   Date range: {hist.index[0]} to {hist.index[-1]}")

            self.data = hist
            return hist

        except Exception as e:
            print(f"   ❌ Error downloading {ticker}: {str(e)}")
            return None

    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

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

    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range (Volatility)"""
        high_low = high - low
        true_range = high_low.rolling(window=period).mean()

        return true_range

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        middle_band = sma

        # Bandwidth: (upper - lower) / middle
        bandwidth = (upper_band - lower_band) / middle_band

        return upper_band, middle_band, lower_band, bandwidth

    def run_backtest(self, strategy_name="rsi_divergence", initial_capital=100000000, position_size=0.2, stop_loss_pct=0.025, take_profit_pct=0.04):
        """Run backtest on historical data and export to CSV"""

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
        entry_date = None
        quantity = 0
        trades = []
        equity_curve = []

        # Strategy parameters
        if strategy_name == "rsi_divergence":
            rsi_oversold = 30
            rsi_overbought = 70
            rsi_period = 14
        else:
            rsi_oversold = 30
            rsi_overbought = 70
            rsi_period = 14

        # Add technical indicators to data
        self.data['RSI'] = self.calculate_rsi(self.data['Close'], period=14)
        self.data['MACD'], self.data['MACD_Signal'], self.data['MACD_Hist'] = self.calculate_macd(self.data['Close'])
        self.data['ATR'] = self.calculate_atr(self.data['High'], self.data['Low'], self.data['Close'])
        self.data['BB_Upper'], self.data['BB_Mid'], self.data['BB_Lower'], self.data['Bandwidth'] = self.calculate_bollinger_bands(self.data['Close'])

        # Run through each day
        for date, row in self.data.iterrows():
            price = row['Close']
            rsi = row['RSI']

            # Entry logic (Long)
            if position is None:
                # RSI Divergence strategy
                if rsi < rsi_oversold and (rsi > rsi_oversold):
                    # Enter long position
                    quantity = int((cash * position_size) / price)

                    entry_price = price
                    entry_date = date
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
                        'hold_days': (date - entry_date).days if entry_date else 0,
                        'rsi': rsi
                    })

                    position = None
                    entry_price = 0
                    quantity = 0
                    entry_date = None

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
                        'hold_days': (date - entry_date).days if entry_date else 0,
                        'rsi': rsi
                    })

                    position = None
                    entry_price = 0
                    quantity = 0
                    entry_date = None

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
                        'hold_days': (date - entry_date).days if entry_date else 0,
                        'rsi': rsi
                    })

                    position = None
                    entry_price = 0
                    quantity = 0
                    entry_date = None

            # Calculate equity at each day (for drawdown)
            if position == 'long':
                equity = cash + (quantity * price)
            else:
                equity = cash

            equity_curve.append({
                'date': date,
                'equity': equity
            })

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
        equity_series = pd.Series([row['equity'] for row in equity_curve])
        max_drawdown = 0

        for i in range(1, len(equity_series)):
            if equity_series[i] >= equity_series[i-1]:
                max_drawdown = max(max_drawdown, 0)
            elif equity_series[i] < equity_series[i-1]:
                dd = (equity_series[i-1] - equity_series[i]) / equity_series[i-1]
                max_drawdown = max(max_drawdown, dd)

        max_drawdown_pct = max_drawdown * 100

        # Calculate Sharpe ratio
        daily_returns = equity_series.pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252)) if len(daily_returns) > 0 else 0

        # Calculate Profit Factor
        winning_trades_pnl = winning_trades['pnl'].sum()
        losing_trades_pnl = trades_df[trades_df['type'] == 'LOSS']['pnl'].sum()
        profit_factor = abs(winning_trades_pnl) / abs(losing_trades_pnl) if losing_trades_pnl != 0 else 0

        # Create equity curve dataframe
        equity_df = pd.DataFrame(equity_curve)

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

        # Export to CSV files
        self.export_to_csv(trades_df, equity_df, total_pnl, total_return, win_rate, max_drawdown_pct, sharpe_ratio, profit_factor)

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

    def export_to_csv(self, trades_df, equity_df, total_pnl, total_return, win_rate, max_drawdown_pct, sharpe_ratio, profit_factor):
        """Export all results to CSV files"""
        print(f"\n📄 Exporting results to CSV...")

        # 1. Backtest Summary CSV
        summary_file = os.path.join(self.output_dir, 'backtest_summary.csv')
        with open(summary_file, 'w', newline='') as csvfile:
            fieldnames = ['date', 'stock', 'initial_capital', 'final_capital', 'total_pnl', 'total_return_pct', 'win_rate', 'max_drawdown_pct', 'sharpe_ratio', 'profit_factor', 'total_trades']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            today = datetime.now().strftime('%Y-%m-%d')

            for i, (ticker, result) in enumerate(self.backtest_results.items(), 1):
                writer.writerow({
                    'date': today,
                    'stock': ticker,
                    'initial_capital': result['initial_capital'],
                    'final_capital': result['final_capital'],
                    'total_pnl': result['total_pnl'],
                    'total_return_pct': result['total_return'],
                    'win_rate': result['win_rate'],
                    'max_drawdown_pct': result['max_drawdown'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'profit_factor': result['profit_factor'],
                    'total_trades': len(result['trades'])
                })

        print(f"   ✅ Backtest Summary: {summary_file}")

        # 2. Trade Log CSV
        trade_log_file = os.path.join(self.output_dir, 'backtest_trade_log.csv')

        with open(trade_log_file, 'w', newline='') as csvfile:
            fieldnames = ['stock', 'date', 'action', 'price', 'quantity', 'type', 'pnl', 'hold_days', 'rsi']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for ticker, result in self.backtest_results.items():
                for _, trade in result['trades'].iterrows():
                    writer.writerow({
                        'stock': ticker,
                        'date': trade['date'],
                        'action': trade['action'],
                        'price': trade['price'],
                        'quantity': trade['quantity'],
                        'type': trade['type'],
                        'pnl': trade['pnl'],
                        'hold_days': trade['hold_days'],
                        'rsi': trade['rsi']
                    })

        print(f"   ✅ Trade Log: {trade_log_file}")

        # 3. Equity Curve CSV
        equity_curve_file = os.path.join(self.output_dir, 'backtest_equity_curve.csv')

        with open(equity_curve_file, 'w', newline='') as csvfile:
            fieldnames = ['stock', 'date', 'equity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for ticker, result in self.backtest_results.items():
                for _, row in result['equity_curve'].iterrows():
                    writer.writerow({
                        'stock': ticker,
                        'date': row['date'],
                        'equity': row['equity']
                    })

        print(f"   ✅ Equity Curve: {equity_curve_file}")

        print(f"\n📊 All results exported to CSV:")
        print(f"   1. {summary_file}")
        print(f"   2. {trade_log_file}")
        print(f"   3. {equity_curve_file}")

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
    print(f"📊 Time Range: 2015-01-01 to {datetime.now().strftime('%Y-%m-%d')} (last 11 years)")

    # Initialize backtester
    backtester = StockBacktester()

    # Download data for all stocks
    for ticker in tickers:
        print(f"\n{'=' * 60}")
        print(f"📥 Downloading {ticker}")
        print(f"{'=' * 60}")

        data = backtester.download_data(ticker)

        if data is None:
            continue

        # Add technical indicators to data
        data['RSI'] = backtester.calculate_rsi(data['Close'], period=14)
        data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = backtester.calculate_macd(data['Close'])
        data['ATR'] = backtester.calculate_atr(data['High'], data['Low'], data['Close'])
        data['BB_Upper'], data['BB_Mid'], data['BB_Lower'], data['Bandwidth'] = backtester.calculate_bollinger_bands(data['Close'])

        # Run backtest for each stock
        print(f"\n{'=' * 60}")
        print(f"🔄 Running Backtest: RSI DIVERGENCE")
        print(f"{'=' * 60}")

        result = backtester.run_backtest(
            strategy_name="rsi_divergence",
            initial_capital=initial_capital,
            position_size=0.2,  # 20% position sizing
            stop_loss_pct=0.025,  # 2.5% stop loss
            take_profit_pct=0.04  # 4% take profit
        )

        if result is None:
            continue

        # Store result
        backtester.backtest_results = {}
        backtester.backtest_results[ticker] = result

    # Print comparison summary
    print(f"\n" + "=" * 60)
    print("📊 BACKTEST COMPARISON SUMMARY")
    print("=" * 60)

    for ticker, result in backtester.backtest_results.items():
        if result:
            print(f"\n{ticker}:")
            print(f"  Total Return: {result['total_return']:.2f}%")
            print(f"  Win Rate: {result['win_rate']:.2f}%")
            print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")
            print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")
            print(f"  Total Trades: {len(result['trades'])}")

    print("\n" + "=" * 60)
    print("✅ BACKTEST COMPLETE!")
    print("=" * 60)
    print(f"\n📊 CSV FILES CREATED:")
    print(f"   /tmp/backtest_summary.csv")
    print(f"   /tmp/backtest_trade_log.csv")
    print(f"   /tmp/backtest_equity_curve.csv")

    print(f"\n💡 Next Steps:")
    print(f"   1. Review CSV files for detailed analysis")
    print(f"   2. Compare performance across BMRI, BBRI, BBCA")
    print(f"   3. Optimize parameters for best performing stock")
    print(f"   4. Run forward testing (paper trading) with live data")
    print(f"   5. Scale to more stocks once strategy is validated")

if __name__ == "__main__":
    main()
