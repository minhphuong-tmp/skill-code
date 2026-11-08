---
name: write-test-code
description: 'Kỹ năng sinh code kiểm thử tự động Unit Test & Integration Test trước khi viết code (chuẩn TDD Red-Green): AI đọc file `specs/test-case-feature-<name>.md` và cẩm nang kiến trúc để chuyển hóa các nhóm kịch bản (Happy Path, Negative, Boundary, State, Security) thành file code test thật (`tests/test_<feature>.py`). Chạy test ngay sau khi viết: test bắt buộc phải BÁO ĐỎ (FAIL) do chưa có code implement.'
---

# KỸ NĂNG SINH CODE TEST TỰ ĐỘNG (UNIT & INTEGRATION) (`write-test-code`)

> [!IMPORTANT]
> **Triết Lý Bắt Buộc: TDD Red-Green Phase**
> 1. Viết file test code dựa trên **Hợp đồng dữ liệu** và **Ma trận test case** từ Bước 1 & Bước 2.
> 2. **Chạy test ngay sau khi viết:** Test **BẮT BUỘC PHẢI BÁO ĐỎ (FAIL)** vì code tính năng chưa được viết. Điều này chứng minh test có hiệu lực, không bị viết ẩu thành luôn pass.
> 3. Không được viết code tính năng ở bước này! Việc viết code làm xanh test thuộc về Bước 4.

---

## Quy Trình 3 Bước Viết Test Code

Mỗi khi nhận lệnh: *"run skill write test code <mô tả>"*, AI thực hiện:

### Bước 1: Đọc Ma Trận Test Case
AI dùng `read_file` đọc:
📄 `specs/test-case-feature-<name>.md`

Trích xuất toàn bộ:
- `TC-HP-xx`: Các kịch bản Happy Path.
- `TC-VAL-xx`: Các kịch bản Validation (thiếu trường, sai kiểu).
- `TC-BND-xx`: Các kịch bản Boundary (rỗng, vượt quá max, double submit).
- `TC-STA-xx`: Các kịch bản State Transition.
- `TC-SEC-xx`: Các kịch bản Phân quyền và Multi-tenant (`team_id`).

---

### Bước 2: Sinh File Code Test Theo Đúng Ngôn Ngữ Dự Án
AI dùng `write_file` tạo file test trong thư mục test tương ứng của dự án (ví dụ: `tests/test_<name>.py` cho Python, `*.spec.ts` / `*.test.ts` cho Node.js/TypeScript, `*_test.go` cho Go):

```python
# Ví dụ minh họa khung sườn Test Contract (áp dụng linh hoạt theo ngôn ngữ của dự án)
import pytest
import unittest
# Import các hàm hoặc class dự kiến sẽ được implement ở Bước 4

class TestFeatureContract(unittest.TestCase):
    
    # 1. HAPPY PATH
    def test_tc_hp_01_create_successful_with_valid_data(self):
        """TC-HP-01: Tạo thành công với dữ liệu hợp lệ."""
        payload = {"name": "Valid Name", "scope_id": 1, "is_active": True}
        raise NotImplementedError("Chưa implement code tính năng (TDD Red Phase)")

    # 2. VALIDATION & NEGATIVE
    def test_tc_val_01_missing_required_field(self):
        """TC-VAL-01: Bỏ trống trường bắt buộc báo lỗi 400/422."""
        payload = {"scope_id": 1}
        raise NotImplementedError("Chưa implement code tính năng")

    # 3. BOUNDARY & EDGE CASES
    def test_tc_bnd_01_exceed_max_length(self):
        """TC-BND-01: Độ dài vượt quá giới hạn cực đại."""
        payload = {"name": "A" * 101, "scope_id": 1}
        raise NotImplementedError("Chưa implement code tính năng")

    # 4. STATE TRANSITION
    def test_tc_sta_02_illegal_state_transition(self):
        """TC-STA-02: Không cho phép chuyển trạng thái bất hợp pháp."""
        raise NotImplementedError("Chưa implement code tính năng")

    # 5. MULTI-TENANT ISOLATION (CHỐNG IDOR)
    def test_tc_sec_03_tenant_isolation(self):
        """TC-SEC-03: Tenant A không thể truy cập tài nguyên của Tenant B."""
        raise NotImplementedError("Chưa implement code tính năng")
```

---

### Bước 3: Chạy Kiểm Thử Báo Đỏ (Verify Red Phase)
AI thực thi lệnh chạy test runner của dự án (được xác định tại Mục 5 của `STEP-0-code-after-scan-codebase.md`, ví dụ `pytest`, `npm test`, `go test ./...`):
```bash
<cau_lenh_chay_test_cua_du_an>
```
- **Kỳ vọng:** Báo `🔴 [FAIL / RED]` (Do `NotImplementedError` hoặc chưa tìm thấy module).
- AI xác nhận: *"✅ File test code đã được tạo theo đúng Test Case và chạy báo ĐỎ chuẩn TDD! Sẵn sàng chuyển sang Bước 4 (`STEP-4-implement-feature.md`) để code làm xanh test."*
