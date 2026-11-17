# Chi phí dự án chuyển đổi số (CNTT) dùng NSNN — NĐ 224/2026, TT 39/2026/TT-BKHCN

Lệnh: `python scripts/cntt_tt39.py --data <thư mục hồ sơ> [--ra tong_hop.xlsx]` — đọc `config_cntt.json`, `khoi_luong.csv`, `gia_tai_nguyen.csv` (ví dụ: `data/vi-du-cntt/`). Không dùng `dutoan.py tinh` cho hồ sơ này (cơ cấu chi phí khác NĐ 206/TT 36).

**Phạm vi áp dụng:** dự án, nhiệm vụ đầu tư, mua sắm, thuê dịch vụ cho chuyển đổi số dùng NSNN (NĐ 224/2026 Điều 2; TT 39 Điều 2). Dự án đã quyết định đầu tư hoặc có báo cáo thẩm định theo NĐ 45/2026 trước 01/7/2026 → tiếp tục NĐ 45 (NĐ 224 Điều 91), dự án đang theo TT 18/2024/TT-BTTTT → tiếp tục TT 18 (TT 39 Điều 10 k4), trừ khi cấp có thẩm quyền chọn quy định mới. Hạng mục CNTT, ITS nằm trong dự án đầu tư xây dựng → vẫn theo NĐ 206/TT 36 (dùng `dutoan.py`, định mức chuyên ngành qua S23).

**Cơ cấu** (TT 39 Điều 5): G = GTB + GQLDA + GTV + GK + GDP; GTB = GMS + GCSDL + GLĐ + GĐT + GTK + GVC + GK_TB.

**Phương pháp** (NĐ 224 Điều 49): k4 — trang thiết bị và chi phí khác: báo giá (a), kết quả LCNT tương tự trong 12 tháng (b), thẩm định giá (c), giá niêm yết (d), **định mức chuyên ngành đặc thù (đ)**, kết hợp (e); k5 — QLDA, tư vấn: báo giá, kết quả LCNT, **chuyên gia**, thẩm định giá, định mức, kết hợp; k6 — tự thực hiện: theo phương pháp, mức chi cơ quan có thẩm quyền quy định (QLDA: TT 70/2024/TT-BTC; giám sát, đánh giá đầu tư: NĐ 19/2026). Kiểm toán, thẩm tra phê duyệt quyết toán: không thuộc k4 (`theo_quy_dinh`).

**Skill tính:**
- GLĐ, GCSDL từ `khoi_luong.csv` × định mức (`data/chuyen-nganh/`, TT 38, hoặc `dinh_muc.csv` hồ sơ) × giá: chi phí trực tiếp VL + NC + M (VL khác, máy khác theo %); VAT theo `thue_gtgt_dinh_muc`. **Chi phí chung, thu nhập chịu thuế tính trước:** TT 39 không quy định tỷ lệ cho phương pháp định mức (bảng báo giá PL TT 39 để nhà cung cấp tự đề xuất) — mặc định 0, nếu tính phải ghi tỷ lệ và căn cứ (`dinh_muc_chi_phi_chung`, `dinh_muc_thu_nhap`).
- Khoản khác: `khoan_muc` [{ma, ten, gia_tri, phuong_phap, can_cu, so_bao_gia, ly_do_mot_bao_gia, so_thang_truoc}].
- Chuyên gia (PL mục III): CTV = CCG + CQL + CK + TN + VAT; CQL = CCG × 55 % (CCG ≤ 1 tỷ), 50 % (1–5 tỷ), 45 % (≥ 5 tỷ) — Bảng 3.2; TN = 6 % (CCG + CQL + CK); cá nhân không tính CQL, TN, VAT. Lương chuyên gia: TT 07/2026/TT-BNV.
- GDP = (GTB + GQLDA + GTV + GK) × Kdp; Kdp tối đa 10 % (tổng mức), 7 % (dự toán), 5 % (BCKTKT).

**Soát:** phương pháp ngoài Điều 49 → chặn; thiếu căn cứ → cảnh báo; 01 báo giá không nêu lý do (PL mục I.1) → cảnh báo; kết quả LCNT quá 12 tháng (PL mục II.1) → chặn; Kdp vượt mức → chặn; thiếu giá tài nguyên → chặn; chưa có GQLDA → cảnh báo; tỷ lệ chung/TN không căn cứ → chặn.

**Chưa làm:** dự án thuê dịch vụ công nghệ số (TT 39 Điều 6: GDVCNS, GVH; phần mềm khấu hao 8 năm), sơ bộ tổng mức (Điều 4), chi thường xuyên (Điều 3), dự toán phần mềm nội bộ theo công tháng.
