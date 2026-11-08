---
name: write-requirement-feature
description: 'Kỹ năng soạn thảo Đặc Tả Yêu Cầu Tính Năng (Feature Requirement / Spec) trước khi viết code: AI bắt buộc đọc cẩm nang nghiệp vụ chung `skills/STEP-0-requirement-after-scan-codebase.md` để nắm chuẩn thuật ngữ, vòng đời thực thể và luật cấm của dự án, sau đó xuất ra bản đặc tả chi tiết `specs/requirement-feature-<name>.md` đầy đủ User Story, Edge Cases và Acceptance Criteria làm đầu vào cho bước sinh Test Case.'
---

# KỸ NĂNG SOẠN THẢO YÊU CẦU TÍNH NĂNG (`write-requirement-feature`)

> [!IMPORTANT]
> **Nguyên Tắc "Hiểu Đúng Mới Được Code" (Spec-First Principle):**
> Trước khi bắt tay vào viết bất kỳ dòng code nào cho một tính năng mới, AI **BẮT BUỘC** phải có một bản đặc tả yêu cầu nghiệp vụ rõ ràng (Feature Specification) được lưu tại thư mục `specs/requirement-feature-<tên-tính-năng>.md`. 
> Điều này đảm bảo AI không bao giờ hiểu nhầm ý đồ của người dùng và làm đầu vào chuẩn xác cho Bước 2 (Viết Test Case).

---

## Quy Trình 3 Bước Soạn Thảo Requirement

Mỗi khi người dùng yêu cầu: *"Làm tính năng X"*, *"Tạo API Y"*, hoặc *"run skill write requirement feature <mô tả>"*, AI thực hiện tuần tự 3 bước sau:

### Bước 1: Đọc Hiến Pháp Nghiệp Vụ Của Dự Án
AI dùng `read_file` mở file cẩm nang nghiệp vụ chung:
📄 [`skills/STEP-0-requirement-after-scan-codebase.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/skills/STEP-0-requirement-after-scan-codebase.md)

AI kiểm tra:
1. Thuật ngữ nghiệp vụ chuẩn của dự án là gì (Domain Ubiquitous Language)? Có khái niệm nào tương tự đã tồn tại không?
2. Tính năng mới này tác động vào những Domain Entities nào?
3. Có làm thay đổi luồng State Machine (máy trạng thái) nào không?
4. Có vi phạm Ma trận phân quyền (RBAC) hoặc Luật cấm nghiệp vụ nào không?

---

### Bước 2: Soạn Thảo Bản Đặc Tả Tính Năng (`specs/requirement-feature-<name>.md`)
AI trực tiếp dùng `write_file` tạo file đặc tả mới trong thư mục `specs/` (ví dụ: `specs/requirement-feature-discount-coupon.md`) với cấu trúc chuẩn bắt buộc sau:

```markdown
# Đặc Tả Yêu Cầu Tính Năng: <Tên Tính Năng>

## 1. Mục Tiêu & User Story
- **Người dùng (Actor):** Là ai? (Admin / Manager / Member).
- **User Story:** "Với vai trò là [Actor], tôi muốn [Hành động] để [Mục đích/Giá trị đạt được]".
- **Giá trị cốt lõi:** Tính năng này giải quyết vấn đề cụ thể nào?

## 2. Ràng Buộc Nghiệp Vụ & Thực Thể Liên Quan
- **Thực thể tác động:** (Đối chiếu với Mục 2 của STEP-0-requirement-after-scan-codebase.md).
- **Vòng đời & Trạng thái:** Thực thể này đi qua các trạng thái nào (State Machine)?
- **Luật cấm kỵ (Invariants):** Những điều hệ thống tuyệt đối không được phép xảy ra.

## 3. Bản Hợp Đồng Dữ Liệu (Input / Output Contract)
- **Đầu vào (Request Input):** Các trường bắt buộc, kiểu dữ liệu, giới hạn độ dài.
- **Đầu ra (Response Output):** Cấu trúc dữ liệu trả về khi thành công.
- **Xử lý lỗi nghiệp vụ:** Mã lỗi và thông báo tương ứng khi vi phạm quy tắc.

## 4. Ma Trận Các Trường Hợp Biên (Edge Cases Matrix)
| Kịch Bản Biên | Hành Vi Hệ Thống Bắt Buộc | Mã Lỗi / Kết Quả |
| :--- | :--- | :--- |
| Dữ liệu rỗng / Thiếu trường | Báo lỗi validation ngay lập tức | 400 Bad Request |
| Thao tác trùng lặp (Double click) | Áp dụng Idempotency key, chỉ xử lý 1 lần | Trả về kết quả cũ |
| Dữ liệu hết hạn / Không tồn tại | Chặn thao tác, ghi log audit | 404 / 410 Expired |
| Sai phân quyền (Trái Tenant/Role) | Chặn truy cập tuyệt đối, chống IDOR | 403 Forbidden |

## 5. Tiêu Chí Nghiệm Thu (Acceptance Criteria / Definition of Done)
- [ ] **Kịch bản 1 (Happy Path):** Given [Dữ liệu hợp lệ] When [Thực hiện hành động] Then [Thành công và cập nhật trạng thái].
- [ ] **Kịch bản 2 (Failure Path):** Given [Dữ liệu sai/hết hạn] When [Thực hiện hành động] Then [Bị từ chối và giữ nguyên dữ liệu cũ].
- [ ] **Kịch bản 3 (Audit & Log):** Thao tác được ghi lại vào log hệ thống kèm Trace ID.
```

---

### Bước 3: Trình Bày Bản Đặc Tả & Kết Nối Sang Bước 2
- AI thông báo:  
  *"✅ Đã tạo xong file đặc tả yêu cầu: `specs/requirement-feature-<name>.md`."*
- Hướng dẫn chuyển sang Bước 2:  
  *"Tiếp theo, hãy chạy: `run skill write test case` (kỹ năng `skills/STEP-2-write-testcases-feature.md`) để đọc file requirement này và sinh ma trận test case toàn diện trước khi bắt đầu code."*
