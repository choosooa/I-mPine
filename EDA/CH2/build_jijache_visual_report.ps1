$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$PanelPath = $null
foreach ($f in (Get-ChildItem -LiteralPath (Join-Path $Root "data\CH2") -Recurse -File -Filter "CH2_local_capacity_final_panel.csv")) {
    $PanelPath = $f.FullName
    break
}
if ($null -eq $PanelPath) { throw "CH2_local_capacity_final_panel.csv not found." }
$OutPath = Join-Path $PSScriptRoot "jijache_report_4_full_visual_eda_external_validity.html"

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
    return [math]::Round($sum / $n, 6)
}
function Values($rows, $col) {
    $arr = @()
    foreach ($r in $rows) {
        $v = ToNum $r.$col
        if (Valid $v) { $arr += [math]::Round($v, 6) }
    }
    return $arr
}
function Corr($rows, $a, $b) {
    $pairs = @()
    foreach ($r in $rows) {
        $x = ToNum $r.$a; $y = ToNum $r.$b
        if ((Valid $x) -and (Valid $y)) { $pairs += ,@($x,$y) }
    }
    if ($pairs.Count -le 2) { return $null }
    $sx=0.0; $sy=0.0
    foreach ($p in $pairs) { $sx += $p[0]; $sy += $p[1] }
    $mx=$sx/$pairs.Count; $my=$sy/$pairs.Count
    $num=0.0; $dx=0.0; $dy=0.0
    foreach ($p in $pairs) {
        $vx=$p[0]-$mx; $vy=$p[1]-$my
        $num += $vx*$vy; $dx += $vx*$vx; $dy += $vy*$vy
    }
    if ($dx -eq 0 -or $dy -eq 0) { return $null }
    return [math]::Round($num/[math]::Sqrt($dx*$dy), 4)
}

$rows = @(Import-Csv -LiteralPath $PanelPath)
$years = @(2016..2023)
$trendVars = @("log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha","log_movement_budget_per_pine_ha","log_active_pest_firm_per_10000_pine_ha")
$indexVars = @("capacity_index_A_pooled","capacity_index_B_pooled")
$histVars = @("capacity_index_A_pooled","capacity_index_B_pooled","log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha","log_active_pest_firm_per_10000_pine_ha","log_movement_budget_per_pine_ha")
$heatVars = @("log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha","log_movement_budget_per_pine_ha","log_active_pest_firm_per_10000_pine_ha","surveillance_share","movement_share_included_budget","active_restriction_area_ratio","capacity_index_A_pooled","capacity_index_B_pooled","current_infected_sites","recurrence_rate_300m","new_site_share_300m")

$trend = @()
foreach ($v in $trendVars) {
    $vals = @()
    foreach ($y in $years) { $vals += Mean (@($rows | Where-Object { [int]$_.year -eq $y } | ForEach-Object { ToNum $_.$v })) }
    $trend += [PSCustomObject]@{ name=$v; values=$vals }
}
$indices = @()
foreach ($v in $indexVars) {
    $vals = @()
    foreach ($y in $years) { $vals += Mean (@($rows | Where-Object { [int]$_.year -eq $y } | ForEach-Object { ToNum $_.$v })) }
    $indices += [PSCustomObject]@{ name=$v; values=$vals }
}
$missing = @()
foreach ($c in $rows[0].PSObject.Properties.Name) {
    $m = @($rows | Where-Object { [string]::IsNullOrWhiteSpace([string]($_.$c)) }).Count
    $missing += [PSCustomObject]@{ label=$c; value=[math]::Round($m/[double]$rows.Count, 4) }
}
$missing = @($missing | Sort-Object value -Descending | Select-Object -First 15)
$sido = @()
foreach ($g in ($rows | Group-Object sido)) {
    $m = Mean (@($g.Group | ForEach-Object { ToNum $_.capacity_index_A_pooled }))
    if ($null -ne $m) { $sido += [PSCustomObject]@{ label=$g.Name; value=$m } }
}
$sido = @($sido | Sort-Object value -Descending)
$top2023 = @()
foreach ($r in (@($rows | Where-Object { [int]$_.year -eq 2023 -and (Valid (ToNum $_.capacity_index_A_pooled)) } | Sort-Object @{Expression={-(ToNum $_.capacity_index_A_pooled)}} | Select-Object -First 12))) {
    $top2023 += [PSCustomObject]@{ label=("$($r.sido) $($r.sigungu_nm)"); value=[math]::Round((ToNum $r.capacity_index_A_pooled), 4); pine_area=[math]::Round((ToNum $r.pine_area_ha_applied), 2); budget=[math]::Round((ToNum $r.included_local_budget), 0) }
}
$hists = @()
foreach ($v in $histVars) { $hists += [PSCustomObject]@{ name=$v; values=(Values $rows $v) } }
$corr = @()
foreach ($a in $heatVars) {
    $row = @()
    foreach ($b in $heatVars) { $row += Corr $rows $a $b }
    $corr += ,$row
}

