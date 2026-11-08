---
name: e2e-after-scan-codebase
description: 'Cẩm nang vận hành kiểm thử End-to-End (E2E) Local đúc kết sau khi quét hệ thống: Lưu trữ file clip bằng chứng chuẩn, hướng dẫn cách khởi chạy và dừng toàn bộ 8/8 services, các lưu ý sống còn về Playwright/SSL/Locators, và quy trình phân tích clip 1 FPS để Step 5 tái sử dụng ngay mà không cần scan lại.'
---

# CẨM NANG VẬN HÀNH KIỂM THỬ E2E LOCAL (`STEP-0-e2e-after-scan-codebase.md`)

> [!IMPORTANT]
> **Mục Đích & Phạm Vi Tái Sử Dụng:**
> Đây là bản đúc kết kiến thức vận hành thực tế toàn bộ môi trường kiểm thử E2E cục bộ sinh ra sau khi hoàn thành **Bước 0 (`STEP-0-scan-e2e-local.md`)**.
> Khi tiến hành kiểm thử các tính năng mới ở **Step 5 (`STEP-5-write-e2e-test.md`)**, AI **KHÔNG CẦN QUÉT LẠI HỆ THỐNG NỮA**. Toàn bộ địa chỉ cổng mạng, câu lệnh khởi động services, cách quay clip video, và các lưu ý sống còn đều được đóng gói đầy đủ tại tài liệu này để tái sử dụng ngay lập tức.

---

## 1. Sản Phẩm Đầu Ra Chuẩn Sau Scan (Verified Scan Artifacts)

Mỗi lần hoàn tất quét E2E, hệ thống bắt buộc lưu lại bộ bằng chứng chuẩn mực đại diện:

1. **File Clip Video Bằng Chứng 1 (Giao Diện Thật PostHog Web :8080 - Probe):**
   👉 [`artifacts/videos/real-posthog-ui_video.webm`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/real-posthog-ui_video.webm) *(Độ dài: 15 giây, quay luồng tải trang PostHog Web, preflight setup wizard và branding logo)*.
2. **File Clip Video Bằng Chứng 2 (Giao Diện Microservices Hub Thật :5001 & :3000):**
   👉 [`artifacts/videos/local-services-probe_video.webm`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/local-services-probe_video.webm) *(Độ dài: 6 giây, quay hành động nhập form tạo đơn hàng bằng native selector, bắn sự kiện sang Node.js Worker và nhận Toast thành công)*.
3. **File Clip Video Bằng Chứng 3 (Midscene AI Vision Thực Chiến :5001):**
   👉 [`artifacts/videos/midscene-real-probe_video.webm`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/midscene-real-probe_video.webm) *(Độ dài: 38 giây, Midscene AI dùng Vision Model đọc hiểu tiếng Việt, tự động điền form, click nút và tự assert kiểm tra màu Toast/Ledger mà không dùng selector)*.
4. **File Clip Video Bằng Chứng 4 (PostHog Web Full User Journey :8080 - Đi Sâu Vào Dashboard):**
   👉 [`artifacts/videos/posthog-full-journey_video.webm`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/posthog-full-journey_video.webm) *(Độ dài: 35 giây, tự động vượt qua Preflight Onboarding -> Đăng nhập tài khoản Admin -> Đi thẳng vào màn hình làm việc chính thức "What do you want to do with PostHog?" tại `/project/1/onboarding`)*.
5. **Khung Hình Trực Quan Tiêu Biểu (1 FPS Keyframe Proof):**
   👉 [`artifacts/videos/frames/real-posthog-ui_video_frame_013.png`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/frames/real-posthog-ui_video_frame_013.png) *(Hình ảnh chứng minh giao diện PostHog thật hiển thị trọn vẹn tại `http://localhost:8080/`)*.
   👉 [`artifacts/videos/frames/local-services-probe_video_frame_004.png`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/frames/local-services-probe_video_frame_004.png) *(Hình ảnh chứng minh giao diện Hub đơn hàng hiển thị 🟢 Processed)*.
   👉 [`artifacts/videos/frames/midscene-real-probe_video_frame_030.png`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/frames/midscene-real-probe_video_frame_030.png) *(Hình ảnh Midscene AI tạo thành công đơn hàng iPad Pro M4 kèm Toast xanh)*.
   👉 [`artifacts/videos/frames/posthog-full-journey_video_frame_033.png`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/frames/posthog-full-journey_video_frame_033.png) *(Hình ảnh giao diện PostHog Platform chính thức với 6 module phân tích)*.
