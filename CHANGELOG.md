# Changelog — skill dự toán xây dựng Việt Nam (`du-toan-xay-dung-vn`)

## [1.0.0] — 2026-10-16 (baseline)
- Bản gốc từ `skill-DT-main.zip` (ngày file 16/10/2026), đẩy nguyên trạng lên `rinnef007/DT-ver2.0` làm baseline cho v2.0.
- Hệ văn bản từ 01/7/2026: NĐ 206/2026, TT 36/2026 (+ QĐ 1538), TT 37/2026, TT 38/2026, TT 40/2026.
- Quy trình 7 bước, 13 script Python, dữ liệu TT 38 (~9.050 mã), 5 bộ ví dụ chạy thử.
- Ngày rà soát pháp lý gần nhất: 16/10/2026.

> Lưu ý về dữ liệu TT 38: bản gốc v1 dùng 6 file `data/tt38/*.csv.gz` (gzip). Do công cụ
> snapshot của Muse chỉ đẩy file text UTF-8, từ 16/11/2026 dữ liệu TT 38 trên repo chuyển
> sang dạng CSV thường (giải nén từ đúng các file `.csv.gz` đó, nội dung không đổi).
> Script `dutoan_core.py` đọc được cả `.csv` và `.csv.gz`.

## [2.0.0] — 2026-11-16
- Dữ liệu TT 38 trên repo chuyển từ `.csv.gz` sang `.csv` thường (6 file, nội dung không đổi),
  để đẩy được bằng snapshot; script vẫn đọc được cả hai dạng.
- `dinh_muc_tt38.csv` (13 MB) chia thành 3 phần `dinh_muc_tt38_p1..p3.csv` (17.506 +
  17.506 + 17.504 dòng, gộp lại đúng bằng file gốc, đã kiểm chứng từng dòng) vì file gộp
  vượt giới hạn kích thước yêu cầu khi đẩy lên GitHub; `dutoan_core.py` đọc được cả file
  gộp, file `.csv.gz`, hoặc 3 phần.
- Sửa lỗi v1: `dutoan_core.py` chỉ nạp định mức TT 38 khi có file `dinh_muc_tt38.csv.gz`
  (kiểm tra sự tồn tại của `.csv.gz` rồi mới đọc `.csv`), nên với dữ liệu `.csv` thường
  thì `tinh`/`tra` không thấy mã TT 38. Nay kiểm tra cả `.csv` và `.csv.gz`.
- Sửa `dutoan.py tra --tai-nguyen`: trước đây mở trực tiếp file `.csv.gz` bằng gzip,
  nay dùng `doc_csv` nên đọc được cả `.csv` và `.csv.gz`.
- Rà soát lại pháp lý hệ 2026 (16/11/2026, `references/can-cu-phap-ly.md`): sửa NĐ 206/2026
  Điều 36 (k3 sửa đúng, bổ sung k5 — dự toán đã nộp thẩm định mà chưa có kết quả thì
  dừng thẩm định, trả lại hồ sơ); bổ sung Luật 135/2025 Điều 73–76, NĐ 193/2026, TT 73/2026/TT-BTC,
  NĐ 207/2026, NĐ 212/2026, NĐ 217/2026 (Điều 74 đã bãi bỏ bởi NĐ 347/2026), NĐ 347/2026,
  TT 32/33/34/39/2026, NĐ 339/2026; ghi rõ khoảng trống: Điều 36 không quy định gói thầu đã
  phát hành HSMT nhưng chưa ký hợp đồng. Mốc 01/01/2027: giá nhân công dùng bảng theo phương
  pháp mới khi Sở XD đã công bố (TT 37 Điều 2 k2); bảng chuyển đổi chỉ tạm thời đến hết 31/12/2026.
  QĐ 2036/2037/QĐ-SXD Hà Nội (26/10/2026) chưa nhập dữ liệu nhân công cho đến khi xác định phương pháp.
