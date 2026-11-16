# Chuẩn bị dữ liệu nguồn

Script đọc các file CSV (UTF-8, dấu phẩy, dấu chấm thập phân) trong một thư mục dữ liệu, ví dụ `du-lieu/ha-noi-2026-q3/`. **Định mức TT 38/2026 đã có sẵn trong `data/tt38/`** — hồ sơ chỉ cần bảng giá + khối lượng; `dinh_muc.csv` chỉ cần khi dùng định mức ngoài TT 38 hoặc muốn ghi đè (định mức riêng ưu tiên). Tên tài nguyên trong bảng giá phải đúng tên TT 38 (vd. `Nhân công nhóm 1`, `Máy đào 0,4m3`, `Xi măng`, `Cát vàng`) — dùng `dutoan.py tra --ma …` để xem. Mẫu tiêu đề cột: `data/mau/`. Dữ liệu minh hoạ (số liệu GIẢ, chỉ để chạy thử): `data/vi-du/`.

**Không dùng `data/vi-du/` để tính thật.** Bộ thật do người dùng nạp từ phụ lục định mức, công bố giá của Sở Xây dựng, báo giá…

## 1. `dinh_muc.csv` — hao phí định mức (mỗi dòng một hao phí)

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| ma_hieu | ✔ | Mã định mức, ví dụ `AB.11111` |
| ten_cong_tac | ✔ | Tên công tác đầy đủ quy cách |
| don_vi | ✔ | Đơn vị định mức (m3, 100m3, tấn…) |
| loai | ✔ | `VL` vật liệu · `NC` nhân công · `M` máy · `VLK` vật liệu khác (%) · `MK` máy khác (%) |
| ma_tn | ✔ (trừ VLK/MK) | Mã tài nguyên, khớp `gia_tai_nguyen.csv` |
| ten_tn |  | Tên tài nguyên (để đọc) |
| don_vi_tn |  | Đơn vị tài nguyên |
| hao_phi | ✔ | Hao phí trên 1 đơn vị định mức; với VLK/MK là % |
| he_so |  | Hệ số áp cho dòng hao phí này (mặc định 1), vd. NC 1,15 khi áp định mức mới cho công tác sửa chữa — chỉ khi có căn cứ |
| can_cu_he_so | khi he_so ≠ 1 | Căn cứ của hệ số |
| ly_do | khi chủ ý khác TT 38 | Lý do điều chỉnh hao phí so với TT 38 (vd. hao phí = 0 vì vật tư đã tính ở công tác khác/do bên khác cấp). Có lý do thì S17 chỉ ghi THÔNG TIN, không cảnh báo; lý do phải được đưa vào thuyết minh |
| nguon | ✔ | Ghi rõ phụ lục TT 38/2026, ví dụ `TT38/2026 PL II`, `TT38/2026 PL VI` (theo bộ phụ lục sau CV 9947). Định mức khác TT 38 thì ghi văn bản và lý do |

## 2. `gia_tai_nguyen.csv` — giá vật liệu, nhân công, ca máy (chưa GTGT)

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| ma_tn | ✔ | Mã tài nguyên |
| ten_tn | ✔ | Tên |
| don_vi | ✔ | Đơn vị |
| loai | ✔ | VL / NC / M |
| vung |  | Mã vùng giá (khớp `vung` trong config). Trống = áp chung mọi vùng |
| don_gia | ✔ | đồng, chưa GTGT; VL là giá đến hiện trường |
| nguon | ✔ | Ví dụ `CBG Sở XD Hà Nội số …, tháng 9/2026`, `Báo giá NCC A ngày …` |
| ngay_ap_dung | ✔ | yyyy-mm-dd |
| khu_vuc |  | Địa bàn, vùng |
| ty_le_luong |  | Riêng ca máy: tỷ lệ tiền lương trong giá ca máy (g), dùng tính Km |
| don_gia_goc |  | Giá gốc của vật liệu tại thời điểm lập giá gốc (đồng, chưa GTGT) — dùng xuất sheet `CL_VT` (mới ở v2.0). Chỉ điền cho vật liệu cần tính chênh lệch; để trống thì tài nguyên đó không có trong `CL_VT` |

