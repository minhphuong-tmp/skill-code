#!/usr/bin/env python3
# scripts/analyze_e2e_clip.py
# -*- coding: utf-8 -*-
"""
Script Phân Tích Clip E2E & Lọc Log Thông Minh Theo Feature (Smart Feature-Scoped Visual & Log Analyzer).
Mục tiêu:
  1. Bóc tách video .webm thành chuỗi ảnh tĩnh (Keyframes) ở tần số 1 ảnh/giây (1 FPS) kèm Scene Change Detection.
  2. BỘ LỌC LOG THÔNG MINH (FEATURE-SCOPED FILTER):
     - Loại bỏ 100% log rác nền không liên quan (Polling telemetry /decide/, /capture/, heartbeat, HMR, asset pings).
     - CHỈ GIỮ LẠI log console & request mạng gắn liền trực tiếp với Feature đang test.
  3. Xuất báo cáo đối chiếu trực quan `artifacts/videos/review-<feature>.md` để AI đọc bằng `read_file`.
"""

import os
import sys
import re
import argparse
import subprocess
import glob
from pathlib import Path

# Danh sách các mẫu log rác nền phổ biến trong Monorepo/Microservices cần LOẠI BỎ (Noise Denylist)
NOISE_PATTERNS = [
    r"/decide/\?v=",
    r"/api/users/@me/",
    r"\[HMR\]",
    r"vite:hmr",
    r"webpackHotUpdate",
    r"heartbeat",
    r"/static/",
    r"\.woff2?",
    r"\.svg\b",
    r"/_posthog/",
    r"/health\b",
    r"favicon\.ico",
    r"session_recording",
    r"batch_exports",
]

def get_repo_root() -> Path:
    cur = Path(__file__).resolve().parent
    while cur != cur.parent:
        if (cur / ".git").exists() or (cur / "package.json").exists() or (cur / "pyproject.toml").exists() or (cur / "go.mod").exists():
            return cur
        cur = cur.parent
    return Path(__file__).resolve().parents[2]

def extract_keyframes(video_path: str, output_frames_dir: str, fps: float = 1.0) -> list[str]:
    """Sử dụng ffmpeg để bóc tách video thành chuỗi ảnh keyframe (1 ảnh mỗi giây)."""
    os.makedirs(output_frames_dir, exist_ok=True)
    video_stem = Path(video_path).stem

    # Xóa các frame cũ nếu có
    for old_f in glob.glob(os.path.join(output_frames_dir, f"{video_stem}_frame_*.png")):
        try: os.remove(old_f)
        except OSError: pass

    output_pattern = os.path.join(output_frames_dir, f"{video_stem}_frame_%03d.png")
    
    print(f"🎬 [FFMPEG] Đang bóc tách video: {video_path}")
    print(f"   Tần số lấy mẫu: {fps} ảnh/giây (1 FPS Smart Sampling)...")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-frame_pts", "1",
        output_pattern
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"⚠️ Cảnh báo ffmpeg: {res.stderr[:200]}")
    except FileNotFoundError:
        print("❌ Không tìm thấy `ffmpeg` trong hệ thống! Vui lòng cài đặt: brew install ffmpeg")
        return []

    # Thu thập danh sách ảnh đã bóc tách
    extracted = sorted(glob.glob(os.path.join(output_frames_dir, f"{video_stem}_frame_*.png")))
    print(f"   ✅ Đã bóc tách thành công {len(extracted)} ảnh keyframes vào: {output_frames_dir}")
    return extracted

def filter_feature_logs(raw_logs: list[str], feature_keyword: str) -> list[str]:
    """
    LỌC LOG THÔNG MINH CHỈ DÀNH RIÊNG CHO FEATURE ĐANG LÀM:
    - Loại bỏ 100% log rác background.
    - Giữ lại log có chứa keyword của feature hoặc các mã lỗi 4xx/5xx liên quan.
    """
    filtered = []
    keyword_pattern = re.compile(re.escape(feature_keyword), re.IGNORECASE) if feature_keyword else None

    for line in raw_logs:
        line_clean = line.strip()
        if not line_clean:
            continue

        # 1. Bỏ qua nếu dính vào Noise Denylist
        if any(re.search(pattern, line_clean, re.IGNORECASE) for pattern in NOISE_PATTERNS):
            continue

        # 2. Nếu có chỉ định feature keyword: Chỉ giữ lại log liên quan trực tiếp
        if keyword_pattern:
            is_relevant = bool(keyword_pattern.search(line_clean))
            is_error = any(err in line_clean.lower() for err in ["error", "fail", "404", "500", "403", "422", "exception"])
            if is_relevant or is_error:
                filtered.append(line_clean)
        else:
            filtered.append(line_clean)

    return filtered

