# -*- coding: utf-8 -*-
"""
축A(위험요인 유형) 임계값 민감도 분석
- ±0.3, ±0.5(기존 채택), ±0.7 세 기준으로 노출도-우세형/인위적확산-우세형/복합형 유형화를
  다시 수행하고, 유형 분포·경계선 근처 시군구의 유형 이동·"부족" 대표목록 안정성을 확인한다.
입력: output/모델링/Model1_기여도분해_유형화_final.csv
"""
import pandas as pd
import numpy as np

OUTDIR = "/Users/chanhaeng17/Desktop/최종 CH2 EDA/병합패널/output"
MODELDIR = f"{OUTDIR}/모델링"

LOG = []
def log(msg):
    print(msg)
    LOG.append(str(msg))

df = pd.read_csv(f"{MODELDIR}/Model1_기여도분해_유형화_final.csv")
diff = df["노출도_점수"] - df["인위적확산_점수"]

THRESHOLDS = [0.3, 0.5, 0.7]
type_cols = {}
for t in THRESHOLDS:
    col = f"축A_{t}"
    df[col] = np.select([diff > t, diff < -t], ["노출도-우세형", "인위적확산-우세형"], default="복합형")
    type_cols[t] = col

log("=== 임계값별 유형 분포 ===")
for t in THRESHOLDS:
    log(f"\n[임계값 ±{t}]")
    log(df[type_cols[t]].value_counts().to_string())

log("\n=== 임계값 간 분류 일치도 ===")
for t1, t2 in [(0.3, 0.5), (0.5, 0.7), (0.3, 0.7)]:
    same = (df[type_cols[t1]] == df[type_cols[t2]]).mean()
    log(f"  ±{t1} vs ±{t2}: 일치율 {same*100:.1f}%")

log("\n=== 임계값에 따라 분류가 바뀌는 '경계선' 시군구 (±0.3 vs ±0.7 기준 불일치) ===")
boundary = df[df[type_cols[0.3]] != df[type_cols[0.7]]]
log(f"경계선 시군구 수: {len(boundary)}/{len(df)}")
log(boundary[["시도", "시군구", "노출도_점수", "인위적확산_점수", type_cols[0.3], type_cols[0.7]]]
    .assign(차이=diff[boundary.index].round(3))
    .sort_values("차이", key=abs)
    .head(15).round(3).to_string(index=False))

# =========================================================
# "부족" 대표 목록 안정성 (배분갭 3분위는 임계값과 무관하게 고정)
# =========================================================
log("\n" + "=" * 70 + "\n임계값별 '부족' 열 대표 시군구(취약성지수 상위 5) 비교\n" + "=" * 70)
for t in THRESHOLDS:
    col = type_cols[t]
    log(f"\n[임계값 ±{t}]")
    for a_type in ["노출도-우세형", "인위적확산-우세형", "복합형"]:
        sub = df[(df[col] == a_type) & (df["축B_배분적정성"] == "부족")]
        sub = sub.sort_values("구조적취약성지수", ascending=False).head(5)
        names = ", ".join(f"{s}{c}" for s, c in zip(sub["시도"], sub["시군구"]))
        log(f"  {a_type}(n={len(df[(df[col]==a_type)&(df['축B_배분적정성']=='부족')])}): {names}")

with open(f"{MODELDIR}/축A_임계값_민감도분석_로그_final.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
log(f"\n저장 완료: 축A_임계값_민감도분석_로그_final.txt")
