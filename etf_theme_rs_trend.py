import datetime as dt
from typing import Dict, Optional
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from pykrx import stock


# ==========================
# 1) 테마별 대표 ETF 정의 (JSON 로드)
# ==========================


def load_theme_etfs() -> Dict[str, Dict[str, Optional[str]]]:
    """theme_etf_data.json 파일에서 테마 정의를 읽어옵니다."""
    current_dir = Path(__file__).parent
    json_path = current_dir / "theme_etf_data.json"

    if not json_path.exists():
        st.error(f"설정 파일({json_path.name})을 찾을 수 없습니다.")
        return {}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"설정 파일 로딩 중 오류 발생: {e}")
        return {}


THEME_ETFS = load_theme_etfs()

# 벤치마크 (KOSPI / KOSDAQ 등) - pykrx 기준 인덱스 코드
# KOSPI: 1001, KOSDAQ: 2001
BENCHMARKS = {
    "KOSPI (KS11)": "1001",
    "KOSDAQ (KQ11)": "2001",
}


# ==========================
# 2) 데이터 로더
# ==========================


@st.cache_data(show_spinner=False)
def load_price(code: str, start: dt.date, end: dt.date) -> pd.DataFrame:
    """
    pykrx로 가격 데이터 로드.
    반환: DateIndex, ['Close', 'Open', 'High', 'Low', 'Volume'] 등.
    컬럼명을 영문으로 변경하여 기존 로직과 호환성 유지.
    """
    start_str = start.strftime("%Y%m%d")
    end_str = end.strftime("%Y%m%d")

    # 1) ETF 시도
    # pykrx의 get_etf_ohlcv_by_date는 ETF가 아니면 빈 DataFrame을 반환하거나 에러가 날 수 있음.
    # 하지만 0098F0 같은 ETF 코드는 여기서 잡혀야 함.
    try:
        df = stock.get_etf_ohlcv_by_date(start_str, end_str, code)
    except Exception:
        df = pd.DataFrame()

    # 2) 데이터가 비었으면 일반 종목(Market) 시도
    # (ETF여도 get_market_ohlcv로 조회 가능한 경우도 있음, 혹은 일반 주식일 수도 있음)
    if df.empty:
        try:
            df = stock.get_market_ohlcv(start_str, end_str, code)
        except Exception:
            pass

    # 3) 그래도 비었으면 지수(Index) 시도 (벤치마크용)
    if df.empty:
        try:
            df = stock.get_index_ohlcv_by_date(start_str, end_str, code)
        except Exception:
            pass

    if df.empty:
        return pd.DataFrame()

    # 컬럼 이름 변경 (한글 -> 영문)
    # pykrx 반환 칼럼: ['시가', '고가', '저가', '종가', '거래량', ...] (지수는 거래대금/상장시가총액 등 다름)
    # 필요한 건 'Close'(종가)가 핵심.
    # 주식/ETF: 시가, 고가, 저가, 종가, 거래량, 거래대금, 등락률
    # 지수: 시가, 고가, 저가, 종가, 거래량, 거래대금, 상장시가총액

    rename_map = {
        "시가": "Open",
        "고가": "High",
        "저가": "Low",
        "종가": "Close",
        "거래량": "Volume",
    }
    df = df.rename(columns=rename_map)

    # 인덱스를 Date로 보장 (pykrx는 이미 DatetimeIndex)
    df = df.sort_index()
    return df


def normalize_price(df: pd.DataFrame, col: str = "Close") -> pd.Series:
    """첫 날을 100으로 기준화한 지수화 시계열."""
    if df.empty:
        return pd.Series(dtype="float64")
    base = df[col].iloc[0]
    return df[col] / base * 100


def compute_return(df: pd.DataFrame, col: str = "Close") -> float:
    """기간 수익률 (단순 %)"""
    if len(df) < 2:
        return float("nan")
    return (df[col].iloc[-1] / df[col].iloc[0] - 1.0) * 100.0