- Khép lỗ hổng dữ liệu TT 38 theo đề xuất Giai đoạn 2 (`phase2-mdb-de-xuat.csv`,
  2.994 dòng, đối chiếu với 4 bảng xuất GXD từ cơ sở dữ liệu TT 38 — xem
  `phase2-mdb-doi-chieu.md`): THEM 2.041 / SUA 585 / XOA 368, áp ngày 16/11/2026
  sau khi anh duyệt. Kết quả: `dinh_muc_tt38.csv` 52.517 → 54.190 dòng
  (8.959 → 9.136 mã trong `danh_muc_ma`); đối chiếu lại với GXD:
  MATCH 9.014, DIFF 58, SKILL_ONLY 11, GXD_ONLY 4 (trước: 8.059/836/64/181).
  14 khối mã thiếu đã bổ sung đủ (AB.5141x, AB.713xx, AB.721xx, AC.211xx,
  AC.251xx/252xx, AD.422xx, AF.333xx, AF.421xx, AG.524xx, MO.015xx, MS.051xx/052xx,
  DA.051xx); 53 mã ảo bị xóa (trong đó AF.51121/22 thực chất là AF.81121/22
  bị đọc nhầm 8 thành 5 — đã thêm lại đúng mã); 52 tên tài nguyên mới bổ sung
  vào `danh_muc_tai_nguyen_tt38.csv` (tổng 2.433 mục); `ma_can_kiem_tra.csv`
  83 → 6 mã (chỉ còn DA.50002/03, DB.10201, DB.17001/02, MS.07201 chưa kết luận).
  Còn tồn tại: 58 mã DIFF (chủ yếu do GXD thiếu dòng hoặc trùng dòng),
  4 mã GXD-only (AF.16120, AF.16210, AK.84211, AN.11311 — 2 mã sau GXD sai,
  skill đúng nên không áp theo GXD), 11 mã skill-only (gồm AF.160120, AF.160210
  và các mã có hậu tố @II). 3 mã GXD sai, giữ theo skill: BA.31002, AK.84211,
  AN.11311.
- Sửa quy ước dòng VLK/MK trong đề xuất: các dòng THEM của đề xuất ghi
  `ma_tn` = "Vật liệu khác"/"Máy khác", trong khi quy ước v1 để trống
  (dòng % tính theo tổng VL/M, không cần giá) — làm `soat` báo chặn S02 giả.
  Đã chuẩn hóa 328 dòng (190 VLK + 138 MK) về `ma_tn` trống, khớp quy ước v1;
  đối chiếu lại với GXD không đổi (MATCH 9.014).
- Ví dụ Nhà để xe (`data/vi-du-nha-de-xe/`): sửa dòng 8 AF.51122 → AF.81122
  (mã đúng TT 38; AF.51122 là mã ảo do đọc nhầm); thêm 3 giá tài nguyên VÍ DỤ
  cho các dòng mới của đề xuất (Vận thăng 0,8 t 500.000 đ/ca, Máy khoan bê tông
  300.000 đ/ca, Đinh, đinh vít 2.000 đ/cái); xóa dòng giá cho tên lỗi gộp
  "Nhân công nhóm 2 Máy thi công" (tên đã sửa đúng thành "Nhân công nhóm 2").
  GXD sau thuế: 280.339.863 → **287.562.073** (AF.11310 đủ NC/M, AK.12222 đủ
  NC, AF.12510 có VL); `soat` 0 chặn, 0 cảnh báo. Tổng mới đã đối chiếu tay
  4 dòng và tính lại bằng LibreOffice, khớp đến đồng.
- Thêm lớp học/thực hành (`references/hoc-thuc-hanh.md`: lộ trình 7 chặng, 10 bài tập kiểm tra được
  bằng script, 10 bẫy thường gặp) và ví dụ Nhà để xe chuyển mã TT 38 (`data/vi-du-nha-de-xe/`:
  41 dòng, 38/41 dòng có mã TT 38, GXD sau thuế 280.339.863 đồng đã kiểm chứng đến đồng).
