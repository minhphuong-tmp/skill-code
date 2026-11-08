---
name: scan-codebase
description: 'Meta-Skill quét tự động bất kỳ Codebase nào bằng bộ ba công cụ: (1) Thu hoạch hướng dẫn/skills có sẵn (existing-guides.md qua Repomix), (2) Nén khung xương AST Repomix (codebase-skeleton.md), và (3) Script thống kê định lượng (codebase-stats.md) để Subagent đúc kết trọn gói Bộ Tứ tự động hóa: Báo cáo Kiến trúc (00-phan-tich-codebase.md), Cẩm nang kiến trúc (skills/STEP-0-code-after-scan-codebase.md), Script kiểm duyệt Git Diff siêu tốc (scripts/audit_codebase.py) và Kỹ năng tự kiểm duyệt mã nguồn sau khi code (skills/STEP-6-validate-after-code.md).'
---

# META-SKILL: QUÉT CODEBASE & TỰ ĐỘNG ĐÚC KẾT BỘ SKILL RIÊNG CHO DỰ ÁN (`/scan-codebase`)

Mục đích của Skill này là biến **bất kỳ một dự án phần mềm nào** (dù lớn hàng chục ngàn file, viết bằng Python, TypeScript/Node.js, Rust, Go, Java...) thành một hệ thống tự trị khép kín gồm **Báo cáo kiến trúc + Cẩm nang mệnh lệnh + Script kiểm duyệt tự động** chuẩn xác 100% theo số liệu thực tế và tri thức sẵn có của dự án đó.

Quy trình áp dụng mô hình **"Tam Giác Tri Thức" (The 3-Pillar Knowledge Triangle)**: Kết hợp giữa *(1) Ý đồ & luật cấm có sẵn trong tài liệu* + *(2) Khung xương AST mã nguồn thật* + *(3) Bằng chứng số liệu định lượng*.

Khi người dùng yêu cầu: *"Quét codebase này tạo bộ skill"*, *"Chạy skill scan-codebase"*, hoặc *"Tạo STEP-0-code-after-scan-codebase.md cho dự án này"*, AI **BẮT BUỘC** thực hiện tuần tự **3 Bước** dưới đây:

---

## Bước 1: Chạy 1 Lệnh Duy Nhất Để Thu Hoạch Bộ Ba Tài Nguyên

AI chỉ cần thực thi đúng 1 lệnh duy nhất:
```bash
python3 scripts/scan_codebase.py <thu_muc_du_an>
```

Script `scripts/scan_codebase.py` đã đóng gói trọn gói toàn bộ công cụ và tự động xuất ra 4 file:
1. **Thu hoạch tài liệu & skills có sẵn (`existing-guides.md`):** Tự động gọi `repomix` gom toàn bộ `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.agents/` và tài liệu nội bộ của tác giả.
2. **Nén khung xương AST mã nguồn (`codebase-skeleton.md`):** Tự động gọi `repomix` dùng Tree-sitter nén toàn bộ chữ ký `class/function/interface` (giảm ~80% token). Nếu file đã tồn tại sẵn, script tự động tái sử dụng để tiết kiệm thời gian.
3. **Quét 12 bảng thông số định lượng (`codebase-stats.md`):** Quét mã nguồn thuần để đo đếm quy ước đặt tên file, hậu tố class, tiền tố hàm, từ điển biến domain và file registries trung tâm.
4. **Bóc tách bản đồ Cơ Sở Dữ Liệu (`database-schema.md`):** Tự động phát hiện và quét các ORM Models / SQL Schemas / Migrations của dự án (ví dụ: Django, Prisma, TypeORM, SQLAlchemy, GORM, ActiveRecord, ClickHouse...) để lập danh mục chi tiết mọi bảng dữ liệu, trường khóa chính, khóa ngoại và phạm vi phân lập Multi-Tenant (nếu có).

---

## Bước 2: Chọn "3 Cụm File Mẫu Chuẩn Mực Nhất" (Golden Samples) Để Đọc Sâu

Sau khi có đủ 3 file từ Bước 1 (`existing-guides.md`, `codebase-skeleton.md`, `codebase-stats.md`), AI **không đọc tràn lan** mà đối chiếu giữa hướng dẫn có sẵn và số liệu thống kê để chọn đúng **3 nhóm file cốt lõi** đọc trực tiếp:
1. **Nhóm File Nút Thắt Trung Tâm (Top Dependency Hubs):**
   - File xử lý lỗi chuẩn (`exceptions.py` / `service-error.ts`).
   - File định tuyến & phân quyền gốc (`routing.py` / `scopes.py` / `auth.ts`).
   - File Base Model / Mixin & Logger (`models/` / `logger.ts`).
2. **Nhóm 2–3 Module Tính Năng Đầy Đủ Nhất (Golden Feature Modules):**
   - Chọn 2 module có đầy đủ các file theo đúng "Khuôn mẫu giải phẫu" ở Bảng 10 của `codebase-stats.md` (gồm đầy đủ `models`, `views/controllers`, `serializers/DTOs`, `facade/services`, `frontend logic/scene`, `tests`).
