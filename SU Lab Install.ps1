# Create Apps-SU directory if it doesn't exist
New-Item -Path "C:\Apps-SU" -ItemType Directory -Force | Out-Null

# Set variables
$prog = "dvcurator"
$exe = "C:\Apps-SU\${prog}_win.exe"
$desktop = [Environment]::GetFolderPath("Desktop")
$lnk = "${desktop}\${prog}.url"

Write-Host "Downloading $prog..."

# Get latest release download URL and download the exe
$release = Invoke-RestMethod -Uri "https://api.github.com/repos/QualitativeDataRepository/dvcurator-python/releases/latest"
$downloadUrl = $release.assets | Where-Object { $_.browser_download_url -like "*.exe" } | Select-Object -ExpandProperty browser_download_url
Invoke-WebRequest -Uri $downloadUrl -OutFile $exe -UseBasicParsing

Write-Host "Download complete!"

Write-Host "Making desktop shortcut..."
@"
[InternetShortcut]
URL=$exe
IconFile=$exe
IconIndex=0
"@ | Out-File -FilePath $lnk -Encoding ASCII

Write-Host "Install complete!"
Pause