6. **Báo Cáo Đối Chiếu Thị Giác Tự Động & HTML Visual Report:**
   👉 [`artifacts/videos/review-real-posthog-ui.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/review-real-posthog-ui.md).
   👉 [`artifacts/videos/review-local-services-probe.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/review-local-services-probe.md).
   👉 [`artifacts/videos/review-midscene-real-probe.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/review-midscene-real-probe.md).
   👉 [`artifacts/videos/review-posthog-full-journey.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/review-posthog-full-journey.md).
   👉 Báo cáo HTML trực quan Midscene: [`posthog/playwright/midscene_run/report/`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/posthog/playwright/midscene_run/report/).

---

## 2. Bản Đồ 8/8 Cổng Dịch Vụ & Cách Khởi Động (Services Topology & Startup)

### 2.1. Bản Đồ Trạng Thái 8/8 Services (100% `🟢 ONLINE`)

| Dịch Vụ | Port | Endpoint Kiểm Tra | Trạng Thái | Vai Trò Trong Hệ Thống |
| :--- | :---: | :--- | :---: | :--- |
| **PostHog Web App** | `8080` | `http://localhost:8080/` | `🟢 ONLINE` | **Giao diện Web thật 100% của PostHog** (Setup / Login / Dashboard) |
| **PostHog Backend API** | `8000` | `http://localhost:8000/api/` | `🟢 ONLINE` | Granian ASGI / Django API & Data Ingestion |
| **Order Service** | `5001` | `http://localhost:5001/` | `🟢 ONLINE` | Python Backend API & Event Hub mô phỏng nghiệp vụ |
| **Worker Service** | `3000` | `http://localhost:3000/process-event` | `🟢 ONLINE` | Node.js Streaming Worker xử lý sự kiện bất đồng bộ |
| **PostgreSQL** | `5432` | `localhost:5432` | `🟢 ONLINE` | Container `posthog-db-1` (Postgres 15) lưu trữ Relational Data |
| **ClickHouse HTTP** | `8123` | `http://localhost:8123/ping` | `🟢 ONLINE` | Container `posthog-clickhouse-1` (ClickHouse 26) phân tích sự kiện |
| **Redis Cache** | `6379` | `localhost:6379` | `🟢 ONLINE` | Container `posthog-redis7-1` (Redis 7.2) quản lý Cache & Task Queue |
| **Apache Kafka** | `9092` | `localhost:9092` | `🟢 ONLINE` | Container `posthog-kafka-1` (Redpanda 25) làm Message Broker |

---

### 2.2. Khởi Động & Dừng Dịch Vụ Siêu Tốc (1-Click Startup & Stop)

Hệ thống đã được đóng gói toàn bộ vào 2 lệnh duy nhất tại thư mục gốc:

#### 🔹 Khởi động trọn gói 8/8 Services & Giao diện Web:
```bash
./run
```
*(Lệnh tự động bật DBs, Kafka, ClickHouse, Redis, PostHog Web :8080 & :8000, Order Service :5001, Node Worker :3000 và kiểm tra health check `[OK]`)*.

#### 🔹 Dừng và giải phóng sạch toàn bộ cổng mạng:
```bash
./stop
```

#### 🔹 Kiểm tra sức khỏe nhanh 8/8 services bất kỳ lúc nào:
```bash
python3 scripts/run_e2e_local.py --check-services
```

---

## 3. Quy Trình Chạy E2E Playwright Kèm Quay Clip Màn Hình

Để chạy kịch bản E2E cho một tính năng bất kỳ và tự động xuất ra video clip:
```bash
python3 scripts/run_e2e_local.py --spec playwright/e2e/<tên_kich_ban>.spec.ts
```

### Script thực hiện tự động:
1. Nạp biến môi trường `PLAYWRIGHT_VIDEO=on` và `BASE_URL=http://localhost:8080`.
2. Khởi chạy Chromium Headless/Headed, tương tác với form và click nút bấm.
3. Thu gom file video quay được từ thư mục test-results và lưu thẳng vào:
   📁 `artifacts/videos/<tên_kich_ban>_video.webm`.

