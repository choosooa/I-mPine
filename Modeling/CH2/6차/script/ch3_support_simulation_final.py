# -*- coding: utf-8 -*-
"""
CH3 지원효과 시뮬레이션 (외부 QA 검토서 8장 권고 구조 구현)
5단계: ①대상지역분류 ②지원패키지매칭 ③변수변화가정 ④단기경보결합 ⑤민감도범위

원칙(검토서 그대로 반영):
  - "이 예산을 투입하면 피해가 몇 % 감소한다"(인과주장) 대신
    "정책개입 가능한 구조취약성 점수가 얼마나 개선되는지"만 시뮬레이션한다.
  - 정책으로 단기간에 바꾸기 어려운 변수(소나무면적·기후)는 고정하고,
    지자체대응역량(예산·예찰사업)만 개입 대상으로 조정한다.
  - Model 2는 효과의 직접 추정치가 아니라 단기 예찰 우선순위로만 결합한다.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
MODELDIR = f"{OUTDIR}/모델링"
PANEL = f"{OUTDIR}/CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

PRESCRIPTION = {
    "노출도-우세형": "예찰·모니터링 인프라 확충",
    "인위적확산-우세형": "도로변/원목유통 관리(이동경로 차단)",
    "복합형": "기본 대응체계·인력 확충",
}

# =========================================================
# ① 대상지역 분류 (기존 v4 산출물 그대로 사용)
# =========================================================
contrib = pd.read_csv(f"{MODELDIR}/Model1_기여도분해_유형화_final.csv")
target = contrib[contrib["축B_배분적정성"] == "부족"].copy()
log(f"[①대상지역분류] '부족' 판정 시군구 n={len(target)}/{len(contrib)}")
log(target["축A_위험요인유형"].value_counts().to_string())

# =========================================================
# ② 지원 패키지 매칭
# =========================================================
target["지원패키지"] = target["축A_위험요인유형"].map(PRESCRIPTION)
log(f"\n[②지원패키지매칭]")
log(target.groupby("축A_위험요인유형")["지원패키지"].first().to_string())

# =========================================================
# ③ 변수 변화 가정 - 지자체대응역량 도메인만 조정(정책개입 가능 변수로 한정)
#    노출도·기후위험도(소나무면적, 기후)는 고정, 인위적확산도 구조변수라 고정.
#    동일가중 지수 = 0.25*(노출도+기후+역량+확산) 이므로 역량_점수를 Δ만큼 올리면
#    지수는 정확히 0.25*Δ만큼 개선된다(선형 구조라 인과추정 없이도 산식으로 계산 가능).
# =========================================================
SCENARIOS = {"보수": 0.3, "기준": 0.6, "적극": 1.0}  # 지자체대응역량_점수 개선폭(SD 단위)

for name, delta in SCENARIOS.items():
    target[f"개선후_역량점수_{name}"] = target["지자체대응역량_점수"] + delta
    target[f"개선후_지수_{name}"] = target["구조적취약성지수"] + 0.25 * delta
    target[f"지수개선폭_{name}"] = target[f"개선후_지수_{name}"] - target["구조적취약성지수"]

log(f"\n[③변수변화가정] 지자체대응역량_점수를 보수(+0.3SD)/기준(+0.6SD)/적극(+1.0SD)만큼 개선")
log(f"  (동일가중 선형구조상 지수 개선폭 = 0.25 x 역량점수 개선폭 = {[round(0.25*d,3) for d in SCENARIOS.values()]})")

# 축B 재분류: 개선 후에도 여전히 "부족" 판정을 받을지(같은 3분위 컷오프 기준)
cutoffs = contrib.groupby("축B_배분적정성")["배분갭"].agg(["min", "max"])
log(f"\n[참고] 배분갭 3분위 컷오프\n{cutoffs.to_string()}")

log("\n=== 시나리오별 유형(축A)별 평균 지수개선폭 ===")
for name in SCENARIOS:
    log(f"\n[{name} 시나리오]")
    log(target.groupby("축A_위험요인유형")[f"지수개선폭_{name}"].agg(["mean", "count"]).round(3).to_string())

# =========================================================
# ④ 단기 경보 결합 - Model 2(현재 시점) 재발위험 확률 부여
#    검증용 train/holdout 분리가 아니라, 실측 연도(2017-2022) 전체로 적합한 뒤
#    가장 최근 실측연도(2022)의 예측확률을 "현재 단기 위험도"로 사용(생산적용 목적).
# =========================================================
Y = "log_피해밀도_본per_ha"
LAG_VARS = ["연속발생연수", "집단발생여부", "log_인접시군_피해밀도_본per_ha"]
idx = pd.read_csv(f"{MODELDIR}/구조적취약성지수_final.csv")
panel = pd.read_csv(PANEL)[["연도", "시도", "시군구"] + LAG_VARS]
panel["key"] = panel["시도"] + panel["시군구"]
panel = panel.sort_values(["key", "연도"])
for c in LAG_VARS:
    panel[f"{c}_L1"] = panel.groupby("key")[c].shift(1)

d = idx.merge(panel[["연도", "시도", "시군구"] + [f"{c}_L1" for c in LAG_VARS]],
              on=["연도", "시도", "시군구"], how="left")
d["key"] = d["시도"] + d["시군구"]
lag_cols = [f"{c}_L1" for c in LAG_VARS]
d = d.dropna(subset=lag_cols + ["구조적취약성지수"]).copy()
real_years = d[d["연도"].between(2017, 2022)]  # 실측 연도만 사용(2016·2023 추정치 제외)

FULL_X = ["구조적취약성지수"] + lag_cols
for c in FULL_X:
    real_years = real_years.copy()
    real_years[f"{c}_gm"] = real_years.groupby("key")[c].transform("mean")
xcols_gm = FULL_X + [f"{c}_gm" for c in FULL_X]
X = sm.add_constant(real_years[xcols_gm])
m2 = sm.GLM(real_years["Y_bin"], X, family=sm.families.Binomial()).fit(
    cov_type="cluster", cov_kwds={"groups": real_years["key"]}
)
real_years["재발위험확률"] = m2.predict(X)
latest = real_years[real_years["연도"] == 2022][["시도", "시군구", "재발위험확률"]]

target = target.merge(latest, on=["시도", "시군구"], how="left")
target["긴급도"] = pd.cut(target["재발위험확률"], bins=[-0.01, 0.3, 0.7, 1.01],
                        labels=["낮음(예방중심)", "중간", "높음(긴급대응 병행 필요)"])
log(f"\n[④단기경보결합] '부족' 판정 지역의 2022년 기준 재발위험확률(Model 2) 결합")
log(target["긴급도"].value_counts().to_string())

log("\n=== '긴급도 높음' + '부족' 동시 해당 지역 (최우선 대응) ===")
urgent = target[target["긴급도"] == "높음(긴급대응 병행 필요)"].sort_values("재발위험확률", ascending=False)
log(urgent[["시도", "시군구", "축A_위험요인유형", "구조적취약성지수", "재발위험확률", "지원패키지"]]
    .round(3).to_string(index=False))

# =========================================================
# ⑤ 민감도 범위 - 보수/기준/적극 시나리오 효과 범위 요약
# =========================================================
log(f"\n{'='*70}\n⑤ 민감도 범위 요약\n{'='*70}")
summary = target.groupby("축A_위험요인유형").agg(
    n=("시군구", "size"),
    현재지수=("구조적취약성지수", "mean"),
    보수=("지수개선폭_보수", "mean"),
    기준=("지수개선폭_기준", "mean"),
    적극=("지수개선폭_적극", "mean"),
)
log(summary.round(3).to_string())
log("\n해석: 동일가중 선형지수 구조상 개선폭은 시나리오별로 고정폭(0.075/0.15/0.25)이며 유형과 무관하다.")
log("실제 정책효과 범위는 '역량 개선폭 가정(0.3~1.0 SD)' 자체의 불확실성에서 나오므로, 이 폭을")
log("보수~적극 시나리오로 명시해 제시하는 것이 핵심이다. 이는 인과추정이 아니라 시나리오상 변화다.")

# =========================================================
# 저장
# =========================================================
target.to_csv(f"{MODELDIR}/CH3_구조취약성개선시나리오_부족지역_final.csv", index=False, encoding="utf-8-sig")
with open(f"{MODELDIR}/CH3_시나리오_로그_final.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\n저장 완료: CH3_구조취약성개선시나리오_부족지역_final.csv, CH3_시나리오_로그_final.txt")
