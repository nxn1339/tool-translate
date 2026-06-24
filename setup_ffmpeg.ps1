# setup_ffmpeg.ps1
# Ensure ffmpeg.exe is present in the project's ffmpeg folder.
# If not, download the official release zip, extract, and copy ffmpeg.exe.

# Resolve project root (directory of this script)
$scriptPath = $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$ffmpegDir = Join-Path $projectRoot 'ffmpeg'
$ffmpegExe = Join-Path $ffmpegDir 'ffmpeg.exe'

# If ffmpeg already exists, exit
if (Test-Path $ffmpegExe) {
    Write-Host '[Setup] ffmpeg already present.'
    exit 0
}

# Write starting message
Write-Host '[Setup] ffmpeg not found, downloading now...'

# URL của bản ffmpeg release essentials
$url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
# Tên file zip tạm thời (không trùng lặp, dựa trên timestamp)
$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$tempZip = Join-Path $projectRoot "ffmpeg_$timestamp.zip"

# Tải zip vào file tạm
Invoke-WebRequest -Uri $url -OutFile $tempZip -UseBasicParsing -ErrorAction Stop

# Thư mục tạm để giải nén
$extractPath = Join-Path $projectRoot 'ffmpeg_extracted'
if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
Expand-Archive -Path $tempZip -DestinationPath $extractPath -Force

# Tìm ffmpeg.exe trong thư mục đã giải nén
$exe = Get-ChildItem -Path $extractPath -Filter 'ffmpeg.exe' -Recurse | Select-Object -First 1
if (-not $exe) { throw 'ffmpeg.exe not found after extraction' }

# Đảm bảo thư mục đích tồn tại
if (-not (Test-Path $ffmpegDir)) { New-Item -ItemType Directory -Path $ffmpegDir | Out-Null }
# Sao chép ffmpeg.exe vào thư mục dự án
Copy-Item -Path $exe.FullName -Destination $ffmpegExe -Force

# Dọn dẹp file tạm
Remove-Item $tempZip -Force
Remove-Item $extractPath -Recurse -Force

Write-Host '[Setup] ffmpeg setup completed.'
