---
name: du-toan-xay-dung-vn
description: Lập, kiểm tra dự toán xây dựng theo quy định Việt Nam (NĐ 206/2026/NĐ-CP, TT 36/37/38/40/2026/TT-BXD): bóc tách khối lượng, áp mã định mức, đơn giá chi tiết, khối lượng theo đoạn/xã và vùng giá, bảng tổng hợp (TDT), xuất Excel theo mẫu, thẩm tra hồ sơ có sẵn. Dùng khi nhắc tới dự toán, bóc khối lượng, định mức, đơn giá, mã hiệu, giá vật liệu, chi phí chung, thu nhập chịu thuế tính trước, TDT, chi phí bảo trì, bảo dưỡng, sửa chữa, dự toán khảo sát, QLDA, thẩm tra dự toán, G8, Eta, F1.
---

# Dự toán xây dựng Việt Nam

Skill này giúp lập và kiểm tra dự toán chi phí xây dựng theo hệ thống văn bản Việt Nam hiện hành. Nguyên tắc xuyên suốt: **AI đề xuất từng bước, người dùng xác nhận rồi mới đi tiếp**; mọi con số đều có nguồn.

## Nguyên tắc bắt buộc

1. **Không tự nhớ số liệu.** Định mức hao phí, đơn giá vật liệu, nhân công, ca máy, tỷ lệ chi phí chỉ lấy từ file dữ liệu người dùng cung cấp hoặc văn bản họ đưa. Không có thì báo thiếu, không ước lượng.
2. **Phép tính chạy bằng script** (`scripts/dutoan.py`), không tính nhẩm. File Excel xuất ra giữ công thức để kiểm tra ngược.
3. **Mỗi số có nguồn:** cột `nguon` ghi văn bản, phụ lục, bảng, thời điểm công bố giá; khối lượng ghi bản vẽ và diễn giải; hệ số và tỷ lệ ghi căn cứ.
4. **Phân biệt rõ** điều đã xác nhận, điều suy luận, điều còn thiếu: `[XÁC NHẬN]`, `[ĐỀ XUẤT]`, `[THIẾU DỮ LIỆU]`.
5. **Căn cứ pháp lý thay đổi nhanh** (ngày rà soát gần nhất: **17/11/2026**). Trước khi lập hồ sơ thật, đọc `references/can-cu-phap-ly.md`; quá ngày rà soát ghi trong file thì tra cứu lại. **Lưu ý:** NĐ 206 Điều 36 không có quy định riêng cho gói thầu đã phát hành HSMT nhưng chưa ký hợp đồng — không tự điền quy tắc khi gặp trường hợp này (NĐ 210/2026 Điều 33 chỉ quy định chuyển tiếp cho điều khoản hợp đồng, không cho dự toán, giá gói thầu). Từ **01/01/2027**, giá nhân công dùng bảng theo phương pháp mới khi Sở XD đã công bố (TT 37 Điều 2 k2); TT 37 không ghi ngày kết thúc cho bảng chuyển đổi (k1) — PL III Mục I.4 chỉ gắn nó với thời gian địa phương đang khảo sát. Hà Nội: QĐ 2036/QĐ-SXD đang áp dụng từ 26/10/2026 (người dùng xác nhận), CV 14502 cho thời điểm áp giá trước đó. Giá nhân công được Sở XD cập nhật định kỳ — skill chọn văn bản theo `thoi_diem_ap_gia` (ghi đủ ngày yyyy-mm-dd); thêm văn bản mới bằng `scripts/cap_nhat_nhan_cong.py` (`data/nhan-cong/README.md`).
6. **Dừng ở mỗi điểm xác nhận** (☐). Không gộp nhiều bước khi người dùng chưa đồng ý.
7. **Theo mẫu của đơn vị khi có.** Người dùng đã có mẫu riêng (xem `references/mau-don-vi.md`): công trình tuyến, KL theo đoạn/xã, nhiều vùng giá, đơn giá chi tiết đầy đủ, làm tròn từng bước, TDT → dùng `mau_xuat: "doan_vung"`, `lam_tron: "tung_buoc"`.

## Quy trình

Ưu tiên: bóc khối lượng → áp mã định mức → lập dự toán → thẩm tra. Có thể vào thẳng bước 7 khi chỉ cần thẩm tra hồ sơ có sẵn.

