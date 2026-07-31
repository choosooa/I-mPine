# -*- coding: utf-8 -*-
"""
CH4 입력 데이터 통합 스크립트
CH3 우선지원 222개 시군구에 대해 CH1(실측 면적/피해목수) · CH2(실측 원화예산) ·
CH3(등급/재발위험확률) · 임업경영실태조사(실측 인건비)를 결합해
data/CH4/ch4_input_data.json 을 생성한다.

주의: treeCount는 이 단계에서는 CH1 sggBurden.누적피해고사목(6주기 누적)을 그대로 쓴다.
     6주기 누적 문제 수정은 02_verify_treecount_cumulative_issue.py,
     03_apply_treecount_fix.py 에서 별도로 처리한다.
"""
import json, csv

ROOT = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
OUT_DIR = ROOT + r"\data\CH4"


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
ch2 = load_data_js(ROOT + r"\ch2\data.js")
ch3 = load_data_js(ROOT + r"\ch3\data.js")

# CH1 sggBurden: 시군구코드 -> row
ch1_by_code = {str(r["시군구코드"]): r for r in ch1["sggBurden"]}

# CH2 sggIndex: sgg_code -> row
ch2_by_code = {}
for r in ch2["sggIndex"]:
    for c in r.get("sgg_codes", []):
        ch2_by_code[c] = r

# CH2 원본 패널(raw 예산, 원 단위) - 시군구코드별 최신연도 관측값
panel_path = ROOT + r"\Modeling\CH2\6차\CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
raw_budget = {}  # 시군구코드 -> {연도: 대응자원투입예산_원}
with open(panel_path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row.get("시군구코드", "").strip()
        year = row.get("연도", "").strip()
        if not code:
            continue
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


GRADE_TARGET_DAYS = {"S": 4, "A": 6, "B": 8, "C": 12, "D": 18}  # 내부 추정 원칙(등급이 급할수록 짧게) - 공식 기준 아님

merged = []
missing_ch1 = []
for r in ch3["prioritySggList"]:
    codes = r.get("sgg_codes", [])

    ch1_row = None
    for c in codes:
        if c in ch1_by_code:
            ch1_row = ch1_by_code[c]
            break

    budget_won, budget_year = (None, None)
    for c in codes:
        b, y = latest_budget(c)
        if b is not None:
            budget_won, budget_year = b, y
            break

    grade = r.get("grade")
    entry = {
        "시도명": r.get("시도명"),
        "시군구명": r.get("시군구명"),
        "sgg_codes": codes,
        "priority_rank": r.get("priority_rank"),
        "grade": grade,
        "재발위험확률": r.get("재발위험확률"),
        "dominant_domain": r.get("dominant_domain"),
        "recommended_policy": r.get("recommended_policy"),
        "area_ha": ch1_row.get("소나무류면적_ha") if ch1_row else None,
        "treeCount": ch1_row.get("누적피해고사목") if ch1_row else None,  # 이후 03에서 최신주기 값으로 교체됨
        "ch1_data_available": ch1_row is not None,
        "budget_won_observed": budget_won,
        "budget_won_observed_year": budget_year,
        "targetDays_suggested": GRADE_TARGET_DAYS.get(grade, 10),
    }
    merged.append(entry)
    if not entry["ch1_data_available"]:
        missing_ch1.append(entry)

labor_stats = {
    "source": "2023년 임업경영실태조사 마이크로데이터 - 영림업 및 목재수확업 모듈",
    "male_daily_wage_krw": 200000,
    "male_daily_wage_n": 57,
    "female_daily_wage_krw": 115000,
    "female_daily_wage_n": 8,
    "note": "여성 표본(n=8)은 참고용으로만 사용, CH4 unitCost 계산에는 남성 중앙값(20만원/일)만 채택",
}

output = {
    "meta": {
        "generated_note": "CH3 우선지원 222개 시군구에 CH1 실측 면적/피해목수, CH2 실측 원화예산(재선충명시 아님, 일반 산림병해충 대응예산 중 관측된 최신값), CH3 등급/재발위험확률 기반 목표일수를 결합한 CH4 입력 원자료",
        "총_시군구_수": len(merged),
        "CH1_데이터_있는_시군구_수": len(merged) - len(missing_ch1),
        "CH1_데이터_없는_시군구_수": len(missing_ch1),
        "budget_필드_설명": "budget_won_observed는 CH2 원본 패널의 '대응자원투입예산_원'(재선충 한정 아닌 일반 산림병해충 대응예산, 관측연도 중 최신값) — 대시보드 표시용 '평균예산_log(재선충명시)'와 다름. 실제 예산 비교가 목적인 CH4에서는 이 실측 원화값 사용을 권장.",
    },
    "labor_wage": labor_stats,
    "sgg_data": merged,
}

with open(OUT_DIR + r"\ch4_input_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("저장 완료:", OUT_DIR + r"\ch4_input_data.json")
print("총 시군구:", len(merged), "/ CH1 데이터 없는 시군구:", len(missing_ch1))
