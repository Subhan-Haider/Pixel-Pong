# Pixel Pong MSIX Build Script 🚀
# This script prepares the folder and provides instructions for packaging.

$ErrorActionPreference = "Stop"

Write-Host "--- 📦 Preparing MSIX Package ---" -ForegroundColor Cyan

# 1. Create Folders
$msixDir = "MSIX_Output"
$assetsDir = "$msixDir\Assets"
if (!(Test-Path $assetsDir)) { New-Item -ItemType Directory -Path $assetsDir }

# 2. Copy Executable and Assets
Write-Host "Copying executable..."
if (Test-Path "dist\PixelPong.exe") {
    Copy-Item "dist\PixelPong.exe" -Destination "$msixDir\PixelPong.exe"
} else {
    Write-Warning "PixelPong.exe not found in dist/. Please run 'pyinstaller' first."
}

Write-Host "Copying manifest..."
Copy-Item "AppxManifest.xml" -Destination "$msixDir\AppxManifest.xml"

# 3. Handle Icons (Placeholder logic)
Write-Host "Copying icons..."
$generatedIcon = Get-ChildItem "pixel_pong_store_icon*.png" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($generatedIcon) {
    Copy-Item $generatedIcon.FullName -Destination "$assetsDir\StoreLogo.png"
    Copy-Item $generatedIcon.FullName -Destination "$assetsDir\Square150x150Logo.png"
    Copy-Item $generatedIcon.FullName -Destination "$assetsDir\Square44x44Logo.png"
    Copy-Item $generatedIcon.FullName -Destination "$assetsDir\Wide310x150Logo.png"
    Copy-Item $generatedIcon.FullName -Destination "$assetsDir\SplashScreen.png"
    Write-Host "Icons copied from generated design."
}

Write-Host "`n--- ✅ Folders Prepared ---" -ForegroundColor Green
Write-Host "To finish building the MSIX, run the following command in your Windows SDK terminal:" -ForegroundColor Yellow
Write-Host "SignTool sign /fd SHA256 /a /f YourCertificate.pfx /p YourPassword PixelPong.msix" -ForegroundColor White
