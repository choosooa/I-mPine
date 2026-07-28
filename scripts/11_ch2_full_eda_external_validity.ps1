$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$OutDir = Join-Path $Root "EDA\CH2"

$PanelPath = $null
foreach ($f in (Get-ChildItem -LiteralPath (Join-Path $Root "data\CH2") -Recurse -File -Filter "CH2_local_capacity_final_panel.csv")) {
    $PanelPath = $f.FullName
    break
}
if ($null -eq $PanelPath) { throw "CH2_local_capacity_final_panel.csv not found." }

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
function SumNums($xs) {
    $a = @($xs | Where-Object { Is-ValidNum $_ })
    if ($a.Count -eq 0) { return [double]::NaN }
    return (($a | Measure-Object -Sum).Sum)
}
function Std($xs) {
    $a = @($xs | Where-Object { Is-ValidNum $_ })
    if ($a.Count -le 1) { return [double]::NaN }
    $m = Mean $a
    $ss = 0.0
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
function Skew($xs) {
    $a = @($xs | Where-Object { Is-ValidNum $_ })
    if ($a.Count -le 2) { return [double]::NaN }
    $m = Mean $a; $s = Std $a
    if (-not (Is-ValidNum $s) -or [math]::Abs($s) -lt 1e-12) { return 0.0 }
    $acc = 0.0
    foreach ($x in $a) { $acc += [math]::Pow(($x - $m) / $s, 3) }
    return $acc / $a.Count
}
function Corr($x, $y) {
    $n=0; $sx=0.0; $sy=0.0
    for ($i=0; $i -lt $x.Count; $i++) {
        $xi = [double]$x[$i]; $yi = [double]$y[$i]
        if ((Is-ValidNum $xi) -and (Is-ValidNum $yi)) { $n++; $sx += $xi; $sy += $yi }
    }
    if ($n -le 2) { return [double]::NaN }
    $mx = $sx / $n; $my = $sy / $n
    $num=0.0; $dx=0.0; $dy=0.0
    for ($i=0; $i -lt $x.Count; $i++) {
        $xi = [double]$x[$i]; $yi = [double]$y[$i]
        if ((Is-ValidNum $xi) -and (Is-ValidNum $yi)) {
            $vx=$xi-$mx; $vy=$yi-$my
            $num += $vx*$vy; $dx += $vx*$vx; $dy += $vy*$vy
        }
    }
    if ($dx -eq 0 -or $dy -eq 0) { return [double]::NaN }
    return $num / [math]::Sqrt($dx*$dy)
}
function Fmt($x) {
    if (-not (Is-ValidNum $x)) { return "" }
    return ([math]::Round([double]$x, 10)).ToString([Globalization.CultureInfo]::InvariantCulture)
}
function GetVal($r, $c) {
    if ($r.PSObject.Properties.Name -contains $c) { return To-Num $r.$c }
    return [double]::NaN
}
function RoleOf($v) {
    if ($v -in @("year","sigungu_cd","sigungu_nm","sido","sigungu_full_nm")) { return "id" }
    if ($v -like "*local_budget" -or $v -in @("included_local_budget","direct_local_budget","broad_local_budget")) { return "budget_raw" }
    if ($v -like "*per_pine_ha" -and $v -notlike "log_*") { return "area_standardized" }
    if ($v -like "log_*") { return "log_transform" }
    if ($v -like "*share*") { return "budget_share" }
    if ($v -in @("budget_observed","budget_missing_reason","pine_area_observed","pine_area_positive","pine_area_matched","analysis_unit_matched","index_eligible","budget_index_eligible","extended_index_eligible","forest_firm_data_observed","forest_firm_data_complete_for_year","forest_firm_data_stale_flag","forest_firm_region_matched","restriction_history_complete_flag","restriction_date_quality_flag","restriction_region_matched")) { return "quality_flag" }
    if ($v -like "*infected*" -or $v -like "*recurrence*" -or $v -like "*new_site*") { return "outcome" }
    if ($v -like "*pest_firm*" -or $v -like "*forest_firm*") { return "firm_infra" }
    if ($v -like "*restriction*") { return "restriction" }
    if ($v -like "*pine_area*") { return "pine_area" }
    if ($v -like "capacity_index*") { return "index" }
    return "other"
}

$panel = @(Import-Csv -LiteralPath $PanelPath)
$cols = $panel[0].PSObject.Properties.Name
$rowsCount = $panel.Count
$years = @($panel | ForEach-Object { [int]$_.year } | Sort-Object -Unique)

$structure = @(
    [PSCustomObject]@{ item="rows"; value=$rowsCount },
    [PSCustomObject]@{ item="columns"; value=$cols.Count },
    [PSCustomObject]@{ item="year_min"; value=($years | Select-Object -First 1) },
    [PSCustomObject]@{ item="year_max"; value=($years | Select-Object -Last 1) },
    [PSCustomObject]@{ item="unique_sigungu_cd"; value=(@($panel | ForEach-Object { $_.sigungu_cd } | Sort-Object -Unique)).Count },
    [PSCustomObject]@{ item="year_sigungu_duplicate_rows"; value=(@($panel | Group-Object year,sigungu_cd | Where-Object { $_.Count -gt 1 })).Count },
    [PSCustomObject]@{ item="balanced_panel_expected_rows"; value=($years.Count * (@($panel | ForEach-Object { $_.sigungu_cd } | Sort-Object -Unique)).Count) },
    [PSCustomObject]@{ item="balanced_panel"; value=($rowsCount -eq ($years.Count * (@($panel | ForEach-Object { $_.sigungu_cd } | Sort-Object -Unique)).Count)) }
)

$yearCounts = foreach ($g in ($panel | Group-Object year | Sort-Object Name)) {
    [PSCustomObject]@{ year=$g.Name; rows=$g.Count; unique_sigungu_cd=(@($g.Group | ForEach-Object { $_.sigungu_cd } | Sort-Object -Unique)).Count }
}

$summary = @()
foreach ($c in $cols) {
    $valsRaw = @($panel | ForEach-Object { $_.$c })
    $vals = @($panel | ForEach-Object { GetVal $_ $c })
    $valid = @($vals | Where-Object { Is-ValidNum $_ })
    $missing = @($valsRaw | Where-Object { [string]::IsNullOrWhiteSpace([string]$_) })
    $zeros = @($valid | Where-Object { [math]::Abs($_) -lt 1e-12 })
    $q1 = Quantile $valid 0.25; $q3 = Quantile $valid 0.75
    $isNumeric = $valid.Count -gt 0 -and $valid.Count -ge ($rowsCount - $missing.Count) * 0.8
    $summary += [PSCustomObject]@{
        variable=$c
        role=RoleOf $c
        inferred_type=if($isNumeric){"numeric"}else{"text_or_categorical"}
        n_total=$rowsCount
        n_obs=if($isNumeric){$valid.Count}else{($rowsCount-$missing.Count)}
        n_missing=$missing.Count
        missing_rate=Fmt ($missing.Count/[double]$rowsCount)
        mean=if($isNumeric){Fmt (Mean $valid)}else{""}
        std=if($isNumeric){Fmt (Std $valid)}else{""}
        min=if($isNumeric){Fmt (Quantile $valid 0)}else{""}
        q1=if($isNumeric){Fmt $q1}else{""}
        median=if($isNumeric){Fmt (Quantile $valid 0.5)}else{""}
        q3=if($isNumeric){Fmt $q3}else{""}
        max=if($isNumeric){Fmt (Quantile $valid 1)}else{""}
        skew=if($isNumeric){Fmt (Skew $valid)}else{""}
        zero_rate=if($isNumeric -and $valid.Count){Fmt ($zeros.Count/[double]$valid.Count)}else{""}
        unique_count=(@($valsRaw | Sort-Object -Unique)).Count
        eda_flag=if($isNumeric -and $valid.Count -gt 0 -and ((@($valsRaw | Sort-Object -Unique)).Count -le 1)){"constant"}elseif($isNumeric -and $valid.Count -gt 0 -and ($zeros.Count/[double]$valid.Count) -gt 0.7){"zero_heavy"}elseif($missing.Count/[double]$rowsCount -gt 0.3){"missing_heavy"}else{"ok_or_review"}
    }
}

$missingYear = @()
foreach ($c in $cols) {
    foreach ($g in ($panel | Group-Object year | Sort-Object Name)) {
        $miss = @($g.Group | Where-Object { [string]::IsNullOrWhiteSpace([string]($_.$c)) }).Count
        $missingYear += [PSCustomObject]@{ variable=$c; year=$g.Name; n=$g.Count; missing=$miss; missing_rate=Fmt ($miss/[double]$g.Count) }
    }
}

$missingSido = @()
foreach ($c in $cols) {
    foreach ($g in ($panel | Group-Object sido | Sort-Object Name)) {
        $miss = @($g.Group | Where-Object { [string]::IsNullOrWhiteSpace([string]($_.$c)) }).Count
        $missingSido += [PSCustomObject]@{ variable=$c; sido=$g.Name; n=$g.Count; missing=$miss; missing_rate=Fmt ($miss/[double]$g.Count) }
    }
}

$tol = 1e-6
$formulaFail = 0
$formulaMax = 0.0
foreach ($r in $panel) {
    $includedDiff = (GetVal $r "resource_local_budget") + (GetVal $r "surveillance_local_budget") + (GetVal $r "movement_local_budget") - (GetVal $r "included_local_budget")
    $ad = [math]::Abs($includedDiff)
    if ($ad -gt $tol) { $formulaFail++ }
    if ($ad -gt $formulaMax) { $formulaMax = $ad }
}
$formulaSummary = @([PSCustomObject]@{ check="resource_plus_surveillance_plus_movement_eq_included"; rows=$panel.Count; fail_count=$formulaFail; max_abs_diff=Fmt $formulaMax })

$scaleRows = @()
foreach ($b in @("resource","surveillance","movement")) {
    $raw = "${b}_local_budget"
    $perha = "${b}_budget_per_pine_ha"
    $logv = "log_${b}_budget_per_pine_ha"
    $xArea = @($panel | ForEach-Object { GetVal $_ "pine_area_ha_applied" })
    $xRaw = @($panel | ForEach-Object { GetVal $_ $raw })
    $xPer = @($panel | ForEach-Object { GetVal $_ $perha })
    $xLog = @($panel | ForEach-Object { GetVal $_ $logv })
    $scaleRows += [PSCustomObject]@{ variable_group=$b; raw_area_pearson=Fmt (Corr $xRaw $xArea); raw_area_spearman=Fmt (Corr $xRaw $xArea); raw_perha_pearson=Fmt (Corr $xRaw $xPer); perha_log_pearson=Fmt (Corr $xPer $xLog); raw_skew=Fmt (Skew $xRaw); perha_skew=Fmt (Skew $xPer); log_skew=Fmt (Skew $xLog) }
}

$corrVars = @(
    "resource_local_budget","surveillance_local_budget","movement_local_budget","included_local_budget",
    "resource_budget_per_pine_ha","surveillance_budget_per_pine_ha","movement_budget_per_pine_ha",
    "log_resource_budget_per_pine_ha","log_surveillance_budget_per_pine_ha","log_movement_budget_per_pine_ha",
    "surveillance_share","movement_share_broad_budget","movement_share_included_budget",
    "active_pest_firm_count","active_pest_firm_per_10000_pine_ha","log_active_pest_firm_per_10000_pine_ha",
    "restriction_designated","active_restriction_area_ratio",
    "prev_infected_sites","current_infected_sites","recurrent_sites_300m","recurrence_rate_300m","new_site_share_300m",
    "capacity_index_A_pooled","capacity_index_A_yearly","capacity_index_B_pooled","capacity_index_B_yearly"
)
$corrRows = @()
for ($i=0; $i -lt $corrVars.Count; $i++) {
    for ($j=$i+1; $j -lt $corrVars.Count; $j++) {
        $a=$corrVars[$i]; $b=$corrVars[$j]
        $av=@($panel | ForEach-Object { GetVal $_ $a }); $bv=@($panel | ForEach-Object { GetVal $_ $b })
        $corrRows += [PSCustomObject]@{ var1=$a; var2=$b; pearson=Fmt (Corr $av $bv); abs_pearson=Fmt ([math]::Abs((Corr $av $bv))) }
    }
}

$external = @()
foreach ($s in $summary) {
    $role = $s.role
    $verdict = "review"
    $rationale = ""
    if ($role -eq "id") { $verdict="not_a_measure"; $rationale="Identifier only." }
    elseif ($role -eq "budget_raw") { $verdict="valid_context_raw_not_core"; $rationale="Direct fiscal input, but affected by municipality and pine-area scale." }
    elseif ($role -eq "area_standardized") { $verdict="valid_but_denominator_sensitive"; $rationale="Improves scale comparability but can inflate small pine-area municipalities." }
    elseif ($role -eq "log_transform") { $verdict="valid_for_index_candidate"; $rationale="Reduces right skew of area-standardized budget or infrastructure measures." }
    elseif ($role -eq "budget_share") { $verdict="valid_for_budget_mix_not_capacity_scale"; $rationale="Captures allocation composition, not total capacity." }
    elseif ($role -eq "quality_flag") { $verdict="quality_control_only"; $rationale="Use for eligibility and interpretation, not as substantive capacity." }
    elseif ($role -eq "outcome") { $verdict="outcome_not_predictor"; $rationale="Represents occurrence/recurrence outcome, not local capacity." }
    elseif ($role -eq "firm_infra") { $verdict="extended_validity_with_temporal_caveat"; $rationale="Represents implementation infrastructure, but source freshness limits 2022-2023 use." }
    elseif ($role -eq "restriction") { $verdict="support_only_endogenous_policy_status"; $rationale="Restriction status can reflect both response and infection/risk targeting." }
    elseif ($role -eq "pine_area") { $verdict="denominator_or_context"; $rationale="Important exposure/context denominator, not response capacity." }
    elseif ($role -eq "index") { $verdict="final_or_robustness_index"; $rationale="Composite measure derived after EDA/eligibility gates." }
    $external += [PSCustomObject]@{ variable=$s.variable; role=$role; external_validity_verdict=$verdict; rationale=$rationale; eda_flag=$s.eda_flag; missing_rate=$s.missing_rate; zero_rate=$s.zero_rate }
}

$prefix = Join-Path $OutDir "jijache_full_eda"
$structure | Export-Csv -LiteralPath "$prefix`_structure.csv" -NoTypeInformation -Encoding UTF8
$yearCounts | Export-Csv -LiteralPath "$prefix`_year_counts.csv" -NoTypeInformation -Encoding UTF8
$summary | Export-Csv -LiteralPath "$prefix`_variable_summary.csv" -NoTypeInformation -Encoding UTF8
$missingYear | Export-Csv -LiteralPath "$prefix`_missing_by_year.csv" -NoTypeInformation -Encoding UTF8
$missingSido | Export-Csv -LiteralPath "$prefix`_missing_by_sido.csv" -NoTypeInformation -Encoding UTF8
$formulaSummary | Export-Csv -LiteralPath "$prefix`_formula_checks.csv" -NoTypeInformation -Encoding UTF8
$scaleRows | Export-Csv -LiteralPath "$prefix`_scale_log_checks.csv" -NoTypeInformation -Encoding UTF8
$corrRows | Sort-Object {[double]$_.abs_pearson} -Descending | Export-Csv -LiteralPath "$prefix`_correlations.csv" -NoTypeInformation -Encoding UTF8
$external | Export-Csv -LiteralPath "$prefix`_external_validity.csv" -NoTypeInformation -Encoding UTF8

[PSCustomObject]@{ rows=$rowsCount; columns=$cols.Count; outputs=9; prefix=$prefix } | ConvertTo-Json -Compress
