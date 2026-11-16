# Mẫu hồ sơ dự toán của đơn vị (công trình dạng tuyến, nhiều địa bàn)

Rút ra từ một hồ sơ mẫu thực tế (công trình dạng tuyến, nhiều địa bàn, năm 2026). Đây là quy ước trình bày của đơn vị — khi lập hồ sơ mới cho người dùng này, mặc định dùng `mau_xuat: "doan_vung"` và các quy ước dưới đây.

## 1. Hai file đi cùng nhau

| File | Vai trò | Cấu trúc |
|---|---|---|
| Khối lượng | Bóc tách, diễn giải | `Bảng tổng hợp` (công tác × đoạn/xã, cột Tổng) ← các sheet chi tiết theo hạng mục (đào rãnh, cáp, ống, gia cố, ca cẩu, ATGT, măng xông/ODF, khoan, cự ly vận chuyển); sheet thuyết minh cho các tỷ lệ tự đặt (vd. 15% đào thủ công) |
| Dự toán | Đơn giá, tổng hợp | `thuyết minh` (căn cứ) · `TDT` (tổng hợp) · `dt-xd`, `dt-dbgt` (bảng dự toán theo hạng mục) · `dtct-sc` (đơn giá chi tiết) · `VL`, `nhân công`, `ca máy` (bảng giá theo vùng) |

## 2. Quy ước chính

