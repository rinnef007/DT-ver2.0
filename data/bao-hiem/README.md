# Phí và mức khấu trừ bảo hiểm bắt buộc công trình trong thời gian xây dựng (NĐ 220/2026/NĐ-CP)

Trích từ Phụ lục III NĐ 220/2026/NĐ-CP ngày 22/6/2026 (thay Phụ lục III NĐ 67/2023), hiệu lực 01/7/2026. Bản nguồn: docx người dùng cung cấp 17/11/2026.

| File | Nội dung |
|---|---|
| `phi_bh_cong_trinh_nd220_muc_I.csv` | Mục I khoản 1 — công trình < 1.000 tỷ đồng, không có lắp đặt thiết bị hoặc giá trị lắp đặt thiết bị < 50% hạng mục: 149 loại công trình, tỷ lệ phí (‰ giá trị công trình, **chưa GTGT**), loại mức khấu trừ M/N |
| `phi_bh_cong_trinh_nd220_muc_II.csv` | Mục II khoản 1 — công trình < 1.000 tỷ đồng, giá trị lắp đặt thiết bị ≥ 50% hạng mục: 195 dòng (‰ theo giá trị hạng mục / loại thiết bị) |
| `khau_tru_nd220.csv` | Mức khấu trừ M, N (triệu đồng) theo giá trị bảo hiểm; áp mức trong bảng hoặc 5% giá trị tổn thất, tùy số nào lớn hơn |

Cách dùng khi lập dự toán (chi phí bảo hiểm công trình thuộc chi phí khác):
- Trước hết xác định công trình có thuộc **đối tượng bắt buộc** theo Điều 32 mới (ảnh hưởng lớn đến an toàn, lợi ích cộng đồng; nguy cơ tác động xấu đến môi trường; quy mô lớn, kỹ thuật phức tạp — theo pháp luật về xây dựng, bảo vệ môi trường). Không tự suy ra: hỏi người dùng căn cứ phân loại.
- Số tiền bảo hiểm tối thiểu = giá trị đầy đủ công trình khi hoàn thành, không thấp hơn tổng giá trị hợp đồng XD kể cả điều chỉnh (Điều 33).
- Phí trong bảng là phí chuẩn: doanh nghiệp bảo hiểm được tăng/giảm tối đa 25% theo mức độ rủi ro; không được giảm với công trình ở vùng nguy cơ lũ quét, sạt lở, sụt lún (Điều 37 k2, k2a). Dự toán nên ghi rõ tỷ lệ dùng và căn cứ.
- Công trình ≥ 1.000 tỷ đồng hoặc loại chưa có trong bảng: phí do thỏa thuận theo xác nhận tái bảo hiểm (Điều 37 k1 điểm c, d) — không tra bảng.
- **Câu hỏi mở:** NĐ 220 không nói riêng về công tác **sửa chữa, bảo trì** công trình đang khai thác (vd. sửa mặt đường cao tốc) có thuộc "bảo hiểm công trình trong thời gian xây dựng" bắt buộc hay không — ghi căn cứ khi tính hoặc không tính.
- Dự án đầu tư công: hợp đồng bảo hiểm trong hoạt động XD áp dụng hình thức theo tỷ lệ phần trăm (NĐ 210/2026 Điều 11 k3 điểm g).

Trích bằng python-docx từ bảng Word, giữ nguyên chữ trong văn bản (dấu phẩy thập phân); các dòng tiêu đề nhóm ghi ở cột `nhom_cha`. Đã đối chiếu tay: 4.1.1 cao tốc 4,0‰ N; 4.4.1 hầm 11,0‰ N; ví dụ khấu trừ trong văn bản (công trình 15.000 triệu, loại M: 150/30; loại N: 200/40) khớp `khau_tru_nd220.csv`.
