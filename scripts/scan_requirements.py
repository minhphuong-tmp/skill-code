#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/scan_requirements.py <thu_muc_codebase>
Tự động thu hoạch toàn bộ dữ liệu nghiệp vụ của dự án:
  1. raw-requirements-docs.md: Gom toàn bộ SKILLS có sẵn, rules, docs, rfcs, specs, PRD, api-specs qua repomix
  2. raw-requirements-domain.md: Bóc tách Domain Entities, State Machines (Enum trạng thái) và Business Test Scenarios từ mã nguồn
"""
import os, re, sys, subprocess
from collections import Counter, defaultdict

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", ".turbo", "target", "coverage"}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".go", ".rs"}

def ensure_repomix():
    """Kiểm tra repomix đã cài đặt chưa; nếu chưa thì tự động cài đặt qua npm."""
    try:
        subprocess.run(["repomix", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        print("📦 Chưa tìm thấy repomix, đang tự động cài đặt qua: npm install -g repomix ...")
        try:
            subprocess.run(["npm", "install", "-g", "repomix"], check=True)
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể cài đặt repomix tự động: {e}. Vui lòng cài thủ công: npm install -g repomix")

def harvest_requirements_docs(root_dir: str, out_file: str = "raw-requirements-docs.md"):
    """Cỗ máy 1: Gom toàn bộ SKILLS có sẵn, rules, RFCs, specs, PRD, docs bằng Repomix."""
    print(f"📚 [1/2] Đang thu hoạch Skills, Rules, Specs & Tài liệu nghiệp vụ ra: {out_file} ...")
    cmd = [
        "repomix", root_dir,
        "--include", (
            "**/AGENTS.md,**/CLAUDE.md,**/.cursorrules,**/.cursor/rules/**,"
            "**/.agents/skills/**,**/skills/**,"
            "**/docs/**,**/rfcs/**,**/specs/**,**/proposals/**,**/design-docs/**,**/PRD/**,"
            "**/*.feature,**/api-spec*.*,**/openapi*.*,**/swagger*.*"
        ),
        "--style", "markdown",
        "--remove-comments",
        "--ignore", "**/node_modules/**,**/dist/**,**/build/**,**/.next/**,**/.turbo/**,**/target/**,**/.git/**,**/.venv/**,**/coverage/**,codebase-skeleton.md",
        "--output", out_file
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            size_kb = os.path.getsize(out_file) / 1024
            print(f"   ✅ Đã tạo {out_file} ({size_kb:.1f} KB)")
        else:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("# Raw Requirements & Docs\n\n*(Không tìm thấy tài liệu docs/specs hoặc skills có sẵn trong dự án này)*\n")
            print(f"   ℹ️ Không có tài liệu sẵn, đã tạo {out_file} placeholder.")
    except Exception as e:
        print(f"   ⚠️ Lỗi khi chạy repomix thu hoạch docs/skills: {e}")

def scan_domain_intelligence(root_dir: str, max_files: int = 25000) -> dict:
    """Cỗ máy 2: Bóc tách Domain Models, State Machines và Business Test Scenarios từ code."""
    domain_models = Counter()
    state_enums = defaultdict(list)
    business_test_rules = defaultdict(list)
    count = 0

    re_model_py = re.compile(r"\bclass\s+([A-Z]\w+)\s*\((?:[^)]*Model|[^)]*Base|[^)]*Entity)[^)]*\):")
    re_model_ts = re.compile(r"\b(?:class|interface|type)\s+([A-Z]\w+)\s+(?:extends\s+(?:Model|Entity|BaseEntity)|implements\s+Entity)")
    re_enum_py = re.compile(r"\bclass\s+([A-Z]\w*(?:Status|State|Type|Kind|Category|Choices|Enum))\s*\((?:[^)]*TextChoices|[^)]*IntegerChoices|[^)]*Enum)[^)]*\):(?:\n\s+[\"'].*?[\"'])?((?:\n\s+[A-Z_]+\s*=\s*.*?)+)")
    re_enum_ts = re.compile(r"\benum\s+([A-Z]\w*(?:Status|State|Type|Kind|Category|Choices)?)\s*\{([^}]+)\}")
    re_test_biz_py = re.compile(r"\bdef\s+(test_(?:cannot|should|requires|must|rejects|validates|expired|forbidden|unauthorized|denied|only|prevents)_\w+)\s*\(")
    re_test_biz_js = re.compile(r"\b(?:it|test)\s*\(\s*['\"](should\s+(?:not\s+|require\s+|reject\s+|prevent\s+|allow\s+|throw\s+|forbid\s+|enforce\s+).*?)['\"]")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = os.path.relpath(dirpath, root_dir)
        is_test_dir = "test" in rel_dir.lower() or "spec" in rel_dir.lower()

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXTS: continue
            count += 1
            if count > max_files: break
            filepath = os.path.join(dirpath, fname)
            rel_file = os.path.join(rel_dir, fname) if rel_dir != "." else fname

            try:
                content = open(filepath, "r", encoding="utf-8", errors="ignore").read(60_000)
            except OSError:
                continue

            # 1. Bóc tách Domain Models
            if not is_test_dir:
                for m in re_model_py.findall(content): domain_models[m] += 1
                for m in re_model_ts.findall(content): domain_models[m] += 1

                # 2. Bóc tách State Machine (Enums)
                for cname, body in re_enum_py.findall(content):
                    vals = [line.strip().split("=")[0].strip() for line in body.splitlines() if line.strip() and not line.strip().startswith("#")]
                    if vals: state_enums[f"{cname} ({rel_file})"] = vals[:10]

                for cname, body in re_enum_ts.findall(content):
                    vals = [line.strip().split("=")[0].split(",")[0].strip() for line in body.splitlines() if line.strip() and not line.strip().startswith("//")]
                    if vals: state_enums[f"{cname} ({rel_file})"] = vals[:10]

            # 3. Bóc tách Business Test Scenarios
            if is_test_dir:
                for fn in re_test_biz_py.findall(content):
                    human_name = fn.replace("test_", "").replace("_", " ")
                    business_test_rules[rel_file].append(human_name)
                for fn in re_test_biz_js.findall(content):
                    business_test_rules[rel_file].append(fn)

    return {
        "files_scanned": count,
        "models": domain_models.most_common(40),
        "state_enums": state_enums,
        "business_test_rules": business_test_rules
    }

def format_domain_requirements_markdown(data: dict) -> str:
    lines = [
        "# Raw Domain Intelligence & Business Invariants",
        f"\n> Báo cáo trích xuất tự động từ {data['files_scanned']} files mã nguồn.",
        "\n---",
        "\n## 1. Top Domain Entities & Thực Thể Nghiệp Vụ Chính",
        "Danh sách các thực thể kinh doanh cốt lõi phát hiện từ Models/Schemas:",
    ]
    for name, freq in data["models"]:
        lines.append(f"- **`{name}`** (Khai báo/kế thừa {freq} lần)")

    lines.append("\n---")
    lines.append("\n## 2. Máy Trạng Thái & Vòng Đời Dữ Liệu (State Machines & Enums)")
    lines.append("Các trạng thái hợp lệ của thực thể phát hiện từ Enum/Choices trong code:")
    for ename, vals in list(data["state_enums"].items())[:30]:
        val_str = " ➔ ".join(vals)
        lines.append(f"\n### `{ename}`")
        lines.append(f"- Các trạng thái: `{val_str}`")

    lines.append("\n---")
    lines.append("\n## 3. Các Quy Tắc Nghiệp Vụ Cấm Kỵ & Tiêu Chí Nghiệm Thu (Trích từ Test Scenarios)")
    lines.append("Các hành vi nghiệp vụ bắt buộc được hệ thống bảo vệ trong test suites:")
    for tfile, tests in list(data["business_test_rules"].items())[:25]:
        lines.append(f"\n### 📁 `{tfile}`")
        for t in tests[:8]:
            lines.append(f"- [x] Nghiệp vụ: *{t}*")

    return "\n".join(lines)

def export_domain_requirements(root_dir: str, out_file: str = "raw-requirements-domain.md"):
    print(f"📊 [2/2] Đang bóc tách Domain Models, State Machines & Test Rules ra: {out_file} ...")
    data = scan_domain_intelligence(root_dir)
    md_content = format_domain_requirements_markdown(data)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    size_kb = os.path.getsize(out_file) / 1024
    print(f"   ✅ Đã xuất {data['files_scanned']} files thành công ra: {out_file} ({size_kb:.1f} KB)")

def main():
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "."
    docs_out = "raw-requirements-docs.md"
    domain_out = "raw-requirements-domain.md"

    print("=" * 65)
    print(f"🚀 [SCAN REQUIREMENTS] Quét toàn diện Nghiệp Vụ & Domain: {root}")
    print("=" * 65)

    ensure_repomix()
    # 1. Gom Docs & Skills
    harvest_requirements_docs(root, docs_out)
    # 2. Bóc tách Domain & State Machine từ code
    export_domain_requirements(root, domain_out)

    print("=" * 65)
    print("🎉 HOÀN TẤT BỘ ĐÔI TÀI NGUYÊN NGHIỆP VỤ:")
    print(f"   1. {docs_out} (Skills có sẵn, Rules, Specs, RFCs, PRD)")
    print(f"   2. {domain_out} (Domain Entities, State Machines, Test Rules)")
    print("👉 AI (hoặc Subagent) sử dụng 2 file này để đúc kết:")
    print("   📄 skills/STEP-0-requirement-after-scan-codebase.md")
    print("=" * 65)

if __name__ == "__main__":
    main()
