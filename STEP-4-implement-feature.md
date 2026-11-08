---
name: implement-feature
description: 'Kỹ năng thi công code tính năng (Implementation Engineer): AI tiếp nhận 4 tài liệu (requirement, test case matrix, file code test, và cẩm nang kiến trúc `STEP-0-code-after-scan-codebase.md`). TUYỆT ĐỐI CẤM SỬA TEST VÀ REQUIREMENT, chỉ sửa và viết code tính năng cho đến khi 100% test chuyển từ ĐỎ sang XANH (PASS), tick `[x]` vào checklist và chạy `git add`.'
---

# KỸ NĂNG THI CÔNG CODE TÍNH NĂNG (`implement-feature`)

> [!CAUTION]
> **LUẬT THÉP CỦA KỸ SƯ THI CÔNG (IMMUTABLE SPEC & TEST RULE):**
> 1. **TUYỆT ĐỐI CẤM SỬA** bất kỳ dòng nào trong:
>    - `specs/requirement-feature-<name>.md`
>    - `specs/test-case-feature-<name>.md`
>    - File code test đã tạo ở Bước 3 (`tests/`, `*.spec.ts`, v.v.)
> 2. Nhiệm vụ duy nhất của bạn: **Viết code tính năng chuẩn kiến trúc để vượt qua toàn bộ các bài test có sẵn!**
> 3. Tuyệt đối không được "sửa test cho pass". Test là luật pháp; code phải phục tùng test!

---

## Các Tài Liệu Bắt Buộc Phải Đọc Trước Khi Gõ Code

Khi nhận lệnh: *"run skill implement code feature <mô tả>"*, AI dùng `read_file` mở các tài liệu:
1. 📄 `specs/requirement-feature-<name>.md` (Nắm rõ User Story và Hợp đồng I/O).
2. 📄 `specs/test-case-feature-<name>.md` (Nắm toàn bộ kịch bản Happy, Negative, Boundary, State, Security).
3. 📄 File code test tạo ở Bước 3 (Đọc các hàm test đang báo đỏ để biết cần implement hàm/class nào).
4. 📄 [`skills/STEP-0-code-after-scan-codebase.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/SKILL%20Code/STEP-0-code-after-scan-codebase.md) (Tuân thủ bản đồ Where-to-write, Scope/Tenant ID, DTOs, UI Design System quy định riêng cho dự án).
5. 📄 [`database-schema.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/database-schema.md) *(Nếu có DB)*: Tra cứu tên bảng thật, trường khóa chính, khóa ngoại, tuyệt đối cấm bịa tên bảng.
6. 📄 `artifacts/e2e-feedback-<name>.md` *(BẮT BUỘC ĐỌC NẾU ĐÂY LÀ VÒNG LẶP SỬA LỖI TỪ STEP 5)*: Đọc ngay để nắm chính xác Test Case nào bị fail, mốc giây/ảnh frame bị lỗi giao diện, và log HTTP 4xx/5xx để fix đúng chỗ!

---

## Quy Trình 4 Bước Thi Công Code Chuẩn Mực

### Bước 1: Viết Mã Nguồn Theo Bản Đồ Phân Tầng
- **Nếu có file `artifacts/e2e-feedback-<name>.md` (Fix Loop từ Step 5):** AI mở ngay ảnh frame lỗi và log lỗi chỉ ra trong file feedback, tập trung sửa triệt để nguyên nhân khiến UI bị lệch hoặc API 422/500 trước khi chạy lại test.
- AI tạo hoặc sửa các file theo đúng cấu trúc mô-đun chuẩn (Vertical Slice) tra cứu tại Mục 1 của `STEP-0-code-after-scan-codebase.md`:
  - **Backend Model / Entity:** Bắt buộc tuân thủ Tenant Scope ID và các ràng buộc toàn vẹn dữ liệu.
  - **Backend Service / Business Logic:** Validate dữ liệu chặt chẽ theo hợp đồng ở Step 1.
  - **Frontend View / Component:** Tách biệt UI presentation và logic state. Nút bấm gọi mạng phải có trạng thái `loading` chống double submission.

---

### Bước 2: Chạy Test Liên Tục Cho Đến Khi Xanh (Turn Red to Green)
Sau mỗi lần viết code, AI thực thi lệnh chạy test runner của dự án (xác định từ Mục 5 của `STEP-0-code-after-scan-codebase.md`):
```bash
<cau_lenh_chay_test_cua_du_an>
```
- Nếu còn lỗi `🔴 [FAIL / RED]`: Đọc kỹ traceback, tinh chỉnh code tính năng cho đến khi đạt `🟢 [PASS / GREEN]`.

---

### Bước 3: Nghiệm Thu Checklist (Definition of Done)
Khi toàn bộ test đã pass, AI dùng `edit_file` mở file `specs/test-case-feature-<name>.md` và chuyển tất cả các ô `[ ]` thành `[x]`:
```markdown
| TC-HP-01  | Thực hiện thành công với dữ liệu hợp lệ | [x] |
| TC-VAL-01 | Bỏ trống trường bắt buộc báo lỗi 422    | [x] |
| TC-BND-01 | Độ dài vượt quá max báo lỗi 400        | [x] |
| TC-STA-01 | Chuyển trạng thái hợp lệ                | [x] |
| TC-SEC-03 | Chống rò rỉ dữ liệu Multi-Tenant (IDOR) | [x] |
```

---

### Bước 4: Lưu Trữ Git (Git Add) & Kết Nối Sang Bước 5
AI thực thi lệnh gom mã nguồn:
```bash
git add -A
```
AI thông báo hoàn thành:  
*"🎉 Code tính năng đã được implement hoàn chỉnh, 100% Unit/Integration Test đã XANH, toàn bộ checklist đã được tick `[x]`! Sẵn sàng chuyển sang Bước 5 (`STEP-5-write-e2e-test.md`) để viết kịch bản Playwright và quay clip màn hình đối chiếu!"*
