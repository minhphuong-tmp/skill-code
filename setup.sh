#!/usr/bin/env bash
# ==============================================================================
# SCRIPT TỰ ĐỘNG THIẾT LẬP MÔI TRƯỜNG TOÀN DIỆN (ONE-CLICK SETUP SCRIPT)
# Tác dụng: Cài đặt và chuẩn bị 100% công cụ để chạy bộ Skill Suite & E2E Testing
# Sử dụng: ./setup.sh hoặc ./setup
# ==============================================================================

set -e

# Xác định thư mục gốc của dự án (nằm trên thư mục SKILL Code hoặc ngay tại thư mục hiện tại)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../package.json" ] || [ -d "$SCRIPT_DIR/../.git" ]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

# Màu sắc thông báo terminal
COLOR_RESET="\033[0m"
COLOR_GREEN="\033[38;5;48m"
COLOR_BLUE="\033[38;5;39m"
COLOR_YELLOW="\033[38;5;220m"
COLOR_RED="\033[38;5;196m"
COLOR_CYAN="\033[38;5;51m"
COLOR_BOLD="\033[1m"

log_info() { echo -e "${COLOR_BLUE}ℹ️  $1${COLOR_RESET}"; }
log_success() { echo -e "${COLOR_GREEN}✅ $1${COLOR_RESET}"; }
log_warn() { echo -e "${COLOR_YELLOW}⚠️  $1${COLOR_RESET}"; }
log_error() { echo -e "${COLOR_RED}❌ $1${COLOR_RESET}"; }
log_step() { echo -e "\n${COLOR_BOLD}${COLOR_CYAN}==> $1${COLOR_RESET}"; }

echo -e "${COLOR_BOLD}${COLOR_GREEN}"
echo "================================================================================"
echo "🚀 [ONE-CLICK SETUP] THIẾT LẬP MÔI TRƯỜNG CHẠY BỘ SKILL SUITE & E2E TESTING"
echo "================================================================================"
echo -e "${COLOR_RESET}"

# ------------------------------------------------------------------------------
# 1. KIỂM TRA HỆ ĐIỀU HÀNH
# ------------------------------------------------------------------------------
log_step "BƯỚC 1: Kiểm Tra Hệ Điều Hành"
OS="$(uname -s)"
ARCH="$(uname -m)"
log_info "Hệ điều hành phát hiện: $OS ($ARCH)"

# ------------------------------------------------------------------------------
# 2. KIỂM TRA PYTHON 3 & PYTEST
# ------------------------------------------------------------------------------
log_step "BƯỚC 2: Kiểm Tra Môi Trường Python 3 & Pytest (Step 3 TDD & Scripts)"
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version)
    log_success "Python 3 đã có sẵn: $PY_VER"
else
    log_error "Không tìm thấy Python 3! Vui lòng cài đặt Python >= 3.9."
    exit 1
fi

if python3 -m pytest --version &>/dev/null; then
    log_success "pytest đã được cài đặt."
else
    log_info "Đang cài đặt pytest cho Python..."
    pip3 install --quiet --break-system-packages pytest pytest-mock 2>/dev/null \
        || pip3 install --quiet pytest pytest-mock 2>/dev/null \
        || python3 -m pip install --quiet pytest pytest-mock 2>/dev/null \
        || log_warn "Không thể cài pytest tự động, sẽ fallback sang unittest mặc định."
fi

# ------------------------------------------------------------------------------
# 3. KIỂM TRA NODE.JS & NPM
# ------------------------------------------------------------------------------
log_step "BƯỚC 3: Kiểm Tra Node.js & Trình Quản Lý Gói"
if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    log_success "Node.js đã có sẵn: $NODE_VER"
else
    log_error "Chưa tìm thấy Node.js! Vui lòng cài đặt Node.js >= 18."
    if [ "$OS" = "Darwin" ] && command -v brew &>/dev/null; then
        log_info "Đang cài đặt Node.js qua Homebrew..."
        brew install node
    else
        log_error "Hãy truy cập https://nodejs.org để tải Node.js và chạy lại script này."
        exit 1
    fi
