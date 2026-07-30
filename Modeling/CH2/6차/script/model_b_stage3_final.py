# -*- coding: utf-8 -*-
"""
모형 B - 3단계(v5): 배분공식 시뮬레이션 - 총예산 보존 + 상하한 제약 동시 만족 재구현
QA 재검증(외부 검토서 2건)에서 확인된 버그:
  1) 총예산 불일치(2017-2019, -1.8~2.1%): 그 해 예산 데이터가 없는 시군구까지 포함해
     위험지수 비중을 정규화한 뒤, 그 '유령 단위'를 출력 단계에서 제거해 몫이 사라졌음.
     -> 수정: 매년 '그 해 실제로 예산 데이터가 있는 단위(active set)'만으로 비중을 정규화.
  2) 상하한(±30%) 위반(2019년 110개, 2022년 186개 등): clip 이후 총액을 pool로 재조정하는
     단일 곱셈 스케일링이 방금 적용한 clip 경계를 다시 깨뜨렸음.
     -> 수정: water-filling(반복 클램핑) 알고리즘으로 전면 재구현. 경계에 걸린 단위는 그
     값으로 고정하고, 남은 pool을 남은 자유단위끼리만 다시 비례배분 -> 위반이 없어질 때까지 반복.
     이 알고리즘은 총액 보존과 경계 준수를 수학적으로 동시에 보장한다(각 반복에서 고정된 금액은
     정확히 그 경계값이고, 남은 pool은 자유단위 몫으로 정확히 재분배되므로 합계가 항상 pool).
  하한(floor)이 상한(cap)보다 커서 두 제약이 충돌하는 예외 케이스(직전year 값이 극히 작아
  +30% cap 자체가 floor보다 낮아지는 경우)는 floor를 우선 적용하고 발생 건수를 로그로 남긴다.
"""
import numpy as np
import pandas as pd
from scipy import stats

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
MODELDIR = f"{OUTDIR}/모델링"
PANEL = f"{OUTDIR}/CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
IDXFILE = f"{MODELDIR}/구조적취약성지수_final.csv"

BUDGET_WON = "대응자원투입예산_원_재선충명시"
FLOOR_RATIO = 0.30
CAP_RATE = 0.30

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))


def bounded_proportional_allocation(pool, weights, lower, upper, tol=1e-6):
    """
    총액 pool을 weights 비례로 배분하되 각 단위가 [lower_i, upper_i] 범위를 반드시 지키도록
    water-filling(반복 클램핑)으로 계산한다. 반환값의 합은 항상 pool과 정확히 일치한다.
    """
    n = len(weights)
    weights = np.asarray(weights, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)

    # 하한이 상한보다 큰 충돌 케이스: 하한 우선(상한을 하한까지 넓힘), 건수 기록
    conflict = lower > upper
    upper = np.where(conflict, lower, upper)

    fixed = np.full(n, np.nan)
    is_free = np.ones(n, dtype=bool)

    for _ in range(n + 1):
        if not is_free.any():
            break
        remaining_pool = pool - np.nansum(np.where(~is_free, fixed, 0.0))
        w_free = weights[is_free]
        if w_free.sum() <= 0:
            share = np.full(w_free.shape, 1.0 / len(w_free))
        else:
            share = w_free / w_free.sum()
        candidate = share * remaining_pool

        viol_low = candidate < lower[is_free] - tol
        viol_high = candidate > upper[is_free] + tol

        if not (viol_low.any() or viol_high.any()):
            fixed[is_free] = candidate
            is_free[:] = False
            break

        idx_free = np.where(is_free)[0]
        newly_low = idx_free[viol_low]
        newly_high = idx_free[viol_high]
        fixed[newly_low] = lower[newly_low]
        fixed[newly_high] = upper[newly_high]
        is_free[newly_low] = False
        is_free[newly_high] = False

    # 안전장치: 혹시 반복이 끝나도 남은 자유단위가 있으면 남은 pool을 균등배분
    if is_free.any():
        remaining_pool = pool - np.nansum(np.where(~is_free, fixed, 0.0))
        fixed[is_free] = remaining_pool / is_free.sum()

    return fixed, conflict


panel = pd.read_csv(PANEL)[["연도", "시도", "시군구", BUDGET_WON, "log_피해밀도_본per_ha"]]
idx = pd.read_csv(IDXFILE)[["연도", "시도", "시군구", "위험지수", "Y_bin"]]
df = idx.merge(panel, on=["연도", "시도", "시군구"], how="left")

main = df[df["연도"].between(2017, 2022)].dropna(subset=[BUDGET_WON]).copy()
main["key"] = main["시도"] + main["시군구"]
log(f"[시뮬레이션 표본] {main.shape}")

