# -*- coding: utf-8 -*-
"""
최종 검증표 및 100/300/500m 민감도 분석표 저장
"""
import pandas as pd
import numpy as np

FINAL_PATH = "data/CH2/CH2_지자체대응역량_재발생률포함_최종패널.csv"
ORIG_PATH = "data/CH2/3. 지자체/intermediate/CH2_지자체대응역량_최종패널.csv"

final = pd.read_csv(FINAL_PATH, dtype={"year": str, "sigungu_cd": str})
orig = pd.read_csv(ORIG_PATH, dtype={"year": str, "sigungu_cd": str})
recurrence_full = pd.read_parquet("processed/recurrence_panel_full_radii.parquet")
bjd_yearly = pd.read_csv("intermediate_recurrence/검증_법정동코드_연도별매칭률.csv")

# ---- 변수 역할 정의 (핵심 지수 후보 vs 진단/보조용) ----
CORE_INDEX_CANDIDATES = {
    "log_resource_budget_per_pine_ha": "핵심 지수 후보 (자원투입)",
    "log_surveillance_budget_per_pine_ha": "핵심 지수 후보 (예찰진단)",
    "surveillance_share": "핵심 지수 후보 (예찰진단 비중)",
    "log_movement_budget_per_pine_ha": "핵심 지수 후보 (이동통제)",
    "movement_share_included_budget": "핵심 지수 후보 (이동통제 비중, 분모=전체대응예산)",
    "recurrence_rate_300m": "핵심 지수 후보 (품질·사후관리)",
    "new_site_share_300m": "핵심 지수 후보 (품질·사후관리)",
}
DIAGNOSTIC_ONLY = {
    "movement_share_broad_budget": "진단/보조용 - 분모(broad_local_budget)가 사업분류 특성에 따라 달라져 "
                                    "시군구간 비교 왜곡 가능. 최종 지수 변수로 사용하지 않음",
    "direct_local_budget": "진단/보조용 - 사업 분류 확인용, 지수 산출에 미사용",
    "pine_area_positive": "진단/보조용 - 면적당 예산 산식 유효성 확인용, 지수 산출에 미사용",
}
role_rows = [[c, CORE_INDEX_CANDIDATES.get(c, DIAGNOSTIC_ONLY.get(c, "식별자/원자료/구성요소"))] for c in final.columns]
role_df = pd.DataFrame(role_rows, columns=["변수", "역할"])
role_df.to_csv("intermediate_recurrence/변수_역할_정의.csv", index=False, encoding="utf-8-sig")

rows = []
rows.append(["최종_행수", len(final)])
rows.append(["최종_변수수", final.shape[1]])
rows.append(["최종_변수수_30개여부", final.shape[1] == 30])
rows.append(["year_sigungu_cd_중복행수", final.duplicated(["year", "sigungu_cd"]).sum()])
rows.append(["기존패널_행수", len(orig)])
rows.append(["기존패널대비_행수변화", len(final) - len(orig)])
rows.append(["movement_share_direct_제거여부", "movement_share_direct" not in final.columns])
rows.append(["movement_share_included_budget_생성여부", "movement_share_included_budget" in final.columns])
rows.append(["movement_share_broad_budget_존재여부(구 movement_share_related)", "movement_share_broad_budget" in final.columns])

ms = final["movement_share_included_budget"].dropna()
rows.append(["movement_share_included_budget_최소값", ms.min()])
rows.append(["movement_share_included_budget_최대값", ms.max()])
rows.append(["movement_share_included_budget_범위이탈행수", ((ms < 0) | (ms > 1)).sum()])

msb = final["movement_share_broad_budget"].dropna()
rows.append(["movement_share_broad_budget_최소값", msb.min()])
rows.append(["movement_share_broad_budget_최대값", msb.max()])
rows.append(["movement_share_broad_budget_범위이탈행수(1초과_구조상_가능)", ((msb < 0) | (msb > 1)).sum()])

for col in ["prev_infected_sites", "current_infected_sites", "recurrent_sites_300m",
            "recurrence_rate_300m", "new_site_share_300m"]:
    rows.append([f"{col}_결측률", final[col].isna().mean()])
    valid = final[col].dropna()
    rows.append([f"{col}_최소값", valid.min() if len(valid) else np.nan])
    rows.append([f"{col}_최대값", valid.max() if len(valid) else np.nan])

rr = final["recurrence_rate_300m"].dropna()
rows.append(["recurrence_rate_300m_범위이탈행수(0~1)", ((rr < 0) | (rr > 1)).sum()])
nss = final["new_site_share_300m"].dropna()
rows.append(["new_site_share_300m_범위이탈행수(0~1)", ((nss < 0) | (nss > 1)).sum()])

cmp_df = final.dropna(subset=["recurrent_sites_300m", "prev_infected_sites"])
rows.append(["recurrent_sites_300m_초과_prev_infected_sites_행수",
             (cmp_df["recurrent_sites_300m"] > cmp_df["prev_infected_sites"]).sum()])

