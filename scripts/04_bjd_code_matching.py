# -*- coding: utf-8 -*-
"""
법정동코드 기준자료 매칭 검증
- 'null00' 플레이스홀더(및 10자리가 아닌 값)는 결측으로 처리
- 기준표(법정동코드 전체자료.txt, cp949, tab구분)와 매칭
- 매칭률/미매칭 목록/폐지코드(동단위 vs 시군구단위)/연도별 미매칭률
- 기존 CH2 패널 sigungu_cd와 비교, 군위군/미추홀구 known case 확인
- 승계코드 자동매핑은 시도하지 않음 (기준자료에 폐지일자/승계코드가 없어 근거 부족 -> 예외관리로 분리)
"""
import pandas as pd
import numpy as np
import os

RAW_DIR = "data/CH1/산림청_산림병해충방제 병해충발생관리정보_20250902"
YEARS = list(range(2016, 2024))
REF_PATH = "data/CH1/법정동코드 전체자료/법정동코드 전체자료.txt"
CHUNKSIZE = 500_000

# ---- 기준표 로드 ----
ref = pd.read_csv(REF_PATH, sep="\t", encoding="cp949", dtype={"법정동코드": str})
ref["법정동코드"] = ref["법정동코드"].str.strip()
ref_map = ref.set_index("법정동코드")[["법정동명", "폐지여부"]].to_dict("index")
ref_codes = set(ref_map.keys())
print("기준표 행수:", len(ref))

# ---- CH2 예산패널 sigungu_cd 목록 ----
budget = pd.read_parquet("processed/budget_panel_step1.parquet")
ch2_sigungu = set(budget["sigungu_cd"].unique())
print("CH2 패널 고유 sigungu_cd 수:", len(ch2_sigungu))

yearly_stats = []
unmatched_codes_all = {}   # code -> [year_set, n_rows]
abolished_used = {}        # code -> [name, year_set, n_rows, level]
all_code_counts = {}       # 전체 연도 통합 code -> n_rows (null 제외, 10자리만)

for year in YEARS:
    path = os.path.join(RAW_DIR, f"병해충발생정보관리_{year}.csv")
    reader = pd.read_csv(path, encoding="cp949", usecols=["법정동코드"], dtype={"법정동코드": str},
                         chunksize=CHUNKSIZE, low_memory=False)
    total = 0
    null_cnt = 0
    matched = 0
    unmatched = 0
    abol_cnt = 0
    code_counts = {}
    for chunk in reader:
        codes = chunk["법정동코드"]
        total += len(codes)
        is_null_placeholder = codes.isna() | (codes == "null00") | (codes.str.len() != 10)
        null_cnt += int(is_null_placeholder.sum())
        valid_codes = codes[~is_null_placeholder]
        for c, cnt in valid_codes.value_counts().items():
            code_counts[c] = code_counts.get(c, 0) + int(cnt)
            all_code_counts[c] = all_code_counts.get(c, 0) + int(cnt)

    for c, cnt in code_counts.items():
        if c not in ref_codes:
            unmatched += cnt
            e = unmatched_codes_all.setdefault(c, [set(), 0])
            e[0].add(year); e[1] += cnt
        else:
            matched += cnt
            if ref_map[c]["폐지여부"] == "폐지":
                abol_cnt += cnt
                level = "시군구" if c[5:] == "00000" else "동"
                e = abolished_used.setdefault(c, [ref_map[c]["법정동명"], set(), 0, level])
                e[1].add(year); e[2] += cnt

    yearly_stats.append([year, total, null_cnt, matched, unmatched, abol_cnt,
                         matched / (total - null_cnt) if (total - null_cnt) else np.nan])
    print(f"[{year}] total={total} null_placeholder={null_cnt} matched={matched} unmatched={unmatched} abolished_used={abol_cnt}")

yearly_df = pd.DataFrame(yearly_stats, columns=["year", "total_rows", "null_placeholder_rows",
                                                  "matched_rows", "unmatched_rows", "abolished_code_rows",
                                                  "matched_rate_excl_null"])
yearly_df.to_csv("intermediate_recurrence/검증_법정동코드_연도별매칭률.csv", index=False, encoding="utf-8-sig")

