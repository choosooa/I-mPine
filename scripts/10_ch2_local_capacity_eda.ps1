$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Ch2Dir = Join-Path $Root "data\CH2"
$Base = @(Get-ChildItem -LiteralPath $Ch2Dir -Directory | Where-Object { $_.Name -like "3.*" } | Select-Object -First 1)[0].FullName

function To-Num($v) {
    if ($null -eq $v) { return [double]::NaN }
    $s = [string]$v
    if ([string]::IsNullOrWhiteSpace($s)) { return [double]::NaN }
    $d = 0.0
    if ([double]::TryParse($s, [Globalization.NumberStyles]::Any, [Globalization.CultureInfo]::InvariantCulture, [ref]$d)) { return $d }
    if ([double]::TryParse($s, [ref]$d)) { return $d }
    return [double]::NaN
}
function Is-ValidNum($x) { return -not ([double]::IsNaN($x) -or [double]::IsInfinity($x)) }
function Mean($xs) {
    $a = @($xs | Where-Object { Is-ValidNum $_ })
    if ($a.Count -eq 0) { return [double]::NaN }
    return (($a | Measure-Object -Average).Average)
}
function Sum-Nums($xs) {
    $a = @($xs | Where-Object { Is-ValidNum $_ })
    if ($a.Count -eq 0) { return [double]::NaN }
    return (($a | Measure-Object -Sum).Sum)
}
function Std($xs) {
    $a = @($xs | Where-Object { Is-ValidNum $_ })
    if ($a.Count -le 1) { return [double]::NaN }
    $m = Mean $a; $ss = 0.0
    foreach ($x in $a) { $ss += [math]::Pow($x - $m, 2) }
    return [math]::Sqrt($ss / ($a.Count - 1))
}
function Quantile($xs, [double]$p) {
    $a = @($xs | Where-Object { Is-ValidNum $_ } | Sort-Object)
    if ($a.Count -eq 0) { return [double]::NaN }
    if ($a.Count -eq 1) { return [double]$a[0] }
    $pos = ($a.Count - 1) * $p
    $lo = [math]::Floor($pos); $hi = [math]::Ceiling($pos)
    if ($lo -eq $hi) { return [double]$a[$lo] }
    return ([double]$a[$lo] + (($pos - $lo) * ([double]$a[$hi] - [double]$a[$lo])))
}
function Corr($x, $y) {
    $pairs = @()
    for ($i = 0; $i -lt $x.Count; $i++) {
        $xi = [double]$x[$i]; $yi = [double]$y[$i]
        if ((Is-ValidNum $xi) -and (Is-ValidNum $yi)) { $pairs += ,@($xi, $yi) }
    }
    if ($pairs.Count -le 2) { return [double]::NaN }
    $mx = Mean ($pairs | ForEach-Object { $_[0] }); $my = Mean ($pairs | ForEach-Object { $_[1] })
    $num = 0.0; $dx = 0.0; $dy = 0.0
    foreach ($p in $pairs) {
        $vx = $p[0] - $mx; $vy = $p[1] - $my
        $num += $vx * $vy; $dx += $vx * $vx; $dy += $vy * $vy
    }
    if ($dx -eq 0 -or $dy -eq 0) { return [double]::NaN }
    return $num / [math]::Sqrt($dx * $dy)
}
function Ranks($xs) {
    $n = $xs.Count; $rank = New-Object double[] $n
    for ($i = 0; $i -lt $n; $i++) { $rank[$i] = [double]::NaN }
    $valid = @()
    for ($i = 0; $i -lt $n; $i++) {
        $v = [double]$xs[$i]
        if (Is-ValidNum $v) { $valid += [PSCustomObject]@{ I = $i; V = $v } }
    }
    $valid = @($valid | Sort-Object V)
    $pos = 0
    while ($pos -lt $valid.Count) {
        $end = $pos
        while (($end + 1) -lt $valid.Count -and [double]$valid[$end + 1].V -eq [double]$valid[$pos].V) { $end++ }
        $avgRank = (($pos + 1) + ($end + 1)) / 2.0
        for ($j = $pos; $j -le $end; $j++) { $rank[$valid[$j].I] = $avgRank }
        $pos = $end + 1
    }
    return $rank
}
function Spearman($x, $y) { return Corr (Ranks $x) (Ranks $y) }
function Fmt($x) {
    if (-not (Is-ValidNum $x)) { return "" }
    return ([math]::Round([double]$x, 10)).ToString([Globalization.CultureInfo]::InvariantCulture)
}
function Get-Val($row, $col) {
    if ($row.PSObject.Properties.Name -contains $col) { return To-Num $row.$col }
    return [double]::NaN
}
function Add-Or-Set($row, [string]$name, $value) {
    if ($row.PSObject.Properties.Name -contains $name) { $row.$name = $value }
    else { $row | Add-Member -NotePropertyName $name -NotePropertyValue $value }
}
function Write-Utf8Csv($rows, $path) { @($rows) | Export-Csv -LiteralPath $path -NoTypeInformation -Encoding UTF8 }

