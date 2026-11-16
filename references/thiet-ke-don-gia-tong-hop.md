# Thiết kế mô hình đơn giá tổng hợp (mã TH) — v2.1

> **Trạng thái: CHỈ THIẾT KẾ, chưa làm code.** Mã TH ngoài phạm vi v2.0 (xem `README.md` mục
> "Ngoài phạm vi"). Tài liệu này ghi lại mô hình dữ liệu và cách tính đã thiết kế, để v2.1 làm theo
> mà không phải thiết kế lại — và ghi rõ những câu hỏi còn mở phải trả lời trước khi code.

## 1. Mã TH là gì (ngữ nghĩa GXD)

Một mã TH là **một đơn giá tổng hợp**: gộp nhiều công tác thành phần (mỗi thành phần là một mã định
mức TT 38 thông thường, có khối lượng riêng) thành một đơn giá duy nhất, tính đầy đủ từ hao phí
thành phần → tổng cộng → chi phí chung → thu nhập chịu thuế → đơn giá trước thuế → GTGT → sau thuế
→ dự phòng → **đơn giá thầu**.

Căn cứ từ file mẫu GXD (`DutoanGXD1.xlsm`, sheet `Don gia tong hop`, 32 cột A–AF):

| Nhóm cột | Nội dung |
|---|---|
| C–H | STT, MÃ VỮA, MH ĐỊNH MỨC, MH ĐƠN GIÁ, MSVT, THÀNH PHẦN CÔNG VIỆC |
| I–K | ĐƠN VỊ, KHỐI LƯỢNG, HAO PHÍ ĐỊNH MỨC, GIÁ VẬT TƯ |
| L | HỆ SỐ |
| M–R | Kvlc, Kvlp, Knc1, Knc2, Knc3, Km |
| S–V | Thành tiền Vật liệu, Vật liệu phụ, Nhân công, Máy |
| W–AF | TỔNG CỘNG, CHI PHÍ CHUNG, TN CT TÍNH TRƯỚC, ĐƠN GIÁ XD TRƯỚC THUẾ, THUẾ GTGT, ĐƠN GIÁ XD SAU THUẾ, CHI PHÍ DỰ PHÒNG, **ĐƠN GIÁ THẦU** |

GXD có cờ `CF_TDGTH` = "Tính đơn giá tổng hợp" trong sheet `Config`.

**Khác với chế độ mã `TG` hiện có của skill:** `TG` (đơn giá trọn gói) chỉ là một con số trọn gói
nhập tay trong `khoi_luong.csv` (`don_gia_tron_goi`), gộp vào chi phí vật liệu theo PL III
TT 36/2026, không lưu thành phần cấu thành, không có sheet riêng. Mã TH thì **trong suốt**: lưu
được danh sách công tác con và tính lại được từ hao phí. TG giữ nguyên cho trường hợp thật sự chỉ
có một con số trọn gói; TH dùng khi có thành phần cấu thành.

## 2. Mô hình dữ liệu mới — `don_gia_tong_hop.csv`

Một file trong thư mục dữ liệu của hồ sơ (cùng cấp với `dinh_muc.csv`, `khoi_luong.csv`).
Mẫu: `data/mau/don_gia_tong_hop.mau.csv` (chưa tạo — tạo ở v2.1 cùng code).

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| ma_th | ✔ | Mã đơn giá tổng hợp, vd. `TH1`. Dùng làm `ma_hieu` trong `khoi_luong.csv` |
| ten_th | ✔ | Tên công tác tổng hợp, vd. `Công tác tổng hợp 1` |
| don_vi_th | ✔ | Đơn vị của mã TH (m3, m2, cái…) — đơn vị tính đơn giá thầu |
| ma_con | ✔ | Mã định mức thành phần (mã TT 38, vd. `AB.11111`) |
| ten_con |  | Tên công tác con (để trống thì lấy theo định mức) |
| don_vi_con |  | Đơn vị khối lượng của thành phần (để trống thì lấy theo định mức) |
| kl_con | ✔ | Khối lượng thành phần trên 1 đơn vị mã TH (vd. 1 m3 TH cần 0,5 m3 AB.11111) |
| he_so_vl, he_so_nc, he_so_m |  | Hệ số điều chỉnh định mức riêng cho thành phần này trong mã TH (mặc định 1) |
| can_cu_he_so | khi có hệ số ≠ 1 | Căn cứ áp hệ số |
| ghi_chu |  | Ghi chú (vd. lý do gộp) |

