# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os, json, base64, csv, collections
from io import BytesIO
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
import libpysal
from esda.moran import Moran

# 한글 폰트 설정 (Windows 기본 맑은 고딕)
for cand in ["Malgun Gothic", "NanumGothic", "Gulim"]:
    if any(cand.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.abspath(__file__))  # .../EDA/CH2
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE))  # .../I-m_Pine
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "CH2", "1. 환경", "인위적 확산", "확정")
IN_FEATURES = os.path.join(DATA_DIR, "sigungu_year_panel_2016_2023_features.csv")
IN_EDA = os.path.join(DATA_DIR, "sigungu_year_panel_2016_2023_eda_features.csv")
PEST_DIR = os.path.join(PROJECT_ROOT, "data", "CH1", "산림청_산림병해충방제 병해충발생관리정보_20250902")
OUTDIR = os.path.join(BASE, "output_인위적확산")
os.makedirs(OUTDIR, exist_ok=True)

figs = {}
def save_fig(name):
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    figs[name] = base64.b64encode(buf.read()).decode()

report = {}

# ---------------------------------------------------------------
# 1단계 - 데이터 병합 (기존과 동일 - 재확인만)
# ---------------------------------------------------------------
df1 = pd.read_csv(IN_FEATURES, dtype={"sigungu_cd": str})
df2 = pd.read_csv(IN_EDA, dtype={"sigungu_cd": str})
df1["sigungu_cd"] = df1["sigungu_cd"].str.zfill(5)
df2["sigungu_cd"] = df2["sigungu_cd"].str.zfill(5)

merged = df1.merge(
    df2[["year", "sigungu_cd", "n_new_infected", "gukyurim_forestroad_density"]],
    on=["year", "sigungu_cd"], how="inner",
)
merged["log_n_new_infected"] = np.log1p(merged["n_new_infected"])
merged["has_gukyurim_forestroad"] = np.where(
    merged["gukyurim_forestroad_density"].isna(), np.nan,
    (merged["gukyurim_forestroad_density"] > 0).astype(float),
)

report["df1_shape"] = list(df1.shape)
report["df2_shape"] = list(df2.shape)
report["merged_shape"] = list(merged.shape)
report["dup_keys_df1"] = int(df1.duplicated(["year", "sigungu_cd"]).sum())
report["dup_keys_df2"] = int(df2.duplicated(["year", "sigungu_cd"]).sum())
report["dup_keys_merged"] = int(merged.duplicated(["year", "sigungu_cd"]).sum())

# ---------------------------------------------------------------
# 2단계 - 기초 점검 (결측 위치 재확인 + dtypes/기술통계 + 시군구코드 안정성[신규])
# ---------------------------------------------------------------
na_counts = merged.isna().sum()
missing_df = na_counts[na_counts > 0].reset_index()
missing_df.columns = ["컬럼", "결측개수"]
missing_df["결측비율(%)"] = (missing_df["결측개수"] / len(merged) * 100).round(2)
missing_df.to_csv(f"{OUTDIR}/missing_summary.csv", index=False, encoding="utf-8-sig")

miss_rows = merged[merged["gukyurim_forestroad_density"].isna()]
miss_sgg = miss_rows[["sigungu_cd", "sido", "sigungu_nm", "pine_ha", "sgg_area_km2"]].drop_duplicates()
miss_sgg.to_csv(f"{OUTDIR}/missing_gukyurim_density_sigungu.csv", index=False, encoding="utf-8-sig")

report["gukyurim_missing_count"] = int(len(miss_rows))
report["gukyurim_missing_is_3x8"] = bool(len(miss_sgg) == 3 and len(miss_rows) == 24)
report["gukyurim_missing_sigungu"] = miss_sgg["sigungu_nm"].tolist()
report["gukyurim_missing_sido"] = miss_sgg["sido"].tolist()
report["gukyurim_missing_years"] = sorted(miss_rows["year"].unique().tolist())
report["gukyurim_missing_all_pine_ha_zero"] = bool((miss_sgg["pine_ha"] == 0).all())

# 다른 결측 컬럼(반경 비율 6개)도 정확히 같은 24행에서 발생하는지
ratio_missing_idx = set(merged[merged["road_pine_ratio_100m"].isna()].index)
gukyurim_missing_idx = set(miss_rows.index)
report["missing_all_same_rows"] = bool(ratio_missing_idx == gukyurim_missing_idx)

