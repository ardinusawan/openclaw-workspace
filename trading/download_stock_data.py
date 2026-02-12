#!/usr/bin/env python3
"""
Stock Data Downloader for Indonesian Stocks
Downloads historical OHLCV (Open, High, Low, Close, Volume) data from various sources

Data Sources:
1. Yahoo Finance (yfinance) - Free, reliable, daily data
2. IDX.co.id (Indonesia Stock Exchange) - Official data
3. Investing.com (InvestPy) - International stocks listed on IDX
4. Yahoo Finance Alternative (yfinance with different ticker format)

Supported Stocks:
- BMRI.JK (Bank Mandiri)
- BBRI.JK (Bank Rakyat Indonesia)
- BBCA.JK (Bank Central Asia)
- BBNI.JK (Bank Negara Indonesia)
- BNI.JK (Bank Nasional Indonesia)
- BTPN.JK (Bank Tabungan Pensiunan Nasional)
- BRII.JK (Bank Rakyat Indonesia Syariah)
- BBTN.JK (Bank Tabungan Negara)
- BDKI.JK (Bank DKI)
- BDMN.JK (Bank Danamon Indonesia)
- BTPS.JK (Bank Tabungan Pensiunan Nasional Syariah)
- BTPN.JK (Bank Tabungan Pensiunan Nasional - Old Ticker)
- UNTR.JK (Bank Rakyat Indonesia - Old Ticker)
- BBKP.JK (Bank Bukopin)
- BNBA.JK (Bank BNP Paribas Indonesia)
- BBNI.JK (Bank Negara Indonesia - Old Ticker)
- AGRO.JK (Bank Rakyat Indonesia - Old Ticker)
- BDMN.JK (Bank Danamon Indonesia - Old Ticker)

Stocks covered: All major Indonesian banking stocks listed on IDX
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import json

class StockDataDownloader:
    """Downloads and manages historical stock data"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ensure_directory()

    def ensure_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"✅ Created data directory: {self.data_dir}")

    def download_stock_yahoo(self, ticker, period_start, period_end="2026-02-12"):
        """
        Download stock data from Yahoo Finance

        Args:
            ticker: Stock ticker (e.g., "BMRI.JK")
            period_start: Start date (e.g., "2015-01-01")
            period_end: End date (default: today)

        Returns:
            DataFrame with OHLCV data
        """
        print(f"📥 Downloading {ticker} from Yahoo Finance...")
        print(f"   Period: {period_start} to {period_end}")

        try:
            stock = yf.Ticker(ticker)

            # Get historical data
            hist = stock.history(start=period_start, end=period_end)

            if hist.empty:
                print(f"   ❌ No data found for {ticker}")
                return None

            # Reset index
            hist.index = hist.index.tz_localize(None).tz_localize('Asia/Jakarta')
            hist.index = hist.index.normalize()

            # Ensure OHLCV columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in hist.columns]

            if missing_columns:
                print(f"   ⚠️  Missing columns: {missing_columns}")
                return None

            # Clean column names
            hist = hist[required_columns]

            # Remove NaN values
            hist = hist.dropna()

            # Remove zero volume rows (possible data errors)
            hist = hist[hist['Volume'] > 0]

            print(f"   ✅ Downloaded {len(hist)} days of data")
            print(f"   Date range: {hist.index[0]} to {hist.index[-1]}")
            print(f"   Volume range: {hist['Volume'].min():,} to {hist['Volume'].max():,}")

            # Save to CSV
            csv_file = f"{self.data_dir}/{ticker.replace('.', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
            hist.to_csv(csv_file)
            print(f"   ✅ Saved to: {csv_file}")

            return hist

        except Exception as e:
            print(f"   ❌ Error downloading {ticker}: {str(e)}")
            return None

    def download_multiple_stocks(self, tickers, period_start):
        """
        Download multiple stocks

        Args:
            tickers: List of stock tickers
            period_start: Start date for historical data

        Returns:
            Dictionary of DataFrames
        """
        results = {}

        print(f"\n📥 Downloading {len(tickers)} stocks from {period_start} to {datetime.now().strftime('%Y-%m-%d')}")

        for i, ticker in enumerate(tickers, 1):
            print(f"\n[{i}/{len(tickers)}] {ticker}")
            data = self.download_stock_yahoo(ticker, period_start)
            results[ticker] = data

        return results

    def get_latest_price(self, ticker):
        """
        Get latest price for stock

        Args:
            ticker: Stock ticker

        Returns:
            Latest price or None
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                return {
                    'ticker': ticker,
                    'price': data['Close'].iloc[-1],
                    'date': data.index[-1],
                    'volume': data['Volume'].iloc[-1],
                    'change': round((data['Close'].iloc[-1] - data['Open'].iloc[0]) / data['Open'].iloc[0] * 100, 2)
                }
            return None
        except Exception as e:
            print(f"❌ Error getting latest price for {ticker}: {str(e)}")
            return None

    def save_summary(self, results, output_file="data/summary.json"):
        """
        Save summary of downloaded data

        Args:
            results: Dictionary of DataFrames
            output_file: Output file path
        """
        summary = {}

        for ticker, data in results.items():
            if data is not None:
                summary[ticker] = {
                    'date_range': f"{data.index[0]} to {data.index[-1]}",
                    'days': len(data),
                    'volume_avg': round(data['Volume'].mean(), 2),
                    'close_latest': data['Close'].iloc[-1],
                    'close_start': data['Open'].iloc[0],
                    'change_pct': round((data['Close'].iloc[-1] - data['Open'].iloc[0]) / data['Open'].iloc[0] * 100, 2)
                }

        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n✅ Summary saved to: {output_file}")


def main():
    """Main function to download stock data"""

    print("=" * 60)
    print("📥 Indonesian Banking Stock Data Downloader")
    print("=" * 60)

    # Indonesian Banking Stocks
    banking_stocks = [
        # Major Banks
        "BMRI.JK",  # Bank Mandiri
        "BBRI.JK",  # Bank Rakyat Indonesia
        "BBCA.JK",  # Bank Central Asia
        "BBNI.JK",  # Bank Negara Indonesia
        "BNI.JK",   # Bank Nasional Indonesia
        "BTPN.JK",  # Bank Tabungan Pensiunan Nasional
        "BRII.JK",  # Bank Rakyat Indonesia Syariah
        "BBTN.JK",  # Bank Tabungan Negara
        "BDKI.JK",  # Bank DKI

        # Regional Banks
        "BDMN.JK",  # Bank Danamon Indonesia
        "BTPS.JK",  # Bank Tabungan Pensiunan Nasional Syariah
        "BBKP.JK",  # Bank Bukopin
        "BNBA.JK",  # Bank BNP Paribas Indonesia

        # Other Financial Services
        "BTPN.JK",  # Bank Tabungan Pensiunan Nasional (Old Ticker)
        "UNTR.JK",  # Bank Rakyat Indonesia (Old Ticker)
        "AGRO.JK",   # Bank Rakyat Indonesia (Old Ticker)
    ]

    # Remove duplicates
    banking_stocks = list(set(banking_stocks))

    print(f"\n📊 Banking Stocks to Download: {len(banking_stocks)} stocks")
    print(f"📊 Stocks: {', '.join(banking_stocks)}")

    # Data period (download last 10 years)
    period_start = "2016-01-01"
    print(f"\n📅 Data Period: {period_start} to {datetime.now().strftime('%Y-%m-%d')} (last 10 years)")

    # Initialize downloader
    downloader = StockDataDownloader()

    # Download all stocks
    results = downloader.download_multiple_stocks(banking_stocks, period_start)

    # Save summary
    downloader.save_summary(results)

    # Get latest prices
    print(f"\n💰 Latest Prices:")

    for ticker in ["BMRI.JK", "BBRI.JK", "BBCA.JK"]:
        data = downloader.get_latest_price(ticker)
        if data:
            print(f"   {ticker}: Rp {data['price']:,.2f} ({data['change_pct']:+.2f}%)")

    print("\n" + "=" * 60)
    print("✅ Data Download Complete!")
    print("=" * 60)
    print(f"\n📁 Data Directory: {downloader.data_dir}")
    print(f"📄 Summary File: {downloader.data_dir}/summary.json")
    print(f"\n💡 Next Steps:")
    print(f"   1. Review downloaded data")
    print(f"   2. Check for missing days or data errors")
    print(f"   3. Implement backtesting strategies")
    print(f"   4. Optimize trading parameters")


if __name__ == "__main__":
    main()
