# Changelog — skill dự toán xây dựng Việt Nam (`du-toan-xay-dung-vn`)

## [1.0.0] — 2026-10-16 (baseline)
- Bản gốc từ `skill-DT-main.zip` (ngày file 16/10/2026), đẩy nguyên trạng lên `rinnef007/DT-ver2.0` làm baseline cho v2.0.
- Hệ văn bản từ 01/7/2026: NĐ 206/2026, TT 36/2026 (+ QĐ 1538), TT 37/2026, TT 38/2026, TT 40/2026.
- Quy trình 7 bước, 13 script Python, dữ liệu TT 38 (~9.050 mã), 5 bộ ví dụ chạy thử.
- Ngày rà soát pháp lý gần nhất: 16/10/2026.

> Lưu ý về dữ liệu TT 38: 6 file `data/tt38/*.csv.gz` là file nhị phân (gzip) nên không đẩy được bằng
> công cụ snapshot của Muse (chỉ đẩy file text UTF-8). 6 file này sẽ được tải lên repo bằng giao diện
> web GitHub ngay sau commit baseline này. Script `dutoan_core.py` đọc được cả `.csv` và `.csv.gz`.

## [Unreleased] — 2.0.0 (đang làm, theo PLAN-nang-cap-skill-DT-ver2.0.md)
- Rà soát lại pháp lý hệ 2026, đọc nguyên văn NĐ 206/2026.
- Khép lỗ hổng dữ liệu TT 38 (79 mã cần kiểm tra, 14 khối mã, PL VII/VIII).
- Thêm lớp học/thực hành và ví dụ Nhà để xe chuyển mã TT 38.
- Đối chiếu mẫu GXD/Excel/Word (`DutoanGXD1.xlsm`).
- Thêm test chạy lại toàn bộ ví dụ.