dtype_df = merged.dtypes.astype(str).reset_index()
dtype_df.columns = ["컬럼", "타입"]
dtype_df.to_csv(f"{OUTDIR}/dtypes.csv", index=False, encoding="utf-8-sig")

NUMERIC_COLS = [
    "pine_ha", "road_pine_ratio_100m", "road_pine_ratio_300m", "road_pine_ratio_500m",
    "resid_pine_ratio_100m", "resid_pine_ratio_300m", "resid_pine_ratio_500m",
    "road_density_km_per_km2", "sgg_area_km2", "n_new_infected", "gukyurim_forestroad_density",
]
desc = merged[NUMERIC_COLS].describe().T
desc["skew"] = merged[NUMERIC_COLS].skew()
desc.to_csv(f"{OUTDIR}/descriptive_stats.csv", encoding="utf-8-sig")

# [신규] 시군구 코드 안정성: 8개 연도 sigungu_cd 집합이 완전히 동일한지
n_per_year = merged.groupby("year")["sigungu_cd"].nunique()
sets_by_year = merged.groupby("year")["sigungu_cd"].apply(lambda s: frozenset(s))
code_stability_ok = bool(len(set(sets_by_year)) == 1 and (n_per_year == 250).all())
report["sigungu_code_stable_all_years"] = code_stability_ok
report["sigungu_count_per_year"] = n_per_year.to_dict()

# ---------------------------------------------------------------
# 3단계 - 패널 구조 진단 (분산 분해) [신규]
# ---------------------------------------------------------------
PANEL_VARS = NUMERIC_COLS + ["log_n_new_infected"]
vd_rows = []
for c in PANEL_VARS:
    nun = merged.groupby("sigungu_cd")[c].nunique(dropna=False)
    time_invariant = bool((nun <= 1).all())
    overall_var = merged[c].var()
    between_var = merged.groupby("sigungu_cd")[c].mean().var()
    sgg_mean = merged.groupby("sigungu_cd")[c].transform("mean")
    within_var = (merged[c] - sgg_mean + merged[c].mean()).var()
    vd_rows.append({
        "변수": c, "시간불변": time_invariant, "평균고유값수": round(float(nun.mean()), 2),
        "전체분산": overall_var, "between분산": between_var, "within분산": within_var,
        "between비중(%)": round(float(between_var / overall_var * 100), 1) if overall_var else np.nan,
    })
variance_decomp = pd.DataFrame(vd_rows)
variance_decomp.to_csv(f"{OUTDIR}/variance_decomposition.csv", index=False, encoding="utf-8-sig")
report["time_invariant_vars"] = variance_decomp.loc[variance_decomp["시간불변"], "변수"].tolist()
report["time_varying_vars"] = variance_decomp.loc[~variance_decomp["시간불변"], "변수"].tolist()

plt.figure(figsize=(9, 6))
vd_sorted = variance_decomp[variance_decomp["변수"] != "log_n_new_infected"].sort_values("between비중(%)")
colors = ["#9c5a1e" if inv else "#2f5d3a" for inv in vd_sorted["시간불변"]]
plt.barh(vd_sorted["변수"], vd_sorted["between비중(%)"], color=colors)
plt.axvline(100, color="gray", linestyle="--", linewidth=1)
plt.title("변수별 between(시군구간) 분산 비중 — 주황=시간불변, 초록=시간변동")
plt.xlabel("between 분산 비중 (%)")
plt.tight_layout()
save_fig("variance_decomposition_bar")

# ---------------------------------------------------------------
# 4단계 - 반경(100/300/500m) 변수 선택 (기존과 동일)
# ---------------------------------------------------------------
ratio_cols = [
    "road_pine_ratio_100m", "road_pine_ratio_300m", "road_pine_ratio_500m",
    "resid_pine_ratio_100m", "resid_pine_ratio_300m", "resid_pine_ratio_500m",
]
rows = []
for c in ratio_cols:
    sub = merged[[c, "n_new_infected", "log_n_new_infected"]].dropna()
    pear_raw = stats.pearsonr(sub[c], sub["n_new_infected"])[0]
    pear_log = stats.pearsonr(sub[c], sub["log_n_new_infected"])[0]
    spear_raw = stats.spearmanr(sub[c], sub["n_new_infected"])[0]
    spear_log = stats.spearmanr(sub[c], sub["log_n_new_infected"])[0]
    rows.append([c, pear_raw, pear_log, spear_raw, spear_log])
