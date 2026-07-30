/**
 * ═══════════════════════════════════════════════════════════════════
 * SGG_CODE_ALIAS — 강원특별자치도 행정코드 개편 폴백
 * ═══════════════════════════════════════════════════════════════════
 * 
 * 문제: CH1_GEOJSON은 구 강원도 코드(42xxx)를 사용하고,
 *       CH2/CH3 data.js는 강원특별자치도 코드(51xxx)를 사용합니다.
 *       → 강원 18개 시군구가 지도에 그려지지 않음
 *
 * 사용법: ch2.html, ch3.html의 지도 렌더링 함수에서
 *         sgg_code로 GeoJSON feature를 찾기 전에 이 함수를 호출하세요.
 *
 *   // BEFORE:
 *   const feature = geoIndex[code];
 *
 *   // AFTER:
 *   const feature = geoIndex[resolveCode(code)] || geoIndex[code];
 *
 * 서울·인천·충북의 누락(45곳)은 GeoJSON 자체에 폴리곤이 없어서이므로
 * 이 패치로는 안 됩니다. 근본 해결은 KOSTAT 2023년판 경계 파일 교체입니다.
 * 
 * 검증: node -e "..." 으로 18/18 매칭 확인 완료 (검증보고서 §2-C 참조)
 * ═══════════════════════════════════════════════════════════════════
 */

// 강원특별자치도(51xxx) → 구 강원도(42xxx) 폴백
// 하위 3자리가 동일하므로 규칙 기반으로 처리
function resolveCode(code) {
  const s = String(code);
  if (s.startsWith('51')) return '42' + s.slice(2);
  return s;
}

// ch2.html, ch3.html에서 sgg_codes 배열을 순회할 때:
// (r.sgg_codes || []).forEach(code => {
//   const resolved = resolveCode(code);
//   const feature = geoIndex[resolved] || geoIndex[code];
//   if (feature) { /* 칠하기 */ }
// });

// ── 아래는 ch2.html / ch3.html 내부에 적용하는 구체적 패치 지침 ──────
// 
// 1) ch2.html에서 "const geoIndex = {};" 직후에:
//    function resolveCode(c){var s=String(c);return s.startsWith('51')?'42'+s.slice(2):s;}
//
// 2) GeoJSON feature를 코드로 찾는 모든 곳에서:
//    geoIndex[code]  →  (geoIndex[resolveCode(code)] || geoIndex[code])
//
// 3) ch3.html에도 동일하게 적용
//
// 예상 복구: 18/63 시군구 (강원 전체). 나머지 45곳은 GeoJSON 교체 필요.
