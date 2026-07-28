$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$MainPath = Join-Path $Root "CH2 data\CH2 전체변수\CH2_지자체대응역량_최종변수선정.csv"
$ExtPath = Join-Path $Root "CH2 data\CH2_지자체대응역량_메인+확장.csv"
$PanelPath = Join-Path $Root "data\CH2\3. 지자체\중간과정\CH2_local_capacity_final_panel.csv"
$OutPath = Join-Path $PSScriptRoot "지자체_report_3차_전체EDA_외적타당성.html"

function ToNum($v) {
    if ($null -eq $v) { return [double]::NaN }
    $s = ([string]$v).Trim()
    if ([string]::IsNullOrWhiteSpace($s)) { return [double]::NaN }
    $d = 0.0
    if ([double]::TryParse($s, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$d)) { return $d }
    if ([double]::TryParse($s, [ref]$d)) { return $d }
    return [double]::NaN
}
function Valid($x) { return -not ([double]::IsNaN($x) -or [double]::IsInfinity($x)) }
function Safe($s) { return [System.Net.WebUtility]::HtmlEncode([string]$s) }
function Fmt($x, [int]$d = 3) {
    if ($null -eq $x) { return "" }
    $n = [double]$x
    if (-not (Valid $n)) { return "" }
    return ([math]::Round($n, $d)).ToString("N$d")
}
function Mean($xs) {
    $sum = 0.0; $n = 0
    foreach ($x in $xs) { if (Valid $x) { $sum += $x; $n++ } }
    if ($n -eq 0) { return $null }
    return $sum / $n
}
function Std($xs) {
    $valid = @($xs | Where-Object { Valid $_ })
    if ($valid.Count -le 1) { return $null }
    $m = Mean $valid; $ss = 0.0
    foreach ($x in $valid) { $ss += ([double]$x - $m) * ([double]$x - $m) }
    return [math]::Sqrt($ss / ($valid.Count - 1))
}
function Quantile($xs, [double]$p) {
    $v = @($xs | Where-Object { Valid $_ } | Sort-Object)
    if ($v.Count -eq 0) { return $null }
    if ($v.Count -eq 1) { return [double]$v[0] }
    $pos = ($v.Count - 1) * $p
    $lo = [math]::Floor($pos); $hi = [math]::Ceiling($pos)
    if ($lo -eq $hi) { return [double]$v[$lo] }
    return [double]$v[$lo] + (([double]$v[$hi] - [double]$v[$lo]) * ($pos - $lo))
}
function Skew($xs) {
    $v = @($xs | Where-Object { Valid $_ })
    if ($v.Count -lt 3) { return $null }
    $m = Mean $v; $sd = Std $v
    if ($null -eq $sd -or $sd -eq 0) { return $null }
    $sum = 0.0
    foreach ($x in $v) { $sum += [math]::Pow(([double]$x - $m) / $sd, 3) }
    return $sum / $v.Count
}
function Corr($rows, $a, $b) {
    $pairs = @()
    foreach ($r in $rows) {
        $x = ToNum $r.$a; $y = ToNum $r.$b
        if ((Valid $x) -and (Valid $y)) { $pairs += ,@($x, $y) }
    }
    if ($pairs.Count -le 2) { return $null }
    $xs = @($pairs | ForEach-Object { $_[0] })
    $ys = @($pairs | ForEach-Object { $_[1] })
    $mx = Mean $xs; $my = Mean $ys
    $num = 0.0; $dx = 0.0; $dy = 0.0
    foreach ($p in $pairs) {
        $vx = $p[0] - $mx; $vy = $p[1] - $my
        $num += $vx * $vy; $dx += $vx * $vx; $dy += $vy * $vy
    }
    if ($dx -eq 0 -or $dy -eq 0) { return $null }
    return $num / [math]::Sqrt($dx * $dy)
}
function Invert-Matrix($A) {
    $n = $A.Count
    $M = New-Object 'object[]' $n
    for ($i = 0; $i -lt $n; $i++) {
        $M[$i] = New-Object 'double[]' ($n * 2)
        for ($j = 0; $j -lt $n; $j++) { $M[$i][$j] = [double]$A[$i][$j] }
        $M[$i][$n + $i] = 1.0
    }
    for ($i = 0; $i -lt $n; $i++) {
        $pivot = $i
        for ($r = $i + 1; $r -lt $n; $r++) {
            if ([math]::Abs($M[$r][$i]) -gt [math]::Abs($M[$pivot][$i])) { $pivot = $r }
        }
        if ([math]::Abs($M[$pivot][$i]) -lt 1e-10) { return $null }
        if ($pivot -ne $i) { $tmp = $M[$i]; $M[$i] = $M[$pivot]; $M[$pivot] = $tmp }
        $div = $M[$i][$i]
        for ($c = 0; $c -lt $n * 2; $c++) { $M[$i][$c] = $M[$i][$c] / $div }
        for ($r = 0; $r -lt $n; $r++) {
            if ($r -eq $i) { continue }
            $factor = $M[$r][$i]
            for ($c = 0; $c -lt $n * 2; $c++) { $M[$r][$c] = $M[$r][$c] - ($factor * $M[$i][$c]) }
        }
    }
    $Inv = New-Object 'object[]' $n
    for ($i = 0; $i -lt $n; $i++) {
        $Inv[$i] = New-Object 'double[]' $n
        for ($j = 0; $j -lt $n; $j++) { $Inv[$i][$j] = $M[$i][$n + $j] }
    }
    return $Inv
}
function Make-Stats($rows, $vars) {
    $n = $rows.Count
    foreach ($v in $vars) {
        $xs = @($rows | ForEach-Object { ToNum $_.$v })
        $valid = @($xs | Where-Object { Valid $_ })
        $zero = @($valid | Where-Object { [math]::Abs($_) -lt 1e-12 }).Count
        [pscustomobject]@{
            변수 = $v
            관측치 = $valid.Count
            결측치 = $n - $valid.Count
            결측률 = if ($n -eq 0) { $null } else { ($n - $valid.Count) / [double]$n }
            평균 = Mean $valid
            표준편차 = Std $valid
            최소 = Quantile $valid 0
            Q1 = Quantile $valid 0.25
            중앙값 = Quantile $valid 0.5
            Q3 = Quantile $valid 0.75
            최대 = Quantile $valid 1
            왜도 = Skew $valid
            영비율 = if ($valid.Count -eq 0) { $null } else { $zero / [double]$valid.Count }
        }
    }
}
function Make-Vif($rows, $vars) {
    $complete = @($rows | Where-Object {
        $ok = $true
        foreach ($v in $vars) { if (-not (Valid (ToNum $_.$v))) { $ok = $false; break } }
        $ok
    })
    if ($vars.Count -eq 1) { return @([pscustomobject]@{ 변수=$vars[0]; VIF=1.0; 완전관측=$complete.Count; 판정="단일 변수" }) }
    $corr = New-Object 'object[]' $vars.Count
    for ($i=0; $i -lt $vars.Count; $i++) {
        $corr[$i] = New-Object 'double[]' $vars.Count
        for ($j=0; $j -lt $vars.Count; $j++) {
            $c = if ($i -eq $j) { 1.0 } else { Corr $complete $vars[$i] $vars[$j] }
            if ($null -eq $c) { return @([pscustomobject]@{ 변수="전체"; VIF=$null; 완전관측=$complete.Count; 판정="상관계산 불가" }) }
            $corr[$i][$j] = [double]$c
        }
    }
    $inv = Invert-Matrix $corr
    if ($null -eq $inv) { return @([pscustomobject]@{ 변수="전체"; VIF=$null; 완전관측=$complete.Count; 판정="상관행렬 특이: 강한 중복 가능" }) }
    $out = @()
    for ($i=0; $i -lt $vars.Count; $i++) {
        $vif = $inv[$i][$i]
        $judge = if ($vif -ge 10) { "높음: 제외/분리 검토" } elseif ($vif -ge 5) { "주의" } else { "양호" }
        $out += [pscustomobject]@{ 변수=$vars[$i]; VIF=$vif; 완전관측=$complete.Count; 판정=$judge }
    }
    return $out
}
function Table-Html($rows, $cols) {
    $head = ($cols | ForEach-Object { "<th>$(Safe $_)</th>" }) -join ""
    $body = ($rows | ForEach-Object {
        $r = $_
        "<tr>" + (($cols | ForEach-Object {
            $val = $r.$_
            if ($val -is [double] -or $val -is [single] -or $val -is [decimal]) { "<td>$(Fmt $val 3)</td>" }
            else { "<td>$(Safe $val)</td>" }
        }) -join "") + "</tr>"
    }) -join "`n"
    return "<table><thead><tr>$head</tr></thead><tbody>$body</tbody></table>"
}
function Stats-Html($stats) {
    $rows = $stats | ForEach-Object {
        [pscustomobject]@{
            변수=$_.변수; 관측치=$_.관측치; 결측치=$_.결측치; 결측률=Fmt ($_.결측률*100) 1;
            평균=Fmt $_.평균 3; 표준편차=Fmt $_.표준편차 3; 최소=Fmt $_.최소 3; Q1=Fmt $_.Q1 3;
            중앙값=Fmt $_.중앙값 3; Q3=Fmt $_.Q3 3; 최대=Fmt $_.최대 3; 왜도=Fmt $_.왜도 3; 영비율=Fmt ($_.영비율*100) 1
        }
    }
    return Table-Html $rows @("변수","관측치","결측치","결측률","평균","표준편차","최소","Q1","중앙값","Q3","최대","왜도","영비율")
}
function LineSvg($rows, $vars, $title) {
    $years = @($rows | Group-Object 연도 | Sort-Object Name | ForEach-Object { [int]$_.Name })
    $series = @()
    foreach ($v in $vars) {
        $vals = @()
        foreach ($y in $years) { $vals += Mean (@($rows | Where-Object { [int]$_.연도 -eq $y } | ForEach-Object { ToNum $_.$v })) }
        $series += [pscustomobject]@{label=$v; values=$vals}
    }
    $valsAll = @($series | ForEach-Object { $_.values } | Where-Object { $null -ne $_ })
    if ($valsAll.Count -eq 0) { return "<p>시각화할 값이 없습니다.</p>" }
    $w=920; $h=300; $l=68; $r=24; $t=34; $b=42
    $min=[double]($valsAll | Measure-Object -Minimum).Minimum; $max=[double]($valsAll | Measure-Object -Maximum).Maximum
    if ($min -eq $max) { $min -= 1; $max += 1 }
    $pw=$w-$l-$r; $ph=$h-$t-$b
    $colors=@("#2f6f9f","#d48331","#4e8b5b","#8a5a9e","#b04f5f","#566573","#9a6b28","#1f8a83")
    $svg="<svg viewBox='0 0 $w $h' class='chart'><rect width='$w' height='$h' fill='#fff'/><text x='$l' y='22' class='svg-title'>$(Safe $title)</text>"
    for ($i=0;$i -lt 5;$i++){ $y=$t+$ph*$i/4; $val=$max-($max-$min)*$i/4; $svg+="<line x1='$l' y1='$y' x2='$($w-$r)' y2='$y' stroke='#e7e2d9'/><text x='8' y='$($y+4)' class='tick'>$(Fmt $val 1)</text>" }
    for ($i=0;$i -lt $years.Count;$i++){ $x=$l+$pw*$i/[math]::Max(1,$years.Count-1); $svg+="<text x='$($x-14)' y='$($h-14)' class='tick'>$($years[$i])</text>" }
    for ($s=0;$s -lt $series.Count;$s++){
        $pts=@()
        for ($i=0;$i -lt $years.Count;$i++){
            $v=$series[$s].values[$i]; if ($null -eq $v) { continue }
            $x=$l+$pw*$i/[math]::Max(1,$years.Count-1); $y=$t+$ph*($max-[double]$v)/($max-$min)
            $pts+="$x,$y"; $svg+="<circle cx='$x' cy='$y' r='3' fill='$($colors[$s % $colors.Count])'/>"
        }
        if ($pts.Count -gt 1) { $svg+="<polyline points='$($pts -join " ")' fill='none' stroke='$($colors[$s % $colors.Count])' stroke-width='2.2'/>" }
        $lx=$l+10+(($s%2)*410); $ly=48+([math]::Floor($s/2)*18)
        $svg+="<rect x='$lx' y='$($ly-9)' width='10' height='10' fill='$($colors[$s % $colors.Count])'/><text x='$($lx+16)' y='$ly' class='legend'>$(Safe $series[$s].label)</text>"
    }
    $svg+="</svg>"
    return $svg
}
function Corr-Html($rows, $vars, $title) {
    $html="<h4>$(Safe $title)</h4><table><thead><tr><th>변수</th>"
    foreach ($v in $vars) { $html+="<th>$(Safe $v)</th>" }
    $html+="</tr></thead><tbody>"
    foreach ($a in $vars) {
        $html+="<tr><th>$(Safe $a)</th>"
        foreach ($b in $vars) {
            $c = if ($a -eq $b) { 1.0 } else { Corr $rows $a $b }
            $light = if ($null -eq $c) { 96 } else { 94 - [math]::Min(34, [math]::Abs($c)*58) }
            $hue = if ($null -eq $c) { 0 } elseif ($c -ge 0) { 205 } else { 18 }
            $html += "<td style='background:hsl($hue,55%,$light%)'>$(Fmt $c 2)</td>"
        }
        $html+="</tr>"
    }
    return $html + "</tbody></table>"
}
function External-Html($rows, $vars, $outcomes) {
    $pairs=@()
    foreach($v in $vars){ foreach($o in $outcomes){ $pairs += [pscustomobject]@{설명변수=$v; 성과변수=$o; 상관=Corr $rows $v $o} } }
    $pairs2 = $pairs | ForEach-Object { [pscustomobject]@{ 설명변수=$_.설명변수; 성과변수=$_.성과변수; 상관=Fmt $_.상관 3 } }
    return Table-Html $pairs2 @("설명변수","성과변수","상관")
}

