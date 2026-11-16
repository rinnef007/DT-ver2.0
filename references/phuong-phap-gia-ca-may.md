# Phương pháp xác định giá ca máy (PL IV TT 37/2026)

Tính giá ca máy từ đầu bằng `scripts/gia_ca_may.py`, thay vì chỉ lấy giá công bố của Sở XD.
Căn cứ: **Phụ lục IV Thông tư 37/2026/TT-BXD** (ngày 26/6/2026, hiệu lực 01/7/2026) — đã đối chiếu
nguyên văn (file PDF của Chính phủ, `datafiles.chinhphu.vn`).

## 1. Công thức (PL IV mục III)

Giá ca máy gồm 5 khoản (công thức 4.1):

```
CCM  = CKH + CSC + CNL + CNC + CCPK
```

| Khoản | Công thức | Ghi chú |
|---|---|---|
| CKH — khấu hao (4.2) | `(G − GTH) × ĐKH / NCA` | G: nguyên giá trước thuế; GTH: giá trị thu hồi = 10% × G nếu G ≥ 30.000.000 đ, ngược lại 0; ĐKH: định mức khấu hao %/năm; NCA: số ca/năm |
| CSC — sửa chữa (4.3) | `G × ĐSC / NCA` | ĐSC: định mức sửa chữa %/năm |
| CNL — nhiên liệu, năng lượng (4.4) | `Σ ĐNLi × GNLi × KPi` | ĐNL: định mức tiêu hao 1 ca; GNL: giá nhiên liệu; KP: hệ số nhiên liệu phụ — xăng 1,02; diezel 1,03; điện 1,05 |
| CNC — nhân công vận hành (4.5) | `Σ Ni × CTLi` | Ni: số nhân công loại i; CTLi: đơn giá ngày công loại i |
| CCPK — chi phí khác (4.6) | `G × ĐK / NCA` | ĐK: định mức chi phí khác %/năm |

- Máy làm việc ở vùng nước mặn, nước lợ, môi trường ăn mòn cao: ĐKH và ĐSC nhân 1,05 (PL IV mục III.1.đ, III.2.b) — cờ `--an-mon`.
- Giá ca máy chờ đợi (PL IV mục II.3): `0,5 × CKH + 0,5 × CNC + CCPK`.
- Giá điều chỉnh CCMĐC: CKH/CSC/CCPK không đổi (chỉ phụ thuộc nguyên giá và định mức %/năm), chỉ CNL/CNC
  tính lại theo giá nhiên liệu và tiền lương tại thời điểm điều chỉnh. Cho giá mới bằng `--gia-*-moi`,
  `--ma-vung-moi` thì cột `gia_ca_may_dieu_chinh` = CCM theo giá mới; không cho giá mới thì CCMĐC = CCM.
- Nguyên giá G (PL IV mục III.1.c): giá máy mới theo mặt bằng thị trường, gồm giá mua (chưa GTGT), thuế nhập
  khẩu, vận chuyển, bốc xếp, bảo quản, lắp đặt lần đầu, chuyển giao công nghệ, chạy thử; không gồm chi phí
  lắp đặt/tháo dỡ trạm trộn, cần trục từ lần thứ hai trở đi (tính riêng vào chi phí khác của dự toán).

Quy ước làm tròn của script: **làm tròn từng khoản về đồng trước rồi mới cộng** (như chế độ `lam_tron:
tung_buoc` của skill) — CCM, giá chờ đợi, CCMĐC in ra luôn bằng đúng tổng các thành phần đã làm tròn.

## 2. Dữ liệu đầu vào

### 2.1. File định mức ca máy — `data/gia-ca-may/dinh_muc_ca_may_tt37.csv`

| Cột | Ý nghĩa |
|---|---|
| ma_may | Mã máy theo Mục V PL IV (vd. `M101.0101`) |
| ten_may | Tên máy |
| nguyen_gia | Nguyên giá trước thuế, đồng |
| so_ca_nam | Số ca làm việc trong năm (NCA) |
| dm_khau_hao, dm_sua_chua, dm_chi_phi_khac | Định mức %/năm (ghi số phần trăm, vd. 17 = 17%) |
| dm_tieu_hao_nl | Định mức tiêu hao nhiên liệu 1 ca (0 nếu máy không dùng nhiên liệu) |
| loai_nl | `diezel` / `xang` / `dien` |
| he_so_nl_phu | Hệ số KP (để trống → lấy mặc định theo loại nhiên liệu) |
| nhan_cong_van_hanh | Vd. `1 nhân công vận hành`, `2 nhân công vận hành`, `1 lái xe` (các thành phần nối bằng `+`) |
| cong_thuc_nl | Tuỳ chọn, dạng GXD cho máy nhiều nhiên liệu: `16*diezel*1,03+5*xang*1,02` (ghi đè dm_tieu_hao_nl/loai_nl/he_so_nl_phu) |
| nguon | Nguồn trích (Mục V PL IV, bảng GXD…) |

