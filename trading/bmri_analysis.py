#!/usr/bin/env python3
"""
BMRI Stock Technical Analysis - Weekly Chart
Provides buy/sell signals based on technical indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
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

def calculate_sma(prices, period):
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return None
    return round(sum(prices[-period:]) / period, 2)

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    multiplier = 2 / (period + 1)
    ema = [prices[0]]
    for price in prices[1:]:
        ema.append(round((price * multiplier) + (ema[-1] * (1 - multiplier)), 2))
    return ema[-1]

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    if len(prices) < slow:
        return None, None, None

    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)

    if ema_fast is None or ema_slow is None:
        return None, None, None

    macd_line = ema_fast - ema_slow
    macd_values = [price - (ema_slow + (i * 0.01)) for i, price in enumerate(prices[-fast:])]

    # Signal line (9-period EMA of MACD)
    if len(macd_values) < signal:
        return macd_line, None, None

    signal_line = calculate_ema(macd_values[-signal:], signal)
    histogram = macd_line - signal_line if signal_line else 0

    return round(macd_line, 2), round(signal_line if signal_line else 0, 2), round(histogram, 2)

def find_support_resistance(prices, period=20):
    """Find key support and resistance levels"""
    recent_prices = prices[-period:]
    support = round(min(recent_prices), 0)
    resistance = round(max(recent_prices), 0)
    return support, resistance

def generate_signal(current_price, rsi, macd_histogram, support, resistance):
    """Generate buy/sell signal based on multiple indicators"""
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

    # Support/Resistance Analysis
    if current_price < support * 1.02:
        signals.append(f"🟢 Near Support at {support}")
        signal_strength += 2
    elif current_price > resistance * 0.98:
        signals.append(f"🔴 Near Resistance at {resistance}")
        signal_strength -= 2

    # Final Signal
    if signal_strength >= 3:
        final_signal = "🚀 STRONG BUY"
        buy_zone = f"Buy Zone: {support:.0f} - {current_price:.0f}"
    elif signal_strength >= 1:
        final_signal = "✅ BUY"
        buy_zone = f"Buy Zone: {current_price:.0f} - {support:.0f}"
    elif signal_strength <= -3:
        final_signal = "🔥 STRONG SELL"
        buy_zone = f"Take Profit: {resistance:.0f}"
    elif signal_strength <= -1:
        final_signal = "❌ SELL"
        buy_zone = f"Take Profit: {current_price:.0f} - {resistance:.0f}"
    else:
        final_signal = "😎 HOLD"
        buy_zone = f"Wait for better entry at support: {support:.0f}"

    return final_signal, signals, buy_zone

def analyze_bmri():
    """Analyze BMRI stock with weekly data"""
    print("🔍 Analyzing BMRI Stock (Bank Mandiri) - Weekly Chart")
    print("=" * 60)

    try:
        # Get BMRI data (weekly, last 2 years)
        ticker = yf.Ticker("BMRI.JK")
        data = ticker.history(period="2y", interval="1wk")

        if data.empty:
            print("❌ Error: No data available for BMRI")
            return

        close_prices = data['Close'].tolist()
        high_prices = data['High'].tolist()
        low_prices = data['Low'].tolist()
        volumes = data['Volume'].tolist()

        current_price = close_prices[-1]
        prev_price = close_prices[-2]
        weekly_change = ((current_price - prev_price) / prev_price) * 100

        # Calculate indicators
        rsi = calculate_rsi(close_prices)
        sma_20 = calculate_sma(close_prices, 20)
        sma_50 = calculate_sma(close_prices, 50)
        ema_12 = calculate_ema(close_prices, 12)
        ema_26 = calculate_ema(close_prices, 26)

        macd_line, macd_signal, macd_histogram = calculate_macd(close_prices)
        support, resistance = find_support_resistance(close_prices)

        # Generate signals
        signal, indicator_signals, zone = generate_signal(current_price, rsi, macd_histogram, support, resistance)

        # Display Results
        print(f"\n📊 BMRI Current Price: Rp {current_price:,.0f}")
        print(f"📈 Weekly Change: {weekly_change:+.2f}%")
        print(f"📊 Volume: {volumes[-1]:,.0f}")
        print(f"\n📍 Support Level: Rp {support:,.0f}")
        print(f"📍 Resistance Level: Rp {resistance:,.0f}")
        print(f"\n📈 SMA 20: Rp {sma_20 if sma_20 else 'N/A'}")
        print(f"📈 SMA 50: Rp {sma_50 if sma_50 else 'N/A'}")
        print(f"📈 EMA 12: Rp {ema_12 if ema_12 else 'N/A'}")
        print(f"📈 EMA 26: Rp {ema_26 if ema_26 else 'N/A'}")
        print(f"\n📉 RSI (14): {rsi if rsi else 'N/A'}")
        print(f"📉 MACD: {macd_line if macd_line else 'N/A'}")
        print(f"📉 MACD Signal: {macd_signal if macd_signal else 'N/A'}")
        print(f"📉 MACD Histogram: {macd_histogram if macd_histogram else 'N/A'}")

        print(f"\n{'='*60}")
        print(f"🎯 FINAL SIGNAL: {signal}")
        print(f"{'='*60}")
        print(f"\n📍 {zone}")
        print(f"\n📋 Indicator Analysis:")
        for s in indicator_signals:
            print(f"   {s}")

        # Trading Levels
        print(f"\n💰 Trading Levels:")
        print(f"   Stop Loss: Rp {support * 0.98:,.0f}")
        print(f"   Target 1: Rp {resistance:,.0f}")
        print(f"   Target 2: Rp {resistance * 1.05:,.0f}")
        print(f"   Target 3: Rp {resistance * 1.10:,.0f}")

        print(f"\n⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")

if __name__ == "__main__":
    analyze_bmri()