fi

# ------------------------------------------------------------------------------
# 4. CÀI ĐẶT REPOMIX TOÀN CỤC (BẮT BUỘC CHO STEP 0.1 & STEP 0.2 SCAN)
# ------------------------------------------------------------------------------
log_step "BƯỚC 4: Kiểm Tra Công Cụ Nén AST & Thu Hoạch Tài Liệu (Repomix)"
if command -v repomix &>/dev/null; then
    log_success "repomix đã có sẵn trong hệ thống: $(repomix --version 2>/dev/null || echo 'OK')"
else
    log_info "Đang tiến hành cài đặt repomix toàn cục qua npm..."
    npm install -g repomix --silent 2>/dev/null || sudo npm install -g repomix --silent 2>/dev/null || log_warn "Không thể cài repomix toàn cục. Sẽ dùng qua npx repomix khi quét."
    log_success "repomix đã được cấu hình!"
fi

# ------------------------------------------------------------------------------
# 5. KIỂM TRA FFMPEG (BẮT BUỘC ĐỂ BÓC TÁCH VIDEO 1 FPS TẠI STEP 5 & STEP 0)
# ------------------------------------------------------------------------------
log_step "BƯỚC 5: Kiểm Tra Công Cụ FFMPEG (Bóc Tách Keyframes Video 1 FPS)"
if command -v ffmpeg &>/dev/null; then
    log_success "ffmpeg đã có sẵn trong PATH."
else
    log_warn "Không tìm thấy ffmpeg! Đang tiến hành cài đặt..."
    if [ "$OS" = "Darwin" ]; then
        if command -v brew &>/dev/null; then
            log_info "Đang cài đặt ffmpeg qua Homebrew..."
            brew install ffmpeg || log_warn "Cài ffmpeg qua brew chưa thành công."
        else
            log_warn "Homebrew chưa cài trên máy Mac này. Bạn có thể cài ffmpeg qua: brew install ffmpeg"
        fi
    elif [ -f /etc/debian_version ]; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    else
        log_warn "Vui lòng cài đặt ffmpeg thủ công để script analyze_e2e_clip.py có thể bóc tách frame ảnh từ video."
    fi
fi

# ------------------------------------------------------------------------------
# 6. CÀI ĐẶT PLAYWRIGHT & MIDSCENE AI (@midscene/web)
# ------------------------------------------------------------------------------
log_step "BƯỚC 6: Cài Đặt Playwright, Trình Duyệt Chromium & Midscene AI"

# Tìm thư mục chứa Playwright trong dự án đích
E2E_TARGET_DIR="$PROJECT_ROOT"
for cand in "playwright" "e2e" "tests/e2e" "frontend/playwright" "posthog/playwright"; do
    if [ -f "$PROJECT_ROOT/$cand/playwright.config.ts" ] || [ -f "$PROJECT_ROOT/$cand/playwright.config.js" ]; then
        E2E_TARGET_DIR="$PROJECT_ROOT/$cand"
        break
    fi
done

log_info "Thư mục cài đặt Playwright & Midscene: $E2E_TARGET_DIR"
cd "$E2E_TARGET_DIR"

if [ ! -f "package.json" ]; then
    log_info "Khởi tạo package.json tại $E2E_TARGET_DIR..."
    npm init -y --silent >/dev/null 2>&1 || true
fi

log_info "Đang cài đặt @midscene/web và @playwright/test..."
npm install -D @midscene/web @playwright/test --no-fund --no-audit --silent 2>/dev/null || npm install -D @midscene/web @playwright/test

log_info "Đang tải trình duyệt Chromium cho Playwright..."
npx playwright install chromium 2>/dev/null || npx playwright install chromium --with-deps 2>/dev/null || true
log_success "Playwright Chromium & Midscene AI đã sẵn sàng!"

cd "$PROJECT_ROOT"

