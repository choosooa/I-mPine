# scripts/ — 1~2단계 + A안 작업 스크립트 모음

`rebuild_ch3_priority.py`(상위 폴더에 있는 것)는 **A/B안 나누기 이전의 예전 버전**입니다.
이 폴더의 스크립트들이 실제로 최종 A안을 만들고 검증한 진짜 작업물입니다.

## 실행 순서대로 정리

1. **`test_plan_formula.py` / `test_plan_formula_v2.py`**
   분석계획서 공식(`0.6×RiskPct+0.4×UnderfundPct`)을 실제 데이터로 검증. v2는 연도별 패널로 더 정확하게 재계산한 버전(내부 판단용, F10 대조).

2. **`test_formula_showdown.py`**
   6개 후보 공식(A~F) 전수비교 + 검증보고서 대안공식(C)의 자기충족성(tautology) 분해 검증.
   → C안 철회, E(RiskPct 단독) 방향 확정의 근거가 된 스크립트.

3. **`test_sign_flip.py` / `test_sign_flip2.py`**
   ⑤번(인위적확산 도메인 부호) A안 vs B안 비교 — 완도군 순위·재발확률 상관·피해량 상관 비교.

4. **`rebuild_optionA.py`** ⭐ 핵심
   실제 A안 최종본을 만든 스크립트. ch2/data.js의 `dom_인위적확산` 부호 반전 →
   index_main·위험지수·배분갭(OLS 재적합)·축A/축B(재분류)·CH3 dominant_domain/priority_score(RiskPct)/grade/priority_rank
   전부 재계산해서 `ch2/data.js`, `ch3/data.js`를 직접 덮어씀.

5. **`model1_ab_test/model1_A안_부호반전.py`** / **`model1_ab_test/model1_B안_원본부호.py`** ⭐ 핵심
   `Modeling/CH2/4차/model1_v4_final.py`를 원본 그대로 복사해 원목업체_resid 부호만 바꾼 버전(A) vs 안 바꾼 버전(B).
   원본 패널(`Modeling/CH2/3차/CH2_전체병합패널_..._최종보정3.csv`)로 실제 CRE 2부문모형을 완주해서
   진짜 AUC·between/within 계수·배분갭 회귀를 산출. 결과는 `output_A/`, `output_B/`에 저장됨
   (`Model1_v4_로그.txt`가 전체 로그, `구조적취약성지수_v4.csv`가 연도별 지수, `Model1_기여도분해_유형화_v4.csv`가 town-level 기여도).
   → 이 결과(A: AUC 0.600/0.616, B: AUC 0.600/0.594)를 `ch2/data.js`·`ch2.html`에 수기 반영함.

6. **`test_E_multimetric.py` / `test_E_multimetric2.py`**
   RiskPct(E) 채택안을 재발확률뿐 아니라 누적피해·피해밀도·반복관측률과도 대조 검증(다중지표 검증, 수식감사 최종본과 교차확인용).

7. **`check_final.py`**
   최종 A안 dashboard 파일(ch2/data.js, ch3/data.js)에 모든 수정이 실제로 반영됐는지 사후검증(완도군 순위, 배분갭 R², 부호 등).

## 핵심 결론 요약
- 최종 채택: **A안**(인위적확산 부호 +1 반전)
- 완도군: priority_rank 1위(원본) → 96위(A안 최종)
- Model1 홀드아웃 AUC: 0.594(B안) → 0.616(A안, 개선)
- 배분갭 회귀 R²: 3.40%(B안) → 4.78%(A안, 개선)
