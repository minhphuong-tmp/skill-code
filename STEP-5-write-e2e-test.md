---
name: write-e2e-test
description: 'Kỹ năng viết kịch bản E2E bằng Midscene AI (@midscene/web) kết hợp Playwright bám sát 100% Test Case & Requirement, chạy quay clip màn hình và dùng script bóc tách keyframes + lọc log độc quyền theo feature để đối chiếu với bản đặc tả giao diện: AI đọc `specs/requirement-feature-<name>.md`, `specs/test-case-feature-<name>.md`, `specs/ui-flow-e2e-<name>.md` và `skills/STEP-0-e2e-after-scan-codebase.md`, viết file test E2E (`<thu_muc_e2e>/<name>.spec.ts`) dùng `aiAction` và `aiAssert`, chạy test quay video, gọi script `scripts/analyze_e2e_clip.py` để lọc sạch log rác và bóc tách ảnh 1 FPS, sau đó đối chiếu thị giác. Nếu sai lệch, gửi feedback ngược lại cho Step 4.'
---

# KỸ NĂNG VIẾT TEST E2E THEO TEST CASE & REQUIREMENT, QUAY CLIP & PHÂN TÍCH THỊ GIÁC (`write-e2e-test`)

> [!IMPORTANT]
> **Quy Tắc Thực Thi E2E Chuẩn Kỹ Thuật & Khép Kín Nghiệp Vụ:**
> 1. **Bám Sát Ma Trận Test Case & Requirement (100% Traceability):** Mọi kịch bản kiểm thử E2E trong file spec BẮT BUỘC phải ánh xạ trực tiếp từ các mã kịch bản trong `specs/test-case-feature-<name>.md` (TC-HP, TC-VAL, TC-STA...) và thỏa mãn tiêu chí chấp nhận (Acceptance Criteria) trong `specs/requirement-feature-<name>.md`.
> 2. **Tuyệt đối không dùng prompt suông:** Bắt buộc dùng script tự động [`scripts/analyze_e2e_clip.py`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/SKILL%20Code/scripts/analyze_e2e_clip.py) để bóc tách video thành chuỗi ảnh tĩnh 1 ảnh/giây (1 FPS).
> 3. **Lọc sạch 100% log rác background:** Hệ thống tự động loại bỏ các log không liên quan (polling `/decide/`, telemetry, `/api/users/@me/`, heartbeat pings) và **CHỈ GIỮ LẠI log và lỗi HTTP của riêng Feature đang làm**.
> 4. **Vòng lặp phản hồi (Feedback Loop):** Nếu ảnh chụp hoặc log bị lệch so với đặc tả, gửi ảnh bằng chứng và log lỗi ngược lại cho Step 4 (`STEP-4-implement-feature.md`) để sửa code!

---

## 4 Tài Liệu Bắt Buộc Đọc Đầu Vào (Đồng Bộ 100% Nghiệp Vụ & Giao Diện)

