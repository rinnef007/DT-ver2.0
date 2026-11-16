# Mẫu biểu Excel đầu ra

Có hai mẫu, chọn bằng `mau_xuat` trong config. Với người dùng đã có mẫu đơn vị (xem `mau-don-vi.md`), mặc định dùng `doan_vung`.

## A. `bang_3_8` (mặc định)

File do `dutoan.py tinh` tạo, giữ công thức (đổi khối lượng, giá, tỷ lệ → toàn bộ tự tính lại). Font Times New Roman 11 (văn bản hành chính). Ô nhập liệu tô vàng nhạt, chữ xanh; ô công thức chữ đen.

| Sheet | Nội dung | Ghi chú |
|---|---|---|
| `TH_CPXD` | Tổng hợp dự toán chi phí xây dựng theo Bảng 3.8 PL III TT 36/2026: T (VL, NC, M), GT (C, TT), TL, GXDTT, GTGT, GXD, LT; dòng ký người lập / người chủ trì | Lấy số từ `DT_CT`, tỷ lệ từ `THAM_SO` |
| `DT_CT` | Dự toán chi tiết: STT, mã hiệu, tên công tác, đơn vị, khối lượng, đơn giá VL/NC/M, thành tiền VL/NC/M; nhóm theo hạng mục có dòng cộng | Đơn giá tham chiếu `PT_DG` |
| `PT_DG` | Phân tích đơn giá: từng mã → từng hao phí × giá = thành tiền; cộng VL, NC, M trên 1 đơn vị định mức; quy đổi về đơn vị khối lượng | Giá tham chiếu `GIA_TN` |
| `TH_VT` | Tổng hợp vật tư, nhân công, máy: tổng hao phí = Σ KL × quy_doi × hao_phi × hệ số, giá, thành tiền; đối chiếu tổng VL/NC/M với `DT_CT` | SUMIF theo mã tài nguyên |
| `CL_VT` | Chênh lệch vật tư gốc vs hiện tại (mới ở v2.0): KL × giá gốc [6] / giá hiện tại [7] / chênh lệch [8]=[7]−[6] / TT chênh lệch [9]=[5]×[8] / thành tiền [10]=[5]×[7]; tỷ trọng trong VL và trong CP trực tiếp | Chỉ xuất khi có `don_gia_goc` trong `gia_tai_nguyen.csv` (xem `references/chuan-bi-du-lieu.md` mục 2); chỉ vật liệu, không gồm VLK |
| `HP_CT` | Hao phí chi tiết từng dòng khối lượng × từng tài nguyên (nguồn cho TH_VT) | Công thức |
| `GIA_TN` | Bảng giá tài nguyên dùng tính, kèm nguồn và ngày áp dụng; thêm cột "Giá gốc (đồng)" khi có tài nguyên nhập `don_gia_goc` | Ô nhập |
| `THAM_SO` | Thông tin công trình, tỷ lệ C, TT, TL, LT, GTGT, Knc, Km kèm căn cứ | Ô nhập |
| `KL_DIEN_GIAI` | Bảng khối lượng: diễn giải, nguồn bản vẽ, trạng thái | Phục vụ thẩm tra |
| `CANH_BAO` | Danh sách cảnh báo khi xuất (thiếu giá, dòng chưa xác nhận, hệ số không căn cứ…) | Chỉ có khi có cảnh báo |

Quy ước: số tiền làm tròn hiển thị đến đồng (`#,##0`), không làm tròn trong công thức; hao phí hiển thị 4 chữ số thập phân.

## B. `doan_vung` (mẫu đơn vị: công trình tuyến, nhiều địa bàn)

| Sheet | Nội dung |
|---|---|
| `TDT` | Bảng tổng hợp theo `tong_hop`: STT · nội dung · tỷ lệ · hệ số · cách tính · trước thuế · GTGT · sau thuế · căn cứ; dòng "Bằng chữ" (theo giá trị lúc xuất); người lập / người chủ trì |
| `DT` | Bảng dự toán theo hạng mục: TT · mã · tên · đơn vị · KL từng đoạn · đơn giá từng vùng · thành tiền từng đoạn · tổng; mỗi hạng mục có cộng trước thuế, GTGT, sau thuế |
| `DGCT` | Đơn giá chi tiết từng mã (từng biến thể hệ số/quy đổi): a) VL, b) NC, c) M với định mức × đơn giá × hệ số cho từng vùng; T, C, TT, GT, TL, G, GTGT, Gxd; đơn giá/đv KL = G / số đv định mức |
| `GIA_TN` | Giá tài nguyên theo vùng, nguồn |
| `CL_VT` | *(mẫu `doan_vung` chưa có — cần thiết kế riêng vì giá theo nhiều vùng; dự kiến v2.1)* |
| `THAM_SO` | Tỷ lệ, thuế suất, danh sách vùng và đoạn |
| `KL_DIEN_GIAI`, `CANH_BAO` | Như mẫu A |

Ký hiệu theo Bảng 3.8 PL III TT 36/2026 (TT cho chi phí không xác định được KL; LT cho nhà tạm). Làm tròn theo `lam_tron`.

Nếu đơn vị có mẫu biểu riêng (ví dụ mẫu của Ban/Phòng thẩm định), lưu file mẫu vào `data/mau/` và điều chỉnh `scripts/xuat_excel.py` theo mẫu đó — mẫu của đơn vị ưu tiên hơn bố cục mặc định ở đây.
