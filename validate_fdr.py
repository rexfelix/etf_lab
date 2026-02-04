import FinanceDataReader as fdr
import pandas as pd
import datetime


def test_fdr():
    try:
        print(f"FinanceDataReader version: {fdr.__version__}")
    except NameError:
        print("FinanceDataReader not verified (version check failed)")

    today = datetime.date.today().strftime("%Y-%m-%d")
    start_date = "2024-01-01"

    print("-" * 30)
    print("1. ETF Price Test (KODEX 2차전지산업: 305720)")
    try:
        df = fdr.DataReader("305720", start_date)
        print(df.tail())
    except Exception as e:
        print(f"Failed: {e}")

    print("-" * 30)
    print("2. Stock Price Test (Samsung Elec: 005930)")
    try:
        df = fdr.DataReader("005930", start_date)
        print(df.tail())
    except Exception as e:
        print(f"Failed: {e}")

    print("-" * 30)
    print("3. Index Price Test (KOSPI: KS11)")
    try:
        df = fdr.DataReader("KS11", start_date)
        print(df.tail())
    except Exception as e:
        print(f"Failed: {e}")

    print("-" * 30)
    print("4. Listing Test (KRX ETF)")
    try:
        df_krx = fdr.StockListing("KRX")  # KRX 전체
        etf = df_krx[df_krx["Code"] == "305720"]
        print(etf)
    except Exception as e:
        print(f"Failed: {e}")


if __name__ == "__main__":
    test_fdr()
