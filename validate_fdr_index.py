import FinanceDataReader as fdr


def test_index():
    print("Testing KOSPI symbols...")
    symbols = ["KS11", "KOSPI"]
    for sym in symbols:
        try:
            print(f"Trying {sym}...")
            df = fdr.DataReader(sym, "2024-01-01")
            print(f"Success {sym}:")
            print(df.tail(2))
        except Exception as e:
            print(f"Failed {sym}: {e}")

    print("-" * 30)
    print("Testing KOSDAQ symbols...")
    symbols = ["KQ11", "KOSDAQ"]
    for sym in symbols:
        try:
            print(f"Trying {sym}...")
            df = fdr.DataReader(sym, "2024-01-01")
            print(f"Success {sym}:")
            print(df.tail(2))
        except Exception as e:
            print(f"Failed {sym}: {e}")


if __name__ == "__main__":
    test_index()