radius_corr = pd.DataFrame(rows, columns=["변수", "pearson_raw", "pearson_log", "spearman_raw", "spearman_log"])
radius_corr.to_csv(f"{OUTDIR}/radius_target_correlation.csv", index=False, encoding="utf-8-sig")

road_inter = merged[["road_pine_ratio_100m", "road_pine_ratio_300m", "road_pine_ratio_500m"]].corr()
resid_inter = merged[["resid_pine_ratio_100m", "resid_pine_ratio_300m", "resid_pine_ratio_500m"]].corr()
road_inter.to_csv(f"{OUTDIR}/radius_intercorr_road.csv", encoding="utf-8-sig")
resid_inter.to_csv(f"{OUTDIR}/radius_intercorr_resid.csv", encoding="utf-8-sig")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
road_vals = radius_corr[radius_corr["변수"].str.startswith("road")].set_index("변수")["pearson_log"]
resid_vals = radius_corr[radius_corr["변수"].str.startswith("resid")].set_index("변수")["pearson_log"]
colors_road = ["#c0392b" if abs(v) == abs(road_vals).max() else "#2f5d3a" for v in road_vals]
colors_resid = ["#c0392b" if abs(v) == abs(resid_vals).max() else "#2f5d3a" for v in resid_vals]
axes[0].bar(["100m", "300m", "500m"], road_vals.values, color=colors_road)
axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_title("road_pine_ratio: 반경별 log1p(n_new_infected) 상관")
axes[0].set_ylabel("Pearson r")
axes[1].bar(["100m", "300m", "500m"], resid_vals.values, color=colors_resid)
axes[1].axhline(0, color="gray", linewidth=0.8)
axes[1].set_title("resid_pine_ratio: 반경별 log1p(n_new_infected) 상관")
plt.tight_layout()
save_fig("radius_selection_bar")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
for ax, corr_m, title in [(axes[0], road_inter, "road_pine_ratio 반경간 상관"), (axes[1], resid_inter, "resid_pine_ratio 반경간 상관")]:
    im = ax.imshow(corr_m.values, cmap="RdBu_r", vmin=0, vmax=1)
    ax.set_xticks(range(3)); ax.set_xticklabels(["100m", "300m", "500m"])
    ax.set_yticks(range(3)); ax.set_yticklabels(["100m", "300m", "500m"])
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{corr_m.values[i,j]:.2f}", ha="center", va="center", fontsize=9,
                     color="white" if corr_m.values[i, j] > 0.85 else "black")
    ax.set_title(title)
fig.colorbar(im, ax=axes, fraction=0.03, pad=0.03)
save_fig("radius_intercorr_heatmap")

SELECTED_ROAD = "road_pine_ratio_500m"
SELECTED_RESID = "resid_pine_ratio_300m"
report["radius_selected"] = {"road": SELECTED_ROAD, "resid": SELECTED_RESID}
report["radius_corr_table"] = radius_corr.round(4).to_dict("records")
# road_pine_ratio가 연도별로 실제 변하는 이유(코드 근거): build_road_pine_ratio.py는 2016~2023
# 개별 연도 도로망 스냅샷을 사용(YEAR_CONFIG에 8개 연도 모두 존재). 반면 resid_pine_ratio는
# build_final_panel_features.py 주석에 "연도 무관, 전 연도 복제"로 명시 - 단일 토지피복 스냅샷을 복제.
report["road_time_varying_reason"] = "build_road_pine_ratio.py YEAR_CONFIG에 2016~2023 개별 도로망 스냅샷 존재"
report["resid_time_invariant_reason"] = "build_final_panel_features.py: 생활권 인접 비율은 연도 무관, 전 연도 복제로 명시"

# ---------------------------------------------------------------
# 5단계 - 개별 변수 최종 포함/처리 방식 결정 [신규]
# ---------------------------------------------------------------
# (a) gukyurim_forestroad_density: 연속형 vs 이진 더미
sub_g = merged.dropna(subset=["has_gukyurim_forestroad"])
r_cont, p_cont = stats.pearsonr(sub_g["gukyurim_forestroad_density"], sub_g["log_n_new_infected"])
r_bin, p_bin = stats.pointbiserialr(sub_g["has_gukyurim_forestroad"], sub_g["log_n_new_infected"])
group_stats = sub_g.groupby("has_gukyurim_forestroad")["n_new_infected"].agg(["mean", "median", "count"])
report["gukyurim_continuous_r"] = round(float(r_cont), 4)
report["gukyurim_continuous_p"] = float(p_cont)
report["gukyurim_binary_r"] = round(float(r_bin), 4)
report["gukyurim_binary_p"] = float(p_bin)
report["gukyurim_group_stats"] = group_stats.round(1).reset_index().to_dict("records")
report["gukyurim_zero_ratio"] = round(float((merged["gukyurim_forestroad_density"] == 0).mean() * 100), 1)

