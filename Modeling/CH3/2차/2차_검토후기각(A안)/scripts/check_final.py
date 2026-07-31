import json
from pathlib import Path

FINAL = Path(r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling\CH3\2차_최종채택(A안)")
text = (FINAL / "ch3" / "data.js").read_text(encoding='utf-8')
i = text.find('= ')
obj, end = json.JSONDecoder().raw_decode(text[i+2:])
w = [r for r in obj['prioritySggList'] if r['시군구명']=='완도군'][0]
print('완도군:', 'rank=', w['priority_rank'], 'grade=', w['grade'], 'score=', w['priority_score'])
print('전체 시군구 수:', len(obj['prioritySggList']))

ch2text = (FINAL / "ch2" / "data.js").read_text(encoding='utf-8')
i2 = ch2text.find('= ')
ch2obj, _ = json.JSONDecoder().raw_decode(ch2text[i2+2:])
w2 = [r for r in ch2obj['sggIndex'] if r['시군구명']=='완도군'][0]
print('완도군 ch2: dom_인위적확산=', w2['dom_인위적확산'], '(양수면 부호반전 적용된 것)')
print('budgetGapSummary:', ch2obj['budgetGapSummary'])
