import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os, json, base64
from io import BytesIO
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 한글 폰트 설정 (macOS 기본 AppleGothic 시도)
for cand in ["AppleGothic", "Apple SD Gothic Neo", "NanumGothic"]:
    if any(cand.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False

BASE = "/Users/chanhaeng17/Desktop/임업통계 공모전/CH2 국가대응수준"
IN = f"{BASE}/CH2_국가대응수준_국비지원(재정365).csv"
OUTDIR = f"{BASE}/output"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(IN)

NUMERIC_COLS = [
    "국비지원액_원", "총사업비_원", "국비비율(%)", "산림면적_ha",
    "산림면적당_국비지원액(원per ha)", "매칭사업수",
    "시도비_원(참고)", "시군구비_원(참고)", "기타재원_원(참고)",
]
CATEGORICAL_COLS = ["시도", "시군구"]

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
# 2. 결측값 분석 (국비비율(%)은 매칭사업 0건 = 총사업비 0인 해에 정의상 결측)
# ---------------------------------------------------------------
na_counts = df.isna().sum()
na_ratio = (df.isna().mean() * 100).round(2)
missing_df = pd.DataFrame({"결측개수": na_counts, "결측비율(%)": na_ratio})
missing_df = missing_df[missing_df["결측개수"] > 0].reset_index().rename(columns={"index": "컬럼"})
missing_df.to_csv(f"{OUTDIR}/missing_summary.csv", index=False, encoding="utf-8-sig")

no_match = df["매칭사업수"] == 0
report["no_match_count"] = int(no_match.sum())
report["no_match_ratio"] = round(float(no_match.mean() * 100), 1)

na_by_year = df.groupby("연도")["국비비율(%)"].apply(lambda s: s.isna().mean() * 100)
plt.figure(figsize=(9, 4))
plt.bar(na_by_year.index.astype(str), na_by_year.values, color="#9c5a1e")
plt.title("연도별 '국비비율(%)' 결측 비율 (=매칭사업 0건 비율)")
plt.ylabel("결측 비율 (%)")
plt.xlabel("연도")
save_fig("missing_by_year")

# 시군구별 매칭사업 0건 연도 수 (8개년 중)
zero_by_sgg = df.groupby("시군구")["매칭사업수"].apply(lambda s: (s == 0).sum()).sort_values(ascending=False)
zero_by_sgg = zero_by_sgg[zero_by_sgg > 0]
plt.figure(figsize=(8, 6))
plt.barh(zero_by_sgg.index[::-1], zero_by_sgg.values[::-1], color="#9c5a1e")
plt.title("시군구별 매칭사업 0건 연도 수 (8개년 중)")
plt.xlabel("0건 연도 수")
save_fig("zero_by_sgg")

report["always_zero_sgg"] = zero_by_sgg[zero_by_sgg == 8].index.tolist()

# ---------------------------------------------------------------
# 3. 기술통계
# ---------------------------------------------------------------
desc = df[NUMERIC_COLS].describe().T
desc["skew"] = df[NUMERIC_COLS].skew()
desc.to_csv(f"{OUTDIR}/descriptive_stats.csv", encoding="utf-8-sig")

# ---------------------------------------------------------------
# 4. 시도별 시군구 수
# ---------------------------------------------------------------
sido_count = df.groupby("시도")["시군구"].nunique().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
plt.barh(sido_count.index[::-1], sido_count.values[::-1], color="#2f5d3a")
plt.title("시도별 대상 시군구 개수")
plt.xlabel("시군구 개수")
save_fig("sido_count")

# ---------------------------------------------------------------
# 5. 연도별 추이
# ---------------------------------------------------------------
year_sum = df.groupby("연도").apply(
    lambda g: pd.Series({
        "국비합계_원": g["국비지원액_원"].sum(),
        "총사업비합계_원": g["총사업비_원"].sum(),
        "매칭사업수합계": g["매칭사업수"].sum(),
    }),
    include_groups=False,
)
year_sum["국비비율_가중평균(%)"] = (year_sum["국비합계_원"] / year_sum["총사업비합계_원"] * 100).round(1)
year_sum.to_csv(f"{OUTDIR}/year_summary.csv", encoding="utf-8-sig")

plt.figure(figsize=(9, 4.5))
plt.plot(year_sum.index, year_sum["국비합계_원"] / 1e8, marker="o", color="#2f5d3a")
plt.title("연도별 국비지원액 합계 (31개 시군구, 억원)")
plt.xlabel("연도"); plt.ylabel("국비지원액 합계 (억원)")
save_fig("year_total_gukbi")

sido_year = df.groupby(["연도", "시도"])["국비지원액_원"].sum().unstack() / 1e8
plt.figure(figsize=(10, 5))
for col in sido_year.columns:
    plt.plot(sido_year.index, sido_year[col], marker="o", label=col, markersize=3)
plt.legend(fontsize=8, ncol=2)
plt.title("시도별 국비지원액 합계 연도 추이 (억원)")
plt.xlabel("연도"); plt.ylabel("국비지원액 합계 (억원)")
save_fig("sido_year_trend")

match_ratio = df.groupby("연도")["매칭사업수"].apply(lambda s: (s > 0).mean() * 100)
plt.figure(figsize=(9, 4))
plt.bar(match_ratio.index.astype(str), match_ratio.values, color="#2f5d3a")
plt.title("연도별 재선충 사업 매칭 시군구 비율")
plt.xlabel("연도"); plt.ylabel("매칭 비율 (%)")
save_fig("match_ratio_by_year")

# ---------------------------------------------------------------
# 6. 분포 (히스토그램)
# ---------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
axes[0, 0].hist(df["국비지원액_원"] / 1e8, bins=25, color="#2f5d3a", edgecolor="white")
axes[0, 0].set_title("국비지원액 (억원)")
axes[0, 1].hist(df.loc[df["매칭사업수"] > 0, "국비비율(%)"], bins=25, color="#2f5d3a", edgecolor="white")
axes[0, 1].set_title("국비비율(%) — 매칭사업 있는 경우만")
axes[1, 0].hist(df["산림면적당_국비지원액(원per ha)"], bins=25, color="#2f5d3a", edgecolor="white")
axes[1, 0].set_title("산림면적당_국비지원액(원/ha)")
axes[1, 1].hist(df["매칭사업수"], bins=range(0, 7), color="#2f5d3a", edgecolor="white", align="left")
axes[1, 1].set_title("연도별 매칭사업수")
plt.tight_layout()
save_fig("distributions")

# ---------------------------------------------------------------
# 7. 시군구별 누적 국비지원액 TOP 15 + 산림면적당 국비 TOP 15
# ---------------------------------------------------------------
top_sgg = df.groupby(["시도", "시군구"])["국비지원액_원"].sum().sort_values(ascending=False).head(15) / 1e8
plt.figure(figsize=(8, 6))
labels = [f"{a} {b}" for a, b in top_sgg.index]
plt.barh(labels[::-1], top_sgg.values[::-1], color="#2e7d32")
plt.title("2016~2023 누적 국비지원액 상위 15개 시군구 (억원)")
plt.xlabel("누적 국비지원액 (억원)")
save_fig("top_sgg_gukbi")

top_perha = df.groupby(["시도", "시군구"])["산림면적당_국비지원액(원per ha)"].mean().sort_values(ascending=False).head(15)
plt.figure(figsize=(8, 6))
labels2 = [f"{a} {b}" for a, b in top_perha.index]
plt.barh(labels2[::-1], top_perha.values[::-1], color="#1b5e20")
plt.title("8개년 평균 산림면적당_국비지원액 상위 15개 시군구 (원/ha)")
plt.xlabel("산림면적당_국비지원액 (원/ha, 8개년 평균)")
save_fig("top_sgg_perha")

# ---------------------------------------------------------------
# 8. 이상치 확인: 시도별 산림면적당_국비지원액 boxplot
# ---------------------------------------------------------------
plt.figure(figsize=(10, 5))
sido_order = df.groupby("시도")["산림면적당_국비지원액(원per ha)"].median().sort_values(ascending=False).index
data_by_sido = [df.loc[df["시도"] == s, "산림면적당_국비지원액(원per ha)"].values for s in sido_order]
plt.boxplot(data_by_sido, labels=sido_order)
plt.xticks(rotation=30, ha="right")
plt.title("시도별 산림면적당_국비지원액(원/ha) 분포 (이상치 확인)")
plt.ylabel("산림면적당_국비지원액 (원/ha)")
save_fig("box_perha")

# ---------------------------------------------------------------
# 9. 상관관계 분석 (다중공선성 탐색용)
#    주의: 총사업비_원 = 국비지원액_원 + 시도비_원 + 시군구비_원 + 기타재원_원 (정의상 항등식)
#    이므로 이 5개를 동시에 VIF/회귀에 넣으면 완전공선성 발생 -> 분석용 변수셋을 분리
# ---------------------------------------------------------------
corr_cols = ["국비지원액_원", "총사업비_원", "국비비율(%)", "산림면적_ha",
             "산림면적당_국비지원액(원per ha)", "매칭사업수"]
corr = df[corr_cols].corr(method="pearson")
corr.to_csv(f"{OUTDIR}/correlation_matrix.csv", encoding="utf-8-sig")

plt.figure(figsize=(8, 6.5))
im = plt.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
plt.colorbar(im, fraction=0.046, pad=0.04)
plt.xticks(range(len(corr.columns)), corr.columns, rotation=90, fontsize=8)
plt.yticks(range(len(corr.columns)), corr.columns, fontsize=8)
for i in range(len(corr)):
    for j in range(len(corr)):
        v = corr.values[i, j]
        if abs(v) >= 0.3:
            plt.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                      color="white" if abs(v) > 0.7 else "black")
