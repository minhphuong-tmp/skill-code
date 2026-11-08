#!/usr/bin/env python3
# scripts/run_e2e_local.py
"""
Script điều phối chạy kiểm thử E2E Playwright trên môi trường Local có Ghi Hình (Video Recording).
Tính năng:
  1. Tự động kiểm tra trạng thái sức khỏe (Health Check) của toàn bộ các Service local.
  2. Ghi rõ nguyên nhân nếu service nào chưa hoạt động (OFFLINE).
  3. Kích hoạt Playwright với cờ quay video (--video=on).
  4. Tự động thu thập video clip (.webm) lưu vào artifacts/videos/<spec_name>.webm để Agent đối chiếu.
"""

import os
import sys
import socket
import argparse
import subprocess
import shutil
import glob
from pathlib import Path

# Danh mục các dịch vụ Local mặc định khi dự án chưa có file services.json
DEFAULT_SERVICES = [
    {"name": "Frontend Web App", "host": "127.0.0.1", "port": 3000, "desc": "Giao diện Web Frontend (React/Vue/Next/Vite)"},
    {"name": "Backend API Service", "host": "127.0.0.1", "port": 8000, "desc": "REST / GraphQL Backend API"},
    {"name": "Database Service", "host": "127.0.0.1", "port": 5432, "desc": "Cơ sở dữ liệu chính (PostgreSQL/MySQL)"},
    {"name": "Cache / Message Broker", "host": "127.0.0.1", "port": 6379, "desc": "Hệ thống Cache & Task Queue (Redis)"},
]

