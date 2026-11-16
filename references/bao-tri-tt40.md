# Chi phí bảo trì công trình — TT 40/2026/TT-BXD

Nguồn: TT 40/2026/TT-BXD ngày 26/6/2026, hiệu lực 01/7/2026, thay TT 14/2021/TT-BXD. **[ĐÃ ĐỐI CHIẾU]** bản người dùng cung cấp ngày 15/10/2026. Căn cứ nội dung chi phí bảo trì: khoản 2 Điều 39 NĐ 207/2026/NĐ-CP; sửa chữa trong bảo trì: khoản 4 Điều 27 NĐ 217/2026/NĐ-CP. Hai nghị định này chưa đọc trực tiếp.

## 1. Khi nào dùng TT 40, khi nào dùng TT 36

| Trường hợp | Văn bản | Chế độ trong skill |
|---|---|---|
| Bảo dưỡng công trình theo kế hoạch bảo trì | TT 40, PL II | `che_do_chi_phi: "tt40_bao_duong"` |
| Sửa chữa trong kế hoạch bảo trì (k4 Đ27 NĐ 217) | TT 40, PL III | `"tt40_sua_chua"` |
| Sửa chữa ngoài phạm vi trên → phải lập BCKTKT hoặc dự án ĐTXD (k2 Điều 4 TT 40) | TT 36 (Bảng 3.8) | `"tt36"` (mặc định) |
| Công trình chuyên ngành có pháp luật chuyên ngành riêng về bảo trì (k1 Điều 7) | Theo pháp luật chuyên ngành | Hỏi người dùng văn bản áp dụng |

**Phạm vi bắt buộc** (k2 Điều 7): công trình bảo trì bằng nguồn chi thường xuyên NSNN và công trình dự án PPP. **Nguồn vốn khác**: chủ sở hữu, chủ sử dụng công trình tự quyết định có áp dụng TT 40 hay không. Vì vậy trước khi chọn chế độ, phải hỏi người dùng nguồn kinh phí bảo trì và văn bản chuyên ngành (nếu có) — không tự suy ra.

**Xác nhận của đơn vị (16/10/2026)**: chi phí bảo dưỡng thường xuyên QL5 và cao tốc xác định theo thông tư, nghị định hiện hành — với hồ sơ bảo dưỡng, sửa chữa trong kế hoạch bảo trì, dùng chế độ TT 40 (`tt40_bao_duong` / `tt40_sua_chua`); nếu có văn bản chuyên ngành đường bộ quy định riêng thì ghi rõ trong cấu hình và thuyết minh.

**Chuyển tiếp** (Điều 8): kế hoạch bảo trì đã được phê duyệt chi phí trước 01/7/2026 → tiếp tục theo quy định tại thời điểm phê duyệt. Công việc phát sinh hoặc điều chỉnh chưa được phê duyệt → theo TT 40.

## 2. Tổng hợp chi phí bảo trì (Bảng 1 PL I)

G_BT = G_BD (bảo dưỡng) + G_SC (sửa chữa) + G_K (công việc khác: quản lý của chủ sở hữu G_QL, kiểm tra, quan trắc, kiểm định, đánh giá an toàn, lập kế hoạch bảo trì hằng năm, lập/thẩm tra quy trình bảo trì, công việc khác theo luật chuyên ngành).

## 3. Dự toán bảo dưỡng (PL II) và sửa chữa (PL III)

Tổng hợp (Bảng 2.1 / Bảng 3.1): chi phí thực hiện (gồm nhà tạm) + chi phí khác (lập, thẩm tra dự toán, giám sát, HSMT/HSYC, thẩm định KQLCNT; riêng sửa chữa có thêm **đảm bảo an toàn giao thông**) + **dự phòng ≤ 5%** của (chi phí thực hiện + chi phí khác).

Chi phí thực hiện (Bảng 2.5 bảo dưỡng / Bảng 3.2 sửa chữa):

| Khoản | Cách tính | Ký hiệu |
|---|---|---|
| Chi phí trực tiếp | VL + NC + M | T |
| Chi phí gián tiếp | **NC × tỷ lệ** (Bảng 2.2) | GT |
| Thu nhập chịu thuế tính trước | (T + GT) × tỷ lệ (Bảng 2.3) | TL |
| Chi phí thực hiện trước thuế | T + GT + TL | G_THTT |
| Thuế GTGT (nếu có) | G_THTT × TGTGT | GTGT |
| Chi phí thực hiện sau thuế | G_THTT + GTGT | G_TH |
| Nhà tạm | **G_TH (sau thuế) × tỷ lệ** (Bảng 2.4) | LT |