$PanelPath = $null
foreach ($f in (Get-ChildItem -LiteralPath $Base -Recurse -File -Filter "*.csv")) {
    $head = Get-Content -LiteralPath $f.FullName -TotalCount 1
    if ($head -like "*active_pest_firm_count*" -and $head -like "*extended_index_eligible*") {
        $PanelPath = $f.FullName
        break
    }
}
if ($null -eq $PanelPath) { throw "Panel file not found." }
$Out = Split-Path -Parent $PanelPath

$AuditPath = $null
foreach ($f in (Get-ChildItem -LiteralPath $Out -File -Filter "*.csv")) {
    $rows = @(Import-Csv -LiteralPath $f.FullName)
    if ($rows.Count -gt 0) {
        $cols = $rows[0].PSObject.Properties.Name
        if ($cols.Count -eq 2 -and (($rows | Select-Object -Last 1).($cols[1]) -eq "PASS")) {
            $AuditPath = $f.FullName
        }
    }
}
$auditVerdict = if ($AuditPath) { "PASS" } else { "BASIC ONLY" }
$analysisMode = if ($auditVerdict -eq "PASS") { "PASS" } else { "BASIC ONLY" }
$panel = @(Import-Csv -LiteralPath $PanelPath)

$coreA = @("log_resource_budget_per_pine_ha", "log_surveillance_budget_per_pine_ha")
$coreBExtra = @("log_active_pest_firm_per_10000_pine_ha")
$support = @("log_movement_budget_per_pine_ha", "surveillance_share", "movement_share_included_budget", "active_pest_firm_count", "active_pest_firm_per_10000_pine_ha", "restriction_designated", "active_restriction_area_ratio")
$quality = @("pine_area_ha_applied", "pine_area_positive", "budget_observed", "budget_index_eligible", "extended_index_eligible", "forest_firm_data_stale_flag", "restriction_history_complete_flag", "restriction_date_quality_flag")

function Add-Index($rows, [string]$outName, $vars, [string]$eligibleCol, [bool]$yearly) {
    $groups = if ($yearly) { @($rows | Group-Object year) } else { @([PSCustomObject]@{ Name="pooled"; Group=$rows }) }
    foreach ($g in $groups) {
        $stats = @{}
        foreach ($v in $vars) {
            $eligibleVals = @($g.Group | Where-Object { (Get-Val $_ $eligibleCol) -eq 1 } | ForEach-Object { Get-Val $_ $v } | Where-Object { Is-ValidNum $_ })
            $stats[$v] = @{ Mean = (Mean $eligibleVals); Std = (Std $eligibleVals) }
        }
        foreach ($r in $g.Group) {
            if ((Get-Val $r $eligibleCol) -ne 1) { Add-Or-Set $r $outName ""; continue }
            $zs = @()
            foreach ($v in $vars) {
                $val = Get-Val $r $v; $sd = $stats[$v].Std
                if ((Is-ValidNum $val) -and (Is-ValidNum $sd) -and [math]::Abs($sd) -gt 1e-12) {
                    $zs += (($val - $stats[$v].Mean) / $sd)
                }
            }
            if ($zs.Count -eq $vars.Count) { Add-Or-Set $r $outName (Fmt (Mean $zs)) } else { Add-Or-Set $r $outName "" }
        }
    }
}

