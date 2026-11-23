#!/usr/bin/env bash
# ==============================================================================
# pp-app-store / app-store-pp-cli 一键跨平台安装脚本 (macOS & Linux)
# 支持环境: macOS (Apple Silicon / Intel), Linux (x86_64 / arm64)
# 数据源: GitHub Releases (mvanhorn/printing-press-library)
# ==============================================================================

set -euo pipefail

RELEASE_REPO="mvanhorn/printing-press-library"
RELEASE_TAG="app-store-current"
CLI_NAME="app-store-pp-cli"
ALIAS_NAME="pp-app-store"
INSTALL_DIR="${BIN_DIR:-$HOME/.local/bin}"

# 颜色控制
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# 1. 架构与操作系统识别
OS_TYPE="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH_RAW="$(uname -m)"

case "$OS_TYPE" in
    darwin)
        OS="darwin"
        ;;
    linux)
        OS="linux"
        ;;
    *)
        log_err "不支持的操作系统: $OS_TYPE。本脚本仅支持 macOS 和 Linux。"
        exit 1
        ;;
esac

case "$ARCH_RAW" in
    x86_64|amd64)
        ARCH="amd64"
        ;;
    arm64|aarch64)
        ARCH="arm64"
        ;;
    *)
        log_err "不支持的硬件架构: $ARCH_RAW。仅支持 amd64 (x86_64) 和 arm64 (aarch64)。"
        exit 1
        ;;
esac

BINARY_FILENAME="${CLI_NAME}-${OS}-${ARCH}"
DOWNLOAD_URL="https://github.com/${RELEASE_REPO}/releases/download/${RELEASE_TAG}/${BINARY_FILENAME}"

if [ -n "${GITHUB_MIRROR:-}" ]; then
    DOWNLOAD_URL="${GITHUB_MIRROR%/}/${DOWNLOAD_URL}"
fi

log_info "目标系统架构: ${OS}-${ARCH}"
log_info "安装目录: ${INSTALL_DIR}"
log_info "下载源: ${DOWNLOAD_URL}"

mkdir -p "${INSTALL_DIR}"

# 2. 下载二进制文件
TEMP_FILE="$(mktemp "/tmp/${CLI_NAME}.XXXXXX")"
trap 'rm -f "${TEMP_FILE}"' EXIT

log_info "正在下载 ${CLI_NAME}..."
if command -v curl >/dev/null 2>&1; then
    curl -fSL --progress-bar "${DOWNLOAD_URL}" -o "${TEMP_FILE}"
elif command -v wget >/dev/null 2>&1; then
    wget -q --show-progress "${DOWNLOAD_URL}" -O "${TEMP_FILE}"
else
    log_err "未找到 curl 或 wget，请先安装下载工具。"
    exit 1
fi

chmod +x "${TEMP_FILE}"
mv -f "${TEMP_FILE}" "${INSTALL_DIR}/${CLI_NAME}"
log_ok "二进制已安装至: ${INSTALL_DIR}/${CLI_NAME}"

# 3. 创建别名软链接
ln -sf "${INSTALL_DIR}/${CLI_NAME}" "${INSTALL_DIR}/${ALIAS_NAME}"
log_ok "已建立便捷别名软链接: ${INSTALL_DIR}/${ALIAS_NAME} -> ${CLI_NAME}"

# 4. PATH 环境变量检查
if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    log_warn "${INSTALL_DIR} 尚未包含在当前 PATH 环境变量中。"
    log_warn "建议在您的 shell 配置文件（~/.zshrc 或 ~/.bashrc）中添加:"
    log_warn "    export PATH=\"${INSTALL_DIR}:\$PATH\""
fi

# 5. 自动配置多 Agent 技能软链接 (若技能目录在本地存在)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/SKILL.md" ]; then
    log_info "检测到本目录为技能根目录，正在检查各 Agent 配置..."

    AGENT_SKILL_TARGETS=(
        "$HOME/.gemini/config/skills/pp-app-store"
        "$HOME/.codex/skills/pp-app-store"
        "$HOME/.workbuddy/skills/pp-app-store"
        "$HOME/.zcode/skills/pp-app-store"
    )

    for target in "${AGENT_SKILL_TARGETS[@]}"; do
        parent_dir="$(dirname "$target")"
        if [ -d "$parent_dir" ]; then
            ln -sf "${SCRIPT_DIR}" "$target"
            log_ok "已自动关联 Agent 技能: $target -> ${SCRIPT_DIR}"
        fi
    done
fi

# 6. 验证运行
echo ""
log_info "验证安装结果:"
"${INSTALL_DIR}/${CLI_NAME}" --version || true

echo ""
log_ok "=========================================================="
log_ok "🎉 pp-app-store 安装与环境配置全部成功完成！"
log_ok "快速测试: app-store-pp-cli top --country cn --genre 6014 --limit 5"
log_ok "Agent 模式: app-store-pp-cli app 989673964 --country cn --agent"
log_ok "=========================================================="