Khác TT 36: không tách chi phí chung và "một số công việc không xác định được KL"; gián tiếp tính trên NC; nhà tạm tính trên giá trị **sau thuế** (về số học bằng GXDTT × tỷ lệ × (1 + TGTGT) của TT 36 sau đính chính).

- **Bảng 2.2 — chi phí gián tiếp (% × NC)**, theo tổng NC trong T của dự toán thực hiện bảo dưỡng (sửa chữa) của công trình: ≤ 15 tỷ: 66 · ≤ 50: 63 · ≤ 100: 60 · > 100: 56. Vùng núi, biên giới, trên biển, hải đảo: hệ số **1,05 ÷ 1,1** tùy điều kiện. Định mức không phù hợp thì lập dự toán theo nội dung mục 2.1.
- **Bảng 2.3 — TL (%)**: dân dụng 5,5 · công nghiệp 6,0 · giao thông 6,0 · NN&MT 5,5 · HTKT 5,5.
- **Bảng 2.4 — nhà tạm (%)**, theo tổng chi phí thực hiện trước thuế của công trình (≤ 15 / ≤ 100 / ≤ 500 / ≤ 1000 / > 1000 tỷ): theo tuyến 2,2 / 2,0 / 1,9 / 1,8 / 1,7 · còn lại 1,1 / 1,0 / 0,95 / 0,9 / 0,85.
- Khối lượng: bảo dưỡng theo tiêu chuẩn và quy trình bảo trì, điều kiện khai thác (chưa có quy trình thì tham khảo công trình tương tự); sửa chữa theo kết quả kiểm tra, đánh giá hiện trạng, hồ sơ thiết kế sửa chữa.
- Giá công tác: theo định mức công việc bảo trì, báo giá, hoặc giá công tác tương tự. Định mức bảo trì do Bộ chuyên ngành, UBND tỉnh ban hành (Điều 6); chưa có thì vận dụng hệ thống định mức hiện hành (TT 38, PL VI cho sửa chữa — lưu ý hệ số mục 3.b khi dùng mã PL II/III).

## 4. Chi phí quản lý của chủ sở hữu, chủ sử dụng (PL IV)

G_QL = (G_BDTT + G_SCTT) × t_QLBD. Bảng 4 (%), theo chi phí bảo dưỡng + sửa chữa theo kế hoạch bảo trì (chưa GTGT, tỷ đồng):

| Loại | ≤10 | 20 | 50 | 100 | 200 | 500 | ≤1.000 |
|---|---|---|---|---|---|---|---|
| Dân dụng | 3,446 | 2,923 | 2,610 | 2,017 | 1,886 | 1,514 | 1,239 |
| Công nghiệp | 3,557 | 3,018 | 2,694 | 2,082 | 1,947 | 1,564 | 1,279 |
| Giao thông | 3,024 | 2,566 | 2,292 | 1,771 | 1,655 | 1,329 | 1,088 |
| NN&MT | 3,263 | 2,769 | 2,473 | 1,910 | 1,786 | 1,434 | 1,174 |
| HTKT | 2,901 | 2,461 | 2,198 | 1,593 | 1,560 | 1,275 | 1,071 |

Tối thiểu **2.000.000 đồng**. TT 40 không ghi công thức nội suy giữa các mốc. Skill nội suy tuyến tính như PL VIII TT 38 (lệnh `dutoan.py ty-le --bang ql-chu-so-huu --loai giao_thong --gia-tri <tỷ>`); cách này phải được người dùng xác nhận. (Các giá trị trùng với 7 cột đầu Bảng 1.1 định mức QLDA PL VIII TT 38.)

## 5. Dùng trong skill

- Config: `che_do_chi_phi`, `quy_mo_nc_ty` (NC trong T, tỷ đồng — ước tính để tra Bảng 2.2), `quy_mo_truoc_thue_ty` (chi phí thực hiện trước thuế — để tra Bảng 2.4), `ty_le.chi_phi_chung` = tỷ lệ gián tiếp, `co_so: "NC"`; không khai `cong_viec_khong_xd_kl` (skill đặt 0). Ví dụ: `data/vi-du-tt40/`.
- Soát: S09 so tỷ lệ với bảng TT 40 theo quy mô khai báo; **S19** (sau khi tính) so lại theo NC và chi phí thực hiện thực tế; S20 nhắc điều kiện áp dụng (Điều 7).
- Chi phí khác, dự phòng (≤ 5%), G_QL: khai trong `tong_hop` (mẫu đoạn/vùng) với căn cứ.
