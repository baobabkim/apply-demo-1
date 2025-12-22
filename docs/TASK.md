# Project Tasks: Zero Cost & Zero Maintenance DA Portfolio

## 1. 환경 설정 및 기초 공사 (Setup)
- [ ] **GitHub Repository 초기화**
    - [ ] `.gitignore` 설정 (Python, virtualenv, Data files)
    - [ ] `README.md` 작성 (프로젝트 개요 및 아키텍처 다이어그램 포함)
- [ ] **GCP (Google Cloud Platform) 설정**
    - [ ] 새 프로젝트 생성 (e.g., `da-portfolio-mvp`)
    - [ ] BigQuery API 활성화 (Sandbox 모드 확인)
    - [ ] Service Account(SA) 생성 및 Key(JSON) 다운로드
    - [ ] GitHub Repository Secrets 등록 (`GCP_SA_KEY`, `GCP_PROJECT_ID`)

## 2. 데이터 생성 엔진 구현 (Data Generator)
- [ ] **Python 프로젝트 구조 잡기**
    - [ ] `requirements.txt` 작성 (`faker`, `pandas`, `pandas-gbq`)
- [ ] **유저 데이터 생성 (`src/generator/users.py`)**
    - [ ] Faker를 이용한 유저 프로필 생성 (ID, 가입일자, 지역, 성별 등)
    - [ ] DataFrame 변환 및 검증
- [ ] **로그 데이터 생성 (`src/generator/events.py`)**
    - [ ] 유저 행동 패턴 정의 (Funnel: 홈 -> 상세 -> 가입/구매)
    - [ ] Timestamp 랜덤 생성 (최근 30일 기준 등)
    - [ ] A/B 테스트 그룹 할당 로직 구현

## 3. 데이터 웨어하우스 구축 (BigQuery)
- [ ] **데이터셋 생성**
    - [ ] `analytics` 데이터셋 생성 (US or Seoul Region)
- [ ] **테이블 스키마 설계**
    - [ ] `users` 테이블 스키마 정의 (Partitioning: 가입일자)
    - [ ] `events` 테이블 스키마 정의 (Partitioning: 이벤트 발생일자)
- [ ] **로컬 적재 테스트**
    - [ ] Python 스크립트로 생성된 데이터를 BigQuery에 업로드 테스트

## 4. 자동화 파이프라인 (ETL Automation)
- [ ] **GitHub Actions 워크플로우 작성 (`.github/workflows/daily_etl.yml`)**
    - [ ] Cron Schedule 설정 (매일 새벽 02:00 KST)
    - [ ] Python 환경 셋업 및 의존성 설치
    - [ ] 데이터 생성 스크립트 실행
    - [ ] BigQuery 적재 (Authentication 처리)
- [ ] **안정성 테스트**
    - [ ] 워크플로우 수동 실행 (workflow_dispatch) 및 성공 여부 확인

## 5. 분석 및 대시보드 (Analysis & BI)
- [ ] **Looker Studio 연동**
    - [ ] BigQuery 데이터 소스 연결
    - [ ] KPI 대시보드 구성 (DAU, WAU, Conversion Rate)
    - [ ] 필터 구현 (날짜, A/B 그룹)
- [ ] **Google Colab 심화 분석**
    - [ ] Colab 노트북 생성 및 BigQuery 연동
    - [ ] 통계적 유의성 검정(Chi-square test) 코드 작성
    - [ ] 리텐션 히트맵 시각화
