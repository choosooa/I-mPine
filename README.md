# 🌲 I'mPine

**소나무재선충병(Pine Wilt Disease) 방제 전략 수립을 위한 데이터 분석 프로젝트**

> 비어플(BEEPL) × 임업통계 활용 경진대회 참가 레포지토리입니다.
> 전국 소나무재선충병 발생 현황부터 방제취약성 진단, 예산배분, 우선지원·맞춤형 방제 설계까지
> **4개 챕터(CH1~CH4)** 로 이어지는 분석 파이프라인을 구성했습니다.

---

## 📌 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 🎯 주제 | 소나무재선충병 발생 분석 및 방제 취약지역 우선지원 전략 설계 |
| 🗂️ 대회 | 임업통계 활용 경진대회 |
| 🧭 구성 | EDA → 모델링 → 대시보드 → 보고서, 총 4단계(CH1~CH4) 스토리라인 |
| 🛠️ 산출물 | 인터랙티브 대시보드 4종 + 통합 대시보드 + 분석 보고서(1~6차) |

---

## 🧩 분석 스토리라인 (CH1 → CH4)

```mermaid
flowchart LR
    A["🔍 CH1<br/>발생현황 분석"] --> B["📊 CH2<br/>방제취약성지수 · 예산배분"]
    B --> C["🎯 CH3<br/>우선지원 전략 설계"]
    C --> D["🛠️ CH4<br/>맞춤형 방제 설계"]
```

| 챕터 | 이름 | 무엇을 하나요? |
|---|---|---|
| 🔍 **CH1** | 소나무재선충병 발생현황 분석 | 전국 시군구·격자 단위 피해 추세, 반복발생 패턴, 공식통계와 원자료 검증(오차 0.67%) |
| 📊 **CH2** | 방제취약성지수 및 예산배분 모델링 | 기후위험도·노출도·지자체 대응역량·국가대응수준·인위적확산 5개 도메인 기반 취약성 지수화, 예산배분 시뮬레이션 |
| 🎯 **CH3** | 우선지원 전략 설계 | 취약성 지수 + 현재 피해등급을 교차해 우선지원 대상 지역 선정 |
| 🛠️ **CH4** | 맞춤형 방제 설계 | 지역 특성에 맞는 방제 방식·강도를 계산해주는 시뮬레이션 계산기 |

---

## 🖥️ 대시보드 미리보기

각 챕터는 **바닐라 HTML/CSS/JS + Leaflet + Chart.js** 기반의 단일 페이지 대시보드로 제작되어 있어, 별도 설치 없이 브라우저로 바로 열어볼 수 있습니다.

| 파일 | 설명 |
|---|---|
| [`ch1/ch1.html`](./ch1/ch1.html) | 🗺️ 전국 발생현황 지도 + 추이 대시보드 |
| [`ch2/ch2.html`](./ch2/ch2.html) | 📈 방제취약성지수 및 예산배분 대시보드 |
| [`ch3/ch3.html`](./ch3/ch3.html) | 🏆 우선지원 전략 설계 대시보드 |
| [`ch4/ch4.html`](./ch4/ch4.html) | 🧮 맞춤형 방제 설계 계산기 |
| [`통합대시보드.html`](./통합대시보드.html) | 🌐 CH1~CH4를 한 화면에서 살펴보는 통합 대시보드 |
| [`산림청_연동_컨셉목업.html`](./산림청_연동_컨셉목업.html) | 🏛️ 산림청 누리집 연동 컨셉 목업(시안) |

### ▶️ 실행 방법

별도 서버 없이도 열리지만, 지도(Leaflet)와 데이터 로딩(fetch)이 정상 동작하려면 로컬 서버로 여는 것을 권장합니다.

```bash
# 저장소 클론
git clone https://github.com/choosooa/I-mPine.git
cd I-mPine

# 로컬 서버 실행 (택 1)
python3 -m http.server 8000
# 또는
npx serve .

# 브라우저에서 접속
# http://localhost:8000/ch1/ch1.html
```

---

## 🔑 핵심 분석 결과 요약 (CH1 기준)

| 지표 | 값 |
|---|---|
| 🌲 최신 발생주기 피해고사목 | 약 177만 그루 |
| 🪓 총 제거목 | 약 309만 그루 |
| 📍 발생 시군구 | 166개 |
| 🚨 심 이상 지역 | 27개 (전국 피해의 **81%**) |
| 🔁 100m 격자 반복관측비율 | **44.2%** (기존 관측지역 재관측 비중 62.1%) |
| ✅ 원자료-공식통계 오차 | **0.67%** (내부 기준 1.0% 미만 통과) |

> 👉 신규 확산 차단만큼 **반복발생 지역에 대한 지속 관리**, 그리고 심 이상 27개 지역에 대한 **집중 투입**이 방제 전략의 핵심 시사점입니다.
> 상세 내용은 [`EDA/CH1/CH1_결과해석_시사점.md`](./EDA/CH1/CH1_결과해석_시사점.md) 참고.

---

## 📁 폴더 구조

```
I-mPine/
├── ch1/               🗺️  CH1 대시보드 (HTML/JS + 지도 데이터)
├── ch2/               📈  CH2 대시보드
├── ch3/               🎯  CH3 대시보드
├── ch4/               🧮  CH4 대시보드
├── EDA/                    탐색적 데이터 분석
│   ├── CH1/               ├─ 발생현황 EDA 노트북 & 결과해석 문서
│   ├── CH2/               ├─ 취약성지수 도메인별 EDA
│   └── output/            └─ EDA 산출 이미지·지도·CSV
├── Modeling/               모델링 버전별 아카이브 (1차 ~ 6차)
│   ├── 1차_분석방향/       ├─ 초기 분석 방향 설정
│   ├── 2차 ~ 5차/          ├─ 지표·모델 고도화 반복
│   ├── 5.5차_TierA_실험/   ├─ 시군구 코드 크로스워크(250→229) 보정 실험
│   └── 6차/                └─ 최종 모델 · 보고서 · 검증 자료
├── 보고서_작성/             경진대회 신청서 및 방법론 정리 문서
├── 통합대시보드.html         CH1~CH4 통합 대시보드
└── 산림청_연동_컨셉목업.html  산림청 누리집 연동 컨셉 목업
```

---

## 🛠️ 기술 스택

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=flat-square&logo=leaflet&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chart.js&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)

- **분석/모델링**: Python (Pandas, Jupyter Notebook)
- **시각화 대시보드**: Vanilla JS, Leaflet.js(지도), Chart.js(차트)
- **좌표계**: EPSG:5186
- **보고서**: Word(.docx), HWPX, PDF

---

## 👥 기여자

| 이름 | 역할 |
|---|---|
| choosooa | 프로젝트 총괄 · CH1 대시보드 · 데이터 정리 |
| 이은서 | CH2 EDA · 변수 설계 |
| 이찬행 | CH2 도메인별 EDA (기후위험도·노출도·지자체 대응역량·국가대응수준) |

---

## 📄 라이선스

본 저장소는 임업통계 활용 경진대회 제출을 위한 프로젝트입니다.