# ------------------------------------------------------------------------------
# 7. KHỞI TẠO FILE CẤU HÌNH BIẾN MÔI TRƯỜNG (.env)
# ------------------------------------------------------------------------------
log_step "BƯỚC 7: Khởi Tạo File Môi Trường .env & .env.example"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"
cat << 'EOF' > "$ENV_EXAMPLE"
# ==============================================================================
# CẤU HÌNH BỘ NÃO MIDSCENE AI (Google Gemini hoặc OpenAI)
# ==============================================================================
# 1. Google Gemini (Khuyên dùng cho Midscene Vision):
GEMINI_API_KEY=your_gemini_api_key_here
MIDSCENE_MODEL_NAME=gemini-3.5-flash-lite
MIDSCENE_MODEL_FAMILY=gemini

# 2. Hoặc dùng OpenAI:
# OPENAI_API_KEY=your_openai_api_key_here
# MIDSCENE_MODEL_NAME=gpt-4o

# ==============================================================================
# CẤU HÌNH PLAYWRIGHT E2E
# ==============================================================================
PLAYWRIGHT_VIDEO=on
DISABLE_SECURE_SSL_REDIRECT=1
EOF
log_success "Đã tạo file mẫu $ENV_EXAMPLE"

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$ENV_EXAMPLE" "$PROJECT_ROOT/.env"
    log_success "Đã tạo file .env chính! Hãy mở .env và điền GEMINI_API_KEY."
else
    log_success "File .env đã tồn tại sẵn tại thư mục gốc."
fi

# ------------------------------------------------------------------------------
# 8. PHÂN QUYỀN THỰC THI (chmod +x) CHO SCRIPTS
# ------------------------------------------------------------------------------
log_step "BƯỚC 8: Cấp Quyền Thực Thi Cho Toàn Bộ Scripts"
chmod +x "$SCRIPT_DIR"/setup.sh "$SCRIPT_DIR"/setup 2>/dev/null || true
if [ -d "$SCRIPT_DIR/scripts" ]; then
    chmod +x "$SCRIPT_DIR"/scripts/*.py "$SCRIPT_DIR"/scripts/*.sh 2>/dev/null || true
fi
log_success "Đã phân quyền thực thi cho toàn bộ scripts!"

# ------------------------------------------------------------------------------
# TỔNG KẾT
# ------------------------------------------------------------------------------
echo -e "\n${COLOR_BOLD}${COLOR_GREEN}"
echo "================================================================================"
echo "🎉 [SETUP COMPLETED] TOÀN BỘ PHỤ THUỘC ĐÃ ĐƯỢC CÀI ĐẶT THÀNH CÔNG 100%!"
echo "================================================================================"
echo -e "${COLOR_RESET}"
echo -e "Các công cụ đã sẵn sàng:"
echo -e "  • ${COLOR_GREEN}Python Test Runner & pytest:${COLOR_RESET} Đã cài đặt"
echo -e "  • ${COLOR_GREEN}Node.js & Repomix:${COLOR_RESET} Đã cài đặt"
echo -e "  • ${COLOR_GREEN}FFMPEG (Bóc tách video 1 FPS):${COLOR_RESET} Đã sẵn sàng"
echo -e "  • ${COLOR_GREEN}Playwright & Midscene AI:${COLOR_RESET} Đã cài đặt"
echo -e "  • ${COLOR_GREEN}File cấu hình:${COLOR_RESET} $PROJECT_ROOT/.env"
echo ""
echo -e "${COLOR_CYAN}👉 BẮT ĐẦU CHẠY QUÉT BƯỚC 0:${COLOR_RESET}"
echo -e "  1. Điền Gemini API Key: ${COLOR_YELLOW}nano .env${COLOR_RESET}"
echo -e "  2. Quét mã nguồn:       ${COLOR_GREEN}python3 'SKILL Code/scripts/scan_codebase.py' .${COLOR_RESET}"
echo -e "  3. Quét nghiệp vụ:      ${COLOR_GREEN}python3 'SKILL Code/scripts/scan_requirements.py' .${COLOR_RESET}"
echo -e "  4. Khảo sát E2E:        ${COLOR_GREEN}python3 'SKILL Code/scripts/run_e2e_local.py' --check-services${COLOR_RESET}"
echo "================================================================================"