Máy chưa có nguyên giá hoặc định mức thì script bỏ qua kèm cảnh báo — **không bịa số liệu**.

### 2.2. Giá đầu vào (người dùng cung cấp theo thời điểm tính)

- Giá nhiên liệu: `--gia-diezel`, `--gia-xang` (đ/lít), `--gia-dien` (đ/kWh) — theo thông báo của nhà cung
  cấp / giá bán điện nhà nước tại thời điểm tính (PL IV mục III.3.d). Không có giá mặc định trong script.
- Giá nhân công vận hành: lấy từ `data/nhan-cong/gia_nhan_cong_chuyen_doi_2026.csv` theo `--ma-vung`
  (mặc định `HN-V1-KV1`): `Nhân công vận hành máy, điều khiển máy` cho "nhân công vận hành",
  `Lái xe` cho "lái xe"; hoặc ghi đè bằng `--gia-van-hanh` / `--gia-lai-xe`.
- Thành phần nhân công khác (thuyền trưởng, thuyền phó, thủy thủ, thợ máy, thợ điện, máy trưởng…)
  **chưa hỗ trợ ở v2.0** — máy đó được tính thiếu CNC và ghi rõ cảnh báo. Bảng đủ cho đội tàu sông/biển
  làm ở v2.1.

## 3. Cách chạy

```bash
# Tính 3 máy mẫu (giá VÍ DỤ: diezel 20.000 đ/lít, NC vận hành HN-V1-KV1)
python scripts/gia_ca_may.py --dinh-muc data/gia-ca-may/dinh_muc_ca_may_tt37.csv \
    --ma-vung HN-V1-KV1 --gia-diezel 20000 \
    --ngay-ap-dung 2026-11-16 --khu-vuc "Hà Nội – Vùng I, Khu vực 1" \
    --ra data/gia-ca-may/gia_ca_may.csv

# Tính giá điều chỉnh theo giá diezel mới 22.000 đ/lít
python scripts/gia_ca_may.py --dinh-muc data/gia-ca-may/dinh_muc_ca_may_tt37.csv \
    --ma-vung HN-V1-KV1 --gia-diezel 20000 --gia-diezel-moi 22000 \
    --ra /tmp/gia_ca_may_dieu_chinh.csv
```

Đầu ra `gia_ca_may.csv` dùng được trực tiếp làm `gia_tai_nguyen.csv` cho loại M (cột `ma_tn`, `ten_tn`,
`don_vi`, `loai`, `vung`, `don_gia`, `nguon`, `ngay_ap_dung`, `khu_vuc`, `ty_le_luong`) + các cột thành
phần `ckh`, `csc`, `cnl`, `cnc`, `ccpk`, `gia_ca_may_cho_doi`, `gia_ca_may_dieu_chinh` để đối chiếu.
`ty_le_luong = CNC / CCM` — tỷ lệ tiền lương trong giá ca máy, dùng để tính hệ số Km
(xem `references/chuan-bi-du-lieu.md` mục 2, cột `ty_le_luong`).

## 4. Ví dụ kiểm chứng tay (3 máy mẫu)

Giá đầu vào VÍ DỤ (không phải giá thật): diezel 20.000 đ/lít; NC vận hành HN-V1-KV1 457.000 đ/công
(CV 14502/SXD-KTXD Sở XD Hà Nội). Đã kiểm chứng bằng phép tính độc lập (Decimal) đến đồng.

### M101.0101 — Máy đào một gàu, bánh xích, gầu 0,40 m3

G = 809.944.000 đ; NCA = 280; ĐKH = 17%; ĐSC = 5,8%; ĐK = 5%; DMTH = 43 lít diezel; KP = 1,03;
1 nhân công vận hành.

- GTH = 10% × 809.944.000 = 80.994.400
- CKH = (809.944.000 − 80.994.400) × 17% / 280 = 123.921.432 / 280 = 442.576,54 → **442.577**
- CSC = 809.944.000 × 5,8% / 280 = 46.976.752 / 280 = 167.774,11 → **167.774**
- CNL = 43 × 20.000 × 1,03 = **885.800**
- CNC = 1 × 457.000 = **457.000**
- CCPK = 809.944.000 × 5% / 280 = 40.497.200 / 280 = 144.632,86 → **144.633**
- **CCM = 2.097.784**; giá chờ đợi = 0,5×442.577 + 0,5×457.000 + 144.633 = 594.421,5 → **594.422**;
  ty_le_luong = 457.000 / 2.097.784 = 0,217849

