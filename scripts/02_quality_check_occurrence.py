# -*- coding: utf-8 -*-
"""
2016~2023 발생자료 품질검사
- 파일 존재/행수/컬럼 구조
- 감염목구분/고사목구분 분포
- 좌표 요약(연도별 min/max/median/자릿수)
- 법정동코드 자릿수
- 국가지점번호 결측률/고유값/중복률
메모리 절약: usecols 지정, chunksize로 스트리밍 집계 (전체를 한 번에 메모리에 올리지 않음)
"""
import pandas as pd
import numpy as np
import os

RAW_DIR = "data/CH1/산림청_산림병해충방제 병해충발생관리정보_20250902"
YEARS = list(range(2016, 2024))
USECOLS = ["지역X좌표", "지역Y좌표", "국가지점번호", "PNU코드", "법정동코드",
           "고사목구분", "감염목구분", "조사일자"]
DTYPE = {"국가지점번호": str, "PNU코드": str, "법정동코드": str,
         "고사목구분": str, "감염목구분": str, "조사일자": str}
CHUNKSIZE = 500_000

os.makedirs("intermediate_recurrence", exist_ok=True)

rows_report = []
infection_dist_all = []
deadtree_dist_all = []
coord_stats = []
bjd_len_counter = {}
gukji_missing = 0
gukji_total = 0
gukji_value_counts_partial = {}  # sample-based uniqueness (exact global uniqueness done later with set, memory ok since these are short strings)
gukji_seen = set()
gukji_dupe_count = 0

for year in YEARS:
    path = os.path.join(RAW_DIR, f"병해충발생정보관리_{year}.csv")
    exists = os.path.exists(path)
    if not exists:
        rows_report.append([year, False, np.nan, np.nan])
        continue

    n_rows = 0
    x_min, x_max = np.inf, -np.inf
    y_min, y_max = np.inf, -np.inf
    x_vals_sample = []
    y_vals_sample = []
    infect_counter = {}
    dead_counter = {}
    bjd_lens_year = {}
    gukji_missing_year = 0
    gukji_total_year = 0
    columns_seen = None

    reader = pd.read_csv(
        path, encoding="cp949", usecols=USECOLS, dtype=DTYPE,
        chunksize=CHUNKSIZE, low_memory=False,
    )
    for chunk in reader:
        if columns_seen is None:
            columns_seen = list(chunk.columns)
        n_rows += len(chunk)

        x = pd.to_numeric(chunk["지역X좌표"], errors="coerce")
        y = pd.to_numeric(chunk["지역Y좌표"], errors="coerce")
        x_min = min(x_min, x.min()); x_max = max(x_max, x.max())
        y_min = min(y_min, y.min()); y_max = max(y_max, y.max())
        if len(x_vals_sample) < 20000:
            x_vals_sample.extend(x.dropna().head(2000).tolist())
            y_vals_sample.extend(y.dropna().head(2000).tolist())

        for k, v in chunk["감염목구분"].value_counts(dropna=False).items():
            infect_counter[k] = infect_counter.get(k, 0) + int(v)
        for k, v in chunk["고사목구분"].value_counts(dropna=False).items():
            dead_counter[k] = dead_counter.get(k, 0) + int(v)

        bjd_len = chunk["법정동코드"].dropna().str.len()
        for k, v in bjd_len.value_counts().items():
            bjd_lens_year[k] = bjd_lens_year.get(k, 0) + int(v)

        gukji_missing_year += chunk["국가지점번호"].isna().sum()
        gukji_total_year += len(chunk)
        for v in chunk["국가지점번호"].dropna().tolist():
            if v in gukji_seen:
                gukji_dupe_count += 1
            else:
                gukji_seen.add(v)

    rows_report.append([year, True, n_rows, columns_seen])
    coord_stats.append([year, x_min, x_max, np.median(x_vals_sample) if x_vals_sample else np.nan,
                         y_min, y_max, np.median(y_vals_sample) if y_vals_sample else np.nan])
    infection_dist_all.append((year, infect_counter))
    deadtree_dist_all.append((year, dead_counter))
    bjd_len_counter[year] = bjd_lens_year
    gukji_missing += gukji_missing_year
    gukji_total += gukji_total_year
    print(f"[{year}] rows={n_rows} 완료")

# ---- 리포트 저장 ----
rows_df = pd.DataFrame(rows_report, columns=["year", "exists", "n_rows", "columns"])
rows_df.to_csv("intermediate_recurrence/검증_파일별_행수_컬럼.csv", index=False, encoding="utf-8-sig")

coord_df = pd.DataFrame(coord_stats, columns=["year", "x_min", "x_max", "x_median_sample", "y_min", "y_max", "y_median_sample"])
coord_df.to_csv("intermediate_recurrence/검증_좌표요약_연도별.csv", index=False, encoding="utf-8-sig")

infect_rows = []
for year, counter in infection_dist_all:
    total = sum(counter.values())
    for k, v in counter.items():
        infect_rows.append([year, k, v, v / total if total else np.nan])
infect_df = pd.DataFrame(infect_rows, columns=["year", "감염목구분", "행수", "비율"])
infect_df.to_csv("intermediate_recurrence/검증_감염목구분_연도별분포.csv", index=False, encoding="utf-8-sig")

dead_rows = []
for year, counter in deadtree_dist_all:
    total = sum(counter.values())
    for k, v in counter.items():
        dead_rows.append([year, k, v, v / total if total else np.nan])
dead_df = pd.DataFrame(dead_rows, columns=["year", "고사목구분", "행수", "비율"])
dead_df.to_csv("intermediate_recurrence/검증_고사목구분_연도별분포.csv", index=False, encoding="utf-8-sig")

bjd_rows = []
for year, d in bjd_len_counter.items():
    for length, cnt in d.items():
        bjd_rows.append([year, length, cnt])
bjd_df = pd.DataFrame(bjd_rows, columns=["year", "법정동코드_자릿수", "행수"])
bjd_df.to_csv("intermediate_recurrence/검증_법정동코드_자릿수_연도별.csv", index=False, encoding="utf-8-sig")

gukji_report = pd.DataFrame([
    ["전체행수", gukji_total],
    ["국가지점번호_결측수", gukji_missing],
    ["국가지점번호_결측률", gukji_missing / gukji_total if gukji_total else np.nan],
    ["국가지점번호_고유값수(결측제외)", len(gukji_seen)],
    ["국가지점번호_중복발생횟수(같은값재등장)", gukji_dupe_count],
], columns=["항목", "값"])
gukji_report.to_csv("intermediate_recurrence/검증_국가지점번호_기초통계.csv", index=False, encoding="utf-8-sig")

print("\n=== 파일별 행수 ===")
print(rows_df[["year", "exists", "n_rows"]].to_string(index=False))
print("\n=== 좌표 요약 ===")
print(coord_df.to_string(index=False))
print("\n=== 감염목구분 분포 (연도별) ===")
print(infect_df.to_string(index=False))
print("\n=== 법정동코드 자릿수 (연도별) ===")
print(bjd_df.to_string(index=False))
print("\n=== 국가지점번호 기초통계 ===")
print(gukji_report.to_string(index=False))
