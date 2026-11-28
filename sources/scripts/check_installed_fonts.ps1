# Lists every installed and_Lubrifont / WD-XL Lubrifont font on this Windows
# PC with the names applications use to find a font, and flags the usual
# causes of "font missing, pick a replacement" when a document moves between
# PCs: an old version, .ttf and .otf both installed, the same font installed
# for all users and for one user, or the CJK edition instead of the
# Latin / Cyrillic / Greek one.
#
# Run it on each PC and compare the two reports: documents open without a
# prompt only when the Family, Style and PostScript names match.
#
# usage (in PowerShell, from the folder with this file):
#   powershell -ExecutionPolicy Bypass -File check_installed_fonts.ps1
#
# The report is also saved to the Desktop as and_Lubrifont-<PC name>.txt.
# Reads only; changes nothing.

$ErrorActionPreference = 'Stop'

function Read-U16([byte[]]$b, [int]$o) {
    return ([int]$b[$o] -shl 8) -bor [int]$b[$o + 1]
}

function Read-U32([byte[]]$b, [int]$o) {
    return [int]([int64]$b[$o] * 16777216 + [int64]$b[$o + 1] * 65536 +
                 [int64]$b[$o + 2] * 256 + [int64]$b[$o + 3])
}

# Windows English names (platform 3, encoding 1, language 0x409) of each
# font in a .ttf, .otf or .ttc file.
function Get-FontNames([string]$path) {
    $b = [IO.File]::ReadAllBytes($path)
    $offsets = @(0)
    if ([Text.Encoding]::ASCII.GetString($b, 0, 4) -eq 'ttcf') {
        $n = Read-U32 $b 8
        $offsets = @(for ($i = 0; $i -lt $n; $i++) { Read-U32 $b (12 + 4 * $i) })
    }
    foreach ($off in $offsets) {
        $numTables = Read-U16 $b ($off + 4)
        $nameOff = -1
        for ($i = 0; $i -lt $numTables; $i++) {
            $rec = $off + 12 + 16 * $i
            if ([Text.Encoding]::ASCII.GetString($b, $rec, 4) -eq 'name') {
                $nameOff = Read-U32 $b ($rec + 8)
            }
        }
        if ($nameOff -lt 0) { continue }
        $count = Read-U16 $b ($nameOff + 2)
        $strOff = $nameOff + (Read-U16 $b ($nameOff + 4))
        $names = @{}
        for ($i = 0; $i -lt $count; $i++) {
            $rec = $nameOff + 6 + 12 * $i
            if ((Read-U16 $b $rec) -eq 3 -and (Read-U16 $b ($rec + 2)) -eq 1 -and
                (Read-U16 $b ($rec + 4)) -eq 0x409) {
                $id = Read-U16 $b ($rec + 6)
                $len = Read-U16 $b ($rec + 8)
                $pos = $strOff + (Read-U16 $b ($rec + 10))
                $names[$id] = [Text.Encoding]::BigEndianUnicode.GetString($b, $pos, $len)
            }
        }
        $version = ''
        if ($names[5] -match '\d+\.\d+') { $version = $Matches[0] }
        [pscustomobject]@{
            Family     = $names[1]
            Style      = $names[2]
            PostScript = $names[6]
            Version    = $version
        }
    }
}

