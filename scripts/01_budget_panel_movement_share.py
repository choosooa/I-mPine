# -*- coding: utf-8 -*-
"""
목표 1,2: movement_share_direct 제거, movement_share_included_budget 생성
입력: data/CH2/3. 지자체/intermediate/CH2_지자체대응역량_최종패널.csv (기존 25개 변수, 원본 미변경)
출력: processed/budget_panel_step1.parquet (24+1=25개 변수, movement_share_direct -> movement_share_included_budget 교체)

변수명 규칙: 분모를 이름에 명시해 movement_share_related(분모가 무엇인지 불명확)와
혼동되지 않도록 함.

  movement_share_included_budget = movement_local_budget / included_local_budget
      (지자체 대응역량 분석에 포함된 전체 대응예산(자원투입+예찰진단+이동통제) 대비
       이동통제 비중) *** 핵심 지수 후보 (최종 EDA/모델링에 사용) ***

  movement_share_broad_budget    = movement_local_budget / broad_local_budget (기존 movement_share_related)
      (사업명이 "B_산림병해충포괄"로 분류된 예산 대비 이동통제 비중. direct_local_budget(A_재선충직접)와는
       별개의 분모이며 direct+broad 합이 아님) *** 진단/보조용 — 분모가 사업 분류 특성에 따라
       달라져 시군구간 비교가 왜곡될 수 있으므로 최종 지수 변수로 사용하지 않음. 사업 분류 교차검증
       등 진단 목적에 한해 참고 ***
"""
import pandas as pd
import numpy as np

SRC = "data/CH2/3. 지자체/intermediate/CH2_지자체대응역량_최종패널.csv"
OUT = "processed/budget_panel_step1.parquet"
VALID_OUT = "intermediate_recurrence/검증_movement_share.csv"

df = pd.read_csv(SRC, dtype={"year": str, "sigungu_cd": str})
n_before = df.shape[1]
assert "movement_share_direct" in df.columns, "movement_share_direct 컬럼이 없습니다"
assert "movement_share_related" in df.columns, "movement_share_related 컬럼이 없습니다"

# 1) movement_share_direct 제거
df = df.drop(columns=["movement_share_direct"])

# 1-1) movement_share_related -> movement_share_broad_budget (분모를 이름에 명시)
df = df.rename(columns={"movement_share_related": "movement_share_broad_budget"})

# 2) movement_share_included_budget 생성
#    - budget_observed == 0 -> NA
#    - included_local_budget == 0 또는 결측 -> NA
#    - movement_local_budget 결측 -> NA
movement_share = df["movement_local_budget"] / df["included_local_budget"]
mask_na = (
    (df["budget_observed"] == 0)
    | (df["included_local_budget"].isna())
    | (df["included_local_budget"] == 0)
    | (df["movement_local_budget"].isna())
)
movement_share = movement_share.mask(mask_na, np.nan)
df["movement_share_included_budget"] = movement_share

n_after = df.shape[1]

# 검증
valid = movement_share.dropna()
out_of_range = ((valid < 0) | (valid > 1)).sum()

report = pd.DataFrame(
    [
        ["변수수_변경전", n_before, ""],
        ["변수수_변경후", n_after, "동일해야 함(25->25, direct 제거+share 추가)"],
        ["movement_share_direct_제거여부", "movement_share_direct" not in df.columns, ""],
        ["movement_share_related_rename_broad_budget_여부", "movement_share_broad_budget" in df.columns, ""],
        ["movement_share_included_budget_생성여부", "movement_share_included_budget" in df.columns, ""],
        ["movement_share_included_budget_결측행수", movement_share.isna().sum(), ""],
        ["movement_share_included_budget_유효행수", valid.shape[0], ""],
        ["movement_share_included_budget_최소값", valid.min() if len(valid) else np.nan, ""],
        ["movement_share_included_budget_최대값", valid.max() if len(valid) else np.nan, ""],
        ["movement_share_included_budget_범위이탈행수", out_of_range, "0이어야 함"],
        ["budget_observed0_행수_movement_share_included_budget_NA", ((df["budget_observed"] == 0) & (movement_share.isna())).sum(), "전부 NA여야 함"],
    ],
    columns=["항목", "값", "비고"],
)

df.to_parquet(OUT, index=False)
report.to_csv(VALID_OUT, index=False, encoding="utf-8-sig")

print(report.to_string(index=False))
print("저장 완료:", OUT)