plt.figure(figsize=(7, 4.5))
data_by_group = [sub_g.loc[sub_g["has_gukyurim_forestroad"] == g, "log_n_new_infected"].values for g in [0.0, 1.0]]
plt.boxplot(data_by_group, tick_labels=["국유림 임도 없음(0)", "국유림 임도 있음(1)"])
plt.title(f"국유림 임도 보유 여부별 log1p(n_new_infected)\n연속형 r={r_cont:.3f}(n.s.) vs 이진더미 r={r_bin:.3f}(p<0.001)")
plt.tight_layout()
save_fig("gukyurim_binary_box")

# (b) sgg_area_km2: pine_ha와의 collinearity, VIF 비교로 최종 판단(6단계에서 수치 산출)
report["sgg_area_pine_ha_corr"] = round(float(merged[["sgg_area_km2", "pine_ha"]].corr().iloc[0, 1]), 4)

# (c) pine_ha: 노출도(2. 노출도) 데이터셋과 대조 - 시간변동 실측값 존재하나 31개 시군구만 커버
EXPOSURE_CSV = os.path.join(PROJECT_ROOT, "data", "CH2", "2. 노출도", "CH2_노출도_2016_2025.csv")
try:
    exp_df = pd.read_csv(EXPOSURE_CSV)
    n_exposure_sgg = exp_df["시군구"].nunique()
    pine_nunique_exposure = exp_df.groupby("시군구")["소나무류_면적_ha"].nunique()
    report["exposure_dataset_found"] = True
    report["exposure_n_sigungu"] = int(n_exposure_sgg)
    report["exposure_pine_ha_time_varying"] = bool((pine_nunique_exposure > 1).all())
    report["exposure_vs_panel_coverage"] = f"{n_exposure_sgg}/250"
except FileNotFoundError:
    report["exposure_dataset_found"] = False

# ---------------------------------------------------------------
# 6단계 - 최종 변수셋 확정 + VIF 종합 진단
# ---------------------------------------------------------------
# 5단계 결론 반영: gukyurim -> 이진 더미로 교체, sgg_area_km2 -> pine_ha와 collinearity로 제외
FINAL_FEATURES = [
    SELECTED_ROAD, SELECTED_RESID, "has_gukyurim_forestroad",
    "road_density_km_per_km2", "pine_ha", "n_new_infected",
]
final_df = merged[["year", "sigungu_cd", "sido", "sigungu_nm", "log_n_new_infected"] + FINAL_FEATURES].copy()
final_df.to_csv(f"{OUTDIR}/final_variable_set.csv", index=False, encoding="utf-8-sig")
report["final_features"] = FINAL_FEATURES

def vif_table(df, cols):
    X = df[cols].dropna()
    X = (X - X.mean()) / X.std()
    X.insert(0, "const", 1.0)
    out = []
    for i, c in enumerate(X.columns):
        if c == "const":
            continue
        v = variance_inflation_factor(X.values, i)
        out.append({"변수": c, "VIF": round(float(v), 2)})
    return pd.DataFrame(out).sort_values("VIF", ascending=False)

