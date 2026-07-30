# -*- coding: utf-8 -*-
"""
기후위험도 QA 피드백 실무 반영
1) 결측 9행 사유 분리: 세종·공주(관측소 미개설/신규개설, 8행) vs 화천군(부분연도 관측, 1행)
2) 관측소 이슈 2종 분리 플래그: 원거리 도서지역(옹진군) vs 대도시권 재사용(stnId=108, 30개 시군구)
3) SPI3_최저월(최심가뭄): ICC≈0(ANOVA 재계산 -0.080) + 개념적으로 between신호 회복 불가 확인
   -> 변수사전 역할을 '핵심'에서 '제외'로 변경, '별도 통제변수' 옵션은 폐기(논리적 결함)
4) 평균풍속_ms: ICC 재계산 0.944(원문서 0.826은 오류) + Spearman(between) -0.144(원문서 Pearson
   0.003~0.019는 근사 0으로 오판) 확인 -> 제외/축소 결정 철회, 핵심 변수로 유지
입력: output/CH2_전체병합패널_5도메인_2016_2023_최종보정 2.csv, output/변수사전_역할태그.csv
출력: output/CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv, output/변수사전_역할태그.csv(갱신)
"""
import pandas as pd

OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
IN_PANEL = f"{OUTDIR}/CH2_전체병합패널_5도메인_2016_2023_최종보정 2.csv"
OUT_PANEL = f"{OUTDIR}/CH2_전체병합패널_5도메인_2016_2023_최종보정3.csv"
DICT_PATH = f"{OUTDIR}/변수사전_역할태그.csv"

df = pd.read_csv(IN_PANEL)
print("[원본]", df.shape)

# =========================================================
# 1) 기후자료_결측사유 (결측 9행 사유 분리)
# =========================================================
df["기후자료_결측사유"] = None
missing_mask = df["연강수량_mm"].isna() | df["GDD_솔수염하늘소_base11.9"].isna()

sejong_gongju = missing_mask & df["시군구"].isin(["세종시", "공주시"])
hwacheon = missing_mask & (df["시군구"] == "화천군") & (df["연도"] == 2016)

df.loc[sejong_gongju, "기후자료_결측사유"] = "관측소_미개설또는신규개설_부분연도(stnId=239, 2019년까지 관측일수<360)"
df.loc[hwacheon, "기후자료_결측사유"] = "기존관측소_부분연도관측(stnId=93, 2016년 관측일수=92)"

n_reason = df["기후자료_결측사유"].notna().sum()
print(f"[기후자료_결측사유] 부여 {n_reason}행 (세종·공주 {sejong_gongju.sum()}행 + 화천 {hwacheon.sum()}행)")
assert n_reason == missing_mask.sum(), "결측행과 사유부여행 수 불일치"

# =========================================================
# 2) 관측소 품질 플래그 2종 분리
# =========================================================
df["관측소_원거리_도서지역_flag"] = (df["시군구"] == "옹진군").astype(int)

station_counts = df[["시도", "시군구", "stnId"]].drop_duplicates().groupby("stnId")["시군구"].transform("nunique")
station_counts_full = df.groupby("stnId")["시군구"].transform(lambda s: df.loc[s.index, ["시도", "시군구"]].drop_duplicates().shape[0])
# 간단히: stnId별 고유 (시도,시군구) 개수 계산 후 병합
unit_per_station = df[["시도", "시군구", "stnId"]].drop_duplicates().groupby("stnId").size()
df["관측소_대도시권_재사용_flag"] = df["stnId"].map(lambda s: 1 if unit_per_station.get(s, 0) >= 10 else 0)

print(f"[관측소_원거리_도서지역_flag] {df['관측소_원거리_도서지역_flag'].sum()}행 (옹진군)")
print(f"[관측소_대도시권_재사용_flag] {df['관측소_대도시권_재사용_flag'].sum()}행 "
      f"({df.loc[df['관측소_대도시권_재사용_flag']==1,'시군구'].nunique()}개 시군구, stnId=108 등)")

