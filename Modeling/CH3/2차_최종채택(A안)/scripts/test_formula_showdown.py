# -*- coding: utf-8 -*-
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, rankdata

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")

def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    prefix = f'window.{varname} = '
    i = text.find(prefix)
    return json.loads(text[i+len(prefix):].rstrip().rstrip(';'))

ch2 = load_js(ROOT / "ch2/data.js", "CH2_DATA")
ch3 = load_js(ROOT / "ch3/data.js", "CH3_DATA")

sgg2 = {(r['시도명'], r['시군구명']): r for r in ch2['sggIndex']}
sgg3 = {(r['시도명'], r['시군구명']): r for r in ch3['prioritySggList']}

rows = []
for key, r2 in sgg2.items():
    r3 = sgg3.get(key)
    if r3 is None or r3.get('재발위험확률') is None:
        continue
    rows.append({
        'name': key,
        'index_main': r2['index_main'],
        '위험지수': r2['위험지수'],
        '배분갭': r2['배분갭'],
        '재발': r3['재발위험확률'],
    })

n = len(rows)
print(f"n = {n}")

index_main = np.array([r['index_main'] for r in rows])
risk3 = np.array([r['위험지수'] for r in rows])       # 역량 제외 3도메인 위험지수 (docx RiskPct 기반)
gap = np.array([r['배분갭'] for r in rows])
recur = np.array([r['재발'] for r in rows])
names = [r['name'] for r in rows]

def z(a):
    return (a - a.mean()) / a.std(ddof=0)

def pct(a):
    return rankdata(a, method='average') / len(a)

RiskPct = pct(risk3)
UnderfundPct = pct(-gap)
RecurPct = pct(recur)

rng = np.random.default_rng(42)
noise = rng.permutation(recur)  # 같은 분포, 무작위 순서로 섞은 노이즈

formulas = {
    'A. 현행 (index_main - 배분갭)': index_main - gap,
    'B. 계획서 (0.6*RiskPct + 0.4*UnderfundPct)': 0.6*RiskPct + 0.4*UnderfundPct,
    'C. 검증보고서 전체 (0.5z(index_main)+0.5z(재발)+0.15z(-갭))': 0.5*z(index_main) + 0.5*z(recur) + 0.15*z(-gap),
    'C2. C에서 재발확률 항 제거 (0.5z(index_main)+0.15z(-갭))': 0.5*z(index_main) + 0.15*z(-gap),
    'C3. C의 재발확률 자리에 랜덤노이즈': 0.5*z(index_main) + 0.5*z(noise) + 0.15*z(-gap),
    'D. 계획서+재발 절충 (0.5RiskPct+0.3UnderfundPct+0.2RecurPct)': 0.5*RiskPct + 0.3*UnderfundPct + 0.2*RecurPct,
    'E. RiskPct 단독': RiskPct,
    'F. 0.6*RiskPct + 0.4*RecurPct': 0.6*RiskPct + 0.4*RecurPct,
}

print(f"\n{'공식':<55s} {'rho(재발)':>10s} {'완도군순위':>8s}")
print("-"*80)
for label, score in formulas.items():
    rho, p = spearmanr(score, recur)
    order = np.argsort(-score)
    rank_of = {names[i]: r+1 for r, i in enumerate(order)}
    wando_rank = rank_of[[k for k in names if k[1]=='완도군'][0]]
    print(f"{label:<55s} {rho:>+10.4f} {wando_rank:>8d}")

print(f"\n(참고) n={n}, C3의 노이즈는 recur를 무작위 순서 재배치한 것(같은 분포, 순서만 다름)")