plt.title("수치형 변수 상관관계 행렬 (Pearson)")
plt.tight_layout()
save_fig("corr_heatmap")

pairs = []
cols = corr.columns.tolist()
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        r = corr.iloc[i, j]
        if abs(r) >= 0.5:
            pairs.append({"변수1": cols[i], "변수2": cols[j], "상관계수": round(float(r), 3)})
high_corr_df = pd.DataFrame(pairs).sort_values("상관계수", key=lambda s: s.abs(), ascending=False)
high_corr_df.to_csv(f"{OUTDIR}/high_correlation_pairs.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 10. VIF - 항등식 관계인 예산 구성요소를 제외한 "분석용 변수셋"만 사용
# ---------------------------------------------------------------
vif_cols = ["국비지원액_원", "산림면적_ha", "매칭사업수", "국비비율(%)"]
X = df[vif_cols].dropna()  # 국비비율(%) 결측(매칭 0건) 행 제외
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

plt.figure(figsize=(8, 4))
vif_sorted = vif_df.sort_values("VIF")
colors = ["#c0392b" if v >= 10 else ("#9c5a1e" if v >= 5 else "#2f5d3a") for v in vif_sorted["VIF"]]
plt.barh(vif_sorted["변수"], vif_sorted["VIF"], color=colors)
plt.axvline(5, color="gray", linestyle="--", linewidth=1)
plt.axvline(10, color="black", linestyle="--", linewidth=1)
plt.title("변수별 VIF (분산팽창지수) — 예산 구성요소 제외한 분석용 변수셋")
plt.xlabel("VIF (점선: 5, 10 기준선)")
save_fig("vif_chart")

# ---------------------------------------------------------------
# 11. 핵심 산점도
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
axes[0].scatter(df["국비지원액_원"] / 1e8, df["총사업비_원"] / 1e8, s=10, alpha=0.5, color="#2f5d3a")
axes[0].set_xlabel("국비지원액 (억원)"); axes[0].set_ylabel("총사업비 (억원)")
axes[0].set_title(f"r={corr.loc['국비지원액_원','총사업비_원']:.2f} (정의상 항등 성분)")

m = df["매칭사업수"] > 0
axes[1].scatter(df.loc[m, "총사업비_원"] / 1e8, df.loc[m, "국비비율(%)"], s=10, alpha=0.5, color="#2f5d3a")
axes[1].set_xlabel("총사업비 (억원)"); axes[1].set_ylabel("국비비율(%)")
axes[1].set_title(f"r={corr.loc['총사업비_원','국비비율(%)']:.2f}")

axes[2].scatter(df["산림면적_ha"], df["산림면적당_국비지원액(원per ha)"], s=10, alpha=0.5, color="#2f5d3a")
axes[2].set_xlabel("산림면적_ha"); axes[2].set_ylabel("산림면적당_국비지원액(원/ha)")
axes[2].set_title(f"r={corr.loc['산림면적_ha','산림면적당_국비지원액(원per ha)']:.2f}")
plt.tight_layout()
save_fig("scatter_key_pairs")

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
print("=== 8개년 전부 매칭 0건인 시군구 ===")
print(report["always_zero_sgg"])
print()
print("=== 상관계수 |r|>=0.5 쌍 ===")
print(high_corr_df.to_string(index=False))
print()
print("=== VIF ===")
print(vif_df.to_string(index=False))
print()
print("DONE. figs:", list(figs.keys()))