- Đối chiếu mẫu GXD/Excel/Word (`references/doi-chieu-gxd.md`, 455 dòng): bảng map GXD → skill đầy đủ
  (Du toan XD 33 cột, Don gia XD 19 cột, Ts, DMTL, THCP); `soat_file_excel.py` thêm kiểm tra E10
  (SUM sai phạm vi so với nhãn), E11 (ô trống giữa công thức), E12 (nhãn mâu thuẫn công thức) và
  E6 liệt kê tọa độ mẫu; `nhap_du_toan_excel.py` thêm chế độ `--kieu gxd`; script mới
  `scripts/gia_ca_may.py` tính giá ca máy theo PL IV TT 37/2026 (3 máy mẫu kiểm chứng đến đồng);
  sheet chênh lệch vật tư `CL_VT` trong `xuat_excel.py` (chỉ xuất khi có `don_gia_goc`); 3 template
  Word tạo lại được bằng `scripts/tao_mau_word.py`; thiết kế đơn giá tổng hợp mã TH
  (`references/thiet-ke-don-gia-tong-hop.md`, chỉ tài liệu — mã TH ngoài phạm vi v2.0, làm ở v2.1).
- Thêm test tự động (`tests/`): kiểm thử soat/nhap trên fixture `DutoanGXD1.xlsm` (10 test) và
  kiểm thử 6 ví dụ khớp tổng baseline đến đồng (`tests/test_examples.py`).
- Sửa BA.31002 (kéo dây, cáp trên lưới đèn, PL III): Băng dính 1,63 → 1,00 cuộn; thêm
  dòng Nhân công nhóm 3 = 1,63 công (dữ liệu gốc bỏ mất dòng NC nên 1,63 bị dồn lên
  dòng Băng dính). Căn cứ: văn bản gốc TT 38/2026 PL III, TT 12/2021, và bảng xuất
  `tbDinhMuc` từ cơ sở dữ liệu GXD (6 dòng, trùng khớp). Xóa BA.31002 khỏi
  `ma_can_kiem_tra.csv`. Kiểm chứng sau sửa: `tra --ma BA.31002` ra đủ 7 dòng;
  6 ví dụ chạy lại khớp đúng đến đồng (vi-du 140.434.146; tt38 87.295.481; doan
  151.531.785; tt40 104.694.588; khao-sat 13.115.401; nha-de-xe 280.339.863 — số trước
  khi áp đề xuất Giai đoạn 2; sau GĐ2 là 287.562.073).

## [2.0.1] — 2026-11-17
- **Giá nhân công Hà Nội theo QĐ 2036/QĐ-SXD (26/10/2026, phương pháp mới):** thêm mã vùng
  `HN-V1`, `HN-V2` vào `data/nhan-cong/gia_nhan_cong_chuyen_doi_2026.csv` (10 loại nhân công × 2
  vùng, nhập từ bản docx người dùng cung cấp). Giữ nguyên bộ CV 14502 (`HN-V1-KV1/KV2/V2`) vì QĐ
  2036 không bãi bỏ CV 14502 và TT 37 Điều 2 k2 ghi mốc 01/01/2027 cho giá theo phương pháp mới
  — câu hỏi mở chọn văn bản ghi tại `references/can-cu-phap-ly.md` mục 1. Vùng I của QĐ 2036 =
  Vùng I KV1 ∪ KV2 của QĐ 3461 (đối chiếu 104/104 tên).
- **Phạm vi vùng Hải Phòng theo QĐ 65/QĐ-SXD (14/01/2026):** gán vùng cho 20 xã, phường Hải
  Phòng trên tuyến cao tốc HN–HP — 19 Vùng I, **xã Hà Đông (Km64+900 ÷ Km72+900) Vùng II**.
  `tra --ly-trinh` không còn trả "chưa xác định" cho đoạn Hải Phòng.