def check_port(host: str, port: int, timeout: float = 0.5) -> bool:
    """Kiểm tra xem một cổng mạng có đang lắng nghe kết nối hay không."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def get_configured_services(root_dir: Path):
    """Nạp danh sách services từ file cấu hình của dự án (services.json) hoặc fallback danh mục mặc định."""
    import json
    for cand in ["services.json", ".services.json", "SKILL Code/services.json", "config/services.json"]:
        f_path = root_dir / cand
        if f_path.exists():
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return DEFAULT_SERVICES

def print_service_status():
    """In bảng trạng thái chi tiết của tất cả dịch vụ trong hệ thống."""
    root_dir = get_repo_root()
    services = get_configured_services(root_dir)
    print("=" * 80)
    print("📡 [E2E LOCAL RUNNER] BẢNG KIỂM TRA TRẠNG THÁI SERVICES LOCAL")
    print("=" * 80)
    print(f"{'Dịch Vụ':<24} | {'Port':<6} | {'Trạng Thái':<12} | {'Ghi Chú / Lý Do'}")
    print("-" * 80)

    all_online = True
    for s in services:
        is_up = check_port(s["host"], s["port"])
        if is_up:
            status = "🟢 ONLINE"
            note = s.get("desc", "Đang phản hồi kết nối")
        else:
            status = "🔴 OFFLINE"
            note = s.get("offline_hint", "Chưa khởi chạy tiến trình hoặc container (kiểm tra script khởi động)")
            all_online = False
        print(f"{s['name']:<24} | {s['port']:<6} | {status:<12} | {note}")

    print("=" * 80)
    return all_online

def get_repo_root() -> Path:
    cur = Path(__file__).resolve().parent
    while cur != cur.parent:
        if (cur / ".git").exists() or (cur / "package.json").exists() or (cur / "pyproject.toml").exists() or (cur / "go.mod").exists():
            return cur
        cur = cur.parent
    return Path(__file__).resolve().parents[2]

def load_env_file(root_dir: Path):
    """Nạp các biến môi trường từ .env (Midscene AI, Gemini API Key, Base URL)."""
    env_file = root_dir / ".env"
    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

def find_playwright_dir(root_dir: Path) -> Path:
    """Tự động phát hiện thư mục chứa cấu hình Playwright trong dự án."""
    # 1. Kiểm tra ngay tại root
    if (root_dir / "playwright.config.ts").exists() or (root_dir / "playwright.config.js").exists():
        return root_dir
    # 2. Kiểm tra các thư mục quy ước phổ biến
    for candidate in ["playwright", "e2e", "tests/e2e", "test/e2e", "frontend/playwright"]:
        p = root_dir / candidate
        if (p / "playwright.config.ts").exists() or (p / "playwright.config.js").exists():
            return p
    # 3. Tìm kiếm file config trên toàn bộ repo (bỏ qua node_modules/.git)
    for cfg in root_dir.glob("**/playwright.config.*"):
        if "node_modules" not in str(cfg) and ".git" not in str(cfg):
            return cfg.parent
    return root_dir

def run_playwright_test(spec_path: str, record_video: bool = True, output_dir: str = "artifacts/videos"):
    """Thực thi kịch bản Playwright và thu thập clip quay màn hình."""
    root_dir = get_repo_root()
    load_env_file(root_dir)
    dest_output_dir = root_dir / output_dir
    os.makedirs(dest_output_dir, exist_ok=True)
    
    playwright_dir = find_playwright_dir(root_dir)

    # Chuẩn hóa đường dẫn spec nếu được truyền từ root
    raw_spec = Path(spec_path)
    if (root_dir / raw_spec).exists() and not (playwright_dir / raw_spec).exists():
        try:
            rel_spec = (root_dir / raw_spec).resolve().relative_to(playwright_dir.resolve())
            spec_path = str(rel_spec)
        except ValueError:
            spec_path = str(raw_spec)

    print(f"\n🎬 Chuẩn bị chạy kịch bản E2E: {spec_path}")
    print(f"📂 Thư mục Playwright: {playwright_dir}")
    print(f"📹 Chế độ quay màn hình: {'BẬT (Recording Video ON)' if record_video else 'TẮT'}")
    print(f"📁 Thư mục lưu trữ video: {root_dir / output_dir}\n")

    cmd = ["npx", "playwright", "test", spec_path]

    env = os.environ.copy()
    env["PLAYWRIGHT_VIDEO"] = "on" if record_video else "off"
    if "BASE_URL" not in env:
        # Tự động chọn port active (3000, 5001, 8080, 8000)
        for p in [8080, 3000, 5001, 8000]:
            if check_port("127.0.0.1", p):
                env["BASE_URL"] = f"http://localhost:{p}"
                break
        if "BASE_URL" not in env:
            env["BASE_URL"] = "http://localhost:3000"

    # Thực thi lệnh Playwright
    try:
        proc = subprocess.run(cmd, cwd=str(playwright_dir), env=env, text=True)
        test_passed = (proc.returncode == 0)
    except Exception as e:
        print(f"❌ Lỗi khi khởi chạy Playwright: {e}")
        test_passed = False

    # Tìm các file video sinh ra
    spec_stem = Path(spec_path).stem.replace(".spec", "")
    video_patterns = [
        str(playwright_dir / "test-results" / "**" / "*.webm"),
        str(root_dir / "test-results" / "**" / "*.webm"),
    ]

    copied_videos = []
    for pattern in video_patterns:
        for v_file in glob.glob(pattern, recursive=True):
            dest_name = f"{spec_stem}_{Path(v_file).name}"
            dest_path = root_dir / output_dir / dest_name
            shutil.copy2(v_file, dest_path)
            copied_videos.append(dest_path)

    print("\n" + "=" * 80)
    if test_passed:
        print("🎉 [E2E SUCCESS] Kịch bản kiểm thử E2E hoàn thành THÀNH CÔNG!")
    else:
        print("⚠️ [E2E WARNING/FAIL] Kịch bản kiểm thử E2E có lỗi hoặc chưa pass hoàn toàn.")

    if copied_videos:
        print("📹 CÁC CLIP QUAY MÀN HÌNH ĐÃ ĐƯỢC LƯU LẠI:")
        for v in copied_videos:
            print(f"   👉 Clip path: {v}")
    else:
        print("ℹ️ Không tìm thấy file video mới sinh ra (có thể test kết thúc quá sớm hoặc chưa cấu hình video recorder).")
    print("=" * 80 + "\n")

    return 0 if test_passed else 1

def main():
    parser = argparse.ArgumentParser(description="Chạy kiểm thử E2E Playwright Local có ghi clip màn hình")
    parser.add_argument("--spec", type=str, help="Đường dẫn file kịch bản E2E (vd: playwright/e2e/auth.spec.ts)")
    parser.add_argument("--check-services", action="store_true", help="Chỉ kiểm tra trạng thái các port service local")
    parser.add_argument("--no-video", action="store_true", help="Tắt tính năng quay video")
    parser.add_argument("--output-dir", type=str, default="artifacts/videos", help="Thư mục xuất file video clip")
    args = parser.parse_args()

    # Bước 1: Kiểm tra trạng thái các service
    print_service_status()

    if args.check_services and not args.spec:
        sys.exit(0)

    # Bước 2: Chạy test nếu có chỉ định spec
    if args.spec:
        exit_code = run_playwright_test(
            spec_path=args.spec,
            record_video=not args.no_video,
            output_dir=args.output_dir
        )
        sys.exit(exit_code)
    else:
        print("💡 Gợi ý: Chạy kịch bản cụ thể kèm quay video bằng lệnh:")
        print("   python3 scripts/run_e2e_local.py --spec e2e/auth.spec.ts\n")

if __name__ == "__main__":
    main()
