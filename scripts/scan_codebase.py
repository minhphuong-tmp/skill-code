#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chạy: python3 scripts/scan_codebase.py <thu_muc_codebase>
Tự động thực hiện trọn vẹn bộ ba thu hoạch:
  1. existing-guides.md: Thu hoạch AGENTS.md, CLAUDE.md, rules có sẵn qua repomix
  2. codebase-skeleton.md: Nén khung xương AST toàn bộ dự án qua repomix
  3. codebase-stats.md: Quét 12 bảng thông số định lượng từ mã nguồn thuần
"""
import os, re, sys, subprocess
from collections import Counter, defaultdict

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next", ".turbo", "target", "coverage"}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".rs", ".go"}
STOP_PARAMS = {"self", "cls", "args", "kwargs", "str", "int", "bool", "float", "any", "none", "string", "number", "boolean", "void", "dict", "list"}

def classify_case(stem: str) -> str:
    if re.match(r"^[a-z0-9]+(_[a-z0-9]+)+$", stem): return "snake_case"
    if re.match(r"^[a-z0-9]+(-[a-z0-9]+)+$", stem): return "kebab-case"
    if re.match(r"^[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*$", stem): return "camelCase"
    if re.match(r"^[A-Z][a-zA-Z0-9]+$", stem): return "PascalCase"
    return "single/other"

def scan_repo(root_dir: str, max_files: int = 25000) -> dict:
    folder_cases, role_locs = defaultdict(Counter), defaultdict(Counter)
    file_sufs, imports, bases, decs, fn_prefs, cls_sufs, params, registries = (Counter() for _ in range(8))
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = os.path.relpath(dirpath, root_dir)
        top_folder = rel_dir.split(os.sep)[0] if rel_dir != "." else "root"
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CODE_EXTS: continue
            count += 1
            if count > max_files: break
            stem = fname[:-len(ext)]
            folder_cases[top_folder][classify_case(stem.split(".")[0])] += 1
            m_suf = re.search(r"([A-Z][a-z0-9]+|_[a-z0-9]+|-[a-z0-9]+)$", stem)
            if m_suf: file_sufs[f"*{m_suf.group(1)}{ext}"] += 1
            rel_path = os.path.join(rel_dir, fname) if rel_dir != "." else fname
            norm_dir = re.sub(r"^([a-zA-Z0-9_-]+/[^/]+)/.*", r"\1/<module>", os.path.dirname(rel_path) or ".")
            try:
                content = open(os.path.join(dirpath, fname), encoding="utf-8", errors="ignore").read(100_000)
            except OSError: continue
            reg_hits = len(re.findall(r"(?:\.register\s*\(|urlpatterns\s*=|Router\(|app\.(?:use|get|post)\()", content))
            if reg_hits >= 6 and "test" not in rel_path.lower(): registries[rel_path] = reg_hits
            for mod in re.findall(r"(?:from\s+([\w.~/@-]+)\s+import|from\s+['\"]([@~\w./-]+)['\"])", content):
                imports[mod[0] or mod[1]] += 1
            for dec in re.findall(r"^\s*@([\w.]+)", content, re.M): decs[f"@{dec}"] += 1
            for cname, py_base, js_base in re.findall(r"\bclass\s+([A-Z]\w+)(?:\(([^)]+)\)|\s+extends\s+([\w.]+))?", content):
                m_c = re.search(r"([A-Z][a-z0-9]+)$", cname)
                if m_c:
                    cls_sufs[f"*{m_c.group(1)}"] += 1
                    role_locs[f"*{m_c.group(1)}"][f"{norm_dir}/{fname}"] += 1
                base_str = py_base or js_base or ""
                for b in base_str.split(","):
                    if b.strip(): bases[b.strip().split("[")[0]] += 1
            for fn, p_str in re.findall(r"\b(?:def|function)\s+([a-zA-Z_]\w*)\s*\(([^)]{0,200})\)", content):
                m_v = re.match(r"^_?([a-z]+)(?:_|[A-Z])", fn)
                if m_v: fn_prefs[f"{m_v.group(1)}_*"] += 1
                for p in p_str.split(","):
                    pn = p.strip().split(":")[0].split("=")[0].strip().lstrip("*")
                    if len(pn) >= 3 and pn.lower() not in STOP_PARAMS and re.match(r"^[a-z_]\w*$", pn):
                        params[pn] += 1
    return {
        "files": count,
        "folder_cases": folder_cases,
        "file_sufs": file_sufs.most_common(15),
        "fn_prefs": fn_prefs.most_common(20),
        "cls_sufs": cls_sufs.most_common(20),
        "params": params.most_common(25),
        "bases": bases.most_common(15),
        "decs": decs.most_common(15),
        "imports": imports.most_common(15),
        "role_locs": {k: v.most_common(3) for k, v in role_locs.items()},
        "registries": registries.most_common(15)
    }

def format_stats_markdown(stats: dict) -> str:
    lines = [
        "# Thống Kê Định Lượng Codebase Thật (`codebase-stats.md`)\n",
        f"- Tổng số files mã nguồn được quét: **{stats['files']}** files\n",
        "## 1. Quy ước đặt tên file theo thư mục (Folder Case Distributions)",
    ]
    for folder, cases in stats["folder_cases"].items():
        lines.append(f"- **{folder}/**: {dict(cases)}")

    lines.append("\n## 2. Top Hậu tố tên File đặc trưng")
    for suf, c in stats["file_sufs"]: lines.append(f"- `{suf}`: {c} files")

    lines.append("\n## 3. Top Tiền tố động từ của tên Hàm (Function Verb Prefixes)")
    for pfx, c in stats["fn_prefs"]: lines.append(f"- `{pfx}`: {c} lần")

    lines.append("\n## 4. Top Hậu tố của tên Class / Interface")
    for suf, c in stats["cls_sufs"]: lines.append(f"- `{suf}`: {c} lần")

    lines.append("\n## 5. Top Tên biến / Tham số Domain cố định")
    for p, c in stats["params"]: lines.append(f"- `{p}`: {c} lần")

    lines.append("\n## 6. Top Base Classes & Mixins phổ biến")
    for b, c in stats["bases"]: lines.append(f"- `{b}`: {c} lần")

    lines.append("\n## 7. Top Decorators (@...)")
    for d, c in stats["decs"]: lines.append(f"- `{d}`: {c} lần")

    lines.append("\n## 8. Top Modules được Import nhiều nhất")
    for imp, c in stats["imports"]: lines.append(f"- `{imp}`: {c} lần")

    lines.append("\n## 9. File Registries trung tâm")
    for reg, c in stats["registries"]: lines.append(f"- `{reg}`: {c} registrations")

    return "\n".join(lines)

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

def export_existing_guides(root_dir: str, out_file: str = "existing-guides.md"):
    """Bước 1: Thu hoạch toàn bộ tài liệu quy ước, AGENTS.md, CLAUDE.md có sẵn."""
    print(f"📚 [1/3] Đang thu hoạch hướng dẫn & skills có sẵn ra: {out_file} ...")
    cmd = [
        "repomix", root_dir,
        "--include", "**/AGENTS.md,**/CLAUDE.md,**/.cursorrules,**/.cursor/rules/**,**/.agents/**,**/docs/architecture*,**/docs/internal/*",
        "--style", "markdown",
        "--output", out_file
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            print(f"   ✅ Đã tạo {out_file} ({os.path.getsize(out_file)} bytes)")
        else:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("# Existing Guides\n\n*(Không tìm thấy tài liệu hướng dẫn AI có sẵn trong dự án này)*\n")
            print(f"   ℹ️ Không có tài liệu sẵn, đã tạo {out_file} placeholder.")
    except Exception as e:
        print(f"   ⚠️ Lỗi khi chạy repomix thu hoạch guides: {e}")

def export_codebase_skeleton(root_dir: str, out_file: str = "codebase-skeleton.md"):
    """Bước 2: Nén khung xương AST mã nguồn bằng Tree-sitter qua repomix."""
    print(f"🦴 [2/4] Đang nén khung xương mã nguồn AST ra: {out_file} ...")
    cmd = [
        "repomix", root_dir,
        "--compress",
        "--style", "markdown",
        "--remove-comments",
        "--ignore", "**/node_modules/**,**/dist/**,**/build/**,**/.next/**,**/.turbo/**,**/target/**,**/.git/**,**/.venv/**,**/coverage/**,codebase-skeleton.md",
        "--output", out_file
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(out_file):
            size_mb = os.path.getsize(out_file) / (1024 * 1024)
            print(f"   ✅ Đã tạo {out_file} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"   ⚠️ Lỗi khi chạy repomix nén skeleton: {e}")

def export_database_schema(root_dir: str, out_file: str = "database-schema.md"):
    """Bước 4: Bóc tách toàn bộ bản đồ Cơ Sở Dữ Liệu: PostgreSQL (Django ORM) & ClickHouse (Analytics)."""
    print(f"🗄️  [4/4] Đang bóc tách bản đồ Cơ Sở Dữ Liệu (Database Schema) ra: {out_file} ...")
    
    pg_models = []
    ch_tables = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if any(x in dirpath for x in [".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"]):
            continue
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(fpath, root_dir)

            # 1. Bóc tách Django ORM Models (PostgreSQL)
            if fname.endswith(".py") and ("model" in fname or "models" in dirpath):
                try:
                    content = open(fpath, encoding="utf-8", errors="ignore").read()
                    classes = re.finditer(r"class\s+([A-Z][a-zA-Z0-9_]+)\s*\(([^)]*Model[^)]*)\):", content)
                    for cl in classes:
                        cname = cl.group(1)
                        tbl_match = re.search(r"db_table\s*=\s*[\"'\']([^\"'\']+)[\"'\']", content[cl.start():cl.start()+2500])
                        tbl_name = tbl_match.group(1) if tbl_match else cname.lower()
                        
                        class_snippet = content[cl.start():cl.start()+3500]
                        fks = re.findall(r"(\w+)\s*=\s*(?:models\.)?ForeignKey\s*\(\s*[\"'\']?([A-Za-z0-9_]+)[\"'\']?", class_snippet)
                        has_tenant = any(t in fk[0].lower() for fk in fks for t in ["tenant", "team", "org", "account", "workspace"]) or any(t in class_snippet for t in ["team_id", "tenant_id", "org_id", "workspace_id"])
                        
                        pg_models.append({
                            "model": cname,
                            "table": tbl_name,
                            "file": rel_path,
                            "fks": [f"{f[0]} -> {f[1]}" for f in fks[:3]],
                            "tenant_scoped": has_tenant
                        })
                except Exception:
                    pass

            # 2. Bóc tách SQL Migrations & Schemas
            elif fname.endswith(".sql") and any(k in dirpath for k in ["migrations", "sql", "schemas"]):
                try:
                    content = open(fpath, encoding="utf-8", errors="ignore").read()
                    matches = re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:[\w]+\.)?([a-zA-Z0-9_]+)", content, re.IGNORECASE)
                    for m in matches:
                        is_tenant = any(t in content.lower() for t in ["team_id", "tenant_id", "org_id", "account_id"])
                        ch_tables.add((m, rel_path, is_tenant))
                except Exception:
                    pass

    # Sắp xếp và phân loại
    pg_models.sort(key=lambda x: x["table"])
    sorted_ch = sorted(list(ch_tables), key=lambda x: x[0])

    # Tạo nội dung Markdown
    lines = []
    lines.append("# BẢN ĐỒ CƠ SỞ DỮ LIỆU & CÁC BẢNG TRONG HỆ THỐNG (DATABASE SCHEMA MAP)")
    lines.append("> Tài liệu sinh tự động từ script `scan_codebase.py` để AI tra cứu cấu trúc bảng trước khi code.\n")
    lines.append("---\n")

    lines.append("## 1. Tổng Quan Kiến Trúc Lưu Trữ (Discovered Databases)")
    lines.append("| Tầng Lưu Trữ | Tổng Số Bảng / Models | Mục Đích & Phạm Vi Quét |")
    lines.append("| :--- | :---: | :--- |")
    if pg_models:
        lines.append(f"| **ORM Data Models** | **{len(pg_models)}** | Các thực thể nghiệp vụ quan hệ (Relational Models / ORM) |")
    if sorted_ch:
        lines.append(f"| **Raw SQL Schemas / Migrations** | **{len(sorted_ch)}** | Bảng dữ liệu định nghĩa qua file DDL SQL |")
    if not pg_models and not sorted_ch:
        lines.append("| **Data Layer** | 0 | Không phát hiện file Model ORM hoặc SQL Schema tĩnh |")
    lines.append("\n---\n")

    lines.append("## 2. Các Thực Thể Dữ Liệu Cốt Lõi Phát Hiện Được (Core Entity Dictionary)")
    lines.append("| Tên Bảng (db_table) | Model Name | Scoped Tenant/Org? | Quan Hệ Khóa Ngoại (Foreign Keys) | File Định Nghĩa |")
    lines.append("| :--- | :--- | :---: | :--- | :--- |")
    # Hiển thị các model quan trọng nhất (ưu tiên có khóa ngoại hoặc tenant scope)
    core_models = [m for m in pg_models if m.get("tenant_scoped") or m.get("fks")][:15]
    if not core_models:
        core_models = pg_models[:15]
    for m in core_models:
        fks_str = ", ".join(m["fks"]) if m["fks"] else "None"
        scoped_str = "✅ Có" if m.get("tenant_scoped") else "Global"
        lines.append(f"| `{m['table']}` | `{m['model']}` | {scoped_str} | {fks_str} | `{m['file']}` |")
    lines.append("\n---\n")

    lines.append(f"## 3. Danh Mục Chi Tiết Toàn Bộ {len(pg_models)} Models ORM")
    lines.append("| Tên Bảng Thật (`db_table`) | Model Name | Tenant Scoped? | Khóa Ngoại (Foreign Keys) | File Định Nghĩa |")
    lines.append("| :--- | :--- | :---: | :--- | :--- |")
    for m in pg_models:
        fks_str = ", ".join(m["fks"]) if m["fks"] else "None"
        scoped_str = "✅ Có" if m.get("tenant_scoped") else "Global"
        lines.append(f"| `{m['table']}` | `{m['model']}` | {scoped_str} | {fks_str} | `{m['file']}` |")
    for m in pg_models:
        fks_str = ", ".join(m["fks"]) if m["fks"] else "None"
        team_str = "✅ Có" if m["team_scoped"] else "❌ Không"
        lines.append(f"| `{m['table']}` | `{m['model']}` | {team_str} | `{fks_str}` | `{m['file']}` |")

    lines.append("\n---\n")
    lines.append(f"## 4. Danh Mục Toàn Bộ {len(sorted_ch)} Bảng ClickHouse (Analytical Schemas)")
    lines.append("| Tên Bảng ClickHouse | Team Scoped? | File Schema SQL / Migration |")
    lines.append("| :--- | :---: | :--- |")
    for t in sorted_ch:
        t_team = "✅ Có" if t[2] else "❌ Không"
        lines.append(f"| `{t[0]}` | {t_team} | `{t[1]}` |")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"   ✅ Đã bóc tách thành công {len(pg_models)} bảng PostgreSQL & {len(sorted_ch)} bảng ClickHouse ra: {out_file}")

def main():
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "."
    stats_out = "codebase-stats.md"
    guides_out = "existing-guides.md"
    skeleton_out = "codebase-skeleton.md"
    schema_out = "database-schema.md"
    stats_only = "--stats-only" in sys.argv

    print("=" * 65)
    print(f"🚀 [SCAN CODEBASE] Bắt đầu quét tự động toàn diện: {root}")
    print("=" * 65)

    if not stats_only:
        ensure_repomix()
        # 1. Thu hoạch guides
        export_existing_guides(root, guides_out)
        # 2. Nén skeleton AST (nếu chưa có hoặc file rỗng thì chạy nén)
        if not os.path.exists(skeleton_out) or os.path.getsize(skeleton_out) == 0:
            export_codebase_skeleton(root, skeleton_out)
        else:
            print(f"🦴 [2/4] Đã có sẵn {skeleton_out} ({os.path.getsize(skeleton_out)/(1024*1024):.1f} MB), tái sử dụng.")

    # 3. Quét số liệu định lượng
    print(f"📊 [3/4] Đang quét 12 bảng thông số định lượng ra: {stats_out} ...")
    stats = scan_repo(root)
    md_content = format_stats_markdown(stats)
    with open(stats_out, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"   ✅ Đã quét {stats['files']} files thành công ra: {stats_out}")

    # 4. Bóc tách bản đồ Cơ sở dữ liệu (Database Schema Map)
    export_database_schema(root, schema_out)

    print("=" * 65)
    print("🎉 HOÀN TẤT BỘ TỨ TÀI NGUYÊN QUÉT:")
    if not stats_only:
        print(f"   1. {guides_out}")
        print(f"   2. {skeleton_out}")
    print(f"   3. {stats_out}")
    print(f"   4. {schema_out} (Bản đồ toàn bộ bảng Database)")
    print("👉 AI (hoặc Subagent) sử dụng 4 file này để đúc kết trọn bộ 4 tài liệu kỹ năng:")
    print("   1. 00-phan-tich-codebase.md (Báo cáo giải phẫu hệ thống)")
    print("   2. SKILL Code/STEP-0-code-after-scan-codebase.md (Cẩm nang điều lệnh kiến trúc)")
    print("   3. SKILL Code/scripts/audit_codebase.py (Script kiểm tra Git Diff siêu tốc)")
    print("   4. SKILL Code/STEP-6-validate-after-code.md (Kỹ năng tự kiểm duyệt mã nguồn)")
    print("=" * 65)

if __name__ == "__main__":
    main()
