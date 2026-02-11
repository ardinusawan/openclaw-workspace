#!/usr/bin/env python3
"""
Comprehensive Stock Analysis with Fundamental Data
Includes technical, fundamental, and valuation metrics
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
        self.data = None
        self.info = None
        self.financials = None

    def fetch_all_data(self):
        """Fetch all available data from Yahoo Finance"""
        try:
            # Price data
            self.data = self.ticker.history(period="2y", interval="1wk", timeout=30)

            # Fundamental data
            self.info = self.ticker.info

            # Financial statements
            self.financials = self.ticker.financials
            self.balance_sheet = self.ticker.balance_sheet
            self.cashflow = self.ticker.cashflow

            if self.data.empty:
                return False, "No price data available"

            return True, "Success"

        except Exception as e:
            return False, str(e)

    def get_fundamental_data(self):
        """Extract fundamental metrics from ticker info"""
        if not self.info:
            return None

        fundamentals = {
            'company_name': self.info.get('longName', self.symbol),
            'sector': self.info.get('sector', 'N/A'),
            'industry': self.info.get('industry', 'N/A'),
            'market_cap': self.info.get('marketCap', 0),
            'current_price': self.info.get('currentPrice', self.info.get('regularMarketPrice', 0)),
            'pe_ratio': self.info.get('trailingPE', 0),
            'pb_ratio': self.info.get('priceToBook', 0),
            'ps_ratio': self.info.get('priceToSalesTrailing12Months', 0),
            'dividend_yield': self.info.get('dividendYield', 0) * 100 if self.info.get('dividendYield') else 0,
            'payout_ratio': self.info.get('payoutRatio', 0) * 100 if self.info.get('payoutRatio') else 0,
            'roe': self.info.get('returnOnEquity', 0) * 100 if self.info.get('returnOnEquity') else 0,
            'roa': self.info.get('returnOnAssets', 0) * 100 if self.info.get('returnOnAssets') else 0,
            'profit_margin': self.info.get('profitMargins', 0) * 100 if self.info.get('profitMargins') else 0,
            'operating_margin': self.info.get('operatingMargins', 0) * 100 if self.info.get('operatingMargins') else 0,
            'debt_to_equity': self.info.get('debtToEquity', 0),
            'current_ratio': self.info.get('currentRatio', 0),
            'quick_ratio': self.info.get('quickRatio', 0),
            'revenue_growth': self.info.get('revenueGrowth', 0) * 100 if self.info.get('revenueGrowth') else 0,
            'earnings_growth': self.info.get('earningsQuarterlyGrowth', 0) * 100 if self.info.get('earningsQuarterlyGrowth') else 0,
            'book_value': self.info.get('bookValue', 0),
            'total_debt': self.info.get('totalDebt', 0),
            'total_cash': self.info.get('totalCash', 0),
            'free_cashflow': self.info.get('freeCashflow', 0),
            'beta': self.info.get('beta', 0),
            '52_week_high': self.info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': self.info.get('fiftyTwoWeekLow', 0),
            'analyst_rating': self.info.get('recommendationKey', 'N/A'),
            'target_price': self.info.get('targetMeanPrice', 0),
            'number_of_analysts': self.info.get('numberOfAnalystOpinions', 0)
        }

        return fundamentals

    def calculate_technical_indicators(self):
        """Calculate technical indicators"""
        if self.data.empty:
            return None

        close_prices = self.data['Close'].tolist()

        # RSI
        def calculate_rsi(prices, period=14):
            if len(prices) < period + 1:
                return None
            gains = []
            losses = []
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                gains.append(max(change, 0))
                losses.append(abs(min(change, 0)))
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            if avg_loss == 0:
                return 100
            rs = avg_gain / avg_loss
            return round(100 - (100 / (1 + rs)), 2)

        # SMA
        def calculate_sma(prices, period):
            if len(prices) < period:
                return None
            return round(sum(prices[-period:]) / period, 2)

        # EMA
        def calculate_ema(period):
            if len(close_prices) < period:
                return None
            multiplier = 2 / (period + 1)
            ema = [close_prices[0]]
            for price in close_prices[1:]:
                ema.append((price * multiplier) + (ema[-1] * (1 - multiplier)))
            return round(ema[-1], 2)

        # MACD
        def calculate_macd():
            ema_12 = calculate_ema(12)
            ema_26 = calculate_ema(26)
            if ema_12 is None or ema_26 is None:
                return None, None, None
            macd_line = ema_12 - ema_26

            # Simple histogram
            recent_changes = [close_prices[i] - close_prices[i-1] for i in range(-9, 0)]
            signal_line = sum(recent_changes) / len(recent_changes) if recent_changes else 0
            histogram = macd_line - signal_line

            return round(macd_line, 2), round(signal_line, 2), round(histogram, 2)

        # Support/Resistance
        def find_support_resistance(period=20):
            recent_prices = close_prices[-period:]
            return round(min(recent_prices), 0), round(max(recent_prices), 0)

        return {
            'rsi': calculate_rsi(close_prices),
            'sma_20': calculate_sma(close_prices, 20),
            'sma_50': calculate_sma(close_prices, 50),
            'sma_200': calculate_sma(close_prices, 200),
            'ema_12': calculate_ema(12),
            'ema_26': calculate_ema(26),
            'macd_line': calculate_macd()[0],
            'macd_signal': calculate_macd()[1],
            'macd_histogram': calculate_macd()[2],
            'support': find_support_resistance()[0],
            'resistance': find_support_resistance()[1],
            'current_price': round(close_prices[-1], 0),
            'prev_price': round(close_prices[-2], 0),
            'price_change': round(((close_prices[-1] - close_prices[-2]) / close_prices[-2]) * 100, 2)
        }

    def generate_fundamental_score(self):
        """Generate fundamental quality score (0-100)"""
        if not self.info:
            return 0, "No data"

        score = 0
        max_score = 100
        feedback = []

        # Profitability (30 points)
        roe = self.info.get('returnOnEquity', 0)
        if roe:
            if roe > 0.15:  # 15% ROE is excellent
                score += 25
                feedback.append(f"✅ ROE Excellent: {roe*100:.1f}%")
            elif roe > 0.10:
                score += 20
                feedback.append(f"✅ ROE Good: {roe*100:.1f}%")
            elif roe > 0.05:
                score += 15
                feedback.append(f"⚠️ ROE Fair: {roe*100:.1f}%")
            else:
                feedback.append(f"❌ ROE Poor: {roe*100:.1f}%")

        # Profit Margin (15 points)
        profit_margin = self.info.get('profitMargins', 0)
        if profit_margin:
            if profit_margin > 0.20:
                score += 15
                feedback.append(f"✅ Profit Margin Excellent: {profit_margin*100:.1f}%")
            elif profit_margin > 0.10:
                score += 10
                feedback.append(f"✅ Profit Margin Good: {profit_margin*100:.1f}%")
            elif profit_margin > 0.05:
                score += 5
                feedback.append(f"⚠️ Profit Margin Fair: {profit_margin*100:.1f}%")
            else:
                feedback.append(f"❌ Profit Margin Poor: {profit_margin*100:.1f}%")

        # Growth (20 points)
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth:
            if revenue_growth > 0.15:
                score += 20
                feedback.append(f"✅ Revenue Growth Excellent: {revenue_growth*100:.1f}%")
            elif revenue_growth > 0.10:
                score += 15
                feedback.append(f"✅ Revenue Growth Good: {revenue_growth*100:.1f}%")
            elif revenue_growth > 0.05:
                score += 10
                feedback.append(f"⚠️ Revenue Growth Moderate: {revenue_growth*100:.1f}%")
            elif revenue_growth > 0:
                score += 5
                feedback.append(f"⚠️ Revenue Growth Low: {revenue_growth*100:.1f}%")
            else:
                feedback.append(f"❌ Revenue Growth Negative: {revenue_growth*100:.1f}%")

        # Valuation (15 points)
        pe_ratio = self.info.get('trailingPE', 0)
        if pe_ratio:
            if pe_ratio < 15:
                score += 15
                feedback.append(f"✅ P/E Attractive: {pe_ratio:.1f}")
            elif pe_ratio < 25:
                score += 10
                feedback.append(f"⚠️ P/E Fair: {pe_ratio:.1f}")
            elif pe_ratio < 40:
                score += 5
                feedback.append(f"⚠️ P/E High: {pe_ratio:.1f}")
            else:
                feedback.append(f"❌ P/E Very High: {pe_ratio:.1f}")

        # Financial Health (20 points)
        debt_to_equity = self.info.get('debtToEquity', 0)
        if debt_to_equity:
            if debt_to_equity < 0.5:
                score += 20
                feedback.append(f"✅ Debt Ratio Excellent: {debt_to_equity:.2f}")
            elif debt_to_equity < 1.0:
                score += 15
                feedback.append(f"✅ Debt Ratio Good: {debt_to_equity:.2f}")
            elif debt_to_equity < 2.0:
                score += 10
                feedback.append(f"⚠️ Debt Ratio Moderate: {debt_to_equity:.2f}")
            else:
                feedback.append(f"❌ Debt Ratio High: {debt_to_equity:.2f}")

        # Dividend (optional bonus)
        dividend_yield = self.info.get('dividendYield', 0)
        if dividend_yield and dividend_yield > 0.03:  # >3%
            feedback.append(f"✅ Dividend Yield Good: {dividend_yield*100:.1f}%")

        return score, feedback

    def generate_investment_recommendation(self, fundamental_score, technical_score):
        """Generate overall investment recommendation"""
        combined_score = (fundamental_score * 0.6) + (technical_score * 0.4)

        if combined_score >= 75:
            return "🚀 STRONG BUY", "Excellent fundamentals + technicals"
        elif combined_score >= 60:
            return "✅ BUY", "Good fundamentals + technicals"
        elif combined_score >= 45:
            return "😎 HOLD", "Average fundamentals + technicals"
        elif combined_score >= 30:
            return "❌ SELL", "Poor fundamentals + technicals"
        else:
            return "🔥 STRONG SELL", "Very poor fundamentals + technicals"

    def analyze(self):
        """Perform comprehensive analysis"""
        success, message = self.fetch_all_data()
        if not success:
            return False, message

        fundamentals = self.get_fundamental_data()
        technicals = self.calculate_technical_indicators()
        fundamental_score, fundamental_feedback = self.generate_fundamental_score()

        # Calculate technical score
        technical_score = 50  # Base score
        if technicals:
            if technicals['rsi'] and technicals['rsi'] < 30:
                technical_score += 20  # Oversold
            elif technicals['rsi'] and technicals['rsi'] > 70:
                technical_score -= 20  # Overbought

            if technicals['macd_histogram'] and technicals['macd_histogram'] > 0:
                technical_score += 15  # Bullish
            elif technicals['macd_histogram'] and technicals['macd_histogram'] < 0:
                technical_score -= 15  # Bearish

            if technicals['current_price'] and technicals['support']:
                if technicals['current_price'] < technicals['support'] * 1.02:
                    technical_score += 15  # Near support

        recommendation, reason = self.generate_investment_recommendation(fundamental_score, technical_score)

        return True, {
            'symbol': self.symbol,
            'fundamentals': fundamentals,
            'technicals': technicals,
            'fundamental_score': fundamental_score,
            'technical_score': technical_score,
            'fundamental_feedback': fundamental_feedback,
            'recommendation': recommendation,
            'reason': reason
        }

def display_comprehensive_report(result):
    """Display comprehensive analysis report"""
    if not result[0]:
        print(f"❌ Error: {result[1]}")
        return

    data = result[1]
    f = data['fundamentals']
    t = data['technicals']

    print(f"\n{'='*80}")
    print(f"📊 COMPREHENSIVE STOCK ANALYSIS - {data['symbol']}")
    print(f"{'='*80}")

    # Company Info
    print(f"\n🏢 Company Information:")
    print(f"   Name: {f['company_name']}")
    print(f"   Sector: {f['sector']}")
    print(f"   Industry: {f['industry']}")
    print(f"   Market Cap: Rp {f['market_cap']:,.0f}" if f['market_cap'] else "   Market Cap: N/A")

    # Price & Performance
    print(f"\n💰 Price & Performance:")
    print(f"   Current Price: Rp {t['current_price']:,.0f}")
    print(f"   Weekly Change: {t['price_change']:+.2f}%")
    print(f"   52-Week Range: Rp {f['52_week_low']:,.0f} - Rp {f['52_week_high']:,.0f}")
    if f['target_price']:
        print(f"   Analyst Target: Rp {f['target_price']:,.0f}")

    # Valuation Metrics
    print(f"\n📈 Valuation Metrics:")
    print(f"   P/E Ratio: {f['pe_ratio']:.2f}" if f['pe_ratio'] else "   P/E Ratio: N/A")
    print(f"   P/B Ratio: {f['pb_ratio']:.2f}" if f['pb_ratio'] else "   P/B Ratio: N/A")
    print(f"   P/S Ratio: {f['ps_ratio']:.2f}" if f['ps_ratio'] else "   P/S Ratio: N/A")

    # Profitability
    print(f"\n💡 Profitability:")
    print(f"   ROE: {f['roe']:.2f}%" if f['roe'] else "   ROE: N/A")
    print(f"   ROA: {f['roa']:.2f}%" if f['roa'] else "   ROA: N/A")
    print(f"   Profit Margin: {f['profit_margin']:.2f}%" if f['profit_margin'] else "   Profit Margin: N/A")
    print(f"   Operating Margin: {f['operating_margin']:.2f}%" if f['operating_margin'] else "   Operating Margin: N/A")

    # Growth
    print(f"\n📊 Growth Metrics:")
    print(f"   Revenue Growth: {f['revenue_growth']:.2f}%" if f['revenue_growth'] else "   Revenue Growth: N/A")
    print(f"   Earnings Growth: {f['earnings_growth']:.2f}%" if f['earnings_growth'] else "   Earnings Growth: N/A")

    # Financial Health
    print(f"\n💪 Financial Health:")
    print(f"   Debt/Equity: {f['debt_to_equity']:.2f}" if f['debt_to_equity'] else "   Debt/Equity: N/A")
    print(f"   Current Ratio: {f['current_ratio']:.2f}" if f['current_ratio'] else "   Current Ratio: N/A")
    print(f"   Total Debt: Rp {f['total_debt']:,.0f}" if f['total_debt'] else "   Total Debt: N/A")
    print(f"   Total Cash: Rp {f['total_cash']:,.0f}" if f['total_cash'] else "   Total Cash: N/A")

    # Dividend
    if f['dividend_yield']:
        print(f"\n💰 Dividend:")
        print(f"   Dividend Yield: {f['dividend_yield']:.2f}%")
        print(f"   Payout Ratio: {f['payout_ratio']:.2f}%" if f['payout_ratio'] else "   Payout Ratio: N/A")

    # Technical Indicators
    print(f"\n📉 Technical Indicators:")
    print(f"   RSI (14): {t['rsi']}" if t['rsi'] else "   RSI (14): N/A")
    print(f"   SMA 20: Rp {t['sma_20']:,.0f}" if t['sma_20'] else "   SMA 20: N/A")
    print(f"   SMA 50: Rp {t['sma_50']:,.0f}" if t['sma_50'] else "   SMA 50: N/A")
    print(f"   SMA 200: Rp {t['sma_200']:,.0f}" if t['sma_200'] else "   SMA 200: N/A")
    print(f"   MACD Histogram: {t['macd_histogram']}" if t['macd_histogram'] else "   MACD Histogram: N/A")
    print(f"   Support: Rp {t['support']:,.0f}" if t['support'] else "   Support: N/A")
    print(f"   Resistance: Rp {t['resistance']:,.0f}" if t['resistance'] else "   Resistance: N/A")

    # Fundamental Score
    print(f"\n⭐ Fundamental Score: {data['fundamental_score']}/100")
    for feedback in data['fundamental_feedback']:
        print(f"   {feedback}")

    # Technical Score
    print(f"\n⭐ Technical Score: {data['technical_score']}/100")

    # Final Recommendation
    print(f"\n{'='*80}")
    print(f"🎯 FINAL RECOMMENDATION: {data['recommendation']}")
    print(f"🎯 Reason: {data['reason']}")
    print(f"{'='*80}")

    # Trading Levels
    print(f"\n💰 Trading Levels:")
    print(f"   Current Price: Rp {t['current_price']:,.0f}")
    print(f"   Stop Loss: Rp {t['support'] * 0.98:,.0f}" if t['support'] else "   Stop Loss: N/A")
    print(f"   Target 1: Rp {t['resistance']:,.0f}" if t['resistance'] else "   Target 1: N/A")
    print(f"   Target 2: Rp {t['resistance'] * 1.05:,.0f}" if t['resistance'] else "   Target 2: N/A")

    # Analyst Opinion
    if f['analyst_rating']:
        print(f"\n📊 Analyst Opinion:")
        print(f"   Rating: {f['analyst_rating']}")
        if f['number_of_analysts']:
            print(f"   Based on {f['number_of_analysts']} analysts")

    print(f"\n⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

def main():
    """Run comprehensive analysis on all 4 stocks"""
    stocks = ["BMRI.JK", "BBCA.JK", "BBRI.JK", "UNTR.JK"]

    print("🔍 COMPREHENSIVE STOCK ANALYSIS")
    print("Including: Technical, Fundamental, Valuation, & Growth Metrics")
    print("="*80)

    results = {}

    for stock in stocks:
        print(f"\n⏳ Analyzing {stock}...")
        analyzer = StockAnalyzer(stock)
        result = analyzer.analyze()
        results[stock] = result
        display_comprehensive_report(result)

    # Comparison Summary
    print(f"\n{'='*80}")
    print(f"📋 COMPARISON SUMMARY - ALL STOCKS")
    print(f"{'='*80}")

    print(f"\n{'Stock':<12} {'Price':<12} {'Funda Score':<12} {'Tech Score':<12} {'Recommendation':<20}")
    print("-" * 80)

    for stock, result in results.items():
        if result[0]:
            d = result[1]
            price = f"Rp {d['fundamentals']['current_price']:,.0f}" if d['fundamentals']['current_price'] else "N/A"
            f_score = f"{d['fundamental_score']}/100"
            t_score = f"{d['technical_score']}/100"
            rec = d['recommendation']
            print(f"{stock:<12} {price:<12} {f_score:<12} {t_score:<12} {rec:<20}")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
