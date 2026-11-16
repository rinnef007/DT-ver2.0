# Ví dụ Nhà để xe — chuyển mã sang TT 38/2026 — GIÁ LÀ SỐ GIẢ

Bảng dự toán hạng mục **Nhà để xe** (phần móng + phần thân, 41 dòng) chuyển toàn bộ
mã cũ (hệ ĐM 1776/1777) sang mã **TT 38/2026/TT-BXD**, giữ nguyên khối lượng và
diễn giải khối lượng của bảng gốc. Giá tài nguyên trong thư mục này là **số giả**
để chạy thử — không phải công bố giá của bất kỳ địa phương nào, không dùng để
lập hồ sơ thật.

- **Nguồn bảng gốc:** `gxd.edu.vn-Bang-Du-toan-Khoi-luong.pdf` (5 trang, bảng dự toán
  Nhà để xe trên giaxaydung.vn; mã cũ AB/AF/AE/AK/AI/AH/BA + 3 dòng tạm tính `TT`).
  Tổng bảng gốc (chỉ chi phí trực tiếp VL+NC+M, chưa có chi phí chung/TL/GTGT):
  73.690.147 đồng — **không so sánh được** với tổng ví dụ này vì đơn giá gốc là
  đơn giá cũ, còn ví dụ này dùng giá giả định theo mặt bằng 2026.
- **Định mức:** mọi mã lấy từ `data/tt38/` (TT 38/2026 đã trích). Không có
  `dinh_muc.csv` riêng trong thư mục này.
- **Chế độ chi phí:** `tt36` (xây mới), công trình dân dụng, không theo tuyến,
  Bảng 3.8 PL III TT 36/2026. Tỷ lệ: CPC 7,3% (Bảng 3.3, nấc ≤40 tỷ), TT 2,5%
  (Bảng 3.5), TL 5,5% (Bảng 3.6), nhà tạm 1,1% (Bảng 3.7, không theo tuyến,
  nấc ≤15 tỷ), GTGT 8% (ví dụ — kiểm tra thuế suất hiện hành).

## Cách chạy

```bash
python3 scripts/dutoan.py soat --data data/vi-du-nha-de-xe \
  --khoi-luong data/vi-du-nha-de-xe/khoi_luong.csv \
  --config data/vi-du-nha-de-xe/config_du_toan.json
python3 scripts/dutoan.py tinh --data data/vi-du-nha-de-xe \
  --khoi-luong data/vi-du-nha-de-xe/khoi_luong.csv \
  --config data/vi-du-nha-de-xe/config_du_toan.json \
  --out vi-du-nha-de-xe.xlsx
```

## Kết quả kiểm chứng (16/11/2026)

`soat`: **0 chặn, 0 cảnh báo**, 3 thông tin S10 (dòng tạm tính, xem dưới).

| Chỉ tiêu | Đồng |
|---|---:|
| VL | 121.079.905 |
| NC | 96.240.306 |
| M | 12.534.310 |
| T (chi phí trực tiếp) | 229.854.521 |
| C (chi phí chung 7,3%) | 16.779.380 |
| TT (công việc không XD KL 2,5%) | 5.746.363 |
| GT (chi phí gián tiếp) | 22.525.743 |
| TL (thu nhập chịu thuế tính trước 5,5%) | 13.880.915 |
| **GXDTT (chi phí XD trước thuế)** | **266.261.178** |
| GTGT 8% | 21.300.894 |
| **GXD (chi phí XD sau thuế)** | **287.562.073** |
| LT (nhà tạm 1,1%, tính riêng sau GXD) | 3.163.183 |
| GXD + LT | 290.725.256 |

Đối chiếu tay 4 dòng (xem `references/hoc-thuc-hanh.md` bài tập 6): dòng 1
(AB.11442: 1,04 công × 300.000 = 312.000 đ/m3), dòng 3 (AF.11110+11.11371:
VL 960.599,25; NC 342.400; M 55.500 đ/m3), dòng 15 (AF.11310+11.12322:
VL 1.043.801,17; NC 380.800; M 50.750 đ/m3), dòng 17 (AF.12510: VL 1.552.875;
NC 851.200; M 114.950 đ/m3). Excel xuất ra giữ công thức; tính lại bằng
LibreOffice khớp số đối chiếu Python đến đồng.

**Lịch sử tổng:** trước khi áp đề xuất dữ liệu Giai đoạn 2 (16/11/2026) GXD là
280.339.863 (AF.11310 thiếu NC/M, AK.12222 chỉ có VL, AF.12510 VL = 0).
Sau khi dữ liệu TT 38 được khép đúng (thêm dòng NC/M và 3 giá tài nguyên mới:
Vận thăng 0,8 t 500.000 đ/ca, Máy khoan bê tông 300.000 đ/ca,
Đinh, đinh vít 2.000 đ/cái — đều là giá VÍ DỤ), GXD thành **287.562.073**.

