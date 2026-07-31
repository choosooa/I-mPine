# -*- coding: utf-8 -*-
"""
옵션 A — 인위적확산 도메인 부호 반전(+1)에 따른 CH2/CH3 하류 지표 전체 재계산.
대상 폴더: Modeling/2차_A안

범위 안내(중요):
  - dom_인위적확산 부호 반전 → index_main, 위험지수, 기여도, 축A_위험요인유형,
    배분갭(위험지수 변경에 따른 OLS 재적합), 축B_배분적정성(qcut 재분할),
    CH3 dominant_domain/recommended_policy/priority_score(RiskPct)/grade
    까지는 결정론적으로 재계산했습니다.
  - Model1의 CRE(Mundlak) 로지스틱 회귀 결과(AUC, between/within 계수)는
    연도별 원본 패널 재적합이 필요한 별도 작업이라 이번 재계산 범위에서 제외했습니다
    (ch2.html의 해당 KPI는 기존 값 그대로 남아있으니 주의).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")
BASE = ROOT / "Modeling" / "2차_A안"

def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    prefix = f'window.{varname} = '
    i = text.find(prefix)
    obj, end = json.JSONDecoder().raw_decode(text[i+len(prefix):])
    return obj

ch2 = load_js(BASE / "ch2" / "data.js", "CH2_DATA")
ch3 = load_js(BASE / "ch3" / "data.js", "CH3_DATA")

# ── 1) 도메인 부호 반전 + 하류 지표 재계산 (ch2) ─────────────────────────
for r in ch2['sggIndex']:
    old = r['dom_인위적확산']
    new = -old
    r['dom_인위적확산'] = new
    r['기여_인위적확산'] = round(0.25 * new, 4)
    r['index_main'] = round(np.mean([r['dom_노출도'], r['dom_기후위험도'], r['dom_지자체역량_역'], new]), 4)
    r['위험지수'] = round(np.mean([r['dom_노출도'], r['dom_기후위험도'], new]), 4)
    diff = r['dom_노출도'] - new
    if diff > 0.5: r['축A_위험요인유형'] = '노출도-우세형'
    elif diff < -0.5: r['축A_위험요인유형'] = '인위적확산-우세형'
    else: r['축A_위험요인유형'] = '복합형'

# 배분갭 재적합: OLS(평균예산_log ~ const + 위험지수_new)
budget = np.array([r['평균예산_log'] for r in ch2['sggIndex']])
risk_new = np.array([r['위험지수'] for r in ch2['sggIndex']])
X = np.column_stack([np.ones(len(risk_new)), risk_new])
beta, *_ = np.linalg.lstsq(X, budget, rcond=None)
pred = X @ beta
resid = budget - pred
ss_res = np.sum(resid**2); ss_tot = np.sum((budget-budget.mean())**2)
r2 = 1 - ss_res/ss_tot
for r, g in zip(ch2['sggIndex'], resid):
    r['배분갭'] = round(float(g), 4)

# 축B 재분할 (qcut 3분위, 기존 방법론 그대로 유지 — 이건 별도 개선과제 ⑧)
gaps = np.array([r['배분갭'] for r in ch2['sggIndex']])
order = np.argsort(gaps)
n = len(gaps)
tertile_labels = np.empty(n, dtype=object)
for rank, idx in enumerate(order):
    frac = rank / n
    tertile_labels[idx] = '부족' if frac < 1/3 else ('적정' if frac < 2/3 else '과다')
for r, lab in zip(ch2['sggIndex'], tertile_labels):
    r['축B_배분적정성'] = lab

print(f"[CH2 재적합] 배분갭 회귀 R²={r2:.4f}, n={n}")
print("축A 유형 분포:", pd.Series([r['축A_위험요인유형'] for r in ch2['sggIndex']]).value_counts().to_dict())
print("축B 분포:", pd.Series([r['축B_배분적정성'] for r in ch2['sggIndex']]).value_counts().to_dict())

# ── 2) CH3 하류 재계산 ───────────────────────────────────────────────
ch2_map = {(r['시도명'], r['시군구명']): r for r in ch2['sggIndex']}
sido_industry = {r['시도명']: r for r in ch3['industryBySido']}

PRESCRIPTION = {
    '노출도-우세형': '예찰·모니터링 인프라 확충',
    '인위적확산-우세형': '원목유통·도로변 관리(이동경로 차단)',
    '복합형': '기본 대응체계·인력 확충',
}

lst = ch3['prioritySggList']
for r in lst:
    key = (r['시도명'], r['시군구명'])
    c2 = ch2_map.get(key)
    if c2 is None:
        continue
    r['index_main'] = c2['index_main']
    r['배분갭'] = c2['배분갭']
    r['위험지수'] = c2['위험지수']
    axisA = c2['축A_위험요인유형']
    axisB = c2['축B_배분적정성']
    sido = sido_industry.get(r['시도명'])
    reclass = False
    if axisB == '부족' and sido is not None:
        if sido['정부지원필요도_평균'] >= 3.2 or sido['참여경험_있음비율'] <= 0.5:
            reclass = True
    if reclass:
        r['dominant_domain'] = '산업기반부족형'
        r['recommended_policy'] = '산업기반·업계 육성 연계 지원'
    else:
        r['dominant_domain'] = axisA
        r['recommended_policy'] = PRESCRIPTION[axisA]

risk = np.array([r['위험지수'] for r in lst], dtype=float)
pct = rankdata(risk, method='average') / len(risk)

def grade(p):
    if p >= 0.95: return 'S'
    if p >= 0.90: return 'A'
    if p >= 0.80: return 'B'
    if p <= 0.20: return 'D'
    return 'C'

for r, p in zip(lst, pct):
    r['priority_score'] = round(float(p), 4)
    r['grade'] = grade(p)

order2 = np.argsort(-pct)
for rank, i in enumerate(order2, 1):
    lst[i]['priority_rank'] = rank
ch3['prioritySggList'] = [lst[i] for i in order2]

ch3['meta']['priority_note'] = (
    "[옵션 A: 인위적확산 도메인 부호 +1 반전 적용] "
    "우선지원 순위 = RiskPct(위험지수의 백분위, 대응역량 제외) 단독. "
    "인위적확산 도메인 부호를 이론대로 +1(원목업체 多=확산위험 高)로 반전 → index_main·위험지수·배분갭·축A/B·CH3 dominant_domain 전부 재계산됨. "
    "Model1 CRE 회귀(AUC·between/within)는 원본 연도별 패널 재적합이 필요해 이번 재계산 범위 밖(기존 값 유지, 주의). "
    "근거: Modeling/1차/I-mPine_검토종합.html §3-10, 옵션 A/B 비교"
)

# ── 3) budgetGapSummary 갱신 (참고용) ───────────────────────────────
gaps_new = np.array([r['배분갭'] for r in ch2['sggIndex']])
under = sum(1 for r in ch2['sggIndex'] if r['축B_배분적정성']=='부족')
over = sum(1 for r in ch2['sggIndex'] if r['축B_배분적정성']=='과다')
ch3['simulation']['underfundedCount'] = under

print(f"\nTOP15 (A안):")
for r in ch3['prioritySggList'][:15]:
    print(f"  {r['priority_rank']:3d} [{r['grade']}] {r['시도명'][:4]} {r['시군구명']:8s} RiskPct={r['priority_score']:.3f} 축A={r.get('dominant_domain')}")

wando = [r for r in ch3['prioritySggList'] if r['시군구명']=='완도군'][0]
print(f"\n완도군: 순위={wando['priority_rank']}, 등급={wando['grade']}, RiskPct={wando['priority_score']:.4f}")

# ── 저장 ─────────────────────────────────────────────────────────
for path, varname, obj in [
    (BASE/"ch2"/"data.js", "CH2_DATA", ch2),
    (BASE/"ch3"/"data.js", "CH3_DATA", ch3),
]:
    out = f"window.{varname} = " + json.dumps(obj, ensure_ascii=False, indent=1) + ";\n"
    path.write_text(out, encoding='utf-8')
    print(f"저장: {path}")
