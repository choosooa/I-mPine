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

BASE = "/Users/chanhaeng17/Desktop/I-mPine/EDA/CH2"
IN = f"{BASE}/../../CH2 data/CH2_노출도_전국_2016_2025.csv"
OUTDIR = f"{BASE}/output_노출도_전국"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(IN)

NUMERIC_COLS = [
    "피해본수_당해연도", "전년도_피해본수", "행정구역면적_ha", "피해밀도_본per ha",
    "최근3년_피해증가율(%)", "연속발생연수", "인접시군_피해밀도_본per ha",
    "소나무류_면적_ha", "산림면적_ha", "소나무류_면적비율(%)",
    "최근감염목과의_거리_km", "집단발생여부",
]
CATEGORICAL_COLS = ["시도", "시군구", "인접시군_산정방식", "소나무류_결측", "데이터유형"]

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

na_by_year = df.groupby("연도")["최근3년_피해증가율(%)"].apply(lambda s: s.isna().mean() * 100)
plt.figure(figsize=(9, 4))
plt.bar(na_by_year.index.astype(str), na_by_year.values, color="#9c5a1e")
plt.title("연도별 '최근3년_피해증가율(%)' 결측 비율 (전국 229개 시군구)")
plt.ylabel("결측 비율 (%)")
plt.xlabel("연도")
save_fig("missing_by_year")

report["missing_only_col"] = "최근3년_피해증가율(%)"
report["missing_count"] = int(na_counts["최근3년_피해증가율(%)"])
report["missing_ratio"] = round(float(df["최근3년_피해증가율(%)"].isna().mean() * 100), 1)

# ---------------------------------------------------------------
# 3. 기술통계
# ---------------------------------------------------------------
desc = df[NUMERIC_COLS].describe().T
desc["skew"] = df[NUMERIC_COLS].skew()
desc.to_csv(f"{OUTDIR}/descriptive_stats.csv", encoding="utf-8-sig")

# ---------------------------------------------------------------
# 4. 데이터유형(실측 vs 추정) 분포 - 전국판에서 새로 중요해진 축
# ---------------------------------------------------------------
dtype_year = pd.crosstab(df["연도"], df["데이터유형"])
dtype_year.to_csv(f"{OUTDIR}/datatype_by_year.csv", encoding="utf-8-sig")
plt.figure(figsize=(9, 4.5))
dtype_year.plot(kind="bar", stacked=True, ax=plt.gca(), color=["#2f5d3a", "#c98a3c"])
plt.title("연도별 실측/추정 데이터유형 구성 (전국 229개 시군구)")
plt.ylabel("시군구 수"); plt.xlabel("연도"); plt.xticks(rotation=0)
plt.legend(title=None, fontsize=9)
save_fig("datatype_by_year")

nb_method = pd.crosstab(df["연도"], df["인접시군_산정방식"])
plt.figure(figsize=(9, 4))
nb_method.plot(kind="bar", stacked=True, ax=plt.gca(), color=["#4a7fb5", "#9c5a1e"])
plt.title("연도별 인접시군 산정방식 구성 (SGIS 실제인접 vs centroid 대체)")
plt.ylabel("시군구 수"); plt.xlabel("연도"); plt.xticks(rotation=0)
plt.legend(fontsize=9)
save_fig("nb_method_by_year")

pine_missing_sido = df[df["소나무류_결측"]].groupby("시도")["시군구"].nunique().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
plt.barh(pine_missing_sido.index[::-1], pine_missing_sido.values[::-1], color="#c0392b")
plt.title("소나무류 면적 결측(0 처리) 시군구 수 - 시도별")
plt.xlabel("시군구 개수")
save_fig("pine_missing_sido")

# ---------------------------------------------------------------
# 5. 범주형 변수 분포
# ---------------------------------------------------------------
sido_count = df.groupby("시도")["시군구"].nunique().sort_values(ascending=False)
plt.figure(figsize=(8, 7))
plt.barh(sido_count.index[::-1], sido_count.values[::-1], color="#2f5d3a")
plt.title("시도별 대상 시군구 개수 (전국)")
plt.xlabel("시군구 개수")
save_fig("sido_count")

