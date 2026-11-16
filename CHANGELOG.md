# Changelog — skill dự toán xây dựng Việt Nam (`du-toan-xay-dung-vn`)

## [1.0.0] — 2026-10-16 (baseline)
- Bản gốc từ `skill-DT-main.zip` (ngày file 16/10/2026), đẩy nguyên trạng lên `rinnef007/DT-ver2.0` làm baseline cho v2.0.
- Hệ văn bản từ 01/7/2026: NĐ 206/2026, TT 36/2026 (+ QĐ 1538), TT 37/2026, TT 38/2026, TT 40/2026.
- Quy trình 7 bước, 13 script Python, dữ liệu TT 38 (~9.050 mã), 5 bộ ví dụ chạy thử.
- Ngày rà soát pháp lý gần nhất: 16/10/2026.

> Lưu ý về dữ liệu TT 38: bản gốc v1 dùng 6 file `data/tt38/*.csv.gz` (gzip). Do công cụ
> snapshot của Muse chỉ đẩy file text UTF-8, từ 16/11/2026 dữ liệu TT 38 trên repo chuyển
> sang dạng CSV thường (giải nén từ đúng các file `.csv.gz` đó, nội dung không đổi).
> Script `dutoan_core.py` đọc được cả `.csv` và `.csv.gz`.

## [Unreleased] — 2.0.0 (đang làm, theo PLAN-nang-cap-skill-DT-ver2.0.md)
- Dữ liệu TT 38 trên repo chuyển từ `.csv.gz` sang `.csv` thường (6 file, nội dung không đổi),
  để đẩy được bằng snapshot; script vẫn đọc được cả hai dạng.
- `dinh_muc_tt38.csv` (13 MB) chia thành 3 phần `dinh_muc_tt38_p1..p3.csv` (17.506 +
  17.506 + 17.504 dòng, gộp lại đúng bằng file gốc, đã kiểm chứng từng dòng) vì file gộp
  vượt giới hạn kích thước yêu cầu khi đẩy lên GitHub; `dutoan_core.py` đọc được cả file
  gộp, file `.csv.gz`, hoặc 3 phần.
- Sửa lỗi v1: `dutoan_core.py` chỉ nạp định mức TT 38 khi có file `dinh_muc_tt38.csv.gz`
  (kiểm tra sự tồn tại của `.csv.gz` rồi mới đọc `.csv`), nên với dữ liệu `.csv` thường
  thì `tinh`/`tra` không thấy mã TT 38. Nay kiểm tra cả `.csv` và `.csv.gz`.
- Sửa `dutoan.py tra --tai-nguyen`: trước đây mở trực tiếp file `.csv.gz` bằng gzip,
  nay dùng `doc_csv` nên đọc được cả `.csv` và `.csv.gz`.
- Rà soát lại pháp lý hệ 2026, đọc nguyên văn NĐ 206/2026.
- Khép lỗ hổng dữ liệu TT 38 (79 mã cần kiểm tra, 14 khối mã, PL VII/VIII).
- Thêm lớp học/thực hành và ví dụ Nhà để xe chuyển mã TT 38.
- Đối chiếu mẫu GXD/Excel/Word (`DutoanGXD1.xlsm`).
- Thêm test chạy lại toàn bộ ví dụ.
