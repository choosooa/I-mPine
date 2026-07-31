# -*- coding: utf-8 -*-
"""
budget_won 결측 문제 검증

CH2 대시보드가 표시하는 평균예산_log(대응자원투입예산_소나무림ha당_log_재선충명시)는
"재선충병으로 명시된 예산"만 잡기 때문에, 완도군처럼 일반 산림병해충 대응예산은
있지만 재선충 전용으로 분류되지 않은 지역은 0.0으로 나온다.

이 스크립트는 (1) 이 값이 0.0인 시군구가 몇 개인지, 완도군이 그 목록 최상위인지 확인하고,
(2) CH2 원본 패널의 실측 원화값(대응자원투입예산_원, 관측 최신연도)으로 대체했을 때
    몇 개가 실제로 해결되는지 검증한다.
"""
import json, csv

ROOT = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"


def load_data_js(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    idx = content.index("=")
    json_str = content[idx + 1:].strip()
    if json_str.endswith(";"):
        json_str = json_str[:-1]
    obj, _ = json.JSONDecoder().raw_decode(json_str)
    return obj


ch2 = load_data_js(ROOT + r"\ch2\data.js")
ch3 = load_data_js(ROOT + r"\ch3\data.js")

ch2_by_code = {}
for r in ch2["sggIndex"]:
    for c in r.get("sgg_codes", []):
        ch2_by_code[c] = r

zero_list = []
for r in ch3["prioritySggList"]:
    codes = r.get("sgg_codes", [])
    ch2row = None
    for c in codes:
        if c in ch2_by_code:
            ch2row = ch2_by_code[c]
            break
    if ch2row and ch2row.get("평균예산_log") == 0.0:
        zero_list.append((codes[0] if codes else None, r.get("시군구명"), r.get("priority_rank")))

print(f"평균예산_log == 0.0 인 시군구: {len(zero_list)} / {len(ch3['prioritySggList'])} "
      f"({round(len(zero_list)/len(ch3['prioritySggList'])*100,1)}%)")
for _, name, rank in sorted(zero_list, key=lambda x: x[2])[:10]:
    print(f"  rank={rank}, {name}")

# ---- 원본 패널의 실측 원화값으로 교체 시 해결 건수 확인 ----
panel_path = ROOT + r"\Modeling\CH2\6차\CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
raw_budget = {}
with open(panel_path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row.get("시군구코드", "").strip()
        year = row.get("연도", "").strip()
        val = row.get("대응자원투입예산_원", "")
        try:
            val = float(val)
        except ValueError:
            val = None
        raw_budget.setdefault(code, {})[year] = val


def latest_budget(code):
    years = raw_budget.get(code, {})
    for y in ["2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016"]:
        v = years.get(y)
        if v is not None and v > 0:
            return v, y
    return None, None


resolved, still_zero = 0, []
for code, name, rank in zero_list:
    v, y = latest_budget(code)
    if v is not None:
        resolved += 1
    else:
        still_zero.append((rank, name))

print()
print(f"원본 대응자원투입예산_원(관측연도 중 양수)으로 해결되는 건수: {resolved} / {len(zero_list)}")
print(f"그래도 여전히 0/결측인 건수: {len(still_zero)}")
for rank, name in sorted(still_zero, key=lambda x: (x[0] is None, x[0]))[:15]:
    print(f"  rank={rank}, {name}")

wando_v, wando_y = latest_budget("46890")
print()
print(f"완도군: 원본 대응자원투입예산_원 최신값={wando_v}, 연도={wando_y}")