vif_with_area = vif_table(merged, [SELECTED_ROAD, SELECTED_RESID, "has_gukyurim_forestroad", "road_density_km_per_km2", "pine_ha", "sgg_area_km2"])
vif_without_area = vif_table(merged, [SELECTED_ROAD, SELECTED_RESID, "has_gukyurim_forestroad", "road_density_km_per_km2", "pine_ha"])
vif_with_area.to_csv(f"{OUTDIR}/vif_with_sgg_area.csv", index=False, encoding="utf-8-sig")
vif_without_area.to_csv(f"{OUTDIR}/vif_final.csv", index=False, encoding="utf-8-sig")
report["vif_with_area"] = vif_with_area.to_dict("records")
report["vif_final"] = vif_without_area.to_dict("records")

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, vt, title in [(axes[0], vif_with_area, "sgg_area_km2 포함"), (axes[1], vif_without_area, "sgg_area_km2 제외(최종)")]:
    vs = vt.sort_values("VIF")
    colors = ["#c0392b" if v >= 10 else ("#9c5a1e" if v >= 5 else "#2f5d3a") for v in vs["VIF"]]
    ax.barh(vs["변수"], vs["VIF"], color=colors)
    ax.axvline(5, color="gray", linestyle="--", linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("VIF")
plt.tight_layout()
save_fig("vif_comparison")

# ---------------------------------------------------------------
# 7단계 - 단변량 분포 탐색 (+이상치 점검[신규])
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
axes[0].hist(merged["n_new_infected"], bins=40, color="#2f5d3a", edgecolor="white")
axes[0].set_title("n_new_infected (원본)")
axes[1].hist(merged["log_n_new_infected"], bins=40, color="#2f5d3a", edgecolor="white")
axes[1].set_title("log1p(n_new_infected)")
plt.tight_layout()
save_fig("hist_n_new_infected")

report["n_new_infected_zero_ratio"] = round(float((merged["n_new_infected"] == 0).mean() * 100), 1)

plt.figure(figsize=(10, 4.5))
years_sorted = sorted(merged["year"].unique())
data_by_year = [merged.loc[merged["year"] == y, "n_new_infected"].values for y in years_sorted]
plt.boxplot(data_by_year, tick_labels=years_sorted)
plt.yscale("symlog")
plt.title("연도별 n_new_infected 분포 (y축: symlog)")
plt.ylabel("n_new_infected (symlog)")
save_fig("box_year_n_new_infected")

fig, axes = plt.subplots(1, 3, figsize=(14, 4.3))
for ax, col in zip(axes, ["gukyurim_forestroad_density", SELECTED_ROAD, SELECTED_RESID]):
    vals = merged[col].dropna()
    ax.hist(vals, bins=30, color="#2f5d3a", edgecolor="white")
    zero_ratio = (vals == 0).mean() * 100
    ax.set_title(f"{col}\n(0값 비중 {zero_ratio:.1f}%)")
plt.tight_layout()
save_fig("hist_final_vars")

report["zero_ratio"] = {
    "gukyurim_forestroad_density": round(float((merged["gukyurim_forestroad_density"] == 0).mean() * 100), 1),
    SELECTED_ROAD: round(float((merged[SELECTED_ROAD] == 0).mean() * 100), 1),
    SELECTED_RESID: round(float((merged[SELECTED_RESID] == 0).mean() * 100), 1),
}

# [신규] 이상치 / 레버리지 포인트
top5 = merged.sort_values("n_new_infected", ascending=False).head(5)[["year", "sigungu_cd", "sido", "sigungu_nm", "n_new_infected"]]
top5.to_csv(f"{OUTDIR}/top5_outliers.csv", index=False, encoding="utf-8-sig")
report["top5_outliers"] = top5.to_dict("records")

# ---------------------------------------------------------------
# 8단계 - 이변량 관계 탐색 (+부분상관/민감도[신규])
# ---------------------------------------------------------------
corr_cols = FINAL_FEATURES + ["log_n_new_infected"]
corr_final = merged[corr_cols].corr(method="pearson")
corr_final.to_csv(f"{OUTDIR}/final_correlation_matrix.csv", encoding="utf-8-sig")

plt.figure(figsize=(8.5, 7.5))
im = plt.imshow(corr_final.values, cmap="RdBu_r", vmin=-1, vmax=1)
plt.colorbar(im, fraction=0.046, pad=0.04)
plt.xticks(range(len(corr_final.columns)), corr_final.columns, rotation=90, fontsize=8)
plt.yticks(range(len(corr_final.columns)), corr_final.columns, fontsize=8)
for i in range(len(corr_final)):
    for j in range(len(corr_final)):
        v = corr_final.values[i, j]
        plt.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                  color="white" if abs(v) > 0.6 else "black")
plt.title("최종 변수셋 상관관계 행렬 (Pearson)")
plt.tight_layout()
save_fig("final_corr_heatmap")

fig, axes = plt.subplots(2, 3, figsize=(14, 8.5))
for ax, col in zip(axes.flat, FINAL_FEATURES[:-1]):
    sub = merged[[col, "log_n_new_infected"]].dropna()
    ax.scatter(sub[col], sub["log_n_new_infected"], s=8, alpha=0.4, color="#2f5d3a")
    if sub[col].std() > 0:
        b, a = np.polyfit(sub[col], sub["log_n_new_infected"], 1)
        xs = np.linspace(sub[col].min(), sub[col].max(), 50)
        ax.plot(xs, a + b * xs, color="#c0392b", linewidth=1.5)
    r = corr_final.loc[col, "log_n_new_infected"]
    ax.set_xlabel(col); ax.set_ylabel("log1p(n_new_infected)")
    ax.set_title(f"r={r:.2f}")
