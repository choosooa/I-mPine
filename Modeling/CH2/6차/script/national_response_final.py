# -*- coding: utf-8 -*-
"""
국가대응수준 보조모형(v3) - 최종보정3 데이터 + Model1 v3 구조적취약성지수 사용
설계는 기존 national_response_robustness.py와 동일.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
rng = np.random.default_rng(42)

OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
MODELDIR = f"{OUTDIR}/모델링"
PANEL = f"{OUTDIR}/CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
IDXFILE = f"{MODELDIR}/구조적취약성지수_final.csv"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

panel = pd.read_csv(PANEL)
idx = pd.read_csv(IDXFILE)

nat_units = panel.loc[panel["국가대응수준_관측포함"] == 1, ["시도", "시군구"]].drop_duplicates()
log(f"[국가대응수준 실측 시군구] {len(nat_units)}개")

full_bin = (panel["log_피해밀도_본per_ha"] > 0).astype(int)
in_nat = panel.merge(nat_units.assign(_in=1), on=["시도", "시군구"], how="left")["_in"].notna()
t, p = stats.ttest_ind(full_bin[in_nat], full_bin[~in_nat], equal_var=False)
log(f"[selection-on-outcome] 발생률: 포함집단={full_bin[in_nat].mean():.3f}, "
    f"미포함집단={full_bin[~in_nat].mean():.3f}, t={t:.2f}, p={p:.4f}")

nat_panel = panel.merge(nat_units.assign(_in=1), on=["시도", "시군구"], how="left")
nat_panel = nat_panel[nat_panel["_in"].notna()].drop(columns="_in")
nat_panel = nat_panel[nat_panel["연도"].between(2017, 2022)]

df = idx.merge(
    nat_panel[["연도", "시도", "시군구", "log_국비지원액_최종_per_ha"]],
    on=["연도", "시도", "시군구"], how="inner"
)
df = df.dropna(subset=["log_국비지원액_최종_per_ha", "구조적취약성지수"]).copy()
df["key"] = df["시도"] + df["시군구"]
log(f"[2017-2022 & 국비변수 결측 제외 후] n={len(df)}, 시군구수={df['key'].nunique()}")

def add_gm(frame, cols, group="key"):
    frame = frame.copy()
    for c in cols:
        frame[f"{c}_gm"] = frame.groupby(group)[c].transform("mean")
    return frame

df = add_gm(df, ["구조적취약성지수", "log_국비지원액_최종_per_ha"])

def fit_logit(frame, xcols):
    X = sm.add_constant(frame[xcols])
    return sm.GLM(frame["Y_bin"], X, family=sm.families.Binomial()).fit(
        cov_type="cluster", cov_kwds={"groups": frame["key"]}
    )

def fit_ols_pos(frame, xcols):
    pos = frame[frame["Y_bin"] == 1]
    X = sm.add_constant(pos[xcols])
    return sm.OLS(pos["log_피해밀도_본per_ha"], X).fit(cov_type="cluster", cov_kwds={"groups": pos["key"]})

xcols_i = ["구조적취약성지수", "구조적취약성지수_gm"]
xcols_ii = xcols_i + ["log_국비지원액_최종_per_ha", "log_국비지원액_최종_per_ha_gm"]

log("\n" + "=" * 70 + "\n모형(i): 구조적취약성지수만\n" + "=" * 70)
logit_i = fit_logit(df, xcols_i)
log(logit_i.summary2().tables[1].round(4).to_string())
ols_i = fit_ols_pos(df, xcols_i)
log(ols_i.summary2().tables[1].round(4).to_string())

log("\n" + "=" * 70 + "\n모형(ii): + 국가대응수준\n" + "=" * 70)
logit_ii = fit_logit(df, xcols_ii)
log(logit_ii.summary2().tables[1].round(4).to_string())
ols_ii = fit_ols_pos(df, xcols_ii)
log(ols_ii.summary2().tables[1].round(4).to_string())

def cluster_bootstrap_coef(frame, xcols, model_fn, coef_name, B=999):
    units = frame["key"].unique()
    boot_coefs = []
    for b in range(B):
        sampled_units = rng.choice(units, size=len(units), replace=True)
        pieces = []
        for i, u in enumerate(sampled_units):
            sub = frame[frame["key"] == u].copy()
            sub["key"] = f"{u}__{i}"
            pieces.append(sub)
        boot_df = pd.concat(pieces, ignore_index=True)
        try:
            m = model_fn(boot_df, xcols)
            boot_coefs.append(m.params.get(coef_name, np.nan))
        except Exception:
            boot_coefs.append(np.nan)
    return np.array(boot_coefs)

log("\n" + "=" * 70 + "\n군집 페어 부트스트랩 (B=999)\n" + "=" * 70)
for label, xcols, coef, point in [
    ("모형(i) 취약성지수_gm", xcols_i, "구조적취약성지수_gm", logit_i.params["구조적취약성지수_gm"]),
    ("모형(ii) 취약성지수_gm", xcols_ii, "구조적취약성지수_gm", logit_ii.params["구조적취약성지수_gm"]),
    ("모형(ii) 국가대응_gm", xcols_ii, "log_국비지원액_최종_per_ha_gm", logit_ii.params["log_국비지원액_최종_per_ha_gm"]),
]:
    boots = cluster_bootstrap_coef(df, xcols, fit_logit, coef, B=999)
    boots = boots[~np.isnan(boots)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    p_boot = 2 * min((boots > 0).mean(), (boots < 0).mean())
    log(f"  [{label}] 점추정={point:.4f}, 95% CI=[{lo:.4f}, {hi:.4f}], p={p_boot:.4f} (n={len(boots)}/999)")

with open(f"{MODELDIR}/국가대응수준_보조모형_로그_final.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\n저장 완료: 국가대응수준_보조모형_로그_final.txt")
