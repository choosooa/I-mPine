$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Root = "C:\Users\SAMSUNG\OneDrive\바탕 화면\공모전\Final_file\I-m_Pine"
$OutRoot = Join-Path $Root "Modeling\CH4\2차"
$OutData = Join-Path $OutRoot "data"
$OutScript = Join-Path $OutRoot "script"
$InputJson = Join-Path $Root "Modeling\CH4\1차\data\ch4_input_data.json"
$TreeJson = Join-Path $Root "Modeling\CH4\1차\data\ch4_treecount_latest_cycle.json"
$PanelCsv = Join-Path $Root "Modeling\CH2\6차\CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
$Ch3Html = Join-Path $Root "ch3\ImPine_ver4\ImPine\ch3\ch3.html"

New-Item -ItemType Directory -Force -Path $OutRoot, $OutData, $OutScript | Out-Null

function Write-Utf8Bom($Path, [string]$Content) {
  [System.IO.File]::WriteAllText($Path, $Content, [System.Text.UTF8Encoding]::new($true))
}

function Read-Json($Path) {
  Get-Content -LiteralPath $Path -Encoding UTF8 -Raw | ConvertFrom-Json
}

function To-NullableDouble($Value) {
  if ($null -eq $Value) { return $null }
  $s = [string]$Value
  if ([string]::IsNullOrWhiteSpace($s)) { return $null }
  $v = 0.0
  if ([double]::TryParse($s, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$v)) { return $v }
  if ([double]::TryParse($s, [ref]$v)) { return $v }
  return $null
}

function LatestValue($RowsByCode, [string[]]$Codes, [string]$Field) {
  foreach ($code in $Codes) {
    if (-not $RowsByCode.ContainsKey($code)) { continue }
    $rows = @($RowsByCode[$code] | Sort-Object { [int]$_.연도 } -Descending)
    foreach ($row in $rows) {
      $v = To-NullableDouble $row.$Field
      if ($null -ne $v) {
        return [pscustomobject]@{ value = $v; year = [string]$row.연도 }
      }
    }
  }
  return [pscustomobject]@{ value = $null; year = $null }
}

$base = Read-Json $InputJson
$tree = Read-Json $TreeJson
$panelRows = Import-Csv -LiteralPath $PanelCsv -Encoding UTF8
$rowsByCode = @{}
foreach ($row in $panelRows) {
  $code = [string]$row.시군구코드
  if ([string]::IsNullOrWhiteSpace($code)) { continue }
  if (-not $rowsByCode.ContainsKey($code)) { $rowsByCode[$code] = New-Object System.Collections.ArrayList }
  [void]$rowsByCode[$code].Add($row)
}

$scaleNumerator = 1770000.0
$scaleDenominator = 378079.0
$scaleFactor = [math]::Round($scaleNumerator / $scaleDenominator, 2)

