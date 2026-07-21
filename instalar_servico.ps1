# =====================================================================
#  instalar_servico.ps1
#  Registra o sistema de Horas Extras como SERVICO do Windows (via NSSM):
#    - fica sempre ativo (sobe junto com o Windows, mesmo sem login)
#    - reinicia sozinho se o processo cair/travar
#
#  COMO USAR: clique com o botao direito no PowerShell > "Executar como
#  administrador", navegue ate a pasta do projeto e rode:
#      .\instalar_servico.ps1
# =====================================================================

$ErrorActionPreference = "Stop"

$Projeto = "A:\Projetos\horas_extras"
$Python  = "C:\Users\andre\AppData\Local\Programs\Python\Python311\python.exe"
$Servico = "HorasExtras"
$Nssm    = Join-Path $Projeto "tools\nssm.exe"

# 1) Exige privilegios de administrador --------------------------------
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($id)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Host "ERRO: rode este script como Administrador." -ForegroundColor Red
    exit 1
}

# 2) Baixa o NSSM se ainda nao existir ---------------------------------
if (-not (Test-Path $Nssm)) {
    Write-Host "Baixando NSSM..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Force (Split-Path $Nssm) | Out-Null
    $zip  = Join-Path $env:TEMP "nssm.zip"
    $dest = Join-Path $env:TEMP "nssm_extract"
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile $zip
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Expand-Archive $zip $dest
    Copy-Item (Join-Path $dest "nssm-2.24\win64\nssm.exe") $Nssm
    Write-Host "NSSM instalado em $Nssm" -ForegroundColor Green
}

# 3) Remove instalacao anterior do servico (para reconfigurar limpo) ---
if (Get-Service $Servico -ErrorAction SilentlyContinue) {
    Write-Host "Removendo servico anterior..." -ForegroundColor Yellow
    & $Nssm stop $Servico
    & $Nssm remove $Servico confirm
    Start-Sleep -Seconds 2
}

# 4) Cria e configura o servico ----------------------------------------
New-Item -ItemType Directory -Force (Join-Path $Projeto "logs") | Out-Null

& $Nssm install $Servico $Python "$Projeto\servidor.py"
& $Nssm set $Servico AppDirectory   $Projeto
& $Nssm set $Servico DisplayName    "Horas Extras - Servidor Web"
& $Nssm set $Servico Description     "Sistema de Horas Extras (Django + waitress). Sempre ativo."
& $Nssm set $Servico Start           SERVICE_AUTO_START          # sobe no boot do Windows
# O servico roda como LocalSystem, que nao enxerga o "user-site" do andre.
# Sem isto, pacotes instalados via "pip install --user" (ex: webdriver_manager)
# ficam invisiveis e derrubam o app com erro 500.
& $Nssm set $Servico AppEnvironmentExtra "PYTHONPATH=C:\Users\andre\AppData\Roaming\Python\Python311\site-packages"
& $Nssm set $Servico AppStdout      "$Projeto\logs\servidor.log"
& $Nssm set $Servico AppStderr      "$Projeto\logs\servidor.log"
& $Nssm set $Servico AppRotateFiles  1
& $Nssm set $Servico AppRotateBytes  5000000
# --- reinicio automatico se o processo sair/cair ---
& $Nssm set $Servico AppExit Default Restart
& $Nssm set $Servico AppRestartDelay 3000                        # espera 3s e reinicia
& $Nssm set $Servico AppThrottle     5000

# 5) Inicia -------------------------------------------------------------
& $Nssm start $Servico
Start-Sleep -Seconds 3
Get-Service $Servico | Select-Object Name, Status, StartType | Format-Table -AutoSize
Write-Host "Pronto! Acesse o sistema em http://localhost:8000" -ForegroundColor Green
