#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0 #1 — CH3 우선지원 순위 산식 교체
═══════════════════════════════════════════════════════════════

문제:
  기존 priority_score = index_main - 배분갭
  → 배분갭의 SD(4.722)가 index_main의 SD(0.492)의 9.6배
  → 순위의 98.9%가 배분갭(≈예산수준)에 의해 결정
  → TOP30에 서울 자치구 8곳, 1위가 피해 0인 완도군
  → Spearman(priority_score, 재발위험확률) = -0.4766

수정 (2×2 배분규칙 + z-정규화 가중평균):
  1) 분석 모집단: 발생 이력이 있는 시군구만 (또는 소나무림 면적 ≥ 300ha)
  2) z-정규화 후 가중결합:
     priority = 0.5*z(구조위험지수) + 0.5*z(재발위험확률) + 0.15*z(-배분갭)
  3) 2×2 매트릭스: 재발위험(상/하) × 현행예산(상/하)

이 스크립트는 기존 ch3/data.js의 prioritySggList를 입력으로 받아
새 priority_score와 2×2 배분규칙을 계산합니다.

사용법:
  1) ch2/data.js와 ch3/data.js가 있는 I-mPine 루트에서 실행
  2) 출력: ch3/data_priority_fixed.json (새 prioritySggList)
  3) 검증 후 ch3/data.js에 반영
