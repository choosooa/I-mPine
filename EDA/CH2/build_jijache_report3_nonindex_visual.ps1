$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$PanelPath = Join-Path $Root "data\CH2\3. 지자체\중간과정\CH2_local_capacity_final_panel.csv"
$OutPath = Join-Path $PSScriptRoot "지자체_report_3차_전체EDA_외적타당성.html"
$ModelOut = Join-Path $Root "CH2 data\CH2 전체변수\CH2_지자체대응역량_모델링용_비지수_최종후보.csv"
$DictOut = Join-Path $Root "CH2 data\CH2 전체변수\CH2_지자체대응역량_비지수_변수설명.csv"

function ToNum($v) {
    if ($null -eq $v) { return [double]::NaN }
    $s = [string]$v
    if ([string]::IsNullOrWhiteSpace($s)) { return [double]::NaN }
    $d = 0.0
    if ([double]::TryParse($s, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$d)) { return $d }
    if ([double]::TryParse($s, [ref]$d)) { return $d }
    return [double]::NaN
}
function Valid($x) { return -not ([double]::IsNaN($x) -or [double]::IsInfinity($x)) }
function Mean($xs) {
    $sum = 0.0; $n = 0
    foreach ($x in $xs) { if (Valid $x) { $sum += $x; $n++ } }
    if ($n -eq 0) { return $null }
    return $sum / $n
}
function Quantile($xs, [double]$p) {
    $v = @($xs | Where-Object { Valid $_ } | Sort-Object)
    if ($v.Count -eq 0) { return $null }
    if ($v.Count -eq 1) { return $v[0] }
    $pos = ($v.Count - 1) * $p
    $lo = [math]::Floor($pos); $hi = [math]::Ceiling($pos)
    if ($lo -eq $hi) { return $v[$lo] }
    return $v[$lo] + (($v[$hi] - $v[$lo]) * ($pos - $lo))
}
function Fmt($x, [int]$digits = 3) {
    if ($null -eq $x) { return "" }
    if (-not (Valid ([double]$x))) { return "" }
    return ([math]::Round([double]$x, $digits)).ToString("N$digits")
}
function Corr($rows, $a, $b) {
    $pairs = @()
    foreach ($r in $rows) {
        $x = ToNum $r.$a; $y = ToNum $r.$b
        if ((Valid $x) -and (Valid $y)) { $pairs += ,@($x, $y) }
    }
    if ($pairs.Count -le 2) { return $null }
    $sx = 0.0; $sy = 0.0
    foreach ($p in $pairs) { $sx += $p[0]; $sy += $p[1] }
    $mx = $sx / $pairs.Count; $my = $sy / $pairs.Count
    $num = 0.0; $dx = 0.0; $dy = 0.0
    foreach ($p in $pairs) {
        $vx = $p[0] - $mx; $vy = $p[1] - $my
        $num += $vx * $vy; $dx += $vx * $vx; $dy += $vy * $vy
    }
    if ($dx -eq 0 -or $dy -eq 0) { return $null }
    return $num / [math]::Sqrt($dx * $dy)
}
function Safe($s) {
    return [System.Net.WebUtility]::HtmlEncode([string]$s)
}
function Bar($pct) {
    $w = [math]::Max(0, [math]::Min(100, [double]$pct))
    return "<div class='bar'><span style='width:$w%'></span></div>"
}
function LineSvg($series, $labels, $title) {
    $width = 860; $height = 280; $left = 58; $right = 20; $top = 28; $bottom = 42
    $vals = @()
    foreach ($s in $series) { foreach ($v in $s.values) { if ($null -ne $v) { $vals += [double]$v } } }
    $min = [double]($vals | Measure-Object -Minimum).Minimum
    $max = [double]($vals | Measure-Object -Maximum).Maximum
    if ($min -eq $max) { $min -= 1; $max += 1 }
    $plotW = $width - $left - $right; $plotH = $height - $top - $bottom
    $colors = @("#2f6f9f", "#d48331", "#4e8b5b", "#8a5a9e", "#b04f5f")
    $svg = "<svg viewBox='0 0 $width $height' class='chart' role='img' aria-label='$(Safe $title)'>"
    $svg += "<rect x='0' y='0' width='$width' height='$height' fill='#ffffff'/>"
    $svg += "<text x='$left' y='18' class='svg-title'>$(Safe $title)</text>"
    for ($i = 0; $i -lt 5; $i++) {
        $y = $top + ($plotH * $i / 4)
        $val = $max - (($max - $min) * $i / 4)
        $svg += "<line x1='$left' y1='$y' x2='$($width-$right)' y2='$y' stroke='#e7e2d9'/>"
        $svg += "<text x='8' y='$($y+4)' class='tick'>$(Fmt $val 1)</text>"
    }
    for ($i = 0; $i -lt $labels.Count; $i++) {
        $x = $left + ($plotW * $i / [math]::Max(1, $labels.Count - 1))
        $svg += "<text x='$($x-14)' y='$($height-14)' class='tick'>$($labels[$i])</text>"
    }
    for ($si = 0; $si -lt $series.Count; $si++) {
        $pts = @()
        for ($i = 0; $i -lt $series[$si].values.Count; $i++) {
            $v = $series[$si].values[$i]
            if ($null -eq $v) { continue }
            $x = $left + ($plotW * $i / [math]::Max(1, $labels.Count - 1))
            $y = $top + ($plotH * ($max - [double]$v) / ($max - $min))
            $pts += "$x,$y"
            $svg += "<circle cx='$x' cy='$y' r='3.5' fill='$($colors[$si % $colors.Count])'/>"
        }
        if ($pts.Count -gt 1) {
            $svg += "<polyline points='$($pts -join " ")' fill='none' stroke='$($colors[$si % $colors.Count])' stroke-width='2.4'/>"
        }
        $lx = $left + 12 + (($si % 2) * 360); $ly = 42 + ([math]::Floor($si / 2) * 18)
        $svg += "<rect x='$lx' y='$($ly-9)' width='10' height='10' fill='$($colors[$si % $colors.Count])'/>"
        $svg += "<text x='$($lx+16)' y='$ly' class='legend'>$(Safe $series[$si].label)</text>"
    }
    $svg += "</svg>"
    return $svg
}

