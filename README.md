# 산업/테마 ETF 동향 대시보드 (ETF Theme RS Trend)

국내 상장된 주요 테마별 대표 ETF의 가격 추이와 상대 강도(RS, Relative Strength)를 분석하고, 벤치마크(KOSPI/KOSDAQ) 대비 성과를 비교하는 Streamlit 대시보드입니다.

## 주요 기능

*   **테마별 ETF 가격 비교**: KODEX, TIGER, SOL 등 주요 운용사의 대표 테마 ETF들의 가격 추이를 차트로 시각화합니다.
*   **상대 강도(RS) 분석**: 벤치마크(KOSPI, KOSDAQ 등) 대비 각 테마의 강세를 수치로 확인할 수 있습니다.
*   **캔들 기반 기간 분석**: 단기 기간(5일, 1개월, 3개월, 6개월)은 달력 일수가 아닌 실제 거래일(캔들) 수 기준으로 분석합니다.
    - 5일 → 최근 5봉, 1개월 → 20봉, 3개월 → 60봉, 6개월 → 120봉
    - 1년 이상, YTD 등은 달력 기반 유지
*   **ETF 구성종목 조회**: 성과 요약 테이블에서 행을 클릭하면 해당 ETF의 구성종목(비중, 시가총액 등)과 동일 기간 등락률을 확인할 수 있습니다.
*   **유연한 종목 관리**: `theme_etf_data.json` 파일을 통해 비교할 ETF 리스트를 손쉽게 추가하거나 수정할 수 있습니다.
*   **편의 기능**: 사이드바의 '전체 선택' / '선택 해제' 버튼을 통해 다수의 테마를 원클릭으로 관리할 수 있습니다.

## 대시보드 구성

| 섹션 | 내용 |
|------|------|
| 1. 가격 추이 차트 | 벤치마크 & 테마 ETF 가격을 100 기준화하여 비교 |
| 2. 기간 성과 요약 | 수익률, 연율화 변동성, 벤치마크 대비 RS를 테이블로 표시 |
| 3. 상관관계 매트릭스 | 테마 간 일간 수익률 기준 피어슨 상관계수 |
| 4. ETF 구성종목 | 성과 테이블에서 행 클릭 시 구성종목 상세 표시 |

## 설치 방법

1.  이 저장소를 클론합니다.
    ```bash
    git clone https://github.com/your-username/etf-theme-trend.git
    cd etf-theme-trend
    ```

2.  필요한 Python 패키지를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

## 실행 방법

### 1. Python 직접 실행
아래 명령어로 Streamlit 앱을 실행합니다.

```bash
streamlit run etf_theme_rs_trend.py
```

브라우저가 자동으로 열리며 대시보드를 확인할 수 있습니다.

### 2. Docker Compose 실행 (권장)
Docker를 사용하여 더욱 안정적으로 서비스를 실행할 수 있습니다. 특히 **자동 재실행(Auto-Restart)** 기능이 포함되어 있어, 컨테이너가 중단되거나 시스템이 재부팅되어도 자동으로 복구됩니다.

```bash
# 컨테이너 빌드 및 실행 (백그라운드)
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 컨테이너 중지
docker-compose down
```
주요 특징:
- `restart: unless-stopped` 정책이 적용되어 수동으로 끄지 않는 한 항상 살아납니다.
- 볼륨 마운트(`.:/app`)로 개발 중인 코드가 컨테이너와 실시간으로 동기화됩니다.


## 테마/종목 추가 및 수정

`theme_etf_data.json` 파일을 열어 JSON 형식으로 새로운 테마나 ETF를 추가할 수 있습니다.

**예시:**

```json
{
    "새로운 테마 이름": {
        "name": "ETF 종목명",
        "code": "종목코드(6자리)"
    }
}
```

*   `code`는 KRX 종목코드(6자리)를 사용합니다 (예: `005930`, `305720`).
*   `FinanceDataReader`가 지원하는 모든 종목(ETF 포함)을 추가할 수 있습니다.

## 파일 구조

```
etf_lab/
├── etf_theme_rs_trend.py   # 메인 Streamlit 애플리케이션
├── theme_etf_data.json     # 테마 및 ETF 정의 (설정)
├── requirements.txt        # Python 의존성
├── Dockerfile              # Docker 빌드 설정
├── docker-compose.yml      # Docker Compose 설정
├── .dockerignore           # Docker 빌드 제외 목록
├── .gitignore              # Git 추적 제외 목록
└── rules/
    └── TEAM_RULES.md       # 팀 협업 규칙
```

## 의존성

| 패키지 | 용도 |
|--------|------|
| `streamlit` | 웹 대시보드 프레임워크 |
| `pandas` | 데이터 처리 |
| `finance-datareader` | ETF/주식/인덱스 가격 데이터 조회 |
| `pykrx` | ETF 구성종목(PDF) 조회 |

## 데이터 출처

*   가격 데이터: [FinanceDataReader](https://github.com/financedata-org/FinanceDataReader) — KRX·Yahoo Finance 등
*   ETF 구성종목: [pykrx](https://github.com/sharebook-kr/pykrx) — KRX(한국거래소) 공식 데이터
