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

BASE = "/Users/chanhaeng17/Desktop/임업통계 공모전/CH2 기후위험도"
IN = "/Users/chanhaeng17/Desktop/I-mPine/CH2 data/CH2_기후위험도_시군구매핑_전국250_2016_2025.csv"
OUTDIR = f"{BASE}/output/nationwide"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(IN, encoding="utf-8-sig")

NUMERIC_COLS = [
    "연평균기온", "겨울철_평균최저기온", "여름철_평균기온", "연강수량_mm", "평균풍속_ms",
    "GDD_솔수염하늘소_base11.9", "GDD_북방수염하늘소_base8.3",
    "SPI3_연평균", "SPI3_최저월(최심가뭄)", "SPI3_최고월(최다습)", "SPI3_유효월수",
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
# 0. 기본 구조 & 매칭 품질(이 파일 고유 이슈: 관측소 1개가 여러 시군구를 대표)
# ---------------------------------------------------------------
report["shape"] = {"rows": df.shape[0], "cols": df.shape[1]}
report["연도범위"] = [int(df["연도"].min()), int(df["연도"].max())]
report["시군구수"] = int(df[["시도", "시군구"]].drop_duplicates().shape[0])  # 시군구명은 도별 중복(중구/남구 등) 가능 -> (시도,시군구) 쌍으로 카운트
report["관측소수"] = int(df["stnId"].nunique())
report["시도수"] = int(df["시도"].nunique())

county_stn = df[["시도", "시군구", "stnId", "참조관측소", "거리_km"]].drop_duplicates()
stn_load = county_stn.groupby(["stnId", "참조관측소"]).size().sort_values(ascending=False)
report["관측소당_담당시군구_평균"] = round(float(stn_load.mean()), 2)
report["관측소당_담당시군구_최대"] = int(stn_load.max())
report["거리30km이상_시군구수"] = int((county_stn["거리_km"] >= 30).sum())
report["거리평균_km"] = round(float(county_stn["거리_km"].mean()), 2)
report["거리중앙값_km"] = round(float(county_stn["거리_km"].median()), 2)

plt.figure(figsize=(8, 4.5))
plt.hist(county_stn["거리_km"], bins=30, color="#2f5d3a", edgecolor="white")
plt.axvline(30, color="#9c5a1e", linestyle="--", linewidth=1.2, label="30km 기준")
plt.legend()
plt.title("시군구 중심점 - 최근접 관측소 간 거리 분포")
plt.xlabel("거리 (km)"); plt.ylabel("시군구 수")
save_fig("distance_hist")

top_load = stn_load.head(15)
plt.figure(figsize=(8, 6))
labels = [f"{a} ({b})" for a, b in top_load.index]
plt.barh(labels[::-1], top_load.values[::-1], color="#2f5d3a")
plt.title("관측소별 담당 시군구 개수 상위 15개")
plt.xlabel("담당 시군구 개수")
save_fig("station_load_top15")

far_counties = county_stn.sort_values("거리_km", ascending=False).head(10)
far_counties.to_csv(f"{OUTDIR}/far_counties_top10.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 1. 결측값 분석 (관측소 결측이 여러 시군구로 '전파'되는 구조)
# ---------------------------------------------------------------
na_counts = df.isna().sum()
na_ratio = (df.isna().mean() * 100).round(2)
missing_df = pd.DataFrame({"결측개수": na_counts, "결측비율(%)": na_ratio})
missing_df = missing_df[missing_df["결측개수"] > 0].reset_index().rename(columns={"index": "컬럼"})
missing_df.to_csv(f"{OUTDIR}/missing_summary.csv", index=False, encoding="utf-8-sig")

na_by_year = df.groupby("연도")["연평균기온"].apply(lambda s: s.isna().mean() * 100)
plt.figure(figsize=(9, 4))
plt.bar(na_by_year.index.astype(str), na_by_year.values, color="#9c5a1e")
plt.title("연도별 '연평균기온' 결측 비율 (시군구 기준)")
plt.ylabel("결측 비율 (%)"); plt.xlabel("연도")
save_fig("missing_by_year")

missing_rows_df = df.loc[df["연평균기온"].isna(), ["시도", "시군구"]].drop_duplicates()
missing_counties = sorted((missing_rows_df["시도"] + " " + missing_rows_df["시군구"]).tolist())
report["missing_counties_n"] = len(missing_counties)
report["missing_core_count"] = int(na_counts["연평균기온"])
report["missing_core_ratio"] = round(float(df["연평균기온"].isna().mean() * 100), 1)
report["missing_stations_behind"] = sorted(df.loc[df["연평균기온"].isna(), "참조관측소"].unique().tolist())

# ---------------------------------------------------------------
# 2. 기술통계
# ---------------------------------------------------------------
desc = df[NUMERIC_COLS].describe().T
desc["skew"] = df[NUMERIC_COLS].skew()
desc.to_csv(f"{OUTDIR}/descriptive_stats.csv", encoding="utf-8-sig")

fig, axes = plt.subplots(2, 2, figsize=(11, 8))
axes[0, 0].hist(df["연평균기온"].dropna(), bins=30, color="#2f5d3a", edgecolor="white")
axes[0, 0].set_title("연평균기온 (°C) - 시군구 기준")
axes[0, 1].hist(df["연강수량_mm"].dropna(), bins=30, color="#2f5d3a", edgecolor="white")
axes[0, 1].set_title("연강수량 (mm)")
axes[1, 0].hist(df["GDD_솔수염하늘소_base11.9"].dropna(), bins=30, color="#2f5d3a", edgecolor="white")
axes[1, 0].set_title("GDD_솔수염하늘소_base11.9")
axes[1, 1].hist(df["SPI3_연평균"].dropna(), bins=30, color="#2f5d3a", edgecolor="white")
axes[1, 1].set_title("SPI3_연평균")
plt.tight_layout()
save_fig("distributions")

# ---------------------------------------------------------------
# 3. 시도별 시군구 수 & 연도별 추이 (시군구 단위 = 관측소 중복 반영된 값)
# ---------------------------------------------------------------
sido_count = df.groupby("시도")["시군구"].nunique().sort_values(ascending=False)
plt.figure(figsize=(8, 6))
plt.barh(sido_count.index[::-1], sido_count.values[::-1], color="#2f5d3a")
plt.title("시도별 시군구 개수")
plt.xlabel("시군구 개수")
save_fig("sido_count")

year_sum = df.groupby("연도")[["연평균기온", "연강수량_mm", "GDD_솔수염하늘소_base11.9",
                                "GDD_북방수염하늘소_base8.3", "SPI3_연평균"]].mean().round(3)
year_sum.to_csv(f"{OUTDIR}/year_summary.csv", encoding="utf-8-sig")

plt.figure(figsize=(9, 4.5))
plt.plot(year_sum.index, year_sum["연평균기온"], marker="o", color="#2f5d3a")
plt.title("연도별 전국 평균기온 (250개 시군구 평균)")
plt.xlabel("연도"); plt.ylabel("연평균기온 (°C)")
save_fig("year_total_temp")

sido_year = df.groupby(["연도", "시도"])["연평균기온"].mean().unstack()
plt.figure(figsize=(10, 5))
for col in sido_year.columns:
    plt.plot(sido_year.index, sido_year[col], marker="o", label=col, markersize=3)
plt.legend(fontsize=7, ncol=3)
plt.title("시도별 연평균기온 연도 추이 (시군구 평균)")
plt.xlabel("연도"); plt.ylabel("연평균기온 (°C)")
save_fig("sido_year_trend")

plt.figure(figsize=(9, 4.5))
plt.plot(year_sum.index, year_sum["GDD_솔수염하늘소_base11.9"], marker="o", label="솔수염하늘소 (11.9°C)", color="#2f5d3a")
plt.plot(year_sum.index, year_sum["GDD_북방수염하늘소_base8.3"], marker="o", label="북방수염하늘소 (8.3°C)", color="#9c5a1e")
plt.legend(fontsize=9)
plt.title("연도별 매개충 발육적산온도(GDD) 추이 - 시군구 평균")
plt.xlabel("연도"); plt.ylabel("GDD")
save_fig("gdd_trend")

# ---------------------------------------------------------------
# 4. 시군구 지리 분포 산점도 (중심점 좌표 x GDD) - 경량 지도 대체
# ---------------------------------------------------------------
county_geo = df[["시군구", "시도"]].drop_duplicates().merge(
    county_stn[["시군구", "stnId"]], on="시군구", how="left"
)
# lat/lon은 build_nationwide_mapping.py 산출물엔 없으므로(중간 산출), county_stn만으로 대체 불가 -> 생략
# 대신 GDD 상위/하위 시군구 순위표로 대체

gdd_latest = df[df["연도"] == df["연도"].max()][["시도", "시군구", "GDD_솔수염하늘소_base11.9", "연평균기온"]].dropna()
top_gdd = gdd_latest.sort_values("GDD_솔수염하늘소_base11.9", ascending=False).head(15)
bottom_gdd = gdd_latest.sort_values("GDD_솔수염하늘소_base11.9", ascending=True).head(15)
top_gdd.to_csv(f"{OUTDIR}/top15_gdd_{df['연도'].max()}.csv", index=False, encoding="utf-8-sig")
bottom_gdd.to_csv(f"{OUTDIR}/bottom15_gdd_{df['연도'].max()}.csv", index=False, encoding="utf-8-sig")

plt.figure(figsize=(8, 6))
labels = [f"{a} {b}" for a, b in zip(top_gdd["시도"], top_gdd["시군구"])]
plt.barh(labels[::-1], top_gdd["GDD_솔수염하늘소_base11.9"][::-1], color="#c0392b")
plt.title(f"{df['연도'].max()}년 GDD_솔수염하늘소 상위 15개 시군구")
plt.xlabel("GDD")
save_fig("top15_gdd")

# ---------------------------------------------------------------
# 5. 상관관계 & VIF (주의: 시군구가 관측소를 공유하므로 유효 독립표본은 250이 아니라 관측소 수(89)에 더 가까움)
# ---------------------------------------------------------------
corr_cols = ["연평균기온", "겨울철_평균최저기온", "여름철_평균기온", "연강수량_mm", "평균풍속_ms",
             "GDD_솔수염하늘소_base11.9", "GDD_북방수염하늘소_base8.3", "SPI3_연평균"]
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
plt.title("수치형 변수 상관관계 행렬 (시군구 단위, Pearson)")
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

vif_cols = ["연평균기온", "겨울철_평균최저기온", "여름철_평균기온", "연강수량_mm",
            "평균풍속_ms", "GDD_솔수염하늘소_base11.9", "SPI3_연평균"]
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

# ---------------------------------------------------------------
# 6. 기존 31개 시군구 수작업 매핑과의 정합성 체크
# ---------------------------------------------------------------
old_path = "/Users/chanhaeng17/Desktop/I-mPine/CH2 data/CH2_기후위험도_시군구매핑_2016_2025.csv"
old = pd.read_csv(old_path, dtype={"stnId": str})
old_map = old[["시도", "시군구", "stnId"]].drop_duplicates().rename(columns={"stnId": "old_stnId"})
new_map = df[["시도", "시군구", "stnId"]].drop_duplicates().rename(columns={"stnId": "new_stnId"})
new_map["new_stnId"] = new_map["new_stnId"].astype(str)
cmp = old_map.merge(new_map, on=["시도", "시군구"], how="inner")
cmp["일치"] = cmp["old_stnId"] == cmp["new_stnId"]
cmp.to_csv(f"{OUTDIR}/consistency_check_vs_manual31.csv", index=False, encoding="utf-8-sig")
report["정합성_겹치는시군구수"] = int(len(cmp))
report["정합성_불일치수"] = int((~cmp["일치"]).sum())

with open(f"{OUTDIR}/figs_b64.json", "w") as f:
    json.dump(figs, f)
with open(f"{OUTDIR}/report_meta.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("=== 기본 구조 ===")
print(report)
print()
print("=== 결측 요약 ===")
print(missing_df)
print()
print("=== VIF ===")
print(vif_df.to_string(index=False))
print()
print("=== 상관계수 |r|>=0.5 쌍 ===")
print(high_corr_df.to_string(index=False))
print()
print("=== 정합성 체크(기존 31개 수작업 매핑) ===")
print(cmp[~cmp["일치"]].to_string(index=False) if (~cmp["일치"]).any() else "전부 일치")
print()
print("DONE. figs:", list(figs.keys()))
