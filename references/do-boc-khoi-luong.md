# Đo bóc khối lượng

**Căn cứ:** PL III TT 36/2026 quy định khối lượng xác định từ thiết kế triển khai sau khi dự án được duyệt, **phù hợp đơn vị tính của giá xây dựng**, có thể lấy từ BIM, phần mềm, công cụ số kết hợp hồ sơ thiết kế. Hướng dẫn đo bóc chi tiết trước đây nằm ở TT 13/2021 (đã bị TT 37/2026 thay thế). **Chưa xác minh hướng dẫn đo bóc chi tiết hiện nằm ở phụ lục nào của TT 36 hay 37/2026 — tra lại khi cần trích căn cứ.** Các nguyên tắc dưới đây là thông lệ nghề, dùng làm quy trình làm việc, không thay cho văn bản.

## Nguyên tắc chung
1. Bóc theo **hạng mục → bộ phận kết cấu → công tác**, thứ tự thi công.
2. Mỗi dòng có: tên công tác mô tả đủ điều kiện (vật liệu, mác, chiều cao/chiều sâu, cấp đất đá, biện pháp), đơn vị, khối lượng, **diễn giải** (công thức kích thước × số lượng), **nguồn bản vẽ** (số hiệu bản vẽ, trang).
3. Đơn vị bóc trùng đơn vị định mức (m³, m², 100m³, tấn, 100m…). Nếu định mức tính theo 100 m³ mà bóc theo m³, ghi rõ hệ số quy đổi; script tự quy đổi khi khai báo cột `quy_doi`.
4. Không tính trùng: phần giao nhau giữa cấu kiện (dầm–cột, sàn–dầm) chỉ tính một lần theo quy ước đã chọn và ghi rõ quy ước.
5. Khối lượng lấy theo kích thước thiết kế; hao hụt đã có trong định mức vật liệu — **không cộng hao hụt vào khối lượng**.
6. Khối lượng cốt thép bóc theo đường kính nhóm định mức (≤10, ≤18, >18 mm…) và vị trí cấu kiện, chiều cao.
7. Công tác chưa đủ cơ sở đo bóc: ghi `[THIẾU DỮ LIỆU]` và nêu hướng xử lý (tạm tính, chờ thiết kế bổ sung) — không tự đặt số.

## Đặc thù công trình giao thông
- Nền đường: đào/đắp theo mặt cắt ngang, phương pháp trung bình mặt cắt hoặc mô hình; tách theo cấp đất, độ chặt yêu cầu (K95, K98…), đào vét hữu cơ, đất không thích hợp; vận chuyển theo cự ly và loại đường.
- Mặt đường: theo kết cấu áo đường từng lớp (diện tích × chiều dày), tưới thấm/dính bám theo m²; phân biệt rải thảm cơ giới/thủ công.
- Cầu, cống: theo bộ phận (cọc, bệ, thân, xà mũ, dầm, bản mặt, lan can, khe co giãn, gối).
- ATGT, ITS, cáp quang: cột, biển, vạch sơn (m²), hộ lan (m), ống/rãnh cáp (m), cáp (m — gồm dự phòng theo thiết kế, ghi rõ), thiết bị (cái/bộ) — thiết bị là **chi phí thiết bị**, lắp đặt là chi phí xây dựng.

## Bóc từ DXF (`scripts/boc_kl_dxf.py`)
- `layers`: liệt kê layer và số đối tượng → người dùng chỉ định layer nào là gì.
- `do`: theo từng layer: tổng chiều dài LINE/LWPOLYLINE/ARC, diện tích polyline kín và HATCH, đếm block theo tên. Đơn vị theo bản vẽ (khai báo `--ty-le` để đổi sang m).
- Kết quả chỉ là số đo hình học; người dùng phải xác nhận ý nghĩa và hệ số (chiều dày, chiều cao) trước khi đưa vào `khoi_luong.csv`.

## Bóc từ PDF
Đọc bảng thống kê khối lượng trong bản vẽ (nếu có) và đối chiếu lại bằng kích thước. Bản vẽ scan: nêu rõ độ tin cậy của số đọc được, khoanh các chỗ chữ mờ.
