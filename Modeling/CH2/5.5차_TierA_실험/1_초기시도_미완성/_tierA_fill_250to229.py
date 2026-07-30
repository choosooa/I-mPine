# -*- coding: utf-8 -*-
"""
TierA 도로소나무비율_500m을 229 통합코드 기준으로 완전 적용.
- 분모/분자 각각 합산 후 나눔 (비율 평균 금지): ratio_229 = sum(road_inter_ha) / sum(pine_ha)
- 기준 파일은 2차/최종보정3.csv (기후 메타 3컬럼 포함된 최신 패널)
- 원본은 절대 덮어쓰지 않고 새 파일로 저장
"""
import sys
import numpy as np
import pandas as pd
import pyogrio

sys.stdout.reconfigure(encoding="utf-8")

BASE = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
PANEL_IN = BASE + r"\Modeling\2차\CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv"
PANEL_TIERA_PREV = BASE + r"\Modeling\1차\data\CH2_전체병합패널_5도메인_2016_2023_최종보정_도로TierA반영.csv"
TIERA_RAW = BASE + r"\Modeling\1차\data\도로소나무비율_TierA_104제외_전체8개년.csv"
CROSSWALK = BASE + r"\data\CH2\CH2data\CH2_crosswalk_250to229.csv"
PINE_GPKG = r"C:\Users\SAMSUNG\Downloads\pine_by_sigungu.gpkg"
PANEL_OUT = BASE + r"\Modeling\2차\CH2_전체병합패널_5도메인_2016_2023_최종보정4_도로TierA_229집계.csv"

COL = "도로소나무비율_500m"
COL_REF = COL + "_TierB참고(2023고정,104포함)"
COL_FLAG = COL + "_TierA_통합시집계_flag"

# ---------------------------------------------------------------- 1. 입력 로드
print("[1] pine_ha (250코드, 지오메트리 제외) 로드...", flush=True)
pine = pyogrio.read_dataframe(PINE_GPKG, columns=["sigungu_cd", "pine_ha"], read_geometry=False)
pine["sigungu_cd"] = pine["sigungu_cd"].astype(int)
print(f"    {len(pine)}건 | pine_ha=0 또는 결측: {int((pine['pine_ha'].fillna(0) <= 0).sum())}건", flush=True)

print("[2] TierA 원시 교차면적 로드 (500m만)...", flush=True)
raw = pd.read_csv(TIERA_RAW, encoding="utf-8-sig")
raw = raw[raw["buffer_m"] == 500].copy()
raw["sigungu_cd"] = raw["sigungu_cd"].astype(int)
print(f"    {len(raw)}행 | 단위 {raw['sigungu_cd'].nunique()}개 | 연도 {raw['year'].min()}~{raw['year'].max()}", flush=True)

print("[3] 250to229 크로스워크 로드...", flush=True)
cw = pd.read_csv(CROSSWALK, encoding="utf-8-sig")
c250, c229 = cw.columns[0], cw.columns[1]
cw[c250] = cw[c250].astype(int)
cw[c229] = cw[c229].astype(int)
cw_map = dict(zip(cw[c250], cw[c229]))
n_merge_src = int((cw[c250] != cw[c229]).sum())
n_merge_tgt = cw.loc[cw[c250] != cw[c229], c229].nunique()
print(f"    {len(cw)}행 | 통합대상 세부코드 {n_merge_src}개 -> 통합시 {n_merge_tgt}개", flush=True)

# ---------------------------------------- 4. 229 집계 (분자/분모 각각 합산)
print("[4] 229 집계: sum(road_inter_ha) / sum(pine_ha)...", flush=True)
raw = raw.merge(pine, on="sigungu_cd", how="left")
raw["code229"] = raw["sigungu_cd"].map(cw_map).fillna(raw["sigungu_cd"]).astype(int)

miss_pine = raw["pine_ha"].isna().sum()
if miss_pine:
    print(f"    [경고] pine_ha 결측 {miss_pine}행 -> 집계에서 제외", flush=True)

agg = (raw.groupby(["year", "code229"], as_index=False)
          .agg(road_inter_ha=("road_inter_ha", "sum"),
               pine_ha=("pine_ha", "sum"),
               n_src=("sigungu_cd", "nunique")))
