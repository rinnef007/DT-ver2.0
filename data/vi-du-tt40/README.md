# Ví dụ chế độ TT 40/2026 — sửa chữa trong kế hoạch bảo trì — GIÁ LÀ SỐ GIẢ

Cùng khối lượng và giá giả với `data/vi-du-tt38/`, nhưng `che_do_chi_phi: "tt40_sua_chua"`:
- Chi phí gián tiếp = NC × 66% (Bảng 2.2 PL II TT 40, áp cho sửa chữa theo mục 2.2 PL III); không có khoản TT.
- TL = (T + GT) × 6% (Bảng 2.3); nhà tạm = chi phí thực hiện sau thuế × 2,2% (Bảng 2.4, theo tuyến).
- Dự phòng (nếu có) ≤ 5%; chi phí khác (lập, thẩm tra dự toán, giám sát, ĐBATGT…) khai trong `tong_hop` nếu dùng mẫu đoạn/vùng.

Chạy: `python scripts/dutoan.py tinh --data data/vi-du-tt40 --khoi-luong data/vi-du-tt40/khoi_luong.csv --config data/vi-du-tt40/config_du_toan.json --out vd_tt40.xlsx`
