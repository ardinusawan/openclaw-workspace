#!/usr/bin/env python3
"""
Technical Stock Screener - Momentum Based Swing Trading (FIXED)
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
import csv

class TechnicalScreener:
    """Technical stock screener for momentum-based swing trading (FIXED VERSION)"""

    def __init__(self):
        self.stocks_data = {}

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0).rolling(window=period).mean())
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
        """Calculate Bollinger Bands (Volatility)"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        middle_band = sma

        return upper_band, middle_band, lower_band

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
            score += 0  # Falling RSI (bearish)

        # MACD Momentum (15 points)
        macd_hist = stock_data['MACD_Hist'].iloc[-1]

        if macd_hist > 0:
            score += 15  # Bullish histogram
        elif macd_hist < 0:
            score += 0  # Bearish histogram

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
        elif bandwidth < 0.10:  # Moderately tight bands
            score += 10
        elif bandwidth < 0.20:  # Normal bands
            score += 5
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
        elif current_volume > volume_ma:
            score += 5  # Normal volume
        else:
            score += 0  # Low volume

        # Volume spike (5 points)
        prev_volume = stock_data['Volume'].iloc[-2] if len(stock_data['Volume']) >= 2 else current_volume

        if current_volume > prev_volume * 2.0:
            score += 5  # Volume spike (institutional interest)

        # Volume trend (increasing) (5 points)
        if len(stock_data['Volume']) >= 3:
            vol_trend = stock_data['Volume'].iloc[-3:]
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

        # Price near upper band (breakout potential) (5 points)
        if close > middle_band * 0.98:
            score += 5

        # Price near lower band (support) (3 points)
        if close < middle_band * 1.02:
            score += 3

        # Price action: Higher highs, higher lows (5 points)
        if len(stock_data['Close']) >= 5:
            highs = stock_data['High'].iloc[-5:]
            if stock_data['High'].iloc[-1] == highs.max():
                score += 5

        # Price action: Consolidation near middle band (2 points)
        if 0.98 < (close / middle_band) < 1.02:
            score += 2

        return score

    def screen_stocks(self, tickers, start_date="2025-08-01", end_date=datetime.now()):
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
                    print(f"   ❌ Insufficient data (< 30 days)")
                    continue

                # Reset index
                hist.index = hist.index.tz_localize(None).tz_localize('Asia/Jakarta')

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
                print(f"      Price: Rp {latest['Close']:,.0f}")

            except Exception as e:
                print(f"   ❌ Error processing {ticker}: {str(e)}")

        return results

    def display_analysis(self, sorted_results):
        """Display detailed analysis of top stocks"""
        print("\n📊 DETAILED ANALYSIS OF TOP 10 STOCKS")

        for i, (ticker, data) in enumerate(sorted_results[:10], 1):
            print(f"\n{i}. {ticker} - SCORE: {data['total_score']:.0f}/100")

            # Momentum Analysis
            print(f"   📈 Momentum: {data['momentum_score']:.0f}/40")

            rsi = data['rsi']

            if rsi > 70:
                print(f"      RSI: {rsi:.2f} (OVERBOUGHT - Bullish)")
            elif rsi < 30:
                print(f"      RSI: {rsi:.2f} (OVERSOLD - Bearish)")
            elif 30 < rsi < 50:
                print(f"      RSI: {rsi:.2f} (WEAK - Slightly Bearish)")
            elif 50 < rsi < 70:
                print(f"      RSI: {rsi:.2f} (STRONG - Slightly Bullish)")

            macd_hist = data['macd_hist']
            print(f"      MACD: {macd_hist:.4f}")

            if macd_hist > 0:
                print(f"      Status: BULLISH HISTOGRAM")
            elif macd_hist < 0:
                print(f"      Status: BEARISH HISTOGRAM")

            # Volatility Analysis
            print(f"   📉 Volatility: {data['volatility_score']:.0f}/25")

            atr = data['atr']
            price = data['price']
            atr_pct = (atr / price * 100)

            print(f"      ATR: {atr:,.2f}")
            print(f"      ATR%: {atr_pct:.2f}%")

            bandwidth = data['bandwidth']

            if bandwidth < 0.05:
                print(f"      Bollinger: TIGHT SQUEEZE (Breakout Potential)")
            elif bandwidth < 0.10:
                print(f"      Bollinger: MODERATE SQUEEZE")
            elif bandwidth < 0.20:
                print(f"      Bollinger: NORMAL BANDS")
            else:
                print(f"      Bollinger: WIDE BANDS")

            # Volume Analysis
            print(f"   📊 Volume Profile: {data['volume_score']:.0f}/20")

            current_volume = data['volume']
            volume_ma = data['volume_ma']

            if current_volume > volume_ma * 1.5:
                print(f"      Volume: HIGH ({current_volume:,.0f} vs MA {volume_ma:,.0f})")
            elif current_volume > volume_ma * 1.2:
                print(f"      Volume: ABOVE AVERAGE ({current_volume:,.0f} vs MA {volume_ma:,.0f})")
            elif current_volume > volume_ma:
                print(f"      Volume: NORMAL ({current_volume:,.0f} vs MA {volume_ma:,.0f})")
            else:
                print(f"      Volume: LOW ({current_volume:,.0f} vs MA {volume_ma:,.0f})")

            # Price Action
            print(f"   💰 Price Action: {data['price_action_score']:.0f}/15")

            bb_upper = data['price'] * (1 + data['bandwidth'] / 2)
            bb_lower = data['price'] * (1 - data['bandwidth'] / 2)

            print(f"      Bollinger Upper: Rp {bb_upper:,.0f}")
            print(f"      Bollinger Lower: Rp {bb_lower:,.0f}")

            if data['price'] > bb_upper * 0.98:
                print(f"      Status: NEAR UPPER BAND (Breakout Potential)")
            elif data['price'] < bb_lower * 1.02:
                print(f"      Status: NEAR LOWER BAND (Support Level)")
            else:
                print(f"      Status: MIDDLE RANGE (Consolidation)")

        print("\n" + "=" * 60)

