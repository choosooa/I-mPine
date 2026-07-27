# -*- coding: utf-8 -*-
"""
국가지점번호 내부 거리분포 검증
- 동일 국가지점번호를 갖는 관측치들이 실제로 얼마나 가까이 모여있는지 정량화
- 2-pass streaming:
  pass1: code -> (sum_x, sum_y, n) 누적 (centroid 계산용)
  pass2: n>=2인 code에 대해 각 관측치의 centroid까지 거리 계산, 전체 분포 수집
- 출력: median/90pct/95pct/max, 10/50/100/300m 초과 비율
"""
import pandas as pd
import numpy as np
import os

RAW_DIR = "data/CH1/산림청_산림병해충방제 병해충발생관리정보_20250902"
YEARS = list(range(2016, 2024))
USECOLS = ["지역X좌표", "지역Y좌표", "국가지점번호"]
DTYPE = {"국가지점번호": str}
CHUNKSIZE = 500_000

# ---- pass 1: centroid 계산 ----
code_sum = {}  # code -> [sum_x, sum_y, n]
for year in YEARS:
    path = os.path.join(RAW_DIR, f"병해충발생정보관리_{year}.csv")
    reader = pd.read_csv(path, encoding="cp949", usecols=USECOLS, dtype=DTYPE,
                         chunksize=CHUNKSIZE, low_memory=False)
    for chunk in reader:
        x = pd.to_numeric(chunk["지역X좌표"], errors="coerce")
        y = pd.to_numeric(chunk["지역Y좌표"], errors="coerce")
        codes = chunk["국가지점번호"]
        valid = codes.notna() & x.notna() & y.notna()
        for c, cx, cy in zip(codes[valid].tolist(), x[valid].tolist(), y[valid].tolist()):
            e = code_sum.get(c)
            if e is None:
                code_sum[c] = [cx, cy, 1]
            else:
                e[0] += cx; e[1] += cy; e[2] += 1
    print(f"[pass1] {year} 완료, 누적 고유코드 {len(code_sum):,}")

code_mean = {c: (s[0] / s[2], s[1] / s[2]) for c, s in code_sum.items() if s[2] >= 2}
print("n>=2인 코드 수:", len(code_mean))

# ---- pass 2: centroid까지 거리 수집 (n>=2인 코드만) ----
distances = []
for year in YEARS:
    path = os.path.join(RAW_DIR, f"병해충발생정보관리_{year}.csv")
    reader = pd.read_csv(path, encoding="cp949", usecols=USECOLS, dtype=DTYPE,
                         chunksize=CHUNKSIZE, low_memory=False)
    for chunk in reader:
        x = pd.to_numeric(chunk["지역X좌표"], errors="coerce")
        y = pd.to_numeric(chunk["지역Y좌표"], errors="coerce")
        codes = chunk["국가지점번호"]
        valid = codes.notna() & x.notna() & y.notna()
        for c, cx, cy in zip(codes[valid].tolist(), x[valid].tolist(), y[valid].tolist()):
            m = code_mean.get(c)
            if m is not None:
                dx = cx - m[0]; dy = cy - m[1]
                distances.append((dx * dx + dy * dy) ** 0.5)
    print(f"[pass2] {year} 완료, 누적 거리표본 {len(distances):,}")

dist_arr = np.array(distances)
result = pd.DataFrame([
    ["n>=2_코드수", len(code_mean)],
    ["관측치_거리표본수(n>=2 코드에 속한 행수)", len(dist_arr)],
    ["거리_중앙값(m)", np.median(dist_arr)],
    ["거리_90퍼센타일(m)", np.percentile(dist_arr, 90)],
    ["거리_95퍼센타일(m)", np.percentile(dist_arr, 95)],
    ["거리_최대값(m)", dist_arr.max()],
    ["10m_초과_비율", (dist_arr > 10).mean()],
    ["50m_초과_비율", (dist_arr > 50).mean()],
    ["100m_초과_비율", (dist_arr > 100).mean()],
    ["300m_초과_비율", (dist_arr > 300).mean()],
], columns=["항목", "값"])

os.makedirs("intermediate_recurrence", exist_ok=True)
result.to_csv("intermediate_recurrence/검증_국가지점번호_내부거리분포.csv", index=False, encoding="utf-8-sig")
print("\n=== 국가지점번호 내부 거리분포 ===")
print(result.to_string(index=False))
