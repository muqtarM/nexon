# examples/demo_windows.ps1
<#
.SYNOPSIS
    Demo script for Nexon on Windows (PowerShell)
.DESCRIPTION
    Runs the full Phase 1 Nexon workflow on Windows using PowerShell.
#>

# Ensure errors stop the script
$ErrorActionPreference = 'Stop'

Write-Host "[1/7] Creating environment 'demo' with role animator"
& nexon create-env demo --role animator

Write-Host "`n[2/7] Scaffolding package 'mytool' version 0.1.0"
& nexon create-package mytool 0.1.0

Write-Host "`n[3/7] Installing 'mytool' into 'demo' (with dependency resolution)"
& nexon install-package demo mytool

Write-Host "`n[4/7] Listing environments and packages"
& nexon list-envs
& nexon list-packages

Write-Host "`n[5/7] Activating 'demo' environment"
& nexon activate-env demo

Write-Host "`nActive environment variable NEXON_ENV:"
Write-Host "NEXON_ENV = $Env:NEXON_ENV"

Write-Host "`n[6/7] Locking environment 'demo' for reproducibility"
& nexon lock-env demo

Write-Host "`n[7/7] Building Docker image for 'demo'"
& nexon build-docker demo --tag myorg/demo:1.0

Write-Host "`n✅ Nexon Windows demo complete!"