$rows = @(Import-Csv -LiteralPath $PanelPath)
$years = @(2016..2023)
$vars = @(
    [pscustomobject]@{ col="log_resource_budget_per_pine_ha"; kr="대응자원투입예산_소나무림ha당_log"; role="메인 후보"; note="소나무림 면적 대비 예산 투입 강도. 규모효과와 편포를 완화하기 위해 log1p 사용" },
    [pscustomobject]@{ col="log_surveillance_budget_per_pine_ha"; kr="예찰진단예산_소나무림ha당_log"; role="메인 후보"; note="조기 발견·진단 역량을 나타내는 예산 강도. 0 값이 많아 분포 확인 필요" },
    [pscustomobject]@{ col="log_active_pest_firm_per_10000_pine_ha"; kr="방제법인수_소나무림1만ha당_log"; role="확장 후보"; note="민간 방제 인프라의 상대적 밀도. 2022년 이후 자료 최신성 주의" },
    [pscustomobject]@{ col="log_movement_budget_per_pine_ha"; kr="이동통제예산_소나무림ha당_log"; role="보조/민감도"; note="감염목 이동·확산 차단과 관련된 예산 강도. 메인보다 보조 분석 권장" },
    [pscustomobject]@{ col="surveillance_share"; kr="예찰진단예산비중"; role="보조/민감도"; note="전체 포함예산 중 예찰·진단의 배분 비중. 총량이 아니라 배분구조 변수" },
    [pscustomobject]@{ col="movement_share_included_budget"; kr="이동통제예산비중"; role="보조/민감도"; note="전체 포함예산 중 이동통제 예산 비중. 총량 변수와 동시에 해석 시 중복 주의" },
    [pscustomobject]@{ col="restriction_designated"; kr="반출금지구역_지정여부"; role="보조/민감도"; note="반출금지구역 지정 여부. 정책 대응이면서 발생 이후 조치 성격도 있어 내생성 주의" },
    [pscustomobject]@{ col="active_restriction_area_ratio"; kr="반출금지구역면적비율"; role="보조/민감도"; note="시군구 내 반출금지구역 면적 비율. 발생 규모와 함께 움직일 수 있음" }
)
$outcomes = @(
    [pscustomobject]@{ col="current_infected_sites"; kr="당해_감염지점수" },
    [pscustomobject]@{ col="recurrent_sites_300m"; kr="재발생지점수_300m" },
    [pscustomobject]@{ col="recurrence_rate_300m"; kr="재발생률_300m" },
    [pscustomobject]@{ col="new_site_share_300m"; kr="신규발생지비율_300m" }
)