## Bảng chuyển mã (mã cũ → mã TT 38/2026)

Quy ước chung: TT 38 rút gọn mã bê tông/xây/trát từ 5 chữ số cuối thành 4 chữ
số (vd. AF.11223 → AF.11220); mác bê tông/vữa không còn nằm trong mã hiệu mà
chọn ở cột `cap_phoi` (cấp phối PL VII TT 38). Khối lượng giữ nguyên 100%
theo bảng gốc; mọi tổng diễn giải đã kiểm tra khớp với KL bảng gốc.

| STT | Mã cũ | Mã TT 38 | Cấp phối | Ghi chú |
|---:|---|---|---|---|
| 1 | AB.11442 | AB.11442 | — | Giữ nguyên (đào móng cột, đất cấp II) |
| 2 | AB.11322 | AB.11322 | — | Giữ nguyên (đào móng băng, đất cấp II) |
| 3 | AF.11111 | AF.11110 | 11.11371 | BT lót móng M100 đá 4x6. Cấp phối: PCB30, độ sụt 6÷8 cm, dmax 70mm — xem mục giả định |
| 4 | AF.11223 | AF.11220 | 11.12322 | BT móng M200 đá 1x2, rộng >250 cm |
| 5 | AF.12213 | AF.12210 | 11.12322 | BT cột (cổ móng) M200, tiết diện ≤0,1 m2, cao ≤4 m |
| 6 | AF.12313 | AF.12310 | 11.12322 | BT xà dầm, giằng nhà M200 |
| 7 | AE.21214 | AE.21210 | 12.10134 | Xây móng, dày >33 cm, vữa XM M75 |
| 8 | AF.81122 | **AF.81122** | — | Giữ nguyên (ván khuôn móng cột, vuông/chữ nhật). Lưu ý: bản trích v1 ghi nhầm mã này thành AF.51122 (đọc 8 thành 5); đề xuất Giai đoạn 2 đã xóa AF.51122 và thêm AF.81122 đúng mã TT 38 — ví dụ sửa theo 16/11/2026 |
| 9 | AF.81141 | AF.81141 | — | Giữ nguyên (ván khuôn xà dầm, giằng) |
| 10 | AF.61110 | AF.61110 | — | Giữ nguyên (cốt thép móng ≤10 mm) |
| 11 | AF.61120 | AF.61120 | — | Giữ nguyên (cốt thép móng ≤18 mm) |
| 12 | AF.61511 | AF.61511 | — | Giữ nguyên (cốt thép xà dầm, giằng ≤10 mm) |
| 13 | AF.61521 | AF.61521 | — | Giữ nguyên; mã nằm trong `ma_can_kiem_tra` nhóm A (S18) |
| 14 | AB.13411 | AB.13411 | — | Giữ nguyên (đắp cát nền móng) |
| 15 | AF.11313 | AF.11310 | 11.12322 | BT nền M200 — đã đủ 5 dòng sau đề xuất Giai đoạn 2 (16/11/2026): thêm NC nhóm 2 1,19 công, Máy khoan bê tông 0,095 ca, Máy đầm bàn 0,089 ca |
| 16 | AF.12213 | AF.12210 | 11.12322 | BT cột (thân) M200 — cùng mã dòng 5 |
| 17 | AF.12513 | AF.12510 | — | BT lanh tô M200 — đã đủ 6 dòng sau đề xuất Giai đoạn 2 (16/11/2026): thêm Vữa 1,025 m3, NC nhóm 2 2,66 công (tên đã sửa đúng, bỏ tên gộp "Nhân công nhóm 2 Máy thi công"), Máy đầm dùi 0,089 ca, Vận thăng 0,8 t 0,11 ca |
| 18 | AF.14323 | AF.14320 | 11.12322 | BT lan can, gờ chắn M200 (nhóm BT bản mặt cầu/lan can — giữ đúng nhóm cũ) |
| 19 | AF.61611 | AF.61611 | — | Giữ nguyên (cốt thép lanh tô ≤10 mm) |
| 20 | AF.61411 | AF.61411 | — | Giữ nguyên (cốt thép cột ≤10 mm) |
| 21 | AF.61421 | AF.61421 | — | Giữ nguyên (cốt thép cột ≤18 mm) |
| 22 | AF.61611 | AF.61611 | — | Giữ nguyên (cốt thép lanh tô ≤10 mm) |
| 23 | AF.81132 | AF.81132 | — | Giữ nguyên (ván khuôn cột) |
| 24 | AF.81151 | AF.81151 | — | Mã gần nhất cho ván khuôn bể giặt; TT 38 không có mã riêng cho bể giặt (nhóm ván khuôn sàn mái/lanh tô/máng nước/tấm đan) |
| 25 | AF.81152 | AF.81152 | — | Giữ nguyên (ván khuôn lanh tô) |
| 26 | AE.22214 | AE.22210 | 12.10134 | Xây tường thẳng, dày ≤33 cm, cao ≤4 m, vữa XM M75 (mã mới lấy nấc cao ≤6 m) |
| 27 | AE.26114 | AE.26110 | 12.10134 | Xây bể chứa, vữa XM M75 |
| 28 | AK.21124 | AK.21120 | 12.10134 | Trát tường ngoài dày 1,5 cm, vữa XM M75 — toàn bộ diện tích trát ngoài (tường + cột) dùng chung mã này; TT 38 không tách mã trát cột ngoài riêng |
| 29 | AK.81120 | **AK.81110** | — | Bẫy đổi mã: mã cũ AK.81120 là "1 nước trắng, 2 nước màu"; trong TT 38 nội dung này là **AK.81110**, còn AK.81120 là "3 nước trắng" |
| 30 | AK.51240 | AK.51240 | — | Giữ nguyên (lát nền, sàn gạch ≤0,09 m2) |
| 31 | AK.31130 | AK.31130 | — | Giữ nguyên (ốp tường, trụ, cột gạch ≤0,09 m2) |
| 32 | AI.61121 | AI.61121 | — | Giữ nguyên (lắp vì kèo thép, khẩu độ ≤18 m) |
| 33 | AI.61131 | AI.61131 | — | Giữ nguyên (lắp xà gồ thép) |
| 34 | AK.12222 | AK.12222 | — | Giữ nguyên (lợp mái tôn múi) — đã đủ 3 dòng sau đề xuất Giai đoạn 2 (16/11/2026): thêm Đinh, đinh vít 450 cái, NC nhóm 3 4,5 công |
| 35 | TT | **TG** | — | Tôn úp nóc — tạm tính, không có mã TT 38 (xem dưới) |
| 36 | AH.32211 | AH.32211 | — | Giữ nguyên (lắp cửa không có khuôn) |
| 37 | TT | **TG** | — | Sản xuất cửa gỗ — tạm tính, không có mã TT 38 |
| 38 | TT | **TG** | — | Sản xuất lắp dựng cửa sổ nhôm kính — tạm tính, không có mã TT 38 |
| 39 | BA.13102 | BA.13102 | — | Giữ nguyên (đèn sát trần có chụp) |
| 40 | BA.16202 | BA.16202 | — | Giữ nguyên (dây dẫn 2 ruột ≤4 mm2; dây gốc 2x0,75 mm2 nằm trong nấc này) |
| 41 | BA.18101 | **BA.17101** | — | Bẫy đổi mã: mã cũ BA.18101 là "lắp công tắc 1 hạt"; trong TT 38 nội dung này là **BA.17101**, còn BA.18101 là "lắp đồng hồ Vol kế" |