# ---------------------------------------------------------------
# 6. 연도별 추이
# ---------------------------------------------------------------
year_sum = df.groupby("연도")["피해본수_당해연도"].sum()
plt.figure(figsize=(9, 4.5))
colors = ["#c98a3c" if t != "실측(원자료 기반)" else "#2f5d3a"
          for t in df.groupby("연도")["데이터유형"].first()]
plt.bar(year_sum.index.astype(str), year_sum.values, color=colors)
plt.title("연도별 전국 피해본수 합계 (녹색=실측, 갈색=추정)")
plt.xlabel("연도"); plt.ylabel("피해본수 합계")
save_fig("year_total")

sido_year = df.groupby(["연도", "시도"])["피해본수_당해연도"].sum().unstack()
plt.figure(figsize=(11, 5.5))
for col in sido_year.columns:
    plt.plot(sido_year.index, sido_year[col], marker="o", label=col, markersize=3)
plt.legend(fontsize=7, ncol=3)
plt.title("시도별 피해본수 합계 연도 추이 (전국)")
plt.xlabel("연도"); plt.ylabel("피해본수 합계")
save_fig("sido_year_trend")

cluster_ratio = df.groupby("연도")["집단발생여부"].mean() * 100
plt.figure(figsize=(9, 4))
plt.bar(cluster_ratio.index.astype(str), cluster_ratio.values, color="#9c5a1e")
plt.title("연도별 집단발생 시군구 비율 (전국 229개 중)")
plt.xlabel("연도"); plt.ylabel("집단발생 비율 (%)")
save_fig("cluster_ratio")

# ---------------------------------------------------------------
# 7. 분포 (히스토그램)
# ---------------------------------------------------------------
dist_cols = ["피해본수_당해연도", "피해밀도_본per ha", "소나무류_면적비율(%)", "최근감염목과의_거리_km"]
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for ax, c in zip(axes.flat, dist_cols):
    ax.hist(df[c].dropna(), bins=30, color="#2f5d3a", edgecolor="white")
    ax.set_title(c)
plt.tight_layout()
save_fig("distributions")

# ---------------------------------------------------------------
# 8. 시군구별 누적 피해본수 TOP 20
# ---------------------------------------------------------------
top_sgg = df.groupby(["시도", "시군구"])["피해본수_당해연도"].sum().sort_values(ascending=False).head(20)
plt.figure(figsize=(8, 8))
labels = [f"{a} {b}" for a, b in top_sgg.index]
plt.barh(labels[::-1], top_sgg.values[::-1], color="#2e7d32")
plt.title("2016~2025 누적 피해본수 상위 20개 시군구 (전국)")
plt.xlabel("누적 피해본수")
save_fig("top_sgg")

# ---------------------------------------------------------------
# 9. 이상치 확인: 시도별 피해밀도 boxplot
# ---------------------------------------------------------------
plt.figure(figsize=(12, 5.5))
sido_order = df.groupby("시도")["피해밀도_본per ha"].median().sort_values(ascending=False).index
data_by_sido = [df.loc[df["시도"] == s, "피해밀도_본per ha"].values for s in sido_order]
plt.boxplot(data_by_sido, labels=sido_order)
plt.xticks(rotation=35, ha="right", fontsize=8)
plt.title("시도별 피해밀도(본/ha) 분포 (전국, 이상치 확인)")
plt.ylabel("피해밀도 (본/ha)")
save_fig("box_density")

# ---------------------------------------------------------------
# 10. 상관관계 분석 (다중공선성 탐색용)
# ---------------------------------------------------------------
corr = df[NUMERIC_COLS].corr(method="pearson")
corr.to_csv(f"{OUTDIR}/correlation_matrix.csv", encoding="utf-8-sig")

