# Giá ca máy do Sở Xây dựng công bố

`gia_ca_may_cong_bo.csv` — mỗi dòng: tỉnh, mã vùng (HN-V1/HN-V2, cùng phạm vi vùng với giá nhân công QĐ 2036), mã máy PL IV TT 37, tên ngắn (phần ghi ở dòng máy), mã nhóm, giá ca máy (đồng/ca, chưa VAT), văn bản, thời hạn hiệu lực, căn cứ giá nhiên liệu.

| Văn bản | Phạm vi | Hiệu lực | Nguồn trích |
|---|---|---|---|
| QĐ 2075/QĐ-SXD ngày 31/10/2026, Sở XD Hà Nội | 778 máy × 2 vùng | từ 31/10/2026 (thay QĐ 2037 ngày 26/10/2026) | PDF người dùng cung cấp 17/11/2026 (pdftotext -layout); đối chiếu từng máy với CSDL GXD trên máy người dùng |

**Kiểm tra:** 778/778 mã có trong GXD; 771 khớp đúng; 6 máy GXD cao hơn đúng 100 đ (M101.0701, M101.0901, M102.0101, M112.0704, M112.3202, M201.0005) — giữ số của bản công bố; M203.0021: bản công bố chỉ ghi 297.600 ở Vùng I, Vùng II để trống (GXD ghi 297.600 cả hai vùng) — skill để trống Vùng II. GXD có thêm 49 mã (biến thể "a", "b", mã thiết bị thí nghiệm điện) không có trong bản công bố — không đưa vào.

**Lưu ý bản PDF:** trang đầu để trống số và ngày ("Số: /QĐ-SXD … ngày tháng năm 2026"; phụ lục ghi "Quyết định số ……"), có chữ ký Phó Giám đốc. Số hiệu, ngày lấy theo nội dung "thay thế QĐ 2037" và nguồn thứ cấp — nên lưu bản có số khi đưa vào hồ sơ. Phần thuyết minh mục III ghi "tính toán cho 3 vùng" nhưng bảng chỉ có 2 vùng; mục II còn dẫn NĐ 10/2021 (đã hết hiệu lực) — lỗi biên tập, không ảnh hưởng bảng giá.

**Kiểm chứng công thức:** `scripts/gia_ca_may.py` (PL IV TT 37) với diesel 29.250 đ/lít, xăng 24.910, điện 1.987 và NC HN-V1 cho M101.0101 = 2.524.467 (công bố 2.524.500), M105.0202 = 4.481.857 (4.481.900), M108.0103 = 1.332.843 (1.332.800) — khớp sau làm tròn 100 đ; CNL M101.0101 = 1.295.483 đúng bằng cột chi phí nhiên liệu của bản công bố.

**Chênh lệch khi lập dự toán:** QĐ 2075 Phần IV mục 2 cho bổ sung chênh lệch giá nhiên liệu và nhân công giữa thời điểm lập dự toán và thời điểm công bố — tính lại bằng `gia_ca_may.py` với giá tại thời điểm lập.

**Chưa có:** QĐ 2037 (26/10–30/10/2026); giá ca máy Hải Phòng, Hưng Yên theo TT 37; nối tên máy trong định mức TT 38 với mã PL IV để điền tự động vào `can-gia`.