Add-Index $panel "capacity_index_A_pooled" $coreA "budget_index_eligible" $false
Add-Index $panel "capacity_index_A_yearly" $coreA "budget_index_eligible" $true
if ($analysisMode -ne "BASIC ONLY") {
    Add-Index $panel "capacity_index_B_pooled" ($coreA + $coreBExtra) "extended_index_eligible" $false
    Add-Index $panel "capacity_index_B_yearly" ($coreA + $coreBExtra) "extended_index_eligible" $true
} else {
    foreach ($r in $panel) { Add-Or-Set $r "capacity_index_B_pooled" ""; Add-Or-Set $r "capacity_index_B_yearly" "" }
}

$edaRows = @()
foreach ($v in ($coreA + $coreBExtra + $support + $quality | Select-Object -Unique)) {
    $vals = @($panel | ForEach-Object { Get-Val $_ $v })
    $valid = @($vals | Where-Object { Is-ValidNum $_ })
    $zeros = @($valid | Where-Object { [math]::Abs($_) -lt 1e-12 })
    $q1 = Quantile $valid 0.25; $q3 = Quantile $valid 0.75
    $iqr = $q3 - $q1
    $outliers = if (Is-ValidNum $iqr) { @($valid | Where-Object { $_ -lt ($q1 - 1.5*$iqr) -or $_ -gt ($q3 + 1.5*$iqr) }) } else { @() }
    $uniqueVals = @($valid | Select-Object -Unique)
    $edaRows += [PSCustomObject]@{
        variable=$v; n_total=$panel.Count; n_obs=$valid.Count; n_missing=$panel.Count-$valid.Count
        missing_rate=Fmt (($panel.Count-$valid.Count)/[double]$panel.Count)
        n_zero=$zeros.Count; zero_rate=if($valid.Count){Fmt ($zeros.Count/[double]$valid.Count)}else{""}
        mean=Fmt (Mean $valid); std=Fmt (Std $valid); min=Fmt (Quantile $valid 0)
        q1=Fmt $q1; median=Fmt (Quantile $valid 0.5); q3=Fmt $q3; max=Fmt (Quantile $valid 1)
        unique_count=$uniqueVals.Count; iqr_outlier_count=$outliers.Count
    }
}

$trendRows = @()
foreach ($v in ($coreA + $coreBExtra + $support + @("resource_local_budget","surveillance_local_budget","movement_local_budget","pine_area_ha_applied"))) {
    $prev = [double]::NaN
    foreach ($year in 2016..2023) {
        $rows = @($panel | Where-Object { [int]$_.year -eq $year })
        $vals = @($rows | ForEach-Object { Get-Val $_ $v })
        $valid = @($vals | Where-Object { Is-ValidNum $_ })
        $m = Mean $valid
        $trendRows += [PSCustomObject]@{
            variable=$v; year=$year; n_obs=$valid.Count; n_missing=$rows.Count-$valid.Count
            missing_rate=Fmt (($rows.Count-$valid.Count)/[double]$rows.Count)
            zero_rate=if($valid.Count){Fmt ((@($valid | Where-Object { [math]::Abs($_)-lt 1e-12 }).Count)/[double]$valid.Count)}else{""}
            simple_mean=Fmt $m; median=Fmt (Quantile $valid 0.5); std=Fmt (Std $valid); sum=Fmt (Sum-Nums $valid)
            yoy_mean_change_rate=if((Is-ValidNum $prev) -and [math]::Abs($prev)-gt 1e-12){Fmt (($m-$prev)/$prev)}else{""}
        }
        $prev = $m
    }
}