plt.figure(figsize=(10, 8))
im = plt.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
plt.colorbar(im, fraction=0.046, pad=0.04)
plt.xticks(range(len(corr.columns)), corr.columns, rotation=90, fontsize=8)
plt.yticks(range(len(corr.columns)), corr.columns, fontsize=8)
for i in range(len(corr)):
    for j in range(len(corr)):
        v = corr.values[i, j]
        if abs(v) >= 0.4:
            plt.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6,
                      color="white" if abs(v) > 0.7 else "black")
plt.title("수치형 변수 상관관계 행렬 (Pearson, 전국)")
plt.tight_layout()
save_fig("corr_heatmap")

pairs = []
cols = corr.columns.tolist()
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        r = corr.iloc[i, j]
        if abs(r) >= 0.7:
            pairs.append({"변수1": cols[i], "변수2": cols[j], "상관계수": round(float(r), 3)})
high_corr_df = pd.DataFrame(pairs).sort_values("상관계수", key=lambda s: s.abs(), ascending=False) if pairs else pd.DataFrame(columns=["변수1", "변수2", "상관계수"])
high_corr_df.to_csv(f"{OUTDIR}/high_correlation_pairs.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 11. VIF (분산팽창지수)
# ---------------------------------------------------------------
vif_cols = [c for c in NUMERIC_COLS if c != "최근3년_피해증가율(%)"]
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

plt.figure(figsize=(8, 6))
vif_sorted = vif_df.sort_values("VIF")
colors = ["#c0392b" if v >= 10 else ("#9c5a1e" if v >= 5 else "#2f5d3a") for v in vif_sorted["VIF"]]
plt.barh(vif_sorted["변수"], vif_sorted["VIF"], color=colors)
plt.axvline(5, color="gray", linestyle="--", linewidth=1)
plt.axvline(10, color="black", linestyle="--", linewidth=1)
plt.title("변수별 VIF (분산팽창지수, 전국)")
plt.xlabel("VIF (점선: 5, 10 기준선)")
save_fig("vif_chart")

# ---------------------------------------------------------------
# 12. 핵심 산점도
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
axes[0].scatter(df["소나무류_면적_ha"], df["산림면적_ha"], s=6, alpha=0.4, color="#2f5d3a")
axes[0].set_xlabel("소나무류_면적_ha"); axes[0].set_ylabel("산림면적_ha")
axes[0].set_title(f"r={corr.loc['소나무류_면적_ha','산림면적_ha']:.2f}")

axes[1].scatter(df["피해본수_당해연도"], df["전년도_피해본수"], s=6, alpha=0.4, color="#2f5d3a")
axes[1].set_xlabel("피해본수_당해연도"); axes[1].set_ylabel("전년도_피해본수")
axes[1].set_title(f"r={corr.loc['피해본수_당해연도','전년도_피해본수']:.2f}")

axes[2].scatter(df["피해밀도_본per ha"], df["인접시군_피해밀도_본per ha"], s=6, alpha=0.4, color="#2f5d3a")
axes[2].set_xlabel("피해밀도_본per ha"); axes[2].set_ylabel("인접시군_피해밀도_본per ha")
axes[2].set_title(f"r={corr.loc['피해밀도_본per ha','인접시군_피해밀도_본per ha']:.2f}")
plt.tight_layout()
save_fig("scatter_key_pairs")

# ---------------------------------------------------------------
# 저장
# ---------------------------------------------------------------
with open(f"{OUTDIR}/figs_b64.json", "w") as f:
    json.dump(figs, f)
with open(f"{OUTDIR}/report_meta.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("=== 기본 구조 ===")
print(report)
print()
print("=== 결측값 요약 ===")
print(missing_df)
print()
print("=== 데이터유형 x 연도 ===")
print(dtype_year)
print()
print("=== 상관계수 |r|>=0.7 쌍 ===")
print(high_corr_df.to_string(index=False))
print()
print("=== VIF ===")
print(vif_df.to_string(index=False))
print()
print("DONE. figs:", list(figs.keys()))