### M105.0202 — Máy rải hỗn hợp bê tông nhựa 100 t/h

G = 1.520.612.000 đ; NCA = 180; ĐKH = 14%; ĐSC = 6,4%; ĐK = 5%; DMTH = 50 lít diezel; KP = 1,03;
2 nhân công vận hành.

- GTH = 152.061.200
- CKH = 1.368.550.800 × 14% / 180 = 191.597.112 / 180 = 1.064.428,40 → **1.064.428**
- CSC = 1.520.612.000 × 6,4% / 180 = 97.319.168 / 180 = 540.662,04 → **540.662**
- CNL = 50 × 20.000 × 1,03 = **1.030.000**
- CNC = 2 × 457.000 = **914.000**
- CCPK = 1.520.612.000 × 5% / 180 = 76.030.600 / 180 = 422.392,22 → **422.392**
- **CCM = 3.971.482**; giá chờ đợi = 0,5×1.064.428 + 0,5×914.000 + 422.392 = **1.411.606**;
  ty_le_luong = 914.000 / 3.971.482 = 0,230141

### M108.0103 — Máy phát điện lưu động 37,5 kVA

G = 117.173.000 đ; NCA = 170; ĐKH = 12%; ĐSC = 3,9%; ĐK = 5%; DMTH = 24 lít diezel; KP = 1,03;
1 nhân công vận hành.

- GTH = 11.717.300
- CKH = 105.455.700 × 12% / 170 = 12.654.684 / 170 = 74.439,32 → **74.439**
- CSC = 117.173.000 × 3,9% / 170 = 4.569.747 / 170 = 26.880,86 → **26.881**
- CNL = 24 × 20.000 × 1,03 = **494.400**
- CNC = 1 × 457.000 = **457.000**
- CCPK = 117.173.000 × 5% / 170 = 5.858.650 / 170 = 34.462,65 → **34.463**
- **CCM = 1.087.183**; giá chờ đợi = 0,5×74.439 + 0,5×457.000 + 34.463 = 300.182,5 → **300.183**;
  ty_le_luong = 457.000 / 1.087.183 = 0,420352

Cả 3 máy: định mức và nguyên giá đã đối chiếu từng số với **Mục V PL IV TT 37/2026**
(vd. M101.0101: 280 ca/năm, 17,0%, 5,80%, 5%, 43 lít diezel, 1 nhân công vận hành, 809.944 nghìn đồng).

## 5. Phạm vi v2.0 và việc còn lại (v2.1)

- **v2.0: chỉ 3 máy mẫu trên**, kiểm chứng tay đến đồng. File `gia_ca_may.csv` hiện tại dùng giá VÍ DỤ —
  khi lập hồ sơ thật, chạy lại script với giá nhiên liệu và giá nhân công tại thời điểm tính.
- **Bảng đủ để v2.1:** Mục V PL IV có khoảng 908 máy; bảng GXD đã xuất (`tbGiaCaMay`, 4 bộ giống hệt nhau)
  có 827 máy. Việc còn lại: trích đủ 908 máy từ Mục V, đối chiếu từng số với văn bản (không lấy số GXD
  làm chuẩn tuyệt đối), rồi chạy script cho toàn bảng. Lưu ý từ kiểm tra bảng GXD: 18 máy chưa có nguyên
  giá (chủ yếu họ M203.*) — không tính được cho đến khi có nguyên giá; 13 máy nhiều nhiên liệu đã có
  công thức `cong_thuc_nl` dạng GXD (script đã đọc được); 324 máy DMTH = 0 (không dùng nhiên liệu,
  vd. rơ mooc) nên CNL = 0; HSTH trong bảng GXD khớp quy tắc GTH (10% nếu G ≥ 30 triệu, ngược lại 0)
  ở mọi máy có ghi HSTH.
- Đối chiếu với GXD: sheet `Gia ca may XD` của GXD tính cùng 5 khoản trên (xem `references/doi-chieu-gxd.md`
  mục 9); GXD lưu thêm các cột chi phí tại thời điểm gốc và giá điều chỉnh CCMĐC — script này tính CCMĐC
  theo cùng nguyên tắc (chỉ CNL/CNC thay theo giá mới).
