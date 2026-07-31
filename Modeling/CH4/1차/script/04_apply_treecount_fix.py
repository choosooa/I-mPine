# -*- coding: utf-8 -*-
"""
03_verify_treecount_cumulative_issue.py 의 결과(ch4_treecount_latest_cycle.json)를
01_build_ch4_input_data.py 의 결과(ch4_input_data.json)에 병합해
treeCount를 6주기 누적치에서 최신 관리주기 값으로 교체한다.

기존 6주기 누적치는 "treeCount_누적_6주기(참고용, CH4에는_미사용)" 필드로 남겨
화면에서 실수로 다시 섞이지 않도록 한다.
"""
import json

ROOT = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
INPUT_PATH = ROOT + r"\data\CH4\ch4_input_data.json"
LATEST_PATH = ROOT + r"\data\CH4\ch4_treecount_latest_cycle.json"

with open(INPUT_PATH, encoding="utf-8") as f:
    data = json.load(f)
with open(LATEST_PATH, encoding="utf-8") as f:
    latest = json.load(f)

by_sgg = latest["by_sgg"]

fixed = 0
for r in data["sgg_data"]:
    codes = r.get("sgg_codes", [])
    match = None
    for c in codes:
        if c in by_sgg:
            match = by_sgg[c]
            break
    old_tree = r.get("treeCount")
    r["treeCount_누적_6주기(참고용, CH4에는_미사용)"] = old_tree
    if match:
        r["treeCount"] = match["최신주기_피해고사목수"]
        r["treeCount_source"] = "CH1 원자료 재계산 - 관리주기 2021(2021.5~2022.4) 단일 주기, 6주기 누적 아님"
        fixed += 1
    else:
        r["treeCount"] = None
        r["treeCount_source"] = "원자료 관측 없음 (CH1 sggBurden에도 없는 지역)"

data["meta"]["treeCount_수정"] = {
    "문제": "기존 treeCount는 CH1 sggBurden.누적피해고사목(2016.5~2022.4, 6개 관리주기 합산)을 그대로 썼음 — CH4가 계산하는 '지금 방제할 물량'과 성격이 다름(6~8배 과대추정)",
    "수정": "최신 관리주기(2021.5~2022.4) 단일 주기 피해고사목수로 교체. 전국 배율 실측 8.63배",
    "검증": "안동시(대표 고피해 도시) 6주기누적=214,030 vs 최신주기=24,986 (8.57배) - 전국 평균과 일치",
    "적용_시군구_수": fixed,
}

with open(INPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("treeCount 수정 적용:", fixed, "/", len(data["sgg_data"]))