- CSV nhân công thêm cột `phuong_phap` (`chuyen_doi`/`moi`) và `ghi_chu_soat`; S22 in THÔNG TIN
  theo `ghi_chu_soat` khi hồ sơ dùng mã vùng Hà Nội (nhắc chọn CV 14502 / QĐ 2036 và ghi căn cứ).
  `xa_phuong_tuyen_hn_hp.csv` thêm `ma_vung_nhan_cong_khac`, `can_cu_vung_khac`; `tra --ly-trinh`
  in thêm "Phương án khác" cho đoạn Hà Nội.
- Tài liệu khớp dữ liệu sau Giai đoạn 2: 9.136 mã, 54.190 dòng, 2.433 tài nguyên, 6 mã cần kiểm
  tra; bỏ ghi chú "14 khối mã chưa có" (đã kiểm chứng đủ 14 khối trong `danh_muc_ma`); bảng dữ liệu
  README đổi `.csv.gz` → `.csv`. Commit 3 template Word W1/W2/W3 (tạo bằng `tao_mau_word.py`).
- Ngày rà soát pháp lý: 17/11/2026 (chỉ bổ sung QĐ 2036, QĐ 65; các văn bản khác giữ kết quả 16/11).
- Kiểm chứng: 6 ví dụ khớp baseline đến đồng (không ví dụ nào dùng mã vùng nhân công).

## [2.0.2] — 2026-11-17
- **Giá nhân công theo thời hạn hiệu lực.** `gia_nhan_cong_chuyen_doi_2026.csv` thêm `hieu_luc_tu`, `hieu_luc_den`;
  `can-gia --nhan-cong` và S22 chọn văn bản hiệu lực tại `thoi_diem_ap_gia` (yyyy-mm-dd; yyyy-mm lấy cuối tháng và
  cảnh báo nếu trong tháng có mốc đổi văn bản). S22 cảnh báo khi mã vùng của hồ sơ không còn văn bản hiệu lực (chỉ mã
  thay thế), nhắc khi văn bản đang dùng quá 12 tháng. Script mới `scripts/cap_nhat_nhan_cong.py` thêm văn bản công bố
  định kỳ (năm/quý) và đóng thời hạn văn bản cũ; test mới `tests/test_nhan_cong.py`.
- **Hà Nội: QĐ 2036/QĐ-SXD đang áp dụng từ 26/10/2026** (người dùng xác nhận 17/11/2026); CV 14502 hiệu lực
  01/7–25/10/2026. Tra lý trình đoạn Hà Nội trả `HN-V1` làm mã chính.
- **Sửa lỗi v2.0.1:** mã `HN-V2` có ở cả CV 14502 và QĐ 2036; `nhan_cong_tham_chieu()` gộp theo (mã vùng, tên) nên
  dòng nạp sau ghi đè dòng trước — Vùng II Hà Nội luôn ra giá QĐ 2036 bất kể văn bản người lập chọn. Nay phân biệt
  bằng thời hạn hiệu lực (test chồng lấn phát hiện lỗi này).
- **Đọc toàn văn TT 37/2026 Điều 1–4 và PL III.** Đính chính: Điều 2 k1 **không ghi ngày kết thúc** bảng chuyển đổi;
  câu "chỉ tạm thời đến hết 31/12/2026" là suy luận — đã sửa ở `SKILL.md`, `chuan-bi-du-lieu.md`,
  `tt38-quy-dinh-ap-dung.md`, `data/nhan-cong/README.md` (mục lịch sử CHANGELOG giữ nguyên).
- **NĐ 209/2026** (VLXD), **NĐ 210/2026** (hợp đồng XD), **NĐ 220/2026** (bảo hiểm bắt buộc) → [ĐÃ ĐỐI CHIẾU].
  NĐ 210 Điều 33 ghi vào mục 2 chuyển tiếp — chỉ lấp khoảng trống HSMT đã phát hành ở phần điều khoản hợp đồng.
