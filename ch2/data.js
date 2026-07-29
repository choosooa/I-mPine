/* ============================================================================
   CH2_DATA — 방제취약성지수 및 맞춤형 예산배분 모델링 대시보드용 데이터 스키마
   ----------------------------------------------------------------------------
   ⚠️ 이 파일은 전부 목업(MOCK)입니다. 실측값이 하나도 없습니다.
   병합·모델링 결과가 나오면, 아래 MOCK 생성 블록을 실제 계산 결과로
   "키(key) 이름을 그대로 유지한 채" 교체하면 ch2.html은 코드 수정 없이 그대로 동작합니다.

   실제 데이터로 교체할 때 지켜야 할 것:
   - sgg_cd는 5자리 법정동코드 문자열(예: "27110")
   - 분석계획 상 표본은 229개 시군구 · 2017–2022 (대구 중구·영등포구 제외, 강화군 포함)
   - within-year 표준화가 주 지수 기준, pooled는 참고용
   - 모형 A 주 사양 = CRE + Poisson(offset=log 소나무림면적), 나머지는 강건성 부록
   - 모형 B는 1단계(배분갭)까지만 정책결론 사용, 2·3단계는 IV/event study 확보 전 탐색적 표시
   ============================================================================ */

(function () {
  // ── 시드 고정 난수 (매번 같은 목업 값이 나오도록) ──────────────────────────
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rnd = mulberry32(20260729);
  const gauss = () => {
    let u = 0, v = 0;
    while (u === 0) u = rnd();
    while (v === 0) v = rnd();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  };
  const clamp01 = (x) => Math.max(0, Math.min(1, x));

  // ── 분석 대상 시군구 목록: KOREA_GEO(ch1/korea_geo.js)에서 끌어옴 ──────────
  // TODO(병합 담당): 실제 CH2 표본은 229개(시 통합) 단위입니다.
  // KOREA_GEO는 CH1 지도용 240개(일반구 분리) 단위이므로, 목업 단계에서만 재사용합니다.
  // 실제 데이터 반영 시 sggIndex의 sgg_cd·시도명·시군구명을 229 단위 병합 패널 기준으로 교체하세요.
  const GEO_FEATS = (typeof KOREA_GEO !== 'undefined' && KOREA_GEO.features) ? KOREA_GEO.features : [];
  const EXCLUDED_CODES = ['27110', '11560']; // 대구 중구 · 서울 영등포구 (소나무림면적=0, 추정표본 제외)
  const sggBase = GEO_FEATS
    .map(f => ({ sgg_cd: f.properties.code, 시도명: f.properties.sido, 시군구명: f.properties.name }))
    .filter(r => !EXCLUDED_CODES.includes(r.sgg_cd));

  // 목업 fallback: KOREA_GEO 로드 실패 시에도 대시보드가 빈 화면이 되지 않도록 최소 표본 확보
  const FALLBACK_SGG = [
    ['47130', '경상북도', '포항시'], ['47130', '경상북도', '경주시'], ['48250', '경상남도', '밀양시'],
    ['48310', '경상남도', '창녕군'], ['31710', '울산광역시', '울주군'], ['41830', '경기도', '양평군'],
    ['47230', '경상북도', '안동시'], ['43800', '충청북도', '제천시'], ['48170', '경상남도', '진주시'],
    ['46870', '전라남도', '해남군'],
  ].map(([c, s, n]) => ({ sgg_cd: c, 시도명: s, 시군구명: n }));
  const SGG_LIST = sggBase.length ? sggBase : FALLBACK_SGG;
  const N = SGG_LIST.length;

  // ── 시군구별 도메인 점수 + 지수 목업 생성 ──────────────────────────────────
  // 실제 계산 시: 도메인당 0~1 정규화 후 4개 도메인 평균 = index_main (표준화가중합, within-year 기준)
  const sggIndex = SGG_LIST.map((r, i) => {
    const base = clamp01(0.5 + gauss() * 0.22); // 시군구 고유 취약도 성향(도메인 간 상관 부여용)
    const dom_노출도 = clamp01(base * 0.6 + rnd() * 0.4);
    const dom_기후 = clamp01(base * 0.4 + rnd() * 0.6);
    const dom_역량 = clamp01(base * 0.3 + rnd() * 0.7); // 이미 역부호 반영된 값(높을수록 대응역량 취약)
    const dom_확산 = clamp01(base * 0.5 + rnd() * 0.5);
    const index_main = (dom_노출도 + dom_기후 + dom_역량 + dom_확산) / 4;
    const index_pca = clamp01(index_main + gauss() * 0.05);
    const index_geo = clamp01(Math.pow(dom_노출도 * dom_기후 * dom_역량 * dom_확산, 0.25) + gauss() * 0.02);
    const index_ex역량 = clamp01((dom_노출도 + dom_기후 + dom_확산) / 3);
    // 실제 계산 시: 소나무류_면적_ha < 500 인 시군구를 표본부족으로 플래그(체크리스트 "면적하한미달_flag" — 지수 분산 3.7배 폭발 근거)
    const 면적하한미달_flag = rnd() < 0.05;
    return {
      sgg_cd: r.sgg_cd, 시도명: r.시도명, 시군구명: r.시군구명,
      dom_노출도: +dom_노출도.toFixed(3), dom_기후위험도: +dom_기후.toFixed(3),
      dom_지자체역량_역: +dom_역량.toFixed(3), dom_인위적확산: +dom_확산.toFixed(3),
      index_main: +index_main.toFixed(3),        // 주 지수: 표준화 가중합(within-year)
      index_pooled: +clamp01(index_main + gauss() * 0.03).toFixed(3),
      index_pca: +index_pca.toFixed(3),           // 강건성: PCA
      index_geo: +index_geo.toFixed(3),           // 강건성: 기하평균(보상성 제거)
      index_ex역량: +index_ex역량.toFixed(3),      // 강건성: 지자체대응역량 제외
      면적하한미달_flag,                            // true면 지도엔 표시하되 순위표에서는 제외
      _base: base,
    };
  });
  sggIndex.sort((a, b) => b.index_main - a.index_main);
  sggIndex.forEach((r, i) => { r.rank_within = i + 1; });

  // ── 지수-피해 관계 목업 (모형 A 검증용) ────────────────────────────────────
  // 실제 계산 시: log_피해밀도_본per_ha(Y)와 index_main의 실측 관계로 교체
  const damageBySgg = sggIndex.map(r => {
    const logDamage = -1.2 + r._base * 3.4 + gauss() * 0.9; // 지수와 상관은 있으나 잡음 큰 관계
    return { sgg_cd: r.sgg_cd, log_피해밀도: logDamage, 피해밀도_본per_ha: Math.max(0, Math.exp(logDamage) - 1) };
  });
  const damageMap = {}; damageBySgg.forEach(d => damageMap[d.sgg_cd] = d);
  sggIndex.forEach(r => {
    const d = damageMap[r.sgg_cd];
    r.log_피해밀도 = +d.log_피해밀도.toFixed(3);
    r.피해밀도_본per_ha = +d.피해밀도_본per_ha.toFixed(3);
  });

  // 십분위표
  const decileRows = [];
  const perDecile = Math.floor(N / 10) || 1;
  for (let d = 0; d < 10; d++) {
    const slice = sggIndex.slice(d * perDecile, d === 9 ? N : (d + 1) * perDecile);
    if (!slice.length) continue;
    const meanIdx = slice.reduce((s, r) => s + r.index_main, 0) / slice.length;
    const meanDmg = slice.reduce((s, r) => s + (damageMap[r.sgg_cd]?.피해밀도_본per_ha || 0), 0) / slice.length;
    decileRows.push({ decile: d + 1, n: slice.length, mean_index: +meanIdx.toFixed(3), mean_damage: +meanDmg.toFixed(3) });
  }

  // ── 예산배분 갭 목업 (모형 B 1단계) ────────────────────────────────────────
  const budgetGap = sggIndex.map(r => {
    const budget_log = 2.5 + rnd() * 2.2 - r._base * 0.3; // 취약성과 약한 음의 관계(배분갭 시사)
    const predicted = 2.2 + r.index_main * 1.6;
    const gap = +(budget_log - predicted).toFixed(3);
    return {
      sgg_cd: r.sgg_cd, 시도명: r.시도명, 시군구명: r.시군구명,
      index_main: r.index_main, 대응자원투입예산_ha당_log: +budget_log.toFixed(3),
      배분갭: gap, 배분갭_방향: gap < -0.15 ? '과소배분(취약 대비)' : (gap > 0.15 ? '과다배분(취약 대비)' : '평균 수준'),
    };
  });
  const underfunded = budgetGap.filter(r => r.배분갭_방향 === '과소배분(취약 대비)').length;
  const overfunded = budgetGap.filter(r => r.배분갭_방향 === '과다배분(취약 대비)').length;

  // ── 상관/성과지표 목업 ─────────────────────────────────────────────────────
  function spearman(xs, ys) {
    const rank = arr => { const idx = arr.map((v, i) => i).sort((a, b) => arr[a] - arr[b]);
      const r = new Array(arr.length); idx.forEach((v, i) => r[v] = i + 1); return r; };
    const rx = rank(xs), ry = rank(ys); const n = xs.length;
    let d2 = 0; for (let i = 0; i < n; i++) d2 += (rx[i] - ry[i]) ** 2;
    return +(1 - (6 * d2) / (n * (n * n - 1))).toFixed(3);
  }
  const idxArr = sggIndex.map(r => r.index_main);
  const dmgArr = sggIndex.map(r => damageMap[r.sgg_cd].피해밀도_본per_ha);
  const spearmanIndexDamage = spearman(idxArr, dmgArr);
  const gapArr = budgetGap.map(r => r.대응자원투입예산_ha당_log);
  const spearmanBudgetIndex = spearman(idxArr, gapArr);

  const top20N = Math.max(1, Math.round(N * 0.2));
  const top20byIndex = new Set(sggIndex.slice(0, top20N).map(r => r.sgg_cd));
  const damageSortedDesc = [...damageBySgg].sort((a, b) => b.피해밀도_본per_ha - a.피해밀도_본per_ha).map(d => d.sgg_cd).slice(0, top20N);
  const hit = damageSortedDesc.filter(c => top20byIndex.has(c)).length;
  const aucTop20 = +(0.62 + (hit / top20N) * 0.25).toFixed(3); // 대략적 목업 근사치(실제는 ROC 적분으로 계산)

  window.CH2_DATA = {
    meta: {
      n_sgg: N,
      period: '2017–2022',
      excluded_note: '대구 중구·영등포구 제외(소나무림면적=0, 순수 도심 구조적 0) · 강화군 포함(재매칭 복원)',
      standardization_main: 'within-year (연도 내 상대순위)',
      standardization_alt: 'pooled (전국 z-score, 참고용)',
      index_method_main: '도메인당 1점 정규화 → 4도메인 동일가중 합산',
      model_a_main_spec: 'CRE(상관확률효과) + Poisson(offset=log 소나무림면적)',
      model_b_status: '1단계(배분갭 진단)까지만 정책결론 사용 · 2·3단계는 IV/event study 확보 전 탐색적 보고',
      domains: ['노출도', '기후위험도', '지자체대응역량(역부호)', '인위적확산'],
      is_mock: true,
    },

    // ── 실측 내용(목업 아님) — CH2_우선순위체크리스트_v2_및_최종변수리스트.html 확정본 그대로 ──
    variableList: {
      Y: [
        { v: 'log_피해밀도_본per_ha', role: '메인 Y', note: '노출도. 229 전체 · 실측 6년(2017–2022)' },
        { v: '당해_감염지점수 / 재발생률_300m 등', role: '로버스트니스', note: '지자체 파일 자체 성과변수(250단위, 다른 정의) — 교차검증용' },
      ],
      기후위험도: [
        { v: 'GDD_솔수염하늘소_base11.9', role: '주', note: '유일한 온도 대표변수' },
        { v: '연강수량_mm', role: '주', note: '' },
        { v: '평균풍속_ms', role: '주', note: '' },
        { v: 'SPI3_최저월(최심가뭄)', role: '주', note: '유효월수<11 NaN 처리 후' },
        { v: '겨울철_평균최저기온 / 여름철_평균기온', role: '제외', note: 'GDD와 between VIF 27~46 — 동시 투입 금지' },
      ],
      노출도: [
        { v: '소나무류_면적비율(%)', role: '주', note: '핵심 노출 지표' },
        { v: 'log_인접시군_피해밀도_본per_ha', role: '진단전용', note: '공간시차 — 설명변수 투입 금지, Moran\'s I·SAR/SLX 진단용' },
        { v: '연속발생연수 / 집단발생여부', role: '보조', note: '결과 인접 변수, 신중히 사용' },
        { v: '최근감염목과의_거리_km', role: '제외', note: '값 오류(2016=2019=2020=2023 완전 동일) — 재계산 전까지 사용 불가' },
      ],
      인위적확산: [
        { v: '도로소나무비율_500m', role: '주', note: '면적 통제 후 부호 (+). log(소나무림면적) 동반 필수' },
        { v: 'log1p_원목생산업체수', role: '주(재해석)', note: '면적 통제 후 부호 (−)' },
        { v: '주거지소나무비율_300m', role: '제외', note: '도로비율과 r=0.82, 시불변(전 시군구 SD=0)' },
      ],
      지자체대응역량_역부호: [
        { v: '대응자원투입예산_소나무림ha당_log', role: '주', note: 'VIF 1.12, t-1 시차 투입' },
        { v: '예찰진단예산_소나무림ha당_log', role: '주', note: '2017–2023 한정(2016 제외), t-1 시차 투입' },
        { v: '방제법인수_소나무림1만ha당_log', role: '보조', note: '2016–2021 한정' },
        { v: '이동통제예산_* / 예산비중_*', role: '민감도만', note: '배분구조 해석용, 메인 모형 제외' },
        { v: '반출금지구역_지정여부 / 면적비율', role: '주의·제외', note: '내생성(피해→지정), 분모오류(최대 204%) 확인 필요' },
      ],
    },

    // 1,832행(229×8년) → 최종 추정표본까지의 처리 흐름 (실측 · 목업 아님)
    sampleFunnel: [
      { step: '전체 패널', n: 1832, note: '229 시군구 × 8개년(2016–2023)' },
      { step: '소나무림면적=0 제외', n: 1816, note: '대구 중구·영등포구 16행 제외(순수 도심 구조적 0)' },
      { step: '분석표본_메인 (2017–2022)', n: 1374, note: '229 × 6개년. 2016은 t-1 시차 공급용으로만 활용, 대입 없이 제외' },
      { step: '국가대응수준 서브샘플 (참고)', n: 248, note: '31개 시군구 × 8년 — selection-on-outcome(피해 심한 곳이 선택됨), 로버스트니스 전용' },
    ],

    sggIndex: sggIndex.map(({ _base, ...rest }) => rest), // 내부 계산용 _base 필드는 노출 안 함

    stability: {
      leaveOneOut: [
        { 제외도메인: '노출도', top20_변경_개수: 4, spearman_vs_full: 0.91 },
        { 제외도메인: '기후위험도', top20_변경_개수: 3, spearman_vs_full: 0.94 },
        { 제외도메인: '지자체대응역량', top20_변경_개수: 6, spearman_vs_full: 0.87 },
        { 제외도메인: '인위적확산', top20_변경_개수: 2, spearman_vs_full: 0.96 },
      ],
      monteCarlo: { 시행횟수: 1000, 가중치범위: '±20%', top20_중위_유지율_pct: 82.4, 순위상관_중위: 0.89 },
      top20StabilityNote: 'OECD/JRC 복합지표 매뉴얼 방식 — 상위 20% 집합의 시뮬레이션 간 순위안정성',
    },

    validity: {
      spearman_index_damage: spearmanIndexDamage,
      aucTop20: aucTop20,
      decile: decileRows,
      modelCompare: [
        { spec: 'CRE + Poisson(offset=log면적)', role: '주 사양', coef_index: 1.42, se: 0.31, p: '<0.01', fit: 'Pseudo-R² 0.28' },
        { spec: 'CRE + log-linear', role: '강건성', coef_index: 0.88, se: 0.22, p: '<0.01', fit: 'R² 0.19' },
        { spec: 'Two-way FE + log-linear', role: '강건성(폐기 사유 확인용)', coef_index: 0.31, se: 0.28, p: '0.27', fit: 'R² 0.41 (내 변이 흡수)' },
      ],
      detectionBiasNote: '예찰예산↑→발견↑→관측피해↑ 기계적 관계 가능 — 예찰강도 통제 확보 전까지 계수는 참고용',
    },

    budgetGap: budgetGap,
    budgetGapSummary: {
      spearman_budget_vs_index: spearmanBudgetIndex,
      n_underfunded_highvuln: underfunded,
      n_overfunded_lowvuln: overfunded,
      note: '이 잔차는 "현행 평균 배분관행 대비 편차"이며 "최적 대비 부족"이 아님',
    },

    robustness: {
      natlResponse: { n: 248, subgroup: 31, damage_mean_included: 0.101, damage_mean_excluded: 0.040, t: 5.56, p: '<0.0001',
        note: '31개 시군구는 대표성이 낮은 게 아니라 피해가 심해 국가관리 대상이 된 selection-on-outcome' },
      holdout: {
        method: 'rolling-origin (2023 단일 홀드아웃 폐기)',
        rounds: [
          { origin: '≤2020 → 2021', rmse: 0.412 },
          { origin: '≤2021 → 2022', rmse: 0.389 },
          { origin: '≤2022 → 2023', rmse: 0.457 },
        ],
      },
      preRegisteredSpec: [
        { item: '표본', value: '2017–2022 · 대구중구·영등포구 제외 · 강화군 포함' },
        { item: '지수', value: '표준화 가중합(within-year) · 지자체대응역량 t-1 포함' },
        { item: '모형 A', value: 'CRE + Poisson-offset' },
        { item: '모형 B', value: '1단계만 정책결론 사용, 2·3단계 탐색적' },
      ],
      appendixOnly: ['Two-way FE 비교', 'PCA 지수', 'log-linear', '2016 포함판', '국가대응수준 서브모형'],
    },
  };
})();
