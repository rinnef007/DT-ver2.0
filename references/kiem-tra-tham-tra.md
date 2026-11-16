# Kiểm tra, thẩm tra dự toán

Dùng cho bước 6 (tự soát) và bước 7 (thẩm tra hồ sơ do tư vấn lập). Mục tiêu là xác định đúng chênh lệch và căn cứ, trình bày điềm đạm để các bên dễ thống nhất.

## A. Kiểm tra tự động (`dutoan.py soat`)
| Mã | Nội dung | Mức |
|---|---|---|
| S01 | Dòng khối lượng chưa `xac_nhan` | Chặn |
| S02 | Tài nguyên thiếu giá / giá = 0 | Chặn |
| S03 | Mã hiệu không có trong bộ định mức đã nạp | Chặn |
| S04 | Đơn vị KL khác đơn vị định mức mà quy_doi = 1 | Cảnh báo |
| S05 | Hệ số ≠ 1 không ghi căn cứ | Cảnh báo |
| S06 | Thiếu diễn giải hoặc nguồn bản vẽ | Cảnh báo |
| S07 | Giá thiếu nguồn/ngày áp dụng, hoặc ngày áp dụng cách thời điểm lập > 6 tháng | Cảnh báo |
| S08 | Công tác trùng (cùng mã, cùng hạng mục, cùng diễn giải) | Cảnh báo |
| S09 | Tỷ lệ C/TT/TL/LT lệch so với bảng PL III theo loại công trình và nấc giá trị khai báo | Cảnh báo |
| S10 | Dòng trọn gói (TG) — nhắc áp tỷ lệ 50% theo Bảng 3.9 nếu thuộc trường hợp đó | Thông tin |
| S11 | Đoạn trong khối lượng chưa khai báo trong config | Chặn |
| S12 | Mã tạm tính (TT…) — cần thuyết minh cách lập hao phí | Cảnh báo |
| S13 | Mục trong bảng tổng hợp thiếu căn cứ, hoặc có hệ số chưa ghi căn cứ | Cảnh báo |
| S05 | (mở rộng) Hệ số theo dòng hao phí trong `dinh_muc.csv` chưa có căn cứ | Cảnh báo |
| S14 | Hệ số theo PL VI mục 3.b: hồ sơ xây mới nhân VL > 1; hồ sơ sửa chữa nhân hệ số cho mã PL VI, hoặc mã PL II/III chưa nhân 1,02/1,15/1,05 | Cảnh báo / Thông tin |
| S15 | Mã không có trong TT 38/2026 (chuyên ngành, tự lập, văn bản cũ) — nêu lý do | Cảnh báo |
| S16 | Mã cấp phối không có, hoặc định mức không có dòng 'Vữa…' để thay | Chặn |
| S17 | Hao phí trong dữ liệu hồ sơ khác hao phí TT 38/2026 cùng mã | Cảnh báo |
| S18 | Mã TT 38 nằm trong danh sách nghi lệch dòng khi trích (ma_can_kiem_tra) — đối chiếu văn bản | Cảnh báo |
| S19 | (Sau khi tính) Chế độ TT 40: tỷ lệ gián tiếp / nhà tạm không đúng nấc theo NC và chi phí thực hiện trước thuế thực tế | Cảnh báo |
| S19 | (Sau khi tính) Chế độ khảo sát: tỷ lệ Bảng 5.1–5.3 không đúng nấc theo NC, T, T+GT+TL thực tế | Cảnh báo |
| S20 | Chế độ TT 40: nhắc điều kiện áp dụng (thuộc kế hoạch bảo trì, nguồn vốn, pháp luật chuyên ngành — Điều 7); chế độ khảo sát: khoản không tính Cpa/Cbc | Thông tin |
| S22 | Giá nhân công trong bảng giá khác văn bản chuyển đổi của Sở XD (`data/nhan-cong/`) cho vùng nhân công khai trong config | Cảnh báo |
| S21 | Mẫu Bảng 3.8/5.4 nhưng khối lượng dùng nhiều vùng giá (chặn — dùng mẫu đoạn/vùng); tỷ lệ riêng theo mã không áp dụng ở mẫu này | Chặn / Cảnh báo |

