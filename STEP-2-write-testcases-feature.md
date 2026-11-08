---
name: write-testcases-feature
description: 'Kỹ năng thiết kế ma trận kịch bản kiểm thử nghiệp vụ (Test Case Specification / QA Checklist) và Đặc tả luồng màn hình E2E trước khi code: AI đọc file yêu cầu tính năng `specs/requirement-feature-<name>.md` và hiến pháp nghiệp vụ `skills/STEP-0-requirement-after-scan-codebase.md`, sau đó áp dụng 5 kỹ thuật kiểm thử ISTQB để xuất ra 2 file: `specs/test-case-feature-<name>.md` và `specs/ui-flow-e2e-<name>.md`.'
---

# KỸ NĂNG THIẾT KẾ TEST CASE & ĐẶC TẢ GIAO DIỆN E2E (`write-testcases-feature`)

> [!IMPORTANT]
> **Bản Chất & Hai Đầu Ra Của Bước Này:**
> 1. **`specs/test-case-feature-<name>.md`**: Ma trận kiểm thử nghiệp vụ (QA Checklist) cho 5 nhóm ISTQB để rà soát khi viết code, làm đầu vào cho Step 3 (`STEP-3-write-test-code.md`) và làm căn cứ ánh xạ kịch bản E2E tại Step 5 (`STEP-5-write-e2e-test.md`).
> 2. **`specs/ui-flow-e2e-<name>.md`**: Bản mô tả chi tiết giao diện màn hình, elements (`data-attr`), modal popup và luồng click-through từng bước làm căn cứ đối chiếu chuẩn mực cho video clip quay ở Step 5 (`STEP-5-write-e2e-test.md`).

---

## 5 Nhóm Kịch Bản Kiểm Thử Bắt Buộc (ISTQB Framework)

Khi phân tích requirement để sinh test case, AI **BẮT BUỘC** phải chia kịch bản thành đúng 5 nhóm sau:

| Nhóm | Tên Nhóm | Mục Tiêu Kiểm Thử |
| :---: | :--- | :--- |
| **G1** | **Happy Path** *(Luồng chuẩn)* | Đi đúng luồng nghiệp vụ chính với dữ liệu hợp lệ. Đảm bảo trạng thái cập nhật đúng, trả về 200/201, phát event (nếu có). |
| **G2** | **Negative & Validation** *(Dữ liệu sai)* | Kiểm tra việc từ chối các input thiếu trường bắt buộc (`required`), sai định dạng (email, phone, regex), sai kiểu dữ liệu. |
| **G3** | **Boundary & Edge Cases** *(Biên & Dị biệt)* | Kiểm tra các giá trị biên min/max, rỗng `""`, chỉ khoảng trắng `"   "`, `null`, số âm, số 0, ký tự Unicode/tiếng Việt/emoji, request trùng lặp (double submit/idempotency). |
| **G4** | **State Transition** *(Máy trạng thái)* | Kiểm tra chuyển trạng thái hợp lệ theo State Machine và **chặn đứng** các bước chuyển bất hợp pháp (ví dụ: từ `CANCELLED` không được phép sang `COMPLETED`). |
| **G5** | **Security & Multi-Tenant** *(Bảo mật & Tenant)* | Kiểm tra chặn người dùng không có quyền (RBAC $\rightarrow$ 403), chưa đăng nhập ($\rightarrow$ 401), và **chống rò rỉ dữ liệu chéo giữa các Tenant (IDOR theo `team_id`)**. |

---

## Quy Trình 3 Bước Thực Hiện

Khi nhận lệnh: *"run skill write test case <mô tả>"* hoặc *"viết test case cho feature X"*, AI thực hiện:

### Bước 1: Đọc Đầu Vào Nghiệp Vụ
AI dùng `read_file` đọc 2 tài liệu:
1. File đặc tả tính năng đã tạo ở Bước 1:
   📄 `specs/requirement-feature-<tên-tính-năng>.md`
