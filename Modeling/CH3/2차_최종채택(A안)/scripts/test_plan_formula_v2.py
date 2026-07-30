# -*- coding: utf-8 -*-
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")

# 1) per-year 위험지수 (역량 제외) — 실제 model1_v4_final.py 산출물
idx = pd.read_csv(ROOT / "Modeling/CH2/4차/구조적취약성지수_v4.csv", encoding='utf-8-sig')
idx = idx[idx['연도'].between(2017, 2022)].copy()

# within-year percentile of 위험지수
idx['RiskPct_year'] = idx.groupby('연도')['위험지수'].rank(pct=True)
risk_town = idx.groupby(['시도','시군구'])['RiskPct_year'].mean().reset_index()
risk_town.columns = ['시도','시군구','RiskPct']

# 2) 배분갭 (town-level, 2017-2022 aggregate) — model1_v4_final.py 산출물
contrib = pd.read_csv(ROOT / "Modeling/CH2/4차/Model1_기여도분해_유형화_v4.csv", encoding='utf-8-sig')
contrib['UnderfundPct'] = contrib['배분갭'].rank(pct=True, ascending=False)  # more negative gap -> higher percentile

merged = risk_town.merge(contrib[['시도','시군구','배분갭','UnderfundPct','축A_위험요인유형']], on=['시도','시군구'])

# 3) 재발위험확률 — ch3/data.js
def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    prefix = f'window.{varname} = '
    idx0 = text.find(prefix)
    json_text = text[idx0+len(prefix):].rstrip().rstrip(';')
    return json.loads(json_text)

ch3 = load_js(ROOT / "ch3/data.js", "CH3_DATA")
recur_map = {(r['시도명'], r['시군구명']): r.get('재발위험확률') for r in ch3['prioritySggList']}
merged['재발위험확률'] = merged.apply(lambda r: recur_map.get((r['시도'], r['시군구'])), axis=1)
merged = merged.dropna(subset=['재발위험확률'])

print(f"매칭된 시군구: {len(merged)}개")

merged['plan_priority'] = 0.6*merged['RiskPct'] + 0.4*merged['UnderfundPct']

rho, p = spearmanr(merged['plan_priority'], merged['재발위험확률'])
print(f"\nSpearman(계획서공식[연도내 백분위 기반], 재발위험확률) = {rho:.4f} (p={p:.4g})")

rho_risk, _ = spearmanr(merged['RiskPct'], merged['위험지수'] if '위험지수' in merged.columns else merged['RiskPct'])
rho_risk_recur, _ = spearmanr(merged['RiskPct'], merged['재발위험확률'])
rho_under_recur, _ = spearmanr(merged['UnderfundPct'], merged['재발위험확률'])
print(f"Spearman(RiskPct 단독, 재발위험확률) = {rho_risk_recur:.4f}")
print(f"Spearman(UnderfundPct 단독, 재발위험확률) = {rho_under_recur:.4f}")

# 완도군 순위
merged_sorted = merged.sort_values('plan_priority', ascending=False).reset_index(drop=True)
wando_rank = merged_sorted[merged_sorted['시군구']=='완도군'].index[0] + 1
print(f"\n완도군 순위: {wando_rank} / {len(merged)}")
print(merged_sorted[merged_sorted['시군구']=='완도군'][['시도','시군구','RiskPct','UnderfundPct','plan_priority','재발위험확률']])

print(f"\n=== TOP15 ===")
print(merged_sorted.head(15)[['시도','시군구','RiskPct','UnderfundPct','plan_priority','재발위험확률']].to_string(index=False))

# 서울 자치구 개수 in TOP30
top30 = merged_sorted.head(30)
seoul_count = (top30['시도']=='서울특별시').sum()
print(f"\nTOP30 중 서울특별시 개수: {seoul_count}")

# Spearman(plan_priority, 위험지수 자체) -- 문서가 주장한 "+0.858"과 비교하기 위해
# 위험지수의 town-level 평균과 비교
risk_avg = idx.groupby(['시도','시군구'])['위험지수'].mean().reset_index()
merged2 = merged.merge(risk_avg, on=['시도','시군구'])
rho_vs_riskindex, _ = spearmanr(merged2['plan_priority'], merged2['위험지수'])
print(f"\nSpearman(계획서공식, 위험지수 자체) = {rho_vs_riskindex:.4f}  (문서 주장: +0.858)")