$payload = [PSCustomObject]@{
    years=$years
    trend=$trend
    indices=$indices
    missing=$missing
    sido=$sido
    top2023=$top2023
    hists=$hists
    heatVars=$heatVars
    corr=$corr
}
$json = $payload | ConvertTo-Json -Depth 8 -Compress

$html = @'
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CH2 Local Capacity Visual EDA</title>
<style>
body{margin:0;background:#f6f7f9;color:#1f2933;font-family:Arial,sans-serif;line-height:1.6}
main{max-width:1180px;margin:0 auto;background:#fff;padding:38px 30px 70px;box-shadow:0 0 0 1px #e5e7eb}
h1{font-size:30px;margin:0 0 8px;color:#111827}h2{font-size:22px;margin-top:34px;padding-top:18px;border-top:1px solid #e5e7eb;color:#111827}
h3{font-size:16px;margin:0 0 8px;color:#0f172a}.meta{color:#64748b}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:22px 0}
.card{border:1px solid #d9e2ec;border-radius:6px;padding:14px 16px;background:#fbfdff}.card strong{display:block;font-size:22px;color:#0f172a}.card span{color:#64748b;font-size:13px}
.chart{border:1px solid #e2e8f0;border-radius:6px;margin:16px 0;padding:14px;background:#fff;overflow:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid .chart{margin:0}
table{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0 22px}th,td{border:1px solid #d9e2ec;padding:8px 10px;vertical-align:top}th{background:#eef2f7;text-align:left}
code{background:#f1f5f9;border-radius:4px;padding:1px 4px;font-family:Consolas,monospace}.ok{color:#0f766e;font-weight:700}.warn{color:#b45309;font-weight:700}.note{border-left:4px solid #64748b;background:#f8fafc;padding:12px 16px;margin:14px 0}
.small{font-size:12px;color:#64748b}@media(max-width:900px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body><main>
<h1>CH2 Local Government Capacity: Visual EDA + External Validity</h1>
<p class="meta">Standalone HTML report with embedded data and SVG charts. Source: CH2_local_capacity_final_panel.csv.</p>
<div class="cards">
<div class="card"><strong>2,000</strong><span>rows</span></div>
<div class="card"><strong>62</strong><span>variables</span></div>
<div class="card"><strong>2016-2023</strong><span>years</span></div>
<div class="card"><strong>250</strong><span>municipalities per year</span></div>
<div class="card"><strong>1,686</strong><span>A index valid rows</span></div>
<div class="card"><strong>1,264</strong><span>B index valid rows</span></div>
</div>
<h2>1. Visual Diagnostics</h2>
<div id="charts"></div>
<h2>2. Interpretation</h2>
<table>
<tr><th>Finding</th><th>Meaning</th></tr>
<tr><td>Main index A is the safest final variable</td><td>It uses two audited, year-by-municipality budget-capacity measures.</td></tr>
<tr><td>Extended index B is useful but conditional</td><td>It adds pest-control firm infrastructure, but firm data are not complete for 2022-2023.</td></tr>
<tr><td>Movement-budget variables are support variables</td><td>They are conceptually relevant but too zero-heavy for the core index.</td></tr>
<tr><td>Restriction variables are support variables</td><td>They mix response action with infection/risk targeting, so external validity as pure capacity is weaker.</td></tr>
<tr><td>Outcome variables should stay separate</td><td>Current infection, recurrence, and new-site share are outcomes, not capacity inputs.</td></tr>
</table>
<div class="note">Recommended use: main analysis with capacity_index_A_pooled; within-year ranking/maps with capacity_index_A_yearly; robustness with capacity_index_B_pooled/yearly; support variables in the all-variable file for appendix and sensitivity checks.</div>
</main>
<script>
const DATA = __DATA_JSON__;
const colors = ["#2563eb","#dc2626","#059669","#9333ea","#f59e0b","#0f766e"];
const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const fmt = x => x == null || Number.isNaN(x) ? "" : Number(x).toFixed(Math.abs(x) >= 10 ? 1 : 3).replace(/\.?0+$/,"");
function wrap(title, svg, note=""){ return `<div class="chart"><h3>${esc(title)}</h3>${svg}${note?`<p class="small">${esc(note)}</p>`:""}</div>`; }
function lineChart(title, series, years){
  const w=760,h=280,p={l:58,r:20,t:38,b:42}, pw=w-p.l-p.r, ph=h-p.t-p.b;
  const vals=series.flatMap(s=>s.values).filter(v=>v!=null);
  let ymin=Math.min(...vals), ymax=Math.max(...vals); if(ymin===ymax){ymax=ymin+1}
  let svg=`<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#fff"/><line x1="${p.l}" y1="${p.t}" x2="${p.l}" y2="${p.t+ph}" stroke="#94a3b8"/><line x1="${p.l}" y1="${p.t+ph}" x2="${p.l+pw}" y2="${p.t+ph}" stroke="#94a3b8"/>`;
  years.forEach((yr,i)=>{ const x=p.l+pw*i/Math.max(1,years.length-1); svg+=`<text x="${x}" y="${h-15}" text-anchor="middle" font-size="11" fill="#475569">${yr}</text>`; });
  series.forEach((s,k)=>{
    const pts=[]; s.values.forEach((v,i)=>{ if(v!=null){ const x=p.l+pw*i/Math.max(1,years.length-1), y=p.t+ph-((v-ymin)/(ymax-ymin))*ph; pts.push(`${x.toFixed(1)},${y.toFixed(1)}`); }});
    const c=colors[k%colors.length]; svg+=`<polyline points="${pts.join(" ")}" fill="none" stroke="${c}" stroke-width="2.4"/>`;
    svg+=`<circle cx="${p.l+8}" cy="${18+k*16}" r="4" fill="${c}"/><text x="${p.l+18}" y="${22+k*16}" font-size="12" fill="#334155">${esc(s.name)}</text>`;
  });
  svg+=`<text x="8" y="${p.t}" font-size="11" fill="#64748b">${fmt(ymax)}</text><text x="8" y="${p.t+ph}" font-size="11" fill="#64748b">${fmt(ymin)}</text></svg>`;
  return wrap(title, svg);
}
function barChart(title, items, note=""){
  items = items.filter(d=>d.value!=null && !Number.isNaN(d.value));
  const w=760,p={l:150,r:40,t:28,b:28}, bh=18,gap=8,h=Math.max(280,p.t+p.b+items.length*(bh+gap)), pw=w-p.l-p.r;
  let min=Math.min(0,...items.map(d=>d.value)), max=Math.max(0,...items.map(d=>d.value)); if(min===max){max=min+1}
  const zx=p.l+(0-min)/(max-min)*pw;
  let svg=`<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#fff"/><line x1="${zx}" y1="${p.t}" x2="${zx}" y2="${h-p.b+4}" stroke="#94a3b8"/>`;
  items.forEach((d,i)=>{ const y=p.t+i*(bh+gap), x0=p.l+(Math.min(0,d.value)-min)/(max-min)*pw, x1=p.l+(Math.max(0,d.value)-min)/(max-min)*pw, bw=Math.max(1,x1-x0), c=d.value>=0?"#2563eb":"#dc2626"; svg+=`<text x="8" y="${y+13}" font-size="12" fill="#334155">${esc(d.label)}</text><rect x="${x0.toFixed(1)}" y="${y}" width="${bw.toFixed(1)}" height="${bh}" rx="3" fill="${c}"/><text x="${(d.value>=0?x1+6:x0-6).toFixed(1)}" y="${y+13}" text-anchor="${d.value>=0?'start':'end'}" font-size="11" fill="#475569">${fmt(d.value)}</text>`; });
  svg += `</svg>`; return wrap(title, svg, note);
}
function histChart(name, values){
  values=values.filter(v=>v!=null); const bins=20,w=760,h=250,p={l:42,r:16,t:30,b:34},pw=w-p.l-p.r,ph=h-p.t-p.b;
  let min=Math.min(...values), max=Math.max(...values); if(min===max){max=min+1}
  const counts=Array(bins).fill(0); values.forEach(v=>{ let i=Math.floor((v-min)/(max-min)*bins); if(i>=bins)i=bins-1; if(i<0)i=0; counts[i]++; });
  const mc=Math.max(...counts), bw=pw/bins; let svg=`<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#fff"/><line x1="${p.l}" y1="${p.t+ph}" x2="${p.l+pw}" y2="${p.t+ph}" stroke="#94a3b8"/>`;
  counts.forEach((c,i)=>{ const bh=mc?ph*c/mc:0, x=p.l+i*bw, y=p.t+ph-bh; svg+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${Math.max(1,bw-2).toFixed(1)}" height="${bh.toFixed(1)}" fill="#0f766e"/>`; });
  svg+=`<text x="${p.l}" y="${h-10}" font-size="11" fill="#475569">${fmt(min)}</text><text x="${p.l+pw}" y="${h-10}" text-anchor="end" font-size="11" fill="#475569">${fmt(max)}</text></svg>`;
  return wrap("Distribution: "+name, svg);
}
function heatmap(title, vars, matrix){
  const cell=34,labelW=220,top=190,w=labelW+vars.length*cell+20,h=top+vars.length*cell+20;
  let svg=`<svg viewBox="0 0 ${w} ${h}"><rect width="${w}" height="${h}" fill="#fff"/>`;
  vars.forEach((v,i)=>{ svg+=`<text transform="translate(${labelW+i*cell+18},180) rotate(-55)" font-size="10" fill="#334155">${esc(v)}</text><text x="6" y="${top+i*cell+22}" font-size="10" fill="#334155">${esc(v)}</text>`; });
  vars.forEach((_,i)=>vars.forEach((__,j)=>{ const c=matrix[i][j], abs=Math.abs(c ?? 0), fill=(c??0)>=0?`rgba(37,99,235,${abs})`:`rgba(220,38,38,${abs})`; svg+=`<rect x="${labelW+j*cell}" y="${top+i*cell}" width="${cell}" height="${cell}" fill="${fill}" stroke="#e2e8f0"/>`; }));
  svg+=`</svg>`; return wrap(title, svg, "Blue positive, red negative; darker means stronger absolute correlation.");
}
const charts=document.getElementById("charts");
charts.innerHTML =
  lineChart("Yearly mean trend: transformed capacity variables", DATA.trend, DATA.years) +
  lineChart("Yearly mean trend: final indices", DATA.indices, DATA.years) +
  barChart("Top missing-rate variables", DATA.missing) +
  barChart("Sido mean: capacity_index_A_pooled", DATA.sido, "Diverging bars use zero as the vertical axis.") +
  barChart("2023 top municipalities: capacity_index_A_pooled", DATA.top2023, "Inspect pine_area and budget before interpreting top ranks as true capacity.") +
  `<div class="grid">${DATA.hists.map(h=>histChart(h.name,h.values)).join("")}</div>` +
  heatmap("Correlation heatmap: core, support, and outcome variables", DATA.heatVars, DATA.corr);
</script>
</body></html>
'@
$html = $html.Replace("__DATA_JSON__", $json)
Set-Content -LiteralPath $OutPath -Value $html -Encoding UTF8
[PSCustomObject]@{ output=$OutPath; bytes=(Get-Item -LiteralPath $OutPath).Length } | ConvertTo-Json -Compress
