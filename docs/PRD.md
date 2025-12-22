# 제품 요구사항 문서 (PRD): Zero Cost & Zero Maintenance DA Portfolio

## 1. 프로젝트 개요
본 프로젝트는 **"비용 0원, 관리 부담 0%"**를 목표로 하는 데이터 분석가(DA) 포트폴리오용 MVP 프로젝트입니다. 대학원생이나 취업 준비생이 서버 비용이나 복잡한 인프라 관리 없이, 현업(당근마켓 등)에서 사용하는 **BigQuery, SQL, Python** 역량을 증명할 수 있는 실무 지향적 환경을 구축합니다.

## 2. 프로젝트 목표 및 핵심 가치
- **Zero Cost (비용 0원)**: 모든 도구를 Free Tier 범위 내에서 사용하여 운영 비용을 완벽하게 제거합니다.
- **Zero Maintenance (유지보수 제로)**: 서버리스(Serverless) 아키텍처를 채택하여 서버 관리, 패치, 모니터링 등의 부담을 없앱니다.
- **High Impact (실무 역량 증명)**: 로컬 DB가 아닌 클라우드 데이터 웨어하우스(BigQuery)와 자동화 도구(GitHub Actions)를 사용하여 데이터 엔지니어링 및 SQL 활용 능력을 보여줍니다.

## 3. 타겟 사용자
- 서버 비용이 부담스러운 대학원생 및 취업 준비생.
- 데이터 분석 역량뿐만 아니라 데이터 파이프라인 구축 경험을 보여주고 싶은 예비 DA.
- 언제 어디서든 접속 가능한 포트폴리오(웹 대시보드)가 필요한 지원자.

## 4. 기술 스택 (Tech Stack)

| 구분 | 추천 기술 | 선택 이유 | 비용 |
| :--- | :--- | :--- | :--- |
| **데이터 생성** | Python (Faker) | 당근마켓 유저 행동 로그(Users, Events)를 가상으로 무한 생성 가능. | 무료 |
| **ETL/자동화** | GitHub Actions | 별도 서버 없이 정해진 시간(Cron)에 스크립트를 실행하여 데이터 적재 자동화. | 무료 |
| **데이터 웨어하우스** | BigQuery Sandbox | 카드 등록 불필요. 10GB 저장/1TB 쿼리 무료 제공. 실무 SQL 환경과 동일. | 무료 |
| **데이터 분석** | Google Colab | 브라우저 기반 분석 환경. 로컬 리소스 제약 없음. | 무료 |
| **시각화 (BI)** | Looker Studio | BigQuery와 Native 연동 지원. 별도 배포 과정 없이 실시간 대시보드 공유 가능. | 무료 |

## 5. 시스템 아키텍처

```mermaid
graph LR
    A[GitHub Actions<br/>(Daily Cron Schedule)] -->|Run Python Script| B(Data Generation<br/>Faker Library)
    B -->|Upload Logs| C{BigQuery Sandbox<br/>(Data Warehouse)}
    C -->|Query & Viz| D[Looker Studio<br/>(Dashboard)]
    C -->|Deep Dive Analysis| E[Google Colab<br/>(Notebook)]
```

### 상세 흐름
1.  **데이터 자동 적재 (GitHub Actions + Python)**
    *   매일 지정된 시간(예: 새벽 2시)에 GitHub Actions 워크플로우 실행.
    *   Python 스크립트가 실행되어 전일자 가상 유저 행동 로그 생성.
    *   생성된 데이터를 BigQuery로 바로 전송 (pandas-gbq 또는 API 활용).
2.  **데이터 저장 (BigQuery Sandbox)**
    *   서버 관리 없이 데이터 영구 저장.
    *   파티셔닝(Partitioning) 및 클러스터링(Clustering)을 적용하여 쿼리 효율 최적화 연습 가능.
3.  **분석 및 시각화**
    *   **Looker Studio**: BigQuery 테이블을 소스로 연결하여 KPI(일일 활성 유저, 전환율 등) 대시보드 자동 업데이트.
    *   **Google Colab**: A/B 테스트 통계 검정, 복잡한 리텐션 분석 등을 수행하고 결과를 주피터 노트북으로 공유.

## 6. 주요 기능 및 구현 범위

### 6.1. 가상 데이터 생성기
*   **Users 테이블**: 유저 ID, 가입일, 지역(서울 서초구 등), 데모그래픽 정보.
*   **Events 테이블**: 상세페이지 진입, 버튼 클릭, 구매/가입 완료 등 행동 로그 (Timestamp 포함).
*   **실험 데이터**: A/B 테스트 그룹 할당 정보.

### 6.2. 자동화 파이프라인
*   GitHub Repository 내 `.github/workflows/daily_etl.yml` 작성.
*   Google Cloud Service Account 키를 GitHub Secrets로 안전하게 관리.

### 6.3. 분석 시나리오 (예시)
*   **퍼널 분석**: 홈 -> 상세 -> 결제시도 -> 결제완료 단계별 전환율.
*   **리텐션 분석**: 가입 코호트별 주간/월간 리텐션 차트.
*   **A/B 테스트 검정**: 실험군(B안)과 대조군(A안) 간의 핵심 지표 통계적 유의성 검증 (Chi-square, T-test).

## 7. 성공 지표 및 기대 효과
*   **자동화 안정성**: 7일 이상 수동 개입 없이 데이터 파이프라인 정상 가동.
*   **비용 효율성**: 프로젝트 운영 기간 동안 발생 비용 0원 유지.
*   **데모 가용성**: 면접관이 URL 클릭 한 번으로 최신 데이터가 반영된 대시보드 확인 가능.