agg[COL] = np.where(agg["pine_ha"] > 0, agg["road_inter_ha"] / agg["pine_ha"], np.nan)
print(f"    집계 결과 {len(agg)}행 | 229단위 {agg['code229'].nunique()}개 "
      f"| 2개이상 구 합산된 단위 {int((agg['n_src'] > 1).sum() / agg['year'].nunique())}개", flush=True)

# ------------------------------------- 5. 기존 TierA 파일과 대조 (215개 검증)
print("[5] 검증: 기존 TierA 파일(215곳)과 값 일치 여부...", flush=True)
prev = pd.read_csv(PANEL_TIERA_PREV, encoding="utf-8-sig")
chk = prev[["시군구코드", "연도", COL]].rename(columns={COL: "prev"}).merge(
    agg[["code229", "year", COL]].rename(columns={"code229": "시군구코드", "year": "연도", COL: "new"}),
    on=["시군구코드", "연도"], how="left")
both = chk.dropna(subset=["prev", "new"])
maxdiff = (both["prev"] - both["new"]).abs().max()
print(f"    기존 비결측 {len(both)}행 최대 절대차 = {maxdiff:.3e} "
      f"({'일치' if maxdiff < 1e-9 else '불일치 - 확인필요'})", flush=True)
if maxdiff >= 1e-9:
    print("    [중단] 기존 값과 재현이 안 됩니다. 저장하지 않고 종료.", flush=True)
    sys.exit(1)

# ------------------------------------------------------------- 6. 패널에 적용
print("[6] 최종보정3.csv 기준으로 적용...", flush=True)
panel = pd.read_csv(PANEL_IN, encoding="utf-8-sig")
print(f"    입력 패널: {panel.shape} | {COL} 결측 {int(panel[COL].isna().sum())}행", flush=True)

# 통합시(2개 이상 구 합산) 코드 집합 -> 플래그용
merged_codes = set(agg.loc[agg["n_src"] > 1, "code229"].unique())

panel[COL_REF] = panel[COL]                     # 기존 TierB 값 감사기록으로 보존
prev_null = panel[COL].isna()

panel = panel.merge(agg[["code229", "year", COL]].rename(
    columns={"code229": "시군구코드", "year": "연도", COL: "_tierA"}),
    on=["시군구코드", "연도"], how="left")
panel[COL] = panel["_tierA"]
panel = panel.drop(columns=["_tierA"])
panel[COL_FLAG] = panel["시군구코드"].isin(merged_codes).astype(int)

# ----------------------------------------------------------------- 7. QA 출력
print("[7] QA", flush=True)
now_null = panel[COL].isna()
print(f"    적용 후 {COL} 결측 = {int(now_null.sum())}행 (기대 24)", flush=True)
print(f"    결측 시군구 = {sorted(panel.loc[now_null, '시군구'].unique().tolist())}", flush=True)
print(f"    통합시 집계 플래그=1 : {int(panel[COL_FLAG].sum())}행 "
      f"({panel.loc[panel[COL_FLAG] == 1, '시군구'].nunique()}개 시군구)", flush=True)
print(f"    플래그=1 행 중 결측 = {int(panel.loc[panel[COL_FLAG] == 1, COL].isna().sum())}행 (기대 0)", flush=True)
print("\n    통합시 11곳 연도별 값:", flush=True)
mg = panel[panel[COL_FLAG] == 1].pivot_table(index="시군구", columns="연도", values=COL)
print(mg.round(4).to_string(), flush=True)
print("\n    연도별 전국평균:", flush=True)
print(panel.groupby("연도")[COL].mean().round(4).to_string(), flush=True)
print(f"\n    전체: mean={panel[COL].mean():.4f} sd={panel[COL].std():.4f} "
      f"min={panel[COL].min():.4f} max={panel[COL].max():.4f}", flush=True)

# ------------------------------------------------------------------ 8. 저장
panel.to_csv(PANEL_OUT, index=False, encoding="utf-8-sig")
print(f"\nSAVED (신규): {PANEL_OUT}", flush=True)
print(f"shape: {panel.shape}", flush=True)
print("원본 3개 파일은 변경하지 않았습니다.", flush=True)
print("ALL DONE", flush=True)
