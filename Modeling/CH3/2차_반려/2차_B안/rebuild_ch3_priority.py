# -*- coding: utf-8 -*-
"""
CH3 우선순위 산식 교체 — 최종 결정 반영
Priority = percentile_rank(위험지수)  (대응역량 제외, 배분갭/재발확률 산식에서 제거)
등급: S(상위5%)/A(10%)/B(20%)/C(80%)/D(하위20%)
근거: Modeling/1차/I-mPine_검토종합.html §3-10
"""
import json
from pathlib import Path
import numpy as np
from scipy.stats import rankdata

ROOT = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine")
TARGET = ROOT / "Modeling" / "2차" / "ch3" / "data.js"

def load_js(path, varname):
    text = Path(path).read_text(encoding='utf-8')
    for prefix in [f'window.{varname} = ']:
        i = text.find(prefix)
        if i >= 0:
            obj, end = json.JSONDecoder().raw_decode(text[i+len(prefix):])
            return obj
    raise ValueError

ch2 = load_js(ROOT / "ch2" / "data.js", "CH2_DATA")
ch3 = load_js(TARGET, "CH3_DATA")

risk_map = {(r['시도명'], r['시군구명']): r['위험지수'] for r in ch2['sggIndex']}

lst = ch3['prioritySggList']
for r in lst:
    key = (r['시도명'], r['시군구명'])
    r['위험지수'] = risk_map.get(key)

risk = np.array([r['위험지수'] for r in lst], dtype=float)
pct = rankdata(risk, method='average') / len(risk)

def grade(p):
    if p >= 0.95: return 'S'
    if p >= 0.90: return 'A'
    if p >= 0.80: return 'B'
    if p <= 0.20: return 'D'
    return 'C'

for r, p in zip(lst, pct):
    r['priority_score'] = round(float(p), 4)   # = RiskPct (위험지수 백분위, 대응역량 제외)
    r['grade'] = grade(p)

# priority_rank 재부여 + 정렬 (ch3.html이 slice(0,15) 하므로 반드시 정렬 상태로 저장)
order = np.argsort(-pct)
for rank, i in enumerate(order, 1):
    lst[i]['priority_rank'] = rank
lst_sorted = [lst[i] for i in order]
ch3['prioritySggList'] = lst_sorted

# meta에 공식 설명 추가
ch3['meta']['priority_note'] = (
    "우선지원 순위 = RiskPct(위험지수의 백분위, 대응역량 제외) 단독. "
    "배분갭은 산식에서 제거하고 지도 툴팁에 참고용으로만 표시. 재발위험확률은 urgentList 교차조건으로만 사용. "
    "등급: S(상위5%)/A(10%)/B(20%)/C(80%)/D(하위20%). "
    "근거·경위: Modeling/1차/I-mPine_검토종합.html §3-10 (6개 후보 공식 전수비교 후 채택; "
    "선행조건: CH2 도메인 F02/F06 수정 시 완도군류 왜곡이 추가로 개선될 여지 있음)"
)

grade_counts = {}
for r in lst_sorted:
    grade_counts[r['grade']] = grade_counts.get(r['grade'], 0) + 1
print("등급 분포:", grade_counts)
print("\nTOP15:")
for r in lst_sorted[:15]:
    print(f"  {r['priority_rank']:3d} [{r['grade']}] {r['시도명'][:4]} {r['시군구명']:8s} RiskPct={r['priority_score']:.3f} 재발={r['재발위험확률']:.3f}")

out = "window.CH3_DATA = " + json.dumps(ch3, ensure_ascii=False, indent=1) + ";\n"
TARGET.write_text(out, encoding='utf-8')
print(f"\n저장 완료: {TARGET}")
