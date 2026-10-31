$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($env:MODULES)) {
    Write-Host 'powershell-modules: no modules requested.'
    exit 0
}

$modules = @($env:MODULES.Split(',') | ForEach-Object { $_.Trim() })
foreach ($module in $modules) {
    if ($module -notmatch '^[A-Za-z0-9][A-Za-z0-9_.-]*$') {
        throw "powershell-modules: use comma-separated module names without empty entries; invalid name '$module'."
    }
}

# Save outside PSModulePath so loaded package-management modules can be updated.
$staging = Join-Path ([IO.Path]::GetTempPath()) ([IO.Path]::GetRandomFileName())
try {
    New-Item -ItemType Directory -Path $staging -Force | Out-Null
    if (-not (Get-PSRepository -Name PSGallery -ErrorAction SilentlyContinue)) {
        Register-PSRepository -Default
    }
    Save-Module -Name ($modules | Select-Object -Unique) -Repository PSGallery -Path $staging -Force -AcceptLicense
    $destination = '/usr/local/share/powershell/Modules'
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Get-ChildItem -LiteralPath $staging -Directory | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force
    }
}
finally {
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}