$v4Rows = @()
foreach ($r in $base.sgg_data) {
  $codes = @($r.sgg_codes | ForEach-Object { [string]$_ })
  $explicit = LatestValue $rowsByCode $codes "대응자원투입예산_원_재선충명시"
  $broad = LatestValue $rowsByCode $codes "대응자원투입예산_원_산림병해충포괄"
  $survExplicit = LatestValue $rowsByCode $codes "예찰진단예산_원_재선충명시"
  $survBroad = LatestValue $rowsByCode $codes "예찰진단예산_원_산림병해충포괄"
  $moveBroad = LatestValue $rowsByCode $codes "이동통제예산_원_산림병해충포괄"

  $treeCount = To-NullableDouble $r.treeCount
  $scaledTree = $null
  if ($null -ne $treeCount) { $scaledTree = [int][math]::Round($treeCount * $scaleNumerator / $scaleDenominator, 0) }

  $pineArea = To-NullableDouble $r.area_ha
  $defaultTreatment = $null
  if ($null -ne $pineArea) { $defaultTreatment = [math]::Round([math]::Min($pineArea, 50.0), 1) }

  $budgetPrimary = $explicit.value
  $budgetMode = "explicit_primary"
  if (($null -eq $budgetPrimary) -or ($budgetPrimary -le 0)) {
    $budgetPrimary = $broad.value
    $budgetMode = "broad_reference_fallback"
  }

  $v4Rows += [pscustomobject]@{
    시도명 = $r.시도명
    시군구명 = $r.시군구명
    sgg_codes = $codes
    priority_rank = $r.priority_rank
    grade = $r.grade
    재발위험확률 = $r.재발위험확률
    dominant_domain = $r.dominant_domain
    recommended_policy = $r.recommended_policy
    pine_area_ha_reference = $pineArea
    treatment_area_ha_default = $defaultTreatment
    area_ha_deprecated = $pineArea
    treeCount_reference = $treeCount
    treeCount_scaled_current = $scaledTree
    treeCount_scale_factor = $scaleFactor
    treeCount_scale_note = "전국 피해고사목 2021.5~2022.4 378,079본 대비 2025.6~2026.5 1,770,000본 비율을 단순 적용한 참고 스케일업값"
    ch1_data_available = $r.ch1_data_available
    treeCount_source = $r.treeCount_source
    treeCount_누적_6주기_참고용 = $r.'treeCount_누적_6주기(참고용, CH4에는_미사용)'
    budget_won_primary = $budgetPrimary
    budget_primary_mode = $budgetMode
    budget_won_explicit = $explicit.value
    budget_won_explicit_year = $explicit.year
    budget_won_broad = $broad.value
    budget_won_broad_year = $broad.year
    surveillance_budget_won_explicit = $survExplicit.value
    surveillance_budget_won_explicit_year = $survExplicit.year
    surveillance_budget_won_broad = $survBroad.value
    surveillance_budget_won_broad_year = $survBroad.year
    movement_control_budget_won_broad = $moveBroad.value
    movement_control_budget_won_broad_year = $moveBroad.year
    targetDays_suggested = $r.targetDays_suggested
    targetDays_basis = "CH3 grade 기반 내부 추정"
    recurrence_probability_role = "targetDays 산정값이 아니라 urgentList 교차조건용 참고값"
    data_quality = [pscustomobject]@{
      treeCount = "B: 공식 원자료 기반 재계산, 2026년 현재 대비 시간 격차 존재"
      pine_area = "B: 소나무류 면적 참고값, 피해면적 아님"
      treatment_area = "D: 사용자 확정 또는 최신 설계자료 필요"
      budgets = "A/B: CH2 예산 패널 원화값. 재선충명시 공식 기준, 포괄 예산은 보조 참고값"
      wage = "C: 임업경영실태조사 근사 실측, 방제 전용 조사 아님"
      unitCost = "D: 내부 추정"
      dailyCapacity = "D: 내부 추정"
      targetDays = "D: grade 기반 내부 추정"
    }
  }
}

$outObj = [pscustomobject]@{
  meta = [pscustomobject]@{
    version = "CH4_v4_execution_assets"
    generated_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    source_input = "Modeling/CH4/1차/data/ch4_input_data.json"
    source_budget_panel = "Modeling/CH2/6차/CH2_전체병합패널_5도메인_2016_2023_최종보정4.csv"
    n_sgg = $v4Rows.Count
    budget_rule = "재선충명시 예산을 공식 기준으로 우선 사용하고, 0/결측이면 산림병해충 포괄 예산을 참고 fallback으로 표시"
    area_rule = "pine_area_ha_reference는 소나무류 면적 참고값이며 실제 방제면적 treatment_area_ha와 분리"
    treeCount_rule = "검증 가능한 2021.5~2022.4 원자료 기준값과 2026년 전국 총량 배율 참고 스케일업값을 병기"
    scale_factor = $scaleFactor
  }
  labor_wage = $base.labor_wage
  sgg_data = $v4Rows
}

$json = $outObj | ConvertTo-Json -Depth 20
Write-Utf8Bom (Join-Path $OutData "ch4_input_data_v4.json") $json
Copy-Item -LiteralPath $TreeJson -Destination (Join-Path $OutData "ch4_treecount_latest_cycle.json") -Force

