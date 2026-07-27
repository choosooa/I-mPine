# -*- coding: utf-8 -*-
"""
예산패널(25개, movement_share_direct 제거 + movement_share_included_budget 추가,
        movement_share_related -> movement_share_broad_budget 개명 반영) +
재발생 변수(300m 5개) 병합 -> 최종 30개 변수 패널
- key: year, sigungu_cd
- 검증용 보조열(법정동명, 폐지여부, 코드매칭상태, 좌표계검증값 등)은 최종 패널에 포함하지 않음
- 기존 파일 덮어쓰지 않고 새 파일로 저장
"""
import pandas as pd
import numpy as np

budget = pd.read_parquet("processed/budget_panel_step1.parquet")  # 25개 변수
recurrence_full = pd.read_parquet("processed/recurrence_panel_full_radii.parquet")

FINAL_RECURRENCE_COLS = ["year", "sigungu_cd", "prev_infected_sites", "current_infected_sites",
                          "recurrent_sites_300m", "recurrence_rate_300m", "new_site_share_300m"]
recurrence_300 = recurrence_full[FINAL_RECURRENCE_COLS].copy()

assert budget.shape[1] == 25, f"예산패널 변수수 이상: {budget.shape[1]}"

final_panel = budget.merge(recurrence_300, on=["year", "sigungu_cd"], how="left")

dup = final_panel.duplicated(["year", "sigungu_cd"]).sum()
assert dup == 0, f"key 중복 발생: {dup}"
assert final_panel.shape[1] == 30, f"최종 변수수 이상: {final_panel.shape[1]}"
assert final_panel.shape[0] == budget.shape[0], "행수 변화 발생 (병합으로 행이 늘거나 줄면 안됨)"

OUT_PATH = "data/CH2/CH2_지자체대응역량_재발생률포함_최종패널.csv"
final_panel.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("최종 패널 shape:", final_panel.shape)
print("컬럼(30개):", list(final_panel.columns))
print("저장 위치:", OUT_PATH)
