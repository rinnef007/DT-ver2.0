# TT 38/2026/TT-BXD — quy định áp dụng định mức và hao phí vật liệu

Trích từ **bộ phụ lục thay thế theo CV 9947/BXD-VPB ngày 29/6/2026** (PL I–VIII TT 38/2026 kèm PL V TT 36/2026), người dùng cung cấp ngày 15/10/2026. **[ĐÃ ĐỐI CHIẾU]** với văn bản đó; các quy định dưới đây giống bản ban hành ban đầu (so sánh tại `data/tt38/so_sanh_ban_goc_cv9947.md`). Có đính chính/thay thế mới thì trích lại.

Dữ liệu đã trích nằm ở `data/tt38/` (xem mục 6). Skill tự dùng bộ này khi hồ sơ không có `dinh_muc.csv` riêng.

## 1. Hao phí vật liệu trong định mức dự toán đã gồm hao hụt thi công

| Phụ lục | Quy định (thuyết minh chung, mục 1.c) |
|---|---|
| II – Dự toán xây dựng công trình | "Mức hao phí vật liệu trong định mức đã bao gồm hao hụt vật liệu ở khâu thi công; riêng đối với các loại cát xây dựng còn bao gồm hao hụt do độ dôi của cát." |
| III – Lắp đặt hệ thống kỹ thuật | "Mức hao phí vật liệu trong định mức đã bao gồm hao hụt vật liệu ở khâu thi công." **Ngoại lệ (Chương II, mục 8):** lắp đặt ống bê tông, cống hộp bê tông, ống gang **chưa** tính hao hụt thi công; tỷ lệ hao hụt thi công 0,5% trên 100 m chiều dài ống, cống hộp. |
| II – Cốt thép | Định mức 1 tấn cốt thép đã gồm hao hụt thép khâu thi công; **chưa** gồm thép nối chồng, thép chống giữa các lớp, thép chờ, kết cấu thép phi tiêu chuẩn chôn sẵn. |
| II – Cọc khoan nhồi có ống vách cố định | Hao hụt vữa bê tông cọc nhồi bằng 5%. |

→ **Không nhân thêm hệ số hao hụt vật liệu** cho công tác dùng định mức PL II, III (trừ các ngoại lệ ghi trong thuyết minh chương), **trừ trường hợp hồ sơ sửa chữa ở mục 2.**

## 2. Hồ sơ sửa chữa, bảo dưỡng — PL VI, mục 3 thuyết minh

- **3.b** Công tác sửa chữa **chưa quy định trong tập định mức sửa chữa** (đào, đắp đất đá cát; sản xuất, lắp dựng cấu kiện bê tông đúc sẵn, cấu kiện gỗ, sắt thép; lắp đặt hệ thống điện, nước…) → áp định mức dự toán xây dựng công trình và điều chỉnh: **vật liệu k = 1,02; nhân công k = 1,15; máy k = 1,05.**
- **3.c** Định mức sửa chữa chưa gồm hao phí gia công, lắp dựng, tháo dỡ dàn giáo, khung dàn, sàn đạo, giằng chống, gia cố… và vận chuyển vật liệu, phế thải ngoài phạm vi quy định.
- **3.d** Cấp phối vữa xây, vữa bê tông, bê tông nhựa dùng cho sửa chữa áp dụng định mức cấp phối của định mức dự toán xây dựng (PL VII).
- Mã PL VI (SA., SB., SE., SF. …) **đã là định mức sửa chữa — không nhân hệ số 3.b.**
- Chương PL VI: I phá dỡ, tháo dỡ, làm sạch · II sửa chữa, gia cố bộ phận, kết cấu · III sửa chữa công trình giao thông trong đô thị · IV bảo dưỡng công trình giao thông trong đô thị.

Trong Skill: khai `"loai_ho_so": "sua_chua"` → script tự nhân 1,02/1,15/1,05 cho các dòng dùng mã PL II/III (khi dòng chưa khai hệ số riêng), ghi căn cứ "PL VI mục 3.b"; soát S14 cảnh báo nếu mã PL VI bị nhân hệ số hoặc mã PL II/III trong hồ sơ sửa chữa chưa nhân. Tắt tự động: `"tu_dong_he_so_sua_chua": false`.