$dataJs = @"
window.CH4_V4_INPUT = $json;

window.CH4_DATA = {
  meta: {
    is_estimate: true,
    note: 'CH4 v4는 실측 입력값과 추정 방제비를 비교하는 실행 가능성 시뮬레이터입니다. 확정 견적이 아닙니다.',
    wageKrwPerPersonDay: 200000,
    wageTrust: 'C: 임업경영실태조사 근사 실측, 방제 전용 조사는 아님'
  },
  methods: [
    { key:'aerial', name:'항공방제 (헬기 약제살포)', unit:'ha', unitCost:250000, dailyCapacityPerWorker:40, minQuantity:30, needsResidentialDistance:true, laborBased:false, trust:'D', basis:'계약형 서비스비 추정', condition:'30ha 이상 · 주거지 비인접 · 지상접근 곤란 지역 참고' },
    { key:'ground', name:'지상 약제방제', unit:'본', unitCost:45000, dailyCapacityPerWorker:20, minQuantity:0, needsResidentialDistance:false, laborBased:true, trust:'D', basis:'피해목 주변 지상작업 추정', condition:'도로 접근 가능 · 중소규모 피해목 처리 참고' },
    { key:'trunkInjection', name:'수간주사 (우량목 예방)', unit:'본', unitCost:30000, dailyCapacityPerWorker:35, minQuantity:0, needsResidentialDistance:false, laborBased:true, trust:'D', basis:'우량목 예방 목적 추정', condition:'감염목 치료가 아니라 보호대상 우량목 예방 조치' },
    { key:'fumigation', name:'훈증처리', unit:'본', unitCost:35000, dailyCapacityPerWorker:15, minQuantity:0, needsResidentialDistance:false, laborBased:true, trust:'D', basis:'개별 감염목 처리 추정', condition:'소규모·확산 초기 단계의 개별 감염목 처리 참고' },
    { key:'felling', name:'벌채 후 파쇄·소각', unit:'본', unitCost:60000, dailyCapacityPerWorker:10, minQuantity:0, needsResidentialDistance:false, laborBased:true, trust:'D', basis:'벌채+파쇄+운반 추정', condition:'피해가 심각해 완전 제거가 필요한 경우 참고' },
    { key:'drone', name:'드론방제 (정밀 살포)', unit:'ha', unitCost:180000, dailyCapacityPerWorker:25, minQuantity:5, needsResidentialDistance:true, laborBased:true, trust:'D', basis:'소면적 정밀 살포 추정', condition:'헬기 진입 곤란 · 소규모 정밀 살포 참고' }
  ],
  distanceSurcharge: { freeKm: 10, pctPerKm: 0.5 },
  defaults: { treatment_area_ha: 50, treeCount: 800, budget_won: 30000000, workers: 10, distance_km: 5, nearResidential: false, targetDays: 7 }
};
"@
Write-Utf8Bom (Join-Path $OutRoot "data.js") $dataJs

