# Áp mã định mức

**Căn cứ chính: Thông tư 38/2026/TT-BXD** — mọi mức hao phí vật liệu, nhân công, máy lấy theo TT 38 trước. Chỉ dùng định mức chuyên ngành hoặc định mức tự lập khi TT 38 không có công tác tương ứng, và phải ghi rõ lý do trong `nguon` / thuyết minh.

| Công việc | Phụ lục TT 38/2026 |
|---|---|
| Xây dựng mới (đào đắp, bê tông, cốt thép, mặt đường…) | II – Định mức dự toán xây dựng công trình |
| Lắp đặt hệ thống kỹ thuật (điện, cấp thoát nước, ống…) | III |
| Lắp đặt máy, thiết bị công nghệ | IV |
| Thí nghiệm chuyên ngành | V |
| **Sửa chữa, bảo dưỡng công trình** (hồ sơ sửa chữa định kỳ, phá dỡ, hoàn trả) | **VI** |
| Mức sử dụng vật liệu (cấp phối bê tông, vữa…; dùng để quy đổi hao phí vật liệu thành phần) | VII |
| Chi phí QLDA, tư vấn | VIII |
| Khảo sát | I |

Lưu ý về vật liệu (đã đối chiếu văn bản TT 38 — chi tiết `references/tt38-quy-dinh-ap-dung.md`):
- Hao phí vật liệu trong định mức PL II, PL III **đã gồm hao hụt thi công** (cát gồm cả độ dôi) → không nhân thêm hệ số hao hụt. Ngoại lệ: ống bê tông, cống hộp, ống gang (PL III) cộng 0,5%; cốt thép chưa gồm thép nối chồng, thép chờ…
- **Hồ sơ sửa chữa:** công tác chưa có trong PL VI thì dùng PL II/III và **nhân VL 1,02; NC 1,15; M 1,05** (PL VI mục 3.b). Mã PL VI không nhân. Khai `loai_ho_so: "sua_chua"` để script tự áp và soát.
- Bê tông: định mức ghi "Vữa bê tông" m³ (đã gồm hao hụt vữa); chọn mác bằng cột `cap_phoi` (cấp phối PL VII, chưa gồm hao hụt) hoặc nhập giá bê tông thương phẩm. Dùng vữa thương phẩm mà đổ thủ công: NC × 0,6, bỏ máy trộn.
- Vật liệu không có trong định mức (cáp, ống, thiết bị tính theo thiết kế): cộng hao hụt theo PL VII Phần 2 (vd. cáp các loại 1%) — ghi căn cứ.

Chi tiết khác: Định mức dự toán xây dựng công trình: Phụ lục II TT 38/2026/TT-BXD (thay TT 12/2021 và các TT sửa đổi); lắp đặt hệ thống kỹ thuật: Phụ lục III; khảo sát: Phụ lục I; các phụ lục khác theo danh mục của TT 38. Định mức chuyên ngành (viễn thông, điện, bảo dưỡng đường bộ…) chỉ dùng khi TT 38 không có công tác tương ứng; kiểm tra hiệu lực riêng và ghi lý do (script cảnh báo S15 khi nguồn định mức không phải TT 38). **Lưu ý CV 9947/BXD-VPB thay thế phụ lục TT 38 — dùng bộ dữ liệu theo phụ lục sau thay thế.**

## Cấu trúc mã hiệu
Mã gồm phần chữ (chương/nhóm) và phần số (công tác, quy cách), ví dụ `AB.25102` = tiền tố bảng `AB.2510` + hậu tố cột `2` (cấp đất II). Khoảng 8.960 mã PL I–VI đã trích vào `data/tt38/` — tra bằng `dutoan.py tra`. Một số mã đã đổi so với TT 12/2021 (vd. bê tông móng AF.1121x → AF.11210/AF.11220 với vật liệu 'Vữa bê tông'; bê tông nền sửa chữa SB.4114x → SB.41140). Danh mục chương thực tế lấy từ dữ liệu: `python scripts/dutoan.py tra --data <dir> --chuong` liệt kê các tiền tố có trong bộ định mức đã nạp. Không đoán tên chương từ trí nhớ.

## Quy trình chọn mã
1. Đọc **thành phần công việc** và **điều kiện áp dụng** của mã (trong thuyết minh chương), không chỉ tên công tác.
2. So khớp: vật liệu, quy cách (mác bê tông, đường kính thép, chiều dày), biện pháp (thủ công/cơ giới, bơm/thủ công), chiều cao/chiều sâu, cấp đất đá, cự ly.
3. Đề xuất mã chính và mã thay thế, nêu tiêu chí phân biệt.
4. Đơn vị: khớp đơn vị định mức; ghi `quy_doi` khi khác (ví dụ KL theo m³, định mức theo 100 m³ → quy_doi = 0,01).
5. Hệ số điều chỉnh (vd. điều kiện thi công khó, chiều cao lớn hơn khung định mức): chỉ áp khi thuyết minh định mức quy định; ghi căn cứ vào `can_cu_he_so`.
6. Công tác không có trong định mức hoặc khác biệt đáng kể: đánh dấu `[CẦN ĐỊNH MỨC MỚI/ĐIỀU CHỈNH]` — xác định theo phương pháp TT 37/2026, không tự chế hao phí.

## Lỗi thường gặp
- Chọn mã theo tên gần đúng, sai biện pháp thi công so với thuyết minh biện pháp.
- Trùng hao phí: vừa tính công tác ván khuôn riêng vừa dùng mã đã gồm ván khuôn; vừa tính vận chuyển riêng vừa dùng mã đã gồm vận chuyển trong phạm vi.
- Sai nhóm đường kính cốt thép, sai chiều cao.
- Dùng mã định mức đã bị sửa đổi/thay thế (TT 12/2021, 09/2024, 08/2025 — hết hiệu lực từ 01/7/2026).
- Dùng định mức chuyên ngành trong khi TT 38 đã có công tác tương ứng.
- Nhân thêm hệ số hao hụt vật liệu không có căn cứ.
- Công tác lắp đặt thiết bị áp vào định mức xây dựng thay vì định mức lắp đặt.
