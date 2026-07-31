# -*- coding: utf-8 -*-
"""
treeCount 6주기 누적 문제 검증 및 최신 관리주기 재계산

CH1 노트북(CH1_소나무재선충병_발생현황_분석.ipynb)의 sggBurden.누적피해고사목은
관리주기 2016~2021(2016.5~2022.4, 6개 관리주기)을 전부 합산한 값이다:

    chunk["관리주기"] = np.where(월>=5, 연도, 연도-1)
    cum = sgg_valid.groupby("시군구코드").agg(누적피해고사목=("피해고사목수","sum"))

CH4는 "지금 방제해야 할 물량"을 계산하는 도구이므로 6주기 누적치를 그대로 쓰면
비용·인력·기간이 실제보다 여러 배 부풀려진다. 이 스크립트는:
  1) 원본 CSV에서 CH1 노트북과 동일한 관리주기 정의로 시군구별 피해고사목수를 재계산하고,
  2) 최신 관리주기(2021.5~2022.4)만의 값과 6주기 누적값을 비교해 배율을 계산하고,
  3) 결과를 data/CH4/ch4_treecount_latest_cycle.json 으로 저장한다.
"""
import csv, glob, os, json
from collections import defaultdict

ROOT = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
DIR = ROOT + r"\data\CH1\산림청_산림병해충방제 병해충발생관리정보_20250902"
OUT_PATH = ROOT + r"\data\CH4\ch4_treecount_latest_cycle.json"

LATEST_CYCLE = 2021  # 2021.5~2022.4 (ANALYSIS_CYCLES=2016..2021 중 마지막 주기, CH1 노트북과 동일 정의)

latest_count = defaultdict(int)   # 시군구코드 -> 최신 관리주기만의 피해고사목수
cum_count = defaultdict(int)      # 시군구코드 -> 6주기(2016.5~2022.4) 누적 피해고사목수 (검증용 재현)

for path in sorted(glob.glob(os.path.join(DIR, "*.csv"))):
    with open(path, encoding="cp949") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_bjd = header.index("법정동코드")
        idx_gsg = header.index("고사목구분")
        idx_date = header.index("조사일자")
        for row in reader:
            bjd = row[idx_bjd]
            if len(bjd) != 10 or not bjd.isdigit():
                continue
            sgg = bjd[:5]
            date = row[idx_date]
            if not date or len(date) < 7:
                continue
            try:
                yr = int(date[:4])
                mo = int(date[5:7])
            except ValueError:
                continue
            cycle = yr if mo >= 5 else yr - 1  # CH1 노트북과 동일한 관리주기 정의(당해 5월~다음해 4월)
            if cycle < 2016 or cycle > 2021:
                continue  # ANALYSIS_CYCLES 범위만
            if row[idx_gsg] == "피해고사목":
                cum_count[sgg] += 1
                if cycle == LATEST_CYCLE:
                    latest_count[sgg] += 1

national_ratio = round(sum(cum_count.values()) / max(1, sum(latest_count.values())), 2)
print("전국 6주기 누적 총합:", sum(cum_count.values()))
print("전국 최신주기(2021.5~2022.4) 총합:", sum(latest_count.values()))
print("전국 배율(누적/최신주기):", national_ratio)

# 검증용 개별 도시 확인 (안동시=대표 고피해 도시, 완도군=CH1 원자료 자체에 관측 없는 지역)
for code, name in [("46890", "완도군"), ("47170", "안동시")]:
    c, l = cum_count.get(code, 0), latest_count.get(code, 0)
    ratio = round(c / l, 2) if l else None
    print(f"{name}({code}): 6주기누적={c}, 최신주기={l}, 배율={ratio}")

result = {
    "meta": {
        "정의": "관리주기 2021(=2021.5~2022.4, ANALYSIS_CYCLES 중 최신)만의 피해고사목수 — CH1 노트북의 6주기(2016.5~2022.4) 누적치인 sggBurden.누적피해고사목 대신, CH4 treeCount(지금 방제할 물량)로 쓰기 위한 단일 최신 주기 값",
        "재현_방법": "원본 CSV(병해충발생정보관리_YYYY.csv) 조사일자 기준 관리주기(당해 5월~다음해4월)를 CH1 노트북과 동일한 규칙으로 재계산 후, 관리주기==2021이고 고사목구분=='피해고사목'인 행만 시군구코드별 count",
        "전국_6주기_누적_총합": sum(cum_count.values()),
        "전국_최신주기_총합": sum(latest_count.values()),
        "전국_배율": national_ratio,
        "주의": "완도군 등 CH1 sggBurden에 아예 없는 시군구는 이 최신주기 집계에서도 0으로 나옴(원자료 자체에 관측 기록이 없기 때문, 계산 오류 아님)",
    },
    "by_sgg": {
        sgg: {"최신주기_피해고사목수": latest_count.get(sgg, 0), "6주기누적_피해고사목수": cum_count.get(sgg, 0)}
        for sgg in cum_count.keys()
    },
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("저장 완료:", OUT_PATH)
