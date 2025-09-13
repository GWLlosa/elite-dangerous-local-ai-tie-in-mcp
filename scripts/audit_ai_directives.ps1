<#
Audit AI Directives vs. Codebase
- Safe, read-only checks (no writes, no network)
- Outputs ASCII-only with clear [INFO]/[WARNING] markers
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Section {
    param([Parameter(Mandatory)][string]$Title)
    $line = ('=' * 78)
    Write-Output $line
    Write-Output "[INFO] $Title"
    Write-Output $line
}

function Count-Matches {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Pattern
    )
    if (-not (Test-Path $Path)) { return 0 }
    $total = 0
    Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        $c = (Select-String -Path $_.FullName -Pattern $Pattern -AllMatches -ErrorAction SilentlyContinue | Measure-Object).Count
        $total += $c
    }
    return $total
}

function Count-File-Matches {
    param(
        [Parameter(Mandatory)][string]$File,
        [Parameter(Mandatory)][string]$Pattern
    )
    if (-not (Test-Path $File)) { return 0 }
    return (Select-String -Path $File -Pattern $Pattern -AllMatches -ErrorAction SilentlyContinue | Measure-Object).Count
}

function List-File-Matches {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Pattern
    )
    if (-not (Test-Path $Path)) { return @() }
    return Select-String -Path $Path -Pattern $Pattern -AllMatches -Context 0,0 -ErrorAction SilentlyContinue
}

function Get-NonAsciiSummary {
    param([Parameter(Mandatory)][string]$File)
    if (-not (Test-Path $File)) { return @{ HasNonAscii = $false; Count = 0; Samples = @() } }
    $text = Get-Content -Raw -Path $File -ErrorAction SilentlyContinue
    if ($null -eq $text) { return @{ HasNonAscii = $false; Count = 0; Samples = @() } }
    $chars = $text.ToCharArray()
    $nonAscii = @()
    foreach ($ch in $chars) {
        $code = [int][char]$ch
        if ($code -gt 127) { $nonAscii += $code }
    }
    $samples = $nonAscii | Select-Object -Unique | Select-Object -First 10 | ForEach-Object { 'U+' + ($_.ToString('X4')) }
    return @{ HasNonAscii = ($nonAscii.Count -gt 0); Count = $nonAscii.Count; Samples = $samples }
}

Write-Section "Repo Overview"
Get-ChildItem -Force | Select-Object Mode, Name, Length | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output

Write-Section "AI Directives Files"
Get-ChildItem -Force ai-directives | Select-Object Mode, Name, Length | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output
Get-ChildItem -Force ai-directives/session-reports | Select-Object Mode, Name, Length | Format-Table -AutoSize | Out-String -Width 4096 | Write-Output

Write-Section "AI Directives README Claims Snapshot"
$aidReadme = 'ai-directives/README.md'
if (Test-Path $aidReadme) {
    $lines = Get-Content -Path $aidReadme -First 120
    $lines | ForEach-Object { $_ } | Out-String -Width 4096 | Write-Output
} else {
    Write-Output "[WARNING] Missing ai-directives/README.md"
}

Write-Section "AI Directives README ASCII Check"
$ascii = Get-NonAsciiSummary -File $aidReadme
Write-Output ("[INFO] Non-ASCII character count: {0}" -f $ascii.Count)
if ($ascii.HasNonAscii) {
    Write-Output ("[WARNING] Non-ASCII detected. Samples: {0}" -f ($ascii.Samples -join ', '))
    # Also check for replacement character U+FFFD explicitly
    $fffdChar = [string]([char]0xFFFD)
    $fffdPattern = [regex]::Escape($fffdChar)
    $fffd = Count-File-Matches -File $aidReadme -Pattern $fffdPattern
    Write-Output ("[INFO] U+FFFD replacement occurrences: {0}" -f $fffd)
}