## 3. Bê tông: "Vữa bê tông" và cấp phối PL VII

- PL II Chương VI: đổ bê tông định mức theo 3 dây chuyền — (1) vữa trộn bằng máy trộn tại hiện trường, đổ thủ công; (2) trạm trộn/bê tông thương phẩm, đổ bằng cần cẩu; (3) trạm trộn/thương phẩm, đổ bằng máy bơm.
- Đổ thủ công nhưng dùng vữa trạm trộn/thương phẩm: **nhân công × 0,6 và không tính máy trộn**. Đổ bằng xe bơm tự hành: nhân công × 0,9; thay máy bơm tĩnh bằng xe bơm, hao phí × 0,8.
- Định mức đổ bê tông ghi vật liệu là **"Vữa bê tông" (m³)**, ví dụ AF.11210 bê tông móng ≤250 cm: 1,025 m³ vữa (đã gồm hao hụt vữa 2,5% khi đổ thủ công/cần cẩu — PL VII bảng 21.2000).
- Giá 1 m³ vữa bê tông: (a) theo **cấp phối PL VII** (xi măng, cát, đá, nước theo mác, độ sụt, cỡ đá, loại xi măng) × giá vật liệu; cấp phối PL VII **chưa** tính hao hụt khâu vận chuyển, bảo quản, thi công; hoặc (b) giá bê tông thương phẩm theo công bố/báo giá.
- Trong Skill: cột `cap_phoi` của `khoi_luong.csv` (vd. `11.12323` = PC40, độ sụt 6÷8 cm, đá dmax 20 mm, mác 250). Script thay dòng "Vữa bê tông" bằng thành phần cấp phối × hao phí vữa. Tra mã: `dutoan.py tra --cap-phoi "PC40 6 ÷ 8 20mm 250"`.
- Mác bê tông ↔ cấp độ bền (PL VII): 100 ↔ B7,5; 150 ↔ B10, B12,5; 200 ↔ B15; 250 ↔ B20; 300 ↔ B22,5; 350 ↔ B25, B27,5; 400 ↔ B30 … (xem bảng đầy đủ trong PL VII Chương I).

## 4. Hao hụt vật liệu — PL VII Phần 2 (dữ liệu: `data/tt38/hao_hut_tt38.csv`)

Dùng cho vật liệu **không** có trong định mức dự toán (tính theo thiết kế) hoặc khi lập định mức mới, quản lý vật tư:
- 21.1000 hao hụt thi công theo % khối lượng gốc (vd. cáp các loại 1,0%; xi măng 1,0%; thép tròn cây 2,0%; thép tấm 5,0%; gạch thẻ 1,5%…).
- 21.2000 hao hụt vữa bê tông: đổ thủ công/cần cẩu 2,5%; bơm 1,5%; cọc nhồi vách bentonite 10%; cọc nhồi có ống vách 5%; bê tông đúc sẵn 1,5%; bê tông hầm 3%…
- 21.3000 trung chuyển; 21.4000 gia công (vd. rửa sỏi 1,10 m³ sỏi bẩn/1 m³); 21.5000 vận chuyển và bảo quản tại kho.
- Vật liệu luân chuyển (ván khuôn, giàn giáo, cây chống): số lần luân chuyển và tỷ lệ bù hao hụt quy định trong PL VII Chương III–IV và thuyết minh PL II Chương VI.

## 5. Một số quy định điều chỉnh khác thường gặp

- PL IV: lắp đặt hoàn toàn thủ công → nhân công × 1,5, không tính máy; định mức tính cho độ cao, độ sâu ≤ 1 m (khác thì nhân hệ số theo phụ lục kèm).
- PL III: thi công đường ống, cống hộp ở mặt bằng chật hẹp → nhân công, máy × 1,1; ống bê tông khoét lòng mo → nhân công × 1,2 công tác nối.
- PL II: công tác thủ công chỉ áp dụng khi không thi công được bằng máy; độ cao chuẩn ≤ 6 m, > 6 m tính thêm bốc xếp vận chuyển lên cao.
- PL VI SB.94xxx vận chuyển phế thải: SB.941–944 trong phạm vi 1.000 m theo loại ô tô; SB.945–948 cho mỗi 1.000 m tiếp theo (nhân số km tiếp theo).