Mỗi cặp (`ma_tn`, `vung`) chỉ một dòng giá. Nhiều thời điểm: tách thư mục theo thời điểm.

**Giá gốc để tính chênh lệch vật tư (CL_VT, mới ở v2.0):** khi hồ sơ cần bảng chênh lệch vật tư (vd. điều chỉnh giá theo hợp đồng, hoặc so sánh giá tại thời điểm lập với giá tại thời điểm lập dự toán gốc), điền cột `don_gia_goc` cho từng vật liệu — giá tại thời điểm gốc, cùng đơn vị và cùng nguồn gốc với `don_gia` (ghi rõ nguồn, ngày áp dụng của giá gốc trong cột `nguon`/`ngay_ap_dung` của dòng đó hoặc trong thuyết minh). Khi xuất, `dutoan.py tinh` tạo thêm sheet `CL_VT` theo đúng chỉ số của GXD (xem `references/mau-bieu-excel.md` mục A): khối lượng tổng hợp từ `HP_CT`, giá gốc [6] và giá hiện tại [7] tham chiếu `GIA_TN`, chênh lệch [8] = [7] − [6], TT chênh lệch [9] = [5] × [8], thành tiền [10] = [5] × [7], kèm tỷ trọng trong tổng vật liệu và trong chi phí trực tiếp. Tài nguyên không có `don_gia_goc` không xuất hiện trong `CL_VT`; "Vật liệu khác %" (VLK) không có giá gốc theo từng tài nguyên nên không có trong bảng này.

**Nhóm nhân công (Bảng 3.1 PL III TT 37/2026, [ĐÃ ĐỐI CHIẾU])** — giá nhân công công bố theo nhóm, tên trong TT 38 là `Nhân công nhóm 1…4`:
- Nhóm 1: chuẩn bị mặt bằng, phá dỡ – tháo dỡ, vệ sinh; phục vụ thi công (bốc xếp, vận chuyển, đóng bao, giàn giáo); đất, đá, cát (đào, đắp, bơm, nạo vét, xói hút, vận chuyển; không gồm phá đá nổ mìn).
- Nhóm 2: cọc, gia cố, khoan tạo lỗ, khớp nối, phá đá khoan nổ mìn, bê tông xi măng, lắp cấu kiện BT, ván khuôn, cốt thép, bê tông nhựa, xây gạch đá và công tác khác không thuộc nhóm 1, 3, 4.
- Nhóm 3: lắp đặt hệ thống kỹ thuật công trình; đường ray; kết cấu gỗ, sắt thép; cáp thép; trát, ốp, lát, láng, trần, mái, sơn bả; khảo sát xây dựng.
- Nhóm 4: lắp đặt, tháo dỡ đường dây tải điện và TBA, thiết bị công nghệ, **thông tin, tín hiệu**, đo lường, điều khiển, thí nghiệm.
- Vận hành máy: điều khiển máy; lái xe; thủy thủ, thợ máy, thợ điện; máy trưởng…; thuyền trưởng, thuyền phó. Khác: kỹ sư khảo sát, thí nghiệm; thợ lặn; nghệ nhân; nhân công hầm lò.
Định mức chuyên ngành ban hành trước 01/7/2026 còn ghi theo bậc thợ (vd. 3,5/7) mà chưa chuyển đổi: chọn nhóm theo tính chất công tác (TT 37 Điều 2 k3) và ghi lý do trong `nguon`. Giá nhân công kỳ chuyển tiếp: bảng Sở XD chuyển đổi từ giá theo bậc (PL III mục I.4); giá khảo sát theo phương pháp mới áp dụng từ 01/01/2027.