2. Hiến pháp nghiệp vụ toàn hệ thống:
   📄 [`skills/STEP-0-requirement-after-scan-codebase.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/skills/STEP-0-requirement-after-scan-codebase.md)

---

### Bước 2: Tạo Bản Đặc Tả Kịch Bản `specs/test-case-feature-<name>.md`
AI dùng `write_file` tạo file đặc tả kịch bản kiểm thử tại thư mục `specs/`:

```markdown
# Ma Trận Kịch Bản Kiểm Thử (Test Case Specification): <Tên Tính Năng>
> **Tài liệu tham chiếu:** `specs/requirement-feature-<tên-tính-năng>.md`  
> **Hiến pháp nghiệp vụ:** `skills/STEP-0-requirement-after-scan-codebase.md`  

## 1. Happy Path Scenarios (Kịch Bản Thành Công Chuẩn)
| ID | Kịch Bản (Scenario) | Tiền Điều Kiện | Input / Thao Tác | Kết Quả Mong Đợi (Expected Outcome) | Check |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-HP-01** | Thực hiện thành công với dữ liệu hợp lệ | User có quyền, Tenant hợp lệ | Payload đầy đủ các trường hợp lệ | Trả về 200/201, DB cập nhật đúng, Event phát ra đúng format | [ ] |

## 2. Negative & Validation Scenarios (Dữ Liệu Không Hợp Lệ)
| ID | Kịch Bản (Scenario) | Tiền Điều Kiện | Input / Thao Tác | Kết Quả Mong Đợi (Expected Outcome) | Check |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-VAL-01** | Bỏ trống trường bắt buộc | User đã đăng nhập | Thiếu trường `<required_field>` trong payload | Trả về 400/422, thông báo rõ: "<field> is required" | [ ] |

## 3. Boundary & Edge Case Scenarios (Giá Trị Biên & Dị Biệt)
| ID | Kịch Bản (Scenario) | Tiền Điều Kiện | Input / Thao Tác | Kết Quả Mong Đợi (Expected Outcome) | Check |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-BND-01** | Độ dài chuỗi vượt quá giới hạn cực đại | User đã đăng nhập | Nhập chuỗi có độ dài `max_length + 1` | Báo lỗi 400/422: Vượt quá số ký tự cho phép | [ ] |
| **TC-BND-02** | Thao tác trùng lặp / Bấm đúp (Double Submit) | User đã đăng nhập | Gửi 2 request giống nhau cùng Idempotency Key trong 1s | Request 1 xử lý; Request 2 trả về kết quả cũ | [ ] |

## 4. State Transition Scenarios (Chuyển Trạng Thái Theo Vòng Đời)
| ID | Kịch Bản (Scenario) | Tiền Điều Kiện | Input / Thao Tác | Kết Quả Mong Đợi (Expected Outcome) | Check |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-STA-01** | Chuyển trạng thái hợp lệ | Đang ở trạng thái A | Kích hoạt hành động chuyển sang B | Trạng thái chuyển thành B, log audit ghi nhận | [ ] |
| **TC-STA-02** | Chặn chuyển trạng thái bất hợp pháp | Đang ở Terminal state | Kích hoạt chuyển sang COMPLETED | Báo lỗi 400: Không thể chuyển trạng thái | [ ] |

## 5. Security, RBAC & Multi-Tenancy Scenarios (Bảo Mật & Phân Quyền)
| ID | Kịch Bản (Scenario) | Tiền Điều Kiện | Input / Thao Tác | Kết Quả Mong Đợi (Expected Outcome) | Check |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-SEC-01** | Truy cập không có Token xác thực | Chưa đăng nhập | Gửi request không có Header Auth | Trả về 401 Unauthorized | [ ] |
| **TC-SEC-02** | Sai vai trò phân quyền (RBAC) | Đăng nhập với Role MEMBER | Thao tác của ADMIN | Trả về 403 Forbidden | [ ] |
| **TC-SEC-03** | Chống rò rỉ Multi-Tenant (IDOR) | User của Team A | Truy cập ID của Team B | Trả về 404 hoặc 403 tuyệt đối | [ ] |
```

---

### Bước 3: Tạo Bản Đặc Tả Luồng Màn Hình E2E `specs/ui-flow-e2e-<name>.md`
AI dùng `write_file` tạo file đặc tả màn hình phục vụ việc đối chiếu video clip ở Step 5:

```markdown
# Đặc Tả Luồng Màn Hình E2E (UI Flow Specification): <Tên Tính Năng>
> Dùng làm căn cứ đối chiếu với video clip quay được từ Playwright E2E ở Step 5.

## 1. Màn Hình & Đường Dẫn URL
- **Trang truy cập (Page URL):** `<base_url_cua_du_an>/<path>` (Tra cứu tại `STEP-0-e2e-after-scan-codebase.md` hoặc biến môi trường `BASE_URL`)
- **Tiêu đề trang (Page Title / Header):** `<Tên hiển thị>`

## 2. Danh Sách Phần Tử Giao Diện (UI Elements & Selectors)
| Phần Tử | Thuộc Tính Định Danh (`data-attr`) | Loại (Button/Input/Modal) | Mô Tả Hiển Thị |
| :--- | :--- | :--- | :--- |
| Nút Tạo Mới | `data-attr="create-feature-btn"` | Button | Nút màu xanh primary, text "Create New" |
| Ô nhập Tên | `data-attr="feature-name-input"` | Input Text | Placeholder "Enter feature name..." |
| Modal Xác Nhận | `data-attr="confirm-modal"` | Modal Dialog | Hộp thoại xác nhận thao tác |
| Thông Báo Toast | `data-attr="success-toast"` | Toast Alert | Báo thành công góc trên bên phải |

## 3. Kịch Bản Thao Tác Từng Bước (Step-by-Step User Flow)
1. **Bước 1 (Vào trang):** Trình duyệt mở URL `http://localhost:8080/<path>`, thấy nút `data-attr="create-feature-btn"`.
2. **Bước 2 (Điền thông tin):** Click nút tạo mới, nhập tên vào `data-attr="feature-name-input"`.
3. **Bước 3 (Submit):** Click nút Save. Hiển thị loading spinner chống click đúp.
4. **Bước 4 (Kỳ vọng hiển thị):** Modal đóng lại, toast xanh hiển thị thông báo "Tạo thành công", dòng mới xuất hiện trong bảng.
```

---

### Bước 4: Hướng Dẫn Kết Nối Sang Bước 3
AI thông báo hoàn thành 2 file:
- `specs/test-case-feature-<name>.md`
- `specs/ui-flow-e2e-<name>.md`
Và hướng dẫn: *"Bây giờ hãy chạy Bước 3: `run skill write test code` (`skills/STEP-3-write-test-code.md`) để sinh code kiểm thử tự động Unit/Integration Test trước khi implement code!"*
