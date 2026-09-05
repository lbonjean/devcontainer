$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
$promptInit = oh-my-posh init pwsh
if (-not $promptInit) { throw 'Oh My Posh did not generate PowerShell initialization' }
$promptInit | Invoke-Expression
if ($PSVersionTable.PSVersion.ToString() -ne '7.6.5') {
    throw "Unexpected PowerShell version: $($PSVersionTable.PSVersion)"
}
foreach ($name in @('PowerShellGet', 'PSReadLine', 'Az.Accounts', 'Microsoft.Graph.Authentication', 'PnP.PowerShell', 'Pester', 'ExchangeOnlineManagement')) {
    $module = Get-Module -ListAvailable -Name $name |
        Where-Object Path -Like '/home/vscode/.local/share/powershell/Modules/*' |
        Sort-Object Version -Descending |
        Select-Object -First 1
    if (-not $module) { throw "Missing user module: $name" }
    Import-Module $module.Path -Force
    Write-Host "$name $($module.Version)"
}
