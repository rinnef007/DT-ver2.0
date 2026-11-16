# Dự toán chi phí khảo sát xây dựng — PL V TT 36/2026 và mẫu đơn vị

Căn cứ: PL V TT 36/2026/TT-BXD (bộ phụ lục thay thế theo CV 9947/BXD-VPB) **[ĐÃ ĐỐI CHIẾU]**; định mức khảo sát PL I TT 38/2026. Tỷ lệ đã có trong `data/bang_ty_le_tt36_2026.json` (`pl_v_khao_sat`). Dự toán thí nghiệm chuyên ngành lập tương tự (phần III PL V).

## 1. Cấu trúc (Bảng 5.4)

| Khoản | Cách tính | Ký hiệu |
|---|---|---|
| Chi phí trực tiếp | VL + NC + M (định mức PL I TT 38; công việc chưa có định mức → lập theo công, ca, ghi lý do) | T |
| Chi phí chung | NC × Bảng 5.1 (NC ≤ 1 tỷ: 70% · 1 ÷ ≤ 2: 65% · > 2: 60%) | C |
| Chi phí không xác định được KL | T × Bảng 5.2 (T ≤ 2 tỷ: 6% · 2 ÷ ≤ 3: 4,5% · > 3: 3%) | TT |
| Thu nhập chịu thuế tính trước | (T + GT) × 6% | TL |
| Lập phương án kỹ thuật khảo sát | (T + GT + TL) × Bảng 5.3 (≤ 2 tỷ: 2% · > 2 tỷ: 1,5%) | Cpa |
| Lập báo cáo kết quả khảo sát | (T + GT + TL) × Bảng 5.3 (≤ 2 tỷ: 3% · > 2 tỷ: 2,5%) | Cbc |
| Chi phí khác phục vụ khảo sát | Di chuyển máy, ĐBATGT, bảo hiểm… — lập dự toán | Ck |
| Chi phí khảo sát trước thuế | (T + GT + TL) + Cpa + Cbc + Ck | G |
| Thuế GTGT | G × TGTGT | GTGT |
| Nhà tạm để ở và điều hành thi công | (G + GTGT) × 2% (không đủ thì lập dự toán) | LT |
| Dự phòng | (G + GTGT) × tỷ lệ, **tối đa 10%** | Cdp |
| **Chi phí khảo sát** | G + GTGT + LT + Cdp | Gks |

Chi phí lập nhiệm vụ khảo sát = 3% dự toán khảo sát (phần II PL V). Giám sát khảo sát: Bảng 2.26 PL VIII TT 38.

## 2. Dùng trong skill

- Config: `che_do_chi_phi: "tt36_khao_sat"`; `ty_le` gồm `chi_phi_chung` (co_so NC), `cong_viec_khong_xd_kl`, `thu_nhap_chiu_thue_tt`, `lap_phuong_an_ks`, `lap_bao_cao_ks`, `nha_tam`, `du_phong`, `thue_gtgt`; quy mô để tra nấc: `quy_mo_nc_ty`, `quy_mo_t_ty`, `quy_mo_t_gt_tl_ty`. Ví dụ: `data/vi-du-khao-sat/`.
- Hai cách trình bày:
  - **Mẫu đơn vị** (`mau_xuat: "doan_vung"`): mỗi hạng mục có khối đơn giá chi tiết theo vùng (T → C → TT → TL → Cpa, Cbc → G → GTGT); bảng khối lượng × đơn giá theo khu vực; bảng tổng hợp có nhà tạm (tính trên giá trị sau thuế rồi tách trước thuế — đúng cách của mẫu đơn vị) và dự phòng. Tỷ lệ riêng theo mã (`ty_le_theo_ma`) dùng cho khoản không tính Cbc (ĐBATGT, xe ĐBGT).
  - **Bảng 5.4** (`mau_xuat: "bang_3_8"`): tổng hợp theo đúng Bảng 5.4; chỉ dùng khi **một vùng giá** (S21 chặn nếu nhiều vùng); Ck nhập tại `khao_sat.chi_phi_khac_phuc_vu_ks`.