3. **Nhóm File Khởi Chạy & Công Cụ Kiểm Thử:**
   - Đọc `package.json`, `pyproject.toml`, `docker-compose.dev.yml`, `bin/start` hoặc `Makefile` để biết chính xác hệ thống khởi chạy những services nào ở local và lệnh chạy test/linter chuẩn là gì.

*(Nếu dự án có nhiều tầng Backend / Frontend / Worker tách biệt, có thể cử 2–3 `research` Subagents đọc song song các nhóm file này để tiết kiệm thời gian).*

---

## Bước 3: Subagent Đúc Kết Trọn Gói "Bộ Tứ Tự Động Hóa" (The 4 Core Artifacts)

> [!IMPORTANT]
> ### Cơ Chế Ủy Quyền Cho Subagent (Subagent Delegation Pattern - Chống Tràn Context Window)
> Trong các dự án vừa và lớn, việc đọc toàn bộ `existing-guides.md`, `codebase-skeleton.md`, `codebase-stats.md` kết hợp duyệt sâu các file code mẫu có thể ngốn hàng chục nghìn tokens.
> **Quy tắc sống còn:** Để bảo vệ **Session chính (Orchestrator)** không bao giờ bị quá tải hoặc tràn bộ nhớ (Out-of-Context), Session chính **phải ủy quyền toàn bộ tác vụ phân tích và sinh mã nguồn cho Subagent** (`invoke_subagent`):
> 1. **Session chính (AI Main - Chỉ giao việc, KHÔNG đọc file):** Tuyệt đối **KHÔNG mở đọc các file dữ liệu nặng** vào context của mình. Session chính chỉ gọi `invoke_subagent` giao toàn quyền cho Subagent kèm đường dẫn các file đã sinh ra ở Bước 1.
> 2. **Subagent (Worker thực thi độc lập - Cả ĐỌC lẫn VIẾT):** Subagent chạy trong ngữ cảnh sandbox riêng biệt:
>    - **Tự mở đọc:** `existing-guides.md`, `codebase-stats.md` và tự chọn mở đọc 3–5 file mã nguồn thật đại diện trên ổ đĩa.
>    - **Tự tổng hợp & Tự ghi:** Tự đúc kết tri thức và trực tiếp dùng công cụ `write_file` để xuất trọn gói **Bộ Tứ 4 file** xuống ổ đĩa:
>      1. `00-phan-tich-codebase.md`: Báo cáo giải phẫu hệ thống.
>      2. `skills/STEP-0-code-after-scan-codebase.md`: Cẩm nang mệnh lệnh kiến trúc (5 Mục chuẩn mực).
>      3. `scripts/audit_codebase.py`: Script Python kiểm tra Git Diff siêu tốc (<0.1s), tự sinh các regex bắt lỗi bám sát theo các bất biến ở Mục 2 của cẩm nang.
>      4. `skills/STEP-6-validate-after-code.md`: Kỹ năng kiểm duyệt tự động hướng dẫn AI gọi script trên để tự sửa lỗi trước khi hoàn thành.
> 3. **Phản hồi siêu nhẹ:** Subagent chỉ gửi trả về cho Session chính 1 tin nhắn ngắn tóm tắt (3–5 gạch đầu dòng và danh sách 4 file đã tạo). Session chính giữ được 95%+ context window sạch sẽ cho các tác vụ lập trình tiếp theo!

Từ tri thức có sẵn trong **`existing-guides.md`**, số liệu định lượng ở `codebase-stats.md` và mẫu code thật ở Bước 2, Subagent kết hợp cả 3 nguồn chân lý để tạo ra **Bộ Tứ 4 file** với cấu trúc bắt buộc sau:

### File 1: `00-phan-tich-codebase.md` (Báo Cáo Giải Phẫu Kiến Trúc)
- Tổng quan công nghệ (Tech Stack), các services chạy ở local (DB, Cache, Queue, Workers) và sơ đồ cây thư mục.
- Sơ đồ luồng dữ liệu (Mermaid Flowchart) từ Client ➔ Gateway/Controller ➔ Service/Facade ➔ Database/Queue.
- Phân tích các điểm cốt lõi của dự án (Multi-tenancy, Quản lý trạng thái, Xử lý bất đồng bộ, Bảo mật).

### File 2: `skills/STEP-0-code-after-scan-codebase.md` (Cẩm Nang Mệnh Lệnh Kiến Trúc)
File `STEP-0-code-after-scan-codebase.md` **BẮT BUỘC phải có đủ 5 Mục sau** (kế thừa toàn bộ luật từ `existing-guides.md` và kèm con số thống kê thật trích từ `codebase-stats.md`):

