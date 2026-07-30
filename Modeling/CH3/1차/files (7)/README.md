# I'mPine P0/P1 패치 적용 가이드
# ═══════════════════════════════════════════════════

## 적용 순서 (P0 → P1)

### P0 — 제출 전 필수

| # | 파일 | 적용 방법 | 소요 |
|---|---|---|---|
| P0 #1 | `P0_1_fix_priority_score.py` | I-mPine 루트에서 `python patches/P0_1_fix_priority_score.py` 실행 → ch3/data_priority_fixed.json 생성 → 검증 후 ch3/data.js에 반영 | 30분 (코드 실행 + data.js 교체) |
| P0 #4 | `P0_4_sgg_code_alias.js` | ch2.html, ch3.html에 `resolveCode()` 함수 추가 + 지도 조회 코드 수정 (파일 내 주석 참조) | 30분 |
| P0 #5 | `P0_5_model2_auc_fix.js` | ch2/data.js에서 `validity.model2_note.holdout`을 0.947→0.911, note 문구 교체 | 5분 |
| P0 #6 | `P0_6_kpi_yoy_fix.js` | ch1/ch1.html에서 KPI 배열의 "전년비 +28만" 배지 삭제 | 5분 |

### P1 — 제출 전 권장

| # | 파일 | 적용 방법 | 소요 |
|---|---|---|---|
| P1 #14 | `P1_14_cross_metric_25.html` | ch1.html §03의 교차기준 카드를 교체, JS에서 .slice(0,7) 제거 | 20분 |
| P1 #16 | `P1_16_localize_cdn.sh` | `bash patches/P1_16_localize_cdn.sh` 실행 → 오프라인 테스트 | 10분 |
| P1 #17 | `P1_17_fix_paths.py` + `requirements.txt` | `python patches/P1_17_fix_paths.py` 실행 + requirements.txt를 루트에 복사 | 10분 |

## 적용 전 체크

1. **반드시 git commit 또는 백업 후 패치하세요.** 모든 .sh/.py 패치는 .bak 파일을 만들지만 이중 안전장치가 좋습니다.
2. P0 #1은 `scipy`가 필요합니다. `pip install -r requirements.txt` 먼저 실행하세요.
3. P0 #4 강원 매핑은 18/18 검증되었지만, 서울/인천/충북(45곳)은 GeoJSON 파일 자체를 교체해야 합니다.

## 적용 후 검증

```bash
# 1) 로컬 서버 시작
cd I-mPine && python3 -m http.server 8000

# 2) 통합대시보드 확인
open http://localhost:8000/통합대시보드_개선안.html

# 3) 각 챕터 지도에서 강원도가 보이는지 확인
# 4) CH2 §02에서 Model2 AUC가 0.911인지 확인
# 5) CH1 KPI에서 "전년비 +28만" 배지가 없는지 확인
# 6) Wi-Fi 끄고 CH2/CH3 지도·차트가 렌더링되는지 확인
```