def compute_volatility(df: pd.DataFrame, col: str = "Close") -> float:
    """일간 수익률 기준 연율화 변동성(단순 근사)."""
    if len(df) < 2:
        return float("nan")
    daily_ret = df[col].pct_change().dropna()
    if daily_ret.empty:
        return float("nan")
    return daily_ret.std() * (252**0.5) * 100.0


def compute_relative_strength(
    asset: pd.DataFrame,
    bench: pd.DataFrame,
    col: str = "Close",
) -> float:
    """
    단순 RS: 기간 수익률(자산) - 기간 수익률(벤치마크).
    (더 elaborate하게 price ratio의 기울기 등으로 바꿀 수도 있음.)
    """
    r_asset = compute_return(asset, col)
    r_bench = compute_return(bench, col)
    if pd.isna(r_asset) or pd.isna(r_bench):
        return float("nan")
    return r_asset - r_bench


# ==========================
# 3) Streamlit UI
# ==========================


def main():
    st.set_page_config(
        page_title="산업/테마 ETF 동향 대시보드",
        layout="wide",
    )

    st.title("📊 산업/테마 ETF 동향 대시보드")
    st.caption(
        "대표 테마 ETF들을 이용해 섹터/산업 트렌드를 비교합니다. (레버리지/인버스 제외)"
    )

    # -------- Sidebar: 설정 --------
    st.sidebar.header("⚙️ 설정")

    # 기간 선택
    today = dt.date.today()
    default_start = today - dt.timedelta(days=365 * 3)  # 기본 3년

    period_option = st.sidebar.selectbox(
        "기간 선택",
        ["3년", "5년", "1년", "YTD", "직접 선택"],
        index=0,
    )

    if period_option == "3년":
        start_date = today - dt.timedelta(days=365 * 3)
    elif period_option == "5년":
        start_date = today - dt.timedelta(days=365 * 5)
    elif period_option == "1년":
        start_date = today - dt.timedelta(days=365)
    elif period_option == "YTD":
        start_date = dt.date(today.year, 1, 1)
    else:
        start_date = st.sidebar.date_input("시작일", value=default_start)
    end_date = st.sidebar.date_input("종료일", value=today)

    # 벤치마크 선택
    bench_name = st.sidebar.selectbox(
        "벤치마크 (RS 계산용)",
        list(BENCHMARKS.keys()),
        index=0,
    )
    bench_code = BENCHMARKS[bench_name]

    # 테마 선택
    theme_names = list(THEME_ETFS.keys())
    default_selection = [
        "2차전지",
        "원자력 SMR",
        "방산",
        "조선",
        "금융 - 은행/지주",
    ]
    default_selection = [t for t in default_selection if t in theme_names]

    # 세션 상태 초기화
    if "selected_themes" not in st.session_state:
        st.session_state["selected_themes"] = default_selection

    # 콜백 함수 정의
    def select_all():
        st.session_state["selected_themes"] = theme_names

    def deselect_all():
        st.session_state["selected_themes"] = []

    # 버튼 배치
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.button("✅ 전체 선택", on_click=select_all, use_container_width=True)
    with col2:
        st.button("❌ 선택 해제", on_click=deselect_all, use_container_width=True)

    selected_themes = st.sidebar.multiselect(
        "비교할 테마 선택",
        theme_names,
        key="selected_themes",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**⚠️ 코드가 비어 있는 ETF**는 자동으로 제외됩니다. theme_etf_data.json에 코드를 추가하면 됩니다.(종목 추가도 가능)"
    )
    no_code = [k for k, v in THEME_ETFS.items() if not v["code"]]
    if no_code:
        st.sidebar.write(
            "TODO: 아래 ETF의 6자리 KRX 코드를 채워 넣으면 대시보드에 포함됩니다:"
        )
        for t in no_code:
            st.sidebar.caption(f"- {t} : {THEME_ETFS[t]['name']}")

    # -------- 데이터 로딩: 벤치마크 --------
    st.subheader("1. 벤치마크 & 테마 가격 추이 (100 기준화)")

    try:
        bench_df = load_price(bench_code, start_date, end_date)
    except Exception as e:
        st.error(f"벤치마크({bench_name}) 데이터 로딩 실패: {e}")
        bench_df = pd.DataFrame()

    # -------- 메인 차트용 데이터 준비 --------
    norm_df = pd.DataFrame()

    if not bench_df.empty:
        norm_df[f"{bench_name} (벤치마크)"] = normalize_price(bench_df)

    theme_price_dfs = {}

    for theme in selected_themes:
        info = THEME_ETFS[theme]
        code = info["code"]
        if not code:
            continue  # 코드가 없으면 스킵

        try:
            df = load_price(code, start_date, end_date)
            if df.empty:
                continue
            theme_price_dfs[theme] = df
            norm_df[info["name"]] = normalize_price(df)
        except Exception as e:
            st.warning(f"{theme} ({info['name']}) 데이터 로딩 실패: {e}")

    if norm_df.empty:
        st.warning("표시할 데이터가 없습니다. (ETF 코드 또는 기간 설정을 확인하세요.)")
        return

    # -------- 라인 차트 --------
    st.line_chart(norm_df)

    st.caption(
        "※ 모든 시계열을 시작일 기준 100으로 기준화해서, "
        "기간 동안 어느 테마가 상대적으로 강했는지 시각적으로 비교합니다."
    )

    # ==========================
    # 4) 성과 / 변동성 / RS 테이블
    # ==========================

    st.subheader("2. 기간 성과 요약 (수익률 · 변동성 · RS)")

    rows = []

    # 벤치마크 지표
    if not bench_df.empty:
        bench_ret = compute_return(bench_df)
        bench_vol = compute_volatility(bench_df)
        rows.append(
            {
                "테마": f"{bench_name} (벤치마크)",
                "ETF명": bench_name,
                "기간 수익률(%)": round(bench_ret, 2),
                "연율화 변동성(%)": round(bench_vol, 2),
                "벤치마크 대비 RS(%)": 0.0,  # 자기 자신 기준 0
            }
        )

    for theme, df in theme_price_dfs.items():
        info = THEME_ETFS[theme]
        ret = compute_return(df)
        vol = compute_volatility(df)
        rs = (
            compute_relative_strength(df, bench_df)
            if not bench_df.empty
            else float("nan")
        )

        rows.append(
            {
                "테마": theme,
                "ETF명": info["name"],
                "기간 수익률(%)": round(ret, 2) if pd.notna(ret) else None,
                "연율화 변동성(%)": round(vol, 2) if pd.notna(vol) else None,
                "벤치마크 대비 RS(%)": round(rs, 2) if pd.notna(rs) else None,
            }
        )

    result_df = pd.DataFrame(rows)
    # 벤치마크 제외 RS 기준 정렬
    result_df_sorted = result_df.sort_values(
        by="벤치마크 대비 RS(%)",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    st.dataframe(result_df_sorted, use_container_width=True)

    st.caption(
        "- **기간 수익률**: 시작일~종료일까지의 단순 수익률\n"
        "- **연율화 변동성**: 일간 수익률의 표준편차 × √252\n"
        "- **RS(%)**: (테마 기간 수익률 − 벤치마크 기간 수익률). 0보다 크면 벤치마크보다 강함."
    )

    # ==========================
    # 5) 상관관계 매트릭스 (선택)
    # ==========================

    st.subheader("3. 테마 간 상관관계 (일간 수익률 기준)")

    # 모든 시계열을 하나로 합치고 일간 수익률 계산
    price_for_corr = pd.DataFrame()

    if not bench_df.empty:
        price_for_corr[f"{bench_name} (벤치)"] = bench_df["Close"]

    for theme, df in theme_price_dfs.items():
        info = THEME_ETFS[theme]
        price_for_corr[info["name"]] = df["Close"]

    if price_for_corr.shape[1] >= 2:
        daily_ret = price_for_corr.pct_change().dropna()
        corr = daily_ret.corr()
        st.dataframe(corr.style.format("{:.2f}"), use_container_width=True)
        st.caption(
            "※ 일간 수익률 기준 상관계수(피어슨). 1에 가까울수록 동행, 0에 가까울수록 독립적 움직임."
        )
    else:
        st.info("상관관계를 계산할 만한 ETF 수가 충분하지 않습니다.")


if __name__ == "__main__":
    main()