$modelRows = foreach ($r in $rows) {
    [pscustomobject]@{
        연도 = $r.year
        시도 = $r.sido
        시군구 = $r.sigungu_nm
        대응자원투입예산_소나무림ha당_log = $r.log_resource_budget_per_pine_ha
        예찰진단예산_소나무림ha당_log = $r.log_surveillance_budget_per_pine_ha
        방제법인수_소나무림1만ha당_log = $r.log_active_pest_firm_per_10000_pine_ha
        이동통제예산_소나무림ha당_log = $r.log_movement_budget_per_pine_ha
        예찰진단예산비중 = $r.surveillance_share
        이동통제예산비중 = $r.movement_share_included_budget
        반출금지구역_지정여부 = $r.restriction_designated
        반출금지구역면적비율 = $r.active_restriction_area_ratio
        예산자료_사용가능여부 = $r.budget_index_eligible
        법인자료_연도완전여부 = $r.forest_firm_data_complete_for_year
        법인자료_최신성주의플래그 = $r.forest_firm_data_stale_flag
    }
}
$modelRows | Export-Csv -LiteralPath $ModelOut -NoTypeInformation -Encoding UTF8
$vars | Select-Object @{n="영문원변수";e={$_.col}}, @{n="한글변수명";e={$_.kr}}, role, note |
    Export-Csv -LiteralPath $DictOut -NoTypeInformation -Encoding UTF8

$nRows = $rows.Count
$nSgg = @($rows | Group-Object sigungu_cd).Count
$yearRange = "$(($rows | ForEach-Object {[int]$_.year} | Measure-Object -Minimum).Minimum)-$(($rows | ForEach-Object {[int]$_.year} | Measure-Object -Maximum).Maximum)"
$dup = @($rows | Group-Object year, sigungu_cd | Where-Object { $_.Count -gt 1 }).Count
$yearCounts = @($rows | Group-Object year | Sort-Object Name | ForEach-Object { "$($_.Name): $($_.Count)" }) -join ", "

$statRows = @()
foreach ($v in $vars) {
    $xs = @($rows | ForEach-Object { ToNum $_.($v.col) })
    $valid = @($xs | Where-Object { Valid $_ })
    $missing = $nRows - $valid.Count
    $zero = @($valid | Where-Object { [math]::Abs($_) -lt 0.000000001 }).Count
    $statRows += [pscustomobject]@{
        변수=$v.kr; 역할=$v.role; 관측=$valid.Count; 결측률=($missing / [double]$nRows * 100);
        평균=(Mean $valid); 중앙값=(Quantile $valid 0.5); 최소=(Quantile $valid 0); 최대=(Quantile $valid 1);
        영비율=($(if ($valid.Count -eq 0) { 0 } else { $zero / [double]$valid.Count * 100 }))
    }
}

$trendSeries = @()
foreach ($v in $vars | Select-Object -First 4) {
    $vals = @()
    foreach ($y in $years) {
        $vals += Mean (@($rows | Where-Object { [int]$_.year -eq $y } | ForEach-Object { ToNum $_.($v.col) }))
    }
    $trendSeries += [pscustomobject]@{ label=$v.kr; values=$vals }
}

$missingBars = @()
foreach ($v in $vars) {
    $valid = @($rows | ForEach-Object { ToNum $_.($v.col) } | Where-Object { Valid $_ }).Count
    $missingBars += [pscustomobject]@{ 변수=$v.kr; 결측률=(($nRows - $valid) / [double]$nRows * 100) }
}
$corrRows = @()
foreach ($v in $vars) {
    foreach ($o in $outcomes) {
        $c = Corr $rows $v.col $o.col
        $corrRows += [pscustomobject]@{ 설명변수=$v.kr; 성과변수=$o.kr; 상관=$c }
    }
}