## 5b. TT 37 Điều 2 k3 — chọn nhóm lao động khi định mức cũ chưa chuyển đổi; dự thảo TT sửa TT 38

- **TT 37/2026 Điều 2 k3** [ĐÃ ĐỐI CHIẾU]: định mức trong bộ định mức chuyên ngành / địa phương ban hành trước 01/7/2026 chưa chuyển đổi sang nhóm lao động thì **chọn nhóm theo tính chất công việc** (Bảng 3.1 PL III TT 37). Đây là cơ chế dự phòng, không tự suy ra nhóm. Hạn chót TT 36 Điều 10 k1 (chuyển đổi định mức cũ sang nhóm lao động trước 01/9/2026) **đã qua**.
- **Mốc 01/01/2027** (TT 37 Điều 2 k2): Sở XD tổ chức khảo sát, xác định giá nhân công XD theo phương pháp mới để công bố, **áp dụng từ 01/01/2027**; bảng chuyển đổi (k1) chỉ là tạm thời đến hết 31/12/2026. Xem `references/chuan-bi-du-lieu.md`.
- **Dự thảo TT sửa đổi TT 38/2026** (Bộ XD lấy ý kiến, công bố 28/10/2026; chương trình soạn thảo QĐ 1759/QĐ-BXD 09/10/2026): sửa đổi định mức XD, định mức sửa chữa/bảo trì và định mức sử dụng vật liệu trong TT 38 — **chỉ là dự thảo, chưa ban hành tính đến 16/11/2026 — không áp dụng**; theo dõi lại trước khi chốt dữ liệu TT 38 (Giai đoạn 2).

## 6. Dữ liệu đã trích (`data/tt38/`)

| File | Nội dung |
|---|---|
| `dinh_muc_tt38.csv` (trên repo chia 3 phần `dinh_muc_tt38_p1..p3.csv`, gộp lại đúng bằng file gốc) | ~8.960 mã PL I–VI (bản thay thế CV 9947), từng dòng hao phí; `ma_tn` = tên tài nguyên đúng như TT 38 (bảng giá phải dùng đúng tên) |
| `ma_can_kiem_tra.csv` | 84 dòng: 79 mã cần đối chiếu văn bản (nghi lệch dòng do ô gộp không đều, bảng trình bày theo khối chưa đọc lại được, hoặc hai cách đọc cho số liệu khác nhau) và 5 mã chỉ ghi chú đơn vị 'Máy khác' — soát S18 cảnh báo khi dùng; cần dùng thì nhập hao phí đúng vào `dinh_muc.csv` của hồ sơ (định mức riêng được ưu tiên) |
| `danh_muc_tai_nguyen_tt38.csv` | **Danh mục tài nguyên** ~2.381 dòng (12 tên nhân công, ~908 máy, ~1.461 vật liệu): tên đúng như TT 38 (dùng làm `ma_tn` bảng giá), đơn vị, số mã dùng, phụ lục, ví dụ mã, cách viết khác của cùng tài nguyên (khâu tra giá coi là một), ghi chú tên chỉ có ở mã cần kiểm tra. Tra: `dutoan.py tra --tai-nguyen "máy lu" [--loai M]` |
| `bao_cao_sua_bang_khoi.md` | Kết quả đọc lại các bảng trình bày theo khối (`scripts/sua_tt38_bang_khoi.py`): mã đã sửa, mã giữ nguyên cần kiểm tra |
| `danh_muc_ma_tt38.csv` | Danh mục mã, tên, đơn vị, phụ lục, chương, nhóm |
| `cap_phoi_tt38.csv` | 378 mã cấp phối vữa bê tông (PCB30, PC40/PCB40, PCB40 + xỉ S95) và vữa xây trát PCB30 |
| `hao_hut_tt38.csv` | Bảng hao hụt PL VII Phần 2 |
| `bao_cao_trich.md` | Số bảng đọc được và danh sách bảng bộ đọc chính chưa nhận dạng (phần lớn là bảng không có mã: cấp phối, phân cấp, mục lục) |
| `bao_cao_bo_sung_luoi.md` | Kết quả đọc lại bằng bộ đọc theo lưới ô (`scripts/bo_sung_tt38_luoi.py`): mã thêm mới, mã gỡ khỏi danh sách kiểm tra, mã sửa tên/loại, mã hai cách đọc khác nhau, bảng còn chưa đọc được |
| `so_sanh_ban_goc_cv9947.md` | So sánh bản ban hành và bản thay thế |

