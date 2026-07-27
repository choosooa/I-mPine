# -*- coding: utf-8 -*-
"""
심화 검증
A) 국가지점번호: 같은 코드 -> 항상 같은 좌표인지 (위치 기반 격자코드 여부)
B) 국가지점번호: 연도 간 반복(cross-year) vs 같은 연도 내 반복(within-year) 분해
C) 국가지점번호 형식(자릿수/패턴) 일관성
D) 좌표계 정합성: 시도코드별(법정동코드 앞2자리) 평균 X,Y로 상대 위치 확인 (서울/부산/제주 등)
E) 2017년 X좌표 최댓값 이상치 원인 확인
F) 법정동코드 6자리(malformed) 표본 확인
"""
import pandas as pd
import numpy as np
import os
import re

RAW_DIR = "data/CH1/산림청_산림병해충방제 병해충발생관리정보_20250902"
YEARS = list(range(2016, 2024))
USECOLS = ["지역X좌표", "지역Y좌표", "국가지점번호", "법정동코드", "감염목구분"]
DTYPE = {"국가지점번호": str, "법정동코드": str, "감염목구분": str}
CHUNKSIZE = 500_000

# --- A,B,C 준비: code -> (year_bitmask, first_x, first_y, coord_consistent, n_rows) ---
code_index = {}          # code -> idx
year_bitmask = None      # numpy uint8 array, grows via list then converted
first_xy = []            # list of (x,y) at first sighting
coord_consistent = []    # bool list: 이후 관측에서도 좌표 동일했는지
n_rows_per_code = []     # list of counts

format_pattern = re.compile(r"^[가-힣]{2}\d{8}$")
format_match_count = 0
format_total = 0
format_len_counter = {}

sido_xy_sum = {}   # sido(2digit) -> [sum_x, sum_y, n]
year2017_outlier_rows = []
malformed_bjd_rows = {2021: [], 2022: []}

for year in YEARS:
    path = os.path.join(RAW_DIR, f"병해충발생정보관리_{year}.csv")
    reader = pd.read_csv(path, encoding="cp949", usecols=USECOLS, dtype=DTYPE,
                         chunksize=CHUNKSIZE, low_memory=False)
    ybit = 1 << (year - 2016)
    for chunk in reader:
        x = pd.to_numeric(chunk["지역X좌표"], errors="coerce")
        y = pd.to_numeric(chunk["지역Y좌표"], errors="coerce")

        # --- D: 시도코드별 좌표 합계 ---
        sido = chunk["법정동코드"].str.slice(0, 2)
        tmp = pd.DataFrame({"sido": sido, "x": x, "y": y}).dropna()
        for sido_code, g in tmp.groupby("sido"):
            if sido_code not in sido_xy_sum:
                sido_xy_sum[sido_code] = [0.0, 0.0, 0]
            sido_xy_sum[sido_code][0] += g["x"].sum()
            sido_xy_sum[sido_code][1] += g["y"].sum()
            sido_xy_sum[sido_code][2] += len(g)

        # --- E: 2017 이상치 (X > 500000) ---
        if year == 2017:
            mask = x > 500000
            if mask.any():
                sub = chunk.loc[mask, ["지역X좌표", "지역Y좌표", "법정동코드", "국가지점번호"]].head(20)
                year2017_outlier_rows.append(sub)

        # --- F: 법정동코드 6자리 표본 ---
        if year in (2021, 2022):
            bjd_len = chunk["법정동코드"].str.len()
            mask6 = bjd_len == 6
            if mask6.any() and len(malformed_bjd_rows[year]) < 20:
                malformed_bjd_rows[year].append(chunk.loc[mask6].head(20 - len(malformed_bjd_rows[year])))

        # --- A,B,C: 국가지점번호 처리 ---
        codes = chunk["국가지점번호"]
        valid = codes.notna()
        codes_v = codes[valid].tolist()
        x_v = x[valid].tolist()
        y_v = y[valid].tolist()

        for c, cx, cy in zip(codes_v, x_v, y_v):
            format_total += 1
            if format_pattern.match(c):
                format_match_count += 1
            L = len(c)
            format_len_counter[L] = format_len_counter.get(L, 0) + 1

            idx = code_index.get(c)
            if idx is None:
                idx = len(code_index)
                code_index[c] = idx
                first_xy.append((cx, cy))
                coord_consistent.append(True)
                n_rows_per_code.append(1)
            else:
                n_rows_per_code[idx] += 1
                fx, fy = first_xy[idx]
                if not (np.isclose(fx, cx, equal_nan=True) and np.isclose(fy, cy, equal_nan=True)):
                    coord_consistent[idx] = False

        if year_bitmask is None:
            year_bitmask = np.zeros(len(code_index) + 10_000_000, dtype=np.uint8)  # 넉넉히 미리 할당(실제로는 아래서 realloc 방지)
        # 인덱스 범위 초과 시 확장
        needed = len(code_index)
        if needed > len(year_bitmask):
            year_bitmask = np.concatenate([year_bitmask, np.zeros(needed - len(year_bitmask) + 1_000_000, dtype=np.uint8)])
        idxs = [code_index[c] for c in codes_v]
        year_bitmask[idxs] |= ybit

    print(f"[{year}] 국가지점번호 누적 고유값: {len(code_index):,}")