**Kết quả: 38/41 dòng chuyển được sang mã TT 38 tương đương; 3 dòng tạm tính
(35, 37, 38) không có mã định mức — dùng `TG` (đơn giá trọn gói), không bịa mã.**

## Giả định khi chọn cấp phối (bảng gốc không ghi — [ĐỀ XUẤT])

- **Bê tông M200 đá 1x2 → 11.12322** (PCB40, độ sụt 6÷8 cm, dmax 20mm, mác 200):
  cùng quy ước với `data/vi-du-tt38/` (11.12323 cho M250, PCB40, độ sụt 6÷8).
  Phương án thay thế cùng mác: 11.11323 (PCB30).
- **Bê tông lót M100 đá 4x6 → 11.11371** (PCB30, độ sụt 6÷8 cm, dmax 70mm,
  mác 100): PL VII TT 38 không có cỡ đá 4x6 chính xác; nhóm dmax 70mm (chứa
  cỡ 4x7 cm) là gần nhất với đá 4x6 (40–60 mm). Lưu ý: dãy cấp phối PCB40
  (11.12xxx) bắt đầu từ mác 150 nên M100 chỉ có ở dãy PCB30 — không dùng
  nhầm 11.12371 (đó là mác 150, không phải 100). Phương án thay thế nếu thiết
  kế giới hạn cỡ đá ≤40 mm: 11.11341 (dmax 40mm, M100).