- Soát: S09 (tỷ lệ theo quy mô khai báo; Cpa/Cbc bằng 0 → nhắc ghi lý do; dự phòng > 10%), S19 (nấc theo NC, T, T+GT+TL thực tế sau khi tính), S20 (khoản không tính Cpa/Cbc), S15 (mã không thuộc TT 38 — dự toán theo công).
- Tra nhanh tỷ lệ: `dutoan.py ty-le --bang ks-chung|ks-khong-xd-kl|ks-phuong-an|ks-bao-cao --gia-tri <tỷ>`.

Đã kiểm tra: tái lập một hồ sơ khảo sát mẫu của đơn vị (3 khu vực, 5 vùng giá) — chi phí khảo sát trước thuế, thuế và tổng sau thuế khớp đến đồng.

## 3. Cách làm của mẫu đơn vị (giữ khi lập hồ sơ mới)

- Công việc khảo sát phục vụ lập phương án sửa chữa (tập hợp, rà soát hồ sơ hoàn công; khảo sát hiện trường; khảo sát thị trường vật tư thiết bị) lập theo **công kỹ sư** và **ca xe bán tải** — không có mã PL I TT 38 tương ứng, ghi lý do trong thuyết minh.
- Kỹ sư: giá nhân công "Kỹ sư thực hiện khảo sát, thí nghiệm" (Bảng 3.1 PL III TT 37) theo công bố của Sở XD từng vùng. Xe: giá ca máy tính theo TT 37 (nhiên liệu × hệ số nhiên liệu phụ, nhân công nhóm lái xe, khấu hao – sửa chữa – chi phí khác).
- ĐBATGT theo thời gian chiếm dụng (≤ 1 ca; < 1/2 ca; < 0,25 ca), vật tư ATGT tính luân chuyển (2% / 1% / 0,5%), kèm ca xe đảm bảo giao thông; không tính Cbc trên khoản này.
- Cpa thường để 0 (không lập phương án kỹ thuật khảo sát riêng); Cbc 3%; dự phòng 10%; nhà tạm 2%, hoặc **không tính khi thời gian khảo sát ngắn ngày** (đơn vị xác nhận 16/10/2026) — ghi lý do này trong thuyết minh.
- Thuế GTGT 8% (đơn vị xác nhận 16/10/2026; kiểm tra lại khi chính sách giảm thuế thay đổi).
- Gói thầu thường gồm thêm **chi phí lập dự toán phương án sửa chữa** = Cxd dự kiến × định mức thiết kế BVTC (Bảng 2.12 PL VIII TT 38, vd. giao thông cấp IV ≤ 10 tỷ: 1,37%) × 1,1 (thiết kế sửa chữa không thay đổi kết cấu chịu lực, mục 3.5a) × 12% (phần lập dự toán, mục 3.4). Khai trong `tong_hop` với căn cứ. Đơn vị lấy **cấp IV theo quy mô của hạng mục sửa chữa** (đơn vị xác nhận 16/10/2026), không theo cấp của tuyến đường. Ghi câu này làm căn cứ trong thuyết minh, vì nếu tra theo cấp của tuyến thì tỷ lệ khác nhiều (≤ 10 tỷ: cấp IV 1,37% · cấp I 2,27%).

## 4. Điểm cần lưu ý khi soát hồ sơ khảo sát (rút từ hồ sơ mẫu)

1. Ký hiệu chi phí không xác định được KL ghi "LT" — theo PL V là khoản thuộc GT (ký hiệu TT); LT là nhà tạm. Có khối ghi nhầm nhãn dòng (dòng 6% mang tên "Thuế GTGT").
2. Cpa = 0, Cbc không tính cho ĐBATGT — hợp lý về thực tế nhưng cần một câu lý do trong thuyết minh; PL V xếp ĐBATGT, di chuyển máy, bảo hiểm vào Cpvks (lập dự toán), không phải vào T.
3. Diễn giải và khối lượng phải khớp (vd. "02 kỹ sư" mà khối lượng 1 công — ghi rõ 02 người × 0,5 ngày).
4. Nguồn giá từng cột vùng phải cùng kỳ: có cột còn ghi công bố giá năm trước. Giá nhân công: bảng nhân công ghi văn bản của Hưng Yên (CV 3385) và Hải Phòng (CV 7546) nhưng chưa ghi văn bản của Hà Nội (CV 14502/SXD-KTXD ngày 02/7/2026) — giá trong hồ sơ khớp cả ba văn bản; chỉ cần bổ sung dòng nguồn. Dùng `can-gia --nhan-cong` và soát S22 để đối chiếu tự động.
5. Bảng giá ca máy còn nhãn cũ ("Nhân công bậc …/4 – Nhóm 4") dù đã lấy giá nhóm lái xe — sửa nhãn cho thống nhất TT 37.
6. Định mức ĐBATGT dùng mã định mức chuyên ngành cũ (bảo dưỡng đường bộ) — kiểm tra hiệu lực và việc chuyển nhân công sang nhóm (TT 36 Điều 10; TT 37 Điều 2 k3).
7. Tồn dư khi sao chép: ô ẩn còn tên công trình khác, nhiều sheet ẩn của hồ sơ khác, liên kết file ngoài, ô `#N/A`/`#VALUE!` ở vùng tính "bằng chữ" — rà trước khi phát hành (`soat_file_excel.py`).
8. Dự phòng 10% là mức tối đa — nêu cơ sở khi lấy mức trần.

