# GitHub Rulesets Import Script (PowerShell)
# This script imports all rulesets into your GitHub repository

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoOwner,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoName
)

$ErrorActionPreference = "Stop"

# API endpoint
$apiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/rulesets"

# Headers
$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
    "Content-Type" = "application/json"
}

# Ruleset files
$rulesets = @(
    "main-branch-protection.json",
    "develop-branch-protection.json",
    "branch-naming-convention.json"
)

Write-Host "Importing GitHub Rulesets..." -ForegroundColor Yellow
Write-Host "Repository: $RepoOwner/$RepoName" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($ruleset in $rulesets) {
    $filePath = ".github/rulesets/$ruleset"
    
    if (-not (Test-Path $filePath)) {
        Write-Host "Error: File $filePath not found" -ForegroundColor Red
        $failCount++
        continue
    }
    
    Write-Host "Importing $ruleset..." -ForegroundColor Yellow
    
    try {
        $jsonContent = Get-Content $filePath -Raw | ConvertFrom-Json | ConvertTo-Json -Depth 100
        
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $jsonContent -ErrorAction Stop
        
        Write-Host "✅ Successfully imported $ruleset" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "❌ Failed to import $ruleset" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.ErrorDetails.Message) {
            $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Details: $($errorDetails.message)" -ForegroundColor Red
        }
        
        $failCount++
    }
    
    Write-Host ""
}

# Summary
Write-Host "Import Summary:" -ForegroundColor Yellow
Write-Host "Success: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red

if ($failCount -eq 0) {
    Write-Host "All rulesets imported successfully!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "Some rulesets failed to import" -ForegroundColor Red
    exit 1
}