$main = @(Import-Csv -LiteralPath $MainPath -Encoding UTF8)
$ext = @(Import-Csv -LiteralPath $ExtPath -Encoding UTF8)
$panel = @(Import-Csv -LiteralPath $PanelPath -Encoding UTF8)
$outcomeMap = @{}
foreach ($p in $panel) {
    $key = "$($p.year)|$($p.sigungu_cd)"
    $outcomeMap[$key] = $p
}
function Add-Outcomes($rows) {
    foreach ($r in $rows) {
        $key = "$($r.연도)|$($r.시군구코드)"
        $o = $outcomeMap[$key]
        $r | Add-Member -NotePropertyName "당해_감염지점수" -NotePropertyValue $(if ($null -eq $o) { "" } else { $o.current_infected_sites }) -Force
        $r | Add-Member -NotePropertyName "재발생지점수_300m" -NotePropertyValue $(if ($null -eq $o) { "" } else { $o.recurrent_sites_300m }) -Force
        $r | Add-Member -NotePropertyName "재발생률_300m" -NotePropertyValue $(if ($null -eq $o) { "" } else { $o.recurrence_rate_300m }) -Force
        $r | Add-Member -NotePropertyName "신규발생지비율_300m" -NotePropertyValue $(if ($null -eq $o) { "" } else { $o.new_site_share_300m }) -Force
    }
    return $rows
}
$main = Add-Outcomes $main
$ext = Add-Outcomes $ext