y2016 = final[final["year"] == "2016"]
recur_cols_2016 = ["prev_infected_sites", "recurrent_sites_300m", "recurrence_rate_300m", "new_site_share_300m"]
rows.append(["2016년_재발생변수_전체NA여부", bool(y2016[recur_cols_2016].isna().all().all())])

# current_infected_sites(t) vs prev_infected_sites(t+1) 일치성 (전체 재계산 재확인)
mismatch_total = 0
for t in range(2016, 2023):
    cur_t = recurrence_full.loc[recurrence_full["year"] == str(t), ["sigungu_cd", "current_infected_sites"]].set_index("sigungu_cd")["current_infected_sites"]
    prev_t1 = recurrence_full.loc[recurrence_full["year"] == str(t + 1), ["sigungu_cd", "prev_infected_sites"]].set_index("sigungu_cd")["prev_infected_sites"]
    mismatch_total += int((cur_t - prev_t1).abs().gt(0).sum())
rows.append(["current_prev_일치성_불일치행수_전체합", mismatch_total])

overall_matched_rate = bjd_yearly["matched_rows"].sum() / (bjd_yearly["total_rows"].sum() - bjd_yearly["null_placeholder_rows"].sum())
rows.append(["법정동코드_기준표_전체매칭률", overall_matched_rate])

ch2_sigungu = set(orig["sigungu_cd"].unique())
final_sigungu = set(final["sigungu_cd"].unique())
rows.append(["기존CH2패널_sigungu_cd_매칭률", len(final_sigungu & ch2_sigungu) / len(ch2_sigungu)])

# ---- 전기간 감염목 확정 발생지 0건 시군구 수 (정의: 2016~2023 전 연도 current_infected_sites==0) ----
# 주의: 이전 보고에서 사용한 68은 '원본 발생행(감염목구분 무관) 존재 여부' 기준이었고,
# 최종패널의 current_infected_sites는 감염목 확정 건만 집계하므로 정의가 다름 -> 83이 정확한 값.
zero_all_years = final.groupby("sigungu_cd")["current_infected_sites"].apply(lambda s: (s == 0).all())
rows.append(["전기간_감염목확정발생지_0건_시군구수(정의:current_infected_sites 8개년 모두 0)", int(zero_all_years.sum())])

report = pd.DataFrame(rows, columns=["항목", "값"])
report.to_csv("intermediate_recurrence/최종검증표.csv", index=False, encoding="utf-8-sig")

# ---- 100/300/500m 민감도 분석표 ----
sens_rows = []
for r in [100, 300, 500]:
    rate_col = f"recurrence_rate_{r}m"
    share_col = f"new_site_share_{r}m"
    rr_ = recurrence_full[rate_col].dropna()
    ss_ = recurrence_full[share_col].dropna()
    sens_rows.append([r, "recurrence_rate",
                      recurrence_full[rate_col].isna().mean(),
                      (rr_ == 0).mean() if len(rr_) else np.nan,
                      rr_.mean() if len(rr_) else np.nan,
                      rr_.median() if len(rr_) else np.nan,
                      rr_.var() if len(rr_) else np.nan])
    sens_rows.append([r, "new_site_share",
                      recurrence_full[share_col].isna().mean(),
                      (ss_ == 0).mean() if len(ss_) else np.nan,
                      ss_.mean() if len(ss_) else np.nan,
                      ss_.median() if len(ss_) else np.nan,
                      ss_.var() if len(ss_) else np.nan])
sens_df = pd.DataFrame(sens_rows, columns=["반경", "변수", "결측률", "0비율", "평균", "중앙값", "분산"])
sens_df.to_csv("intermediate_recurrence/민감도분석_반경별_기술통계.csv", index=False, encoding="utf-8-sig")

# 반경간 상관계수 (같은 연도 시군구 기준)
corr_input = recurrence_full[["recurrence_rate_100m", "recurrence_rate_300m", "recurrence_rate_500m"]].dropna()
corr_matrix = corr_input.corr()
corr_matrix.to_csv("intermediate_recurrence/민감도분석_반경간_상관계수.csv", encoding="utf-8-sig")

# 연도별 분포(반경별)
year_dist_rows = []
for r in [100, 300, 500]:
    g = recurrence_full.groupby("year")[f"recurrence_rate_{r}m"].agg(["count", "mean", "median"])
    g["radius"] = r
    year_dist_rows.append(g.reset_index())
year_dist_df = pd.concat(year_dist_rows, ignore_index=True)
year_dist_df.to_csv("intermediate_recurrence/민감도분석_연도별_반경별_recurrence_rate.csv", index=False, encoding="utf-8-sig")

print(report.to_string(index=False))
print("\n=== 민감도 분석(반경별 기술통계) ===")
print(sens_df.to_string(index=False))
print("\n=== 반경간 상관계수 ===")
print(corr_matrix.to_string())