year_bitmask = year_bitmask[: len(code_index)]

# ---- 결과 정리 ----
n_rows_per_code = np.array(n_rows_per_code)
coord_consistent = np.array(coord_consistent)

popcount = np.zeros(len(code_index), dtype=np.uint8)
for b in range(8):
    popcount += (year_bitmask >> b) & 1

report_AB = pd.DataFrame([
    ["국가지점번호_고유값수", len(code_index)],
    ["코드당_평균행수", n_rows_per_code.mean()],
    ["코드당_중앙행수", np.median(n_rows_per_code)],
    ["코드당_최대행수", n_rows_per_code.max()],
    ["같은코드_좌표항상일치_비율", coord_consistent.mean()],
    ["같은코드_좌표불일치_코드수", (~coord_consistent).sum()],
    ["연도1개에서만_등장한_코드수", (popcount == 1).sum()],
    ["연도2개이상_등장한_코드수(교차연도반복)", (popcount >= 2).sum()],
    ["연도2개이상_등장_비율", (popcount >= 2).mean()],
    ["연도최대반복수(popcount_max)", popcount.max()],
], columns=["항목", "값"])
report_AB.to_csv("intermediate_recurrence/검증_국가지점번호_심화.csv", index=False, encoding="utf-8-sig")

report_C = pd.DataFrame([
    ["형식(가-힣2자+숫자8자)_일치건수", format_match_count],
    ["전체건수", format_total],
    ["형식일치율", format_match_count / format_total if format_total else np.nan],
] + [[f"자릿수_{k}", v] for k, v in sorted(format_len_counter.items())], columns=["항목", "값"])
report_C.to_csv("intermediate_recurrence/검증_국가지점번호_형식.csv", index=False, encoding="utf-8-sig")

sido_rows = []
for sido_code, (sx, sy, n) in sido_xy_sum.items():
    sido_rows.append([sido_code, n, sx / n, sy / n])
sido_df = pd.DataFrame(sido_rows, columns=["시도코드", "n", "평균X", "평균Y"]).sort_values("시도코드")
sido_df.to_csv("intermediate_recurrence/검증_시도코드별_평균좌표.csv", index=False, encoding="utf-8-sig")

if year2017_outlier_rows:
    pd.concat(year2017_outlier_rows).to_csv("intermediate_recurrence/검증_2017_좌표이상치.csv", index=False, encoding="utf-8-sig")
else:
    pd.DataFrame(columns=["지역X좌표", "지역Y좌표", "법정동코드", "국가지점번호"]).to_csv(
        "intermediate_recurrence/검증_2017_좌표이상치.csv", index=False, encoding="utf-8-sig")

for yr, rows in malformed_bjd_rows.items():
    if rows:
        pd.concat(rows).to_csv(f"intermediate_recurrence/검증_법정동코드6자리_표본_{yr}.csv", index=False, encoding="utf-8-sig")

print("\n=== A,B: 국가지점번호 심화 ===")
print(report_AB.to_string(index=False))
print("\n=== C: 국가지점번호 형식 ===")
print(report_C.to_string(index=False))
print("\n=== D: 시도코드별 평균좌표 ===")
print(sido_df.to_string(index=False))