Quy tắc:
- Một mã TH = nhiều dòng (một dòng một thành phần). Mã TH không được rỗng (ít nhất 1 thành phần).
- `ma_con` phải là mã định mức có trong `dinh_muc.csv`/TT 38, **không được là một mã TH khác** —
  v2.0 không cho TH lồng TH (xem câu hỏi mở Q4).
- `kl_con` > 0. Đơn vị của thành phần là đơn vị khối lượng (như `don_vi` trong `khoi_luong.csv`);
  hệ số `quy_doi` của thành phần lấy theo định mức của mã con (không có cột riêng).
- Cấp phối vữa (`cap_phoi`) của thành phần: dùng cột `cap_phoi` như trong `khoi_luong.csv` nếu cần
  (thêm cột ở v2.1 khi triển khai, không có trong bản thiết kế này nếu không cần).

## 3. Cách tính (quyết định thiết kế)

### D1. Tính chi phí chung / thu nhập chịu thuế MỘT LẦN ở cấp mã TH, không tính ở cấp thành phần
Mỗi thành phần chỉ tính đến **chi phí trực tiếp** (VL, NC, M) theo `tinh_ma()` hiện có
(`scripts/dutoan_core.py`), với khối lượng thành phần = `kl_con × KL của dòng TH trong khoi_luong.csv`.
Sau đó cộng VL/NC/M của các thành phần lại thành T của mã TH, rồi áp C, TT, TL, GTGT **một lần**
theo đúng công thức của `tinh_doan_vung()`/`DGCT` cho một mã thường. Lý do: GXD tính C/TL ở cấp TH
(cột W–AF của sheet `Don gia tong hop`); tính C/TT ở cấp thành phần rồi cộng lại sẽ tính trùng
chi phí chung trên cùng một đồng chi phí trực tiếp.

### D2. Đơn giá thầu = đơn giá sau thuế + dự phòng
`Đơn giá thầu = (T + C + TT + TL) × (1 + GTGT) + dự phòng`, với dự phòng mặc định 0 và cấu hình
riêng theo mã TH (tỷ lệ dự phòng trong config, khóa `du_phong_theo_th`, vì dự phòng ở cấp TH là
khoản dự phòng của nhà thầu cho công tác đó, khác với dự phòng cấp dự án trong `TH_CPXD`).
Nếu không cấu hình, đơn giá thầu = đơn giá sau thuế.

### D3. Hệ số Kvlc/Kvlp/Knc1–3/Km
GXD có các hệ số này ở cấp thành phần trong sheet TH (cột M–R). Trong skill, `he_so_vl/he_so_nc/
he_so_m` ở cấp thành phần đã bao hàm Kvlc/Kvlp (vật liệu) và Knc/Km (nhân công/máy) theo cách
`tinh_ma()` đang làm. Ở v2.1, khi nhập từ GXD (`nhap --kieu gxd`), map: Kvlc × Kvlp → `he_so_vl`,
Knc1–3 → **giữ riêng 3 cột trong báo cáo nhập** (theo N-4, chưa gộp khi chưa rõ ý nghĩa), Km →
`he_so_m`. Không bịa thêm cột hệ số riêng cho TH cho đến khi rõ ngữ nghĩa Knc1–3.

### D4. Mã TH dùng như một mã thường ở mọi chỗ khác
- `khoi_luong.csv`: dòng có `ma_hieu = TH1` như dòng mã thường (KL, đơn vị = `don_vi_th`).
- `PT_DG`: mở rộng mã TH thành các dòng thành phần (mỗi thành phần một khối hao phí, có tiêu đề
  "Thành phần của TH1"), để thẩm tra được từng hao phí.
- `HP_CT` / `TH_VT`: hao phí tài nguyên của mã TH = tổng hao phí của các thành phần (KL dòng TH ×
  kl_con × hao phí định mức mã con) — cộng dồn như mã thường, không cần sheet riêng.
- `DT_CT`: một dòng cho mã TH, đơn giá VL/NC/M là tổng của các thành phần; thêm cột ghi chú
  "Đơn giá tổng hợp — xem DG_TH".
- `kiemtra-dulieu`: thêm kiểm tra S-mới — mã TH không có trong `don_gia_tong_hop.csv` thì CHẶN;
  thành phần không phải mã định mức hợp lệ thì CHẶN; TH lồng TH thì CHẶN; `kl_con` ≤ 0 thì CHẶN.

## 4. Sheet mới `DG_TH` trong `xuat_excel.py` (mở rộng `DGCT` nếu hợp lý)

Một sheet riêng cho mã TH (không gộp vào `DGCT` của mẫu `doan_vung` vì `DGCT` tính theo vùng/đoạn,
còn TH là một đơn giá duy nhất). Bố cục theo đúng cột của GXD (mục 1):

