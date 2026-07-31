$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$Root = "C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
$Src = Join-Path $Root "data\CH4\ImPine_CH4_맞춤형방제설계_분석계획서_v3.docx"
$Dst = Join-Path $Root "data\CH4\ImPine_CH4_맞춤형방제설계_분석계획서_v4.docx"
$FallbackDst = Join-Path $Root "data\CH4\ImPine_CH4_맞춤형방제설계_분석계획서_v4_최종수정.docx"

# Copy even when Word/OneDrive is holding a read handle.
$inStream = [IO.File]::Open($Src, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
try {
  try {
    $outStream = [IO.File]::Open($Dst, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::None)
  } catch {
    Write-Host "Primary v4 is locked; writing fallback $FallbackDst"
    $Dst = $FallbackDst
    $outStream = [IO.File]::Open($Dst, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::None)
  }
  try { $inStream.CopyTo($outStream) } finally { $outStream.Close() }
} finally {
  $inStream.Close()
}

$zip = [System.IO.Compression.ZipArchive]::new([IO.File]::Open($Dst, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None), [System.IO.Compression.ZipArchiveMode]::Update)
try {
  $entry = $zip.GetEntry("word/document.xml")
  $reader = [IO.StreamReader]::new($entry.Open(), [Text.Encoding]::UTF8)
  $xmlText = $reader.ReadToEnd()
  $reader.Close()

  [xml]$doc = $xmlText
  $nsm = [System.Xml.XmlNamespaceManager]::new($doc.NameTable)
  $wNs = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  $nsm.AddNamespace("w", $wNs)

  function Get-ParaText($p) {
    (($p.SelectNodes(".//w:t", $nsm) | ForEach-Object { $_.'#text' }) -join "").Trim()
  }

  function Set-ParaText($p, [string]$text) {
    $texts = $p.SelectNodes(".//w:t", $nsm)
    if ($texts.Count -eq 0) { return }
    $texts[0].'#text' = $text
    for ($i = 1; $i -lt $texts.Count; $i++) { $texts[$i].'#text' = "" }
  }

  function New-WElement([string]$name) {
    return $doc.CreateElement("w", $name, $wNs)
  }

  function New-Paragraph([string]$text, [bool]$bold = $false) {
    $p = New-WElement "p"
    $r = New-WElement "r"
    if ($bold) {
      $rPr = New-WElement "rPr"
      $b = New-WElement "b"
      [void]$rPr.AppendChild($b)
      [void]$r.AppendChild($rPr)
    }
    $t = New-WElement "t"
    $space = $doc.CreateAttribute("xml", "space", "http://www.w3.org/XML/1998/namespace")
    $space.Value = "preserve"
    [void]$t.Attributes.Append($space)
    $t.InnerText = $text
    [void]$r.AppendChild($t)
    [void]$p.AppendChild($r)
    return $p
  }

  function New-BlankParagraph() {
    return New-Paragraph ""
  }

  function Insert-BeforeParagraphText([string]$anchorText, [string[]]$newTexts) {
    $body = $doc.SelectSingleNode("//w:body", $nsm)
    $paras = $doc.SelectNodes("//w:body/w:p", $nsm)
    $anchor = $null
    foreach ($p in $paras) {
      if ((Get-ParaText $p) -eq $anchorText) { $anchor = $p; break }
    }
    if ($null -eq $anchor) { throw "Anchor not found: $anchorText" }
    foreach ($line in $newTexts) {
      $isHeading = $line -match "^\d+\.\d+|\d+\.|^v4 "
      [void]$body.InsertBefore((New-Paragraph $line $isHeading), $anchor)
    }
  }

  # Targeted text updates.
  $paras = $doc.SelectNodes("//w:p", $nsm)
  foreach ($p in $paras) {
    $txt = Get-ParaText $p
    if ($txt -eq "2026. 07. 31.") {
      Set-ParaText $p "2026. 07. 31. (v4 보완)"
    } elseif ($txt -eq "시군구 1건(사용자 선택) × 방제방식 4종(항공·지상·훈증·벌채)") {
      Set-ParaText $p "시군구 1건(사용자 선택) × 현행 4종 + v4 확장 목표 2종(항공·지상·훈증·벌채·수간주사·드론)"
    } elseif ($txt -eq "GitHub 저장소 main 브랜치 ch4/ch4.html·data.js 구조 및 2023년 임업경영실태조사 마이크로데이터(산림청)") {
      Set-ParaText $p "GitHub 저장소 main 브랜치 ch4/ch4.html·data.js의 현행 구조, CH1~CH3 산출물, 2023년 임업경영실태조사 마이크로데이터(산림청), v4 보완 검토 결과"
    } elseif ($txt -like "*방제 방식을 임의로 추천하는 계산기*확보 가능한 항목*실측으로 교체하고*") {
      Set-ParaText $p "CH4는 방제 방식을 임의로 추천하는 계산기가 아니라, CH3에서 우선지원으로 선정된 지역의 공개 원자료 기준 규모(소나무류 면적 참고값·피해목 수)를 받아 실행 가능한 방제 계획을 산출하는 실행설계 단계로 설계한다. 확보 가능한 항목인 인건비는 임업경영실태조사 실측 중앙값을 참고치로 병기하되, 방제 방식별 단가 자체는 방제 전용 통계 부재로 추정치를 유지한다."
    } elseif ($txt -like "*최신 관리주기(2021.5~2022.4) 단일 주기로 재계산*전국 평균 8.63배*") {
      Set-ParaText $p "검증 가능한 최신 원자료 관리주기(2021.5~2022.4) 단일 주기로 재계산 - 6주기 누적 평균 8.63배 과대추정 제거, 단 2026년 현재 대비 과소추정 가능성은 별도 경고(2.4, 2.5 참조)"
    } elseif ($txt -like "CH1 원자료 재계산 기반 자동 입력 area_ha*treeCount*최신 관리주기 단일 값*") {
      Set-ParaText $p "CH1 원자료 재계산 기반 자동 입력 pine_area_ha_reference·treeCount(treeCount는 검증 가능한 최신 원자료 관리주기 단일 값, CH1 공백 지역은 전국임상도 참고치로 보완 표시). 실제 방제면적은 treatment_area_ha로 별도 확정"
    } elseif ($txt -eq "수간주사(명칭 정리)·드론방제(신규)를 포함한 확장된 방제방식 목록") {
      Set-ParaText $p "현행 4종 방식에 수간주사(명칭 정리)·드론방제(신규)를 추가하는 확장 목표 목록"
    } elseif ($txt -eq "피해목 수(treeCount)·소나무림 면적(area_ha)의 실측 근거") {
      Set-ParaText $p "피해목 수(treeCount)의 원자료 근거와 소나무류 면적 참고값(pine_area_ha_reference)의 근거"
    } elseif ($txt -eq "추천 방식 1~2개(기존 조건식 유지)") {
      Set-ParaText $p "현행 조건식 기준 추천 방식 1~2개 + v4 확장 방식은 구현 후 별도 표시"
    } elseif ($txt -eq "면적, 주거지 인접여부, 지상접근 가능성") {
      Set-ParaText $p "실제 방제면적(treatment_area_ha), 소나무류 면적 참고값, 주거지 인접여부, 지상접근 가능성"
    } elseif ($txt -eq "dailyCapacityPerWorker(추정), area_ha/treeCount") {
      Set-ParaText $p "dailyCapacityPerWorker(추정), treatment_area_ha/treeCount"
    } elseif ($txt -eq "area_ha, treeCount, targetDays 전달 성공률") {
      Set-ParaText $p "pine_area_ha_reference, treeCount, targetDays 전달 및 사용자가 treatment_area_ha를 확정하는 흐름의 성공률"
    } elseif ($txt -like "정태적 계산*연도 개념 없음*2023년 임업경영실태조사 기준 단가 적용*") {
      Set-ParaText $p "정태적 계산 - 2023년 임업경영실태조사 기준 단가 적용. 단, 피해목수는 공개 원자료 완결성을 우선해 2021.5~2022.4 관리주기를 기준으로 하며, 2026년 현재 규모와의 시간 격차를 별도 표시"
    } elseif ($txt -eq "사용자 선택 시군구 1건 × 방제방식 4종") {
      Set-ParaText $p "사용자 선택 시군구 1건 × 현행 4종 + v4 확장 목표 2종(수간주사·드론)"
    } elseif ($txt -eq "area_ha(방제대상 면적) 산출 근거 — 관측된 180개 시군구만 포함, 전수 아님") {
      Set-ParaText $p "pine_area_ha_reference(소나무류 면적 참고값) 산출 근거 - 관측된 180개 시군구만 포함, 전수 아님. 실제 방제면적(treatment_area_ha)은 이 값을 그대로 쓰지 않고 사용자 확인 또는 최신 설계자료로 확정"
    } elseif ($txt -eq "평균예산_log, 배분갭") {
      Set-ParaText $p "평균예산_log·배분갭(재선충명시 공식 기준), 원본 패널의 재선충명시/산림병해충포괄 원화예산"
    } elseif ($txt -eq "예산 적정성 맥락 참고(비용 대비 현행 예산 비교)") {
      Set-ParaText $p "CH2 공식 분석축은 재선충명시로 유지하고, CH4 실행비 비교에서는 재선충명시 예산과 산림병해충 포괄 예산을 분리 병기"
    } elseif ($txt -like "treeCount는 6주기 누적이 아니라 최신 관리주기(2021.5~2022.4)*") {
      Set-ParaText $p "treeCount는 6주기 누적이 아니라 공개 원자료에서 시군구 단위로 재현 가능한 최신 단일 관리주기(2021.5~2022.4)의 피해고사목수를 사용한다. 원본 CSV에서 CH1 노트북과 동일한 로직으로 이 값을 별도 재계산했으며, 결과는 data/CH4/ch4_treecount_latest_cycle.json에 저장했다. 기존 6주기 누적치는 참고용으로만 함께 남기되, 2026년 현재 전국 피해 규모가 크게 증가한 점은 별도 민감도 시나리오로 병기한다."
    } elseif ($txt -eq "area_ha, treeCount(최신 관리주기 기준, 6주기 누적 아님), budget_won, targetDays") {
      Set-ParaText $p "pine_area_ha_reference, treatment_area_ha(사용자 확정), treeCount(검증 가능한 최신 원자료 기준 + 참고 스케일업), budget_won_explicit/budget_won_broad, targetDays"
    } elseif ($txt -eq "CH2 배분갭·예산과 비교") {
      Set-ParaText $p "CH2 배분갭(재선충명시 공식 기준), 재선충명시 예산, 산림병해충 포괄 예산 보조값과 비교"
    } elseif ($txt -eq "실측(CH1, treeCount는 최신 관리주기 재계산치)") {
      Set-ParaText $p "B등급(공식 원자료 기반 재계산, 단 2026년 현재 대비 시간 격차 존재)"
    } elseif ($txt -like "방제 규모를 결정하는 핵심 근거*treeCount는 CH1 sggBurden*") {
      Set-ParaText $p "방제 규모를 결정하는 핵심 근거. treeCount는 CH1 sggBurden의 6주기 누적치가 아니라 2021.5~2022.4 원자료 재계산값이며, 현재 규모 판단에는 참고 스케일업값과 최신 현장자료 확인이 필요하다."
    } elseif ($txt -eq "실측(임업경영실태조사)") {
      Set-ParaText $p "C등급 근사 실측(임업경영실태조사, 방제 전용 조사는 아님)"
    } elseif ($txt -eq "CH2 원본 패널 대응자원투입예산_원(일반 산림병해충 대응예산, 최신 관측연도)") {
      Set-ParaText $p "CH2 원본 패널의 재선충명시 대응예산을 공식 기준으로 사용하고, 산림병해충 포괄 대응예산은 보조 참고값으로 병기"
    } elseif ($txt -like "주의*대시보드 표시값*재선충명시*완도군*") {
      Set-ParaText $p "주의 - CH2 취약성지수와 배분갭은 분석 일관성을 위해 재선충명시 예산을 유지한다. 다만 일부 지자체는 재선충 방제를 일반 산림병해충 방제 사업에 포괄 편성하므로, CH4 실행비 비교 화면에서는 재선충명시 예산을 보수적 기준으로, 산림병해충 포괄 예산을 참고 상한 기준으로 함께 제시한다. 포괄 예산은 재선충 전용 재원으로 해석하지 않는다."
    } elseif ($txt -like "연결 방식: CH3 화면에서 시군구를 클릭하면*ch4.html로 이동한다*") {
      Set-ParaText $p "연결 방식(설계 - 아직 미구현, 코드 검증 필요): CH3 화면에서 시군구를 클릭하면 맞춤형 방제 설계로 보내기 링크가 노출되고, 클릭 시 URL 쿼리파라미터로 값을 실어 ch4.html로 이동하도록 구현한다. 현재 저장소에서는 ch3.html에 ch4 연결 문자열이 없어 실제 구현 전 검증이 필요하다."
    } elseif ($txt -eq "CH3 prioritySggList.grade / 재발위험확률") {
      Set-ParaText $p "CH3 prioritySggList.grade 기반 내부 추정. 재발위험확률은 targetDays 산정값이 아니라 urgentList 교차조건용 참고값"
    } elseif ($txt -like "본 계산기는 선택 지역의 방제 규모*인건비는 2023년 임업경영실태조사*") {
      Set-ParaText $p "본 계산기는 선택 지역의 방제 규모(면적·피해목 수)를 기반으로 적합한 방제 방식과 예상 비용·소요기간을 제시한다. 인건비는 2023년 임업경영실태조사 실측 중앙값(20만원/인/일, n=57)을 반영했으며, 장비비·재료비·방식별 작업량 등 나머지 항목은 추정치다. 따라서 CH4는 확정 견적 도구가 아니라 실측 입력값과 추정 방제비를 비교하는 실행 가능성 시뮬레이터로 해석한다."
    } elseif ($txt -like "treeCount는 6주기 누적치가 아니라 최신 관리주기 재계산치로 교체했지만*") {
      Set-ParaText $p "treeCount는 6주기 누적치가 아니라 검증 가능한 최신 원자료 관리주기 재계산치로 교체했지만, 그래도 등록 건수이지 실제 방제 대상 나무 수와 완전히 같지는 않다. 또한 2026년 현재 전국 피해고사목 규모가 2021.5~2022.4 대비 약 4.7배 증가했으므로, 현재 물량은 지역별로 더 클 수 있다."
    } elseif ($txt -eq "전체 흐름(CH3 클릭 → CH4 자동입력 → 결과 표시) 점검") {
      Set-ParaText $p "전체 흐름(CH3 클릭 또는 지역 선택 → CH4 자동입력/수동확정 → 결과 표시) 점검. 현재 저장소 구현 상태에서는 CH3→CH4 URL 전달 및 CH4 파라미터 파싱 구현 여부를 별도 코드 검증 필요"
    } elseif ($txt -like "CH4는 ① CH1 실측 데이터*") {
      Set-ParaText $p "CH4는 ① CH1 공개 원자료 기반 피해목 수와 소나무류 면적 참고값 연계, ② 임업경영실태조사 마이크로데이터 실측 인건비의 참고치 병기, ③ 재선충명시 예산을 공식 기준으로 두고 산림병해충 포괄 예산을 보조 시나리오로 병기, ④ 2026년 현재와의 시간 격차 및 실측/추정 항목의 투명한 구분 공개, ⑤ 현재 구현과 개선 목표의 분리 관리를 원칙으로 확정한다."
    }
  }

  $section25 = @(
    "2.5 공개 원자료 시점 격차와 2026년 현재 과소추정 가능성",
    "v3에서 가장 큰 오류였던 6주기 누적치 사용 문제는 해결했지만, 2021.5~2022.4 원자료를 2026년 현재 실행 물량으로 그대로 읽으면 반대 방향의 과소추정 문제가 남는다. 산림청 발표 기준 전국 피해고사목은 2021.5~2022.4 약 37.8만 그루에서 2025.6~2026.5 약 177만 그루로 증가했으므로, 전국 총량 기준 약 4.7배 차이가 있다.",
    "이 차이는 계산 오류가 아니라 공개 원자료의 완결성 문제에서 온다. CH1 원자료 검증에서 2022.5~2023.4 주기는 공식 총계의 약 44.6%만 포함되어 있어 시군구 단위 실행 물량 산정에 그대로 쓰기 어렵다. 따라서 CH4는 시군구 단위로 재현 가능한 2021.5~2022.4 값을 기준값으로 쓰되, 2026년 현재 규모와의 차이를 경고문과 민감도 시나리오로 별도 표시한다.",
    "화면 표시 원칙: ① 검증 원자료 기준 treeCount, ② 전국 증가율을 단순 적용한 참고 스케일업 treeCount를 나란히 보여준다. 두 번째 값은 지역별 실측치가 아니라 전국 총량 증가율을 반영한 민감도 시나리오이며, 실제 계약·방제 설계 전에는 최신 지자체 예찰자료 또는 산림청 확정자료로 교체해야 한다.",
    ""
  )
  Insert-BeforeParagraphText "3. 최종 분석 프레임" $section25

  $section51 = @(
    "5.1 예산 기준 이중화: 재선충명시 공식 기준 + 포괄 예산 보조 기준",
    "CH2의 지자체대응역량과 예산배분 갭은 재선충병으로 명시된 예산을 기준으로 산정했으므로, CH4에서도 공식 예산 기준은 재선충명시 값을 유지한다. 이는 CH2→CH3→CH4의 분석축을 흔들지 않기 위한 원칙이다.",
    "다만 예산서상 재선충 방제가 일반 산림병해충 방제 사업에 포괄 편성되는 지자체가 있다. 완도군처럼 재선충명시 예산은 0이지만 산림병해충 포괄 대응예산은 존재하는 사례가 있으므로, 포괄 예산을 완전히 배제하면 실제 가용 예산을 과소평가할 수 있다.",
    "따라서 CH4 화면은 재선충명시 예산을 '보수적 전용예산 기준', 산림병해충 포괄 대응예산을 '참고 상한 기준'으로 함께 제시한다. 예찰진단 예산과 이동통제 예산은 직접 방제비로 차감하지 않고, 사전 탐지·진단 및 인위적 확산 차단 역량을 설명하는 보조 지표로만 사용한다.",
    ""
  )
  Insert-BeforeParagraphText "6. 화면 설계 수정사항" $section51

  $section61 = @(
    "6.1 실측·추정 신뢰등급 표시",
    "CH4의 모든 입력값과 산출값에는 신뢰등급을 붙인다. A등급은 원자료 실측 또는 공식 집계값, B등급은 공식 원자료 기반 재계산값, C등급은 다른 조사에서 가져온 근사 실측값, D등급은 내부 추정치다.",
    "A/B: 재선충명시·산림병해충 포괄 예산, CH1 원자료 기반 treeCount, 소나무류 면적. C: 2023년 임업경영실태조사 인건비 20만원/인/일(방제 전용 조사가 아니라 영림업 및 목재수확업 근사치). D: unitCost 중 장비비·재료비, dailyCapacityPerWorker, targetDays, 드론방제·수간주사 단가.",
    "결과 해석은 '실측 인건비를 일부 반영한 추정 계산'으로 제한한다. '실측 기반 방제비' 또는 '확정 견적'처럼 보이는 표현은 사용하지 않는다.",
    ""
  )
  Insert-BeforeParagraphText "7. 결과 해석 문장 템플릿 및 주의사항" $section61

  $section62 = @(
    "6.2 CH1~CH3 연결 및 구현 정합성 체크",
    "문서상 연결 목표와 현재 화면 구현을 분리해 관리한다. 현재 ch4/data.js는 4개 방식 중심의 정적 계산기 구조이며, v4에서 제안한 수간주사·드론 분리, laborBased 플래그, 재선충명시/포괄 예산 이중 표시, treeCount 참고 스케일업값은 구현 반영이 필요하다.",
    "CH1 연결 체크: treeCount는 data/CH4/ch4_treecount_latest_cycle.json의 2021.5~2022.4 재계산값을 기준으로 쓰고, 6주기 누적값은 참고용 필드로만 보존한다. area_ha는 피해면적이 아니라 소나무류 면적 참고값이므로 treatment_area_ha와 분리한다.",
    "CH2 연결 체크: CH2의 공식 지자체대응역량과 배분갭은 재선충명시 예산으로 계산되었으므로, CH4의 기본 예산 비교도 재선충명시를 우선한다. 산림병해충 포괄 예산, 예찰진단 예산, 이동통제 예산은 보조 지표 또는 참고 상한으로만 표시한다.",
    "CH3 연결 체크: CH3는 지역 선택, grade, 재발위험확률, 정책유형을 CH4에 넘기는 입력 트리거 역할을 한다. targetDays는 grade 기반 내부 추정이므로 공식 기준처럼 보이지 않게 표시하고, 사용자가 수정할 수 있어야 한다.",
    ""
  )
  Insert-BeforeParagraphText "7. 결과 해석 문장 템플릿 및 주의사항" $section62

  $section91 = @(
    "9.1 v4 최종 반영 사항",
    "v4에서는 이전 검토에서 확인된 심사 리스크를 모두 반영했다. 2021.5~2022.4 기준 treeCount의 현재 과소추정 가능성, CH2 재선충명시 예산축과 CH4 포괄 예산 보조값의 분리, 대부분의 단가·작업량이 추정치라는 한계, 0장 인건비 '실측 교체' 표현의 과장, area_ha의 피해면적 오인 위험, CH3→CH4 자동전달 구현 검증 필요성, 현행 4종 구현과 v4 확장 목표의 불일치를 명시적으로 정리했다.",
    "심사 대응 문장: CH4는 공식 견적 산출기가 아니라, 검증 가능한 원자료와 일부 근사 실측 인건비 참고치를 바탕으로 방제 규모·예산 여력·실행 가능성을 비교하는 의사결정 보조 도구다. 최신 지자체 실측 물량과 업체 견적이 확보되면 treeCount, treatment_area_ha, unitCost, dailyCapacityPerWorker를 교체하도록 설계한다.",
    ""
  )
  Insert-BeforeParagraphText "참고자료" $section91

  $entry.Delete()
  $newEntry = $zip.CreateEntry("word/document.xml")
  $writer = [IO.StreamWriter]::new($newEntry.Open(), [Text.Encoding]::UTF8)
  try { $writer.Write($doc.OuterXml) } finally { $writer.Close() }
} finally {
  $zip.Dispose()
}

Write-Host "Created $Dst"
