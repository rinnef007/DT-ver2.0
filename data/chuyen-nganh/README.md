# Định mức chuyên ngành: CNTT và viễn thông

Trích ngày 17/11/2026 từ file đính kèm nhúng trong văn bản người dùng cung cấp (QĐ 1601, QĐ 1595, CV 258 chỉ chứa quyết định; bảng định mức nằm trong file .doc/.zip nhúng). Cùng cấu trúc cột với `data/tt38/dinh_muc_tt38_p*.csv`; `phu_luc` ghi mã bộ (`CNTT-1601`, `CNTT-1595`, `VT-258`).

| File | Văn bản | Số mã / dòng | Ghi chú |
|---|---|---|---|
| `cntt/dinh_muc_cntt_1601.csv` | QĐ 1601/QĐ-BTTTT ngày 03/10/2011 (lắp đặt phần cứng, cài đặt phần mềm), đã áp QĐ 1235/QĐ-BTTTT ngày 04/9/2014 | 319 / 1.597 | 10 chương: thiết bị mạng, cáp mạng, máy chủ, lưu trữ, CDN, VoIP, hội nghị truyền hình, an ninh mạng, phần mềm quản trị, phần mềm máy trạm |
| `cntt/dinh_muc_cntt_1595.csv` | QĐ 1595/QĐ-BTTTT ngày 03/10/2011 (tạo lập cơ sở dữ liệu) | 61 / 301 | Mức độ phức tạp 1–3; nhân công theo "nhóm công" ở nhiều mã |
| `vien-thong/dinh_muc_vt_258.csv` | CV 258/BTTTT-KHTC ngày 09/02/2009 (định mức XDCB công trình bưu chính, viễn thông) | 2.133 / 12.419 | 634/634 mã đề mục có dữ liệu |

**Quy ước mã cột** (người dùng đồng ý 17/11/2026): bảng nhiều cột của CV 258 điền số cột vào 2 chữ số cuối theo hệ mã của văn bản (`10.010100.00`, cột 4 → `10.010100.04`); bảng nhiều cột CNTT thêm `_n` (`01.01.01.01_2`) vì văn bản đã có mã dạng `01.07.01.01.1`. Bảng một cột giữ nguyên mã.

**Kèm theo:** `*/ghi_chu_*.csv` — ghi chú, hệ số, bảng hệ số (độ cao, dung lượng, cự ly…) và cách chọn mức độ phức tạp theo mã; `ma_can_kiem_tra_chuyen_nganh.csv` — 138 mục cần đối chiếu (công thức, mã sai trong văn bản, nhóm công, ô đơn vị trống); `anh_xa_nhan_cong.csv` — 16 quy tắc chọn nhóm nhân công (người dùng yêu cầu chọn, 17/11/2026), áp khi nạp; `nhat_ky_trich.md` — nhật ký trích và áp QĐ 1235.

**Nhân công — chọn nhóm (TT 37 Điều 2 k3: căn cứ tính chất công tác chọn nhóm theo Bảng 3.1 PL III; hao phí giữ nguyên, không quy đổi cấp bậc):**

| Bộ / phạm vi | Công nhân, thợ | Kỹ sư |
|---|---|---|
| CNTT-1601 (lắp đặt, cài đặt thiết bị CNTT) | Nhóm 4 — "lắp đặt… thiết bị công nghệ, thông tin". Chương 2 (cáp mạng) cũng nhóm 4; có thể bị xem là nhóm 3 khi đi cáp trong công trình | "Kỹ sư" (III.1 — gần nhất) |
| CNTT-1595 (tạo lập CSDL) | — | "Kỹ sư"; "nhóm công" × số người trong nhóm (vd. Nhóm 03 KS3 và 02 KS4: × 5); dòng đơn vị "công" ghi nhiều người giữ × 1 và S23 cảnh báo |
| VT-258 Phần I, II, Chương 31 | Nhóm 1 (mặt bằng, bốc dỡ, vận chuyển, đào đắp) | — |
| VT-258 Chương 32, 33 | Nhóm 2 (bê tông, xây, cốt thép) | — |
| VT-258 Chương 34 | Nhóm 3 (lắp dựng cột, kết cấu thép) | — |
| VT-258 Chương 35 | Nhóm 4 (lắp đặt cáp thông tin; có thể bị xem là nhóm 3) | — |
| VT-258 Chương 36 | Nhóm 3 (tiếp đất, chống sét) | "Kỹ sư" |
| VT-258 Phần IV (41–43) | Nhóm 4 (lắp đặt, cài đặt, đo thử thiết bị thông tin) | "Kỹ sư" (43 đo thử ≈ thí nghiệm) |
| Thợ lặn (Chương 35) | "Thợ lặn" (III.2) | — |

Nhiều cấp bậc trong một mã cùng về một nhóm thì cộng hao phí; tên gốc giữ ở trường `ten_goc`. Bảng 3.1 không có nhóm cho kỹ sư lắp đặt, cấu hình CNTT hay nhập liệu: dự án CNTT theo NĐ 224/2026 có thể định giá kỹ sư theo TT 07/2026/TT-BNV (phương pháp chuyên gia) hoặc báo giá — ghi căn cứ. Tắt việc đổi tên (giữ tên cấp bậc): điền giá theo tên gốc trong `gia_tai_nguyen.csv` và đặt `anh_xa_nc = False` trong mã gọi.

**Cách dùng:** skill nạp các bộ này sau định mức hồ sơ và TT 38 (mã đã có ở hồ sơ hoặc TT 38 thì không ghi đè). Soát S23 nhắc nguồn, căn cứ, mã cần kiểm tra và ghi chú áp dụng. Giá nhân công: định mức ghi "Công nhân 4/7", "Kỹ sư 2/8"… — điền giá cho đúng tên đó trong `gia_tai_nguyen.csv` theo nhóm đã chọn, ghi căn cứ.

**Tạo lại:** `scripts/nhap_dinh_muc_chuyen_nganh.py --file <docx> --bo cntt_1601|vt_258 --ra …` (QĐ 1595 dùng hàm `trich_1595`), rồi `scripts/ap_qd1235.py dm1601.csv QD1235.docx ra.csv nhat_ky.txt`. File .doc nhúng phải bóc ra và chuyển sang .docx (LibreOffice) trước.

**Đã đối chiếu tay:** 01.01.01.01_2 (Hub > 8 cổng: Kỹ sư 2/8 = 0,5 công), 10.010100.04 (chặt cây ĐK 50 cm: Công nhân 3,5/7 = 0,49; máy cưa 0,24 ca), 02.10.01.01.01_2 (Mức 2: 4,375 nhóm công). Chưa đối chiếu ngẫu nhiên toàn bộ — làm trước khi dùng cho hồ sơ thật.
