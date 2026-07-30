# -*- coding: utf-8 -*-
"""
model1_final.py 원본이 어디에도 없어(전체 폴더 검색 완료), 4차의 model1_v4_final.py 구조를 그대로
가져오되 6차 보고서가 명시한 변경사항만 반영해 충실히 재구현.

6차 변경사항(보고서 §2.2, §3.1 본문 근거):
  - 데이터: 최종보정4.csv
  - 인위적확산 도메인 = log1p_원목생산업체수(면적통제 잔차) 단독 (도로소나무비율_500m 제외)
  - 표본: 1832 -> 1816(면적=0 제외) -> 1804(소나무림면적_자료유효_flag=0 제외) -> 1753(핵심변수 완비)
  - 도로소나무비율_500m은 이제 지수에 들어가지 않고, "제외해도 되는가"를 판단하기 위한
    진단용 변수로만 남음(면적통제 후 편상관 계산 대상)

이 스크립트는 그 진단 계산을 TierA(최종보정4)와 TierB(최종보정3)에서 동일한 표본정의·통제방식으로
나란히 재현해, "0.19 -> 0.0008"이 어떤 조건에서 나올 수 있는 값인지 근거를 남긴다.

[2026-07-31 추가] 이 스크립트는 원본 model1_final.py가 아니다 — 원본은 이후
`6차/script/model1_final.py`에서 별도로 발견됨(해당 파일 48번째 줄 주석에 "0.0008"이 문구로만
남아있고 계산 코드는 없음). 이 스크립트는 그 주석의 근거를 사후적으로 재구성하기 위한
보조 진단용이며, 아래는 이 스크립트 + 과거 저장된 체크포인트(`5.5차_TierA_실험/
2_크로스워크완성_최종/비교_TierA_vs_TierB/summary_TierA.json`, `비교표.txt`)를 포함한
독립 계산 결과 확정치다:
  - TierB 편상관 r≈0.19~0.23(대표값 0.2265, p<0.001, 유의) — 보고서의 "0.19"는 신뢰 가능한 실측치
  - TierA 편상관 r≈0.01~0.05(대표값 0.0148, p=0.54, 비유의) — 이 값이 실측 확정치
  - "0.0008"은 4개 독립 계산(오래전 시도/JSON 체크포인트/비교표.txt/2026-07-31 재실행) 중
    어디서도 재현 안 됨 — 폐기, 보고서에 이 숫자 그대로 쓰지 말 것
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats as st

Y = "log_피해밀도_본per_ha"
ROAD = "도로소나무비율_500m"
WOOD = "log1p_원목생산업체수"
AREA = "log_소나무림면적"

CORE_NOROAD = ["소나무류_면적비율(%)", "연강수량_mm", "GDD_솔수염하늘소_base11.9",
               "대응자원투입예산_소나무림ha당_log_재선충명시", "예찰사업_재선충명시_존재_flag",
               WOOD, AREA, Y]


def build_sample(path, label):
    df = pd.read_csv(path, low_memory=False)
    n0 = len(df)
    excl_area = df.loc[df[AREA].isna(), ["시도", "시군구"]].drop_duplicates()
    d = df.merge(excl_area.assign(_e1=1), on=["시도", "시군구"], how="left")
    d = d[d["_e1"].isna()].drop(columns="_e1")
    n1 = len(d)
    if "소나무림면적_자료유효_flag" in d.columns:
        d = d[d["소나무림면적_자료유효_flag"] != 0]
    n2 = len(d)
    core = [c for c in CORE_NOROAD if c in d.columns]
    d_core = d.dropna(subset=core).copy()
    n3 = len(d_core)
    print(f"[{label}] cascade: {n0} -> {n1} -> {n2} -> {n3}")
    return d_core


def road_partial_corr(d_core, label):
    """핵심변수 완비 표본(d_core) 안에서, 도로변수가 결측이 아닌 행만으로 면적통제 후 편상관 계산.
    (도로변수는 더 이상 핵심변수가 아니므로 listwise deletion에 포함되지 않음 - 진단만 이 서브셋에서)"""
    sub = d_core.dropna(subset=[ROAD, Y, AREA])
    X = sm.add_constant(sub[[AREA]])
    resid_road = sm.OLS(sub[ROAD], X).fit().resid
    resid_y = sm.OLS(sub[Y], X).fit().resid
    r, p = st.pearsonr(resid_road, resid_y)
    print(f"[{label}] 도로비율 면적통제 후 편상관: n={len(sub)}, r={r:.4f}, p={p:.4g}")
    return r, p, len(sub)


MOD = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine\Modeling"
tierA_path = MOD + r"\6차\CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
tierB_path = MOD + r"\3차\CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv"

d_core_A = build_sample(tierA_path, "TierA(최종보정4)")
d_core_B = build_sample(tierB_path, "TierB(최종보정3)")

rA, pA, nA = road_partial_corr(d_core_A, "TierA")
rB, pB, nB = road_partial_corr(d_core_B, "TierB")

# 원목업체수도 같은 표본에서 재계산(교차검증용)
subA_w = d_core_A.dropna(subset=[WOOD, Y, AREA])
Xw = sm.add_constant(subA_w[[AREA]])
resid_w = sm.OLS(subA_w[WOOD], Xw).fit().resid
resid_yw = sm.OLS(subA_w[Y], Xw).fit().resid
rw, pw = st.pearsonr(resid_w, resid_yw)
print(f"[TierA] 원목업체수 면적통제 후 잔차상관: n={len(subA_w)}, r={rw:.4f}, p={pw:.4g}")

print(f"\n=== 최종 근거 ===")
print(f"TierB(구버전) 편상관: {rB:.4f} (n={nB})  <- 보고서 '0.19'")
print(f"TierA(최종판) 편상관: {rA:.4f} (n={nA})  <- 보고서 '0.0008'")
print(f"두 값 모두 동일 스크립트·동일 표본정의·동일 통제방식(log_소나무림면적)으로 계산됨.")
