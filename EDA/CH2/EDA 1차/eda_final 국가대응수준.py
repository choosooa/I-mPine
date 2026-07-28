import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os, json, base64
from io import BytesIO
from statsmodels.stats.outliers_influence import variance_inflation_factor

for cand in ["AppleGothic", "Apple SD Gothic Neo", "NanumGothic"]:
    if any(cand.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

BASE = "/Users/chanhaeng17/Desktop/임업통계 공모전/CH2 국가대응수준"
IN = f"{BASE}/CH2_국가대응수준_국비지원_최종(재선충직접+예찰진단).csv"
OUTDIR = f"{BASE}/output_최종"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(IN)

NUMERIC_COLS = [
    "국비지원액_원", "총사업비_원", "국비비율(%)", "매칭사업수",
    "예찰진단_국비지원액_원", "예찰진단_총사업비_원", "예찰진단_국비비율(%)", "예찰진단_매칭사업수",
    "국비지원액_최종_원", "총사업비_최종_원", "국비비율_최종(%)", "매칭사업수_최종",
    "산림면적_ha", "산림면적당_국비지원액(원per ha)", "산림면적당_국비지원액_최종(원per ha)",
]

figs = {}
def save_fig(name):
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    figs[name] = base64.b64encode(buf.read()).decode()

report = {}

# ---------------------------------------------------------------
# 1. 기본 구조
# ---------------------------------------------------------------
report["shape"] = {"rows": df.shape[0], "cols": df.shape[1]}
report["연도범위"] = [int(df["연도"].min()), int(df["연도"].max())]
report["시군구수"] = int(df["시군구"].nunique())
report["시도수"] = int(df["시도"].nunique())
dtype_df = df.dtypes.astype(str).reset_index()
dtype_df.columns = ["컬럼", "타입"]
dtype_df.to_csv(f"{OUTDIR}/dtypes.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 2. 결측값 분석
# ---------------------------------------------------------------
na_counts = df.isna().sum()
na_ratio = (df.isna().mean() * 100).round(2)
missing_df = pd.DataFrame({"결측개수": na_counts, "결측비율(%)": na_ratio})
missing_df = missing_df[missing_df["결측개수"] > 0].reset_index().rename(columns={"index": "컬럼"})
missing_df.to_csv(f"{OUTDIR}/missing_summary.csv", index=False, encoding="utf-8-sig")

no_match_a = df["매칭사업수"] == 0
no_match_c = df["예찰진단_매칭사업수"] == 0
no_match_final = df["매칭사업수_최종"] == 0
report["no_match_a_ratio"] = round(float(no_match_a.mean() * 100), 1)
report["no_match_c_ratio"] = round(float(no_match_c.mean() * 100), 1)
report["no_match_final_ratio"] = round(float(no_match_final.mean() * 100), 1)

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
na_by_year_a = df.groupby("연도")["국비비율(%)"].apply(lambda s: s.isna().mean() * 100)
na_by_year_c = df.groupby("연도")["예찰진단_국비비율(%)"].apply(lambda s: s.isna().mean() * 100)
na_by_year_final = df.groupby("연도")["국비비율_최종(%)"].apply(lambda s: s.isna().mean() * 100)
axes[0].bar(na_by_year_a.index.astype(str), na_by_year_a.values, color="#9c5a1e")
axes[0].set_title("A(재선충직접) 결측 비율")
axes[1].bar(na_by_year_c.index.astype(str), na_by_year_c.values, color="#1b6ec2")
axes[1].set_title("C(예찰진단) 결측 비율")
axes[2].bar(na_by_year_final.index.astype(str), na_by_year_final.values, color="#2f5d3a")
axes[2].set_title("최종(A+C) 결측 비율")
for ax in axes:
    ax.set_xlabel("연도"); ax.set_ylabel("결측 비율 (%)")
plt.tight_layout()
save_fig("missing_by_year")

zero_by_sgg_final = df.groupby("시군구")["매칭사업수_최종"].apply(lambda s: (s == 0).sum()).sort_values(ascending=False)
zero_by_sgg_final = zero_by_sgg_final[zero_by_sgg_final > 0]
report["always_zero_final"] = zero_by_sgg_final[zero_by_sgg_final == 8].index.tolist()

plt.figure(figsize=(8, 6))
plt.barh(zero_by_sgg_final.index[::-1], zero_by_sgg_final.values[::-1], color="#2f5d3a")
plt.title("시군구별 최종(A+C) 매칭 0건 연도 수 (8개년 중)")
plt.xlabel("0건 연도 수")
save_fig("zero_by_sgg_final")

# ---------------------------------------------------------------
# 3. 기술통계
# ---------------------------------------------------------------
desc = df[NUMERIC_COLS].describe().T
desc["skew"] = df[NUMERIC_COLS].skew()
desc.to_csv(f"{OUTDIR}/descriptive_stats.csv", encoding="utf-8-sig")

# ---------------------------------------------------------------
# 4. 연도별 추이
# ---------------------------------------------------------------
year_summary = df.groupby("연도").apply(lambda g: pd.Series({
    "A_국비합계_원": g["국비지원액_원"].sum(),
    "C_국비합계_원": g["예찰진단_국비지원액_원"].sum(),
    "최종_국비합계_원": g["국비지원액_최종_원"].sum(),
    "최종_총사업비합계_원": g["총사업비_최종_원"].sum(),
    "최종_매칭사업수합계": g["매칭사업수_최종"].sum(),
}), include_groups=False)
year_summary["최종_국비비율_가중평균(%)"] = (year_summary["최종_국비합계_원"] / year_summary["최종_총사업비합계_원"] * 100).round(1)
year_summary.to_csv(f"{OUTDIR}/year_summary.csv", encoding="utf-8-sig")

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
axes[0].plot(year_summary.index, year_summary["A_국비합계_원"] / 1e8, marker="o", color="#9c5a1e", label="A(재선충직접)")
axes[0].plot(year_summary.index, year_summary["C_국비합계_원"] / 1e8, marker="o", color="#1b6ec2", label="C(예찰진단)")
axes[0].plot(year_summary.index, year_summary["최종_국비합계_원"] / 1e8, marker="o", color="#2f5d3a", label="최종(A+C)")
axes[0].legend(); axes[0].set_title("연도별 국비지원액 합계 (억원)")
axes[0].set_xlabel("연도"); axes[0].set_ylabel("억원")
axes[1].bar(year_summary.index.astype(str), year_summary["최종_매칭사업수합계"], color="#2f5d3a")
axes[1].set_title("연도별 최종 매칭사업수 합계")
axes[1].set_xlabel("연도"); axes[1].set_ylabel("건수")
plt.tight_layout()
save_fig("year_total_final")

sido_year = df.groupby(["연도", "시도"])["국비지원액_최종_원"].sum().unstack() / 1e8
plt.figure(figsize=(10, 5))
for col in sido_year.columns:
    plt.plot(sido_year.index, sido_year[col], marker="o", label=col, markersize=3)
plt.legend(fontsize=8, ncol=2)
plt.title("시도별 국비지원액_최종 합계 연도 추이 (억원)")
plt.xlabel("연도"); plt.ylabel("국비지원액_최종 합계 (억원)")
save_fig("sido_year_trend")

# ---------------------------------------------------------------
# 5. 분포
# ---------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
axes[0, 0].hist(df["국비지원액_최종_원"] / 1e8, bins=25, color="#2f5d3a", edgecolor="white")
axes[0, 0].set_title("국비지원액_최종 (억원)")
axes[0, 1].hist(df["국비비율_최종(%)"].dropna(), bins=25, color="#2f5d3a", edgecolor="white")
axes[0, 1].set_title("국비비율_최종(%) (매칭 있는 경우만)")
axes[1, 0].hist(df["산림면적당_국비지원액_최종(원per ha)"], bins=25, color="#2f5d3a", edgecolor="white")
axes[1, 0].set_title("산림면적당_국비지원액_최종(원/ha)")
axes[1, 1].hist(df["매칭사업수_최종"], bins=25, color="#2f5d3a", edgecolor="white")
axes[1, 1].set_title("매칭사업수_최종")
plt.tight_layout()
save_fig("distributions")

# ---------------------------------------------------------------
# 6. 시군구별 편중
# ---------------------------------------------------------------
top_sgg = df.groupby(["시도", "시군구"])["국비지원액_최종_원"].sum().sort_values(ascending=False).head(15) / 1e8
plt.figure(figsize=(8, 6))
labels = [f"{a} {b}" for a, b in top_sgg.index]
plt.barh(labels[::-1], top_sgg.values[::-1], color="#2e7d32")
plt.title("2016~2023 누적 국비지원액_최종 상위 15개 시군구 (억원)")
plt.xlabel("누적 국비지원액_최종 (억원)")
save_fig("top_sgg_final")

# ---------------------------------------------------------------
# 7. 상관관계 & VIF (항등식 성분 제외한 분석용 변수셋)
# ---------------------------------------------------------------
corr_cols = ["국비지원액_최종_원", "산림면적_ha", "매칭사업수_최종",
             "산림면적당_국비지원액_최종(원per ha)", "국비비율_최종(%)"]
corr = df[corr_cols].corr(method="pearson")
corr.to_csv(f"{OUTDIR}/correlation_matrix.csv", encoding="utf-8-sig")

plt.figure(figsize=(7, 6))
im = plt.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
plt.colorbar(im, fraction=0.046, pad=0.04)
plt.xticks(range(len(corr.columns)), corr.columns, rotation=90, fontsize=8)
plt.yticks(range(len(corr.columns)), corr.columns, fontsize=8)
for i in range(len(corr)):
    for j in range(len(corr)):
        v = corr.values[i, j]
        if abs(v) >= 0.3:
            plt.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                      color="white" if abs(v) > 0.7 else "black")
plt.title("최종 데이터 변수 상관관계 행렬 (Pearson)")
plt.tight_layout()
save_fig("corr_heatmap")

pairs = []
cols = corr.columns.tolist()
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        r = corr.iloc[i, j]
        if abs(r) >= 0.4:
            pairs.append({"변수1": cols[i], "변수2": cols[j], "상관계수": round(float(r), 3)})
high_corr_df = pd.DataFrame(pairs).sort_values("상관계수", key=lambda s: s.abs(), ascending=False) if pairs else pd.DataFrame(columns=["변수1","변수2","상관계수"])
high_corr_df.to_csv(f"{OUTDIR}/high_correlation_pairs.csv", index=False, encoding="utf-8-sig")

vif_cols = ["국비지원액_최종_원", "산림면적_ha", "매칭사업수_최종"]
X = df[vif_cols].dropna()
X = (X - X.mean()) / X.std()
X.insert(0, "const", 1.0)
vif_data = []
for i, col in enumerate(X.columns):
    if col == "const":
        continue
    v = variance_inflation_factor(X.values, i)
    vif_data.append({"변수": col, "VIF": round(float(v), 2)})
vif_df = pd.DataFrame(vif_data).sort_values("VIF", ascending=False)
vif_df.to_csv(f"{OUTDIR}/vif.csv", index=False, encoding="utf-8-sig")

plt.figure(figsize=(8, 3.5))
vif_sorted = vif_df.sort_values("VIF")
colors = ["#c0392b" if v >= 10 else ("#9c5a1e" if v >= 5 else "#2f5d3a") for v in vif_sorted["VIF"]]
plt.barh(vif_sorted["변수"], vif_sorted["VIF"], color=colors)
plt.axvline(5, color="gray", linestyle="--", linewidth=1)
plt.axvline(10, color="black", linestyle="--", linewidth=1)
plt.title("변수별 VIF (최종 데이터 분석용 변수셋)")
plt.xlabel("VIF (점선: 5, 10 기준선)")
save_fig("vif_chart")

# ---------------------------------------------------------------
# 저장
# ---------------------------------------------------------------
with open(f"{OUTDIR}/figs_b64.json", "w") as f:
    json.dump(figs, f)
with open(f"{OUTDIR}/report_meta.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("=== 결측값 요약 ===")
print(missing_df)
print()
print("=== 연도별 요약 ===")
print(year_summary)
print()
print("=== 상관계수 |r|>=0.4 쌍 ===")
print(high_corr_df.to_string(index=False) if len(high_corr_df) else "(없음)")
print()
print("=== VIF ===")
print(vif_df.to_string(index=False))
print()
print("DONE. figs:", list(figs.keys()))