**Giá nhân công tham chiếu**: `data/nhan-cong/gia_nhan_cong_chuyen_doi_2026.csv` (Hà Nội, Hưng Yên, Hải Phòng — giá chuyển đổi theo nhóm, hiệu lực đến khi có văn bản thay thế). Trong config, mỗi vùng giá có thể gán `"nhan_cong": "<ma_vung>"` (vd. `HN-V1-KV1`, `HY-V2`, `HP-V1`); `can-gia --nhan-cong` điền sẵn giá nhân công, soát S22 cảnh báo khi bảng giá khác văn bản.

**Mốc 01/01/2027** (TT 37 Điều 2 k2, [ĐÃ ĐỐI CHIẾU]): từ ngày này dùng bảng giá nhân công theo phương pháp mới khi Sở XD đã công bố; bảng chuyển đổi (k1) chỉ là tạm thời đến hết 31/12/2026. **QĐ 2036/2037/QĐ-SXD Hà Nội (26/10/2026)** công bố giá nhân công XD và giá ca máy Hà Nội — **chưa nhập vào `data/nhan-cong/`** cho đến khi xác định được đây là giá theo phương pháp mới hay giá chuyển đổi ([CHƯA ĐỐI CHIẾU] — chưa đọc nội dung QĐ).

**Giá vật liệu, ca máy không đóng gói trong skill** (công bố giá thay đổi theo kỳ). Cách lập nhanh cho từng hồ sơ: chạy `dutoan.py can-gia` sau khi khối lượng và mã đã xác nhận → file có sẵn `ma_tn`, `ten_tn`, `don_vi`, `loai`, `vung` và cột `dung_o_ma` (để biết tài nguyên dùng ở mã nào); điền `don_gia`, `nguon`, `ngay_ap_dung` từ công bố giá kỳ hiện hành, lưu thành `gia_tai_nguyen.csv` (cột `dung_o_ma` được bỏ qua khi tính). Tài nguyên có hao phí = 0 ở mọi mã (bỏ có chủ ý, ghi `ly_do`) không cần giá. Dòng nào để trống `don_gia` thì `kiemtra-dulieu` báo lỗi — không để giá 0 cho tài nguyên có dùng.

## 3. `khoi_luong.csv` — bảng khối lượng đầu vào dự toán

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| stt | ✔ | Số thứ tự |
| hang_muc | ✔ | Hạng mục (để nhóm) |
| ma_hieu | ✔ | Mã định mức; `TG` nếu dùng đơn giá trọn gói |
| cap_phoi |  | Mã cấp phối vữa PL VII (vd. `11.12323`) — thay dòng 'Vữa bê tông'/'Vữa' của định mức bằng xi măng, cát, đá, nước |
| ten_cong_tac |  | Để trống thì lấy theo định mức |
| don_vi | ✔ | Đơn vị khối lượng |
| doan |  | Mã đoạn/xã (khớp `doan` trong config). Một công tác nhiều đoạn → nhiều dòng cùng `stt` |
| khoi_luong | ✔ | Theo thiết kế |
| quy_doi |  | Hệ số đổi KL sang đơn vị định mức (mặc định 1) |
| he_so_vl, he_so_nc, he_so_m |  | Hệ số điều chỉnh định mức (mặc định 1) |
| can_cu_he_so | khi có hệ số ≠ 1 | Căn cứ áp hệ số |
| don_gia_tron_goi | khi ma_hieu = TG | Đơn giá trọn gói (gộp vào VL theo PL III) |
| dien_giai | ✔ | Công thức đo bóc |
| nguon_ban_ve | ✔ | Số hiệu bản vẽ |
| trang_thai | ✔ | `de_xuat` / `xac_nhan` |

## 4. `config_du_toan.json`
Mẫu: `data/mau/config_du_toan.mau.json` (một vùng, Bảng 3.8) và `data/vi-du-doan/config_du_toan.json` (đoạn – vùng, có bảng tổng hợp). Mọi tỷ lệ ghi dạng số thập phân (6,2% → 0.062) kèm `can_cu`.