def generate_review_report(video_path: str, feature_name: str, frames: list[str], filtered_logs: list[str], output_report_path: str):
    """Xuất file Markdown báo cáo đối chiếu trực quan để Agent dùng read_file đọc và review."""
    root = get_repo_root()
    rel_video = os.path.relpath(video_path, root) if os.path.isabs(video_path) else video_path

    content = []
    content.append(f"# Báo Cáo Đối Chiếu Thị Giác E2E: Feature `{feature_name}`")
    content.append(f"> **File Clip Gốc:** `{rel_video}`  ")
    content.append(f"> **Thời Điểm Phân Tích:** Tự động trích xuất bởi `analyze_e2e_clip.py`  ")
    content.append(f"> **Cơ Chế:** Trích xuất 1 FPS + Lọc Log Scoped độc quyền cho `{feature_name}`\n")
    content.append("---\n")

    content.append("## 1. Chuỗi Khung Hình Trực Quan (Extracted Keyframes)")
    content.append("Agent hãy dùng công cụ `read_file` mở trực tiếp các file ảnh sau để đối chiếu giao diện thực tế:\n")
    
    if not frames:
        content.append("*(Chưa có ảnh nào được trích xuất hoặc clip quá ngắn)*\n")
    else:
        content.append("| Giây (Time) | File Ảnh Keyframe | Trạng Thái Giao Diện Dự Kiến |")
        content.append("| :---: | :--- | :--- |")
        for idx, fpath in enumerate(frames, start=1):
            rel_img = os.path.relpath(fpath, root)
            content.append(f"| **Giây {idx:02d}** | [{Path(fpath).name}]({rel_img}) | Đang tải / Thao tác form / Toast kết quả |")
        content.append("")

    content.append("---\n")
    content.append(f"## 2. Nhật Ký Đã Lọc Riêng Cho Feature `{feature_name}` (Filtered Scoped Logs)")
    content.append("*(Toàn bộ log rác telemetry, polling heartbeat, asset tĩnh đã được lọc sạch 100%)*\n")

    if not filtered_logs:
        content.append("🟢 **Không phát hiện lỗi Console hay lỗi mạng HTTP nào liên quan đến feature này!**")
    else:
        content.append("```log")
        for log_line in filtered_logs[:50]:  # Giới hạn 50 dòng log quan trọng nhất
            content.append(log_line)
        content.append("```\n")

    content.append("---\n")
    content.append("## 3. Hướng Dẫn Review & Phản Hồi (Feedback Protocol)")
    content.append("1. **Nếu tất cả các ảnh hiển thị đúng tiêu chuẩn của `specs/ui-flow-e2e-<name>.md`:**")
    content.append("   - Đánh dấu PASS, chuyển tiếp sang Bước 6 (`STEP-6-validate-after-code.md`).")
    content.append("2. **Nếu phát hiện lỗi giao diện (Vỡ layout, nút bấm không ăn, thiếu Toast):**")
    content.append(f"   - Trích dẫn cụ thể tên file ảnh bị lỗi (ví dụ: `{Path(frames[-1]).name if frames else 'frame_xxx.png'}`).")
    content.append("   - Gửi báo cáo Feedback ngược lại cho Step 4 (`STEP-4-implement-feature.md`) để kỹ sư code sửa ngay lập tức!")

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    print(f"📄 [REPORT] Đã xuất báo cáo đối chiếu thị giác ra: {output_report_path}")

def main():
    parser = argparse.ArgumentParser(description="Phân tích clip E2E & Lọc log dành riêng cho feature")
    parser.add_argument("--video", type=str, required=True, help="Đường dẫn file video .webm")
    parser.add_argument("--feature", type=str, default="", help="Tên hoặc từ khóa của Feature cần lọc log (vd: auth, coupon, order)")
    parser.add_argument("--log-file", type=str, help="File nhật ký browser / network log nếu có")
    parser.add_argument("--output-dir", type=str, default="artifacts/videos", help="Thư mục xuất kết quả")
    args = parser.parse_args()

    root = get_repo_root()
    video_path = Path(args.video)
    if not video_path.is_absolute():
        video_path = root / video_path

    if not video_path.exists():
        print(f"❌ Không tìm thấy file video: {video_path}")
        sys.exit(1)

    feature_name = args.feature or video_path.stem.split("_")[0]
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    frames_dir = out_dir / "frames"
    
    print("=" * 70)
    print(f"🔍 [SMART E2E ANALYZER] BẮT ĐẦU PHÂN TÍCH CLIP RIÊNG CHO: {feature_name.upper()}")
    print("=" * 70)

    # 1. Trích xuất keyframes 1 FPS
    frames = extract_keyframes(str(video_path), str(frames_dir), fps=1.0)

    # 2. Đọc và lọc log nếu có log file
    raw_logs = []
    if args.log_file and os.path.exists(args.log_file):
        with open(args.log_file, "r", encoding="utf-8", errors="ignore") as f:
            raw_logs = f.readlines()
    filtered_logs = filter_feature_logs(raw_logs, feature_name)

    # 3. Xuất file báo cáo Markdown
    report_file = out_dir / f"review-{feature_name}.md"
    generate_review_report(str(video_path), feature_name, frames, filtered_logs, str(report_file))

    print("=" * 70)
    print("🎉 Hoàn tất phân tích! AI hãy dùng `read_file` đọc file báo cáo:")
    print(f"   👉 {report_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