$sidoRows = @()
foreach ($v in ($coreA + $coreBExtra + $support + @("capacity_index_A_pooled","capacity_index_B_pooled"))) {
    foreach ($g in ($panel | Group-Object sido)) {
        $vals = @($g.Group | ForEach-Object { Get-Val $_ $v })
        $valid = @($vals | Where-Object { Is-ValidNum $_ })
        $sidoRows += [PSCustomObject]@{
            variable=$v; sido=$g.Name; n_rows=$g.Count; n_obs=$valid.Count
            mean=Fmt (Mean $valid); median=Fmt (Quantile $valid 0.5)
            total_budget=Fmt (Sum-Nums (@($g.Group | ForEach-Object { Get-Val $_ "included_local_budget" })))
            total_pine_area=Fmt (Sum-Nums (@($g.Group | ForEach-Object { Get-Val $_ "pine_area_ha_applied" })))
            budget_eligible_rate=Fmt ((@($g.Group | Where-Object { (Get-Val $_ "budget_index_eligible") -eq 1 }).Count)/[double]$g.Count)
            extended_eligible_rate=Fmt ((@($g.Group | Where-Object { (Get-Val $_ "extended_index_eligible") -eq 1 }).Count)/[double]$g.Count)
        }
    }
}

$rankRows = @()
foreach ($v in ($coreA + $coreBExtra + @("capacity_index_A_pooled","capacity_index_A_yearly","capacity_index_B_pooled","capacity_index_B_yearly"))) {
    foreach ($year in 2016..2023) {
        $validRows = @($panel | Where-Object { [int]$_.year -eq $year -and (Is-ValidNum (Get-Val $_ $v)) })
        foreach ($r in (@($validRows | Sort-Object @{Expression={-(Get-Val $_ $v)}} | Select-Object -First 10))) {
            $rankRows += [PSCustomObject]@{ variable=$v; scope="year_top10"; year=$year; sido=$r.sido; sigungu_nm=$r.sigungu_nm; sigungu_cd=$r.sigungu_cd; value=Fmt (Get-Val $r $v); numerator_hint=Fmt (Get-Val $r "included_local_budget"); pine_area_ha_applied=Fmt (Get-Val $r "pine_area_ha_applied"); budget_observed=$r.budget_observed; budget_missing_reason=$r.budget_missing_reason; pine_area_positive=$r.pine_area_positive; budget_index_eligible=$r.budget_index_eligible; extended_index_eligible=$r.extended_index_eligible; reason_hint="high numerator, small denominator, or genuine capacity" }
        }
        foreach ($r in (@($validRows | Sort-Object @{Expression={Get-Val $_ $v}} | Select-Object -First 10))) {
            $rankRows += [PSCustomObject]@{ variable=$v; scope="year_bottom10"; year=$year; sido=$r.sido; sigungu_nm=$r.sigungu_nm; sigungu_cd=$r.sigungu_cd; value=Fmt (Get-Val $r $v); numerator_hint=Fmt (Get-Val $r "included_local_budget"); pine_area_ha_applied=Fmt (Get-Val $r "pine_area_ha_applied"); budget_observed=$r.budget_observed; budget_missing_reason=$r.budget_missing_reason; pine_area_positive=$r.pine_area_positive; budget_index_eligible=$r.budget_index_eligible; extended_index_eligible=$r.extended_index_eligible; reason_hint="zero/low budget, missing, or large denominator" }
        }
    }
}