Khi nhận lệnh: *"run skill write test e2e <mô tả>"*, AI dùng `read_file` mở đủ 4 tài liệu:
1. 📄 `specs/requirement-feature-<name>.md` (Nắm trọn vẹn User Story, Tiêu chí chấp nhận - Acceptance Criteria và Hợp đồng I/O).
2. 📄 `specs/test-case-feature-<name>.md` (Ma trận 5 nhóm kịch bản ISTQB: Happy Path, Negative/Validation, Boundary, State Transition, Security/RBAC - Dùng để tổ chức các block `test()` trong Playwright).
3. 📄 `specs/ui-flow-e2e-<name>.md` (Bản đặc tả luồng màn hình: Page URL, thuộc tính `data-attr`, dialog modal, toast alert làm chuẩn mực đối chiếu thị giác).
4. 📄 [`skills/STEP-0-e2e-after-scan-codebase.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/SKILL%20Code/STEP-0-e2e-after-scan-codebase.md) (Cẩm nang vận hành E2E local, cấu hình cổng dịch vụ, tài khoản test và lệnh chạy runner có quay clip).

---

## Quy Trình 4 Bước Viết E2E & Phân Tích Bằng Script

### Bước 1: Viết File Kịch Bản E2E Bằng Midscene AI (`<thu_muc_e2e>/<name>.spec.ts`)
AI dùng `write_file` tạo file test trong thư mục E2E của dự án (xác định từ `STEP-0-e2e-after-scan-codebase.md`, ví dụ: `playwright/e2e/`, `e2e/`, hoặc `tests/e2e/`).

> [!TIP]
> **Sức Mạnh Của Midscene AI Trong Bước Này:**
> Thay vì AI phải vất vả đi tìm từng selector phức tạp (`xpath`, `css`, `data-testid`), AI **bê nguyên văn các bước từ `specs/test-case-feature-<name>.md` và `specs/ui-flow-e2e-<name>.md`** ném thẳng vào 2 hàm AI cốt lõi của Midscene:
> * `aiAction("hành động...")`: AI tự phân tích DOM/Accessibility Tree và click/gõ chuẩn xác 100%.
> * `aiAssert("kỳ vọng...")`: AI tự kiểm tra thị giác màn hình xem kết quả có đúng như mô tả không (nếu sai tự động báo FAIL).

```typescript
// <thu_muc_e2e>/<name>.spec.ts
import { test as base } from '@playwright/test'
import type { PlayWrightAiFixtureType } from '@midscene/web/playwright'
import { PlaywrightAiFixture } from '@midscene/web/playwright'

// Kích hoạt bộ công cụ Midscene AI Fixture
export const test = base.extend<PlayWrightAiFixtureType>(PlaywrightAiFixture())

test.describe('<Tên Tính Năng> - E2E Verification Bằng Midscene AI', () => {

    test.beforeEach(async ({ page }) => {
        // Mở đúng URL theo specs/ui-flow-e2e-<name>.md
        await page.goto('/<path>')
    })

    // 1. Ánh xạ từ TC-HP-01 (Happy Path trong specs/test-case-feature-<name>.md)
    test('[TC-HP-01] Người dùng thực hiện luồng nghiệp vụ thành công theo đúng Requirement', async ({ page, aiAction, aiAssert }) => {
        // Dùng aiAction đọc trực tiếp các bước hành động trong test case:
        await aiAction('Click vào nút "Create New Feature"')
        await aiAction('Nhập "E2E Test Item Valid" vào ô tên tính năng')
        await aiAction('Click nút Save trên hộp thoại xác nhận')

        // Dùng aiAssert đối chiếu trực tiếp với Acceptance Criteria & Mô tả màn hình:
        await aiAssert('Phải hiển thị Toast thông báo màu xanh "Tạo thành công" ở góc màn hình')
        await aiAssert('Trong danh sách phải hiển thị mục mới có tên "E2E Test Item Valid"')
    })

    // 2. Ánh xạ từ TC-VAL-01 (Validation trong specs/test-case-feature-<name>.md)
    test('[TC-VAL-01] Chặn submit khi bỏ trống trường bắt buộc & hiển thị thông báo lỗi', async ({ page, aiAction, aiAssert }) => {
        await aiAction('Click vào nút "Create New Feature"')
        await aiAction('Để trống trường bắt buộc và click nút Save')

        // aiAssert kiểm tra giao diện báo lỗi đỏ đúng quy cách:
        await aiAssert('Phải hiển thị thông báo lỗi màu đỏ "Trường này là bắt buộc" bên dưới ô nhập')
    })
})
```

---

### Bước 2: Chạy Test E2E Có Bật Quay Màn Hình
AI thực thi lệnh runner:
```bash
python3 scripts/run_e2e_local.py --spec e2e/<name>.spec.ts
```
Runner tự động:
1. Kiểm tra trạng thái các port dịch vụ local (được liệt kê trong `STEP-0-e2e-after-scan-codebase.md`).
2. Bật browser thật và ghi lại toàn bộ video luồng test.
3. Xuất file video vào: `artifacts/videos/<name>_<hash>.webm`.

---

### Bước 3: Phân Tích Clip Bằng Script & Đối Chiếu Ma Trận Test Case
AI thực thi ngay script bóc tách và lọc log:
```bash
python3 scripts/analyze_e2e_clip.py --video artifacts/videos/<name>.webm --feature <name>
```

Script sẽ tự động:
1. Gọi `ffmpeg` bóc tách chuỗi ảnh keyframes tại tần số 1 FPS vào: `artifacts/videos/frames/`.
2. **Lọc log thông minh:** Loại bỏ hoàn toàn các log polling telemetry không liên quan, chỉ trích xuất đúng các log lỗi của feature `<name>`.
3. Xuất báo cáo Markdown: `artifacts/videos/review-<name>.md`.

**AI dùng `read_file` mở báo cáo `review-<name>.md`, xem trực tiếp các ảnh frame và lập Bảng Đối Chiếu Ma Trận Nghiệp Vụ:**

| Mã Kịch Bản | Mục Tiêu Kiểm Thử | Mốc Thời Gian Video / Frame | Bằng Chứng Giao Diện & Log | Đánh Giá |
| :--- | :--- | :---: | :--- | :---: |
| **[TC-HP-01]** | Điền form và tạo mới thành công | 00:03 (Frame 003) | Toast xanh hiển thị, item xuất hiện trong bảng, không có lỗi HTTP | 🟢 PASS |
| **[TC-VAL-01]**| Chặn submit khi thiếu trường | 00:05 (Frame 005) | Thông báo lỗi đỏ hiển thị đúng quy cách | 🟢 PASS |

- **Trường Hợp A: TOÀN BỘ TEST CASES ĐỀU PASS & Ảnh khớp 100% với đặc tả:**
  - AI thông báo hoàn thành kèm đường dẫn clip và ảnh:
    ```markdown
    ✅ [E2E PASS] Toàn bộ kịch bản E2E bám sát Test Case & Requirement đã hoàn thành xuất sắc!
    📹 Clip video: `artifacts/videos/<name>.webm`
    📸 Đã kiểm tra chuỗi ảnh keyframes: Khớp 100% với `specs/ui-flow-e2e-<name>.md`.
    🎯 Ma trận Test Case: 100% [TC-xxx] đều PASS.
    🟢 Log kiểm tra: Sạch sẽ, không có lỗi console hay HTTP 500 của feature.
    Sẵn sàng chuyển sang Bước 6 (`skills/STEP-6-validate-after-code.md`)!
    ```

- **Trường Hợp B: TEST FAIL hoặc Ảnh/Log bị lệch so với Test Case & Đặc tả:**
  - *(Ví dụ: Toast không hiện trong ảnh frame giây thứ 3, nút bấm bị disabled sai logic, hoặc có lỗi 422/500 trên API của feature)*.
  - **AI KHÔNG ĐƯỢC TỰ Ý SỬA TEST HAY ĐẶC TẢ!**
  - **Quy trình gửi phản hồi 2 bước chuẩn kỹ thuật để Session Step 4 hiểu 100%:**
    1. **Ghi biên bản lỗi ra file vật lý (Persistence):** AI dùng `write_file` tạo file:
       📄 `artifacts/e2e-feedback-<name>.md`
       ```markdown
       # E2E FEEDBACK REPORT: <name>
       > **Trạng thái:** FAILED
       > **Test Case lỗi:** [TC-HP-01]
       > **Ảnh minh chứng:** artifacts/videos/frames/<name>_frame_002.png
       > **Log lỗi Scoped:** POST /api/<name>/ failed with status 422: missing field
       > **Chi tiết lỗi:** Nút create-feature-btn bị disabled ở giây thứ 2, không hiện toast thành công.
       > **Hành động yêu cầu cho Step 4:** Mở lại code form và payload API để fix đúng trường missing field.
       ```
    2. **Trả tín hiệu điều phối cho Main Agent / Session Điều Hành:**
       AI xuất thông báo có format rõ ràng để Main Agent hoặc người điều phối nhận biết ngay:
       ```markdown
       🚨 [STATUS: E2E_FAILED_NEED_FIX]
       Đã phát hiện sai lệch khi test E2E cho feature `<name>`.
       Đã ghi nhận toàn bộ bằng chứng vào file: `artifacts/e2e-feedback-<name>.md`
       👉 HÀNH ĐỘNG TIẾP THEO: Main Agent kích hoạt lại session:
          `run skill implement code feature <name>` (Step 4) để đọc file feedback và sửa code!
       ```

---

### Bước 4: Chuyển Sang Bước 6 Khi Mọi Thứ Đã Hoàn Hảo
Sau khi test E2E xanh, chuỗi ảnh frame đạt chuẩn và log scoped sạch sẽ $\rightarrow$ Chạy tiếp:
`run skill validate after code` ([`skills/STEP-6-validate-after-code.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/SKILL%20Code/STEP-6-validate-after-code.md)) để rà soát git diff và clean code trước khi commit!
