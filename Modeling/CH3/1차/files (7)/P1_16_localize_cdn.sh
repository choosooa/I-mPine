#!/bin/bash
# P1 #16 — CH2/CH3의 외부 CDN 의존을 로컬 vendor로 전환
# 실행: I-mPine 루트에서 bash patches/P1_16_localize_cdn.sh
#
# CH1은 이미 vendor/ 폴더에 leaflet + chart.js를 가지고 있습니다.
# CH2/CH3만 unpkg.com, cdnjs.cloudflare.com을 씁니다.
# 발표장 인터넷이 끊기면 CH2/CH3 지도와 차트가 전멸합니다.

set -e
echo "=== CDN → 로컬 vendor 전환 ==="

# ch2.html
echo "[ch2/ch2.html] 패치 중..."
sed -i.bak \
  -e 's|https://unpkg.com/leaflet@[^/]*/dist/leaflet.css|../ch1/vendor/leaflet/leaflet.css|g' \
  -e 's|https://unpkg.com/leaflet@[^/]*/dist/leaflet.js|../ch1/vendor/leaflet/leaflet.js|g' \
  -e 's|https://cdnjs.cloudflare.com/ajax/libs/Chart.js/[^/]*/chart.umd.js|../ch1/vendor/chart.umd.js|g' \
  -e 's|https://cdnjs.cloudflare.com/ajax/libs/Chart.js/[^/]*/chart.umd.min.js|../ch1/vendor/chart.umd.js|g' \
  ch2/ch2.html

# ch3.html
echo "[ch3/ch3.html] 패치 중..."
sed -i.bak \
  -e 's|https://unpkg.com/leaflet@[^/]*/dist/leaflet.css|../ch1/vendor/leaflet/leaflet.css|g' \
  -e 's|https://unpkg.com/leaflet@[^/]*/dist/leaflet.js|../ch1/vendor/leaflet/leaflet.js|g' \
  -e 's|https://cdnjs.cloudflare.com/ajax/libs/Chart.js/[^/]*/chart.umd.js|../ch1/vendor/chart.umd.js|g' \
  -e 's|https://cdnjs.cloudflare.com/ajax/libs/Chart.js/[^/]*/chart.umd.min.js|../ch1/vendor/chart.umd.js|g' \
  ch3/ch3.html

echo ""
echo "=== 검증 ==="
for f in ch2/ch2.html ch3/ch3.html; do
  cdn=$(grep -c 'unpkg.com\|cdnjs.cloudflare' "$f" || true)
  local=$(grep -c '../ch1/vendor' "$f" || true)
  echo "  $f: CDN 참조 ${cdn}개 / 로컬 참조 ${local}개"
  if [ "$cdn" -gt 0 ]; then
    echo "    ⚠ 아직 CDN 참조가 남아 있습니다. 수동 확인 필요:"
    grep -n 'unpkg.com\|cdnjs.cloudflare' "$f" | head -5
  fi
done

echo ""
echo "=== 오프라인 테스트 방법 ==="
echo "  1) Wi-Fi 끄기"
echo "  2) python3 -m http.server 8000"
echo "  3) http://localhost:8000/통합대시보드_개선안.html 에서 CH2/CH3 탭 확인"
echo "  4) 지도와 차트가 모두 렌더링되면 성공"
echo ""
echo "원본은 .bak 파일로 백업되어 있습니다."