Write-Section "Claims Extracted From README"
if (Test-Path $aidReadme) {
    $claims = @{
        ProductionReady = (Select-String -Path $aidReadme -Pattern "Status\s*:\s*Production Ready" -Quiet)
        TestsClaim      = (Select-String -Path $aidReadme -Pattern "Tests\s*:\s*([0-9\+]+)" -AllMatches)
        CoverageClaim   = (Select-String -Path $aidReadme -Pattern "Coverage\s*:\s*([0-9]{2,3})%\+?" -AllMatches)
        ToolsClaim      = (Select-String -Path $aidReadme -Pattern "Core MCP Tools\s*-\s*([0-9\+]+)" -AllMatches)
        ResourcesClaim  = (Select-String -Path $aidReadme -Pattern "MCP Resources\s*-\s*([0-9\+]+)" -AllMatches)
        PromptsClaim    = (Select-String -Path $aidReadme -Pattern "MCP Prompts\s*-\s*([0-9\+]+)" -AllMatches)
        EventsClaim     = (Select-String -Path $aidReadme -Pattern "Event Processing\s*-\s*([0-9\+]+)" -AllMatches)
    }
    Write-Output ("[INFO] Production Ready: {0}" -f $claims.ProductionReady)
    $testsCount = if ($claims.TestsClaim) { $claims.TestsClaim.Matches.Count } else { 0 }
    $covCount   = if ($claims.CoverageClaim) { $claims.CoverageClaim.Matches.Count } else { 0 }
    $toolsCount = if ($claims.ToolsClaim) { $claims.ToolsClaim.Matches.Count } else { 0 }
    $resCount   = if ($claims.ResourcesClaim) { $claims.ResourcesClaim.Matches.Count } else { 0 }
    $promCount  = if ($claims.PromptsClaim) { $claims.PromptsClaim.Matches.Count } else { 0 }
    $evtCount   = if ($claims.EventsClaim) { $claims.EventsClaim.Matches.Count } else { 0 }
    Write-Output ("[INFO] Tests claim lines: {0}" -f $testsCount)
    Write-Output ("[INFO] Coverage claim lines: {0}" -f $covCount)
    Write-Output ("[INFO] Tools claim lines: {0}" -f $toolsCount)
    Write-Output ("[INFO] Resources claim lines: {0}" -f $resCount)
    Write-Output ("[INFO] Prompts claim lines: {0}" -f $promCount)
    Write-Output ("[INFO] Event processing claim lines: {0}" -f $evtCount)
}

Write-Section "Code Reality: Test Counts"
$testFuncCount = Count-Matches -Path 'tests' -Pattern "^\s*def\s+test_"
$testFiles = Get-ChildItem -Path tests -Recurse -Filter *.py -File -ErrorAction SilentlyContinue | Measure-Object
Write-Output ("[INFO] Test files: {0}" -f $testFiles.Count)
Write-Output ("[INFO] Test functions (def test_): {0}" -f $testFuncCount)

Write-Section "Code Reality: MCP Endpoints (@app.tool)"
$toolCountAll = Count-Matches -Path 'src/mcp' -Pattern "@app\.tool\("
$toolCountTools = Count-File-Matches -File 'src/mcp/mcp_tools.py' -Pattern "@app\.tool\("
$toolCountResources = Count-File-Matches -File 'src/mcp/mcp_resources.py' -Pattern "@app\.tool\("
$toolCountPrompts = Count-File-Matches -File 'src/mcp/mcp_prompts.py' -Pattern "@app\.tool\("
Write-Output ("[INFO] Total @app.tool handlers: {0}" -f $toolCountAll)
Write-Output ("[INFO] Tools file handlers: {0}" -f $toolCountTools)
Write-Output ("[INFO] Resources file handlers: {0}" -f $toolCountResources)
Write-Output ("[INFO] Prompts file handlers: {0}" -f $toolCountPrompts)

Write-Section "FastMCP Invalid Usage Checks"
$badDecorResource = Count-Matches -Path 'src' -Pattern "@app\.resource\("
$badDecorPrompt = Count-Matches -Path 'src' -Pattern "@app\.prompt\("
$badToolsAttr = Count-Matches -Path 'src' -Pattern "server\.app\.tools"
Write-Output ("[INFO] @app.resource decorator occurrences: {0}" -f $badDecorResource)
Write-Output ("[INFO] @app.prompt decorator occurrences: {0}" -f $badDecorPrompt)
Write-Output ("[INFO] server.app.tools attribute occurrences: {0}" -f $badToolsAttr)

