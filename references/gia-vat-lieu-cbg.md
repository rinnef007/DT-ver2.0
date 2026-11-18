# Giá vật liệu theo công bố giá (CBG) — Hà Nội, Hải Phòng, Hưng Yên

Lệnh `scripts/gia_vat_lieu.py` (ds | tra | goi-y). Nguồn: tệp `GVT_<kỳ>_<năm>_<TỈNH>.csv` trong `<thư mục>/<HaNoi|HaiPhong|HungYen>/GVT/` — định dạng thư viện giá của Dự toán GXD (UTF-16, tab; tên, đơn vị, giá, nguồn, ghi chú, khu vực). Trên máy người dùng mặc định `D:\GXD\Dulieu` (đặt `DT_GVT_DIR` hoặc `--thu-muc` nếu khác).

**Không chép dữ liệu GXD vào repo** (repo công khai; thư viện giá là sản phẩm biên tập có bản quyền của GXD) — skill chỉ đọc trên máy. Có thể tự lập tệp cùng định dạng từ bản CBG gốc của Sở XD.

- `ds`: các kỳ có sẵn theo tỉnh (sắp theo thời gian; Q3 = tháng 9, QII = tháng 6, T08 = tháng 8).
- `tra --tinh HN|HP|HY --tu-khoa … [--ky Q3/2026] [--khu-vuc …]`: khớp đúng chuỗi có dấu; chỉ khi không có kết quả mới thử bỏ dấu và in cảnh báo (vd. "cap" khớp cả "cáp" và "cấp").
- `goi-y --tinh … --data <hồ sơ>`: với từng vật liệu trong định mức của hồ sơ, đề xuất 3 dòng CBG có nhiều từ trùng nhất (so khớp có dấu, cộng điểm khi cùng đơn vị) → `goi_y_gia_vat_lieu.csv`. **Không tự điền `gia_tai_nguyen.csv`** — người lập chọn dòng, ghi giá, số CBG, trang, địa điểm giao; cộng cước vận chuyển đến chân công trình nếu CBG là giá tại nguồn (bãi, mỏ, nhà máy).

Lưu ý khi dùng giá CBG: giá chưa VAT hay đã VAT theo ghi chú của từng CBG; địa điểm giao (tại bãi/nhà máy hay chân công trình); khu vực, vùng (Hưng Yên chia Vùng 1–8; Hải Phòng ghi khu vực phía Đông/Tây); kỳ công bố phù hợp `thoi_diem_ap_gia`.

Đã thử trên dữ liệu thật (17/11/2026): Hà Nội 14 kỳ (mới nhất Q3/2026 — CBG 03.01/2026 ngày 07/10/2026), Hải Phòng 22 kỳ (T8/2026 — CBG 622/TB-SXD ngày 09/09/2026), Hưng Yên 23 kỳ (T08/2026 — CBG 435/CB-SXD ngày 07/09/2026).
