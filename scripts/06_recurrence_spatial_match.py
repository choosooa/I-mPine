# -*- coding: utf-8 -*-
"""
전국단위 공간매칭으로 재발생/신규발생 변수 계산 (100/300/500m)
- 시군구 경계로 매칭을 제한하지 않음 (전국 cKDTree)
- 브루트포스 거리행렬 금지: 연도쌍마다 딱 2번의 최근접이웃 쿼리만 수행
    1) dist_curr_to_prev = KDTree(prev).query(curr)  -> 신규발생 판정용 (당해->전년 최근접거리)
    2) dist_prev_to_curr = KDTree(curr).query(prev)  -> 재발생 판정용 (전년->당해 최근접거리)
  각 반경(100/300/500)은 이 두 거리에 대한 임계값 비교로만 산출 (추가 쿼리 없음)
- 재발생: 전년도 발생지 시군구에 귀속 / 신규발생: 당해연도 발생지 시군구에 귀속
- prev_infected_sites(t) == current_infected_sites(t-1) 되도록 동일 캐시에서 유도(정합성 보장)
- 2016년: 전년도 자료 없음 -> 재발생 관련 변수 전부 NA (current_infected_sites만 실값)
- 250개 sigungu_cd 전체에 대해 행 생성, 발생자료 없는 시군구는 0으로 채움(감염목 미보고가 아니라
  발생자료 자체가 nationwide 커버리지이므로 '없음=0'으로 간주. 68개 시군구가 전기간 무기록임을
  4단계 검증에서 확인)
"""
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import os

YEARS = list(range(2016, 2024))
RADII = [100, 300, 500]

budget = pd.read_parquet("processed/budget_panel_step1.parquet")
FULL_SIGUNGU = sorted(budget["sigungu_cd"].unique())
print("전체 sigungu_cd 수:", len(FULL_SIGUNGU))

sites_cache = {y: pd.read_parquet(f"processed/infected_sites_{y}.parquet") for y in YEARS}

all_rows = []

# ---- 2016: 재발생 변수 전부 NA, current_infected_sites만 실값 ----
cur16 = sites_cache[2016].groupby("sigungu_cd").size().reindex(FULL_SIGUNGU, fill_value=0)
for sgg in FULL_SIGUNGU:
    row = {"year": 2016, "sigungu_cd": sgg, "current_infected_sites": int(cur16[sgg]),
           "prev_infected_sites": np.nan}
    for r in RADII:
        row[f"recurrent_sites_{r}m"] = np.nan
        row[f"recurrence_rate_{r}m"] = np.nan
        row[f"new_sites_{r}m"] = np.nan
        row[f"new_site_share_{r}m"] = np.nan
    all_rows.append(row)

# ---- 2017~2023: 연도쌍 매칭 ----
for t in YEARS[1:]:
    prev = sites_cache[t - 1].copy()
    curr = sites_cache[t].copy()
    print(f"\n[{t-1} -> {t}] prev={len(prev)} curr={len(curr)}")

    if len(prev) == 0 or len(curr) == 0:
        dist_curr_to_prev = np.full(len(curr), np.inf)
        dist_prev_to_curr = np.full(len(prev), np.inf)
    else:
        tree_prev = cKDTree(prev[["x", "y"]].values)
        tree_curr = cKDTree(curr[["x", "y"]].values)
        dist_curr_to_prev, _ = tree_prev.query(curr[["x", "y"]].values, k=1)
        dist_prev_to_curr, _ = tree_curr.query(prev[["x", "y"]].values, k=1)

    prev = prev.assign(**{f"recurrent_{r}m": dist_prev_to_curr <= r for r in RADII})
    curr = curr.assign(**{f"new_{r}m": dist_curr_to_prev > r for r in RADII})

    prev_agg = prev.groupby("sigungu_cd").agg(
        prev_infected_sites=("site_key", "size"),
        **{f"recurrent_sites_{r}m": (f"recurrent_{r}m", "sum") for r in RADII},
    ).reindex(FULL_SIGUNGU, fill_value=0)

    curr_agg = curr.groupby("sigungu_cd").agg(
        current_infected_sites=("site_key", "size"),
        **{f"new_sites_{r}m": (f"new_{r}m", "sum") for r in RADII},
    ).reindex(FULL_SIGUNGU, fill_value=0)

    merged = prev_agg.join(curr_agg, how="outer").reset_index().rename(columns={"index": "sigungu_cd"})
    merged["year"] = t

    for r in RADII:
        rec_col = f"recurrent_sites_{r}m"
        rate_col = f"recurrence_rate_{r}m"
        merged[rate_col] = np.where(
            merged["prev_infected_sites"] > 0,
            merged[rec_col] / merged["prev_infected_sites"],
            np.nan,
        )
        new_col = f"new_sites_{r}m"
        share_col = f"new_site_share_{r}m"
        merged[share_col] = np.where(
            merged["current_infected_sites"] > 0,
            merged[new_col] / merged["current_infected_sites"],
            np.nan,
        )

    all_rows.extend(merged.to_dict("records"))

recurrence_panel = pd.DataFrame(all_rows)
recurrence_panel["year"] = recurrence_panel["year"].astype(str)

os.makedirs("processed", exist_ok=True)
recurrence_panel.to_parquet("processed/recurrence_panel_full_radii.parquet", index=False)

# ---- consistency 체크: current_infected_sites(t) == prev_infected_sites(t+1) ----
chk = recurrence_panel.pivot_table(index=["sigungu_cd"], columns="year", values="current_infected_sites")
check_rows = []
for t in YEARS[:-1]:
    cur_t = recurrence_panel.loc[recurrence_panel["year"] == str(t), ["sigungu_cd", "current_infected_sites"]].set_index("sigungu_cd")["current_infected_sites"]
    prev_t1 = recurrence_panel.loc[recurrence_panel["year"] == str(t + 1), ["sigungu_cd", "prev_infected_sites"]].set_index("sigungu_cd")["prev_infected_sites"]
    diff = (cur_t - prev_t1).abs()
    mismatch = (diff > 0).sum()
    check_rows.append([t, t + 1, mismatch])
consistency_df = pd.DataFrame(check_rows, columns=["year_t", "year_t+1", "불일치_시군구수"])
consistency_df.to_csv("intermediate_recurrence/검증_current_prev_일치성.csv", index=False, encoding="utf-8-sig")
print("\n=== current_infected_sites(t) vs prev_infected_sites(t+1) 일치성 ===")
print(consistency_df.to_string(index=False))

print("\n최종 recurrence_panel shape:", recurrence_panel.shape)
print(recurrence_panel.head(10).to_string(index=False))