---

## 4. 6 Lưu Ý "Sống Còn" Khi Viết & Chạy Test E2E (Critical Gotchas)

Khi viết test E2E tại **Step 5 (`STEP-5-write-e2e-test.md`)**, kỹ sư và AI bắt buộc phải tuân thủ 6 nguyên tắc đã đúc kết từ thực tế:

### ⚠️ Lưu Ý 1: Cờ Quay Video Trong Playwright
* **LỖI THƯỜNG GẶP:** Truyền flag `--video=on` trên dòng lệnh Playwright CLI sẽ gây lỗi `error: unknown option '--video=on'`.
* **CÁCH CHUẨN:** Bắt buộc cấu hình `use: { video: 'on' }` trong [`posthog/playwright/playwright.config.ts`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/posthog/playwright/playwright.config.ts) hoặc thiết lập biến môi trường `export PLAYWRIGHT_VIDEO=on`. Script [`run_e2e_local.py`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/SKILL%20Code/scripts/run_e2e_local.py) đã tích hợp sẵn cơ chế này.

### ⚠️ Lưu Ý 2: Xử Lý Chuyển Hướng HTTPS (SSL Redirect) Ở Môi Trường Local
* **HIỆN TƯỢNG:** Web server Granian/Django mặc định ép chuyển hướng sang HTTPS (`301 Moved Permanently`), dẫn đến truy cập HTTP bị ngắt kết nối (`Connection reset by peer`).
* **CÁCH XỬ LÝ:** Khi chạy container Web App trên cổng `8080`, luôn đặt cờ `-e DISABLE_SECURE_SSL_REDIRECT=1` (đã được cấu hình tự động trong [`start_posthog_web.sh`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/scripts/start_posthog_web.sh)).

### ⚠️ Lưu Ý 3: Tránh Lỗi Playwright Strict Mode Violation
* **LỖI THƯỜNG GẶP:** Dùng selector chung chung như `page.locator('text=PostHog')` sẽ bị crash nếu trên màn hình có nhiều phần tử chứa chữ "PostHog".
* **CÁCH CHUẨN:**
  * Luôn dùng cờ `{ exact: true }`: `page.getByText('PostHog', { exact: true })`.
  * Hoặc ưu tiên dùng Test ID: `page.getByTestId('data-attr-name')` (PostHog đã cấu hình `testIdAttribute: 'data-attr'` trong Playwright config).

### ⚠️ Lưu Ý 4: Bộ Lọc Log Scoped Theo Feature (Loại Bỏ 100% Log Rác)
* **HIỆN TƯỢNG:** Hệ thống PostHog liên tục bắn hàng trăm request polling background (`/decide/`, heartbeat telemetry, HMR, asset `.js.map`).
* **CÁCH XỬ LÝ:** Sau khi quay video, **BẮT BUỘC** gọi script phân tích kèm cờ `--feature`:
  ```bash
  python3 scripts/analyze_e2e_clip.py --video artifacts/videos/<tên_clip>.webm --feature <tên_feature>
  ```
  Script sẽ tự động lọc sạch 100% log rác và chỉ giữ lại log lỗi Console và HTTP status của chính tính năng đó.

### ⚠️ Lưu Ý 5: Bóc Tách Ảnh 1 FPS Bằng FFMPEG (Thị Giác Hóa Không Rác Bộ Nhớ)
* Script `analyze_e2e_clip.py` tự động cắt 1 ảnh mỗi giây (`1.0 FPS Smart Sampling`) vào thư mục [`artifacts/videos/frames/`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/artifacts/videos/frames/).
* AI có thể dùng công cụ `read_file` mở trực tiếp các file ảnh `.png` để "nhìn tận mắt" giao diện thực tế mà không cần xem toàn bộ clip video nặng.

