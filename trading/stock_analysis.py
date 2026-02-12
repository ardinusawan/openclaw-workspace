#!/usr/bin/env python3
"""
Comprehensive Stock Analysis for Indonesian Stocks
Analyzes BMRI, BBCA, BBRI, UNTR with weekly charts
Provides buy/sell signals with price levels
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = None
        self.current_price = 0
        self.prev_price = 0
        self.weekly_change = 0

    def fetch_data(self):
        """Fetch stock data from Yahoo Finance with retry logic"""
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(period="2y", interval="1wk", timeout=30)

            if self.data.empty:
                return False, "No data available"

            self.current_price = self.data['Close'].iloc[-1]
            self.prev_price = self.data['Close'].iloc[-2]
            self.weekly_change = ((self.current_price - self.prev_price) / self.prev_price) * 100

            return True, "Success"

        except Exception as e:
            if "timeout" in str(e).lower() or "resolving" in str(e).lower():
                return False, "Connection timeout - retrying..."
            return False, str(e)

    def calculate_rsi(self, period=14):
        """Calculate RSI indicator"""
        close_prices = self.data['Close'].tolist()
        if len(close_prices) < period + 1:
            return None

        gains = []
        losses = []

        for i in range(1, len(close_prices)):
            change = close_prices[i] - close_prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

    def calculate_sma(self, period):
        """Calculate Simple Moving Average"""
        close_prices = self.data['Close'].tolist()
        if len(close_prices) < period:
            return None
        return round(sum(close_prices[-period:]) / period, 2)

    def calculate_ema(self, period):
        """Calculate Exponential Moving Average"""
        close_prices = self.data['Close'].tolist()
        if len(close_prices) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = [close_prices[0]]
        for price in close_prices[1:]:
            ema.append(round((price * multiplier) + (ema[-1] * (1 - multiplier)), 2))
        return ema[-1]

    def calculate_macd(self, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        close_prices = self.data['Close'].tolist()
        if len(close_prices) < slow:
            return None, None, None

        ema_fast = self.calculate_ema(fast)
        ema_slow = self.calculate_ema(slow)

        if ema_fast is None or ema_slow is None:
            return None, None, None

        macd_line = ema_fast - ema_slow

        # Calculate MACD histogram based on recent prices
        recent_prices = close_prices[-signal:]
        if len(recent_prices) < signal:
            return round(macd_line, 2), None, None

        # Simple signal line calculation
        avg_change = sum(recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))) / (len(recent_prices) - 1)
        signal_line = avg_change
        histogram = macd_line - signal_line

        return round(macd_line, 2), round(signal_line, 2) if signal_line else 0, round(histogram, 2)

    def find_support_resistance(self, period=20):
        """Find key support and resistance levels"""
        close_prices = self.data['Close'].tolist()
        recent_prices = close_prices[-period:]
        support = round(min(recent_prices), 0)
        resistance = round(max(recent_prices), 0)
        return support, resistance

    def generate_signal(self):
        """Generate buy/sell signal based on technical analysis"""
        rsi = self.calculate_rsi()
        macd_line, macd_signal, macd_histogram = self.calculate_macd()
        support, resistance = self.find_support_resistance()
        sma_20 = self.calculate_sma(20)
        sma_50 = self.calculate_sma(50)

        signals = []
        signal_strength = 0

        # RSI Analysis
        if rsi is not None:
            if rsi < 30:
                signals.append(f"✅ RSI Oversold ({rsi}) - Bullish")
                signal_strength += 2
            elif rsi > 70:
                signals.append(f"❌ RSI Overbought ({rsi}) - Bearish")
                signal_strength -= 2
            elif 30 <= rsi <= 50:
                signals.append(f"⚠️ RSI Neutral ({rsi}) - Bullish potential")
                signal_strength += 1
            else:
                signals.append(f"⚠️ RSI Neutral ({rsi}) - Bearish potential")
                signal_strength -= 1

        # MACD Analysis
        if macd_histogram is not None:
            if macd_histogram > 0:
                signals.append(f"📈 MACD Bullish ({macd_histogram})")
                signal_strength += 1
            else:
                signals.append(f"📉 MACD Bearish ({macd_histogram})")
                signal_strength -= 1

        # SMA Trend Analysis
        if sma_20 and sma_50:
            if self.current_price > sma_20 and sma_20 > sma_50:
                signals.append(f"📈 Price > SMA20 > SMA50 - Strong Uptrend")
                signal_strength += 2
            elif self.current_price < sma_20 and sma_20 < sma_50:
                signals.append(f"📉 Price < SMA20 < SMA50 - Strong Downtrend")
                signal_strength -= 2
            else:
                signals.append(f"⚠️ Mixed SMA signals - Sideways")

        # Support/Resistance Analysis
        if self.current_price < support * 1.02:
            signals.append(f"🟢 Near Support at Rp {support:,.0f}")
            signal_strength += 2
        elif self.current_price > resistance * 0.98:
            signals.append(f"🔴 Near Resistance at Rp {resistance:,.0f}")
            signal_strength -= 2

        # Final Signal
        if signal_strength >= 4:
            final_signal = "🚀 STRONG BUY"
            action = f"BUY at Rp {self.current_price:,.0f}"
        elif signal_strength >= 2:
            final_signal = "✅ BUY"
            action = f"BUY at Rp {self.current_price:,.0f}"
        elif signal_strength <= -4:
            final_signal = "🔥 STRONG SELL"
            action = f"SELL at Rp {self.current_price:,.0f}"
        elif signal_strength <= -2:
            final_signal = "❌ SELL"
            action = f"SELL at Rp {self.current_price:,.0f}"
        else:
            final_signal = "😎 HOLD"
            action = f"Wait for better entry at support: Rp {support:,.0f}"

        return {
            'signal': final_signal,
            'action': action,
            'strength': signal_strength,
            'indicators': signals,
            'rsi': rsi,
            'macd_histogram': macd_histogram,
            'support': support,
            'resistance': resistance,
            'sma_20': sma_20,
            'sma_50': sma_50
        }

    def get_trading_levels(self):
        """Calculate trading levels for the stock"""
        support, resistance = self.find_support_resistance()

        return {
            'stop_loss': round(support * 0.98, 0),
            'target_1': round(resistance, 0),
            'target_2': round(resistance * 1.05, 0),
            'target_3': round(resistance * 1.10, 0),
            'current': round(self.current_price, 0)
        }

    def analyze(self):
        """Perform complete analysis"""
        success, message = self.fetch_data()
        if not success:
            return False, message

        analysis = self.generate_signal()
        levels = self.get_trading_levels()

        volume = self.data['Volume'].iloc[-1] if not self.data.empty else 0

        return True, {
            'symbol': self.symbol,
            'price': round(self.current_price, 0),
            'change': round(self.weekly_change, 2),
            'volume': volume,
            'analysis': analysis,
            'levels': levels
        }

def display_analysis(result):
    """Display analysis results in formatted way"""
    if not result[0]:
        print(f"❌ Error: {result[1]}")
        return

    data = result[1]
    a = data['analysis']
    l = data['levels']

    print(f"\n{'='*70}")
    print(f"📊 {data['symbol']} - WEEKLY CHART ANALYSIS")
    print(f"{'='*70}")
    print(f"\n💰 Current Price: Rp {data['price']:,.0f}")
    print(f"📈 Weekly Change: {data['change']:+.2f}%")
    print(f"📊 Volume: {data['volume']:,.0f}")

    print(f"\n📍 Support Level: Rp {a['support']:,.0f}")
    print(f"📍 Resistance Level: Rp {a['resistance']:,.0f}")

    print(f"\n📈 SMA 20: Rp {a['sma_20'] if a['sma_20'] else 'N/A'}")
    print(f"📈 SMA 50: Rp {a['sma_50'] if a['sma_50'] else 'N/A'}")
    print(f"📉 RSI (14): {a['rsi'] if a['rsi'] else 'N/A'}")
    print(f"📉 MACD Histogram: {a['macd_histogram'] if a['macd_histogram'] else 'N/A'}")

    print(f"\n{'='*70}")
    print(f"🎯 FINAL SIGNAL: {a['signal']}")
    print(f"🎯 ACTION: {a['action']}")
    print(f"{'='*70}")

    print(f"\n📋 Technical Analysis:")
    for indicator in a['indicators']:
        print(f"   {indicator}")

    print(f"\n💰 Trading Levels:")
    print(f"   Current Price: Rp {l['current']:,.0f}")
    print(f"   Stop Loss: Rp {l['stop_loss']:,.0f}")
    print(f"   Target 1: Rp {l['target_1']:,.0f}")
    print(f"   Target 2: Rp {l['target_2']:,.0f}")
    print(f"   Target 3: Rp {l['target_3']:,.0f}")

    print(f"\n⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

def main():
    """Analyze all 4 stocks"""
    stocks = ["BMRI.JK", "BBCA.JK", "BBRI.JK", "UNTR.JK"]

    print("🔍 COMPREHENSIVE STOCK ANALYSIS - WEEKLY CHART")
    print("="*70)
    print("Analyzing: BMRI, BBCA, BBRI, UNTR")
    print("="*70)

    results = {}

    for stock in stocks:
        print(f"\n⏳ Analyzing {stock}...")
        analyzer = StockAnalyzer(stock)

        # Retry logic for API calls
        max_retries = 3
        for attempt in range(max_retries):
            result = analyzer.analyze()
            if result[0]:
                break
            else:
                print(f"   ⚠️ Attempt {attempt + 1}/{max_retries}: {result[1]}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry

        results[stock] = result
        display_analysis(result)

    # Summary
    print(f"\n{'='*70}")
    print("📋 SUMMARY - ALL STOCKS")
    print(f"{'='*70}")

    for stock, result in results.items():
        if result[0]:
            data = result[1]
            print(f"\n{stock}:")
            print(f"   Price: Rp {data['price']:,.0f} ({data['change']:+.2f}%)")
            print(f"   Signal: {data['analysis']['signal']}")
            print(f"   Action: {data['analysis']['action']}")
        else:
            print(f"\n{stock}: ❌ Analysis failed - {result[1]}")

    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    main()