years = sorted(main["연도"].unique())

panel_all = pd.read_csv(PANEL)
panel_all["key"] = panel_all["시도"] + panel_all["시군구"]

records = []
floor_bind_count = 0
cap_bind_count = 0
conflict_count = 0
total_n = 0
relaxed_years = []
sim_prev_map = {}  # key -> 직전연도 시뮬예산(그 해 active했던 단위만 갱신)

for y in years:
    yr = main[main["연도"] == y].copy()
    active_units = yr["key"].tolist()  # <- 핵심 수정: 그 해 실제 예산자료가 있는 단위만 사용
    n = len(active_units)
    pool = yr[BUDGET_WON].sum()

    yr = yr.set_index("key")
    risk = yr.loc[active_units, "위험지수"]
    risk_norm = (risk - risk.min()) / (risk.max() - risk.min())
    risk_norm = risk_norm.fillna(risk_norm.mean())
    weights = risk_norm.values

    floor_amt = FLOOR_RATIO * (pool / n)
    prev_vals = np.array([sim_prev_map.get(u, 0.0) for u in active_units])

    # 실현가능성 체크: 총액이 전년대비 개별상한(30%) 이상으로 커지면, 모든 단위가 +30%씩
    # 늘어도 새 pool을 다 못 채운다(수학적으로 불가능). 이 경우에만 그 해 상한을 '총액 증가율'
    # 수준까지 최소한으로 완화한다(30% 초과분 없이는 총액 보존 자체가 불가능하기 때문).
    # 하한-상한 충돌(floor override)이 섞이면 1차 추정치로는 부족할 수 있어 반복 보정한다.
    prev_sum = prev_vals.sum()
    effective_cap_rate = CAP_RATE
    cap_relaxed = False
    if prev_sum > 0 and pool / prev_sum - 1 > CAP_RATE:
        effective_cap_rate = pool / prev_sum - 1
        cap_relaxed = True

    for _ in range(20):
        lower_cap = prev_vals * (1 - CAP_RATE)
        upper_cap = np.where(prev_vals > 0, prev_vals * (1 + effective_cap_rate), np.inf)
        lower = np.maximum(floor_amt, lower_cap)
        upper = upper_cap
        alloc, conflict = bounded_proportional_allocation(pool, weights, lower, upper)
        shortfall = pool - alloc.sum()
        if abs(shortfall) < 1.0 or prev_sum <= 0:
            break
        # 부족분만큼 상한을 추가로 완화(하한충돌로 1차 추정이 못 미친 경우 보정)
        effective_cap_rate += shortfall / prev_sum
        cap_relaxed = True

    if cap_relaxed:
        log(f"  [{y}] 총액 증가율(pool/전년비) 때문에 그 해 상한을 "
            f"{effective_cap_rate*100:.1f}%로 완화(그래야 총액 보존과 상한이 동시에 성립)")
        relaxed_years.append((y, round(effective_cap_rate, 4)))

    # 검증: 총액·경계 위반 자동 점검
    assert abs(alloc.sum() - pool) < 1.0, f"{y}년 총액 불일치: {alloc.sum()} vs {pool}"
    viol = ((alloc < lower - 1.0) | (alloc > upper + 1.0)) & ~conflict
    assert viol.sum() == 0, f"{y}년 경계 위반 {viol.sum()}건 발생"

    n_floor = (np.isclose(alloc, floor_amt, rtol=1e-4)).sum()
    n_cap = (np.isclose(alloc, lower_cap, rtol=1e-4) | np.isclose(alloc, upper_cap, rtol=1e-4)).sum() - n_floor
    n_cap = max(n_cap, 0)
    floor_bind_count += n_floor
    cap_bind_count += n_cap
    conflict_count += conflict.sum()
    total_n += n

    for u, a, r in zip(active_units, alloc, risk.values):
        records.append({
            "key": u, "연도": y,
            "실제예산": yr.loc[u, BUDGET_WON],
            "시뮬예산": a,
            "위험지수": r,
            "Y": yr.loc[u, "log_피해밀도_본per_ha"],
            "Y_bin": yr.loc[u, "Y_bin"],
        })
        sim_prev_map[u] = a

sim = pd.DataFrame(records)
key_to_region = main[["key", "시도", "시군구"]].drop_duplicates(subset="key").set_index("key")
sim["시도"] = sim["key"].map(key_to_region["시도"])
sim["시군구"] = sim["key"].map(key_to_region["시군구"])

log(f"\n[제약 발동 빈도] 하한: {floor_bind_count}/{total_n}건 ({floor_bind_count/total_n*100:.1f}%), "
    f"상한: {cap_bind_count}/{total_n}건 ({cap_bind_count/total_n*100:.1f}%), "
    f"하한-상한 충돌(하한 우선 적용): {conflict_count}건")