plt.tight_layout()
save_fig("scatter_final_vars")

# [신규] 부분상관: pine_ha 통제
def partial_corr(df, x, y, control):
    sub = df[[x, y, control]].dropna()
    bx, ax_ = np.polyfit(sub[control], sub[x], 1)
    by, ay_ = np.polyfit(sub[control], sub[y], 1)
    rx = sub[x] - (ax_ + bx * sub[control])
    ry = sub[y] - (ay_ + by * sub[control])
    r, p = stats.pearsonr(rx, ry)
    return r, p, rx, ry

partial_results = {}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, var in zip(axes, [SELECTED_ROAD, SELECTED_RESID]):
    r_raw = corr_final.loc[var, "log_n_new_infected"]
    r_partial, p_partial, rx, ry = partial_corr(merged, var, "log_n_new_infected", "pine_ha")
    partial_results[var] = {"raw_r": round(float(r_raw), 4), "partial_r": round(float(r_partial), 4), "partial_p": float(p_partial)}
    ax.scatter(rx, ry, s=8, alpha=0.4, color="#2f5d3a")
    b, a_ = np.polyfit(rx, ry, 1)
    xs = np.linspace(rx.min(), rx.max(), 50)
    ax.plot(xs, a_ + b * xs, color="#c0392b", linewidth=1.5)
    ax.set_title(f"{var}\n원래 r={r_raw:.2f} → pine_ha 통제 후 r={r_partial:.2f}")
    ax.set_xlabel(f"{var} (pine_ha 통제 잔차)")
    ax.set_ylabel("log1p(n_new_infected) (pine_ha 통제 잔차)")
plt.tight_layout()
save_fig("partial_corr_plot")
report["partial_corr"] = partial_results

# [신규] 민감도 분석: 상위 2개 이상치 제외 후 상관 재계산
top2_idx = merged.sort_values("n_new_infected", ascending=False).head(2).index
merged_trim = merged.drop(top2_idx)
sensitivity = {}
for var in [SELECTED_ROAD, SELECTED_RESID]:
    r_full = corr_final.loc[var, "log_n_new_infected"]
    sub_trim = merged_trim[[var, "log_n_new_infected"]].dropna()
    r_trim, _ = stats.pearsonr(sub_trim[var], sub_trim["log_n_new_infected"])
    sensitivity[var] = {"r_full": round(float(r_full), 4), "r_excl_top2": round(float(r_trim), 4)}
report["sensitivity_top2_excl"] = sensitivity

# ---------------------------------------------------------------
# 9단계 - 시공간 패턴 탐색 (+결측 3개 시군구 특성[신규])
# ---------------------------------------------------------------
sido_order = merged.groupby("sido")["log_n_new_infected"].median().sort_values(ascending=False).index
plt.figure(figsize=(11, 5.5))
data_by_sido = [merged.loc[merged["sido"] == s, "log_n_new_infected"].values for s in sido_order]
plt.boxplot(data_by_sido, tick_labels=sido_order)
plt.xticks(rotation=40, ha="right")
plt.title("시도별 log1p(n_new_infected) 분포")
plt.ylabel("log1p(n_new_infected)")
plt.tight_layout()
save_fig("box_sido")

year_sum = merged.groupby("year")["n_new_infected"].sum()
plt.figure(figsize=(9, 4.3))
plt.plot(year_sum.index, year_sum.values, marker="o", color="#2f5d3a")
plt.title("연도별 확인된 감염목 발생 건수 합계 (250개 시군구)")
plt.xlabel("연도"); plt.ylabel("n_new_infected 합계")
plt.tight_layout()
save_fig("year_trend")
report["year_sum"] = year_sum.round(0).astype(int).to_dict()

merged_sorted = merged.sort_values(["sigungu_cd", "year"])
merged_sorted["diff"] = merged_sorted.groupby("sigungu_cd")["n_new_infected"].diff()
top_surge = merged_sorted.sort_values("diff", ascending=False).head(10)[["sigungu_cd", "sido", "sigungu_nm", "year", "n_new_infected", "diff"]]
top_surge.to_csv(f"{OUTDIR}/top_surge_sigungu.csv", index=False, encoding="utf-8-sig")
report["top_surge"] = top_surge.round(0).to_dict("records")

