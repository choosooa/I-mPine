# -*- coding: utf-8 -*-
"""
Model 1 v3 재현판 (TierB) - 순수 TierA vs TierB 비교용
- v4_final.py에서 평균풍속_ms를 기후위험도 도메인에 다시 포함시켜 v3 사양대로 복원.
- 입력: 최종보정3.csv (TierB, 도로소나무비율_500m 2023년 고정)
- 기존 Modeling/2차/Model1_v3_로그.txt 값(AUC 0.617/0.622, Spearman 0.268/0.277,
  노출도-인위적확산 상호상관 0.416)과 일치하는지 검증용으로도 사용.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import roc_auc_score

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

MODELDIR = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\비교_TierA_vs_TierB"
PANEL = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\2차\CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv"
TAG = "TierB"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

df = pd.read_csv(PANEL, encoding="utf-8-sig")
log(f"[원본] {df.shape}")

excl_area_zero = df.loc[df["log_소나무림면적"].isna(), ["시도", "시군구"]].drop_duplicates()
excl_invalid = df.loc[df["소나무림면적_자료유효_flag"] == 0, ["연도", "시도", "시군구"]]
df = df.merge(excl_area_zero.assign(_e1=1), on=["시도", "시군구"], how="left")
df = df.merge(excl_invalid.assign(_e2=1), on=["연도", "시도", "시군구"], how="left")
df = df[df["_e1"].isna() & df["_e2"].isna()].drop(columns=["_e1", "_e2"]).reset_index(drop=True)
log(f"[표본정의 후] {df.shape}")

Y = "log_피해밀도_본per_ha"
CORE = {
    "노출도": ["소나무류_면적비율(%)"],
    "기후위험도": ["연강수량_mm", "평균풍속_ms", "GDD_솔수염하늘소_base11.9"],  # v3 사양(SPI3 제외, 평균풍속 포함)
    "지자체대응역량": ["대응자원투입예산_소나무림ha당_log_재선충명시", "예찰사업_재선충명시_존재_flag"],
    "인위적확산": ["도로소나무비율_500m", "log1p_원목생산업체수"],
}
AREA = "log_소나무림면적"
ALL_CORE = [v for vs in CORE.values() for v in vs] + [AREA, Y]

before = len(df)
model_df = df.dropna(subset=ALL_CORE).copy()
log(f"\n[핵심변수 listwise deletion] {before} -> {len(model_df)}행 "
    f"({(before-len(model_df))/before*100:.1f}% 손실)")

log(f"\n=== 핵심변수 vs Y 상관 (방향성 확인, {TAG}) ===")
sign_check = {}
for dom, vs in CORE.items():
    for v in vs:
        r = model_df[[v, Y]].corr().iloc[0, 1]
        sign_check[v] = r
        log(f"  [{dom}] {v}: r={r:+.3f}")

Xa = sm.add_constant(model_df[AREA])
model_df["도로소나무비율_resid"] = sm.OLS(model_df["도로소나무비율_500m"], Xa).fit().resid
model_df["원목업체_resid"] = sm.OLS(model_df["log1p_원목생산업체수"], Xa).fit().resid
r_road = model_df[["도로소나무비율_resid", Y]].corr().iloc[0, 1]
r_wood = model_df[["원목업체_resid", Y]].corr().iloc[0, 1]
log(f"\n[면적통제 후 재해석, {TAG}] 도로소나무비율_resid vs Y: r={r_road:+.3f} (사전 명시: +)")
log(f"[면적통제 후 재해석, {TAG}] 원목업체_resid vs Y: r={r_wood:+.3f} (사전 명시: -)")

def within_year_z(frame, col):
    return frame.groupby("연도")[col].transform(lambda s: (s - s.mean()) / s.std(ddof=0))

INDEX_INPUTS = {
    "노출도": [("소나무류_면적비율(%)", +1)],
    "기후위험도": [
        ("연강수량_mm", np.sign(sign_check["연강수량_mm"]) or 1),
        ("평균풍속_ms", np.sign(sign_check["평균풍속_ms"]) or 1),
        ("GDD_솔수염하늘소_base11.9", np.sign(sign_check["GDD_솔수염하늘소_base11.9"]) or 1),
    ],
    "지자체대응역량": [
        ("대응자원투입예산_소나무림ha당_log_재선충명시", -1),
        ("예찰사업_재선충명시_존재_flag", -1),
    ],
    "인위적확산": [
        ("도로소나무비율_resid", +1),
        ("원목업체_resid", -1),
    ],
}
for dom, items in INDEX_INPUTS.items():
    zs = [within_year_z(model_df, col) * direction for col, direction in items]
    model_df[f"{dom}_점수"] = pd.concat(zs, axis=1).mean(axis=1)

dom_cols = [f"{d}_점수" for d in CORE.keys()]
log(f"\n=== 도메인 점수 상호상관 ({TAG}) ===")
log(model_df[dom_cols].corr().round(3).to_string())

model_df["구조적취약성지수"] = model_df[dom_cols].mean(axis=1)
log("\n[가중치] 동일가중(각 0.25) 유지")

model_df["Y_bin"] = (model_df[Y] > 0).astype(int)
model_df["key"] = model_df["시도"] + model_df["시군구"]

def add_gm(frame, cols, group="key"):
    frame = frame.copy()
    for c in cols:
        frame[f"{c}_gm"] = frame.groupby(group)[c].transform("mean")
    return frame

def run_two_part(frame, index_col, label):
    frame = add_gm(frame, [index_col])
    xcols = [index_col, f"{index_col}_gm"]
    log(f"\n----- 모형A [{label}] (CRE, n={len(frame)}) -----")
    Xb = sm.add_constant(frame[xcols])
    logit = sm.GLM(frame["Y_bin"], Xb, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": frame["key"]}
    )
    pred_p = logit.predict(Xb)
    auc = roc_auc_score(frame["Y_bin"], pred_p)
    rho = stats.spearmanr(frame[index_col], frame[Y]).correlation
    log(f"  AUC={auc:.3f}  Spearman rho={rho:.3f}")
    return {"auc": auc, "rho": rho}

train = model_df[model_df["연도"].between(2017, 2020)]
holdout = model_df[model_df["연도"].between(2021, 2022)]
log(f"\n[훈련 2017-2020] 구조적취약성지수({TAG})")
res_train = run_two_part(train, "구조적취약성지수", f"훈련/{TAG}")
log(f"\n[홀드아웃 2021-2022] 구조적취약성지수({TAG})")
res_holdout = run_two_part(holdout, "구조적취약성지수", f"홀드아웃/{TAG}")

RISK_DOMAINS = ["노출도_점수", "기후위험도_점수", "인위적확산_점수"]
model_df["위험지수"] = model_df[RISK_DOMAINS].mean(axis=1)
BUDGET = "대응자원투입예산_소나무림ha당_log_재선충명시"
main = model_df[model_df["연도"].between(2017, 2022)]
gm = main.groupby(["시도", "시군구"]).agg(
    평균예산=(BUDGET, "mean"), 평균위험=("위험지수", "mean"),
    구조적취약성지수=("구조적취약성지수", "mean"),
    노출도_점수=("노출도_점수", "mean"), 인위적확산_점수=("인위적확산_점수", "mean"),
).reset_index()
X = sm.add_constant(gm["평균위험"])
m_gap = sm.OLS(gm["평균예산"], X).fit(cov_type="HC3")
gm["예측예산"] = m_gap.predict(X)
gm["배분갭"] = gm["평균예산"] - gm["예측예산"]

contrib = main.groupby(["시도", "시군구"])[dom_cols + ["구조적취약성지수"]].mean().reset_index()
for c in dom_cols:
    contrib[f"{c}_기여"] = 0.25 * contrib[c]
contrib = contrib.merge(gm[["시도", "시군구", "배분갭"]], on=["시도", "시군구"], how="left")

DIFF_THRESH = 0.5
diff = contrib["노출도_점수"] - contrib["인위적확산_점수"]
contrib["축A_위험요인유형"] = np.select(
    [diff > DIFF_THRESH, diff < -DIFF_THRESH],
    ["노출도-우세형", "인위적확산-우세형"], default="복합형"
)
contrib["축B_배분적정성"] = pd.qcut(contrib["배분갭"], 3, labels=["부족", "적정", "과다"])
log(f"\n=== 2×3 매트릭스 ({TAG}) ===")
log(pd.crosstab(contrib["축A_위험요인유형"], contrib["축B_배분적정성"]).to_string())

top20 = contrib.sort_values("구조적취약성지수", ascending=False).head(20)
log(f"\n=== 상위20 시군구 ({TAG}) ===")
log(top20[["시도", "시군구", "구조적취약성지수"]].round(3).to_string(index=False))

contrib.to_csv(f"{MODELDIR}/Model1_기여도분해_{TAG}.csv", index=False, encoding="utf-8-sig")
with open(f"{MODELDIR}/Model1_v3replica_{TAG}_로그.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))

import json
summary = {
    "tag": TAG,
    "raw_corr_도로소나무비율": float(sign_check["도로소나무비율_500m"]) if "도로소나무비율_500m" in sign_check else None,
    "resid_corr_도로소나무비율": float(r_road),
    "domain_corr_노출도_인위적확산": float(model_df[dom_cols].corr().loc["노출도_점수","인위적확산_점수"]),
    "AUC_train": float(res_train["auc"]), "rho_train": float(res_train["rho"]),
    "AUC_holdout": float(res_holdout["auc"]), "rho_holdout": float(res_holdout["rho"]),
    "n_model": len(model_df),
    "top20_list": top20["시군구"].tolist(),
}
with open(f"{MODELDIR}/summary_{TAG}.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

log(f"\n저장 완료: {TAG}")
