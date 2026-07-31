# -*- coding: utf-8 -*-
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")

def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    for prefix in [f'window.{varname} = ', f'const {varname} = ']:
        i = text.find(prefix)
        if i >= 0:
            obj, end = json.JSONDecoder().raw_decode(text[i+len(prefix):])
            return obj
    raise ValueError

ch2 = load_js(ROOT / "ch2/data.js", "CH2_DATA")
ch3 = load_js(ROOT / "ch3/data.js", "CH3_DATA")

sgg3 = {(r['시도명'], r['시군구명']): r for r in ch3['prioritySggList']}

rows = []
for r in ch2['sggIndex']:
    key = (r['시도명'], r['시군구명'])
    r3 = sgg3.get(key)
    if r3 is None or r3.get('재발위험확률') is None:
        continue
    rows.append({
        'name': key,
        'dom_노출도': r['dom_노출도'],
        'dom_기후위험도': r['dom_기후위험도'],
        'dom_인위적확산': r['dom_인위적확산'],
        '재발': r3['재발위험확률'],
    })

names = [r['name'] for r in rows]

def pct(a):
    return rankdata(a, method='average') / len(a)

# 옵션 B (현행 유지, 이름만 변경) -- 기존 위험지수 그대로
risk_B = np.array([(r['dom_노출도'] + r['dom_기후위험도'] + r['dom_인위적확산'])/3 for r in rows])
# 옵션 A (부호 +1로 반전)
risk_A = np.array([(r['dom_노출도'] + r['dom_기후위험도'] - r['dom_인위적확산'])/3 for r in rows])
recur = np.array([r['재발'] for r in rows])

RiskPct_B = pct(risk_B)
RiskPct_A = pct(risk_A)

def wando_rank(score):
    order = np.argsort(-score)
    rank = {names[i]: r+1 for r, i in enumerate(order)}
    return rank[[k for k in names if k[1]=='완도군'][0]]

rho_B, _ = spearmanr(RiskPct_B, recur)
rho_A, _ = spearmanr(RiskPct_A, recur)

print(f"n = {len(rows)}")
print(f"\n[옵션 B: 부호 유지, 이름만 변경 -- 위험지수 수치 동일]")
print(f"  Spearman(RiskPct_B, 재발확률) = {rho_B:.4f}")
print(f"  완도군 순위 = {wando_rank(RiskPct_B)} / {len(rows)}")

print(f"\n[옵션 A: 인위적확산 부호 +1로 반전]")
print(f"  Spearman(RiskPct_A, 재발확률) = {rho_A:.4f}")
print(f"  완도군 순위 = {wando_rank(RiskPct_A)} / {len(rows)}")

print(f"\n=== 옵션 A 적용시 TOP10 ===")
order_A = np.argsort(-RiskPct_A)
for rank, i in enumerate(order_A[:10], 1):
    print(f"  {rank:2d}. {names[i][0][:4]} {names[i][1]:8s}  RiskPct_A={RiskPct_A[i]:.3f}  재발={recur[i]:.3f}")

# 추가: log_피해밀도(실제 피해량)와의 상관도 비교 -- "지수 성능" 원 주장 확인용
dmg = np.array([r.get('log_피해밀도') for r in ch2['sggIndex'] if (r['시도명'], r['시군구명']) in names] if False else None)