plt.figure(figsize=(9, 5.5))
labels = [f"{r.sido} {r.sigungu_nm} ({int(r.year)})" for r in top_surge.itertuples()]
plt.barh(labels[::-1], top_surge["diff"].values[::-1], color="#c0392b")
plt.title("전년 대비 신규 감염목 급증 상위 10개 시군구x연도")
plt.xlabel("전년 대비 증가 건수")
plt.tight_layout()
save_fig("top_surge_bar")

# [신규] 결측 3개 시군구(영등포구/대구 중구/인천 동구) 공통특성
area_pctile = (merged.loc[merged["year"] == 2016, "sgg_area_km2"].rank(pct=True))
miss_area_pctile = {}
ref2016 = merged[merged["year"] == 2016].set_index("sigungu_cd")
for sgg in miss_sgg["sigungu_cd"]:
    miss_area_pctile[sgg] = round(float((ref2016["sgg_area_km2"] < ref2016.loc[sgg, "sgg_area_km2"]).mean() * 100), 1)
report["missing_sgg_area_percentile"] = miss_area_pctile
report["national_sgg_area_km2_describe"] = ref2016["sgg_area_km2"].describe().round(1).to_dict()

national_median_area = ref2016["sgg_area_km2"].median()
national_median_density = ref2016["road_density_km_per_km2"].median()
miss_sgg_2016 = ref2016.loc[miss_sgg["sigungu_cd"]].reset_index()
labels3 = miss_sgg_2016["sido"] + " " + miss_sgg_2016["sigungu_nm"]
x = np.arange(3)
w = 0.35
fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax1.bar(x - w/2, miss_sgg_2016["sgg_area_km2"], width=w, color="#2f5d3a", label="면적(km²)")
ax1.axhline(national_median_area, color="#2f5d3a", linestyle="--", linewidth=1, label=f"전국 중앙값 면적({national_median_area:.0f})")
ax1.set_ylabel("면적 (km²)")
ax2 = ax1.twinx()
ax2.bar(x + w/2, miss_sgg_2016["road_density_km_per_km2"], width=w, color="#c0392b", label="도로밀도")
ax2.axhline(national_median_density, color="#c0392b", linestyle="--", linewidth=1, label=f"전국 중앙값 도로밀도({national_median_density:.1f})")
ax2.set_ylabel("도로밀도 (km/km²)")
ax1.set_xticks(x); ax1.set_xticklabels(labels3)
ax1.set_title("gukyurim_forestroad_density 결측 3개 시군구: 면적·도로밀도 vs 전국 중앙값")
fig.legend(loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, fontsize=8)
plt.tight_layout()
save_fig("missing_sgg_characteristics")

# ---------------------------------------------------------------
# 10단계 - 공간·시계열 구조 탐색 [신규]
# ---------------------------------------------------------------
# 10-1) 공간자기상관 (Moran's I): 시군구 경계 shp가 프로젝트에 없어(임상도/전국임상도 폴더에 .shx만 잔존)
#       병해충발생정보관리 원자료(좌표 있음, 2016~2023 전체)의 시군구별 평균좌표를 근사 중심점으로 사용,
#       KNN(k=6) 공간가중치로 대체. 폴리곤 인접(Queen contiguity)이 아닌 근사치임을 명시.
sum_x = collections.Counter(); sum_y = collections.Counter(); cnt = collections.Counter()
for year in range(2016, 2024):
    fname = os.path.join(PEST_DIR, f"병해충발생정보관리_{year}.csv")
    with open(fname, encoding="cp949", errors="replace") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            sgg = row[5][:5]
            if len(sgg) == 5 and sgg.isdigit():
                try:
                    x = float(row[1]); y = float(row[2])
                except ValueError:
                    continue
                sum_x[sgg] += x; sum_y[sgg] += y; cnt[sgg] += 1
centroids = {s: (sum_x[s] / cnt[s], sum_y[s] / cnt[s]) for s in cnt}

panel_sgg = set(merged["sigungu_cd"].unique())
valid_sgg = sorted(panel_sgg & set(centroids.keys()))
report["moran_n_sigungu_with_centroid"] = len(valid_sgg)
report["moran_coverage_pct"] = round(len(valid_sgg) / len(panel_sgg) * 100, 1)

coords = np.array([[centroids[s][0], centroids[s][1]] for s in valid_sgg])
w = libpysal.weights.KNN.from_array(coords, k=6)
w.transform = "r"

