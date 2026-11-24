$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
foreach ($name in @('PowerShellGet', 'PSReadLine', 'Az.Accounts', 'Microsoft.Graph.Authentication', 'PnP.PowerShell', 'Pester', 'ExchangeOnlineManagement')) {
    $module = Get-Module -ListAvailable -Name $name |
        Where-Object Path -Like '/usr/local/share/powershell/Modules/*' |
        Sort-Object Version -Descending |
        Select-Object -First 1
    if (-not $module) { throw "Missing system module: $name" }
    Import-Module $module.Path -Force
    Write-Host "$name $($module.Version)"
}
