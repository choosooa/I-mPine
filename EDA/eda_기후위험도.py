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

BASE = "/Users/chanhaeng17/Desktop/임업통계 공모전/CH2 기후위험도"
IN = f"{BASE}/climate_risk_2016_2025.csv"
OUTDIR = f"{BASE}/output"
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(IN, encoding="utf-8-sig")

NUMERIC_COLS = [
    "연평균기온", "겨울철_평균최저기온", "여름철_평균기온", "연강수량_mm", "평균풍속_ms",
    "GDD_솔수염하늘소_base11.9", "GDD_북방수염하늘소_base8.3",
    "SPI3_연평균", "SPI3_최저월(최심가뭄)", "SPI3_최고월(최다습)", "SPI3_유효월수",
]
CATEGORICAL_COLS = ["시도", "stnNm"]

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
report["연도범위"] = [int(df["year"].min()), int(df["year"].max())]
report["관측소수"] = int(df["stnId"].nunique())
report["시도수"] = int(df["시도"].nunique())
dtype_df = df.dtypes.astype(str).reset_index()
dtype_df.columns = ["컬럼", "타입"]
dtype_df.to_csv(f"{OUTDIR}/dtypes.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 2. 결측값 분석
#    - 표고_m은 전량 결측(산출물에서 제외 처리된 컬럼), 토양수분은 필드 자체가 없음
#    - 핵심 기상 변수는 관측 개시/중단 시점이 다른 4개 관측소에 결측이 몰려 있음
# ---------------------------------------------------------------
na_counts = df.isna().sum()
na_ratio = (df.isna().mean() * 100).round(2)
missing_df = pd.DataFrame({"결측개수": na_counts, "결측비율(%)": na_ratio})
missing_df = missing_df[missing_df["결측개수"] > 0].reset_index().rename(columns={"index": "컬럼"})
missing_df.to_csv(f"{OUTDIR}/missing_summary.csv", index=False, encoding="utf-8-sig")

na_by_year = df.groupby("year")["연평균기온"].apply(lambda s: s.isna().mean() * 100)
plt.figure(figsize=(9, 4))
plt.bar(na_by_year.index.astype(str), na_by_year.values, color="#9c5a1e")
plt.title("연도별 '연평균기온' 결측 비율")
plt.ylabel("결측 비율 (%)")
plt.xlabel("연도")
save_fig("missing_by_year")

missing_stations = sorted(df.loc[df["연평균기온"].isna(), "stnNm"].unique().tolist())
report["missing_stations"] = missing_stations
report["missing_core_count"] = int(na_counts["연평균기온"])
report["missing_core_ratio"] = round(float(df["연평균기온"].isna().mean() * 100), 1)
report["missing_elevation_ratio"] = round(float(df["표고_m"].isna().mean() * 100), 1) if "표고_m" in df.columns else None

zero_by_stn = df.groupby("stnNm")["연평균기온"].apply(lambda s: s.isna().sum())
zero_by_stn = zero_by_stn[zero_by_stn > 0].sort_values(ascending=False)
plt.figure(figsize=(7, 4))
plt.barh(zero_by_stn.index[::-1], zero_by_stn.values[::-1], color="#9c5a1e")
plt.title("관측소별 '연평균기온' 결측 연도 수 (10개년 중)")
plt.xlabel("결측 연도 수")
save_fig("missing_by_station")

# ---------------------------------------------------------------
# 3. 기술통계
# ---------------------------------------------------------------
desc = df[NUMERIC_COLS].describe().T
desc["skew"] = df[NUMERIC_COLS].skew()
desc.to_csv(f"{OUTDIR}/descriptive_stats.csv", encoding="utf-8-sig")

# ---------------------------------------------------------------
# 4. 시도별 관측소 수
# ---------------------------------------------------------------
sido_count = df.groupby("시도")["stnId"].nunique().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
plt.barh(sido_count.index[::-1], sido_count.values[::-1], color="#2f5d3a")
plt.title("시도별 관측소 개수")
plt.xlabel("관측소 개수")
save_fig("sido_count")

# ---------------------------------------------------------------
# 5. 연도별 추이
# ---------------------------------------------------------------
year_sum = df.groupby("year")[["연평균기온", "연강수량_mm", "GDD_솔수염하늘소_base11.9",
                                "GDD_북방수염하늘소_base8.3", "SPI3_연평균"]].mean().round(3)
year_sum.to_csv(f"{OUTDIR}/year_summary.csv", encoding="utf-8-sig")

plt.figure(figsize=(9, 4.5))
plt.plot(year_sum.index, year_sum["연평균기온"], marker="o", color="#2f5d3a")
plt.title("연도별 전국 평균기온 (98개 관측소 평균)")
plt.xlabel("연도"); plt.ylabel("연평균기온 (°C)")
save_fig("year_total_temp")

sido_year = df.groupby(["year", "시도"])["연평균기온"].mean().unstack()
plt.figure(figsize=(10, 5))
for col in sido_year.columns:
    plt.plot(sido_year.index, sido_year[col], marker="o", label=col, markersize=3)
plt.legend(fontsize=8, ncol=2)
plt.title("시도별 연평균기온 연도 추이")
plt.xlabel("연도"); plt.ylabel("연평균기온 (°C)")
save_fig("sido_year_trend")

plt.figure(figsize=(9, 4.5))
plt.plot(year_sum.index, year_sum["GDD_솔수염하늘소_base11.9"], marker="o", label="솔수염하늘소 (11.9°C)", color="#2f5d3a")
plt.plot(year_sum.index, year_sum["GDD_북방수염하늘소_base8.3"], marker="o", label="북방수염하늘소 (8.3°C)", color="#9c5a1e")
plt.legend(fontsize=9)
plt.title("연도별 매개충 발육적산온도(GDD) 추이")
plt.xlabel("연도"); plt.ylabel("GDD")
save_fig("gdd_trend")

plt.figure(figsize=(9, 4))
colors = ["#2f5d3a" if v >= 0 else "#9c5a1e" for v in year_sum["SPI3_연평균"]]
plt.bar(year_sum.index.astype(str), year_sum["SPI3_연평균"], color=colors)
plt.axhline(0, color="gray", linewidth=1)
plt.title("연도별 SPI3 연평균 (건조 ↔ 습윤)")
plt.xlabel("연도"); plt.ylabel("SPI3 (음수=건조, 양수=습윤)")
save_fig("spi_trend")

# ---------------------------------------------------------------
# 6. 분포 (히스토그램)
# ---------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
axes[0, 0].hist(df["연평균기온"].dropna(), bins=25, color="#2f5d3a", edgecolor="white")
axes[0, 0].set_title("연평균기온 (°C)")
axes[0, 1].hist(df["연강수량_mm"].dropna(), bins=25, color="#2f5d3a", edgecolor="white")
axes[0, 1].set_title("연강수량 (mm)")
axes[1, 0].hist(df["GDD_솔수염하늘소_base11.9"].dropna(), bins=25, color="#2f5d3a", edgecolor="white")
axes[1, 0].set_title("GDD_솔수염하늘소_base11.9")
axes[1, 1].hist(df["SPI3_연평균"].dropna(), bins=25, color="#2f5d3a", edgecolor="white")
axes[1, 1].set_title("SPI3_연평균")
plt.tight_layout()
save_fig("distributions")

# ---------------------------------------------------------------
# 7. 관측소별 편중 & 이상치
# ---------------------------------------------------------------
slopes = []
for stn, g in df.groupby("stnNm"):
    g2 = g.dropna(subset=["연평균기온"])
    if len(g2) >= 5:
        slope = np.polyfit(g2["year"], g2["연평균기온"], 1)[0]
        slopes.append((stn, g2["시도"].iloc[0], slope, len(g2)))
slope_df = pd.DataFrame(slopes, columns=["관측소", "시도", "온난화속도(°C/년)", "n"]).sort_values(
    "온난화속도(°C/년)", ascending=False
)
slope_df.to_csv(f"{OUTDIR}/warming_rate_by_station.csv", index=False, encoding="utf-8-sig")

top_warm = slope_df.head(15)
plt.figure(figsize=(8, 6))
labels = [f"{a} ({b})" for a, b in zip(top_warm["관측소"], top_warm["시도"])]
plt.barh(labels[::-1], top_warm["온난화속도(°C/년)"][::-1], color="#c0392b")
plt.title("관측소별 온난화 속도(선형회귀 기울기) 상위 15개")
plt.xlabel("°C / 년")
save_fig("top_warming")

plt.figure(figsize=(10, 5))
sido_order = df.groupby("시도")["연평균기온"].median().sort_values(ascending=False).index
data_by_sido = [df.loc[df["시도"] == s, "연평균기온"].dropna().values for s in sido_order]
plt.boxplot(data_by_sido, labels=sido_order)
plt.xticks(rotation=30, ha="right")
plt.title("시도별 연평균기온 분포 (이상치 확인)")
plt.ylabel("연평균기온 (°C)")
save_fig("box_temp")

# ---------------------------------------------------------------
# 8. 상관관계 분석 (다중공선성 탐색용)
#    주의: GDD_솔수염하늘소_base11.9 와 GDD_북방수염하늘소_base8.3 은
#    같은 일별 기온 데이터에서 기준온도만 다르게 적용한 파생 변수라 r=0.99로 사실상 항등 관계
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
# 9. VIF - 항등관계인 GDD_북방수염하늘소_base8.3(파생 쌍둥이 변수)은 제외한 분석용 변수셋만 사용
# ---------------------------------------------------------------
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

plt.figure(figsize=(8, 4))
vif_sorted = vif_df.sort_values("VIF")
colors = ["#c0392b" if v >= 10 else ("#9c5a1e" if v >= 5 else "#2f5d3a") for v in vif_sorted["VIF"]]
plt.barh(vif_sorted["변수"], vif_sorted["VIF"], color=colors)
plt.axvline(5, color="gray", linestyle="--", linewidth=1)
plt.axvline(10, color="black", linestyle="--", linewidth=1)
plt.title("변수별 VIF (분산팽창지수) — GDD 쌍둥이 변수 중 하나 제외")
plt.xlabel("VIF (점선: 5, 10 기준선)")
save_fig("vif_chart")

# ---------------------------------------------------------------
# 10. 핵심 산점도
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
axes[0].scatter(df["연평균기온"], df["GDD_솔수염하늘소_base11.9"], s=8, alpha=0.5, color="#2f5d3a")
axes[0].set_xlabel("연평균기온 (°C)"); axes[0].set_ylabel("GDD_솔수염하늘소_base11.9")
axes[0].set_title(f"r={corr.loc['연평균기온','GDD_솔수염하늘소_base11.9']:.2f}")

axes[1].scatter(df["GDD_솔수염하늘소_base11.9"], df["GDD_북방수염하늘소_base8.3"], s=8, alpha=0.5, color="#2f5d3a")
axes[1].set_xlabel("GDD_솔수염하늘소_base11.9"); axes[1].set_ylabel("GDD_북방수염하늘소_base8.3")
axes[1].set_title(f"r={corr.loc['GDD_솔수염하늘소_base11.9','GDD_북방수염하늘소_base8.3']:.2f} (파생 쌍둥이)")

axes[2].scatter(df["연강수량_mm"], df["SPI3_연평균"], s=8, alpha=0.5, color="#2f5d3a")
axes[2].set_xlabel("연강수량_mm"); axes[2].set_ylabel("SPI3_연평균")
axes[2].set_title(f"r={corr.loc['연강수량_mm','SPI3_연평균']:.2f}")
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
print("=== 결측 관측소 ===")
print(missing_stations)
print()
print("=== 상관계수 |r|>=0.5 쌍 ===")
print(high_corr_df.to_string(index=False))
print()
print("=== VIF ===")
print(vif_df.to_string(index=False))
print()
print("DONE. figs:", list(figs.keys()))
