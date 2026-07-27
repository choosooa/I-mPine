# -*- coding: utf-8 -*-
"""
연도별 고유 감염발생지(site) 생성 및 parquet 캐싱
- 감염목구분 == '감염목' 필터
- 법정동코드 null00/10자리 아닌 값(placeholder) 제외 -> sigungu_cd 없는 행은 별도 관리
- sigungu_cd = 법정동코드[:5]
- 중복 제거 키: 국가지점번호(있으면) 우선, 없으면 좌표쌍(X_Y 문자열)
  근거: 검증 결과 국가지점번호 결측률 0.03%, 형식일치율 98.9%. 좌표의 공간적 배열(시도별
        상대위치)과 서울-부산 간 계산거리(318.7km, 실제 약 325km, 오차 1.9%)를 비교한 결과
        좌표가 미터 기반 거리 계산에 적합할 가능성이 높다고 판단함(별도 CRS 메타데이터로
        확정한 것은 아님). 같은 코드 내 좌표가 100% 일치하지는 않지만(74.6%), 내부거리
        분포 검증(중앙값/90·95퍼센타일/초과비율, 검증_국가지점번호_내부거리분포.csv)에서도
        대부분 근접 범위에 머무는 것으로 나타나 GPS 측정오차 수준으로 판단.
        -> 국가지점번호를 '발생지' 단위 dedup 키로 사용 (그루/개체 단위가 아님)
- site 대표좌표 = 그룹 평균(X,Y)
- 이상치 분리: 국가지점번호 내부거리 분포 검증(검증_국가지점번호_내부거리분포.csv)에서 10m 초과
  비율은 0.049%였지만 그 초과분이 대부분 300m도 훌쩍 넘는 극단치(코드 오기재로 추정)였음.
  판정 기준은 centroid(평균) 거리가 아니라 그룹 내 두 점 사이 '최대 쌍거리(지름)' > 300m로 함
  (centroid 거리 300m씩인 두 점은 서로 최대 600m 떨어질 수 있어 지름 기준이 더 보수적/정확함).
  n_obs가 큰 그룹은 전수 쌍거리 계산이 비싸므로 ConvexHull 정점 사이의 최대거리로 계산
  (2D 점집합의 지름을 이루는 두 점은 항상 convex hull 위에 있으므로 결과는 동일, 계산량만 절감).
  이상치로 판정된 국가지점번호는 위치 신뢰도가 없다고 보고 좌표기반 fallback key로 재할당
  (사실상 국가지점번호 결측과 동일하게 처리) -> 재집계.
  분리된 코드는 검증_국가지점번호_300m초과_재할당.csv에 기록.
- 출력: processed/infected_sites_{year}.parquet
        columns: site_key, x, y, sigungu_cd, year, n_obs
"""
import pandas as pd
import numpy as np
import os
from scipy.spatial import ConvexHull, QhullError
from scipy.spatial.distance import pdist

RAW_DIR = "data/CH1/산림청_산림병해충방제 병해충발생관리정보_20250902"
YEARS = list(range(2016, 2024))
USECOLS = ["지역X좌표", "지역Y좌표", "국가지점번호", "법정동코드", "감염목구분"]
DTYPE = {"국가지점번호": str, "법정동코드": str, "감염목구분": str}
CHUNKSIZE = 500_000
os.makedirs("processed", exist_ok=True)

OUTLIER_RADIUS_M = 300
HULL_THRESHOLD_N = 50  # 이 이상이면 ConvexHull 정점만으로 지름 계산(전수 pdist 대신)


def max_pairwise_distance(xy):
    """2D 점집합의 최대 쌍거리(지름). n<=1이면 0. 큰 그룹은 ConvexHull로 축약 후 pdist."""
    n = len(xy)
    if n <= 1:
        return 0.0
    if n == 2:
        d = xy[0] - xy[1]
        return float(np.hypot(d[0], d[1]))
    pts = xy
    if n > HULL_THRESHOLD_N:
        try:
            hull = ConvexHull(xy)
            pts = xy[hull.vertices]
        except QhullError:
            pts = xy  # 공선(collinear) 등으로 hull 계산 불가 -> 전수 pdist로 폴백
    if len(pts) < 2:
        return 0.0
    return float(pdist(pts).max())

dedup_report = []
sigungu_dedup_report = []
excluded_no_sigungu_report = []
outlier_reassign_report = []

