#!/usr/bin/env python3
# scripts/run_unit_tests.py
"""
Script chạy nhanh các file kiểm thử Unit & Integration Test trong thư mục tests/.
Hiển thị rõ ràng trạng thái ĐỎ (FAIL / RED) hoặc XANH (PASS / GREEN) phục vụ chuẩn TDD.
"""

import sys
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    tests_dir = root_dir / "tests"

    print("=" * 65)
    print("🧪 [UNIT & INTEGRATION TEST RUNNER] KIỂM THỬ TỰ ĐỘNG THEO TDD")
    print("=" * 65)

    test_files = list(tests_dir.glob("test_*.py"))
    if not test_files:
        print("ℹ️ Chưa có file test nào trong thư mục `tests/`.")
        print("💡 Hãy chạy Step 3 (`skills/STEP-3-write-test-code.md`) để sinh file test trước khi code.")
        sys.exit(0)

    print(f"🔍 Phát hiện {len(test_files)} file test cần chạy:")
    for tf in test_files:
        print(f"   • {tf.relative_to(root_dir)}")
    print("-" * 65)

    # Thử chạy bằng pytest trước, nếu không có thì fallback sang unittest
    try:
        cmd = ["pytest", str(tests_dir), "-v"]
        result = subprocess.run(cmd, cwd=str(root_dir))
        returncode = result.returncode
    except FileNotFoundError:
        print("ℹ️ Pytest không có trong PATH, chuyển sang chạy bằng `python3 -m unittest`...")
        cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]
        result = subprocess.run(cmd, cwd=str(root_dir))
        returncode = result.returncode

    print("=" * 65)
    if returncode == 0:
        print("🟢 [PASS / GREEN] TẤT CẢ UNIT & INTEGRATION TEST ĐÃ VƯỢT QUA!")
        print("🎉 Bạn đã hoàn thành code đạt chuẩn!")
    else:
        print("🔴 [FAIL / RED] TEST BỊ THẤT BẠI HOẶC CHƯA PASS.")
        print("💡 Nếu đang ở Bước 3 (TDD): Báo đỏ là HOÀN TOÀN ĐÚNG KỲ VỌNG vì chưa có code implement.")
        print("   Hãy tiếp tục chuyển sang Bước 4 (`STEP-4-implement-feature.md`) để viết code làm xanh test.")
    print("=" * 65)

    sys.exit(returncode)

if __name__ == "__main__":
    main()
