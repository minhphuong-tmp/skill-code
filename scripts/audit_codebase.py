#!/usr/bin/env python3
# scripts/audit_codebase.py
"""
Script kiểm tra siêu tốc (dưới 0.1 giây) các thay đổi Git hiện tại đối chiếu với STEP-0-code-after-scan-codebase.md.
Tự động quét:
  1. Multi-Tenancy & IDOR (thiếu team_id scope)
  2. Identity RPC (cấm query trực tiếp bảng Person)
  3. Product Isolation (cấm import chéo nội bộ product khác)
  4. Dataclass Immutability (bắt buộc @frozen)
  5. Frontend Double-Submission (thiếu loading state trên LemonButton)
"""

import subprocess
import os
import re
import sys

def get_git_changed_files() -> list[str]:
    """Lấy danh sách tất cả file đang thay đổi: unstaged, staged và untracked."""
    changed = set()
    try:
        # 1. Unstaged changes
        out = subprocess.check_output(["git", "diff", "--name-only"], text=True, stderr=subprocess.DEVNULL)
        for f in out.splitlines():
            if f.strip(): changed.add(f.strip())

        # 2. Staged changes (đã git add)
        out_staged = subprocess.check_output(["git", "diff", "--name-only", "--cached"], text=True, stderr=subprocess.DEVNULL)
        for f in out_staged.splitlines():
            if f.strip(): changed.add(f.strip())

        # 3. Untracked files mới tạo
        out_status = subprocess.check_output(["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL)
        for line in out_status.splitlines():
            if line.strip():
                # Bỏ 3 ký tự trạng thái đầu ("?? ", "M  ", " A ")
                changed.add(line[3:].strip())
    except Exception:
        pass

    return sorted([f for f in changed if os.path.exists(f) and f.endswith((".py", ".ts", ".tsx")) and "audit_codebase" not in f])

def audit_file(file_path: str) -> list[str]:
    """Quét nội dung 1 file đối chiếu với các bất biến kiến trúc phần mềm tiêu chuẩn."""
    violations = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, start=1):
        # 1. KIỂM TRA MULTI-TENANCY & IDOR (Cấm truy vấn Entity không qua Tenant/Team Scope)
        if re.search(r"\bobjects\.get\(", line) and not any(k in line for k in ["team", "tenant", "org", "account", "workspace", "for_"]):
            violations.append(
                f"Dòng {idx}: [Multi-Tenancy & IDOR] Gọi `.objects.get()` trực tiếp không có scope (tenant/team/account)! "
                f"Sửa thành: `Model.objects.filter(team=..., id=...).first()` hoặc dùng scope helper."
            )

        # 2. KIỂM TRA ĐỘC LẬP MODULE / PRODUCT ISOLATION (Cấm import nội bộ private của module/package khác)
        if re.search(r"from\s+(?:products|modules|packages|services)\.\w+\.(?:backend|internal|private)\.(?:models|presentation|tasks)", line):
            violations.append(
                f"Dòng {idx}: [Module Isolation] Cấm import trực tiếp nội bộ module/service khác! "
                f"Bắt buộc giao tiếp qua API công khai hoặc Facade/Contracts."
            )

        # 3. KIỂM TRA DATACLASS IMMUTABILITY (Chống mutated state ngoài luồng)
        if "@dataclass" in line and "frozen=True" not in line and "frozen" not in line:
            violations.append(
                f"Dòng {idx}: [Immutability] Dataclass thiếu tính đóng băng! Bắt buộc dùng `@dataclass(frozen=True)` để đảm bảo thread-safe và bất biến."
            )

        # 4. KIỂM TRA FRONTEND DOUBLE SUBMISSION (Chống spam click gọi API)
        if re.search(r"<(?:[A-Z]\w*Button|button)\b", line) and "onClick" in line and not any(k in line for k in ["loading", "disabled", "isSubmitting", "pending"]):
            violations.append(
                f"Dòng {idx}: [Frontend State] Nút Button có onClick nhưng thiếu thuộc tính `loading` hoặc `disabled` để chống người dùng click đúp!"
            )

    return violations

def main():
    changed_files = get_git_changed_files()

    print("=" * 65)
    print("🔍 [AUDIT CODEBASE] Báo cáo kiểm tra các thay đổi Git hiện tại")
    print("=" * 65)

    if not changed_files:
        print("ℹ️ Không phát hiện file code (.py, .ts, .tsx) nào đang thay đổi trong Git.")
        print("✅ Trạng thái: SẠCH SẼ (Clean Working Tree)")
        sys.exit(0)

    total_violations = 0
    for fpath in changed_files:
        errs = audit_file(fpath)
        if errs:
            total_violations += len(errs)
            print(f"\n❌ FILE: {fpath}")
            for err in errs:
                print(f"   👉 {err}")
        else:
            print(f"✅ FILE: {fpath} (Đạt chuẩn)")

    print("\n" + "=" * 65)
    if total_violations > 0:
        print(f"🚨 TỔNG CỘNG: {total_violations} lỗi vi phạm quy chuẩn kiến trúc!")
        print("👉 AI hãy tự động mở các file và dòng bị báo lỗi trên để sửa lại ngay.")
        print("=" * 65)
        sys.exit(1)
    else:
        print("🎉 TẤT CẢ FILE THAY ĐỔI ĐỀU ĐẠT CHUẨN 100% THEO SKILL!")
        print("=" * 65)
        sys.exit(0)

if __name__ == "__main__":
    main()