# =========================================================
# 3) SPI3 컬럼은 남기되(원자료 보존), 아래에서 변수사전 역할만 '제외'로 변경
#    (패널 자체에서 삭제하지 않음 - 검산/재현 가능성 유지)
# =========================================================

df.to_csv(OUT_PANEL, index=False, encoding="utf-8-sig")
print(f"\n저장: {OUT_PANEL} {df.shape}")

# =========================================================
# 4) 변수사전 갱신
# =========================================================
vd = pd.read_csv(DICT_PATH)

def update_row(colname, **kwargs):
    idx = vd[vd["컬럼명"] == colname].index
    if len(idx) == 0:
        print(f"  [경고] 변수사전에 {colname} 없음 - 건너뜀")
        return
    for k, v in kwargs.items():
        vd.loc[idx, k] = v

update_row(
    "SPI3_최저월(최심가뭄)", 역할="제외",
    비고=("QA 재검증: ANOVA ICC=-0.080(원문서 0.000 표기는 방향만 맞음, 수치 재계산 필요). "
          "SPI는 정의상 장기평균이 0에 수렴하는 이상치지수라 between 신호 구조적 회복 불가. "
          "'별도 통제변수 분리' 안은 표준화 여부와 무관하게 근본 문제(신뢰 불가한 소표본 between "
          "추정치)를 해결 못해 폐기 - 완전 제외로 단일화(2026-07-30 QA)")
)
update_row(
    "평균풍속_ms", 역할="핵심",
    비고=("QA 재검증: ANOVA ICC=0.944(원문서 0.826은 계산 오류, 4개 기후변수 중 최고 - "
          "가장 강한 지자체 고유특성). Pearson은 근사 0이나 Spearman(between)=-0.144로 "
          "뚜렷한 단조관계 확인 - 제외/축소 결정 철회, 핵심 변수로 유지(2026-07-30 QA)")
)
update_row(
    "거리_km",
    비고=("관측소까지 거리. 옹진군만 73.94km로 이상치(전국평균 11.9km) - 도서지역 관측공백 문제. "
          "관측소 재사용(대도시권 30개 시군구 공유) 문제와는 별개 현상이므로 각주 분리 필요(2026-07-30 QA)")
)
update_row(
    "stnId",
    비고=("관측소 ID, 클러스터 SE용. stnId=108이 30개 시군구(서울 25개구+경기 5개시)에 동시 배정 - "
          "대도시권 관측소 공유 패턴. 옹진군의 원거리(73.94km) 문제와는 별개 현상(2026-07-30 QA)")
)

new_rows = pd.DataFrame([
    {"순번": vd["순번"].max()+1, "컬럼명": "기후자료_결측사유", "도메인": "기후위험도", "역할": "품질",
     "비고": "결측 9행 사유 분리: 세종·공주(관측소 미개설/신규개설) vs 화천군(부분연도 관측, 별도 사유)"},
    {"순번": vd["순번"].max()+2, "컬럼명": "관측소_원거리_도서지역_flag", "도메인": "기후위험도", "역할": "품질",
     "비고": "옹진군만 1 - 관측소까지 73.94km(전국평균 11.9km) 도서지역 관측공백"},
    {"순번": vd["순번"].max()+3, "컬럼명": "관측소_대도시권_재사용_flag", "도메인": "기후위험도", "역할": "품질",
     "비고": "동일 stnId를 10개 이상 시군구가 공유하면 1 (stnId=108: 서울25구+경기5시 등)"},
])
vd = pd.concat([vd, new_rows], ignore_index=True)
vd.to_csv(DICT_PATH, index=False, encoding="utf-8-sig")
print(f"저장: {DICT_PATH} {vd.shape}")

print("\n=== 갱신된 SPI3/평균풍속 역할 확인 ===")
print(vd[vd["컬럼명"].isin(["SPI3_최저월(최심가뭄)", "평균풍속_ms"])][["컬럼명", "역할"]].to_string(index=False))
