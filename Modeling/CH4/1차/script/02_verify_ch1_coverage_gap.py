# -*- coding: utf-8 -*-
"""
CH1 sggBurden 커버리지 검증
CH3 우선지원 222개 시군구 중 CH1 sggBurden(180개 시군구, 실측 관측 지역만 포함)에
없는 지역이 몇 개인지, 그리고 상위 우선순위 지역 중 공백이 있는지 확인한다.

완도군(우선지원 6위, S등급)이 CH1에 없다는 것을 이 스크립트로 처음 확인했다.
이어서 원본 병해충 개별목 CSV(2016~2023)에서도 완도군(시군구코드 46890) 행이
0건인지 재확인해, sggBurden 누락이 집계 버그가 아니라 원자료 자체의 관측 공백임을 검증한다.
"""
import json, csv, glob, os

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


ch1 = load_data_js(ROOT + r"\ch1\data.js")
ch3 = load_data_js(ROOT + r"\ch3\data.js")

ch1_codes = {str(r.get("시군구코드", "")) for r in ch1["sggBurden"]}
print("CH1 sggBurden 총 시군구 수:", len(ch1_codes))

priority = ch3["prioritySggList"]
print("CH3 prioritySggList 총 시군구 수:", len(priority))

missing = [r for r in priority if not any(c in ch1_codes for c in r.get("sgg_codes", []))]
print("CH1에 존재:", len(priority) - len(missing), " / CH1에 없음:", len(missing))

top20 = sorted(priority, key=lambda x: x.get("priority_rank", 9999))[:20]
missing_in_top20 = [r for r in top20 if not any(c in ch1_codes for c in r.get("sgg_codes", []))]
print(f"상위 20위 안에서 CH1 데이터 없는 지역: {len(missing_in_top20)}개")
for r in missing_in_top20:
    print(f"  rank={r.get('priority_rank')}, {r.get('시군구명')}, grade={r.get('grade')}")

# ---- 원자료 재확인: 완도군(46890) 원본 CSV 행 수 ----
DIR = ROOT + r"\data\CH1\산림청_산림병해충방제 병해충발생관리정보_20250902"
WANDO_PREFIX = "46890"
total_wando = 0
for path in sorted(glob.glob(os.path.join(DIR, "*.csv"))):
    with open(path, encoding="cp949") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_dong = header.index("법정동코드")
        for row in reader:
            if row[idx_dong].startswith(WANDO_PREFIX):
                total_wando += 1
print()
print(f"원본 CSV(2016~2023 전체) 완도군({WANDO_PREFIX}) 행수: {total_wando} (0이면 sggBurden 누락이 원자료 자체의 공백임을 의미)")