Write-Section "DataStore API Checks"
$dsFile = 'src/utils/data_store.py'
$hasRecent = (Select-String -Path $dsFile -Pattern "def\s+get_recent_events\(" -Quiet)
$hasByType = (Select-String -Path $dsFile -Pattern "def\s+get_events_by_type\(" -Quiet)
$hasByCat  = (Select-String -Path $dsFile -Pattern "def\s+get_events_by_category\(" -Quiet)
Write-Output ("[INFO] DataStore.get_recent_events: {0}" -f $hasRecent)
Write-Output ("[INFO] DataStore.get_events_by_type: {0}" -f $hasByType)
Write-Output ("[INFO] DataStore.get_events_by_category: {0}" -f $hasByCat)
$badGetAll = Count-Matches -Path 'src' -Pattern "get_all_events\("
Write-Output ("[INFO] get_all_events() usage in code: {0}" -f $badGetAll)

Write-Section "ProcessedEvent Usage Checks"
$peInitInCode = Count-Matches -Path 'src' -Pattern "ProcessedEvent\("
$peInitInTests = Count-Matches -Path 'tests' -Pattern "ProcessedEvent\("
Write-Output ("[INFO] ProcessedEvent constructor calls in src: {0}" -f $peInitInCode)
Write-Output ("[INFO] ProcessedEvent constructor calls in tests: {0}" -f $peInitInTests)
$peDataKw = Count-Matches -Path 'src' -Pattern "ProcessedEvent\([^\)]*data\s*="
$peRawKw  = Count-Matches -Path 'src' -Pattern "ProcessedEvent\([^\)]*raw_event\s*="
Write-Output ("[INFO] Calls using data= kw in src: {0}" -f $peDataKw)
Write-Output ("[INFO] Calls using raw_event= kw in src: {0}" -f $peRawKw)

Write-Section "Timezone Safety Checks"
$utcnow = Count-Matches -Path 'src' -Pattern "datetime\.utcnow\("
$dtNowBare = Count-Matches -Path 'src' -Pattern "datetime\.now\(\)"
$tzAwareNow = Count-Matches -Path 'src' -Pattern "datetime\.now\(\s*timezone\.utc\s*\)"
Write-Output ("[INFO] datetime.utcnow() occurrences: {0}" -f $utcnow)
Write-Output ("[INFO] datetime.now() bare occurrences: {0}" -f $dtNowBare)
Write-Output ("[INFO] datetime.now(timezone.utc) occurrences: {0}" -f $tzAwareNow)

Write-Section "Event Categories Declared"
$eventsFile = 'src/journal/events.py'
if (Test-Path $eventsFile) {
    $inEnum = $false
    $countEnum = 0
    foreach ($line in Get-Content -Path $eventsFile) {
        if ($line -match '^class\s+EventCategory') { $inEnum = $true; continue }
        if ($inEnum -and $line -match '^class\s+') { break }
        if ($inEnum -and $line -match '^[ \t]*[A-Z0-9_]+\s*=') { $countEnum++ }
    }
    Write-Output ("[INFO] EventCategory members: {0}" -f $countEnum)
    $mapCount = Count-File-Matches -File $eventsFile -Pattern 'EVENT_CATEGORIES\s*=\s*\{'
    Write-Output ("[INFO] EVENT_CATEGORIES mapping blocks: {0}" -f $mapCount)
    $mappedEvents = Count-File-Matches -File $eventsFile -Pattern '\"[A-Za-z0-9_]+\"\\s*:\\s*EventCategory\.[A-Za-z_]+'
    Write-Output ("[INFO] EVENT_CATEGORIES mapped entries (rough count): {0}" -f $mappedEvents)
} else {
    Write-Output "[WARNING] Missing src/journal/events.py"
}

Write-Section "Summary"
Write-Output "[INFO] Audit complete. Review warnings above for inconsistencies."