moran_rows = []
moran_2017_x, moran_2017_lag = None, None
for year in range(2016, 2024):
    yr = merged[merged["year"] == year].set_index("sigungu_cd").reindex(valid_sgg)
    x = np.log1p(yr["n_new_infected"].values)
    mi = Moran(x, w, permutations=999)
    moran_rows.append({"year": year, "moran_I": round(float(mi.I), 4), "p_sim": float(mi.p_sim)})
    if year == 2017:
        moran_2017_x = x
        moran_2017_lag = libpysal.weights.lag_spatial(w, x)
moran_df = pd.DataFrame(moran_rows)
moran_df.to_csv(f"{OUTDIR}/moran_by_year.csv", index=False, encoding="utf-8-sig")
report["moran_by_year"] = moran_rows

plt.figure(figsize=(8, 4.3))
plt.plot(moran_df["year"], moran_df["moran_I"], marker="o", color="#2f5d3a")
plt.axhline(0, color="gray", linewidth=0.8)
plt.title(f"연도별 Moran's I (log1p n_new_infected, KNN k=6, {len(valid_sgg)}개 시군구)")
plt.xlabel("연도"); plt.ylabel("Moran's I")
plt.tight_layout()
save_fig("moran_by_year_line")

plt.figure(figsize=(6, 6))
plt.scatter(moran_2017_x, moran_2017_lag, s=14, alpha=0.5, color="#2f5d3a")
b, a_ = np.polyfit(moran_2017_x, moran_2017_lag, 1)
xs = np.linspace(moran_2017_x.min(), moran_2017_x.max(), 50)
plt.plot(xs, a_ + b * xs, color="#c0392b", linewidth=1.5)
plt.axhline(moran_2017_lag.mean(), color="gray", linewidth=0.6)
plt.axvline(moran_2017_x.mean(), color="gray", linewidth=0.6)
plt.title(f"Moran 산점도 (2017, I={moran_df.loc[moran_df['year']==2017,'moran_I'].values[0]:.3f})")
plt.xlabel("log1p(n_new_infected)"); plt.ylabel("공간지연값(이웃 평균)")
plt.tight_layout()
save_fig("moran_scatter_2017")

# 10-2) 시계열 자기상관 (lag-1, 같은 시군구 t-1 vs t)
merged_sorted2 = merged.sort_values(["sigungu_cd", "year"])
merged_sorted2["log_n_lag1"] = merged_sorted2.groupby("sigungu_cd")["log_n_new_infected"].shift(1)
lag_sub = merged_sorted2.dropna(subset=["log_n_lag1"])
r_lag, p_lag = stats.pearsonr(lag_sub["log_n_lag1"], lag_sub["log_n_new_infected"])
rho_lag, p_rho = stats.spearmanr(lag_sub["log_n_lag1"], lag_sub["log_n_new_infected"])
report["temporal_autocorr"] = {"n_pairs": int(len(lag_sub)), "pearson_r": round(float(r_lag), 4), "pearson_p": float(p_lag), "spearman_rho": round(float(rho_lag), 4)}

plt.figure(figsize=(6, 6))
plt.scatter(lag_sub["log_n_lag1"], lag_sub["log_n_new_infected"], s=8, alpha=0.35, color="#2f5d3a")
b, a_ = np.polyfit(lag_sub["log_n_lag1"], lag_sub["log_n_new_infected"], 1)
xs = np.linspace(lag_sub["log_n_lag1"].min(), lag_sub["log_n_lag1"].max(), 50)
plt.plot(xs, a_ + b * xs, color="#c0392b", linewidth=1.5)
plt.title(f"시계열 자기상관: t-1 vs t (r={r_lag:.3f})")
plt.xlabel("log1p(n_new_infected), t-1년"); plt.ylabel("log1p(n_new_infected), t년")
plt.tight_layout()
save_fig("temporal_lag_scatter")

# ---------------------------------------------------------------
# 저장
# ---------------------------------------------------------------
with open(f"{OUTDIR}/figs_b64.json", "w") as f:
    json.dump(figs, f)
with open(f"{OUTDIR}/report_meta.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2, default=str)

print("=== merged shape ===", merged.shape)
print("=== sigungu code stable ===", code_stability_ok)
print("=== VIF final ===")
print(vif_without_area)
print("=== Moran by year ===")
print(moran_df)
print("=== temporal autocorr ===", report["temporal_autocorr"])
print("DONE. figs:", list(figs.keys()))