- **Vữa XM mác 75 → 12.10134** (vữa xi măng cát vàng, mác 75): bảng gốc không
  ghi loại cát; mặc định cát vàng. Phương án thay thế: 12.10144 / 12.10154
  (cát mịn).
- **Độ sụt 6÷8 cm** cho mọi mác bê tông: bảng gốc ghi "đổ bằng thủ công",
  không ghi độ sụt; chọn độ sụt thường dùng cho đổ thủ công. Nếu thiết kế
  quy định độ sụt khác thì đổi mã cấp phối tương ứng (cùng dmax, cùng mác).

## Các điểm dữ liệu TT 38 chưa hoàn chỉnh (ảnh hưởng trực tiếp tới ví dụ này)

Những điểm này thuộc về **dữ liệu TT 38 đã trích** (`data/tt38/`), không phải
lỗi của bảng gốc hay của script. Các mục 1–4 đã được **khép lại ngày 16/11/2026**
bằng đề xuất dữ liệu Giai đoạn 2 (đối chiếu với bảng xuất GXD); chỉ mục 5 còn mở.

1. **AF.11310 (BT nền, dòng 15): ĐÃ KHÉP 16/11/2026** — nay đủ 5 dòng: VL "Vữa
   bê tông" 1,025 m3/m3 + VLK 1% + NC nhóm 2 1,19 công + Máy khoan bê tông
   0,095 ca + Máy đầm bàn 1 kW 0,089 ca. Đơn giá dòng 15: VL 1.043.801,
   NC 380.800, M 50.750 đ/m3.
2. **AK.12222 (lợp mái tôn múi, dòng 34): ĐÃ KHÉP 16/11/2026** — nay đủ 3 dòng:
   VL "Tôn múi" 118,5 m2/100m2 + VL "Đinh, đinh vít" 450 cái + NC nhóm 3
   4,5 công. Đơn giá dòng 34: VL 18.675.000, NC 1.575.000 đ/100m2.
3. **AF.12510 (BT lanh tô, dòng 17): ĐÃ KHÉP 16/11/2026** — nay đủ 6 dòng: VL
   "Vữa" 1,025 m3 + VLK 1% + NC nhóm 2 2,66 công (tên đã sửa đúng, bỏ tên gộp
   "Nhân công nhóm 2 Máy thi công" — dòng giá cho tên lỗi đó trong
   `gia_tai_nguyen.csv` đã xóa) + Máy trộn 250l 0,095 ca + Máy đầm dùi 1,5 kW
   0,089 ca + Vận thăng 0,8 t 0,11 ca. Đơn giá dòng 17: VL 1.552.875,
   NC 851.200, M 114.950 đ/m3. Lưu ý: dòng VL là "Vữa" (không phải "Vữa bê
   tông") nên `cap_phoi` không thay được — dòng 17 dùng giá Vữa chung
   1.500.000 đ/m3 (giá VÍ DỤ).
4. **AF.61521 (dòng 13): ĐÃ KHÉP 16/11/2026** — mã đã khớp với bảng xuất GXD
   sau đề xuất Giai đoạn 2 và đã xóa khỏi `ma_can_kiem_tra.csv`; `soat` không
   còn cảnh báo S18 cho ví dụ này.
5. **Tài nguyên "Vữa" của AH.32211 (dòng 36)** không có đơn vị trong dữ liệu
   TT 38 đã trích; ví dụ tạm tính theo m3 (0,01 m3/m2 cửa).

## Ba dòng tạm tính (TG)

Bảng gốc ghi mã `TT` (tạm tính) cho tôn úp nóc, sản xuất cửa gỗ, sản xuất lắp
dựng cửa sổ nhôm kính — không có mã định mức tương ứng trong TT 38 nên giữ
nguyên dạng tạm tính bằng `ma_hieu = TG` + `don_gia_tron_goi` (giá giả định,
lấy theo đơn giá gộp của chính bảng gốc: tôn úp nóc 40.000 VL + 15.000 NC =
55.000 đ/md; cửa gỗ 700.000 đ/m2; cửa sổ nhôm kính 500.000 đ/m2). Script gộp
toàn bộ đơn giá trọn gói vào VL và báo thông tin S10: chỉ áp tỷ lệ 50% theo
Bảng 3.9 PL III TT 36 khi thuộc trường hợp "báo giá trọn gói cho công việc
thiết kế riêng/công nghệ đặc thù" — 3 dòng này là vật tư/cửa thông thường
nên **không** thuộc Bảng 3.9, vẫn tính đủ tỷ lệ. Nếu hồ sơ thật xác định khác
thì khai `ty_le_theo_ma` trong config.
