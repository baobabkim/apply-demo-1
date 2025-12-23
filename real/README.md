# C2C Marketplace User Retention Analysis

데이터 기반 C2C 마켓플레이스 유저 리텐션 향상을 위한 분석 및 실험 프로젝트

## 📋 프로젝트 개요

이 프로젝트는 C2C 마켓플레이스의 유저 리텐션을 개선하기 위해 데이터 분석과 A/B 테스트를 수행합니다. 가상의 유저 데이터를 생성하고, BigQuery에 적재하여 분석하며, Looker Studio와 Google Colab을 통해 인사이트를 도출합니다.

### 주요 목표
- **D+7 리텐션 5%p 개선**을 위한 핵심 동인 발견
- **상세 페이지 → 채팅 시작 전환율(CVR) 10% 향상**을 위한 UI/UX 개선안 제안

## 🏗️ 아키텍처

```
┌─────────────────┐
│ Data Generation │ (Python + Faker)
│   Engine        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Actions │ (Daily ETL at 02:00 KST)
│   Workflow      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   BigQuery      │ (Data Warehouse)
│   Analytics DB  │
└────────┬────────┘
         │
         ├─────────────────┐
         ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ Looker Studio│   │ Google Colab │
│  Dashboard   │   │   Analysis   │
└──────────────┘   └──────────────┘
```

## 🛠️ 기술 스택

- **Data Generation**: Python, Faker, Pandas, NumPy
- **Data Warehouse**: Google BigQuery
- **Automation**: GitHub Actions
- **Analysis**: Python (Pandas, Scipy, Statsmodels)
- **Visualization**: Looker Studio, Matplotlib, Seaborn
- **Collaboration**: Google Colab

## 📁 프로젝트 구조

```
.
├── .github/
│   └── workflows/
│       └── daily_etl.yml          # 일일 ETL 자동화
├── src/
│   └── generator/
│       ├── __init__.py
│       ├── users.py               # 유저 데이터 생성
│       └── events.py              # 이벤트 로그 생성
├── scripts/
│   ├── setup_bigquery.py          # BigQuery 초기 설정
│   └── load_data.py               # 데이터 적재
├── notebooks/
│   └── analysis.ipynb             # 분석 노트북
├── docs/
│   ├── PRD.md                     # 프로젝트 요구사항 문서
│   ├── TASK.md                    # 작업 목록
│   ├── Idelation.md               # 아이디어 문서
│   └── LOOKER_SETUP.md            # Looker Studio 설정 가이드
├── requirements.txt               # Python 의존성
├── .gitignore
└── README.md
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/baobabkim/apply-demo-1.git
cd apply-demo-1

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. GCP 설정

1. GCP 프로젝트 생성
2. BigQuery API 활성화
3. Service Account 생성 및 키 발급
4. 키 파일을 `service-account-key.json`으로 저장 (gitignore에 포함됨)

### 3. BigQuery 초기화

```bash
python scripts/setup_bigquery.py
```

### 4. 데이터 생성 및 적재

```bash
python scripts/load_data.py
```

### 5. GitHub Secrets 설정

Repository Settings > Secrets and variables > Actions에 다음 추가:
- `GCP_PROJECT_ID`: GCP 프로젝트 ID
- `GCP_SA_KEY`: Service Account JSON 키 (전체 내용)

## 📊 데이터 스키마

### Users Table
- `user_id`: STRING
- `name`: STRING
- `location`: STRING
- `join_date`: DATE
- `verified_neighborhood`: BOOLEAN
- `created_at`: TIMESTAMP

### Events Table
- `event_id`: STRING
- `user_id`: STRING
- `event_type`: STRING (page_view, search, item_view, chat_click, chat_send)
- `event_timestamp`: TIMESTAMP
- `ab_group`: STRING (control, treatment)
- `item_id`: STRING
- `session_id`: STRING

## 📈 분석 내용

1. **Funnel Analysis**: 메인 홈 → 검색 → 상세 페이지 → 채팅 클릭 → 채팅 발송
2. **Cohort Analysis**: 동네 인증, 첫 거래 성공 여부에 따른 리텐션 분석
3. **A/B Test**: 신뢰 지표 노출 기능의 효과 검증

## 📝 관련 문서

- [PRD (Product Requirements Document)](./docs/PRD.md)
- [Task List](./docs/TASK.md)
- [Looker Studio Setup Guide](./docs/LOOKER_SETUP.md)

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

## 📄 라이선스

MIT License