$varTable = ($vars | ForEach-Object {
    "<tr><td>$(Safe $_.kr)</td><td>$(Safe $_.role)</td><td>$(Safe $_.note)</td></tr>"
}) -join "`n"
$statTable = ($statRows | ForEach-Object {
    "<tr><td>$(Safe $_.변수)</td><td>$(Safe $_.역할)</td><td>$($_.관측)</td><td>$(Fmt $_.결측률 1)%</td><td>$(Fmt $_.평균 3)</td><td>$(Fmt $_.중앙값 3)</td><td>$(Fmt $_.최소 3)</td><td>$(Fmt $_.최대 3)</td><td>$(Fmt $_.영비율 1)%</td></tr>"
}) -join "`n"
$missHtml = ($missingBars | Sort-Object 결측률 -Descending | ForEach-Object {
    "<tr><td>$(Safe $_.변수)</td><td>$(Bar $_.결측률)</td><td>$(Fmt $_.결측률 1)%</td></tr>"
}) -join "`n"
$corrHtml = ($corrRows | ForEach-Object {
    $c = $_.상관
    $light = if ($null -eq $c) { 96 } else { 92 - [math]::Min(32, [math]::Abs($c) * 90) }
    $hue = if ($null -eq $c) { 0 } elseif ($c -ge 0) { 205 } else { 18 }
    "<tr><td>$(Safe $_.설명변수)</td><td>$(Safe $_.성과변수)</td><td style='background:hsl($hue,55%,$light%)'>$(Fmt $c 3)</td></tr>"
}) -join "`n"
$line = LineSvg $trendSeries $years "개별 후보변수의 연도별 평균 추세"