unmatched_rows = []
for c, (years, cnt) in unmatched_codes_all.items():
    unmatched_rows.append([c, sorted(years), cnt])
unmatched_df = pd.DataFrame(unmatched_rows, columns=["법정동코드", "등장연도", "행수"]).sort_values("행수", ascending=False)
unmatched_df.to_csv("intermediate_recurrence/검증_법정동코드_미매칭목록.csv", index=False, encoding="utf-8-sig")

abol_rows = []
for c, (name, years, cnt, level) in abolished_used.items():
    abol_rows.append([c, name, level, sorted(years), cnt])
abol_df = pd.DataFrame(abol_rows, columns=["법정동코드", "법정동명", "레벨", "등장연도", "행수"]).sort_values("행수", ascending=False)
abol_df.to_csv("intermediate_recurrence/검증_법정동코드_폐지코드사용.csv", index=False, encoding="utf-8-sig")

# ---- sigungu_cd 후보 vs CH2 패널 비교 ----
sigungu_rows = []
for c, cnt in all_code_counts.items():
    sgg = c[:5]
    sigungu_rows.append([sgg, c, cnt])
sigungu_df = pd.DataFrame(sigungu_rows, columns=["sigungu_cd_candidate", "법정동코드", "행수"])
sgg_agg = sigungu_df.groupby("sigungu_cd_candidate")["행수"].sum().reset_index()

occ_sigungu = set(sgg_agg["sigungu_cd_candidate"])
only_in_occ = occ_sigungu - ch2_sigungu
only_in_ch2 = ch2_sigungu - occ_sigungu

mismatch_df = pd.DataFrame({
    "발생자료에만_존재": sorted(only_in_occ) + [""] * max(0, len(only_in_ch2) - len(only_in_occ)),
})
# 두 리스트 길이 다를 수 있어 별도 컬럼으로 저장
mismatch_report = pd.concat([
    pd.Series(sorted(only_in_occ), name="발생자료에만_존재_sigungu_cd"),
    pd.Series(sorted(only_in_ch2), name="CH2패널에만_존재_sigungu_cd"),
], axis=1)
mismatch_report.to_csv("intermediate_recurrence/검증_sigungu_cd_불일치목록.csv", index=False, encoding="utf-8-sig")

# ---- known case 확인: 군위군, 미추홀구 ----
known_names = ["군위", "미추홀"]
known_rows = ref[ref["법정동명"].str.contains("|".join(known_names), na=False)]
known_rows.to_csv("intermediate_recurrence/검증_known_case_기준표.csv", index=False, encoding="utf-8-sig")

known_in_occ = []
for _, row in known_rows.iterrows():
    c = row["법정동코드"]
    sgg = c[:5]
    if sgg in occ_sigungu:
        cnt = sgg_agg.loc[sgg_agg["sigungu_cd_candidate"] == sgg, "행수"].sum()
        known_in_occ.append([c, row["법정동명"], row["폐지여부"], sgg, sgg in ch2_sigungu, cnt])
known_df = pd.DataFrame(known_in_occ, columns=["법정동코드", "법정동명", "폐지여부", "sigungu_cd", "CH2패널존재", "발생자료행수"])
known_df.to_csv("intermediate_recurrence/검증_known_case_발생자료매칭.csv", index=False, encoding="utf-8-sig")

print("\n=== 연도별 매칭률 ===")
print(yearly_df.to_string(index=False))
print("\n전체 미매칭 고유코드 수:", len(unmatched_codes_all), " / 전체 미매칭 행수:", sum(v[1] for v in unmatched_codes_all.values()))
print("폐지코드 사용 고유코드 수:", len(abolished_used))
print("  - 시군구레벨:", sum(1 for v in abolished_used.values() if v[3] == "시군구"))
print("  - 동레벨:", sum(1 for v in abolished_used.values() if v[3] == "동"))
print("\n발생자료 고유 sigungu_cd 수:", len(occ_sigungu))
print("CH2패널에만 있고 발생자료엔 없는 sigungu_cd 수:", len(only_in_ch2))
print("발생자료에만 있고 CH2패널엔 없는 sigungu_cd 수:", len(only_in_occ))
print("\n=== 군위군/미추홀구 known case ===")
print(known_df.to_string(index=False))