$transitionRows = @()
foreach ($v in @("resource_budget_per_pine_ha","surveillance_budget_per_pine_ha","movement_budget_per_pine_ha","active_pest_firm_per_10000_pine_ha")) {
    $numVar = if ($v -eq "active_pest_firm_per_10000_pine_ha") { "active_pest_firm_count" } else { $v -replace "_budget_per_pine_ha","_local_budget" }
    $r2019 = @($panel | Where-Object { [int]$_.year -eq 2019 }); $r2020 = @($panel | Where-Object { [int]$_.year -eq 2020 })
    $m2019 = Mean (@($r2019 | ForEach-Object { Get-Val $_ $v })); $m2020 = Mean (@($r2020 | ForEach-Object { Get-Val $_ $v }))
    $n2019 = Mean (@($r2019 | ForEach-Object { Get-Val $_ $numVar })); $n2020 = Mean (@($r2020 | ForEach-Object { Get-Val $_ $numVar }))
    $d2019 = Mean (@($r2019 | ForEach-Object { Get-Val $_ "pine_area_ha_applied" })); $d2020 = Mean (@($r2020 | ForEach-Object { Get-Val $_ "pine_area_ha_applied" }))
    $transitionRows += [PSCustomObject]@{ variable=$v; numerator=$numVar; denominator="pine_area_ha_applied"; mean_2019=Fmt $m2019; mean_2020=Fmt $m2020; mean_change_rate=if([math]::Abs($m2019)-gt 1e-12){Fmt (($m2020-$m2019)/$m2019)}else{""}; numerator_change_rate=if([math]::Abs($n2019)-gt 1e-12){Fmt (($n2020-$n2019)/$n2019)}else{""}; denominator_change_rate=if([math]::Abs($d2019)-gt 1e-12){Fmt (($d2020-$d2019)/$d2019)}else{""}; diagnosis="decomposed; no automatic correction applied" }
}

$plausRows = @()
foreach ($v in @("capacity_index_A_pooled","capacity_index_B_pooled","log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha")) {
    $x = @($panel | ForEach-Object { Get-Val $_ $v })
    foreach ($outcome in @("recurrence_rate_300m","new_site_share_300m","current_infected_sites")) {
        $y = @($panel | ForEach-Object { Get-Val $_ $outcome })
        $plausRows += [PSCustomObject]@{ variable=$v; outcome=$outcome; lag="same_year"; pearson=Fmt (Corr $x $y); spearman=Fmt (Spearman $x $y); note="association only; not a treatment effect" }
    }
}

$counterRows = @()
$areaCut5 = Quantile (@($panel | ForEach-Object { Get-Val $_ "pine_area_ha_applied" })) 0.05
foreach ($v in @("capacity_index_A_pooled","capacity_index_B_pooled","log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha")) {
    foreach ($r in (@($panel | Where-Object { Is-ValidNum (Get-Val $_ $v) } | Sort-Object @{Expression={-(Get-Val $_ $v)}} | Select-Object -First 20))) {
        $counterRows += [PSCustomObject]@{ variable=$v; year=$r.year; sido=$r.sido; sigungu_nm=$r.sigungu_nm; sigungu_cd=$r.sigungu_cd; value=Fmt (Get-Val $r $v); numerator=Fmt (Get-Val $r "included_local_budget"); denominator_pine_area=Fmt (Get-Val $r "pine_area_ha_applied"); budget_observed=$r.budget_observed; budget_missing_reason=$r.budget_missing_reason; data_stale=$r.forest_firm_data_stale_flag; diagnosis=if((Get-Val $r "pine_area_ha_applied") -lt $areaCut5){"small denominator effect possible"}else{"check numerator concentration or genuine high capacity"} }
    }
}

$sensRows = @()
foreach ($idx in @("capacity_index_A_pooled","capacity_index_A_yearly","capacity_index_B_pooled","capacity_index_B_yearly")) {
    foreach ($scenario in @("all","exclude_bottom_1pct_area","exclude_bottom_5pct_area")) {
        $areas = @($panel | ForEach-Object { Get-Val $_ "pine_area_ha_applied" })
        $cut = if($scenario -eq "exclude_bottom_1pct_area"){Quantile $areas 0.01}elseif($scenario -eq "exclude_bottom_5pct_area"){Quantile $areas 0.05}else{[double]::NegativeInfinity}
        $rows = @($panel | Where-Object { (Is-ValidNum (Get-Val $_ $idx)) -and (Get-Val $_ "pine_area_ha_applied") -gt $cut })
        $vals = @($rows | ForEach-Object { Get-Val $_ $idx })
        $sensRows += [PSCustomObject]@{ index=$idx; scenario=$scenario; n=$rows.Count; mean=Fmt (Mean $vals); std=Fmt (Std $vals); note=if($scenario -eq "all"){"baseline"}else{"small denominator excluded; source unchanged"} }
    }
}