| Khoá | Ý nghĩa |
|---|---|
| `mau_xuat` | `bang_3_8` (mặc định: một bảng chi tiết + tổng hợp Bảng 3.8) hoặc `doan_vung` (mẫu đơn vị: đơn giá chi tiết đầy đủ, KL theo đoạn, TDT) |
| `lam_tron` | `khong` (mặc định) hoặc `tung_buoc` (ROUND đến đồng ở mỗi bước, như hồ sơ lập trên Excel) |
| `vung` | `[{"id": "V1", "ten": "Hà Nội …"}, …]` |
| `doan` | `[{"id": "D1", "ten": "Xã … Km… – Km…", "vung": "V1"}, …]` |
| `ty_le` | C (`co_so` T/NC), TT, TL, nhà tạm, GTGT |
| `ty_le_theo_ma` | Tỷ lệ riêng cho từng mã, vd. `{"QLĐCT.10420": {"chi_phi_chung": {"gia_tri": 0.66, "co_so": "NC", "can_cu": "Bảng 3.4 …"}}}` |
| `tong_hop` | Bảng tổng hợp kiểu TDT — xem `references/mau-don-vi.md` mục 4 |
| `loai_ho_so` | `xay_dung_moi` (mặc định) hoặc `sua_chua` (áp hệ số PL VI mục 3.b cho mã PL II/III) |
| `tu_dong_he_so_sua_chua` | `true` (mặc định) / `false` — tắt khi hệ số đã ghi sẵn trong dữ liệu |

## 5. Chuyển đổi dữ liệu từ G8 / Eta / F1 / Excel khác
Các phần mềm có cấu trúc xuất khác nhau, skill không giả định trước. Dùng lệnh:

```
python scripts/dutoan.py chuyendoi --nguon file_xuat.xlsx --anh-xa anh_xa.json --ra du-lieu/dinh_muc.csv
```

File ánh xạ (mẫu `data/mau/anh_xa.mau.json`) khai báo sheet, dòng tiêu đề, tên cột nguồn tương ứng từng cột chuẩn, và giá trị cố định (ví dụ `nguon`). Với file định mức dạng "mã hiệu ở dòng cha, hao phí ở dòng con" khai báo `"kieu": "phan_cap"` để script điền mã hiệu xuống các dòng con.

Sau chuyển đổi luôn chạy `kiemtra-dulieu` và đối chiếu ngẫu nhiên 5–10 mã với văn bản gốc.

## 6. Nhập từ một hồ sơ dự toán Excel đã lập

```
python scripts/nhap_du_toan_excel.py --file du_toan.xls --dgct "dtct-sc" --dt "dt-xd,dt-dbgt" --ra du-lieu/ten-ho-so
```
Nhận diện sheet đơn giá chi tiết và các sheet dự toán theo tiêu đề cột, tạo đủ 4 file chuẩn và `bao_cao_nhap.md` (lỗi công thức trong khối đơn giá, đơn giá tính lại khác file, STT trùng, KL bằng 0…). Số liệu trích ra là số của hồ sơ đó (nguồn ghi "trích từ file"), không thay văn bản gốc; khối lượng mặc định `de_xuat` (dùng `--xac-nhan` chỉ khi tái lập để đối chiếu). Bảng tổng hợp (TDT) chưa nhập tự động — khai báo `tong_hop` theo TDT của hồ sơ.

Hồ sơ dự toán khảo sát (mẫu khối đơn giá theo vùng + bảng giá trị khảo sát): `python scripts/nhap_ks_excel.py --file DT_KS.xls --ra du-lieu/ks-x [--vung-nc …] [--xac-nhan] [--tinh-lai]` — tự nhận sheet, tính lại theo PL V TT 36 và ghi bộ dữ liệu (xem `references/du-toan-khao-sat.md` mục 5).