## A2. Soát file Excel có sẵn (`scripts/soat_file_excel.py`)
E1 ô lỗi · E2 liên kết file ngoài · E3 hàm tồn dư Google Sheets · E4 số lưu dạng chữ · E5 số nhập tay giữa công thức · E6 sheet ẩn có lỗi/tồn dư · E7 văn bản hết hiệu lực từ 01/7/2026 · E8 thuế suất GTGT không thống nhất · E9 ký hiệu LT cho chi phí không xác định được KL. Với hồ sơ có đơn giá chi tiết, chạy thêm `nhap_du_toan_excel.py` để tính lại từng khối và phát hiện công thức sai (TL, phạm vi % vật liệu khác); hồ sơ dự toán khảo sát dùng `nhap_ks_excel.py` (`references/du-toan-khao-sat.md` mục 5).

## B. Checklist thẩm tra thủ công
1. **Hệ văn bản áp dụng**: hồ sơ lập theo NĐ 206 + TT 36/37/38/2026 hay thuộc diện chuyển tiếp theo NĐ 10/2021? Không trộn. Hồ sơ đã duyệt / đã nộp thẩm định trước 01/7/2026: áp **Điều 36 NĐ 206** (6 khoản — xem `references/can-cu-phap-ly.md` mục 2; đặc biệt k3 TMĐT tiếp tục thẩm định theo NĐ 206, k5 dự toán dừng thẩm định, trả lại hồ sơ để CĐT tự tổ chức thẩm định/phê duyệt) để xác định có thẩm định lại hay không.
2. **Khối lượng**: đối chiếu bản vẽ; kiểm tra trùng/thiếu; quy ước giao cấu kiện; cấp đất, cự ly vận chuyển, độ chặt.
3. **Mã định mức**: theo TT 38/2026 (đúng phụ lục: XD mới PL II, sửa chữa PL VI, lắp đặt PL III/IV); mức hao phí vật liệu đúng TT 38, không nhân thêm hao hụt không căn cứ; đúng biện pháp thi công đã duyệt; đúng quy cách; không trùng hao phí; hệ số có căn cứ.
4. **Giá vật liệu**: theo công bố giá của địa bàn tại thời điểm lập; vật liệu không có trong công bố có đủ báo giá; cước vận chuyển đến hiện trường hợp lý.
5. **Giá nhân công, ca máy**: theo công bố của Sở XD; nhóm, bậc thợ; phương pháp TT 37/2026 hoặc bảng chuyển đổi.
6. **Tỷ lệ**: loại công trình, nấc giá trị (theo chi phí XD trước thuế của từng công trình trong TMĐT duyệt), hệ số vùng 1,1, nhà tạm theo tuyến/không theo tuyến.
7. **Thuế GTGT**: thuế suất áp dụng tại thời điểm lập — kiểm tra quy định thuế hiện hành (có thời kỳ giảm thuế).
8. **Thiết bị vs. xây dựng**: thiết bị không nằm trong chi phí xây dựng; lắp đặt dùng định mức lắp đặt.
9. **Số học**: cộng dồn, làm tròn, đơn vị (đồng / nghìn đồng).
10. **Ranh giới kiểm toán hồ sơ (bước 8):** skill tính dự toán / TMĐT / giá gói thầu; quyết toán hợp đồng và quyết toán vốn đầu tư **không** thuộc phạm vi NĐ 206 (Điều 1 k2) mà thuộc NĐ 193/2026 (Điều 4, 5, 29 — k2 Điều 29 chưa đọc được nguyên văn đầy đủ, không trích câu hoàn chỉnh) + mẫu biểu TT 73/2026/TT-BTC (bãi bỏ TT 27/2025). Khi thẩm tra hồ sơ quyết toán, chỉ kiểm tra ranh giới và mẫu biểu, không áp công thức dự toán vào quyết toán.

## C. Mẫu bảng kết quả thẩm tra
| STT | Nội dung | Giá trị đề nghị | Giá trị thẩm tra | Chênh lệch | Lý do | Căn cứ |
|---|---|---|---|---|---|---|

Lý do viết ngắn, khách quan: "Áp mã AF.xxxxx (bê tông bơm) thay cho AF.yyyyy (thủ công) theo biện pháp thi công tại bản vẽ BPTC-03". Tránh nhận xét chủ quan về đơn vị lập.