$mainVars = @("대응자원투입예산_소나무림ha당_log","예찰진단예산_소나무림ha당_log")
$extVars = @("대응자원투입예산_소나무림ha당_log","예찰진단예산_소나무림ha당_log","방제법인수_소나무림1만ha당_log","이동통제예산_소나무림ha당_log","예찰진단예산비중","이동통제예산비중","반출금지구역_지정여부","반출금지구역면적비율")
$outcomes = @("당해_감염지점수","재발생지점수_300m","재발생률_300m","신규발생지비율_300m")

$mainEligible = @($main | Where-Object { $_.예산자료_사용가능여부 -eq "1" })
$extBudgetEligible = @($ext | Where-Object { $_.예산자료_사용가능여부 -eq "1" })
$extComplete = @($ext | Where-Object {
    $ok=$true
    foreach($v in $extVars){ if (-not (Valid (ToNum $_.$v))) { $ok=$false; break } }
    $ok
})

$mainStats = Make-Stats $main $mainVars
$extStats = Make-Stats $ext $extVars
$mainVif = Make-Vif $mainEligible $mainVars
$extVif = Make-Vif $ext $extVars

$mainPanelDiag = @(
    [pscustomobject]@{항목="행 수"; 값=$main.Count},
    [pscustomobject]@{항목="열 수"; 값=$main[0].PSObject.Properties.Name.Count},
    [pscustomobject]@{항목="시군구 수"; 값=@($main | Group-Object 시군구코드).Count},
    [pscustomobject]@{항목="연도 범위"; 값="$(($main | ForEach-Object {[int]$_.연도} | Measure-Object -Minimum).Minimum)-$(($main | ForEach-Object {[int]$_.연도} | Measure-Object -Maximum).Maximum)"},
    [pscustomobject]@{항목="연도×시군구코드 중복"; 값=@($main | Group-Object 연도,시군구코드 | Where-Object Count -gt 1).Count},
    [pscustomobject]@{항목="예산자료 사용가능 행"; 값=$mainEligible.Count}
)
$extPanelDiag = @(
    [pscustomobject]@{항목="행 수"; 값=$ext.Count},
    [pscustomobject]@{항목="열 수"; 값=$ext[0].PSObject.Properties.Name.Count},
    [pscustomobject]@{항목="시군구 수"; 값=@($ext | Group-Object 시군구코드).Count},
    [pscustomobject]@{항목="연도 범위"; 값="$(($ext | ForEach-Object {[int]$_.연도} | Measure-Object -Minimum).Minimum)-$(($ext | ForEach-Object {[int]$_.연도} | Measure-Object -Maximum).Maximum)"},
    [pscustomobject]@{항목="연도×시군구코드 중복"; 값=@($ext | Group-Object 연도,시군구코드 | Where-Object Count -gt 1).Count},
    [pscustomobject]@{항목="확장변수 완전관측 행"; 값=$extComplete.Count},
    [pscustomobject]@{항목="법인자료 최신성 주의 행"; 값=@($ext | Where-Object 법인자료_최신성주의플래그 -eq "1").Count}
)

