<#
.SYNOPSIS
    pp-app-store (app-store-pp-cli) Windows 自动化安装脚本
.DESCRIPTION
    自动检测 Windows 架构（AMD64 / ARM64），从 GitHub Releases 下载对应的 app-store-pp-cli.exe，
    部署到用户本地目录并配置别名与 Agent 技能软链接。
#>

[CmdletBinding()]
param (
    [string]$InstallDir = "$env:USERPROFILE\.local\bin",
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

Write-Info "目标系统架构: Windows ($arch)"
Write-Info "安装目录: $InstallDir"
Write-Info "下载源: $downloadUrl"

# 2. 创建目录
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

$targetExe = Join-Path $InstallDir "app-store-pp-cli.exe"
$aliasExe = Join-Path $InstallDir "pp-app-store.exe"
$tempFile = [System.IO.Path]::GetTempFileName()

try {
    Write-Info "正在下载 $binaryName..."
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing
    Move-Item -Path $tempFile -Destination $targetExe -Force
    Copy-Item -Path $targetExe -Destination $aliasExe -Force
    Write-Success "二进制已安装至: $targetExe"
    Write-Success "别名快捷方式已就绪: $aliasExe"
} catch {
    Write-Err "下载或安装失败: $_"
    if (Test-Path $tempFile) { Remove-Item $tempFile -Force }
    exit 1
}

# 3. 环境变量 PATH 检查
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -split ';' -notcontains $InstallDir) {
    Write-Warn "$InstallDir 未包含在当前用户的 PATH 中。"
    try {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$InstallDir", "User")
        $env:Path = "$env:Path;$InstallDir"
        Write-Success "已自动将 $InstallDir 追加到用户 PATH 环境变量！"
    } catch {
        Write-Warn "无法自动修改 PATH，请手动在系统环境变量中添加: $InstallDir"
    }
}

# 4. 自动关联 Agent 技能目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $scriptDir "SKILL.md")) {
    Write-Info "正在检查本地各 Agent 技能配置..."
    $targets = @(
        "$env:USERPROFILE\.gemini\config\skills\pp-app-store",
        "$env:USERPROFILE\.codex\skills\pp-app-store",
        "$env:USERPROFILE\.workbuddy\skills\pp-app-store",
        "$env:USERPROFILE\.zcode\skills\pp-app-store"
    )

    foreach ($target in $targets) {
        $parent = Split-Path -Parent $target
        if (Test-Path $parent) {
            try {
                if (Test-Path $target) { Remove-Item $target -Recurse -Force }
                New-Item -ItemType SymbolicLink -Path $target -Target $scriptDir -Force | Out-Null
                Write-Success "已关联 Agent 技能: $target -> $scriptDir"
            } catch {
                # Windows 非管理员模式下软链接可能受限，降级为目录硬链接/Junction
                try {
                    cmd /c mklink /J "$target" "$scriptDir" | Out-Null
                    Write-Success "已通过 Junction 关联 Agent 技能: $target -> $scriptDir"
                } catch {
                    Write-Warn "无法创建技能链接至 $target: $_"
                }
            }
        }
    }
}

# 5. 验证版本
Write-Host ""
Write-Info "验证安装版本:"
& $targetExe --version

Write-Host ""
Write-Success "=========================================================="
Write-Success "🎉 pp-app-store Windows 安装配置成功！"
Write-Success "使用示例: app-store-pp-cli top --country us --limit 10"
Write-Success "=========================================================="
