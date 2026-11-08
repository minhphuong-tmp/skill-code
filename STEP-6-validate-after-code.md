---
name: validate-after-code
description: 'Kỹ năng tự kiểm duyệt mã nguồn sau khi viết/sửa code: AI tự động chạy script `audit_codebase.py` để quét toàn bộ thay đổi trong Git (staged, unstaged, untracked) dưới 0.1s, đối chiếu với các luật kiến trúc trong `STEP-0-code-after-scan-codebase.md`, và tự động sửa lại code nếu có lỗi trước khi báo cáo hoàn thành. Không dùng grep thủ công.'
---

# Kỹ Năng Tự Kiểm Duyệt Sau Khi Code (`validate-after-code`)

> [!IMPORTANT]
> **Quy Tắc Tốc Độ & Hiệu Suất:**
> Khi cần kiểm tra các file vừa sửa trong Git, AI **TUYỆT ĐỐI KHÔNG dùng grep thủ công hoặc đọc từng file một** (cách đó rất chậm, tốn hàng chục tool calls và dễ bỏ sót lỗi).
> Thay vào đó, AI chỉ cần thực hiện đúng **1 thao tác duy nhất**: Chạy script `audit_codebase.py`. Script này dùng Git và Python quét toàn bộ thay đổi chỉ trong **0.05 giây**!

---

## Quy Trình 3 Bước Tự Kiểm Duyệt Bắt Buộc

Mỗi khi AI vừa hoàn thành xong việc viết code hoặc sửa đổi các file theo yêu cầu của người dùng, AI phải thực hiện tuần tự 3 bước sau trước khi thông báo hoàn tất:

### Bước 1: Chạy Script Kiểm Tra Git Diff
Thực thi lệnh kiểm tra:
```bash
python3 scripts/audit_codebase.py
```

### Bước 2: Đọc Data Báo Cáo Từ Output Của Script
Script sẽ tự động đọc `git diff` (cả unstaged, staged và untracked files) và đối chiếu với các bất biến trong [`skills/STEP-0-code-after-scan-codebase.md`](skills/STEP-0-code-after-scan-codebase.md):
- **Trường hợp 1 (Xanh - Thành công):**
  Output hiển thị: `🎉 TẤT CẢ FILE THAY ĐỔI ĐỀU ĐẠT CHUẨN 100% THEO SKILL!`
  $\rightarrow$ AI chính thức hoàn thành nhiệm vụ và báo cáo kết quả sạch sẽ cho người dùng.
- **Trường hợp 2 (Đỏ - Vi phạm):**
  Output hiển thị danh sách cụ thể: `❌ FILE: ... Dòng ...: Vi phạm ...`
  $\rightarrow$ Chuyển ngay sang Bước 3!

### Bước 3: Tự Động Sửa Lỗi (Self-Healing)
Nếu script phát hiện vi phạm:
1. Output của script đã chỉ đích danh tên file, số dòng và **mục điều luật tương ứng trong [`skills/STEP-0-code-after-scan-codebase.md`](skills/STEP-0-code-after-scan-codebase.md)**.
2. AI đọc đúng mục được chỉ dẫn trong [`skills/STEP-0-code-after-scan-codebase.md`](skills/STEP-0-code-after-scan-codebase.md) để tra cứu bối cảnh, quy chuẩn và mẫu code chuẩn mực của dự án.
3. AI sửa lại mã nguồn cho khớp 100% với quy chuẩn.
4. Chạy lại `python3 scripts/audit_codebase.py` để xác nhận toàn bộ lỗi đã được khắc phục triệt để.
