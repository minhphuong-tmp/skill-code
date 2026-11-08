---
name: scan-requirement
description: 'Meta-Skill quét tự động toàn bộ tri thức nghiệp vụ (Requirements & Domain) của dự án bằng bộ đôi công cụ: (1) Thu hoạch Skills có sẵn, Rules, Specs, RFCs, PRD qua Repomix (raw-requirements-docs.md) và (2) Bóc tách Domain Models, State Machines & Test Rules từ code (raw-requirements-domain.md) để Subagent đúc kết thành Hiến Pháp Nghiệp Vụ duy nhất của toàn bộ dự án (skills/STEP-0-requirement-after-scan-codebase.md).'
---

# META-SKILL: QUÉT NGHIỆP VỤ & TỰ ĐỘNG ĐÚC KẾT BỘ YÊU CẦU DỰ ÁN (`/scan-requirement`)

Mục đích của Skill này là giúp AI nắm trọn **"Linh hồn Nghiệp Vụ" (LÀM CÁI GÌ & TẠI SAO?)** của dự án. Nếu chỉ có cẩm nang kỹ thuật (`STEP-0-code-after-scan-codebase.md`), AI rất dễ rơi vào bẫy: *"Code rất đúng cú pháp nhưng SAI HOÀN TOÀN Ý ĐỒ SẢN PHẨM"*.

Quy trình áp dụng mô hình **"Tam Giác Nghiệp Vụ" (The 3-Pillar Domain Triangle)**:
1. **Tri thức có sẵn từ Skills & Rules:** Đọc toàn bộ các file Skill, Rule, Prompt của tác giả (`.agents/skills/`, `.cursorrules`, `AGENTS.md`) – nơi lưu giữ 50% quy ước ngầm của sản phẩm.
2. **Tài liệu đặc tả (Specs & RFCs):** Đọc các tài liệu thiết kế tính năng, PRD, BDD features.
3. **Mã nguồn thực địa (Domain Code):** Bóc tách các Domain Models, Máy trạng thái (Enums/Choices) và các Scenarios kiểm thử nghiệp vụ (`test_cannot_*`, `test_should_*`).

Khi người dùng yêu cầu: *"Quét nghiệp vụ dự án này"*, *"Chạy skill scan-requirement"*, hoặc *"Tạo STEP-0-requirement-after-scan-codebase.md"*, AI **BẮT BUỘC** thực hiện tuần tự **2 Bước** dưới đây:

---

## Bước 1: Chạy 1 Lệnh Duy Nhất Để Thu Hoạch Bộ Đôi Tài Nguyên Nghiệp Vụ

AI chỉ cần thực thi đúng 1 lệnh duy nhất:
```bash
python3 scripts/scan_requirements.py <thu_muc_du_an>
```

Script `scripts/scan_requirements.py` đã đóng gói trọn gói toàn bộ công cụ và tự động xuất ra 2 file thô:
1. **Thu hoạch Skills, Rules, Specs & Docs (`raw-requirements-docs.md`):** Tự động gọi `repomix` gom toàn bộ các file Skill có sẵn, `.cursorrules`, `AGENTS.md`, `CLAUDE.md`, thư mục `docs/`, `rfcs/`, `specs/`, `PRD/`, `*.feature`.
2. **Bóc tách Domain Models, State Machines & Test Scenarios (`raw-requirements-domain.md`):** Tự động phân tích AST mã nguồn để đo đếm các thực thể kinh doanh, các Enum trạng thái và các luật cấm nghiệp vụ đang được test suite bảo vệ.

---

## Bước 2: Subagent Đúc Kết Ra "Hiến Pháp Nghiệp Vụ" Duy Nhất Của Dự Án

