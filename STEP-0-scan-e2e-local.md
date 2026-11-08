---
name: scan-e2e-local
description: 'Meta-Skill quét và khảo sát năng lực kiểm thử End-to-End (E2E) trên môi trường Local: Đọc cẩm nang kiến trúc `STEP-0-code-after-scan-codebase.md`, tự động phát hiện và kiểm tra các services local, chạy E2E test quay clip hoàn chỉnh với từng service, ghi rõ lý do nếu service offline, bắn seed webhook mock data, xuất clip video + keyframes 1 FPS làm bằng chứng thực tế, và đúc kết toàn bộ kinh nghiệm thành file `STEP-0-e2e-after-scan-codebase.md`.'
---

# META-SKILL: QUÉT & KHẢO SÁT NĂNG LỰC E2E LOCAL XUẤT CLIP HOÀN CHỈNH (`scan-e2e-local`)

> [!IMPORTANT]
> **Mục Đích & Yêu Cầu Đầu Ra (Definition of Done):**
> Thực hiện quy trình rà soát thực tế toàn bộ môi trường chạy cục bộ (Runtime Local Environment) của **bất kỳ dự án phần mềm nào**. **Đầu ra BẮT BUỘC phải có clip video E2E hoàn chỉnh làm bằng chứng thực nghiệm:**
> 1. Đọc cẩm nang kiến trúc `STEP-0-code-after-scan-codebase.md` (hoặc cấu hình Docker/mạng) để nắm rõ danh sách toàn bộ services, web apps và cổng kết nối của dự án.
> 2. Khởi tạo các services local và kiểm tra trạng thái sức khỏe từng cổng mạng.
> 3. Với các service **chưa chạy được hoặc không có kết quả ở Local**, bắt buộc **ghi rõ lý do kỹ thuật** (thiếu credentials cloud, container đang build, tiến trình phụ trợ chưa bật...).
> 4. Bắn thử nghiệm dữ liệu mẫu qua script seed dữ liệu của dự án (`scripts/seed_webhook.py` hoặc tương đương) để kích hoạt luồng xử lý ngầm.
> 5. **Chạy kịch bản E2E Probe thực tế với cờ quay video:** Bắt buộc thu được file clip video hoàn chỉnh (`.webm`), bóc tách ảnh 1 FPS và tạo báo cáo review thị giác.
> 6. Đúc kết trọn vẹn toàn bộ kinh nghiệm và bằng chứng vào file:
>    📄 **`SKILL Code/STEP-0-e2e-after-scan-codebase.md`** (Cẩm nang E2E Local sau khi quét để Step 5 tái sử dụng ngay).

---

## Bộ 4 Sản Phẩm Bắt Buộc Phải Có Sau Khi Scan E2E Local

Sau khi chạy xong kỹ năng này, thư mục dự án BẮT BUỘC phải xuất hiện đầy đủ 4 thành phần bằng chứng:
1. 📹 **File Clip Video E2E Hoàn Chỉnh:** `artifacts/videos/<probe_name>_video.webm` (Ghi lại mượt mà toàn bộ hành trình browser tải trang, tương tác UI thật của service local).
2. 📸 **Chuỗi Keyframes 1 FPS:** `artifacts/videos/frames/<probe_name>_video_frame_xxx.png` (Ảnh bóc tách từng giây chứng minh UI thật đã render thành công).
3. 📝 **Báo Cáo Phân Tích Thị Giác:** `artifacts/videos/review-<probe_name>.md` (Lọc sạch log rác background, chỉ giữ log dịch vụ).
4. 📄 **File Cẩm Nang Tái Sử Dụng:** `SKILL Code/STEP-0-e2e-after-scan-codebase.md` (Chứa link clip bằng chứng, bản đồ port và quy tắc chạy cho Step 5).

---

## Quy Trình 4 Bước Khảo Sát & Xuất Clip E2E Bằng Chứng

Khi nhận lệnh: *"run skill scan E2E local"*, AI thực hiện:

### Bước 1: Khám Phá & Kiểm Tra Sức Khỏe Toàn Bộ Dịch Vụ Của Dự Án
AI tự động xác định danh sách dịch vụ thông qua:
1. File cẩm nang kiến trúc `STEP-0-code-after-scan-codebase.md` (Mục 5).
2. Cấu hình container (`docker-compose*.yml`), biến môi trường (`.env`), hoặc script khởi chạy (`run.sh`, `Makefile`, `Procfile`).
3. Thực thi lệnh runner kiểm tra cổng mạng:
```bash
python3 scripts/run_e2e_local.py --check-services
```

AI phân loại và ghi chép chi tiết vào báo cáo:
- **Dịch vụ `🟢 ONLINE`:** Ghi nhận cổng, endpoint phản hồi và vai trò trong hệ thống.
- **Dịch vụ `🔴 OFFLINE`:** Bắt buộc phân loại chính xác vào **1 trong 3 nhóm nguyên nhân chuẩn kỹ thuật** để Step 5 biết cách xử lý:
  1. **Nhóm 1: Phụ thuộc Cloud / Dịch vụ bên thứ ba (External Dependency):**
     * *Nguyên nhân:* Thiếu AWS S3, Stripe Webhook, Third-party OAuth credentials trong môi trường local.
     * *Chỉ thị cho Step 5:* Tuyệt đối không gọi thật; bắt buộc sử dụng mock data hoặc script seed webhook.
  2. **Nhóm 2: Tiến trình phụ trợ chưa bật (Auxiliary Process / Microservices):**
     * *Nguyên nhân:* Các microservice vệ tinh, worker ngầm, hoặc API server chưa được bật background.
     * *Chỉ thị cho Step 5:* Cung cấp lệnh bật nhanh tương ứng (ví dụ: `python3 <worker>.py &` hoặc `npm run worker &`).
  3. **Nhóm 3: Hạ tầng Container nền (Docker Infrastructure):**
     * *Nguyên nhân:* Docker daemon chưa bật, container DB/Cache/Queue chưa sẵn sàng hoặc bị chiếm cổng.
     * *Chỉ thị cho Step 5:* Báo rõ cần khởi động lại container qua `./run` hoặc `docker compose up -d`.