- **Khối lượng theo đoạn/xã** (mỗi đoạn một cột). Mỗi đoạn gắn một **vùng giá** (vd. tỉnh A; tỉnh B vùng II). Thành tiền từng đoạn = KL × đơn giá vùng tương ứng.
- **Đơn giá chi tiết đầy đủ** cho từng mã: a) vật liệu, b) nhân công, c) máy (mỗi dòng: định mức × đơn giá × hệ số) → T → C (T × 6,2%) → TT (T × 2%) → GT → TL ((T+GT) × 6%) → G (trước thuế) → GTGT → Gxd. Đơn giá dùng trong bảng dự toán = G / số đơn vị của định mức (vd. /100).
- **Làm tròn từng bước** đến đồng (ROUND ở mỗi dòng, mỗi dòng cộng, mỗi thành tiền). → `lam_tron: "tung_buoc"`.
- **Hệ số theo dòng hao phí** (cột Hệ số): thường gặp VL 1,02; NC 1,15; M 1,05; vật tư ATGT luân chuyển 0,02 hoặc 0,01. → cột `he_so` trong `dinh_muc.csv`, **bắt buộc ghi căn cứ** (`can_cu_he_so`). **Căn cứ: PL VI TT 38/2026 mục 3.b** — hồ sơ sửa chữa dùng định mức PL II/III thì nhân VL 1,02; NC 1,15; M 1,05; mã PL VI (SA., SB.) không nhân. Skill tự áp khi `loai_ho_so: "sua_chua"`.
- **Định mức**: TT 38/2026 là căn cứ chính (sửa chữa: PL VI; xây dựng: PL II; lắp đặt: PL III). Định mức chuyên ngành chỉ dùng cho công tác TT 38 không có. Hồ sơ mẫu dùng: viễn thông (mã dạng `22.xxxxxx.xx/ĐM44_2020`), quản lý bảo dưỡng đường bộ (`QLĐCT.xxxxx`), sửa chữa (`SA.`, `SB.`), lắp đặt (`BB.`); mã tự lập `TT` (tạm tính), `CM2` (ca xe). Kiểm tra hiệu lực từng bộ định mức chuyên ngành (một số bộ trước đây do Bộ GTVT, Bộ TT&TT ban hành).
- **Bỏ hao phí có chủ ý**: đơn vị có thể để hao phí một số vật tư bằng 0 so với TT 38. Ví dụ đã xác nhận: BB.43201 trong hồ sơ cáp quang để cùm nối và màng keo bằng 0, trong khi TT 38 ghi 19 cái và 0,75 m². → giữ hao phí như hồ sơ và ghi cột `ly_do` trong `dinh_muc.csv`; S17 khi đó chỉ ghi thông tin. AI **không tự đặt hao phí về giá trị TT 38** và **không tự suy ra lý do**; nếu chưa có lý do thì hỏi người lập. Khi thẩm tra, đề nghị đưa lý do vào thuyết minh.
- **Hồ sơ QL5 quản lý, bảo dưỡng thường xuyên / sửa chữa trong bảo trì**: xác định có thuộc kế hoạch bảo trì và nguồn kinh phí trước khi chọn `che_do_chi_phi` (TT 40 hay TT 36) — xem `references/bao-tri-tt40.md`. Không tự suy ra.
- **Dự toán khảo sát** (gói tư vấn khảo sát và lập dự toán phương án sửa chữa): theo mẫu riêng — xem `references/du-toan-khao-sat.md` (cấu trúc, cách làm của đơn vị, điểm cần lưu ý); `che_do_chi_phi: "tt36_khao_sat"`.
- **VAT 8%** — đơn vị xác nhận áp dụng 8% (16/10/2026); kiểm tra lại khi chính sách giảm thuế thay đổi.
- **Định mức chuyên ngành** dùng trong hồ sơ (viễn thông, quản lý bảo dưỡng đường bộ…): đơn vị xác nhận đang dùng bản mới nhất (16/10/2026). Khi đưa vào `dinh_muc.csv` ghi số hiệu văn bản trong cột `nguon`; nhân công theo nhóm TT 37.
- **Vị trí trên tuyến cao tốc HN–HP**: xác định xã, tỉnh, vùng nhân công theo lý trình (`dutoan.py tra --ly-trinh`, danh sách 32 xã, phường tại `data/nhan-cong/xa_phuong_tuyen_hn_hp.csv`); mỗi đoạn/khu vực trong config gắn đúng vùng giá của tỉnh đó.
- **Giá nhân công**: giá chuyển đổi theo nhóm của Sở XD Hà Nội (CV 14502), Hưng Yên (CV 3385), Hải Phòng (CV 7546) có sẵn tại `data/nhan-cong/`; gán vùng nhân công trong config (`"nhan_cong": "HN-V1-KV1"`) để `can-gia --nhan-cong` điền sẵn và S22 đối chiếu.
- **TDT**: Chi phí xây dựng (XD + nhà tạm 2,2%) · QLDA (tỷ lệ × hệ số) gồm cả thẩm định TK, dự toán · Tư vấn (khảo sát nhập giá trị theo QĐ; lập BCKTKT, giám sát theo tỷ lệ; HSMT/đánh giá/thẩm định có mức tối thiểu – tối đa) · Chi phí khác (ĐBGT + nhà tạm, kiểm toán và thẩm tra quyết toán theo TMĐT) · Dự phòng 5% (VAT dự phòng = 5% × tổng VAT các khoản). → khai báo trong `tong_hop` (mục 4).
- **Căn cứ các hệ số trong TDT** — PL VIII TT 38/2026 (bản thay thế CV 9947), [ĐÃ ĐỐI CHIẾU]:
  - QLDA = (Cxd + Ctb chưa GTGT) × Nt (Bảng 1.1, nội suy) × **0,8** — mục 1.4 Chương I: chủ đầu tư tự thực hiện quản lý dự án (Điều 48 NĐ quản lý hoạt động xây dựng). Hệ số khác: biển, đảo, biên giới, xã ĐBKK 1,35; tuyến từ 2 tỉnh trở lên 1,1; thiết bị ≥ 50% 0,8. Tra: `dutoan.py ty-le --bang qlda --loai giao_thong --gia-tri <tỷ> --he-so 0.8`.
  - Thẩm định BCKTKT do cơ quan chuyên môn trực thuộc người QĐĐT tự thực hiện = **80%** chi phí thẩm tra BCKTKT (mục 4.6 Chương II); chi phí thẩm tra BCKTKT = (định mức thẩm tra thiết kế + thẩm tra dự toán) × Cxd × **1,2** (mục 4.4) → "× 0,8 × 1,2". Nếu thuê tư vấn thẩm tra thì chi phí thẩm định = 15% chi phí thẩm tra. Thẩm định TKXD triển khai sau khi dự án được duyệt do CĐT trực tiếp làm = 80% chi phí thẩm tra, tính bổ sung vào nguồn QLDA (Chương I, hướng dẫn Bảng 1.1).
  - Đây là cách đọc khớp với số trong hồ sơ mẫu; khi lập hồ sơ mới vẫn ghi rõ căn cứ từng hệ số trong cột căn cứ của `tong_hop`.
