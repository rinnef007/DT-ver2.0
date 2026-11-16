# Giá nhân công xây dựng chuyển đổi theo nhóm — giai đoạn chuyển tiếp TT 37/2026

`gia_nhan_cong_chuyen_doi_2026.csv`: giá nhân công theo nhóm (Bảng 3.1 PL III TT 37/2026) do Sở Xây dựng chuyển đổi theo mục 4 Mục I PL III TT 37, áp dụng **từ 01/7/2026 đến khi có văn bản thay thế** (TT 37 Điều 2 k1; Sở XD công bố theo phương pháp mới từ 01/01/2027). Đơn vị: đồng/ngày công (8 giờ), chưa gồm các khoản bảo hiểm người sử dụng lao động nộp (đã tính trong chi phí chung), chưa gồm làm thêm giờ, ban đêm, nặng nhọc độc hại.

Đây là dữ liệu tham chiếu, **không phải bảng giá của hồ sơ**: `can-gia --nhan-cong` dùng để điền sẵn giá nhân công; `soat` (S22) cảnh báo khi giá nhân công trong `gia_tai_nguyen.csv` khác văn bản. Khi Sở XD ban hành văn bản mới, cập nhật file này và ghi vào `references/can-cu-phap-ly.md`.

| Tỉnh | Văn bản | Vùng / khu vực (`ma_vung`) |
|---|---|---|
| Hà Nội | CV 14502/SXD-KTXD ngày 02/7/2026 (Sở XD Hà Nội) | `HN-V1-KV1`, `HN-V1-KV2`, `HN-V2` — phạm vi khu vực theo QĐ 3461/QĐ-SXD ngày 22/12/2025 |
| Hưng Yên | CV 3385/SXD-KT&VLXD ngày 02/7/2026 (Sở XD Hưng Yên) | `HY-V2`, `HY-V3`, `HY-V4` |
| Hải Phòng | CV 7546/SXD-KTQLĐTXD ngày 07/7/2026 và phụ lục (Sở XD Hải Phòng) | `HP-V1`, `HP-V2` — công văn không quy định phạm vi vùng |

## Phạm vi vùng / khu vực

**Hà Nội** (QĐ 3461/QĐ-SXD; CV 14502 giữ nguyên quy định khu vực, vùng):
- Vùng I – Khu vực 1: các phường Hoàn Kiếm, Cửa Nam, Ba Đình, Ngọc Hà, Giảng Võ, Hai Bà Trưng, Vĩnh Tuy, Bạch Mai, Đống Đa, Kim Liên, Văn Miếu - Quốc Tử Giám, Láng, Ô Chợ Dừa, Hồng Hà, Lĩnh Nam, Hoàng Mai, Vĩnh Hưng, Tương Mai, Định Công, Hoàng Liệt, Yên Sở, Thanh Xuân, Khương Đình, Phương Liệt, Cầu Giấy, Nghĩa Đô, Yên Hoà, Tây Hồ, Phú Thượng, Tây Tựu, Phú Diễn, Xuân Đỉnh, Đông Ngạc, Thượng Cát, Từ Liêm, Xuân Phương, Tây Mỗ, Đại Mỗ, Long Biên, Bồ Đề, Việt Hưng, Phúc Lợi, Hà Đông, Dương Nội, Yên Nghĩa, Phú Lương, Kiến Hưng, Thanh Liệt và các xã Thanh Trì, Đại Thanh, Nam Phù, Ngọc Hồi, Gia Lâm, Thuận An, Bát Tràng, Phù Đổng, Thư Lâm, Đông Anh, Phúc Thịnh, Thiên Lộc, Vĩnh Thanh, Hoài Đức, Dương Hoà, Sơn Đồng, An Khánh.
- Vùng I – Khu vực 2: các phường Chương Mỹ, Sơn Tây, Tùng Thiện và các xã Thượng Phúc, Thường Tín, Chương Dương, Hồng Vân, Phú Xuyên, Thanh Oai, Bình Minh, Tam Hưng, Dân Hòa, Phú Nghĩa, Xuân Mai, Trần Phú, Hoà Phú, Quảng Bị, Yên Bài, Đoài Phương, Thạch Thất, Hạ Bằng, Tây Phương, Hoà Lạc, Yên Xuân, Quốc Oai, Hưng Đạo, Kiều Phú, Phú Cát, Mê Linh, Yên Lãng, Tiến Thắng, Quang Minh, Sóc Sơn, Đa Phúc, Nội Bài, Trung Giã, Kim Anh, Ô Diên, Liên Minh.
- Vùng II: các xã, phường còn lại.