> [!IMPORTANT]
> ### Cơ Chế Ủy Quyền Cho Subagent (Subagent Delegation Pattern - Chống Tràn Context Window)
> Các file tài liệu docs, specs và skills có sẵn có thể rất dài (hàng chục nghìn tokens).
> **Quy tắc sống còn:** Để bảo vệ **Session chính (Orchestrator)** không bao giờ bị quá tải hoặc tràn bộ nhớ, Session chính **phải ủy quyền toàn bộ tác vụ phân tích và viết cẩm nang nghiệp vụ cho Subagent** (`invoke_subagent`):
> 1. **Session chính (AI Main - Chỉ giao việc, KHÔNG đọc file):** Tuyệt đối **KHÔNG mở đọc các file dữ liệu thô** vào context của mình. Session chính chỉ gọi `invoke_subagent` giao toàn quyền cho Subagent kèm đường dẫn 2 file đã sinh ra ở Bước 1.
> 2. **Subagent (Worker thực thi độc lập - Cả ĐỌC lẫn VIẾT):** Subagent chạy trong ngữ cảnh sandbox riêng biệt:
>    - **Tự mở đọc:** `raw-requirements-docs.md` (chú trọng các luật nghiệp vụ trong skills và RFCs có sẵn).
>    - **Tự mở đọc:** `raw-requirements-domain.md` (đối chiếu các State Machine và thực thể trong code).
>    - **Tự tổng hợp & Tự ghi:** Tự đúc kết tri thức và trực tiếp dùng công cụ `write_file` để xuất ra file duy nhất:
>      📄 `skills/STEP-0-requirement-after-scan-codebase.md`
> 3. **Phản hồi siêu nhẹ:** Subagent chỉ gửi trả về cho Session chính 1 tin nhắn ngắn tóm tắt (3–5 gạch đầu dòng và đường dẫn file). Session chính giữ được 95%+ context window sạch sẽ cho các tác vụ tiếp theo!

---

## Cấu Trúc Bắt Buộc Của File `skills/STEP-0-requirement-after-scan-codebase.md`

File `STEP-0-requirement-after-scan-codebase.md` **BẮT BUỘC phải có đủ 5 Mục sau** (kế thừa toàn bộ tri thức từ Skills có sẵn và các mỏ quặng nghiệp vụ đã quét):

1. **Mục 1 – Tầm Nhìn Sản Phẩm & Giá Trị Cốt Lõi (Product Vision & Core Domains):**
   - Dự án này giải quyết bài toán kinh doanh gì? Đối tượng người dùng mục tiêu (Target Persona) là ai?
   - Các phân hệ sản phẩm lớn (Vertical Slices / Core Modules).
2. **Mục 2 – Từ Điển Ngôn Ngữ Miền Chung (Domain Ubiquitous Language & Entity Glossary):**
   - Bảng định nghĩa chính xác từng thực thể nghiệp vụ (ví dụ: `Workspace`, `Organization`, `Team`, `Cohort`, `Billing`, `Invoice`...).
   - Mối quan hệ giữa các thực thể (1-N, N-N). Cấm AI sử dụng sai thuật ngữ nghiệp vụ.
3. **Mục 3 – Vòng Đời Thực Thể & Máy Trạng Thái (Entity State Machines & Transitions):**
   - Các luồng chuyển đổi trạng thái hợp lệ của từng thực thể cốt lõi (ví dụ: `DRAFT ➔ PENDING ➔ APPROVED ➔ ACTIVE ➔ EXPIRED`).
   - Các hành động bị cấm khi thực thể đang ở trạng thái nhất định.
4. **Mục 4 – Ma Trận Phân Quyền & Luật Cấm Nghiệp Vụ (RBAC & Business Invariants):**
   - Vai trò và quyền hạn (Admin, Manager, Member, Guest).
   - Các luật cấm kỵ bất khả xâm phạm về mặt sản phẩm (ví dụ: Không được xóa dữ liệu audit log, không được hạ cấp gói khi chưa hết chu kỳ).
5. **Mục 5 – Tiêu Chuẩn Soạn Thảo Feature Spec (Feature Spec Standard):**
   - Khung sườn bắt buộc để khi người dùng yêu cầu làm tính năng mới, skill `write-requirement-feature` phải tuân theo để viết ra bản đặc tả tính năng đầy đủ:
     - User Story (Người dùng muốn gì, tại sao).
     - Input / Output Contract.
     - Edge Cases (Dữ liệu rỗng, trùng lặp, hết hạn, mất mạng).
     - Acceptance Criteria (Tiêu chí nghiệm thu rõ ràng).