## 5. Nhập hồ sơ khảo sát có sẵn — tính lại và chỉ ra chênh lệch

```bash
python scripts/nhap_ks_excel.py --file DT_KS.xls --ra du-lieu/ks-x \
    --vung-nc HN-V1-KV1,HY-V2,HY-V3,HP-V1,HP-V2 --tinh-lai
```

- Tự nhận diện theo nội dung: sheet đơn giá chi tiết (tiêu đề "Thành phần hao phí", các dòng Cpa/Cbc), bảng giá trị khảo sát (cột Đơn giá trỏ sang sheet đơn giá chi tiết; ưu tiên sheet đang hiện, nhiều dòng tham chiếu nhất), sheet tổng hợp ("Khoản mục chi phí"). Đọc được file .xls (chuyển bằng LibreOffice) và file có liên kết ngoài hỏng.
- Tính lại từng khối × từng vùng từ hao phí, đơn giá, hệ số, tỷ lệ ghi trong file (làm tròn từng bước): dòng hao phí, %, T, C, TT, GT, TL, Cpa, Cbc, G, GTGT; bảng giá trị: đơn giá, thành tiền, G, GTGT, LT, Cdp, Gks; tổng hợp: sau thuế = trước thuế + thuế, khớp bảng giá trị.
- Chỉ ra: số lệch (vị trí, giá trị file – tính lại); dòng lấy đơn giá sai vùng so với tên khu vực; ký hiệu LT cho chi phí không xác định được KL; nhãn ghi nhầm (dòng 6% mang tên "Thuế GTGT"), nhãn ghi tỷ lệ khác tỷ lệ dùng; công thức lấy tỷ lệ ở ô của khối khác; số thứ tự khối trùng, mã dùng cho nhiều khối; tỷ lệ khác nấc Bảng 5.1–5.3 theo quy mô thực tế, dự phòng > 10%; diễn giải số người khác khối lượng; giá nhân công khác văn bản Sở XD (khi có `--vung-nc`, theo thứ tự các cột vùng); các khoản bằng 0 cần lý do (Cpa, Cbc, LT).
- `--ra` ghi `dinh_muc.csv`, `gia_tai_nguyen.csv`, `khoi_luong.csv`, `config_du_toan.json` (mỗi khối một mã; tỷ lệ riêng theo khối vào `ty_le_theo_ma`) và `bao_cao_nhap_ks.md`; `--tinh-lai` chạy `dutoan.py tinh` và so G, Gks với file.
- Không tính lại: nguồn giá vật liệu, ca máy (đối chiếu công bố giá tại thời điểm lập); các khoản ngoài chi phí khảo sát trong tổng hợp (vd. lập dự toán phương án sửa chữa — dùng `dutoan.py ty-le`).

Đã kiểm tra trên hai hồ sơ mẫu của đơn vị: tính lại và tái lập khớp đến đồng (G 15.840.822 / Gks 19.161.059; G 8.658.915 / Gks 10.286.791, không tính nhà tạm). Thử trên bản sửa cố ý (TL tính trên T + C ở một vùng; một dòng lấy đơn giá sai vùng; nhà tạm 3% trong khi nhãn ghi 2%): cả ba được chỉ ra, kèm ảnh hưởng tới Gks và bảng tổng hợp.