$vifMainHtml = Table-Html ($mainVif | ForEach-Object { [pscustomobject]@{변수=$_.변수; VIF=Fmt $_.VIF 3; 완전관측=$_.완전관측; 판정=$_.판정} }) @("변수","VIF","완전관측","판정")
$vifExtHtml = Table-Html ($extVif | ForEach-Object { [pscustomobject]@{변수=$_.변수; VIF=Fmt $_.VIF 3; 완전관측=$_.완전관측; 판정=$_.판정} }) @("변수","VIF","완전관측","판정")

$html = @"
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>CH2 지자체 대응역량 3차 전체 EDA 및 외적타당성</title>
<style>
body{font-family:"Malgun Gothic",Arial,sans-serif;margin:0;background:#fbfaf7;color:#252525;line-height:1.58}
main{max-width:1220px;margin:0 auto;padding:34px 28px 70px}
h1{font-size:30px;margin:0 0 8px} h2{font-size:22px;margin:36px 0 12px;border-top:1px solid #ddd5c9;padding-top:22px}
h3{font-size:18px;margin:24px 0 10px} h4{font-size:15px;margin:18px 0 8px}
.meta,.small{color:#666;font-size:13px}.notice{background:#fff3cd;border:1px solid #e3ce7c;padding:14px 16px;border-radius:8px;margin:16px 0}
.toc{background:#fff;border:1px solid #e1ddd4;border-radius:8px;padding:14px 18px;margin:18px 0}.toc a{display:block;color:#255f85;text-decoration:none;margin:4px 0}
table{border-collapse:collapse;width:100%;background:#fff;margin:10px 0 20px} th,td{border:1px solid #e1ddd4;padding:7px 9px;text-align:left;font-size:13px;vertical-align:top} th{background:#f0eee8}
.chart{width:100%;height:auto;border:1px solid #e1ddd4;background:#fff;border-radius:8px;margin:10px 0 18px}.svg-title{font-size:15px;font-weight:700;fill:#222}.tick{font-size:11px;fill:#666}.legend{font-size:11px;fill:#333}
code{background:#eee8dc;padding:1px 4px;border-radius:4px}.warn{color:#9a5b00;font-weight:700}.ok{color:#1f6f4a;font-weight:700}
</style>
</head>
<body><main>
<h1>CH2 지자체 대응역량 3차 전체 EDA 및 외적타당성</h1>
<div class="meta">생성일: $(Get-Date -Format "yyyy-MM-dd HH:mm") · 입력 1: CH2_지자체대응역량_최종변수선정.csv · 입력 2: CH2_지자체대응역량_메인+확장.csv</div>
<div class="notice">이번 보고서는 최신 최종 파일 2개를 기준으로 다시 생성했다. 지수화 변수는 사용하지 않고, 메인 예산 기반 변수와 확장/민감도 변수를 분리해 점검한다. 외적타당성은 기존 최종 패널의 발생·재발생 성과변수를 <code>연도×시군구코드</code>로 병합해 탐색적으로 확인했다.</div>

<div class="toc">
<b>목차</b>
<a href="#main">1. 최종변수선정 파일 EDA</a>
<a href="#main-validity">2. 최종변수선정 파일 외적타당성</a>
<a href="#ext">3. 메인+확장 파일 EDA</a>
<a href="#ext-validity">4. 메인+확장 파일 외적타당성</a>
<a href="#modeling">5. 모델링 전 최종 판단</a>
</div>

<h2 id="main">1. 최종변수선정 파일 EDA</h2>
<p>이 파일은 주 모형에 바로 투입할 메인 변수만 담은 파일이다. <code>예산자료_사용가능여부=1</code>인 행을 주 분석 표본으로 사용한다.</p>
$(Table-Html $mainPanelDiag @("항목","값"))
<h3>기본 기술통계</h3>
$(Stats-Html $mainStats)
<h3>연도별 평균 추세</h3>
$(LineSvg $main $mainVars "최종변수선정: 메인 변수 연도별 평균")
<h3>상관관계</h3>
$(Corr-Html $mainEligible $mainVars "최종변수선정: 메인 변수 상관관계")
<h3>VIF</h3>
$vifMainHtml
<p class="small">VIF는 <code>예산자료_사용가능여부=1</code> 표본에서 계산했다. 두 메인 변수의 중복성이 높지 않으면 같은 모형에 함께 넣을 수 있다.</p>

<h2 id="main-validity">2. 최종변수선정 파일 외적타당성</h2>
<p>외적타당성은 대응역량 변수가 발생·재발생 성과와 완전히 무관하지 않은지 확인하는 탐색적 절차다. 여기의 상관은 인과효과가 아니다.</p>
$(External-Html $mainEligible $mainVars $outcomes)

<h2 id="ext">3. 메인+확장 파일 EDA</h2>
<p>이 파일은 메인 변수에 방제 인프라, 이동통제, 예산 배분구조, 반출금지구역 관련 변수를 더한 확장/민감도 분석용 파일이다.</p>
$(Table-Html $extPanelDiag @("항목","값"))
<h3>기본 기술통계</h3>
$(Stats-Html $extStats)
<h3>연도별 평균 추세</h3>
$(LineSvg $ext $extVars "메인+확장: 후보 변수 연도별 평균")
<h3>상관관계</h3>
$(Corr-Html $ext $extVars "메인+확장: 후보 변수 상관관계")
<h3>VIF</h3>
$vifExtHtml
<p class="small">확장 VIF는 모든 후보 변수가 관측된 완전관측 표본 기준이다. 완전관측 수가 작거나 VIF가 높으면 변수를 한꺼번에 넣기보다 확장 사양을 나누는 편이 안전하다.</p>

<h2 id="ext-validity">4. 메인+확장 파일 외적타당성</h2>
<p>확장 변수는 이론적 설명 범위를 넓히지만, 일부 변수는 자료 최신성·내생성·극단값 문제가 있다. 특히 법인자료는 2022-2023년에 최신성 주의 플래그가 켜져 있고, 반출금지구역 변수는 발생 이후 지정되는 성격이 강하다.</p>
$(External-Html $ext $extVars $outcomes)

<h2 id="modeling">5. 모델링 전 최종 판단</h2>
<table><thead><tr><th>구분</th><th>권장 사용</th><th>이유</th></tr></thead><tbody>
<tr><td>주 모형</td><td><code>CH2_지자체대응역량_최종변수선정.csv</code>에서 예산 2개 사용</td><td>자료 품질이 가장 안정적이고, 예산 기반 대응역량이라는 개념이 명확하다.</td></tr>
<tr><td>표본 필터</td><td><code>예산자료_사용가능여부=1</code></td><td>0값은 실제 관측된 0으로 유지하고, 사용가능여부 0인 행만 계산 불가로 제외한다.</td></tr>
<tr><td>확장 분석</td><td>메인 변수 + <code>방제법인수_소나무림1만ha당_log</code></td><td>실제 방제 수행 인프라를 보완하지만 2022-2023 최신성 한계가 있어 주 모형보다 보조가 적절하다.</td></tr>
<tr><td>민감도 분석</td><td>이동통제예산, 예산비중 변수</td><td>총량이 아닌 기능별·배분구조 해석에 유용하다.</td></tr>
<tr><td>주의 분석</td><td>반출금지구역 지정여부/면적비율</td><td>정책 대응 조치이지만 발생 이후 지정되는 성격이 강해 내생성 주의가 필요하다.</td></tr>
</tbody></table>
<p><b>종합 판단:</b> 소나무재선충병 대응역량을 설명하기에는 메인 예산 2개만으로도 이론적 기본축은 충족한다. 다만 “현장 실행력”까지 주장하려면 확장 변수로 방제법인을 보조적으로 제시하는 것이 좋다. 따라서 본문 주 분석은 최종변수선정 파일, 부록 또는 강건성 분석은 메인+확장 파일을 쓰는 구성이 가장 방어 가능하다.</p>
</main></body></html>
"@

$enc = New-Object System.Text.UTF8Encoding($true)
[System.IO.File]::WriteAllText($OutPath, $html, $enc)
Write-Output "REPORT=$OutPath"
Write-Output "MAIN_ROWS=$($main.Count)"
Write-Output "EXT_ROWS=$($ext.Count)"
Write-Output "MAIN_ELIGIBLE=$($mainEligible.Count)"
Write-Output "EXT_COMPLETE=$($extComplete.Count)"
