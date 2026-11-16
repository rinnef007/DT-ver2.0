# Ví dụ dự toán chi phí khảo sát (PL V TT 36/2026) — GIÁ LÀ SỐ GIẢ

`che_do_chi_phi: "tt36_khao_sat"`, mẫu đơn vị (`mau_xuat: "doan_vung"`, làm tròn từng bước):
- Mỗi hạng mục (kỹ sư khảo sát, xe phục vụ, đảm bảo ATGT, xe ĐBGT) có khối đơn giá chi tiết theo từng vùng giá:
  T → C = NC × 70% (Bảng 5.1) → TT = T × 6% (Bảng 5.2) → TL = (T+GT) × 6% → Cpa, Cbc = (T+GT+TL) × tỷ lệ (Bảng 5.3) → G.
- Bảng tổng hợp: G, GTGT; nhà tạm = (G + GTGT) × 2% (tính sau thuế rồi tách trước thuế); dự phòng = (G + GTGT) × tỷ lệ (≤ 10%).
- Đảm bảo ATGT và xe ĐBGT không tính lập báo cáo khảo sát (`ty_le_theo_ma`) — cần ghi lý do; theo PL V, chi phí khác phục vụ khảo sát (ĐBATGT, di chuyển máy, bảo hiểm) thuộc Cpvks và lập dự toán riêng.

Chạy: `python scripts/dutoan.py tinh --data data/vi-du-khao-sat --khoi-luong data/vi-du-khao-sat/khoi_luong.csv --config data/vi-du-khao-sat/config_du_toan.json --out vd_ks.xlsx`
