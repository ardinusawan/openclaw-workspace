#!/usr/bin/env python3
"""
Technical Stock Screener - Momentum Based Swing Trading
Screens Indonesian stocks (IDX) for technical swing trading criteria

Scoring Criteria:
1. Momentum Strength (RSI, MACD, Volume) - 40%
2. Volatility Characteristics (ATR, Bollinger) - 25%
3. Volume Profile (High, Increasing, Spike) - 20%
4. Price Action (Support/Resistance, Trend) - 15%

Total Score: 100%
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TechnicalScreener:
    """Technical stock screener for momentum-based swing trading"""

    def __init__(self):
        self.stocks_data = {}

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = 100 - (100 / (1 + gain / loss))

        return rs

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow

        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - macd_signal

        return macd, macd_signal, histogram

    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range (Volatility)"""
        high_low = high - low
        true_range = high_low.rolling(window=period).mean()

        return true_range

    def calculate_bollinger(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        middle_band = sma

        # Bandwidth: (upper - lower) / middle
        bandwidth = (upper_band - lower_band) / middle_band

        return upper_band, middle_band, lower_band, bandwidth

    def calculate_volume_ma(self, volume, period=20):
        """Calculate 20-day volume moving average"""
        return volume.rolling(window=period).mean()

    def calculate_momentum_score(self, stock_data):
        """Calculate momentum strength score (40 points)"""
        score = 0

        # RSI Momentum (15 points)
        rsi = stock_data['RSI'].iloc[-1]

        # RSI between 30-70 is neutral
        if 30 < rsi < 70:
            score += 5  # Neutral momentum
        elif rsi > 70:
            score += 10  # Bullish momentum (strong)
        elif rsi < 30:
            score += 0  # Bearish momentum (not good for swing)

        # RSI Trend (rising/falling) (10 points)
        rsi_prev = stock_data['RSI'].iloc[-2] if len(stock_data['RSI']) >= 2 else stock_data['RSI'].iloc[-1]

        if rsi > rsi_prev:
            score += 10  # Rising RSI (bullish)
        elif rsi < rsi_prev:
            score -= 5  # Falling RSI (bearish)

        # MACD Momentum (15 points)
        macd_hist = stock_data['MACD_Hist'].iloc[-1]

        if macd_hist > 0:
            score += 15  # Bullish histogram
        elif macd_hist < 0:
            score += 0  # Bearish histogram

        # MACD Crossover (additional 5 points)
        if len(stock_data['MACD']) >= 2:
            macd_prev = stock_data['MACD'].iloc[-2]
            if macd_prev < 0 and stock_data['MACD'].iloc[-1] > 0:
                score += 5  # Bullish crossover

        return score

    def calculate_volatility_score(self, stock_data):
        """Calculate volatility score (25 points)"""
        score = 0

        # ATR-based volatility (10 points)
        atr = stock_data['ATR'].iloc[-1]
        avg_price = stock_data['Close'].iloc[-20:].mean()

        if atr:
            atr_pct = (atr / avg_price) * 100

            if atr_pct > 2.0:
                score += 10  # High volatility (good for swing)
            elif atr_pct > 1.0:
                score += 7  # Moderate volatility
            elif atr_pct > 0.5:
                score += 4  # Low volatility
            else:
                score += 0  # Very low volatility

        # Bollinger Band Squeeze (15 points)
        bandwidth = stock_data['Bandwidth'].iloc[-1]

        if bandwidth < 0.05:  # Very tight bands (squeeze)
            score += 15
        elif bandwidth < 0.10:
            score += 10  # Moderately tight bands
        elif bandwidth < 0.20:
            score += 5  # Normal bands
        else:
            score += 0  # Wide bands

        return score

    def calculate_volume_score(self, stock_data):
        """Calculate volume profile score (20 points)"""
        score = 0

        # High volume (10 points)
        current_volume = stock_data['Volume'].iloc[-1]
        volume_ma = stock_data['Volume_MA'].iloc[-1]

        if current_volume > volume_ma * 1.5:
            score += 10  # High volume
        elif current_volume > volume_ma * 1.2:
            score += 7  # Above average volume
        elif current_volume > volume_ma * 1.0:
            score += 5  # Normal volume
        else:
            score += 0  # Low volume

        # Volume spike (5 points)
        prev_volume = stock_data['Volume'].iloc[-2] if len(stock_data['Volume']) >= 2 else stock_data['Volume'].iloc[-1]

        if current_volume > prev_volume * 2.0:
            score += 5  # Volume spike (institutional interest)

        # Volume trend (increasing) (5 points)
        if len(stock_data['Volume']) >= 3:
            vol_trend = stock_data['Volume'].iloc[-3:]  # Last 3 days
            if vol_trend.is_monotonic_increasing():
                score += 5  # Increasing volume

        return score

    def calculate_price_action_score(self, stock_data):
        """Calculate price action score (15 points)"""
        score = 0

        close = stock_data['Close'].iloc[-1]
        upper_band = stock_data['BB_Upper'].iloc[-1]
        lower_band = stock_data['BB_Lower'].iloc[-1]
        middle_band = stock_data['BB_Mid'].iloc[-1]

        # Price near upper band (breakout potential) - 5 points
        if close > middle_band * 0.98:
            score += 5

        # Price near lower band (support) - 3 points
        if close < middle_band * 1.02:
            score += 3

        # Price action: Higher highs, higher lows (trend) - 5 points
        if len(stock_data['Close']) >= 5:
            highs = stock_data['High'].iloc[-5:].max()
            if stock_data['High'].iloc[-1] == highs:
                score += 5  # Making higher highs

        # Price action: Consolidation near middle band - 2 points
        if 0.98 < (close / middle_band) < 1.02:
            score += 2

        return score

    def screen_stocks(self, tickers, start_date="2025-08-01", end_date="2026-02-12"):
        """Screen stocks based on technical criteria"""
        print(f"\n🔍 Screening {len(tickers)} stocks for swing trading...")
        print(f"   Time range: {start_date} to {end_date}")

        results = {}

        for i, ticker in enumerate(tickers, 1):
            print(f"\n[{i}/{len(tickers)}] {ticker}")

            try:
                # Download data
                stock = yf.Ticker(ticker)
                hist = stock.history(start=start_date, end=end_date)

                if hist.empty or len(hist) < 30:
                    print(f"   ❌ Insufficient data (less than 30 days)")
                    continue

                # Reset index
                hist.index = hist.index.tz_localize(None).tz_localize('Asia/Jakarta')

                # Ensure required columns
                if 'Volume' not in hist.columns:
                    print(f"   ⚠️  No volume data")
                    continue

                # Calculate indicators
                hist['RSI'] = self.calculate_rsi(hist['Close'], period=14)
                hist['MACD'], hist['MACD_Signal'], hist['MACD_Hist'] = self.calculate_macd(hist['Close'])
                hist['ATR'] = self.calculate_atr(hist['High'], hist['Low'], hist['Close'])
                hist['BB_Upper'], hist['BB_Mid'], hist['BB_Lower'], hist['Bandwidth'] = self.calculate_bollinger(hist['Close'])
                hist['Volume_MA'] = self.calculate_volume_ma(hist['Volume'])

                # Calculate scores
                momentum_score = self.calculate_momentum_score(hist)
                volatility_score = self.calculate_volatility_score(hist)
                volume_score = self.calculate_volume_score(hist)
                price_action_score = self.calculate_price_action_score(hist)

                # Total score (100 points max)
                total_score = momentum_score + volatility_score + volume_score + price_action_score

                # Get latest data
                latest = hist.iloc[-1]

                results[ticker] = {
                    'ticker': ticker,
                    'total_score': total_score,
                    'momentum_score': momentum_score,
                    'volatility_score': volatility_score,
                    'volume_score': volume_score,
                    'price_action_score': price_action_score,
                    'rsi': latest['RSI'],
                    'macd_hist': latest['MACD_Hist'],
                    'atr': latest['ATR'],
                    'bandwidth': latest['Bandwidth'],
                    'price': latest['Close'],
                    'volume': latest['Volume'],
                    'volume_ma': latest['Volume_MA'],
                    'date': latest.name
                }

                print(f"   📊 Score: {total_score:.0f}/100")
                print(f"      Momentum: {momentum_score:.0f}")
                print(f"      Volatility: {volatility_score:.0f}")
                print(f"      Volume: {volume_score:.0f}")
                print(f"      Price Action: {price_action_score:.0f}")
                print(f"      RSI: {latest['RSI']:.2f}")
                print(f"      Price: Rp {latest['Close']:,.0f}")

            except Exception as e:
                print(f"   ❌ Error processing {ticker}: {str(e)}")
                continue

        # Sort by total score
        sorted_results = sorted(results.items(), key=lambda x: x[1]['total_score'], reverse=True)

        # Display top stocks
        print(f"\n📈 TOP 10 STOCKS FOR SWING TRADING:")
        print("=" * 60)

        for i, (ticker, data) in enumerate(sorted_results[:10], 1):
            print(f"\n{i}. {ticker}")
            print(f"   Score: {data['total_score']:.0f}/100")
            print(f"   Price: Rp {data['price']:,.0f}")
            print(f"   Volume: {data['volume']:,.0f}")
            print(f"   RSI: {data['rsi']:.2f}")
            print(f"   MACD Hist: {data['macd_hist']:.4f}")
            print(f"   ATR: {data['atr']:,.0f}")
            print(f"   Bandwidth: {data['bandwidth']:.4f}")

        print("\n" + "=" * 60)

        return sorted_results

    def display_analysis(self, sorted_results):
        """Display detailed analysis of top stocks"""
        print("\n📊 DETAILED ANALYSIS OF TOP STOCKS")

        for i, (ticker, data) in enumerate(sorted_results[:5], 1):
            print(f"\n{i}. {ticker} - SCORE: {data['total_score']:.0f}/100")

            # Momentum Analysis
            print(f"   📈 Momentum Score: {data['momentum_score']:.0f}/40")
            if data['rsi'] > 70:
                print(f"      RSI: {data['rsi']:.2f} (OVERBOUGHT - Bullish)")
            elif data['rsi'] < 30:
                print(f"      RSI: {data['rsi']:.2f} (OVERSOLD - Bearish)")
            else:
                print(f"      RSI: {data['rsi']:.2f} (NEUTRAL)")

            print(f"      MACD Histogram: {data['macd_hist']:.4f}")

            if data['macd_hist'] > 0:
                print(f"      Status: BULLISH MOMENTUM")
            elif data['macd_hist'] < 0:
                print(f"      Status: BEARISH MOMENTUM")

            # Volatility Analysis
            print(f"   📉 Volatility Score: {data['volatility_score']:.0f}/25")

            if data['bandwidth'] < 0.05:
                print(f"      Bollinger: TIGHT SQUEE (Breakout potential)")
            elif data['bandwidth'] < 0.10:
                print(f"      Bollinger: MODERATE SQUEZE")
            else:
                print(f"      Bollinger: WIDE BANDS (Range)")

            print(f"      ATR (Volatility): {data['atr']:,.0f}")

            # Volume Analysis
            print(f"   📊 Volume Score: {data['volume_score']:.0f}/20")

            if data['volume'] > data['volume_ma'] * 1.5:
                print(f"      Volume: HIGH ({data['volume']:,.0f} vs MA {data['volume_ma']:,.0f})")
            elif data['volume'] > data['volume_ma'] * 1.2:
                print(f"      Volume: ABOVE AVERAGE ({data['volume']:,.0f} vs MA {data['volume_ma']:,.0f})")
            else:
                print(f"      Volume: NORMAL ({data['volume']:,.0f} vs MA {data['volume_ma']:,.0f})")

            # Price Action Analysis
            print(f"   💰 Price Action Score: {data['price_action_score']:.0f}/15")

            bb_upper = data['price'] * (1 + data['bandwidth'] / 2)
            bb_lower = data['price'] * (1 - data['bandwidth'] / 2)

            print(f"      Bollinger Upper: Rp {bb_upper:,.0f}")
            print(f"      Bollinger Lower: Rp {bb_lower:,.0f}")

            if data['price'] > bb_upper * 0.98:
                print(f"      Status: NEAR UPPER BAND (Breakout potential)")
            elif data['price'] < bb_lower * 1.02:
                print(f"      Status: NEAR LOWER BAND (Support level)")
            else:
                print(f"      Status: MIDDLE RANGE (Consolidation)")

        print("\n" + "=" * 60)

def main():
    """Main function"""
    print("=" * 60)
    print("🔍 TECHNICAL STOCK SCREENER - MOMENTUM SWING TRADING")
    print("=" * 60)

    # Indonesian stocks to screen (mix of banking, mining, consumer, telecom, etc.)
    idx_stocks = [
        # Banking
        'BMRI.JK', 'BBRI.JK', 'BBCA.JK', 'BNI.JK', 'BTPN.JK', 'BBTN.JK', 'BRII.JK',

        # Mining & Energy
        'ADHI.JK', 'ANTM.JK', 'TPIA.JK', 'ELSA.JK', 'TINS.JK', 'CPIN.JK',

        # Consumer Goods
        'ICBP.JK', 'UNVR.JK', 'GGRM.JK', 'MYOR.JK',

        # Telecommunications
        'TLKM.JK', 'EXCL.JK', 'ISAT.JK',

        # Infrastructure
        'WIKA.JK', 'ADHI.JK', 'PWON.JK', 'ADRO.JK',

        # Automotive
        'ASII.JK', 'AUTO.JK',

        # Property
        'PWON.JK',

        # Others (Growth stocks)
        'GOTO.JK', 'UNTR.JK'
    ]

    # Screen stocks
    screener = TechnicalScreener()
    sorted_results = screener.screen_stocks(idx_stocks)

    # Save results to CSV
    import csv

    with open('/tmp/top_swing_stocks.csv', 'w', newline='') as csvfile:
        fieldnames = ['rank', 'ticker', 'total_score', 'momentum_score', 'volatility_score', 'volume_score', 'price_action_score', 'rsi', 'macd_hist', 'atr', 'bandwidth', 'price', 'volume', 'date']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, (ticker, data) in enumerate(sorted_results, 1):
            writer.writerow({
                'rank': i,
                'ticker': ticker,
                'total_score': data['total_score'],
                'momentum_score': data['momentum_score'],
                'volatility_score': data['volatility_score'],
                'volume_score': data['volume_score'],
                'price_action_score': data['price_action_score'],
                'rsi': data['rsi'],
                'macd_hist': data['macd_hist'],
                'atr': data['atr'],
                'bandwidth': data['bandwidth'],
                'price': data['price'],
                'volume': data['volume'],
                'date': data['date']
            })

    print(f"\n📊 Results saved to: /tmp/top_swing_stocks.csv")
    print(f"   Total stocks screened: {len(sorted_results)}")

    print("\n" + "=" * 60)
    print("✅ SCREENING COMPLETE!")
    print("=" * 60)
    print("\n💡 Recommendation: Run this screener weekly to find new momentum plays")
    print("💡 Best for: Swing trading (3-10 days), Market timing entries")
    print("💡 Focus on: Stocks with score > 60/100 and positive momentum")

if __name__ == "__main__":
    main()