### ⚠️ Lưu Ý 6: Quy Chuẩn Phản Hồi Khi Lệch Giao Diện (Feedback Loop)
* Nếu ảnh trích xuất từ video không khớp với đặc tả [`specs/ui-flow-e2e-<feature>.md`](file:///Users/macos/Desktop/phongvan/python/github%20project%20microservices/SKILL%20Code/STEP-2-write-testcases-feature.md):
  * **CẤM SỬA TEST HAY SỬA FILE ĐẶC TẢ!**
  * Lập tức trích dẫn file ảnh chụp bị lỗi (ví dụ: `frame_014.png`) và gửi Feedback về cho **Step 4 (`STEP-4-implement-feature.md`)** để sửa mã nguồn giao diện.

### ⚠️ Lưu Ý 7: Kích Hoạt Bộ Não Midscene AI (`@midscene/web`) Cho E2E Tự Động
* **LỢI ÍCH VƯỢT TRỘI:** Thay vì phải mò mẫm từng selector CSS/XPath dễ bị vỡ (fragile), Midscene tích hợp trực tiếp vào Playwright (`PlaywrightAiFixture`) cho phép viết test bằng ngôn ngữ tự nhiên:
  * `await aiAction('Click vào nút Đăng nhập')`
  * `await aiAssert('Phải hiển thị Toast xanh thông báo thành công')`
* **CẤU HÌNH BẮT BUỘC:**
  * Cài đặt thư viện: `npm install -D @midscene/web` (trong thư mục `posthog/playwright/`).
  * Khai báo API Key trong `.env`: `OPENAI_API_KEY=...` kèm `MIDSCENE_MODEL_NAME=gemini-3.5-flash-lite` và `MIDSCENE_MODEL_FAMILY=gemini`.
  * Midscene kết hợp hoàn hảo với Playwright video recorder: vừa tự động thao tác chuẩn xác theo ngữ nghĩa, vừa sinh ra file clip video và HTML visual replay cho reviewer!

### ⚠️ Lưu Ý 8: Tiêu Chuẩn Thiết Kế Kịch Bản Dài (Full User Journey E2E)
* **PHÂN TẦNG KỊCH BẢN:**
  * **Tầng 1 - Probe Test (10s):** Dùng để khảo sát kiểm tra server sống/chết (smoke probe).
  * **Tầng 2 - Journey Test (30s - 90s):** Bắt buộc phải dẫn dắt người dùng qua toàn bộ vòng đời tính năng (ví dụ: Landing Page -> Onboarding Wizard -> Tạo tài khoản Admin -> Vào Dashboard -> Kiểm tra Menu điều hướng & Biểu đồ).
* **QUY TẮC TIMEOUT & CHUYỂN TRANG:**
  * Luôn đặt `test.setTimeout(180000)` (3 phút) ở đầu kịch bản Journey Test.
  * Khi chuyển giữa các view lớn (ví dụ từ Onboarding sang Dashboard), luôn dùng `await page.waitForLoadState('networkidle')` hoặc `await page.waitForURL(...)` trước khi gọi bước thao tác tiếp theo.
* **CẤU TRÚC PHÂN CHẶNG (MULTI-PHASE EXECUTION):**
  * Chia rõ ràng thành các Phase: `Phase 1: Preflight/Onboarding` -> `Phase 2: Authentication/Registration` -> `Phase 3: Core Workspace/Dashboard Inspection`.
  * Mỗi Phase kết thúc bằng ít nhất 1 câu lệnh `aiAssert` hoặc `expect` để đảm bảo hệ thống không bị "rớt nhịp" trước khi bước sang Phase kế tiếp.

---

## 5. Hướng Dẫn Tái Sử Dụng Nhanh Cho Step 5 (Reuse Guide)

Khi triển khai viết test E2E cho một tính năng mới ở **Step 5**:
1. Đọc tài liệu này để lấy URL gốc: `http://localhost:8080`.
2. Tạo file kịch bản: `posthog/playwright/e2e/<tên_feature>.spec.ts`.
3. Chạy test và tự động quay video clip:
   ```bash
   python3 scripts/run_e2e_local.py --spec playwright/e2e/<tên_feature>.spec.ts
   ```
4. Bóc tách ảnh và đối chiếu giao diện:
   ```bash
   python3 scripts/analyze_e2e_clip.py --video artifacts/videos/<tên_feature>_video.webm --feature <tên_feature>
   ```
5. Đọc báo cáo review: `artifacts/videos/review-<tên_feature>.md`. Hoàn tất quy trình E2E mà không cần tốn thời gian scan lại!
