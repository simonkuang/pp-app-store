#!/usr/bin/env bash
# ==============================================================================
# pp-app-store 通用一键安装脚本 (macOS & Linux)
# 支持环境: macOS (Apple Silicon / Intel), Linux (x86_64 / arm64)
# 数据源: GitHub Releases (mvanhorn/printing-press-library)
# ==============================================================================

set -euo pipefail

RELEASE_REPO="mvanhorn/printing-press-library"
RELEASE_TAG="app-store-current"
CLI_NAME="app-store-pp-cli"
ALIAS_NAME="pp-app-store"

BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"
DATA_DIR="${DATA_DIR:-$HOME/.local/data}"
SKILLS_ROOT="${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}"
TARGET_SKILL_DIR="${SKILLS_ROOT}/pp-app-store"

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
    darwin) OS="darwin" ;;
    linux)  OS="linux" ;;
    *)
        log_err "不支持的操作系统: $OS_TYPE。本脚本仅支持 macOS 和 Linux。"
        exit 1
        ;;
esac

case "$ARCH_RAW" in
    x86_64|amd64) ARCH="amd64" ;;
    arm64|aarch64) ARCH="arm64" ;;
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
log_info "二进制安装路径: ${BIN_DIR}"
log_info "数据存储目录: ${DATA_DIR}"
log_info "通用技能目录: ${TARGET_SKILL_DIR}"

mkdir -p "${BIN_DIR}" "${DATA_DIR}" "${SKILLS_ROOT}"

# 2. 下载与部署 CLI 二进制文件
TEMP_FILE="$(mktemp "/tmp/${CLI_NAME}.XXXXXX")"
trap 'rm -f "${TEMP_FILE}"' EXIT

log_info "正在从 GitHub Releases 下载 ${CLI_NAME}..."
if command -v curl >/dev/null 2>&1; then
    curl -fSL --progress-bar "${DOWNLOAD_URL}" -o "${TEMP_FILE}"
elif command -v wget >/dev/null 2>&1; then
    wget -q --show-progress "${DOWNLOAD_URL}" -O "${TEMP_FILE}"
else
    log_err "未找到 curl 或 wget，请先安装下载工具。"
    exit 1
fi

chmod +x "${TEMP_FILE}"
mv -f "${TEMP_FILE}" "${BIN_DIR}/${CLI_NAME}"
ln -sf "${BIN_DIR}/${CLI_NAME}" "${BIN_DIR}/${ALIAS_NAME}"
log_ok "二进制与便捷别名安装完成: ${BIN_DIR}/${CLI_NAME} (${ALIAS_NAME})"

# 3. 部署通用 Skill 到 ~/.agents/skills/pp-app-store
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${CURRENT_DIR}/SKILL.md" ]; then
    if [ "${CURRENT_DIR}" != "${TARGET_SKILL_DIR}" ]; then
        log_info "正在将 Skill 项目同步部署至通用技能目录..."
        mkdir -p "${TARGET_SKILL_DIR}"
        cp -Rf "${CURRENT_DIR}/." "${TARGET_SKILL_DIR}/"
        log_ok "通用 Skill 已部署至: ${TARGET_SKILL_DIR}"
    else
        log_ok "当前目录即为通用 Skill 目录: ${TARGET_SKILL_DIR}"
    fi
fi

# 4. PATH 检查提示
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
    log_warn "${BIN_DIR} 尚未包含在当前 PATH 中。"
    log_warn "建议在 shell 配置（~/.zshrc 或 ~/.bashrc）中添加:"
    log_warn "    export PATH=\"${BIN_DIR}:\$PATH\""
fi

# 5. 验证执行
echo ""
log_info "验证安装结果:"
"${BIN_DIR}/${CLI_NAME}" --version || true

echo ""
log_ok "=========================================================="
log_ok "🎉 pp-app-store 通用安装成功！"
log_ok "CLI 可执行文件: ${BIN_DIR}/${CLI_NAME}"
log_ok "通用技能说明书: ${TARGET_SKILL_DIR}/SKILL.md"
log_ok "SQLite 默认目录: ${DATA_DIR}/pp-app-store.db"
log_ok "=========================================================="
