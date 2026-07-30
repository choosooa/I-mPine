# -*- coding: utf-8 -*-
"""
TierA 도로 교차면적에 연도별 pine_ha 붙이기
- 2016~2019: 2019 임상도 pine_ha
- 2020~2023: 2024 임상도 pine_ha
"""
import os
import pandas as pd
import numpy as np

BASE = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
CKPT_DIR = BASE + r"\Modeling\1차\data\_tierA_checkpoints"
OUT_CSV = BASE + r"\Modeling\1차\data\도로소나무비율_TierA_104제외_전체8개년_연도별임상도.csv"
PINE_2019 = BASE + r"\data\CH2\1. 환경\인위적 확산\자료\임상도\전국임상도\2019_sgg_pine_forest.csv"
PINE_2024 = BASE + r"\data\CH2\1. 환경\인위적 확산\자료\임상도\전국임상도\2024_sgg_pine_forest.csv"

print("[1] 연도별 임상도 로드...", flush=True)
pine19 = pd.read_csv(PINE_2019, encoding='utf-8-sig')[['sigungu_cd', 'pine_ha']].astype({'sigungu_cd': int})
pine24 = pd.read_csv(PINE_2024, encoding='utf-8-sig')[['sigungu_cd', 'pine_ha']].astype({'sigungu_cd': int})
print(f"    2019: {len(pine19)}건")
print(f"    2024: {len(pine24)}건")

print("[2] 체크포인트 로드 및 pine_ha 붙이기...", flush=True)
all_data = []
for year in range(2016, 2024):
    ckpt = pd.read_csv(os.path.join(CKPT_DIR, f'year_{year}.csv'))

    # 연도별 임상도 선택
    pine = pine19 if year <= 2019 else pine24

    # pine_ha 붙이기
    ckpt = ckpt.merge(pine, on='sigungu_cd', how='left')

    # 비율 계산 (분모가 0이거나 결측인 경우 nan)
    ckpt['ratio'] = np.where(ckpt['pine_ha'] > 0,
                             ckpt['road_inter_ha'] / ckpt['pine_ha'],
                             np.nan)

    all_data.append(ckpt)
    print(f"    {year}: {len(ckpt)}행 | ratio 결측 {int(ckpt['ratio'].isna().sum())}개")

print("[3] 통합 및 저장...", flush=True)
final = pd.concat(all_data, ignore_index=True)
final = final[['year', 'sigungu_cd', 'buffer_m', 'road_inter_ha', 'pine_ha', 'ratio']]
final.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
print(f"    저장: {OUT_CSV}")
print(f"    shape: {final.shape}")

print("\n[4] QA", flush=True)
print(f"    500m 버퍼만:")
f500 = final[final['buffer_m'] == 500]
for year in range(2016, 2024):
    yrdata = f500[f500['year'] == year]
    pine_src = '2019' if year <= 2019 else '2024'
    print(f"      {year}: mean={yrdata['ratio'].mean():.4f} | null={int(yrdata['ratio'].isna().sum())} | pine_src={pine_src}")

print("\nALL DONE", flush=True)
