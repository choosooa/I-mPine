# -*- coding: utf-8 -*-
"""
Model 1 (구조적 취약성지수) v4 - 평균풍속 교란효과 확인 반영
- 입력: CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv
- 변경점(v3 대비): 평균풍속_ms를 기후위험도 도메인에서 제외.
  재검토 발견: 평균풍속의 Y와의 Spearman(between)=-0.144(v3에서 '유지' 결정 근거)는 관측소
  대도시권 공유지역(주로 서울/수도권 30여곳)을 제외하면 0.005로 완전히 사라짐. ICC 자체는
  안정적(0.939)이나 Y와의 관계는 수도권 교란효과일 가능성이 높아 최종 제외로 결정 변경.
  기후위험도 도메인 = 연강수량_mm, GDD_솔수염하늘소_base11.9 (2개, SPI3는 v3에서 이미 제외)
- 나머지 설계(동일가중, CRE 2부문모형, 배분갭, 기여도분해, 2축 유형화)는 v3와 동일.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.metrics import roc_auc_score

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

import os
OUTDIR = os.path.dirname(os.path.abspath(__file__)) + "/output_A"
MODELDIR = OUTDIR
os.makedirs(OUTDIR, exist_ok=True)
PANEL = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\CH2\3차\CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

# =========================================================
# 1. 표본 정의
# =========================================================
df = pd.read_csv(PANEL)
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
    "기후위험도": ["연강수량_mm", "GDD_솔수염하늘소_base11.9"],  # SPI3 제외(v4) + 평균풍속 제외(v4, 관측소 공유 교란확인)
    "지자체대응역량": ["대응자원투입예산_소나무림ha당_log_재선충명시", "예찰사업_재선충명시_존재_flag"],
    "인위적확산": ["도로소나무비율_500m", "log1p_원목생산업체수"],
}
AREA = "log_소나무림면적"
ALL_CORE = [v for vs in CORE.values() for v in vs] + [AREA, Y]

before = len(df)
model_df = df.dropna(subset=ALL_CORE).copy()
log(f"\n[핵심변수 listwise deletion] {before} -> {len(model_df)}행 "
    f"({(before-len(model_df))/before*100:.1f}% 손실) - SPI3 제외로 n 소폭 증가 여부 확인")

# =========================================================
# 2. 방향성 확인
# =========================================================
log("\n=== 핵심변수 vs Y 상관 (방향성 확인) ===")
sign_check = {}
for dom, vs in CORE.items():
    for v in vs:
        r = model_df[[v, Y]].corr().iloc[0, 1]
        sign_check[v] = r
        log(f"  [{dom}] {v}: r={r:+.3f}")

# =========================================================
# 3. 인위적확산 잔차화
# =========================================================
Xa = sm.add_constant(model_df[AREA])
model_df["도로소나무비율_resid"] = sm.OLS(model_df["도로소나무비율_500m"], Xa).fit().resid
model_df["원목업체_resid"] = sm.OLS(model_df["log1p_원목생산업체수"], Xa).fit().resid

# =========================================================
# 4. 도메인 z-score + 동일가중 지수
# =========================================================
def within_year_z(frame, col):
    return frame.groupby("연도")[col].transform(lambda s: (s - s.mean()) / s.std(ddof=0))

INDEX_INPUTS = {
    "노출도": [("소나무류_면적비율(%)", +1)],
    "기후위험도": [
        ("연강수량_mm", np.sign(sign_check["연강수량_mm"]) or 1),
        ("GDD_솔수염하늘소_base11.9", np.sign(sign_check["GDD_솔수염하늘소_base11.9"]) or 1),
    ],
    "지자체대응역량": [
        ("대응자원투입예산_소나무림ha당_log_재선충명시", -1),
        ("예찰사업_재선충명시_존재_flag", -1),
    ],
    "인위적확산": [
        ("도로소나무비율_resid", +1),
        ("원목업체_resid", +1),  # [옵션A] 이론대로 반전: 원목업체 多 = 확산위험 高
    ],
}
for dom, items in INDEX_INPUTS.items():
    zs = [within_year_z(model_df, col) * direction for col, direction in items]
    model_df[f"{dom}_점수"] = pd.concat(zs, axis=1).mean(axis=1)

dom_cols = [f"{d}_점수" for d in CORE.keys()]
log("\n=== 도메인 점수 상호상관 (v4, SPI3 제외 후) ===")
log(model_df[dom_cols].corr().round(3).to_string())

model_df["구조적취약성지수"] = model_df[dom_cols].mean(axis=1)
log("\n[가중치] 동일가중(각 0.25) 유지")

# =========================================================
# 5. 모형 A (Model 1 검증)
# =========================================================
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
    log("[발생여부 로지스틱]")
    log(logit.summary2().tables[1].round(4).to_string())
    pred_p = logit.predict(Xb)
    auc = roc_auc_score(frame["Y_bin"], pred_p)
    rho = stats.spearmanr(frame[index_col], frame[Y]).correlation
    log(f"  AUC={auc:.3f}  Spearman rho={rho:.3f}")
    pos = frame[frame["Y_bin"] == 1]
    Xp = sm.add_constant(pos[xcols])
    ols = sm.OLS(pos[Y], Xp).fit(cov_type="cluster", cov_kwds={"groups": pos["key"]})
    log("[발생시 크기 OLS]")
    log(ols.summary2().tables[1].round(4).to_string())
    return {"auc": auc, "rho": rho}

train = model_df[model_df["연도"].between(2017, 2020)]
holdout = model_df[model_df["연도"].between(2021, 2022)]
log(f"\n{'='*70}\n[훈련 2017-2020] 구조적취약성지수(v4)\n{'='*70}")
run_two_part(train, "구조적취약성지수", "훈련")
log(f"\n{'='*70}\n[홀드아웃 2021-2022] 구조적취약성지수(v4)\n{'='*70}")
run_two_part(holdout, "구조적취약성지수", "홀드아웃")

# =========================================================
# 6. 배분갭
# =========================================================
log(f"\n{'='*70}\n배분갭(축B 입력)\n{'='*70}")
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
log(m_gap.summary2().tables[1].round(4).to_string())
log(f"  R² = {m_gap.rsquared:.4f}")
gm["예측예산"] = m_gap.predict(X)
gm["배분갭"] = gm["평균예산"] - gm["예측예산"]

# =========================================================
# 7. 기여도 분해
# =========================================================
contrib = main.groupby(["시도", "시군구"])[dom_cols + ["구조적취약성지수"]].mean().reset_index()
for c in dom_cols:
    contrib[f"{c}_기여"] = 0.25 * contrib[c]
top20 = contrib.sort_values("구조적취약성지수", ascending=False).head(20)
log(f"\n{'='*70}\n취약성지수 상위 20개 시군구 - 도메인별 기여도 (v4)\n{'='*70}")
log(top20[["시도", "시군구", "구조적취약성지수"] + [f"{c}_기여" for c in dom_cols]].round(3).to_string(index=False))

# =========================================================
# 8. 2축 유형화
# =========================================================
DIFF_THRESH = 0.5
diff = contrib["노출도_점수"] - contrib["인위적확산_점수"]
contrib["축A_위험요인유형"] = np.select(
    [diff > DIFF_THRESH, diff < -DIFF_THRESH],
    ["노출도-우세형", "인위적확산-우세형"], default="복합형"
)
contrib = contrib.merge(gm[["시도", "시군구", "배분갭"]], on=["시도", "시군구"], how="left")
contrib["축B_배분적정성"] = pd.qcut(contrib["배분갭"], 3, labels=["부족", "적정", "과다"])
log(f"\n{'='*70}\n2×3 매트릭스 (v4)\n{'='*70}")
log(pd.crosstab(contrib["축A_위험요인유형"], contrib["축B_배분적정성"]).to_string())

PRESCRIPTION = {
    ("노출도-우세형", "부족"): "예찰·모니터링 인프라 확충",
    ("인위적확산-우세형", "부족"): "도로변/원목유통 관리(이동경로 차단)",
    ("복합형", "부족"): "기본 대응체계·인력 확충",
}
contrib["정책처방"] = contrib.apply(
    lambda r: PRESCRIPTION.get((r["축A_위험요인유형"], r["축B_배분적정성"]), "-"), axis=1
)
for a_type in ["노출도-우세형", "인위적확산-우세형", "복합형"]:
    sub = contrib[(contrib["축A_위험요인유형"] == a_type) & (contrib["축B_배분적정성"] == "부족")]
    sub = sub.sort_values("구조적취약성지수", ascending=False).head(5)
    log(f"\n[{a_type} x 부족] 상위 5개")
    log(sub[["시도", "시군구", "구조적취약성지수", "배분갭"]].round(3).to_string(index=False))

# =========================================================
# 저장
# =========================================================
contrib.to_csv(f"{MODELDIR}/Model1_기여도분해_유형화_v4.csv", index=False, encoding="utf-8-sig")
main_out_cols = ["연도", "시도", "시군구", Y, "Y_bin"] + dom_cols + ["구조적취약성지수", "위험지수"]
model_df[model_df["연도"].between(2016, 2023)][main_out_cols].to_csv(
    f"{MODELDIR}/구조적취약성지수_v4.csv", index=False, encoding="utf-8-sig"
)
with open(f"{MODELDIR}/Model1_v4_로그.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\n저장 완료: Model1_기여도분해_유형화_v4.csv, 구조적취약성지수_v4.csv, Model1_v4_로그.txt")
