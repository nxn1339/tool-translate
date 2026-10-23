param(
  [Parameter(Mandatory = $true)]
  [string]$AppRepo,

  [Parameter(Mandatory = $true)]
  [string]$DocsRepo,

  [Parameter(Mandatory = $true)]
  [int[]]$PrNumbers,

  [string]$Base = "develop",

  [string]$TaskFile = "docs/01.management/04.task/dev_task_list.md",

  [string[]]$TaskPatterns = @("DEV-", "CAND-DEV-", "TASK-", "DoD", "Foundation")
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
  param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string[]]$Args,
    [switch]$AllowFail
  )

  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    $output = & git -C $Repo @Args 2>&1
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
  }
  if ($exitCode -ne 0 -and -not $AllowFail) {
    throw "git -C $Repo $($Args -join ' ') failed: $output"
  }
  [pscustomobject]@{
    ExitCode = $exitCode
    Output = ($output -join [Environment]::NewLine)
  }
}

function Write-Section {
  param([string]$Title)
  Write-Output ""
  Write-Output "## $Title"
}

$appRoot = [System.IO.Path]::GetFullPath($AppRepo)
$docsRoot = [System.IO.Path]::GetFullPath($DocsRepo)
$taskPath = Join-Path $docsRoot $TaskFile

if (-not (Test-Path -LiteralPath $appRoot)) { throw "AppRepo not found: $appRoot" }
if (-not (Test-Path -LiteralPath $docsRoot)) { throw "DocsRepo not found: $docsRoot" }
if (-not (Test-Path -LiteralPath $taskPath)) { throw "Task file not found: $taskPath" }

Write-Section "Repositories"
Write-Output "AppRepo: $appRoot"
Write-Output "DocsRepo: $docsRoot"
Write-Output "Base: $Base"
Write-Output "App remote:"
(Invoke-Git -Repo $appRoot -Args @("remote", "-v")).Output

Write-Section "Fetch"
Invoke-Git -Repo $appRoot -Args @("fetch", "--prune") | Out-Null
foreach ($pr in $PrNumbers) {
  $ref = "refs/pull/$pr/head:refs/remotes/origin/pr/$pr"
  $result = Invoke-Git -Repo $appRoot -Args @("fetch", "origin", $ref) -AllowFail
  if ($result.ExitCode -eq 0) {
    Write-Output "PR #$pr fetched to origin/pr/$pr"
  } else {
    Write-Output "PR #$pr fetch failed: $($result.Output)"
  }
}

Write-Section "Task Lines"
$taskLines = Get-Content -LiteralPath $taskPath -Encoding UTF8
for ($i = 0; $i -lt $taskLines.Count; $i++) {
  $line = $taskLines[$i]
  foreach ($pattern in $TaskPatterns) {
    if ($line -like "*$pattern*") {
      "{0}: {1}" -f ($i + 1), $line
      break
    }
  }
}

foreach ($pr in $PrNumbers) {
  $prRef = "origin/pr/$pr"
  Write-Section "PR #$pr Summary"
  $rev = Invoke-Git -Repo $appRoot -Args @("rev-parse", "--verify", $prRef) -AllowFail
  if ($rev.ExitCode -ne 0) {
    Write-Output "Missing ref: $prRef"
    continue
  }

  Write-Output "Head: $($rev.Output.Trim())"
  Write-Output "Commits:"
  (Invoke-Git -Repo $appRoot -Args @("log", "--oneline", "origin/$Base..$prRef") -AllowFail).Output

  Write-Output ""
  Write-Output "Changed files:"
  (Invoke-Git -Repo $appRoot -Args @("diff", "--name-status", "origin/$Base...$prRef") -AllowFail).Output

  Write-Output ""
  Write-Output "Diff stat:"
  (Invoke-Git -Repo $appRoot -Args @("diff", "--stat", "origin/$Base...$prRef") -AllowFail).Output

  Write-Output ""
  Write-Output "Diff check:"
  $diffCheck = Invoke-Git -Repo $appRoot -Args @("diff", "--check", "origin/$Base...$prRef") -AllowFail
  if ([string]::IsNullOrWhiteSpace($diffCheck.Output)) {
    Write-Output "clean"
  } else {
    $diffCheck.Output
  }

  Write-Output ""
  Write-Output "Likely verification commands:"
  $changed = (Invoke-Git -Repo $appRoot -Args @("diff", "--name-only", "origin/$Base...$prRef") -AllowFail).Output
  if ($changed -match "apps/api|packages/shared|deploy|package\.json|package-lock\.json") {
    Write-Output "- npm ci"
    Write-Output "- npm run build"
    Write-Output "- npm test"
    Write-Output "- npm run lint"
    Write-Output "- docker compose -f deploy/docker-compose.yml --env-file deploy/env/.env.example config"
  }
  if ($changed -match "apps/mobile") {
    Write-Output "- cd apps/mobile"
    Write-Output "- flutter --version"
    Write-Output "- flutter pub get"
    Write-Output "- flutter test"
    Write-Output "- Verify CI has a mobile job or record local-only gap"
  }
}