def main():
    """Main function to run screener"""

    print("=" * 60)
    print("🔍 TECHNICAL STOCK SCREENER - MOMENTUM SWING TRADING (FIXED)")
    print("=" * 60)

    # Indonesian stocks to screen (mix of sectors)
    idx_stocks = [
        # Banking
        'BMRI.JK', 'BBRI.JK', 'BBCA.JK', 'BNI.JK', 'BTPN.JK', 'BRII.JK',

        # Mining & Energy
        'ADHI.JK', 'ANTM.JK', 'TPIA.JK', 'ELSA.JK',

        # Consumer Goods
        'ICBP.JK', 'UNVR.JK', 'GGRM.JK', 'MYOR.JK',

        # Telecommunications
        'TLKM.JK', 'EXCL.JK', 'ISAT.JK',

        # Infrastructure
        'WIKA.JK', 'ADHI.JK', 'PWON.JK',

        # Automotive
        'ASII.JK', 'AUTO.JK'
    ]

    # Start date (6 months of data)
    start_date = "2025-08-01"

    # Initialize screener
    screener = TechnicalScreener()

    # Run screening
    results = screener.screen_stocks(idx_stocks, start_date=start_date)

    # Sort by total score
    sorted_results = sorted(results.items(), key=lambda x: x[1]['total_score'], reverse=True)

    # Display analysis
    screener.display_analysis(sorted_results)

    # Save to CSV
    import csv

    with open('/tmp/top_swing_stocks.csv', 'w', newline='') as csvfile:
        fieldnames = ['rank', 'ticker', 'total_score', 'momentum_score', 'volatility_score', 'volume_score', 'price_action_score', 'rsi', 'macd_hist', 'atr', 'bandwidth', 'price', 'volume', 'volume_ma', 'date']

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
                'volume_ma': data['volume_ma'],
                'date': data['date']
            })

    print(f"\n📊 Results saved to: /tmp/top_swing_stocks.csv")
    print(f"   Total stocks screened: {len(sorted_results)}")
    print(f"   Top stocks for swing trading: {sorted_results[:5]}")

    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION FOR SWING TRADING")
    print("=" * 60)
    print("\n📊 Stock Scoring Breakdown:")
    print("   - Momentum Strength (RSI, MACD, Volume): 40 points")
    print("   - Volatility Characteristics (ATR, Bollinger): 25 points")
    print("   - Volume Profile (High, Spike, Trend): 20 points")
    print("   - Price Action (Support/Resistance, Trend): 15 points")
    print("   - TOTAL: 100 points max")

    print("\n🎯 Top 5 Stocks for Swing Trading:")
    for i, (ticker, data) in enumerate(sorted_results[:5], 1):
        print(f"   {i}. {ticker} (Score: {data['total_score']:.0f}/100)")

    print("\n" + "=" * 60)
    print("✅ SCREENING COMPLETE!")
    print("=" * 60)
    print(f"\n💡 Next Steps:")
    print(f"   1. Review top stocks for swing trading")
    print(f"   2. Check volume and liquidity")
    print(f"   3. Confirm momentum and volatility")
    print(f"   4. Run backtest on selected stocks")
    print(f"   5. Optimize entry/exit parameters")


if __name__ == "__main__":
    main()