Giới hạn: PL VIII (chi phí QLDA, tư vấn) và các bảng định mức sử dụng vật liệu khác của PL VII (xây, trát, ván khuôn, hàn…) chưa trích thành dữ liệu; vữa xây trát PCB40 chưa trích. Một số bảng ghi tên máy trong tên công tác — tên tài nguyên được suy ra (vd. "Máy đào 0,4m3"). **Trước khi dùng cho hồ sơ thật, đối chiếu ngẫu nhiên vài mã với văn bản gốc.** Tạo lại dữ liệu khi có bản phụ lục mới: `python scripts/nhap_tt38_doc.py --file Phu_luc.doc --ra data/tt38` rồi nén `.gz`; sau đó `python scripts/sua_tt38_bang_khoi.py --txt <bản text phụ lục> --data data/tt38 --ghi` và `python scripts/bo_sung_tt38_luoi.py --file Phu_luc.docx --data data/tt38 --ghi` và `python scripts/lap_danh_muc_tai_nguyen.py --data data/tt38`.

Đã sửa (15/10/2026): 37 mã trích sai do bảng trình bày theo khối (vd. AD.22111 thiếu "Đá 1x2", "Máy khác 7%" bị ghi 7 ca; AD.112xx; AC.313xx; AC.323xx); các dòng "Máy khác"/"Vật liệu khác" còn bị ghi loại máy/vật liệu được chuyển sang %; điền đơn vị trống (nhân công: công; máy: ca).

Đã bổ sung (16/10/2026) bằng bộ đọc theo lưới ô Word (`scripts/doc_bang_luoi.py`, giữ dòng trống làm vị trí giữ chỗ để căn tên – đơn vị – số): thêm 81 mã chưa có (AB.712xx, BA.192xx/193xx, BB.121xx, MI, MK, MN, MQ…); 64 mã gỡ khỏi danh sách kiểm tra vì đọc lại đủ số liệu; 24 mã sửa tên tài nguyên hoặc loại khi số liệu không đổi (vd. AL.241xx, BB.904xx tên sai; AG.62210 "Thợ lặn", SE.353/354 "Công nhân" là nhân công) và AF.31310 (bản trích cũ sót dòng vữa, nhân công 0,4 thay vì 0,74 — đã đối chiếu văn bản). Mã có hai cách đọc cho số liệu khác nhau (AF.5115x–5118x, BA.31002, SB.85323, SB.85422/85423) giữ bản cũ và đưa vào danh sách kiểm tra. Kiểm chứng bộ đọc trên toàn văn bản: 6.487/6.510 bảng một khối mã cho kết quả trùng bản trích cũ.

Còn **14 khối mã chưa có trong dữ liệu** (bảng trình bày quá phức tạp cho cả hai bộ đọc) — dùng thì tra văn bản và nhập hao phí vào `dinh_muc.csv` của hồ sơ: AB.5141x (phá đá giếng điều áp), AB.713xx, AB.721xx (nạo vét bằng tàu), AC.211xx (đóng cọc dưới nước), AC.251xx/252xx (ép trước cọc 150T), AD.422xx (đặt đường sắt khổ 1,435 m), AF.333xx (bê tông dầm cầu đúc đẩy), AF.421xx (bê tông thủy công cần cẩu 25 t), AG.524xx (cấu kiện cầu cảng), MO.015xx (ống thép áp lực trong hầm), MS.051xx/052xx (sơn thiết bị, kết cấu kim loại), DA.051xx (thí nghiệm phản ứng kiềm cốt liệu).