"""
import json
import sys
import numpy as np
from pathlib import Path

def load_js_data(path, varname):
    """window.XXX = { ... }; 형태의 JS 파일에서 데이터 추출"""
    text = Path(path).read_text(encoding='utf-8')
    # "window.CH3_DATA = " 또는 "const CH3_DATA = " 제거
    for prefix in [f'window.{varname} = ', f'window.{varname}=',
                   f'const {varname} = ', f'const {varname}=']:
        idx = text.find(prefix)
        if idx >= 0:
            json_start = idx + len(prefix)
            break
    else:
        raise ValueError(f"{varname}을 찾을 수 없습니다: {path}")
    
    # 마지막 세미콜론 제거
    json_text = text[json_start:].rstrip().rstrip(';')
    return json.loads(json_text)


def zscore(arr):
    """NaN-safe z-정규화"""
    a = np.array(arr, dtype=float)
    mask = ~np.isnan(a)
    if mask.sum() < 2:
        return np.zeros_like(a)
    mu = np.nanmean(a)
    sd = np.nanstd(a, ddof=0)
    if sd < 1e-12:
        return np.zeros_like(a)
    return (a - mu) / sd


def main():
    root = Path('.')
    ch3_path = root / 'ch3' / 'data.js'
    
    if not ch3_path.exists():
        print("ch3/data.js를 찾을 수 없습니다. I-mPine 루트에서 실행하세요.")
        sys.exit(1)
    
    ch3 = load_js_data(ch3_path, 'CH3_DATA')
    sgg_list = ch3['prioritySggList']
    
    print(f"입력: {len(sgg_list)}개 시군구")
    
    # ── 1) 모집단 제한: 피해밀도 > 0 OR 재발위험확률 > 0.5 ──────────
    # (피해 이력이 전혀 없는 도심 지역 제외)
    # 주의: 이 기준은 팀이 논의해서 확정해야 합니다.
    # 여기서는 "재발위험확률 > 0.05 또는 index_main > 0" 으로 느슨하게 잡습니다.
    # 더 엄격한 기준: 원자료에서 1회 이상 발생
    eligible = []
    excluded = []
    for r in sgg_list:
        prob = r.get('재발위험확률', 0) or 0
        idx = r.get('index_main', 0) or 0
        # 느슨한 기준: 적어도 하나라도 신호가 있는 곳
        if prob > 0.05 or idx > 0.3:
            eligible.append(r)
        else:
            excluded.append(r)
    
    print(f"모집단 제한: {len(eligible)}개 잔여 / {len(excluded)}개 제외")
    print(f"  제외 예시: {', '.join(r['시군구명'] for r in excluded[:10])}")
    
    # ── 2) z-정규화 가중결합 ─────────────────────────────────────
    idx_arr = [r['index_main'] for r in eligible]
    prob_arr = [r.get('재발위험확률', 0) or 0 for r in eligible]
    gap_arr = [-r['배분갭'] for r in eligible]  # 음수 반전: 과소배분이 높을수록 높은 값
    
    z_idx = zscore(idx_arr)
    z_prob = zscore(prob_arr)
    z_gap = zscore(gap_arr)
    
    W_IDX = 0.50   # 구조적 위험
    W_PROB = 0.50   # 재발위험확률
    W_GAP = 0.15    # 배분갭 (조정 요소)
    
    scores = W_IDX * z_idx + W_PROB * z_prob + W_GAP * z_gap
    
    # 순위 부여
    order = np.argsort(-scores)
    for rank, i in enumerate(order, 1):
        eligible[i]['priority_score_v2'] = round(float(scores[i]), 4)
        eligible[i]['priority_rank_v2'] = rank
    
    # 제외 지역은 rank = None
    for r in excluded:
        r['priority_score_v2'] = None
        r['priority_rank_v2'] = None
    
    # ── 3) 2×2 배분규칙 ─────────────────────────────────────────
    prob_median = np.median(prob_arr)
    
    # 현행 예산 수준: 배분갭의 부호 대신 평균예산_log 직접 사용
    # (배분갭은 위험지수로 보정한 잔차이므로 여기서는 원변수가 더 투명)
    # ch3/data.js에 평균예산이 없으므로 배분갭 부호로 대리
    gap_median = np.median([r['배분갭'] for r in eligible])
    
    for r in eligible:
        prob = r.get('재발위험확률', 0) or 0
        gap = r['배분갭']
        
        high_risk = prob >= prob_median
        low_budget = gap < gap_median  # 갭이 음수 = 예산이 적음
        
        if high_risk and low_budget:
            r['quadrant'] = '①최우선_증액'
        elif high_risk and not low_budget:
            r['quadrant'] = '②유지_점검'
        elif not high_risk and low_budget:
            r['quadrant'] = '③예찰_유지'
        else:
            r['quadrant'] = '④재배분_검토'
    
    for r in excluded:
        r['quadrant'] = '⑤대상외'
    
    # ── 출력 ─────────────────────────────────────────────────────
    result = eligible + excluded
    
    # 결과 요약
    print(f"\n=== 새 우선지원 TOP 20 ===")
    top20 = sorted(eligible, key=lambda r: r['priority_rank_v2'])[:20]
    for r in top20:
        prob = r.get('재발위험확률', 0) or 0
        print(f"  {r['priority_rank_v2']:3d}  {r['시도명'][:5]:5s} {r['시군구명']:8s}  "
              f"score={r['priority_score_v2']:+6.3f}  "
              f"idx={r['index_main']:+6.3f}  "
              f"재발={prob:.3f}  "
              f"갭={r['배분갭']:+7.3f}  "
              f"{r['quadrant']}")
    
    print(f"\n=== 2×2 분포 ===")
    from collections import Counter
    qcnt = Counter(r['quadrant'] for r in result)
    for q in sorted(qcnt):
        print(f"  {q}: {qcnt[q]}개")
    
    # Spearman 검증
    from scipy.stats import spearmanr
    valid_scores = [(r['priority_score_v2'], r.get('재발위험확률', 0) or 0) 
                    for r in eligible if r['priority_score_v2'] is not None]
    if valid_scores:
        ss, pp = zip(*valid_scores)
        rho, p = spearmanr(ss, pp)
        print(f"\n=== Spearman(new_score, 재발위험확률) = {rho:.4f} (p={p:.4g}) ===")
        print(f"    (기존: -0.4766 → 목표: 양의 상관)")
    
    # JSON 저장
    out_path = root / 'ch3' / 'data_priority_fixed.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'meta': {
                'formula': f'priority = {W_IDX}*z(index_main) + {W_PROB}*z(재발위험확률) + {W_GAP}*z(-배분갭)',
                'eligible_n': len(eligible),
                'excluded_n': len(excluded),
                'exclusion_criteria': '재발위험확률 <= 0.05 AND index_main <= 0.3',
                'note': '검증보고서 §2-A 권장 산식 적용. 팀 논의 후 가중치·모집단 기준 확정 필요.'
            },
            'prioritySggList': result
        }, f, ensure_ascii=False, indent=1)
    
    print(f"\n저장: {out_path}")
    print("→ 검증 후 ch3/data.js의 prioritySggList를 이 값으로 교체하세요.")


if __name__ == '__main__':
    main()