$corrRows = @()
$corrVars = @("log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha","log_active_pest_firm_per_10000_pine_ha","log_movement_budget_per_pine_ha","surveillance_share","active_restriction_area_ratio")
foreach ($a in $corrVars) {
    foreach ($b in $corrVars) {
        if ($a -lt $b) {
            $av = @($panel | ForEach-Object { Get-Val $_ $a }); $bv = @($panel | ForEach-Object { Get-Val $_ $b })
            $corrRows += [PSCustomObject]@{ var1=$a; var2=$b; pearson=Fmt (Corr $av $bv); spearman=Fmt (Spearman $av $bv); note="screening correlation" }
        }
    }
}

$selectionRows = @(
    [PSCustomObject]@{ variable="log_resource_budget_per_pine_ha"; final_role="final_core_A_B"; decision="include"; reason="audited budget per pine area" },
    [PSCustomObject]@{ variable="log_surveillance_budget_per_pine_ha"; final_role="final_core_A_B"; decision="include"; reason="audited surveillance budget per pine area" },
    [PSCustomObject]@{ variable="log_active_pest_firm_per_10000_pine_ha"; final_role="extended_core_B"; decision=if($analysisMode -eq "BASIC ONLY"){"exclude"}else{"include_when_extended_eligible"}; reason="firm data gated by completeness" },
    [PSCustomObject]@{ variable="log_movement_budget_per_pine_ha"; final_role="support"; decision="support_only"; reason="sparse and zero-heavy" },
    [PSCustomObject]@{ variable="surveillance_share"; final_role="support"; decision="support_only"; reason="composition, not scale" },
    [PSCustomObject]@{ variable="movement_share_included_budget"; final_role="support"; decision="support_only"; reason="movement-control composition" },
    [PSCustomObject]@{ variable="restriction_designated"; final_role="support"; decision="support_only"; reason="regulatory status" },
    [PSCustomObject]@{ variable="active_restriction_area_ratio"; final_role="support"; decision="support_only"; reason="can exceed one by construction" }
)

$prefix = "CH2_local_capacity"
Write-Utf8Csv $edaRows (Join-Path $Out "$prefix`_EDA_summary.csv")
Write-Utf8Csv $trendRows (Join-Path $Out "$prefix`_yearly_trend.csv")
Write-Utf8Csv $sidoRows (Join-Path $Out "$prefix`_sido_mean.csv")
Write-Utf8Csv $rankRows (Join-Path $Out "$prefix`_rankings.csv")
Write-Utf8Csv $transitionRows (Join-Path $Out "$prefix`_2019_2020_transition.csv")
Write-Utf8Csv $plausRows (Join-Path $Out "$prefix`_empirical_plausibility.csv")
Write-Utf8Csv $counterRows (Join-Path $Out "$prefix`_counterintuitive_diagnosis.csv")
Write-Utf8Csv $sensRows (Join-Path $Out "$prefix`_sensitivity.csv")
Write-Utf8Csv $corrRows (Join-Path $Out "$prefix`_correlation_diagnosis.csv")
Write-Utf8Csv $selectionRows (Join-Path $Out "$prefix`_final_variable_selection.csv")
Write-Utf8Csv $panel (Join-Path $Out "$prefix`_final_panel.csv")

$log = @(
    "CH2 local capacity EDA/index generation",
    "audit_verdict=$auditVerdict",
    "analysis_mode=$analysisMode",
    "input_panel=$PanelPath",
    "rows=$($panel.Count)",
    "outputs=11 csv + 1 log",
    "No source values were overwritten.",
    "B indices are blank outside extended_index_eligible==1."
)
Set-Content -LiteralPath (Join-Path $Out "$prefix`_validation_log.txt") -Value ($log -join [Environment]::NewLine) -Encoding UTF8

[PSCustomObject]@{ audit_verdict=$auditVerdict; analysis_mode=$analysisMode; rows=$panel.Count; outputs=12; output_dir=$Out } | ConvertTo-Json -Compress
