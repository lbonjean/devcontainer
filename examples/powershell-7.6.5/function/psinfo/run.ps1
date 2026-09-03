using namespace System.Net

# Input bindings are passed in via param block.
param($Request, $TriggerMetadata)



$body= "PowerShell version: $($PSVersionTable.PSVersion)`n"
$body+= "PS Module path: $($env:PSModulePath)`n"
$body+= "---------------------------------------------------`n"
$modules=Get-Module -ListAvailable | Select-Object Name, Version, ModuleBase | Sort-Object Name
$body+= "Available Modules: $($modules | ForEach-Object { "$($_.Name) v$($_.Version) ($($_.ModuleBase))" } | Out-String)`n"
$body+= "---------------------------------------------------`n"
$envvars = Get-ChildItem env: 
$body+= "Environment: $($envvars | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" } | Out-String)`n"
$body+= "---------------------------------------------------`n"
$body+= "Request Query: $($Request.Query | ConvertTo-Json -Depth 10)`n"
$body+= "Request Body: $($Request.Body | ConvertTo-Json -Depth 10)`n"
$body+= "Request Headers: $($Request.Headers | ConvertTo-Json -Depth 10)`n"
$body+= "Trigger Metadata: $($TriggerMetadata | ConvertTo-Json -Depth 10)`n"
$body+= "Request Params: $($Request.Params | ConvertTo-Json -Depth 10)`n"
$body+= "Request Method: $($Request.Method)`n"
$body+= "Request Uri: $($Request.Uri)`n"  



# Write the body to the console for debugging purposes
Write-Host $body
# Associate values to output bindings by calling 'Push-OutputBinding'.
Push-OutputBinding -Name Response -Value ([HttpResponseContext]@{
    StatusCode = [HttpStatusCode]::OK
    Body = $body
})
