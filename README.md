# 산업/테마 ETF 동향 대시보드 (ETF Theme RS Trend)

국내 상장된 주요 테마별 대표 ETF의 가격 추이와 상대 강도(RS, Relative Strength)를 분석하고, 벤치마크(KOSPI/KOSDAQ) 대비 성과를 비교하는 Streamlit 대시보드입니다.

## 주요 기능

*   **테마별 ETF 가격 비교**: KODEX, TIGER, SOL 등 주요 운용사의 대표 테마 ETF들의 가격 추이를 차트로 시각화합니다.
*   **상대 강도(RS) 분석**: 벤치마크(KOSPI, KOSDAQ 등) 대비 각 테마의 강세를 수치로 확인할 수 있습니다.
*   **기간 설정**: 1년, 3년, 5년, YTD 등 다양한 기간에 대한 성과 분석이 가능합니다.
*   **유연한 종목 관리**: `theme_etf_data.json` 파일을 통해 비교할 ETF 리스트를 손쉽게 추가하거나 수정할 수 있습니다.
*   **편의 기능**: 사이드바의 '전체 선택' / '선택 해제' 버튼을 통해 다수의 테마를 원클릭으로 관리할 수 있습니다.
*   **데이터 신뢰성**: `FinanceDataReader` 라이브러리를 사용하여 KRX·Yahoo Finance 등 다양한 소스에서 안정적인 데이터를 제공합니다.

## 설치 방법

1.  이 저장소를 클론합니다.
    ```bash
    git clone https://github.com/your-username/etf-theme-trend.git
    cd etf-theme-trend
    ```

2.  필요한 Python 패키지를 설치합니다.
    ```bash
    pip install streamlit pandas finance-datareader
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
# 컨테이너 실행 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 중지
docker-compose down
```
주요 특징:
- `restart: unless-stopped` 정책이 적용되어 수동으로 끄지 않는 한 항상 살아납니다.
- 개발 중인 코드가 컨테이너와 실시간으로 동기화됩니다.


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

*   `etf_theme_rs_trend.py`: 메인 애플리케이션 코드
*   `theme_etf_data.json`: 테마 및 ETF 정의 파일 (설정)
*   `.gitignore`: Git 추적 제외 파일 목록

## 데이터 출처

*   이 프로젝트는 [FinanceDataReader](https://github.com/financedata-org/FinanceDataReader)를 통해 KRX·Yahoo Finance 등의 데이터를 사용합니다.