1. **Mục 1 – Bản Đồ Vị Trí Viết Code (Where-To-Write-Code Map):**
   - **1.1. Sơ đồ giải phẫu chuẩn của 1 Feature Module:** Chỉ rõ từng file trong module làm nhiệm vụ gì, file nào là code sinh tự động cấm sửa tay.
   - **1.2. Bảng tra cứu nhanh *"Muốn viết X thì mở đúng File/Folder nào & Đăng ký (Wiring) ở File Trung Tâm nào?"*:** (Model, Serializer/DTO, API View/Controller, Facade/Service, Background Task, UI State, Scene/Page).
   - **1.3. Thứ tự viết code từ trên xuống dưới bên trong 1 File (Intra-file Section Order):** Quy định rõ trong 1 file Backend và 1 file Frontend thì đặt Imports, Types, Serializers, Class/Logic theo thứ tự nào.
2. **Mục 2 – Các Bất Biến Kiến Trúc & Quy Chuẩn Đặt Tên (Core Invariants & Naming Conventions):**
   - Các luật sống còn của dự án (kế thừa từ `existing-guides.md`: cô lập dữ liệu tenant, ranh giới giữa các module, quản lý transaction, gọi mạng ra ngoài).
   - **Quy chuẩn Đặt tên định lượng (Trích từ `codebase-stats.md`):**
     - Kiểu đặt tên file theo từng thư mục (`snake_case`, `kebab-case`, `PascalCase`, `camelCase`) và các hậu tố file chuẩn.
     - Top tiền tố động từ của tên Hàm (`get_`, `fetch_`, `build_`, `create_`, `validate_`, `is_`, `has_`...).
     - Top hậu tố của tên Class / Interface (`*ViewSet`, `*Serializer`, `*Service`, `*DTO`, `*Props`, `*Error`...).
     - **Từ điển tên biến nghiệp vụ cố định (Canonical Domain Vocabulary):** Liệt kê các tên biến chuẩn của dự án và những từ đồng nghĩa bị cấm dùng lệch.
     - Top Base Classes, Mixins và Decorators bắt buộc phải tái sử dụng.
3. **Mục 3 – Khuôn Mẫu Code Chuẩn Của Dự Án (Project Golden Code Templates):**
   - Cung cấp các đoạn code mẫu chuẩn mực thực tế theo đúng **ngôn ngữ & công nghệ mà dự án đang sử dụng** (được xác định từ `codebase-stats.md`, ví dụ: Go, Rust, Java, Python, TypeScript...):
     - Truy vấn Database an toàn (Model/ORM/QueryBuilder có team/tenant scope).
     - Chuẩn hóa xử lý lỗi (`Custom Exceptions / Errors`).
     - Ghi log có cấu trúc (`Structured Logging + Trace ID`).
4. **Mục 4 – Quy Chuẩn Giao Diện / Frontend (Nếu dự án có Frontend):**
   - Cách quản lý State, thư viện UI Component nội bộ bắt buộc dùng, chống bấm đúp (double submission), responsive layout.
5. **Mục 5 – Lệnh Chạy Local, Test, Linter & Chuẩn Commit:**
   - Cách bật môi trường local, lệnh chạy test cho đúng file vừa sửa, lệnh chạy linter/typecheck.

### File 3: `scripts/audit_codebase.py` (Script Tự Động Kiểm Duyệt Git Diff Siêu Tốc)
Subagent lập trình trực tiếp file script này bằng Python:
- Sử dụng `subprocess.check_output` đọc trực tiếp danh sách file thay đổi từ Git (`git diff --name-only`, `git diff --cached --name-only`, và `git status --porcelain`). Tự động bỏ qua các file trong thư mục `scripts/` hoặc file kiểm tra.
- Quét từng dòng code thay đổi bằng regex để kiểm tra đối chiếu trực tiếp với các bất biến kiến trúc ở Mục 2 của `STEP-0-code-after-scan-codebase.md` (ví dụ: thiếu team/tenant scope, cấm query bảng identity nhạy cảm, cấm import chéo nội bộ giữa các module, bắt buộc DTOs bất biến...).
- Báo cáo kết quả rõ ràng:
  - Trả về exit code 0 và thông báo xanh nếu tất cả các file đạt chuẩn 100%.
  - Trả về exit code 1 và chỉ rõ tên file, số dòng vi phạm kèm trích dẫn mục tương ứng trong `STEP-0-code-after-scan-codebase.md` để AI tự sửa lại.

### File 4: `skills/STEP-6-validate-after-code.md` (Kỹ Năng Tự Kiểm Duyệt Sau Khi Code)
Subagent tạo file này với quy trình chuẩn 3 bước:
- **Bước 1:** Chạy script `python3 scripts/audit_codebase.py`.
- **Bước 2:** Đọc dữ liệu báo cáo từ script.
- **Bước 3 (Self-Healing):** Nếu có lỗi, AI mở đúng mục được script chỉ dẫn trong `skills/STEP-0-code-after-scan-codebase.md` để tra cứu bối cảnh và mẫu code chuẩn, tự sửa lại file, rồi chạy lại script cho đến khi 100% xanh sạch.
