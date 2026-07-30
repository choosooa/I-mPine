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
    raise ValueError("not found: " + varname)

ch1 = load_js(ROOT / "ch1/data.js", "CH1_DATA")
ch2 = load_js(ROOT / "ch2/data.js", "CH2_DATA")

burden = {(r['시도명'], r['시군구명']): r for r in ch1['sggBurden']}
sgg2 = {(r['시도명'], r['시군구명']): r for r in ch2['sggIndex']}

def pct(a):
    return rankdata(a, method='average') / len(a)

rows = []
for key, r2 in sgg2.items():
    b = burden.get(key)
    rows.append({
        'name': key,
        '위험지수': r2['위험지수'],
        'log_피해밀도': r2.get('log_피해밀도'),
        '누적피해고사목': b['누적피해고사목'] if b else None,
        '반복관측률': b['반복관측격자비율(%)'] if b else None,
    })

risk = np.array([r['위험지수'] for r in rows])
RiskPct = pct(risk)
names = [r['name'] for r in rows]
order = np.argsort(-RiskPct)
rank_of = {names[i]: r+1 for r, i in enumerate(order)}

print(f"전체 n = {len(rows)}")
for target_town in ['울주군', '구미시', '광주시', '완도군']:
    matches = [k for k in names if k[1] == target_town]
    for m in matches:
        print(f"  {m}: RiskPct순위={rank_of[m]}")

# 로그피해밀도 상관 (CH2 sample, n=222)
dmg = np.array([r['log_피해밀도'] for r in rows])
mask_dmg = ~np.isnan(dmg.astype(float))
rho_dmg, p_dmg = spearmanr(RiskPct[mask_dmg], dmg[mask_dmg])
print(f"\nSpearman(RiskPct, log_피해밀도) = {rho_dmg:.4f}  n={mask_dmg.sum()}  (문서 주장: +0.187)")

# 누적피해고사목, 반복관측률 (CH1 sggBurden 매칭, n<=180)
cum = np.array([r['누적피해고사목'] if r['누적피해고사목'] is not None else np.nan for r in rows], dtype=float)
rep = np.array([r['반복관측률'] if r['반복관측률'] is not None else np.nan for r in rows], dtype=float)

mask_cum = ~np.isnan(cum)
rho_cum, p_cum = spearmanr(RiskPct[mask_cum], cum[mask_cum])
print(f"Spearman(RiskPct, 누적피해고사목) = {rho_cum:.4f}  n={mask_cum.sum()}  (문서 주장: +0.157, log 여부 불명)")

mask_rep = ~np.isnan(rep)
rho_rep, p_rep = spearmanr(RiskPct[mask_rep], rep[mask_rep])
print(f"Spearman(RiskPct, 반복관측률) = {rho_rep:.4f}  n={mask_rep.sum()}  (문서 주장: +0.050)")

# log 누적피해고사목 (0인 곳 있으므로 log1p)
logcum = np.log1p(cum)
rho_logcum, _ = spearmanr(RiskPct[mask_cum], logcum[mask_cum])
print(f"Spearman(RiskPct, log1p(누적피해고사목)) = {rho_logcum:.4f}  (참고용)")

# TOP 누적피해 지역들의 RiskPct 순위 확인
print(f"\n=== 누적피해고사목 TOP10 지역의 RiskPct 순위 ===")
cum_order = np.argsort(-np.nan_to_num(cum, nan=-1))
for i in cum_order[:10]:
    if not np.isnan(cum[i]):
        print(f"  {names[i][0][:4]} {names[i][1]:8s}  누적피해={cum[i]:>10.0f}  RiskPct순위={rank_of[names[i]]:>4d}/{len(rows)}")
