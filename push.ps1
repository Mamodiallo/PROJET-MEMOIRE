param(
  [string]$Branch = "main",                       # adapte si ta branche est 'master'
  [string]$CsvRelPath = "Donnee\1_raw\AMV_GDT_P3M.csv",
  [int]$MaxRetries = 5,
  [int]$SleepSeconds = 3
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Repo = dossier où se trouve ce script
$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$Csv  = Join-Path $Repo $CsvRelPath
$Log  = Join-Path $Repo "push.log"
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# petit logger
function Log($msg) { Add-Content -Path $Log -Value "[$stamp] $msg"; Write-Host $msg }

try {
  if (!(Test-Path $Csv)) { Log "CSV introuvable : $Csv"; exit 1 }

  Log "==== Début push auto ===="
  Log "Repo: $Repo"
  Log "Branche: $Branch"
  Log "CSV: $CsvRelPath"

  # S'assurer d'être à jour et sur la bonne branche
  git -C $Repo fetch --all | Out-Null
  git -C $Repo checkout $Branch | Out-Null
  git -C $Repo pull --rebase | Out-Null

  # Attendre si le fichier est verrouillé (Excel, etc.)
  for ($i=0; $i -lt $MaxRetries; $i++) {
    try {
      $fs = [System.IO.File]::Open($Csv,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        [System.IO.FileShare]::ReadWrite)
      $fs.Close()
      break
    } catch {
      if ($i -eq $MaxRetries-1) { Log "Fichier verrouillé, abandon."; exit 2 }
      Start-Sleep -Seconds $SleepSeconds
    }
  }

  # Mettre en scène uniquement le CSV
  git -C $Repo add -- "$CsvRelPath"

  # Y a-t-il quelque chose à committer ?
  & git -C $Repo diff --cached --quiet
  $changed = $LASTEXITCODE -ne 0

  if ($changed) {
    $msg = "auto: update AMV_GDT_P3M.csv $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git -C $Repo commit -m "$msg" | Out-Null
    git -C $Repo push | Out-Null
    Log "✅ Commit + push effectués."
  } else {
    Log "ℹ️  Aucun changement détecté (pas de commit)."
  }

  Log "==== Fin push auto ===="
  exit 0
}
catch {
  Log "❌ Erreur: $($_.Exception.Message)"
  exit 9
}