$html = @'
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I'mPine - CH4 v4 맞춤형 방제 설계</title>
<script src="data.js"></script>
<style>
:root{--gd:#0b3300;--gm:#1a5a0a;--gl:#2d7016;--risk:#c0392b;--wa:#e67e22;--b:#2a78d6;--t:#1baf7a;--bg:#f6f8f3;--sf:#fff;--bd:#dde8d0;--tx:#1a1a18;--mu:#6b7560;--mu2:#8a9482}
*{box-sizing:border-box}body{margin:0;font-family:"Noto Sans KR","Malgun Gothic",system-ui,sans-serif;background:var(--bg);color:var(--tx);font-size:14px;line-height:1.55}.mono{font-family:Consolas,"JetBrains Mono",monospace}
.hdr{background:linear-gradient(135deg,var(--gd),var(--gm));padding:12px 24px;color:#fff;display:flex;align-items:center;gap:14px;position:sticky;top:0;z-index:5}.hdr h1{font-size:20px;margin:0}.hdr .sub{font-size:12px;color:#cde9b7}.hdr a{margin-left:auto;color:#fff;text-decoration:none;border:1px solid rgba(255,255,255,.45);border-radius:18px;padding:5px 12px;font-size:12px}
.basis{padding:8px 24px;background:#eef4e6;border-bottom:1px solid var(--bd);font-size:12px;color:var(--gd)}.tag{display:inline-block;border-radius:10px;padding:2px 8px;font-size:10px;font-weight:700}.tag.d{background:#fdebd2;color:#9a4a0a}.tag.c{background:#dcecff;color:#1d4ed8}.tag.b{background:#eaf3e0;color:#1a5a0a}.tag.a{background:#dcf4ea;color:#0f7a52}
.pg{max-width:1420px;margin:0 auto;padding:16px 24px 28px}.grid{display:grid;grid-template-columns:360px 1fr;gap:14px;align-items:start}@media(max-width:900px){.grid{grid-template-columns:1fr}}
.card{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:15px 17px;margin-bottom:14px}.ct{font-weight:700;color:var(--gd);margin-bottom:9px;display:flex;gap:8px;align-items:center}.field{margin-bottom:13px}.field label{display:flex;justify-content:space-between;color:var(--mu);font-size:12px;margin-bottom:5px}.field input,.field select{width:100%;padding:7px 9px;border:1px solid var(--bd);border-radius:7px;background:#fff}.field input[type=range]{padding:0;accent-color:var(--gl)}.val{font-family:Consolas,monospace;color:var(--gd);font-weight:700}
.notice{font-size:11.5px;background:#fff8ee;border-left:4px solid var(--wa);border-radius:8px;padding:9px 11px;color:#7a4a0a;margin-top:8px}.info{font-size:11.5px;background:#eef6ff;border-left:4px solid var(--b);border-radius:8px;padding:9px 11px;color:#1d4ed8;margin-top:8px}
.recobox{background:linear-gradient(135deg,var(--gd),var(--gm));color:#fff;border-radius:12px;padding:18px 20px;margin-bottom:14px}.recobox .l{font-size:11px;color:#cde9b7}.recobox .v{font-size:23px;font-weight:800}.recobox .why{font-size:12px;margin-top:6px;color:#eaf7de}.recobox.warn{background:linear-gradient(135deg,#7a2b0f,#a3401a)}
.krow{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:14px}.kpi{background:#fff;border:1px solid var(--bd);border-radius:10px;padding:12px 14px;border-left:4px solid var(--gl)}.kl{font-size:11px;color:var(--mu)}.kv{font-size:20px;font-weight:800;font-family:Consolas,monospace}.ks{font-size:10.5px;color:var(--mu2);margin-top:3px}
table{width:100%;border-collapse:collapse;font-size:12px}th{background:#f0f5ea;text-align:left;padding:7px 9px;border-bottom:2px solid var(--bd);color:var(--mu)}td{padding:7px 9px;border-bottom:1px solid #eee;vertical-align:top}td.num{text-align:right;font-family:Consolas,monospace}tr.best td{background:#eaf6f0}.pill{border-radius:9px;padding:2px 8px;font-size:10px;font-weight:700}.ok{background:#dcf4ea;color:#0f7a52}.no{background:#fde2e1;color:#a33}
</style>
</head>
<body>
<div class="hdr"><h1>I'mPine</h1><div class="sub">CH4 v4 맞춤형 방제 설계</div><a href="../../../../ch3/ImPine_ver4/ImPine/ch3/ch3.html">CH3로 돌아가기</a></div>
<div class="basis"><span class="tag d">추정 포함</span> 재선충명시 예산을 공식 기준으로 우선 사용하고, 산림병해충 포괄 예산은 보조 참고값으로 표시합니다. 본 화면은 확정 견적이 아닙니다.</div>
<section class="pg">
  <div class="grid">
    <div>
      <div class="card">
        <div class="ct">지역 선택</div>
        <div class="field"><label>CH3 우선지원 지역 <span class="val" id="v-region">-</span></label><select id="region-select"></select></div>
        <div class="info" id="region-note"></div>
      </div>
      <div class="card">
        <div class="ct">현장 조건 입력</div>
        <div class="field"><label>실제 방제면적 treatment_area_ha <span class="val" id="v-area">-</span></label><input type="range" id="in-area" min="1" max="300" step="1"></div>
        <div class="field"><label>피해목 기준 treeCount <span class="val" id="v-tree">-</span></label><input type="range" id="in-tree" min="0" max="20000" step="10"></div>
        <div class="field"><label>예산 기준 <span class="val" id="v-budget-mode">-</span></label><select id="budget-mode"><option value="primary">재선충명시 우선 기준</option><option value="explicit">재선충명시만</option><option value="broad">산림병해충 포괄 참고</option><option value="manual">수동 입력</option></select></div>
        <div class="field"><label>비교 예산 <span class="val" id="v-budget">-</span></label><input type="range" id="in-budget" min="0" max="300000" step="100"></div>
        <div class="field"><label>보유 인력 <span class="val" id="v-workers">-</span></label><input type="range" id="in-workers" min="1" max="100" step="1"></div>
        <div class="field"><label>현장까지 거리 <span class="val" id="v-distance">-</span></label><input type="range" id="in-distance" min="0" max="150" step="1"></div>
        <div class="field"><label>목표 작업일수 <span class="val" id="v-days">-</span></label><input type="range" id="in-days" min="1" max="30" step="1"></div>
        <label style="font-size:12px"><input type="checkbox" id="in-residential"> 주거지 인접 또는 비산 민원 우려</label>
        <div class="notice">면적은 소나무류 면적 참고값이 아니라 실제 방제면적을 사용해야 합니다. 기본값은 임시값이며 현장 설계자료로 확정하세요.</div>
      </div>
    </div>
    <div>
      <div class="recobox" id="recobox"><div class="l">추천 방제방법</div><div class="v" id="reco-name">-</div><div class="why" id="reco-why"></div></div>
      <div class="krow" id="kpi-row"></div>
      <div class="card"><div class="ct">예산·데이터 신뢰도</div><table id="budget-table"></table></div>
      <div class="card"><div class="ct">방제방법 비교</div><table id="compare-table"></table><div class="notice">단가·작업량은 D등급 추정치입니다. 인건비 20만원/인/일은 C등급 근사 실측 참고치로만 병기합니다.</div></div>
    </div>
  </div>
</section>
<script>
const INPUT = window.CH4_V4_INPUT;
const DATA = window.CH4_DATA;
const rows = (INPUT.sgg_data || []).slice().sort((a,b)=>a.priority_rank-b.priority_rank);
const fmt = n => n==null || isNaN(n) ? '-' : Math.round(Number(n)).toLocaleString('ko-KR');
const moneyMan = n => n==null || isNaN(n) ? '-' : fmt(Number(n)/10000)+'만원';
const qs = new URLSearchParams(location.search);
const els = {
  select: document.getElementById('region-select'), area: document.getElementById('in-area'), tree: document.getElementById('in-tree'),
  budgetMode: document.getElementById('budget-mode'), budget: document.getElementById('in-budget'), workers: document.getElementById('in-workers'),
  distance: document.getElementById('in-distance'), days: document.getElementById('in-days'), residential: document.getElementById('in-residential')
};
function rowCode(r){ return (r.sgg_codes||[])[0] || ''; }
function labelRow(r){ return `${r.priority_rank}. ${r.시도명} ${r.시군구명} (${r.grade})`; }
function findInitial(){
  const code = qs.get('sgg') || qs.get('code');
  const name = qs.get('name');
  return rows.find(r => code && (r.sgg_codes||[]).includes(code)) || rows.find(r => name && r.시군구명 === name) || rows[0];
}
rows.forEach(r => {
  const opt = document.createElement('option');
  opt.value = rowCode(r);
  opt.textContent = labelRow(r);
  els.select.appendChild(opt);
});
function selectedRow(){ return rows.find(r => (r.sgg_codes||[]).includes(els.select.value)) || rows[0]; }
function budgetFor(r, mode){
  if(mode === 'explicit') return Number(r.budget_won_explicit || 0);
  if(mode === 'broad') return Number(r.budget_won_broad || 0);
  if(mode === 'manual') return Number(els.budget.value || 0) * 10000;
  return Number(r.budget_won_primary || 0);
}
function setBudgetSlider(won){
  const man = Math.max(0, Math.round((Number(won||0))/10000));
  els.budget.max = Math.max(300000, Math.ceil((man || 3000) * 1.3 / 100) * 100);
  els.budget.value = man || 3000;
}
function applyRow(r){
  els.select.value = rowCode(r);
  const area = Number(qs.get('area') || r.treatment_area_ha_default || DATA.defaults.treatment_area_ha);
  const tree = Number(qs.get('tree') || r.treeCount_reference || DATA.defaults.treeCount);
  els.area.max = Math.max(300, Math.ceil((Number(r.pine_area_ha_reference || area || 300))/100)*100);
  els.area.value = Math.max(1, Math.round(area));
  els.tree.max = Math.max(20000, Math.ceil((Number(r.treeCount_scaled_current || tree || 20000))/1000)*1000);
  els.tree.value = Math.max(0, Math.round(tree));
  els.days.value = Number(qs.get('days') || r.targetDays_suggested || DATA.defaults.targetDays);
  els.workers.value = Number(qs.get('workers') || DATA.defaults.workers);
  els.distance.value = Number(qs.get('distance') || DATA.defaults.distance_km);
  els.residential.checked = qs.get('residential') === '1';
  setBudgetSlider(budgetFor(r, els.budgetMode.value));
  render();
}
function methodQty(method, ctx){ return method.unit === 'ha' ? ctx.area : ctx.tree; }
function calc(method, ctx){
  const qty = methodQty(method, ctx);
  const baseCost = qty * method.unitCost;
  const overKm = Math.max(0, ctx.distance - DATA.distanceSurcharge.freeKm);
  const totalCost = baseCost + baseCost * (overKm * DATA.distanceSurcharge.pctPerKm / 100);
  const neededWorkers = method.dailyCapacityPerWorker > 0 ? Math.ceil(qty / (method.dailyCapacityPerWorker * Math.max(1, ctx.days))) : null;
  const daysWithCurrentWorkers = method.dailyCapacityPerWorker > 0 ? Math.ceil(qty / (method.dailyCapacityPerWorker * Math.max(1, ctx.workers))) : null;
  const meetsMinQty = qty >= (method.minQuantity || 0);
  const meetsResidential = !(method.needsResidentialDistance && ctx.residential);
  const meetsBudget = totalCost <= ctx.budget;
  const feasible = meetsMinQty && meetsResidential && meetsBudget;
  return {...method, qty, totalCost, neededWorkers, daysWithCurrentWorkers, feasible, meetsMinQty, meetsResidential, meetsBudget};
}
function render(){
  const r = selectedRow();
  if(els.budgetMode.value !== 'manual') setBudgetSlider(budgetFor(r, els.budgetMode.value));
  const ctx = { area:Number(els.area.value), tree:Number(els.tree.value), budget:Number(els.budget.value)*10000, workers:Number(els.workers.value), distance:Number(els.distance.value), days:Number(els.days.value), residential:els.residential.checked };
  document.getElementById('v-region').textContent = `${r.시군구명} ${r.grade}`;
  document.getElementById('v-area').textContent = `${fmt(ctx.area)} ha`;
  document.getElementById('v-tree').textContent = `${fmt(ctx.tree)} 본`;
  document.getElementById('v-budget').textContent = moneyMan(ctx.budget);
  document.getElementById('v-workers').textContent = `${fmt(ctx.workers)}명`;
  document.getElementById('v-distance').textContent = `${fmt(ctx.distance)} km`;
  document.getElementById('v-days').textContent = `${fmt(ctx.days)}일`;
  document.getElementById('v-budget-mode').textContent = els.budgetMode.options[els.budgetMode.selectedIndex].textContent;
  document.getElementById('region-note').innerHTML = `<b>${r.시도명} ${r.시군구명}</b> · CH3 우선순위 ${r.priority_rank}위(${r.grade}) · 정책 ${r.recommended_policy}<br>treeCount 원자료 기준 ${fmt(r.treeCount_reference)}본, 2026 전국배율 참고 ${fmt(r.treeCount_scaled_current)}본 · 소나무류 면적 참고 ${fmt(r.pine_area_ha_reference)}ha`;
  const results = DATA.methods.map(m => calc(m, ctx));
  const feasible = results.filter(x=>x.feasible).sort((a,b)=>a.totalCost-b.totalCost);
  const best = feasible[0];
  const reco = document.getElementById('recobox');
  if(best){
    reco.classList.remove('warn');
    document.getElementById('reco-name').textContent = best.name;
    document.getElementById('reco-why').innerHTML = `${best.condition}<br>예상비용 <b>${moneyMan(best.totalCost)}</b> · 보유인력 기준 ${fmt(best.daysWithCurrentWorkers)}일`;
  }else{
    reco.classList.add('warn');
    document.getElementById('reco-name').textContent = '조건 내 적용 가능 방식 없음';
    document.getElementById('reco-why').textContent = '예산, 주거지 인접, 최소 물량 조건을 조정해 확인하세요.';
  }
  const kpis = best ? [
    ['예상 최소비용', moneyMan(best.totalCost), best.name],
    ['필요인력', fmt(best.neededWorkers)+'명', `목표 ${ctx.days}일 기준`],
    ['예산 대비', ctx.budget ? (best.totalCost/ctx.budget*100).toFixed(0)+'%' : '-', els.budgetMode.options[els.budgetMode.selectedIndex].textContent],
    ['기준 treeCount', fmt(ctx.tree)+'본', r.treeCount_scale_note]
  ] : [['적용 가능','없음','조건 조정 필요']];
  document.getElementById('kpi-row').innerHTML = kpis.map(k=>`<div class="kpi"><div class="kl">${k[0]}</div><div class="kv">${k[1]}</div><div class="ks">${k[2]}</div></div>`).join('');
  document.getElementById('budget-table').innerHTML =
    '<tr><th>항목</th><th class="num">금액</th><th>해석</th></tr>' +
    `<tr><td>재선충명시 대응예산 <span class="tag a">공식</span></td><td class="num">${moneyMan(r.budget_won_explicit)}</td><td>CH2 공식 분석축. 0이면 전용 편성 확인 필요</td></tr>`+
    `<tr><td>산림병해충 포괄 대응예산 <span class="tag b">보조</span></td><td class="num">${moneyMan(r.budget_won_broad)}</td><td>재선충 전용 재원으로 해석 금지, 참고 상한</td></tr>`+
    `<tr><td>예찰진단 예산</td><td class="num">${moneyMan(r.surveillance_budget_won_broad)}</td><td>직접 방제비가 아니라 탐지·진단 역량</td></tr>`+
    `<tr><td>이동통제 예산</td><td class="num">${moneyMan(r.movement_control_budget_won_broad)}</td><td>인위적 확산 차단 보조지표</td></tr>`;
  document.getElementById('compare-table').innerHTML =
    '<tr><th>방법</th><th>신뢰</th><th class="num">물량</th><th class="num">단가</th><th class="num">예상비용</th><th class="num">필요인력</th><th>판정</th></tr>' +
    results.map(x=>`<tr class="${best&&x.key===best.key?'best':''}"><td><b>${x.name}</b><br><span style="color:var(--mu2);font-size:10.5px">${x.basis} · ${x.condition}</span></td><td><span class="tag d">${x.trust}</span></td><td class="num">${fmt(x.qty)}${x.unit}</td><td class="num">${fmt(x.unitCost)}원/${x.unit}</td><td class="num">${moneyMan(x.totalCost)}</td><td class="num">${fmt(x.neededWorkers)}명</td><td>${x.feasible?'<span class="pill ok">가능</span>':'<span class="pill no">불가</span>'}</td></tr>`).join('');
}
els.select.addEventListener('change', ()=>applyRow(selectedRow()));
els.budgetMode.addEventListener('change', ()=>render());
[els.area,els.tree,els.budget,els.workers,els.distance,els.days,els.residential].forEach(el=>el.addEventListener('input', ()=>{ if(el===els.budget) els.budgetMode.value='manual'; render(); }));
applyRow(findInitial());
</script>
</body>
</html>
'@
Write-Utf8Bom (Join-Path $OutRoot "ch4.html") $html

# Patch the requested CH3 v4 dashboard only.
$ch3 = Get-Content -LiteralPath $Ch3Html -Encoding UTF8 -Raw
if ($ch3 -notmatch "function ch4Url") {
  $helper = @'
function ch4Url(r){
  const code = encodeURIComponent((r.sgg_codes||[])[0] || '');
  const name = encodeURIComponent(r.시군구명 || '');
  const days = encodeURIComponent(r.grade==='S'?4:r.grade==='A'?6:r.grade==='B'?8:r.grade==='C'?12:18);
  return `../../../../Modeling/CH4/2차/ch4.html?sgg=${code}&name=${name}&days=${days}`;
}
'@
  $ch3 = $ch3.Replace("const fmt = n => n==null||isNaN(n) ? '–' : Number(n).toLocaleString('ko-KR');", "const fmt = n => n==null||isNaN(n) ? '–' : Number(n).toLocaleString('ko-KR');`r`n$helper")
}
if ($ch3 -notmatch "CH4 설계") {
  $ch3 = $ch3.Replace("'<tr><th>순위</th><th>등급</th><th>시군구</th><th class=`"num`">점수</th><th>추천정책</th></tr>' +", "'<tr><th>순위</th><th>등급</th><th>시군구</th><th class=`"num`">점수</th><th>추천정책</th><th>CH4 설계</th></tr>' +")
  $ch3 = $ch3.Replace("'<tr><th>시군구</th><th>우세 도메인</th><th>추천 정책</th></tr>' +", "'<tr><th>시군구</th><th>우세 도메인</th><th>추천 정책</th><th>CH4 설계</th></tr>' +")
}
if ($ch3 -notmatch "CH4로 보내기") {
  $ch3 = $ch3.Replace('<td class="num">${(r.priority_score*100).toFixed(1)}%</td><td>${r.recommended_policy}</td></tr>`).join('');', '<td class="num">${(r.priority_score*100).toFixed(1)}%</td><td>${r.recommended_policy}</td><td><a class="tag real" href="${ch4Url(r)}">CH4로 보내기</a></td></tr>`).join('');')
  $ch3 = $ch3.Replace('<td>${r.recommended_policy}</td></tr>`).join('');', '<td>${r.recommended_policy}</td><td><a class="tag real" href="${ch4Url(r)}">CH4로 보내기</a></td></tr>`).join('');')
  $ch3 = $ch3.Replace('<td class="num">${(r.priority_score*100).toFixed(1)}%</td><td>${r.recommended_policy}</td></tr>`).join('''');', '<td class="num">${(r.priority_score*100).toFixed(1)}%</td><td>${r.recommended_policy}</td><td><a class="tag real" href="${ch4Url(r)}">CH4로 보내기</a></td></tr>`).join('''');')
  $ch3 = $ch3.Replace('<td>${r.recommended_policy}</td></tr>`).join('''');', '<td>${r.recommended_policy}</td><td><a class="tag real" href="${ch4Url(r)}">CH4로 보내기</a></td></tr>`).join('''');')
  $ch3 = $ch3.Replace('<td class="num">${(r.priority_score*100).toFixed(1)}%</td><td>${r.recommended_policy}</td></tr>`).join('''');', '<td class="num">${(r.priority_score*100).toFixed(1)}%</td><td>${r.recommended_policy}</td><td><a class="tag real" href="${ch4Url(r)}">CH4로 보내기</a></td></tr>`).join('''');')
}
Write-Utf8Bom $Ch3Html $ch3

Write-Host "Generated:"
Write-Host " - $OutData\ch4_input_data_v4.json"
Write-Host " - $OutRoot\data.js"
Write-Host " - $OutRoot\ch4.html"
Write-Host "Patched:"
Write-Host " - $Ch3Html"