$locations = @(
    @{ Scope = 'All users'
       Key   = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
       Dir   = Join-Path $env:WINDIR 'Fonts' },
    @{ Scope = 'This user'
       Key   = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
       Dir   = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts' }
)
$skip = 'PSPath', 'PSParentPath', 'PSChildName', 'PSDrive', 'PSProvider'

$rows = @()
$seen = @{}
foreach ($loc in $locations) {
    $files = @()
    if (Test-Path $loc.Key) {
        foreach ($p in (Get-ItemProperty $loc.Key).PSObject.Properties) {
            if ($skip -contains $p.Name) { continue }
            $value = [string]$p.Value
            if ($p.Name -match 'ubrifont' -or $value -match 'ubrifont') {
                if ([IO.Path]::IsPathRooted($value)) { $files += $value }
                else { $files += Join-Path $loc.Dir $value }
            }
        }
    }
    if (Test-Path $loc.Dir) {
        $files += Get-ChildItem $loc.Dir -File -Filter '*ubrifont*' |
                  ForEach-Object { $_.FullName }
    }
    foreach ($f in $files) {
        if ($seen.ContainsKey($f.ToLower())) { continue }
        $seen[$f.ToLower()] = $true
        if (-not (Test-Path $f)) {
            $rows += [pscustomobject]@{ Scope = $loc.Scope; File = $f; Family = '(registered, file missing)';
                                       Style = ''; PostScript = ''; Version = '' }
            continue
        }
        try {
            foreach ($n in (Get-FontNames $f)) {
                $rows += [pscustomobject]@{ Scope = $loc.Scope; File = (Split-Path $f -Leaf);
                                           Family = $n.Family; Style = $n.Style;
                                           PostScript = $n.PostScript; Version = $n.Version }
            }
        } catch {
            $rows += [pscustomobject]@{ Scope = $loc.Scope; File = (Split-Path $f -Leaf);
                                       Family = "(could not read: $($_.Exception.Message))";
                                       Style = ''; PostScript = ''; Version = '' }
        }
    }
}

$report = @()
$report += "and_Lubrifont fonts installed on $env:COMPUTERNAME ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
$report += ''
if ($rows.Count -eq 0) {
    $report += 'No and_Lubrifont or WD-XL Lubrifont fonts are installed.'
} else {
    $report += ($rows | Sort-Object Family, Style, Scope, File |
                Format-Table Scope, File, Family, Style, PostScript, Version -AutoSize |
                Out-String -Width 300).TrimEnd()
    $report += ''
    $problems = @()

    $old = $rows | Where-Object { $_.Family -like 'WD-XL*' -or $_.PostScript -like 'and_Lubrifont*' -or
                                  $_.PostScript -like 'WD-XL*' }
    if ($old) {
        $problems += '- Old version installed (WD-XL Lubrifont, or and_Lubrifont 2.401 whose PostScript name has an underscore):'
        $problems += $old | ForEach-Object { "    $($_.File)  ($($_.Scope))" }
    }

    $versions = @($rows | Where-Object { $_.Version } | ForEach-Object { $_.Version } | Sort-Object -Unique)
    if ($versions.Count -gt 1) {
        $problems += "- More than one version installed: $($versions -join ', '). Keep only the newest."
    }

    $dupes = $rows | Where-Object { $_.PostScript } | Group-Object PostScript | Where-Object { $_.Count -gt 1 }
    foreach ($d in $dupes) {
        $problems += "- $($d.Name) is installed $($d.Count) times (.ttf and .otf, or for all users and for this user):"
        $problems += $d.Group | ForEach-Object { "    $($_.File)  ($($_.Scope))" }
    }

    $families = @($rows | ForEach-Object { $_.Family } | Sort-Object -Unique)
    if ($families -notcontains 'and_Lubrifont') {
        $problems += '- The main family "and_Lubrifont" (andLubrifont-Regular.ttf) is not installed.'
    }
    if ($families | Where-Object { $_ -match '^and_Lubrifont (SC|TC|JP)' }) {
        $problems += '- The CJK edition (and_Lubrifont SC / TC / JP) is installed. It is a different family:'
        $problems += '  a document set in "and_Lubrifont SC" will not find "and_Lubrifont" on the other PC, and the reverse.'
    }

    if ($problems.Count -eq 0) {
        $report += 'No problems found. Compare this report with the one from the other PC.'
    } else {
        $report += 'Problems:'
        $report += $problems
    }
}

$report | ForEach-Object { Write-Output $_ }
$out = Join-Path ([Environment]::GetFolderPath('Desktop')) "and_Lubrifont-$env:COMPUTERNAME.txt"
$report | Out-File -FilePath $out -Encoding UTF8
Write-Output ''
Write-Output "Saved to $out"