### Bước 0 — Thông tin công trình
Ghi vào `config_du_toan.json` (mẫu: `data/mau/config_du_toan.mau.json`, `data/vi-du-doan/config_du_toan.json`): dự án, công trình, loại công trình, theo tuyến hay không, chi phí XD trước thuế trong TMĐT (tra nấc tỷ lệ), **danh sách vùng giá và đoạn/xã** (đoạn → vùng), thời điểm áp giá, thuế suất GTGT, mẫu xuất, cách làm tròn.
**Chọn chế độ chi phí** (`che_do_chi_phi`): `tt36` (mặc định — Bảng 3.8 PL III TT 36) cho xây dựng mới, cải tạo, sửa chữa lập BCKTKT/dự án; `tt40_bao_duong` / `tt40_sua_chua` cho bảo dưỡng, sửa chữa **trong kế hoạch bảo trì** (TT 40/2026 — `references/bao-tri-tt40.md`); `tt36_khao_sat` cho **dự toán khảo sát xây dựng**, thí nghiệm chuyên ngành (PL V TT 36, Bảng 5.4 — `references/du-toan-khao-sat.md`). Hỏi người dùng công việc có thuộc kế hoạch bảo trì, nguồn kinh phí và văn bản chuyên ngành trước khi chọn; không tự suy ra. Các bảng định mức tỷ lệ TT 36, TT 40 và Bảng 1.1 QLDA (PL VIII TT 38) có sẵn trong `data/bang_ty_le_tt36_2026.json`, `data/bang_ty_le_tt40_2026.json`; tra nhanh: `python scripts/dutoan.py ty-le --bang qlda|ql-chu-so-huu|ks-chung|ks-khong-xd-kl|ks-phuong-an|ks-bao-cao|tv-quan-ly|tb-quan-ly-mua-sam --gia-tri <tỷ> [--loai …] [--he-so …]`.
☐ Xác nhận cấu hình và tỷ lệ tra theo PL III TT 36/2026 hoặc PL II TT 40/2026.

### Bước 1 — Dữ liệu nguồn
`python scripts/dutoan.py kiemtra-dulieu --data <thư mục>`. Cấu trúc file: `references/chuan-bi-du-lieu.md`. Dữ liệu từ G8/Eta/F1: lệnh `chuyendoi` với file ánh xạ cột. Lấy từ một hồ sơ Excel cũ: `scripts/nhap_du_toan_excel.py` (mục 6 trong chuan-bi-du-lieu.md). Chạy thử bằng `data/vi-du/`, `data/vi-du-doan/`, `data/vi-du-tt38/`, `data/vi-du-tt40/`, `data/vi-du-khao-sat/`, `data/vi-du-nha-de-xe/` (giá giả; bộ TT 38/TT 40 dùng mã TT 38 thật, bộ TT 40 theo chế độ sửa chữa trong bảo trì, bộ khảo sát theo mẫu đơn vị; bộ Nhà để xe — 41 dòng chuyển mã cũ sang TT 38, chế độ tt36, GXD sau thuế 287.562.073 đồng đã kiểm chứng đến đồng).
☐ Xác nhận bộ dữ liệu dùng để tính.

### Bước 2 — Bóc tách khối lượng
Theo `references/do-boc-khoi-luong.md`. Nguồn: bản vẽ PDF, DXF (`scripts/boc_kl_dxf.py`), bảng thống kê thiết kế, file khối lượng của đơn vị. Ghi vào `khoi_luong.csv`, mỗi dòng một (công tác, đoạn), có `dien_giai`, `nguon_ban_ve`, `trang_thai = de_xuat`. Nêu rõ giả định (cấp đất, cự ly, tỷ lệ thủ công/máy…) và tỷ lệ tự đặt phải có thuyết minh.
☐ Người dùng duyệt từng hạng mục → `xac_nhan`.