for year in YEARS:
    path = os.path.join(RAW_DIR, f"병해충발생정보관리_{year}.csv")
    reader = pd.read_csv(path, encoding="cp949", usecols=USECOLS, dtype=DTYPE,
                         chunksize=CHUNKSIZE, low_memory=False)
    parts = []
    n_infected_total = 0
    n_excluded_no_sigungu = 0
    for chunk in reader:
        infected = chunk[chunk["감염목구분"] == "감염목"].copy()
        n_infected_total += len(infected)
        bjd = infected["법정동코드"]
        valid_sgg = bjd.notna() & (bjd.str.len() == 10) & (bjd != "null00")
        n_excluded_no_sigungu += int((~valid_sgg).sum())
        infected = infected[valid_sgg]
        if len(infected) == 0:
            continue
        infected["x"] = pd.to_numeric(infected["지역X좌표"], errors="coerce")
        infected["y"] = pd.to_numeric(infected["지역Y좌표"], errors="coerce")
        infected["sigungu_cd"] = infected["법정동코드"].str.slice(0, 5)
        infected["site_key"] = np.where(
            infected["국가지점번호"].notna(),
            infected["국가지점번호"],
            "XY_" + infected["x"].round(1).astype(str) + "_" + infected["y"].round(1).astype(str),
        )
        parts.append(infected[["site_key", "x", "y", "sigungu_cd"]])

    excluded_no_sigungu_report.append([year, n_infected_total, n_excluded_no_sigungu])

    if not parts:
        sites = pd.DataFrame(columns=["site_key", "x", "y", "sigungu_cd", "year", "n_obs"])
        n_unique = 0
        n_valid_for_dedup = 0
    else:
        year_df = pd.concat(parts, ignore_index=True)
        n_valid_for_dedup = len(year_df)

        # ---- 그룹 내 최대 쌍거리(지름) 계산 (n_obs>=2인 국가지점번호 그룹만 대상) ----
        is_gukji_key = ~year_df["site_key"].str.startswith("XY_")
        gukji_df = year_df.loc[is_gukji_key]
        group_sizes = gukji_df.groupby("site_key").size()
        multi_keys = group_sizes[group_sizes >= 2].index

        outlier_keys = set()
        outlier_detail_rows = []
        if len(multi_keys) > 0:
            multi_df = gukji_df[gukji_df["site_key"].isin(multi_keys)]
            for key, g in multi_df.groupby("site_key"):
                xy = g[["x", "y"]].to_numpy()
                d = max_pairwise_distance(xy)
                if d > OUTLIER_RADIUS_M:
                    outlier_keys.add(key)
                    outlier_detail_rows.append([key, len(g), d])

        is_outlier_code = year_df["site_key"].isin(outlier_keys)
        n_outlier_codes = len(outlier_keys)
        n_outlier_rows = int(is_outlier_code.sum())
        if outlier_detail_rows:
            outlier_detail = pd.DataFrame(outlier_detail_rows, columns=["site_key", "n_obs", "max_dist_m"])
            outlier_detail["year"] = year
            outlier_reassign_report.append(outlier_detail)

        # ---- 이상치 코드는 좌표기반 fallback key로 재할당 (국가지점번호 결측과 동일 취급) ----
        year_df.loc[is_outlier_code, "site_key"] = (
            "XY_" + year_df.loc[is_outlier_code, "x"].round(1).astype(str)
            + "_" + year_df.loc[is_outlier_code, "y"].round(1).astype(str)
        )

        grouped = year_df.groupby("site_key").agg(
            x=("x", "mean"), y=("y", "mean"),
            sigungu_cd=("sigungu_cd", lambda s: s.mode().iloc[0]),
            n_obs=("site_key", "size"),
        ).reset_index()
        grouped["year"] = year
        sites = grouped
        n_unique = len(sites)

        print(f"        -> 300m초과 이상치코드 {n_outlier_codes}개({n_outlier_rows}행) 좌표기반키로 재할당")

    sites.to_parquet(f"processed/infected_sites_{year}.parquet", index=False)

    dedup_report.append([year, n_infected_total, n_excluded_no_sigungu, n_valid_for_dedup, n_unique,
                          n_valid_for_dedup - n_unique,
                          (n_valid_for_dedup - n_unique) / n_valid_for_dedup if n_valid_for_dedup else np.nan])

    # 시군구별 중복제거율 (변화 큰 지역 확인용)
    if n_unique:
        sgg_before = sites.groupby("sigungu_cd")["n_obs"].sum()  # 중복제거 전 총 관측수(시군구별)
        sgg_after = sites.groupby("sigungu_cd").size()           # 중복제거 후 고유 site수
        sgg_stat = pd.DataFrame({"before": sgg_before, "after": sgg_after})
        sgg_stat["removed"] = sgg_stat["before"] - sgg_stat["after"]
        sgg_stat["removed_rate"] = sgg_stat["removed"] / sgg_stat["before"]
        sgg_stat["year"] = year
        sigungu_dedup_report.append(sgg_stat.reset_index())

    print(f"[{year}] 감염목행수={n_infected_total} sigungu결측제외후={n_valid_for_dedup} "
          f"고유발생지={n_unique} 제거중복={n_valid_for_dedup - n_unique}")

dedup_df = pd.DataFrame(dedup_report, columns=["year", "감염목_전체행수", "sigungu결측_제외행수",
                                                 "dedup대상행수", "고유발생지수", "제거된중복수", "중복제거율"])
dedup_df.to_csv("intermediate_recurrence/검증_중복제거_연도별.csv", index=False, encoding="utf-8-sig")

excluded_df = pd.DataFrame(excluded_no_sigungu_report, columns=["year", "감염목_전체행수", "sigungu결측_제외행수"])
excluded_df.to_csv("intermediate_recurrence/검증_sigungu결측_제외행수_연도별.csv", index=False, encoding="utf-8-sig")

if sigungu_dedup_report:
    sgg_all = pd.concat(sigungu_dedup_report, ignore_index=True)
    sgg_all.to_csv("intermediate_recurrence/검증_시군구별_중복제거_연도별.csv", index=False, encoding="utf-8-sig")
    top_change = sgg_all.sort_values("removed_rate", ascending=False).head(20)
    top_change.to_csv("intermediate_recurrence/검증_시군구별_중복제거율_상위20.csv", index=False, encoding="utf-8-sig")

print("\n=== 연도별 중복제거 요약 ===")
print(dedup_df.to_string(index=False))

if outlier_reassign_report:
    outlier_df = pd.concat(outlier_reassign_report, ignore_index=True).sort_values("max_dist_m", ascending=False)
    outlier_df.to_csv("intermediate_recurrence/검증_국가지점번호_300m초과_재할당.csv", index=False, encoding="utf-8-sig")
    print(f"\n300m 초과 이상치 코드 총 {len(outlier_df)}건(연도 합계) 좌표기반 키로 재할당, "
          f"검증_국가지점번호_300m초과_재할당.csv 저장")
else:
    print("\n300m 초과 이상치 코드 없음")