| Cột | Nội dung |
|---|---|
| A–B | STT, mã TH |
| C | Thành phần công việc (tên mã con) |
| D–E | Đơn vị, khối lượng thành phần (kl_con) |
| F–H | Hao phí định mức, giá, thành tiền từng loại (VL / VL phụ / NC / M) |
| I | Tổng cộng thành phần |
| J–L | Chi phí chung, TN chịu thuế, đơn giá trước thuế (cấp TH) |
| M–O | GTGT, đơn giá sau thuế, chi phí dự phòng |
| P | **Đơn giá thầu** |

Mỗi mã TH một khối: dòng tiêu đề mã TH (tên, đơn vị, đơn giá thầu), các dòng thành phần, dòng cộng
VL/NC/M, dòng C/TT/TL/GTGT/dự phòng. Công thức Excel đầy đủ (đổi KL hoặc giá → tự tính lại),
như các sheet khác của skill.

## 5. Nhập từ GXD (v2.1, mở rộng N-3)

`nhap_du_toan_excel.py --kieu gxd` đọc thêm sheet `Don gia tong hop` → sinh
`don_gia_tong_hop.csv` theo mục 2, và các dòng TH trong `Du toan XD` → `khoi_luong.csv` với
`ma_hieu = TH…`. Lưu ý: file mẫu GXD hiện có chỉ có demo TH1 trống (giá trị 0) — không đủ để suy
ra quy tắc gộp, nên bước nhập này chỉ làm được sau khi có file GXD thật có mã TH có số liệu
(xem Q1).

## 6. Câu hỏi mở — phải trả lời trước khi code (v2.1)

- **Q1. Quy tắc gộp thành mã TH là gì?** File demo TH1 trống, giá trị 0 — không suy ra được GXD
  gộp các công tác nào thành một mã TH, và khi nào thì gộp. Cần một file GXD thật có mã TH có số
  liệu, hoặc hỏi người dùng lấy ví dụ thực tế, rồi mới code nhập/tính.
- **Q2. Căn cứ pháp lý của đơn giá tổng hợp?** Chưa xác minh TT 36/2026 (PL III) có điều khoản nào
  quy định đơn giá tổng hợp hay không, hay đây chỉ là cách làm của GXD. Cần đối chiếu văn bản
  trước khi ghi căn cứ vào tài liệu.
- **Q3. Dự phòng ở cấp TH có ý nghĩa gì?** GXD có cột "CHI PHÍ DỰ PHÒNG" trong sheet TH, nhưng
  dự phòng thường là khoản cấp dự án (trong `TH_CPXD` của skill đã có DP ở cấp dự án cho mẫu
  `doan_vung`). Cần xác minh dự phòng TH là dự phòng của nhà thầu, hay chỉ là cột để trống.
  Nếu không xác minh được thì v2.1 để mặc định 0 và ghi rõ trong tài liệu.
- **Q4. TH có được lồng TH không?** Thiết kế này cấm (D-mục 2). Nếu GXD cho phép TH chứa TH thì
  phải sửa mô hình thành đệ quy và thêm kiểm tra vòng lặp. Cần kiểm chứng trên file GXD thật.
- **Q5. Hệ số Knc1–3 ở cấp TH?** Theo N-4, Knc1–3 chưa rõ ý nghĩa nên giữ riêng trong báo cáo
  nhập. Nếu ở v2.1 vẫn chưa rõ thì mã TH nhập từ GXD sẽ mất thông tin Knc1–3 — cần hỏi người
  dùng hoặc đọc tài liệu GXD về ý nghĩa 3 hệ số này trước khi chốt mapping.

## 7. Kế hoạch kiểm thử cho v2.1 (chưa làm)

1. Tạo `data/mau/don_gia_tong_hop.mau.csv` + ví dụ nhỏ: 1 mã TH gồm 2–3 mã TT38 có sẵn trong
   `data/vi-du/` (vd. TH gồm 1 mã đào + 1 mã đắp), tính tay VL/NC/M/C/TT/TL/GTGT đến đồng.
2. Chạy `dutoan.py tinh` trên ví dụ đó, đối chiếu tổng GXD với phép tính tay; kiểm tra `DG_TH`,
   `PT_DG` mở rộng, `TH_VT` cộng đúng hao phí tài nguyên.
3. Nhập một file GXD thật có mã TH (khi có) bằng `nhap --kieu gxd`, đối chiếu `don_gia_tong_hop.csv`
   sinh ra với sheet `Don gia tong hop` gốc.
4. Chạy lại 6 ví dụ chuẩn — tổng không đổi (mã TH không ảnh hưởng ví dụ cũ).