### Bước 3 — Áp mã định mức
**Định mức và mức hao phí vật liệu theo Thông tư 38/2026/TT-BXD** — đã trích sẵn 9.136 mã PL I–VI, cấp phối vữa và hao hụt PL VII vào `data/tt38/`; quy định áp dụng tại `references/tt38-quy-dinh-ap-dung.md` (đọc trước khi chọn mã). Đúng phụ lục: XD mới PL II, lắp đặt PL III/IV, sửa chữa – bảo dưỡng PL VI. Hao phí VL PL II/III đã gồm hao hụt thi công; hồ sơ sửa chữa dùng mã PL II/III thì nhân VL 1,02; NC 1,15; M 1,05 (PL VI mục 3.b — khai `loai_ho_so: "sua_chua"`). Bê tông: chọn mác vữa ở cột `cap_phoi` (`tra --cap-phoi`). Định mức chuyên ngành chỉ khi TT 38 không có, nêu lý do — đã trích sẵn CNTT (QĐ 1601 sđ QĐ 1235, QĐ 1595) và viễn thông (CV 258) tại `data/chuyen-nganh/` (đọc README ở đó; soát S23; nhân công theo cấp bậc đã chọn nhóm theo TT 37 Điều 2 k3). **Dự án chuyển đổi số (CNTT) dùng NSNN** — không dùng `dutoan.py tinh`: dùng `scripts/cntt_tt39.py`, đọc `references/cntt-tt39.md`. `python scripts/dutoan.py tra --data <dir> --tu-khoa "..."` (hoặc `--ma`). Đề xuất mã chính + mã thay thế, lý do; kiểm tra đơn vị và `quy_doi`; hệ số (theo dòng hao phí hoặc theo dòng KL) chỉ khi có căn cứ. Theo `references/ap-ma-dinh-muc.md`.
☐ Xác nhận mã hiệu và hệ số.

### Bước 4 — Giá tài nguyên theo vùng
**Skill không chứa giá** — công bố giá của Sở XD cập nhật liên tục, nên mỗi hồ sơ lấy giá kỳ hiện hành tại thời điểm lập. `python scripts/dutoan.py can-gia --data <dir> --khoi-luong … --config … --ra can_gia.csv` → danh sách đúng các tài nguyên hồ sơ dùng (tên theo TT 38) × từng vùng, giữ giá đã có, chỉ ra dòng còn trống. Đối chiếu tên trong công bố giá với danh mục tài nguyên TT 38: `dutoan.py tra --tai-nguyen "<từ khoá>" [--loai VL|NC|M]` (các cách viết khác của cùng tài nguyên dùng chung một dòng giá). Giá nhân công chuyển đổi theo nhóm của Hà Nội, Hưng Yên, Hải Phòng có sẵn (`data/nhan-cong/`): gán `"nhan_cong"` cho từng vùng trong config rồi thêm `--nhan-cong` để điền sẵn; S22 đối chiếu. Công trình trên tuyến cao tốc HN–HP: `dutoan.py tra --ly-trinh Km…` cho xã, tỉnh, vùng nhân công (Hải Phòng phân vùng theo QĐ 65/QĐ-SXD; Hà Nội mã chính theo QĐ 2036, kèm mã CV 14502 cho hồ sơ áp giá trước 26/10/2026). Hỏi người dùng công bố giá kỳ nào (số, ngày, Sở XD tỉnh/thành nào cho từng vùng), rồi điền từ file họ cung cấp; tài nguyên không có trong công bố → báo giá, ghi nguồn. Không tự điền giá, không dùng lại giá của hồ sơ khác khi chưa được xác nhận.
☐ Xác nhận bảng giá.

### Bước 5 — Tính và xuất Excel
`python scripts/dutoan.py tinh --data <dir> --khoi-luong khoi_luong.csv --config config_du_toan.json --out <file>.xlsx`
Từ chối tính khi còn mục chặn (dùng `--nhap` để xuất bản nháp có đánh dấu). Mẫu xuất: `references/mau-bieu-excel.md`. Sau khi xuất: tính lại công thức (LibreOffice) và so với số đối chiếu Python (`*_doi_chieu.json`) — phải khớp đến đồng.
☐ Người dùng xem bản nháp, góp ý.

### Bước 6 — Tự soát
`python scripts/dutoan.py soat --data <dir> --khoi-luong khoi_luong.csv --config config_du_toan.json` (S01–S22, `references/kiem-tra-tham-tra.md`). Báo các điểm cần xem lại, không tự sửa.