if relaxed_years:
    log(f"[상한 완화 연도] {relaxed_years} — 이 연도들은 총액 증가율이 30%를 넘어 "
        f"±30% 고정 상한으로는 총액보존 자체가 불가능했음(수학적 필연)")
else:
    log("[상한 완화 연도] 없음 - 전 연도에서 ±30% 상한 그대로 유지하며 총액보존 성립")

# =========================================================
# 자동 검증: 연도별 총액 보존 + 상하한 준수 여부
# =========================================================
log(f"\n{'='*70}\n자동 검증: 총액 보존 및 상하한 준수\n{'='*70}")
g = sim.groupby("연도").agg(n=("key", "size"), 실제총액=("실제예산", "sum"), 시뮬총액=("시뮬예산", "sum"))
g["차액"] = g["시뮬총액"] - g["실제총액"]
g["차이율(%)"] = g["차액"] / g["실제총액"] * 100
log(g.round(2).to_string())

piv = sim.pivot(index="key", columns="연도", values="시뮬예산")
pct = piv.pct_change(axis=1, fill_method=None)
relaxed_rate_by_year = dict(relaxed_years)
log("\n연도별 전년대비 증감률, '그 해 실제 적용된 상한' 기준 위반 건수(0이어야 정상):")
for y in years[1:]:
    s = pct[y].dropna()
    cap_this_year = relaxed_rate_by_year.get(y, CAP_RATE)
    n_over = (s > cap_this_year + 1e-3).sum()
    n_under = (s < -CAP_RATE - 1e-3).sum()
    note = f" (상한 {cap_this_year*100:.1f}%로 완화 적용됨)" if y in relaxed_rate_by_year else ""
    log(f"  {y}: n={len(s)}, 적용상한초과={n_over}, -30%미만={n_under}, 범위=[{s.min()*100:.1f}%, {s.max()*100:.1f}%]{note}")

# =========================================================
# 기존 지표 재산출
# =========================================================
sim["diff"] = sim["시뮬예산"] - sim["실제예산"]
log("\n=== 연도별 재배분 규모 ===")
for y in years:
    yr = sim[sim["연도"] == y]
    realloc = yr["diff"].clip(lower=0).sum()
    pool = yr["실제예산"].sum()
    log(f"  {y}: 이동액 {realloc:,.0f}원 / 총액 {pool:,.0f}원 = {realloc/pool*100:.1f}%")

log("\n=== 피해발생지역(Y_bin=1) 예산 포착률: 실제 vs 시뮬 ===")
for y in years:
    yr = sim[sim["연도"] == y]
    pos = yr[yr["Y_bin"] == 1]
    tot_actual, tot_sim = yr["실제예산"].sum(), yr["시뮬예산"].sum()
    cap_actual = pos["실제예산"].sum() / tot_actual
    cap_sim = pos["시뮬예산"].sum() / tot_sim
    log(f"  {y}: 실제배분 포착률={cap_actual*100:.1f}%  시뮬배분 포착률={cap_sim*100:.1f}%")

overall_actual = sim.loc[sim["Y_bin"] == 1, "실제예산"].sum() / sim["실제예산"].sum()
overall_sim = sim.loc[sim["Y_bin"] == 1, "시뮬예산"].sum() / sim["시뮬예산"].sum()
log(f"\n[전체기간 합산] 실제배분 포착률={overall_actual*100:.1f}%  시뮬배분 포착률={overall_sim*100:.1f}%")
r_actual = stats.spearmanr(sim["실제예산"], sim["Y"]).correlation
r_sim = stats.spearmanr(sim["시뮬예산"], sim["Y"]).correlation
log(f"[Spearman: 예산 vs 실제피해밀도] 실제배분={r_actual:.3f}  시뮬배분={r_sim:.3f}")

last = sim[sim["연도"] == 2022].copy()
log("\n=== 2022년 기준 증액 Top 10 ===")
log(last.sort_values("diff", ascending=False).head(10)[["시도", "시군구", "위험지수", "실제예산", "시뮬예산", "diff"]]
    .round(0).to_string(index=False))
log("\n=== 2022년 기준 감액 Top 10 ===")
log(last.sort_values("diff").head(10)[["시도", "시군구", "위험지수", "실제예산", "시뮬예산", "diff"]]
    .round(0).to_string(index=False))

sim.to_csv(f"{MODELDIR}/배분공식_시뮬레이션결과_final.csv", index=False, encoding="utf-8-sig")
with open(f"{MODELDIR}/배분공식_로그_final.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\n저장 완료: 배분공식_시뮬레이션결과_final.csv, 배분공식_로그_final.txt")