---

### Bước 2: Bắn Thử Nghiệm Mock Data & Seed Webhook
Kích hoạt luồng dữ liệu ngầm giữa các dịch vụ để kiểm tra pipeline:
```bash
python3 scripts/seed_webhook.py --target all --event "scan_e2e_probe" --user "user_probe_local"
```
*(Nếu dự án có API endpoint ingestion hoặc webhook riêng, gửi HTTP POST mock data tương ứng)*.
Ghi nhận: Endpoint nào tiếp nhận thành công (HTTP 200/201), endpoint nào từ chối và mã lỗi trả về.

---

### Bước 3: Chạy Test E2E Probe & Full Journey Trên Service Local & Xuất Clip Hoàn Chỉnh
AI tự động tìm kiếm hoặc sinh kịch bản E2E kiểm thử Web UI chính của dự án:
1. **Tìm framework E2E của dự án:** Kiểm tra xem dự án đang dùng Playwright, Cypress, hay Puppeteer (tìm file config hoặc thư mục test).
2. **Xác định kịch bản kiểm thử:**
   - Ưu tiên chạy các kịch bản probe/smoke test đã có trong thư mục E2E của dự án (ví dụ `playwright/e2e/`, `e2e/`, `tests/e2e/`).
   - Nếu dự án chưa có test E2E, AI tự động tạo 1 file probe ngắn trỏ vào Web UI chính được phát hiện ở Bước 1.
3. **Thực thi runner có cờ quay video:**
```bash
python3 scripts/run_e2e_local.py --spec <duong_dan_test_spec>
```

> [!IMPORTANT]
> **TIÊU CHUẨN ĐỘ SÂU BẰNG CHỨNG (CẤM KỊCH BẢN NÔNG / MÀN HÌNH TRẮNG):**
> • **Kịch bản Web App chính:** Bắt buộc phải vượt qua màn hình loading/preflight, tương tác form (login/onboarding) và ghi nhận giao diện không gian làm việc bên trong, không dừng ở màn hình trắng hoặc popup khởi động.
> • **Kịch bản có AI (Midscene AI):** Khuyến khích tích hợp `@midscene/web` (`PlaywrightAiFixture`, `aiAction`, `aiAssert`) để kiểm thử thị giác ngữ nghĩa không phụ thuộc selector CSS.

Runner tự động:
1. Mở trình duyệt Chromium, thực hiện luồng truy cập và tương tác form/nút bấm.
2. Thu thập và đóng gói file video vào: `artifacts/videos/<probe_name>_video.webm`.
3. AI kích hoạt ngay script phân tích video:
   ```bash
   python3 scripts/analyze_e2e_clip.py --video artifacts/videos/<probe_name>_video.webm --feature <probe_name>
   ```
4. Script tự động bóc tách chuỗi ảnh 1 FPS vào `artifacts/videos/frames/` và xuất báo cáo `review-<probe_name>.md`.

---

### Bước 4: Đúc Kết Toàn Bộ Kinh Nghiệm Ra File `STEP-0-e2e-after-scan-codebase.md`
AI dùng `write_file` hoặc `edit_file` cập nhật tài liệu cẩm nang E2E riêng của dự án:
📄 `SKILL Code/STEP-0-e2e-after-scan-codebase.md`

Nội dung bắt buộc cập nhật trong file đúc kết:
1. **Đính kèm đường link file clip video E2E chuẩn mực** vừa quay được ở Bước 3.
2. **Đính kèm ảnh keyframe tiêu biểu** chứng minh giao diện thật đã tải thành công.
3. Bản đồ trạng thái thực tế của toàn bộ các dịch vụ ở local (kèm lý do các service offline nếu có).
4. Hướng dẫn seed webhook và mock event chuẩn của dự án.
5. Hướng dẫn chạy test E2E có quay video màn hình.
6. Hướng dẫn sử dụng script bóc tách keyframes 1 FPS và lọc log scoped.
7. Đảm bảo tài liệu này sẵn sàng 100% để **Step 5 (`STEP-5-write-e2e-test.md`)** kế thừa ngay mà không cần scan lại từ đầu!
2. **Đính kèm ảnh keyframe tiêu biểu** chứng minh giao diện thật đã tải thành công.
3. Bản đồ trạng thái thực tế của các dịch vụ ở local (kèm lý do các service offline nếu có).
4. Hướng dẫn seed webhook và mock event chuẩn.
5. Hướng dẫn chạy test E2E có quay video màn hình.
6. Hướng dẫn sử dụng script bóc tách keyframes 1 FPS và lọc log scoped.
7. Đảm bảo tài liệu này sẵn sàng 100% để **Step 5 (`STEP-5-write-e2e-test.md`)** kế thừa ngay mà không cần scan lại từ đầu!
