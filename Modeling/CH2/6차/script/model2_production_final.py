# -*- coding: utf-8 -*-
"""
Model 2 (조기경보모형) v2 - 데이터 누수 수정 + 2023(추정치) 검증대상 제외
QA 반영 사항:
  1) 데이터 누수 수정: _gm(시군구 평균)을 훈련기간(2017-2020) 데이터에서만 계산 -> 그 frozen
     매핑을 홀드아웃(2021-2022)에 그대로 적용. 이전 버전(v1)은 전체기간에서 _gm을 먼저 계산해
     홀드아웃 평가에 미래정보가 섞여 있었음(리뷰 피드백으로 발견, 코드 확인으로 100% 재현).
  2) `데이터유형` 컬럼 확인 결과 2016·2023년이 "추정(시군구 평균비중x국가총량)"이지 실측이 아님
     -> rolling-origin에서 test=2023 스텝 제외(추정 Y를 정답으로 채점하는 문제). 2016은 이미
     train/holdout 어디에도 포함되지 않으나, 2017년의 t-1 lag 입력값이 2016(추정)에서 온다는
     점은 잔존 한계로 별도 명시.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import roc_auc_score

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
MODELDIR = f"{OUTDIR}/모델링"
PANEL = f"{OUTDIR}/CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
IDXFILE = f"{MODELDIR}/구조적취약성지수_final.csv"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

Y = "log_피해밀도_본per_ha"
LAG_VARS = ["연속발생연수", "집단발생여부", "log_인접시군_피해밀도_본per_ha"]

# =========================================================
# 0. 데이터유형(실측/추정) 확인
# =========================================================
panel_raw = pd.read_csv(PANEL)
dtype_by_year = panel_raw.groupby("연도")["데이터유형"].value_counts()
log("=== 연도별 데이터유형 ===")
log(dtype_by_year.to_string())
log("-> 2016·2023년은 '추정' 값이므로 rolling-origin에서 test=2023 스텝은 제외한다.\n")

# =========================================================
# 1. 데이터 결합 + t-1 시차
# =========================================================
panel = panel_raw[["연도", "시도", "시군구"] + LAG_VARS].copy()
idx = pd.read_csv(IDXFILE)

p = panel.copy()
p["key"] = p["시도"] + p["시군구"]
p = p.sort_values(["key", "연도"])
for c in LAG_VARS:
    p[f"{c}_L1"] = p.groupby("key")[c].shift(1)

df = idx.merge(p[["연도", "시도", "시군구"] + [f"{c}_L1" for c in LAG_VARS]],
               on=["연도", "시도", "시군구"], how="left")
df["key"] = df["시도"] + df["시군구"]
lag_cols = [f"{c}_L1" for c in LAG_VARS]
before = len(df)
df = df.dropna(subset=lag_cols + ["구조적취약성지수"]).copy()
log(f"[t-1 시차 결합] {before} -> {len(df)}행")

BASE_X = ["구조적취약성지수"]
FULL_X = BASE_X + lag_cols

train = df[df["연도"].between(2017, 2020)].copy()
holdout = df[df["연도"].between(2021, 2022)].copy()
log(f"[표본] 훈련(2017-2020, 전부 실측) n={len(train)}, 홀드아웃(2021-2022, 전부 실측) n={len(holdout)}")

# =========================================================
# 2. 누수 수정: _gm은 훈련기간에서만 계산 -> frozen 매핑을 두 표본에 동일 적용
# =========================================================
def freeze_gm_from_train(train_frame, apply_frames, cols, group="key"):
    means = train_frame.groupby(group)[cols].mean()
    means.columns = [f"{c}_gm" for c in cols]
    out = []
    for frame in apply_frames:
        merged = frame.merge(means, on=group, how="left")
        # 훈련기간에 해당 시군구가 없었을 경우(있을 수 없지만 안전장치) 전체훈련평균으로 대체
        for c in cols:
            merged[f"{c}_gm"] = merged[f"{c}_gm"].fillna(means[f"{c}_gm"].mean())
        out.append(merged)
    return out

train_frozen, holdout_frozen = freeze_gm_from_train(train, [train, holdout], FULL_X)
log(f"\n[누수 수정] _gm을 훈련기간(2017-2020)에서만 계산 -> 훈련·홀드아웃 양쪽에 동일 매핑 적용")
log(f"  (v1 버그: 전체기간에서 _gm을 먼저 계산해 홀드아웃 평가에 2021-2023년 정보가 섞였음)")

def run_model(frame, xcols, label):
    xcols_gm = xcols + [f"{c}_gm" for c in xcols]
    log(f"\n----- [{label}] (n={len(frame)}) -----")
    Xb = sm.add_constant(frame[xcols_gm])
    logit = sm.GLM(frame["Y_bin"], Xb, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": frame["key"]}
    )
    log(logit.summary2().tables[1].round(4).to_string())
    pred = logit.predict(Xb)
    auc = roc_auc_score(frame["Y_bin"], pred)
    log(f"  AUC={auc:.3f}")
    return auc

log(f"\n{'='*70}\n훈련(2017-2020) - Model 1 vs Model 2 (누수 수정판)\n{'='*70}")
auc_m1_tr = run_model(train_frozen, BASE_X, "Model 1(구조적지수만)/훈련")
auc_m2_tr = run_model(train_frozen, FULL_X, "Model 2(+t-1)/훈련")

log(f"\n{'='*70}\n홀드아웃(2021-2022) - Model 1 vs Model 2 (누수 수정판, _gm은 훈련기간에서 고정)\n{'='*70}")
auc_m1_ho = run_model(holdout_frozen, BASE_X, "Model 1(구조적지수만)/홀드아웃")
auc_m2_ho = run_model(holdout_frozen, FULL_X, "Model 2(+t-1)/홀드아웃")

log(f"\n{'='*70}\nAUC 비교 요약 (v1 누수판 대비)\n{'='*70}")
log(f"  Model 1 - 훈련 {auc_m1_tr:.3f} / 홀드아웃 {auc_m1_ho:.3f}   (v1과 동일 로직, 참고용)")
log(f"  Model 2 - 훈련 {auc_m2_tr:.3f} / 홀드아웃 {auc_m2_ho:.3f}   (v1 누수판: 0.981/0.962)")

# =========================================================
# 3. 단순 재발 기준모형 비교 (리뷰 권고 반영)
# =========================================================
log(f"\n{'='*70}\n단순 재발 기준모형 비교 (홀드아웃 AUC)\n{'='*70}")
baseline_specs = {
    "전년도 발생여부만(집단발생여부_L1)": ["집단발생여부_L1"],
    "연속발생연수_L1 단독": ["연속발생연수_L1"],
    "집단발생여부_L1 단독(gm 없이)": ["집단발생여부_L1"],
}
for label, cols in baseline_specs.items():
    Xtr = sm.add_constant(train[cols])
    m = sm.GLM(train["Y_bin"], Xtr, family=sm.families.Binomial()).fit()
    Xho = sm.add_constant(holdout[cols], has_constant="add")
    pred = m.predict(Xho)
    auc = roc_auc_score(holdout["Y_bin"], pred)
    log(f"  [{label}] 홀드아웃 AUC={auc:.3f}")

log(f"  [참고] Model 2(누수 수정, 전체변수+frozen gm) 홀드아웃 AUC={auc_m2_ho:.3f}")

# =========================================================
# 4. Rolling-origin - 2023(추정치) 테스트 스텝 제외
# =========================================================
log(f"\n{'='*70}\nRolling-origin 표본외 검증 (2023 테스트 제외 - 데이터유형=추정)\n{'='*70}")
for train_end, test_year in [(2020, 2021), (2021, 2022)]:  # (2022, 2023) 제외
    tr = df[df["연도"] <= train_end]
    te = df[df["연도"] == test_year]
    for xcols, label in [(BASE_X, "Model1"), (FULL_X, "Model2")]:
        Xtr = sm.add_constant(tr[xcols])
        m = sm.GLM(tr["Y_bin"], Xtr, family=sm.families.Binomial()).fit()
        Xte = sm.add_constant(te[xcols], has_constant="add")
        pred = m.predict(Xte)
        auc = roc_auc_score(te["Y_bin"], pred)
        log(f"  train<={train_end} -> test={test_year} [{label}] AUC={auc:.3f} (n={len(te)})")
log("  (참고: train<=2022 -> test=2023 스텝은 2023년 Y가 '추정'값이라 제외했다."
    " 이 스텝은 v1에서 Model2 AUC=0.955로 보고됐으나 재현하지 않는다.)")

# =========================================================
# 저장
# =========================================================
with open(f"{MODELDIR}/Model2_final_로그.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\n저장 완료: Model2_final_로그.txt")