$html = @"
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>CH2 지자체 대응역량 전체 EDA 및 외적타당성 검토</title>
<style>
body{font-family:"Malgun Gothic",Arial,sans-serif;margin:0;background:#fbfaf7;color:#252525;line-height:1.55}
main{max-width:1180px;margin:0 auto;padding:34px 28px 70px}
h1{font-size:30px;margin:0 0 8px}
h2{font-size:21px;margin:34px 0 12px;border-top:1px solid #ded8ce;padding-top:22px}
h3{font-size:17px;margin:22px 0 10px}
.meta{color:#666;margin-bottom:22px}
.notice{background:#fff3cd;border:1px solid #ecd78b;padding:14px 16px;border-radius:8px;margin:18px 0}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}
.card{background:#fff;border:1px solid #e1ddd4;border-radius:8px;padding:14px}
.num{font-size:24px;font-weight:700;color:#255f85}
table{border-collapse:collapse;width:100%;background:#fff;margin:12px 0 20px}
th,td{border:1px solid #e1ddd4;padding:8px 10px;text-align:left;font-size:14px;vertical-align:top}
th{background:#f0eee8}
.bar{height:14px;background:#eee8dc;border-radius:3px;overflow:hidden}
.bar span{display:block;height:100%;background:#547c8c}
.chart{width:100%;height:auto;border:1px solid #e1ddd4;background:#fff;border-radius:8px;margin:10px 0 18px}
.svg-title{font-size:15px;font-weight:700;fill:#222}
.tick{font-size:11px;fill:#666}
.legend{font-size:12px;fill:#333}
.small{font-size:13px;color:#666}
code{background:#eee8dc;padding:1px 4px;border-radius:4px}
</style>
</head>
<body>
<main>
<h1>CH2 지자체 대응역량 전체 EDA 및 외적타당성 검토</h1>
<div class="meta">생성일: $(Get-Date -Format "yyyy-MM-dd HH:mm") · 기준 파일: CH2_local_capacity_final_panel.csv</div>

<div class="notice">
이 보고서는 <b>지수화하지 않는 분석</b>을 전제로 다시 작성했다. 따라서 A/B 통합지수는 최종 후보에서 제외하고,
개별 변수의 분포·결측·중복성·성과변수와의 탐색적 관계를 기준으로 모델 투입 후보를 검토한다.
</div>

<h2>1. 패널 구조 확인</h2>
<div class="grid">
<div class="card"><div class="small">행 수</div><div class="num">$nRows</div></div>
<div class="card"><div class="small">시군구 수</div><div class="num">$nSgg</div></div>
<div class="card"><div class="small">연도 범위</div><div class="num">$yearRange</div></div>
<div class="card"><div class="small">연도×시군구 중복</div><div class="num">$dup</div></div>
</div>
<p>연도별 행 수는 $yearCounts 이다. 한 행은 시군구-연도 관측치로 해석할 수 있다.</p>

<h2>2. 비지수화 기준 최종 변수 후보</h2>
<table>
<thead><tr><th>한글 변수명</th><th>역할</th><th>해석</th></tr></thead>
<tbody>$varTable</tbody>
</table>
<p><b>권장 구조:</b> 메인 모형에는 <code>대응자원투입예산_소나무림ha당_log</code>와 <code>예찰진단예산_소나무림ha당_log</code>를 넣고,
방제법인·이동통제·예산비중·반출금지구역 변수는 확장 또는 민감도 분석에서 따로 확인한다.</p>

<h2>3. 전체 변수 기술통계</h2>
<table>
<thead><tr><th>변수</th><th>역할</th><th>관측</th><th>결측률</th><th>평균</th><th>중앙값</th><th>최소</th><th>최대</th><th>0 비율</th></tr></thead>
<tbody>$statTable</tbody>
</table>

<h2>4. 결측 구조</h2>
<table>
<thead><tr><th>변수</th><th>결측률</th><th>값</th></tr></thead>
<tbody>$missHtml</tbody>
</table>
<p>방제법인 변수와 반출금지구역 변수는 예산 변수보다 결측·최신성 문제가 크다. 따라서 메인 설명변수로 바로 고정하기보다
확장/민감도 분석으로 두는 편이 더 안전하다.</p>

<h2>5. 연도별 변화 시각화</h2>
$line
<p>예산 강도 변수는 연도별로 증가 또는 구조 변화가 보인다. 특히 예찰·이동통제 변수는 0 또는 결측 처리의 영향을 받을 수 있어,
단순 평균 추세만으로 정책 효과를 해석하면 안 된다.</p>

<h2>6. 외적타당성: 발생성과 변수와의 탐색적 관계</h2>
<table>
<thead><tr><th>설명변수 후보</th><th>성과변수</th><th>Pearson 상관</th></tr></thead>
<tbody>$corrHtml</tbody>
</table>
<p>이 표는 인과효과가 아니라 방향성과 안정성을 보는 탐색적 진단이다. 대응역량 변수는 발생이 많은 지역에 더 많이 배정되는 경향도
같이 반영할 수 있으므로, 상관이 양수라고 해서 대응역량이 피해를 늘린다는 뜻은 아니다.</p>

<h2>7. 최종 판단</h2>
<table>
<thead><tr><th>구분</th><th>변수</th><th>모델링 판단</th></tr></thead>
<tbody>
<tr><td>메인 변수</td><td>대응자원투입예산_소나무림ha당_log, 예찰진단예산_소나무림ha당_log</td><td>지수화하지 않고 개별 변수로 투입</td></tr>
<tr><td>확장 변수</td><td>방제법인수_소나무림1만ha당_log</td><td>법인자료 최신성 한계 때문에 확장 모형에서 사용</td></tr>
<tr><td>보조/민감도</td><td>이동통제예산_소나무림ha당_log, 예찰진단예산비중, 이동통제예산비중</td><td>예산 구조와 기능별 차이를 확인하는 대체 사양</td></tr>
<tr><td>주의 변수</td><td>반출금지구역_지정여부, 반출금지구역면적비율</td><td>발생 이후 조치 성격이 있어 내생성 주의. 민감도 분석에 제한적으로 사용</td></tr>
<tr><td>제외</td><td>A/B 통합지수</td><td>현재 분석 방향이 비지수화이므로 모델 투입 후보에서 제외</td></tr>
</tbody>
</table>

<p class="small">함께 생성된 모델링용 파일: CH2 data/CH2 전체변수/CH2_지자체대응역량_모델링용_비지수_최종후보.csv</p>
</main>
</body>
</html>
"@

[System.IO.File]::WriteAllText($OutPath, $html, [System.Text.Encoding]::UTF8)

Write-Output "REPORT=$OutPath"
Write-Output "MODEL=$ModelOut"
Write-Output "DICT=$DictOut"
