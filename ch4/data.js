/* ============================================================================
   CH4_DATA — 맞춤형 방제 설계 계산기 (민간 업체용)
   ----------------------------------------------------------------------------
   ⚠️ 이 파일의 단가·1인당 작업량은 전부 추정치입니다. 실제 데이터가 프로젝트 안에
   존재하지 않아서(산림청 방제사업 표준시방서·품셈·실제 업체 견적 등 미확보)
   상식적으로 그럴듯한 값을 넣었습니다. 실제 자료가 확보되면 unitCost·
   dailyCapacityPerWorker만 교체하면 됩니다 — 계산 로직(ch4.html)은 안 바뀝니다.
   ============================================================================ */

window.CH4_DATA = {
  meta: {
    is_estimate: true,
    note: '단가·인당 작업량은 전부 추정치(공개 표준시방서·품셈 미확보). 실제 견적과 다를 수 있습니다.',
  },

  // unit: 'ha'(항공방제만 면적 기준) | '본'(나머지는 피해목 본수 기준)
  methods: [
    {
      key: 'aerial', name: '항공방제 (헬기 약제살포)', unit: 'ha',
      unitCost: 250000,            // 원/ha (추정)
      dailyCapacityPerWorker: 40,  // ha/인/일 — 감독·유도 인력 기준 (추정)
      minQuantity: 30,             // 최소 30ha 이상이어야 경제성 있음
      needsResidentialDistance: true, // 주거지와 일정 거리 이격 필요
      condition: '방제면적 30ha 이상 · 주거지 비인접 · 급경사 등 지상접근 곤란 지역에 적합',
    },
    {
      key: 'ground', name: '지상 약제방제 (나무주사)', unit: '본',
      unitCost: 45000,             // 원/본 (추정)
      dailyCapacityPerWorker: 20,  // 본/인/일 (추정)
      minQuantity: 0,
      needsResidentialDistance: false,
      condition: '도로 접근 가능 지역 · 중소규모 피해목에 적합',
    },
    {
      key: 'fumigation', name: '훈증처리', unit: '본',
      unitCost: 35000,             // 원/본 (추정)
      dailyCapacityPerWorker: 15,  // 본/인/일 (추정)
      minQuantity: 0,
      needsResidentialDistance: false,
      condition: '소규모·확산 초기 단계의 개별 감염목 처리에 적합',
    },
    {
      key: 'felling', name: '벌채 후 파쇄·소각', unit: '본',
      unitCost: 60000,             // 원/본 (추정, 벌채+파쇄+운반 포함)
      dailyCapacityPerWorker: 10,  // 본/인/일 (추정)
      minQuantity: 0,
      needsResidentialDistance: false,
      condition: '피해가 심각해 완전제거가 필요한 경우에 적합',
    },
  ],

  // 현장까지 거리에 따른 운반비 가산(추정) — freeKm 이내는 가산 없음
  distanceSurcharge: { freeKm: 10, pctPerKm: 0.5 }, // 10km 초과분 1km당 총비용의 0.5% 가산

  defaults: {
    area_ha: 50,
    treeCount: 800,
    budget_won: 30000000,
    workers: 10,
    distance_km: 5,
    nearResidential: false,
    targetDays: 7,
  },
};
