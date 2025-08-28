param(
  [string]$Branch = "main",
  [string]$CsvRelPath = "Donnee\1_raw\AMV_GDT_P3M.csv",
  [int]$MaxRetries = 5,
  [int]$SleepSeconds = 3
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$Csv  = Join-Path $Repo $CsvRelPath
$Log  = Join-Path $Repo "push.log"

function Log($msg) {
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  Add-Content -Path $Log -Value ("[{0}] {1}" -f $ts, $msg)
  Write-Host $msg
}

try {
  if (!(Test-Path $Csv)) { Log ("CSV not found: {0}" -f $Csv); exit 1 }

  Log "== Start auto push =="
  Log ("Repo: {0}" -f $Repo)
  Log ("Branch: {0}" -f $Branch)
  Log ("CSV: {0}" -f $CsvRelPath)

  git -C $Repo fetch --all | Out-Null
  git -C $Repo checkout $Branch | Out-Null
  git -C $Repo pull --rebase | Out-Null

  for ($i=0; $i -lt $MaxRetries; $i++) {
    try {
      $fs = [System.IO.File]::Open($Csv, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
      $fs.Close()
      break
    } catch {
      if ($i -eq $MaxRetries-1) { Log "File locked, abort."; exit 2 }
      Start-Sleep -Seconds $SleepSeconds
    }
  }

  git -C $Repo add -- "$CsvRelPath"

  & git -C $Repo diff --cached --quiet
  $changed = $LASTEXITCODE -ne 0

  if ($changed) {
    $msg = "auto: update AMV_GDT_P3M.csv " + (Get-Date -Format "yyyy-MM-dd HH:mm")
    git -C $Repo commit -m "$msg" | Out-Null
    git -C $Repo push | Out-Null
    Log "Commit and push done."
  } else {
    Log "No change (no commit)."
  }

  Log "== End =="
  exit 0
}
catch {
  Log ("Error: {0}" -f $_.Exception.Message)
  exit 9
}
