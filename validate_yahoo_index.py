import FinanceDataReader as fdr


def test_yahoo_index():
    print("Testing Yahoo Finance symbols...")
    # Yahoo Finance ticker for KOSPI: ^KS11, KOSDAQ: ^KQ11
    symbols = ["^KS11", "^KQ11"]

    for sym in symbols:
        try:
            print(f"Trying {sym}...")
            # fdr.DataReader에서 날짜 포맷 주의
            df = fdr.DataReader(sym, "2024-01-01")
            print(f"Success {sym}:")
            print(df.tail(2))
        except Exception as e:
            print(f"Failed {sym}: {e}")


if __name__ == "__main__":
    test_yahoo_index()