- Dữ liệu mới `data/bao-hiem/`: tỷ lệ phí (‰) và loại khấu trừ PL III NĐ 220 (Mục I 149 dòng, Mục II 195 dòng),
  bảng mức khấu trừ M/N; câu hỏi mở về công tác sửa chữa, bảo trì. Chưa có lệnh tra (v2.1).
- Kiểm chứng: 6 ví dụ khớp baseline đến đồng; 3 test dữ liệu nhân công đạt.

## [2.1.0] — 2026-11-17
- **Định mức chuyên ngành CNTT và viễn thông** (`data/chuyen-nganh/`): QĐ 1601/QĐ-BTTTT đã áp QĐ 1235/QĐ-BTTTT
  (319 mã, 1.597 dòng), QĐ 1595/QĐ-BTTTT (61 mã, 301 dòng), CV 258/BTTTT-KHTC (2.133 mã, 12.419 dòng; 634/634 mã đề
  mục có dữ liệu). Bảng định mức lấy từ file nhúng trong văn bản. Kèm ghi chú áp dụng theo mã, 138 mục cần kiểm tra,
  bảng ánh xạ 64 tên nhân công theo cấp bậc (để trống nhóm), nhật ký trích. Quy ước mã cột: CV 258 điền 2 số cuối, CNTT
  thêm `_n`.
- `DuLieu` nạp các bộ chuyên ngành sau hồ sơ và TT 38 (không ghi đè). Soát mới **S23**: nguồn, căn cứ, mã cần kiểm
  tra, ghi chú áp dụng.
- Script `nhap_dinh_muc_chuyen_nganh.py`, `ap_qd1235.py` để tạo lại dữ liệu.
- Căn cứ pháp lý: NĐ 224/2026/NĐ-CP (Điều 49 k4 đ: định mức chuyên ngành là một phương pháp xác định chi phí CNTT;
  NĐ 45/2026 hết hiệu lực từ 01/7/2026, chuyển tiếp Điều 91), TT 39/2026/TT-BKHCN, QĐ 1601/1235/1595, CV 258,
  QĐ 23/2005/QĐ-BBCVT hết hiệu lực. Chế độ chi phí dự án CNTT theo TT 39 chưa làm (v2.2).

## [2.2.0] — 2026-11-17
- **Chọn nhóm nhân công cho định mức chuyên ngành** (người dùng yêu cầu): `data/chuyen-nganh/anh_xa_nhan_cong.csv` thành
  16 quy tắc theo bộ và chương (TT 37 Điều 2 k3, Bảng 3.1 PL III), áp khi nạp: tên cấp bậc → "Nhân công nhóm 1–4",
  "Kỹ sư", "Thợ lặn"; hao phí giữ nguyên, cộng dồn khi nhiều cấp bậc về một nhóm; "nhóm công" QĐ 1595 × số người.
  Toàn bộ tên nhân công (6 nhóm đích) đều có quy tắc; cột `can_xem_xet` ghi điểm có thể bị thẩm định khác (cáp mạng
  nhóm 3/4, cáp thông tin, kỹ sư CNTT). S23 cảnh báo dòng "nhóm" có đơn vị "công".
- VT-258: 6 dòng thiết bị đo bị xếp vào nhân công (bảng gốc thiếu dòng "+ Máy thi công") → loại M.
- **Chế độ chi phí dự án chuyển đổi số theo TT 39/2026/TT-BKHCN** — `scripts/cntt_tt39.py`, `references/cntt-tt39.md`,
  ví dụ `data/vi-du-cntt/`: G = GTB + GQLDA + GTV + GK + GDP; GLĐ, GCSDL bằng định mức (NĐ 224 Điều 49 k4 đ); khoản
  khác theo phương pháp Điều 49 k4–k6 kèm căn cứ; phương pháp chuyên gia (CQL Bảng 3.2, TN 6 %); Kdp tối đa
  10/7/5 %; soát phương pháp, căn cứ, số báo giá, thời hạn LCNT, Kdp; xuất Excel 4 sheet.
