# -*- coding: utf-8 -*-
"""
Model 2 (재발위험 조기경보모형) - 6차 검증 방법 재구현
- 원본 model2_production_final.py 미확보로 재구현.
- Model 1(구조적취약성지수) 위에 t-1 확산이력(연속발생연수, 집단발생여부, 인접시군 피해밀도)을 추가.
- 데이터 누수 방지: _gm(그룹평균)은 훈련기간에서만 계산해 홀드아웃에 고정 적용(frozen-gm).
- 2023년은 데이터유형=추정이라 검증/적합 모두에서 제외(6차 §5.4와 동일 기준).
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score

PANEL = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\6차\CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
Y = "log_피해밀도_본per_ha"
AREA = "log_소나무림면적"
WOOD = "log1p_원목생산업체수"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

df = pd.read_csv(PANEL, low_memory=False)

# ── 표본 정의 (Model 1과 동일 카스케이드, 검증 완료된 로직) ─────────────────
excl_area = df.loc[df[AREA].isna(), ["시도", "시군구"]].drop_duplicates()
d = df.merge(excl_area.assign(_e1=1), on=["시도", "시군구"], how="left")
d = d[d["_e1"].isna()].drop(columns="_e1")
d = d[d["소나무림면적_자료유효_flag"] != 0]

CORE = {
    "노출도": ["소나무류_면적비율(%)"],
    "기후위험도": ["연강수량_mm", "GDD_솔수염하늘소_base11.9"],
    "지자체대응역량": ["대응자원투입예산_소나무림ha당_log_재선충명시", "예찰사업_재선충명시_존재_flag"],
    "인위적확산": [WOOD],
}
ALL_CORE = [v for vs in CORE.values() for v in vs] + [AREA, Y]
model_df = d.dropna(subset=ALL_CORE).copy()
log(f"[Model1 표본] {model_df.shape}, 시군구={model_df[['시도','시군구']].drop_duplicates().shape[0]}")

# ── 도메인 점수·구조적취약성지수 (Model 1과 동일) ──────────────────────────
Xa = sm.add_constant(model_df[AREA])
model_df["원목업체_resid"] = sm.OLS(model_df[WOOD], Xa).fit().resid

def within_year_z(frame, col):
    return frame.groupby("연도")[col].transform(lambda s: (s - s.mean()) / s.std(ddof=0))

INDEX_INPUTS = {
    "노출도": [("소나무류_면적비율(%)", +1)],
    "기후위험도": [("연강수량_mm", +1), ("GDD_솔수염하늘소_base11.9", +1)],
    "지자체대응역량": [("대응자원투입예산_소나무림ha당_log_재선충명시", -1), ("예찰사업_재선충명시_존재_flag", -1)],
    "인위적확산": [("원목업체_resid", -1)],
}
dom_cols = []
for dom, items in INDEX_INPUTS.items():
    zs = [within_year_z(model_df, col) * direction for col, direction in items]
    model_df[f"{dom}_점수"] = pd.concat(zs, axis=1).mean(axis=1)
    dom_cols.append(f"{dom}_점수")
model_df["구조적취약성지수"] = model_df[dom_cols].mean(axis=1)
model_df["Y_bin"] = (model_df[Y] > 0).astype(int)
model_df["key"] = model_df["시도"] + model_df["시군구"]

# ── t-1 확산이력 lag 생성 (2016년은 lag 공급용으로만 사용, 자체 행은 이후 제외) ──
LAG_SRC = ["연속발생연수", "집단발생여부", "log_인접시군_피해밀도_본per_ha"]
full_sorted = df.sort_values(["시도", "시군구", "연도"]).copy()
full_sorted["key"] = full_sorted["시도"] + full_sorted["시군구"]
for c in LAG_SRC:
    full_sorted[f"{c}_L1"] = full_sorted.groupby("key")[c].shift(1)
lag_cols = ["연도", "시도", "시군구"] + [f"{c}_L1" for c in LAG_SRC]
model_df = model_df.merge(full_sorted[lag_cols], on=["연도", "시도", "시군구"], how="left")

LAG_L1 = [f"{c}_L1" for c in LAG_SRC]
m2 = model_df.dropna(subset=LAG_L1 + ["구조적취약성지수", "Y_bin"]).copy()
# 2023 제외 (데이터유형=추정): 검증·적합 전부에서 제외 (6차와 동일 기준)
m2 = m2[m2["연도"] != 2023]
log(f"\n[Model2 표본(2017-2022, lag 확보)] {m2.shape}, 시군구={m2[['시도','시군구']].drop_duplicates().shape[0]}")

XVARS = ["구조적취약성지수"] + LAG_L1

def add_frozen_gm(train_df, apply_df, cols, group="key"):
    """훈련기간에서만 그룹평균 계산 후 고정 적용 (frozen-gm, 누수 차단)"""
    gm_table = train_df.groupby(group)[cols].mean()
    gm_table.columns = [f"{c}_gm" for c in cols]
    out = apply_df.merge(gm_table, on=group, how="left")
    # 훈련기간에 아예 없던 그룹(신규 시군구)은 전체 훈련평균으로 대체
    for c in cols:
        out[f"{c}_gm"] = out[f"{c}_gm"].fillna(train_df[c].mean())
    return out

def fit_eval(train_raw, test_raw, label):
    train = add_frozen_gm(train_raw, train_raw, XVARS)
    test = add_frozen_gm(train_raw, test_raw, XVARS)  # frozen: train 기준 gm을 test에도 적용
    xcols = XVARS + [f"{c}_gm" for c in XVARS]
    Xtr = sm.add_constant(train[xcols])
    model = sm.GLM(train["Y_bin"], Xtr, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": train["key"]})
    auc_tr = roc_auc_score(train["Y_bin"], model.predict(Xtr))
    Xte = sm.add_constant(test[xcols], has_constant="add")
    auc_te = roc_auc_score(test["Y_bin"], model.predict(Xte)) if len(test) else None
    log(f"\n----- {label} -----")
    log(f"train n={len(train)}, AUC={auc_tr:.4f}")
    if auc_te is not None:
        log(f"test  n={len(test)}, AUC={auc_te:.4f}")
    log(model.summary2().tables[1].round(4).to_string())
    return model, auc_tr, auc_te

# ── 훈련(2017-2020) vs 홀드아웃(2021-2022), frozen-gm ──────────────────────
train = m2[m2["연도"].between(2017, 2020)].copy()
holdout = m2[m2["연도"].between(2021, 2022)].copy()
model_final, auc_tr, auc_ho = fit_eval(train, holdout, "Model2 훈련/홀드아웃 (frozen-gm)")

# ── 단순 기준모형 비교 ──────────────────────────────────────────────────────
for base_col in ["연속발생연수_L1"]:
    Xb = sm.add_constant(holdout[[base_col]])
    m_simple_tr = sm.GLM(train["Y_bin"], sm.add_constant(train[[base_col]]), family=sm.families.Binomial()).fit()
    auc_simple = roc_auc_score(holdout["Y_bin"], m_simple_tr.predict(Xb))
    log(f"\n[기준모형: {base_col} 단독] 홀드아웃 AUC={auc_simple:.4f}")

# ── Rolling-origin (frozen-gm, 2023 제외) ──────────────────────────────────
log(f"\n{'='*60}\nRolling-origin\n{'='*60}")
for train_end, test_year in [(2020, 2021), (2021, 2022)]:
    tr = m2[m2["연도"] <= train_end].copy()
    te = m2[m2["연도"] == test_year].copy()
    _, atr, ate = fit_eval(tr, te, f"rolling <= {train_end} -> {test_year}")

# ── 최종 프로덕션 모형: 2017-2022 전체로 적합, 2022년 단면 예측 (6차 §9.3과 동일 기준) ──
log(f"\n{'='*60}\n최종 프로덕션 모형 (2017-2022 전체 적합)\n{'='*60}")
full_gm = m2.groupby("key")[XVARS].mean()
full_gm.columns = [f"{c}_gm" for c in XVARS]
m2_full = m2.merge(full_gm, on="key", how="left")
xcols = XVARS + [f"{c}_gm" for c in XVARS]
Xfull = sm.add_constant(m2_full[xcols])
model_prod = sm.GLM(m2_full["Y_bin"], Xfull, family=sm.families.Binomial()).fit(
    cov_type="cluster", cov_kwds={"groups": m2_full["key"]})
log(model_prod.summary2().tables[1].round(4).to_string())
auc_prod = roc_auc_score(m2_full["Y_bin"], model_prod.predict(Xfull))
log(f"전체(2017-2022) 적합 AUC = {auc_prod:.4f}")

# 2022년 단면 예측 (시군구별 "현재" 재발위험확률)
snap2022 = m2_full[m2_full["연도"] == 2022].copy()
Xsnap = sm.add_constant(snap2022[xcols], has_constant="add")
snap2022["재발위험확률"] = model_prod.predict(Xsnap)
snap_out = snap2022[["시도", "시군구", "구조적취약성지수", "재발위험확률"]].sort_values("재발위험확률", ascending=False)
log(f"\n[2022년 기준 재발위험확률 상위 10개]")
log(snap_out.head(10).to_string(index=False))

# ── 저장 ─────────────────────────────────────────────────────────────────
import os
OUTDIR = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\7차"
os.makedirs(OUTDIR, exist_ok=True)
snap_out.to_csv(os.path.join(OUTDIR, "Model2_재발위험확률_2022기준_final.csv"), index=False, encoding="utf-8-sig")
with open(os.path.join(OUTDIR, "Model2_final_로그.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
print("\n저장 완료:", OUTDIR)