**Hưng Yên** (CV 3385):
- Vùng II: các phường Phố Hiến, Sơn Nam, Hồng Châu, Mỹ Hào, Đường Hào, Thượng Hồng, Thái Bình, Trần Lãm, Trần Hưng Đạo, Trà Lý, Vũ Phúc và các xã Tân Hưng, Yên Mỹ, Việt Yên, Hoàn Long, Nguyễn Văn Linh, Như Quỳnh, Lạc Đạo, Đại Đồng, Nghĩa Trụ, Phụng Công, Văn Giang, Mễ Sở.
- Vùng III: các xã Hoàng Hoa Thám, Tiên Lữ, Tiên Hoa, Quang Hưng, Đoàn Đào, Tiên Tiến, Tống Trân, Lương Bằng, Nghĩa Dân, Hiệp Cường, Đức Hợp, Ân Thi, Xuân Trúc, Phạm Ngũ Lão, Nguyễn Trãi, Hồng Quang, Khoái Châu, Triệu Việt Vương, Việt Tiến, Chí Minh, Châu Ninh, Thái Thụy, Đông Thụy Anh, Bắc Thụy Anh, Thụy Anh, Nam Thụy Anh, Bắc Thái Ninh, Thái Ninh, Đông Thái Ninh, Nam Thái Ninh, Tây Thái Ninh, Tây Thụy Anh, Tiền Hải, Tây Tiền Hải, Ái Quốc, Đồng Châu, Đông Tiền Hải, Nam Cường, Hưng Phú, Nam Tiền Hải.
- Vùng IV: các xã, phường còn lại.

**Hải Phòng**: CV 7546 (theo chỉ đạo tại CV 8118/VP-XDCT ngày 03/7/2026 của Văn phòng UBND thành phố) chuyển đổi giá nhân công đang công bố sang nhóm theo khoản 4 Mục I PL III TT 37; công văn và phụ lục chỉ ghi Vùng I, Vùng II, **không có danh sách xã, phường** và không ghi ngày bắt đầu áp dụng. Phạm vi vùng giữ theo văn bản công bố giá nhân công Hải Phòng trước đó (chưa có trong skill) — ghi rõ căn cứ khi chọn vùng cho hồ sơ.

## Xã, phường trên tuyến cao tốc Hà Nội – Hải Phòng

`xa_phuong_tuyen_hn_hp.csv`: 32 xã, phường theo lý trình Km0-420 ÷ Km105+450 (danh sách đơn vị cung cấp 16/10/2026), chia 3 khu vực tuyến; mỗi đoạn lý trình một dòng (`tu_km`, `den_km`, `chieu` khi chỉ áp cho một chiều HN-HP hoặc HP-HN), kèm mã vùng nhân công. Tra: `dutoan.py tra --ly-trinh Km36+200`.

- Tỉnh: Khu vực 1 gồm Hà Nội (Long Biên, Gia Lâm, Bát Tràng) và Hưng Yên; Khu vực 2, 3 thuộc Hải Phòng. Danh sách gốc không ghi tỉnh — skill gán theo đoạn tuyến, khớp cách chọn vùng trong hồ sơ khảo sát mẫu (Km02 Hà Nội; Km08 Hưng Yên; Km36, Km51, Km89 Hải Phòng). **Không tra vùng theo tên xã**: nhiều tên trùng giữa các tỉnh (xã Hà Đông, xã An Khánh — Hải Phòng / phường Hà Đông, xã An Khánh — Hà Nội; xã Thượng Hồng — Hải Phòng / phường Thượng Hồng — Hưng Yên; xã Chí Minh — Hải Phòng / Hưng Yên).
- Vùng nhân công: Hà Nội — Vùng I, Khu vực 1; Hưng Yên — Phụng Công, Nghĩa Trụ, Văn Giang, Hoàn Long, Việt Yên, Yên Mỹ: Vùng II; Xuân Trúc, Phạm Ngũ Lão, Ân Thi: Vùng III; **Hải Phòng: chưa xác định** (chưa có văn bản phân vùng) — hồ sơ mẫu áp Vùng I cho Km36, Km51, Km89; ghi căn cứ khi chọn.
- Cần kiểm tra trong danh sách gốc: Nguyễn Lương Bằng (đến Km42+640) và Bình Giang (từ Km42+200) chồng nhau 440 m; đoạn Km1+400 ÷ Km1+800 chiều HP-HN chưa ghi xã.

## Ghi chú đối chiếu
- QĐ 3461/QĐ-SXD (12/2025) công bố giá theo nhóm của TT 13/2021 (vd. nhóm 2 Vùng I KV1: 400.000 đ); CV 14502 thay bằng giá chuyển đổi theo TT 37 (nhóm 2: 413.000 đ). Chỉ dùng QĐ 3461 cho phạm vi khu vực.
- CV 14502 ghi "Thông tư số 37/2021/TT-BXD" ở hai chỗ — theo ngữ cảnh là TT 37/2026/TT-BXD (lỗi đánh máy trong văn bản).
- CV 14502 còn hướng dẫn: định mức theo PL I–VII TT 38; ca máy theo PL IV TT 37, nhiên liệu theo công bố Petrolimex tại thời điểm lập, nhân công điều khiển máy theo bảng trên; vật liệu theo công bố giá quý (tháng) của Sở XD; QLDA, tư vấn theo PL VIII TT 38.
- Tên tài nguyên: "Kỹ sư" khớp tên trong định mức TT 38 (nhân công khảo sát, thí nghiệm); nhóm vận hành máy, lái xe dùng khi tính giá ca máy.