- Bảng dự toán có thể kèm cột "giá trị lần trước" và "chênh lệch" để so phiên bản — ẩn trước khi phát hành.

## 3. Những lỗi thường gặp — kiểm tra lại ở mọi hồ sơ

1. Công thức TL lấy (T + C) thay vì (T + GT) ở một vài khối đơn giá → thiếu phần TL trên TT. Importer tự phát hiện.
2. Dòng "vật liệu khác %" tính trên phạm vi không đủ các dòng vật liệu (SUM thiếu dòng). Importer tự phát hiện; cần xác định là chủ ý (vật liệu bổ sung ngoài định mức) hay sót.
3. Ký hiệu **LT** ghi cho chi phí một số công việc không xác định được KL — theo PL III TT 36/2026 là **TT** (LT là nhà tạm).
4. Số thứ tự trùng trong bảng dự toán (khi chèn thêm dòng, vd. vận chuyển theo cự ly).
5. Bảng dự toán liên kết sang file khối lượng, file khối lượng liên kết ra file khác (`[1]`, `[2]`…) → khi gửi đi số liệu có thể không cập nhật. Phát hành: dán giá trị hoặc gộp file.
6. Hàm tồn dư Google Sheets (`__xludf.DUMMYFUNCTION`); số lưu dạng chữ (lý trình, khoảng cách).
7. Ô lỗi `#N/A`, `#VALUE!` trên sheet phát hành (vd. dòng "Bằng chữ" dùng add-in không có trên máy khác); nhiều sheet ẩn tồn dư của công trình khác.
8. Tên công trình, quy mô, lý trình ghi không thống nhất giữa thuyết minh, TDT và file khối lượng; mục căn cứ chép từ hồ sơ khác — rà khi sao chép mẫu.
9. Tên vùng ghi khác nhau giữa các bảng giá (VL, nhân công, ca máy); nguồn giá ghi sai ngày tháng hoặc lấy từ bộ đơn giá cũ.
10. Tên nhân công ghi theo bậc nhưng lấy giá theo mã nhóm (hoặc ngược lại) — thống nhất cách quy đổi theo TT 37/2026.
11. Khối đơn giá dùng khung dự toán khảo sát (chi phí chung = NC × 70%, TT 5%) cho công tác không phải khảo sát — kiểm tra lại: khảo sát theo PL V TT 36 (Bảng 5.1, 5.2); công tác xây dựng theo PL III TT 36.
12. Định mức chuyên ngành/cũ dùng cho công tác đã có trong TT 38/2026; hệ số hao hụt vật liệu nhân thêm không có căn cứ.
13. Chi phí tính theo TMĐT (kiểm toán, thẩm tra quyết toán) dùng TMĐT nhập cố định — cập nhật khi tổng thay đổi.

## 4. Khai báo `tong_hop` (bảng tổng hợp kiểu TDT)

Mỗi mục: `ma`, `stt`, `ten`, `kieu`, `can_cu`, tuỳ chọn `dam` (in đậm).
- `hang_muc`: lấy tổng trước thuế các hạng mục trong bảng dự toán. `"hang_muc": ["XÂY DỰNG"]`
- `ty_le`: `ty_le` × `he_so` × tổng trước thuế các mục trong `co_so` (được dùng số cố định, vd. TMĐT). Tuỳ chọn `toi_thieu`, `toi_da`, `vat` (`true` / `false` / `"theo_co_so"`), `can_cu_he_so`.
- `gia_tri`: giá trị nhập (vd. chi phí khảo sát theo quyết định).
- `tong`: cộng các mục trong `gom`.
VAT mặc định = trước thuế × thuế suất (làm tròn). Ví dụ đầy đủ: `data/vi-du-doan/config_du_toan.json`.
