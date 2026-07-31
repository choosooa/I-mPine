# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    for prefix in [f'window.{varname} = ']:
        idx = text.find(prefix)
        if idx >= 0:
            json_start = idx + len(prefix)
            break
    else:
        raise ValueError("not found")
    json_text = text[json_start:].rstrip().rstrip(';')
    return json.loads(json_text)

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")
ch2 = load_js(ROOT / "ch2" / "data.js", "CH2_DATA")
ch3 = load_js(ROOT / "ch3" / "data.js", "CH3_DATA")

sgg2 = {(r['시도명'], r['시군구명']): r for r in ch2['sggIndex']}
sgg3 = {(r['시도명'], r['시군구명']): r for r in ch3['prioritySggList']}

rows = []
for key, r2 in sgg2.items():
    r3 = sgg3.get(key)
    if r3 is None or r3.get('재발위험확률') is None:
        continue
    rows.append({
        '시도명': key[0], '시군구명': key[1],
        'dom_노출도': r2['dom_노출도'],
        'dom_기후위험도': r2['dom_기후위험도'],
        'dom_인위적확산': r2['dom_인위적확산'],
        '배분갭': r2['배분갭'],
        'index_main': r2['index_main'],
        '재발위험확률': r3['재발위험확률'],
        '기존_priority': r3['priority_score'],
    })

print(f"매칭된 시군구: {len(rows)}개")

def pct_rank(arr):
    # percentile rank in [0,1], higher value -> higher percentile
    return rankdata(arr, method='average') / len(arr)

risk_raw = np.array([(r['dom_노출도'] + r['dom_기후위험도'] + r['dom_인위적확산'])/3 for r in rows])
gap_raw = np.array([r['배분갭'] for r in rows])
recur = np.array([r['재발위험확률'] for r in rows])
existing_priority = np.array([r['기존_priority'] for r in rows])
index_main = np.array([r['index_main'] for r in rows])

RiskPct = pct_rank(risk_raw)
UnderfundPct = pct_rank(-gap_raw)   # more negative gap (underfunded) -> higher percentile

plan_priority = 0.6*RiskPct + 0.4*UnderfundPct

rho_plan, p_plan = spearmanr(plan_priority, recur)
rho_existing, p_existing = spearmanr(existing_priority, recur)

print(f"\n=== 기존 공식 (index_main - 배분갭) ===")
print(f"Spearman(기존순위, 재발위험확률) = {rho_existing:.4f} (p={p_existing:.4g})")

print(f"\n=== 분석계획서 공식 (0.6*RiskPct + 0.4*UnderfundPct) ===")
print(f"Spearman(계획서순위, 재발위험확률) = {rho_plan:.4f} (p={p_plan:.4g})")

# 완도군 rank check
names = [(r['시도명'], r['시군구명']) for r in rows]
order_plan = np.argsort(-plan_priority)
rank_plan = {names[i]: rank+1 for rank, i in enumerate(order_plan)}
wando_key = [k for k in names if k[1]=='완도군'][0]
print(f"\n완도군 계획서공식 순위: {rank_plan[wando_key]} / {len(rows)}")
print(f"완도군 RiskPct={RiskPct[names.index(wando_key)]:.3f}, UnderfundPct={UnderfundPct[names.index(wando_key)]:.3f}")

# TOP10 by plan formula
print(f"\n=== 계획서공식 TOP10 ===")
for rank, i in enumerate(order_plan[:10], 1):
    print(f"  {rank:2d}. {names[i][0][:4]} {names[i][1]:6s} plan_score={plan_priority[i]:.3f} risk%={RiskPct[i]:.2f} underfund%={UnderfundPct[i]:.2f} 재발={recur[i]:.3f} index_main={index_main[i]:+.3f}")

# RiskPct 자체가 얼마나 재발위험확률과 관련있는지 (인위적확산 도메인 왜곡 영향 확인용)
rho_risk_only, _ = spearmanr(RiskPct, recur)
rho_underfund_only, _ = spearmanr(UnderfundPct, recur)
print(f"\nSpearman(RiskPct 단독, 재발위험확률) = {rho_risk_only:.4f}")
print(f"Spearman(UnderfundPct 단독, 재발위험확률) = {rho_underfund_only:.4f}")

# 인위적확산 제외한 RiskPct (노출도+기후만)도 비교
risk_raw_noindustry = np.array([(r['dom_노출도'] + r['dom_기후위험도'])/2 for r in rows])
RiskPct_noindustry = pct_rank(risk_raw_noindustry)
plan_priority_v2 = 0.6*RiskPct_noindustry + 0.4*UnderfundPct
rho_plan_v2, _ = spearmanr(plan_priority_v2, recur)
print(f"\n(참고) 인위적확산 도메인 제외한 RiskPct로 계산: Spearman = {rho_plan_v2:.4f}")
