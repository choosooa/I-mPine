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

def pct(a):
    return rankdata(a, method='average') / len(a)

names = [(r['시도명'], r['시군구명']) for r in ch2['sggIndex']]
risk_B = np.array([(r['dom_노출도'] + r['dom_기후위험도'] + r['dom_인위적확산'])/3 for r in ch2['sggIndex']])
risk_A = np.array([(r['dom_노출도'] + r['dom_기후위험도'] - r['dom_인위적확산'])/3 for r in ch2['sggIndex']])
dmg = np.array([r['log_피해밀도'] for r in ch2['sggIndex']])

RiskPct_B = pct(risk_B)
RiskPct_A = pct(risk_A)

rho_B, _ = spearmanr(RiskPct_B, dmg)
rho_A, _ = spearmanr(RiskPct_A, dmg)
print(f"n = {len(names)}")
print(f"Spearman(RiskPct_B[부호유지], log_피해밀도) = {rho_B:.4f}")
print(f"Spearman(RiskPct_A[부호반전], log_피해밀도) = {rho_A:.4f}")

order_B = np.argsort(-RiskPct_B)
rank_B = {names[i]: r+1 for r, i in enumerate(order_B)}
order_A = np.argsort(-RiskPct_A)
rank_A = {names[i]: r+1 for r, i in enumerate(order_A)}
w = [k for k in names if k[1]=='완도군'][0]
print(f"완도군: B안 순위={rank_B[w]}, A안 순위={rank_A[w]}")
