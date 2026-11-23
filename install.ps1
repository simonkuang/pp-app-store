<#
.SYNOPSIS
    pp-app-store (app-store-pp-cli) 通用 Windows 自动化安装脚本
.DESCRIPTION
    自动检测 Windows 架构（AMD64 / ARM64），从 GitHub Releases 下载对应的二进制，
    并将技能部署到通用的 agents skills 目录 (%USERPROFILE%\.agents\skills\pp-app-store)。
#>

[CmdletBinding()]
param (
    [string]$BinDir = "$env:USERPROFILE\.local\bin",
    [string]$DataDir = "$env:USERPROFILE\.local\data",
    [string]$SkillsRoot = "$env:USERPROFILE\.agents\skills",
    [string]$ReleaseRepo = "mvanhorn/printing-press-library",
    [string]$ReleaseTag = "app-store-current"
)

$ErrorActionPreference = "Stop"

function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Warn { Write-Host "[WARN] $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "[ERROR] $args" -ForegroundColor Red }

# 1. 架构检测
$arch = switch ($env:PROCESSOR_ARCHITECTURE) {
    "AMD64" { "amd64" }
    "ARM64" { "arm64" }
    default {
        Write-Err "不支持的 Windows 架构: $env:PROCESSOR_ARCHITECTURE，仅支持 AMD64 与 ARM64。"
        exit 1
    }
}

$binaryName = "app-store-pp-cli-windows-${arch}.exe"
$downloadUrl = "https://github.com/$ReleaseRepo/releases/download/$ReleaseTag/$binaryName"

if ($env:GITHUB_MIRROR) {
    $downloadUrl = "$($env:GITHUB_MIRROR.TrimEnd('/'))/$downloadUrl"
}

$targetSkillDir = Join-Path $SkillsRoot "pp-app-store"

Write-Info "目标系统架构: Windows ($arch)"
Write-Info "二进制安装路径: $BinDir"
Write-Info "通用技能目录: $targetSkillDir"
Write-Info "数据存储目录: $DataDir"

# 2. 创建目录
if (-not (Test-Path $BinDir)) { New-Item -ItemType Directory -Path $BinDir -Force | Out-Null }
if (-not (Test-Path $DataDir)) { New-Item -ItemType Directory -Path $DataDir -Force | Out-Null }
if (-not (Test-Path $SkillsRoot)) { New-Item -ItemType Directory -Path $SkillsRoot -Force | Out-Null }

$targetExe = Join-Path $BinDir "app-store-pp-cli.exe"
$aliasExe = Join-Path $BinDir "pp-app-store.exe"
$tempFile = [System.IO.Path]::GetTempFileName()

try {
    Write-Info "正在下载 $binaryName..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    Move-Item -Path $tempFile -Destination $targetExe -Force
    Copy-Item -Path $targetExe -Destination $aliasExe -Force
    Write-Success "二进制及别名已安装: $targetExe"
} catch {
    Write-Err "下载或安装失败: $_"
    if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    exit 1
}

# 3. 部署 Skill 到通用目录
$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $currentDir "SKILL.md")) {
    if ($currentDir -ne $targetSkillDir) {
        Write-Info "正在将 Skill 项目同步部署至通用目录..."
        if (-not (Test-Path $targetSkillDir)) { New-Item -ItemType Directory -Path $targetSkillDir -Force | Out-Null }
        Copy-Item -Path "$currentDir\*" -Destination $targetSkillDir -Recurse -Force
        Write-Success "通用 Skill 已部署至: $targetSkillDir"
    } else {
        Write-Success "当前目录即为通用 Skill 目录: $targetSkillDir"
    }
}

# 4. PATH 环境变量检查
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -split ';' -notcontains $BinDir) {
    Write-Warn "$BinDir 未包含在用户 PATH 中。"
    try {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$BinDir", "User")
        $env:Path = "$env:Path;$BinDir"
        Write-Success "已自动将 $BinDir 追加到用户 PATH 环境变量！"
    } catch {
        Write-Warn "无法自动修改 PATH，请手动在环境变量中追加: $BinDir"
    }
}

# 5. 验证版本
Write-Host ""
Write-Info "验证安装版本:"
& $targetExe --version

Write-Host ""
Write-Success "=========================================================="
Write-Success "🎉 pp-app-store Windows 通用安装完成！"
Write-Success "CLI 可执行文件: $targetExe"
Write-Success "通用技能说明书: $targetSkillDir\SKILL.md"
Write-Success "=========================================================="
