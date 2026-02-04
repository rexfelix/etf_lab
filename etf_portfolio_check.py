from pykrx import stock


def check_etf_pdf_history():
    # 2024년 1월 2일 (과거)
    target_date = "20240102"
    ticker = "069500"  # KODEX 200

    print(f"Checking ETF PDF for {ticker} on {target_date}...")
    try:
        pdf = stock.get_etf_portfolio_deposit_file(ticker, target_date)
        print("PDF fetch result:")
        print(pdf.head(10))
        print(f"Total Components: {len(pdf)}")
    except Exception as e:
        print(f"PDF fetch failed: {e}")


if __name__ == "__main__":
    check_etf_pdf_history()