### Bước 7 — Thẩm tra hồ sơ có sẵn
1. `python scripts/soat_file_excel.py <file dự toán> <file khối lượng>`: ô lỗi, liên kết file ngoài, hàm tồn dư, số nhập tay, sheet ẩn, văn bản hết hiệu lực, thuế suất, ký hiệu.
2. `python scripts/nhap_du_toan_excel.py --file … --dgct … --dt … --ra …`: tính lại từng khối đơn giá theo PL III, chỉ ra công thức sai và chênh lệch; rồi `tinh` để có bảng so sánh tổng.
   Hồ sơ **dự toán khảo sát**: `python scripts/nhap_ks_excel.py --file … [--vung-nc HN-V1-KV1,HY-V2,…] --tinh-lai` — tự nhận sheet đơn giá chi tiết, bảng giá trị và tổng hợp; tính lại theo PL V TT 36; báo chênh lệch số, nhãn/ký hiệu, công thức, vùng giá, tỷ lệ, diễn giải, giá nhân công; ghi bộ dữ liệu để `tinh` tái lập (`references/du-toan-khao-sat.md` mục 5).
3. Đối chiếu khối lượng giữa file KL và bảng dự toán; checklist mục B trong `kiem-tra-tham-tra.md`; các lỗi thường gặp trong `mau-don-vi.md` mục 3.
Đầu ra: bảng chênh lệch (đề nghị – thẩm tra – lý do – căn cứ), lượng hoá ảnh hưởng tới tổng. Văn phong điềm đạm, nêu đúng vấn đề, không nghiêm trọng hoá.

## Công thức (chi tiết và nguồn: `references/phuong-phap-chi-phi-xay-dung.md`)

T = VL + NC×Knc + M×Km · GT = C + TT · TL = (T+GT)×tỷ lệ · GXDTT = T+GT+TL · GTGT = GXDTT×TGTGT · LT = GXDTT×tỷ lệ×(1+TGTGT)
TT 40 (bảo dưỡng/sửa chữa trong bảo trì): GT = NC × tỷ lệ (Bảng 2.2) · TL = (T+GT)×tỷ lệ · LT = G sau thuế × tỷ lệ (Bảng 2.4) · dự phòng ≤ 5%
Khảo sát (PL V TT 36): C = NC × 70/65/60% · TT = T × 6/4,5/3% · TL 6% · Cpvks = (T+GT+TL) × (2% + 3%) + Ck · LT = (G+GTGT) × 2% · Cdp ≤ 10% × (G+GTGT)
Mẫu đơn giá đầy đủ: đơn giá/đv KL = G / số đv định mức; thành tiền đoạn = KL đoạn × đơn giá vùng của đoạn.

## Tham chiếu

| File | Đọc khi |
|---|---|
| `references/can-cu-phap-ly.md` | Mọi lần lập hồ sơ thật; khi hỏi căn cứ |
| `references/tt38-quy-dinh-ap-dung.md` | Bước 3–5; mọi câu hỏi về hao hụt, hệ số sửa chữa, cấp phối bê tông |
| `references/mau-don-vi.md` | Người dùng có mẫu đơn vị; lập TDT; thẩm tra |
| `references/phuong-phap-chi-phi-xay-dung.md` | Bước 0, 5; cấu trúc chi phí và bảng tỷ lệ |
| `references/bao-tri-tt40.md` | Bảo dưỡng, sửa chữa trong kế hoạch bảo trì; chi phí quản lý của chủ sở hữu |
| `references/du-toan-khao-sat.md` | Dự toán khảo sát, thí nghiệm chuyên ngành; mẫu khảo sát của đơn vị; chi phí lập dự toán phương án sửa chữa |
| `references/do-boc-khoi-luong.md` | Bước 2 |
| `references/ap-ma-dinh-muc.md` | Bước 3 |
| `references/chuan-bi-du-lieu.md` | Bước 1; nạp dữ liệu; cấu hình |
| `references/mau-bieu-excel.md` | Bước 5 |
| `references/kiem-tra-tham-tra.md` | Bước 6, 7 |
| `references/hoc-thuc-hanh.md` | Học / thực hành: lộ trình 7 chặng, bài tập kiểm tra được bằng script, 10 bẫy thường gặp |

## Trình bày với người dùng

- Mỗi bước kết thúc bằng: bảng tóm tắt ngắn → các điểm cần quyết định (đánh số) → câu hỏi xác nhận.
- Số tiền: đồng, phân tách hàng nghìn bằng dấu chấm; khối lượng 2–3 chữ số thập phân.
- Văn phong hành chính, rõ ràng, không phóng đại. Khi không chắc, nói rõ và đề nghị kiểm tra lại.
