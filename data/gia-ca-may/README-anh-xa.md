# Danh mục máy PL IV TT 37 và ánh xạ tên máy TT 38

**`danh_muc_may_pl4_tt37.csv`** — 787 máy Mục V Phụ lục IV TT 37/2026 (trích từ docx người dùng cung cấp 18/11/2026): mã, tên đầy đủ (tên nhóm + thông số), số ca năm, định mức khấu hao/sửa chữa/chi phí khác (%), tiêu hao nhiên liệu, nhân công vận hành, nguyên giá tham khảo (1.000 đ). 8 thiết bị không ghi nguyên giá trong văn bản. Đính chính: tài liệu cũ ghi "khoảng 908 máy" — văn bản có 787 máy. QĐ 2075 Hà Nội công bố 778/787 (9 máy PL IV không công bố).

**`anh_xa_may_tt38.csv`** — 886 tên máy khác nhau trong định mức TT 38 (14.440 dòng hao phí) → mã PL IV. Định mức TT 38 chỉ ghi tên rút gọn ("Cần cẩu 25 t", "Máy nén khí 600 m3/h"), không ghi mã, nên một tên có thể ứng với nhiều máy (cần cẩu bánh hơi hay bánh xích; máy nén khí động cơ xăng hay diesel) — giá chênh đáng kể (vd. HN-V1: cần cẩu bánh hơi 25 t 2.961.100 đ/ca, bánh xích 25 t 3.638.400 đ/ca).

| trang_thai | Số tên | Cách lập | Dùng |
|---|---|---|---|
| khop_doi_chieu | 261 | Khớp tự động (loại máy + thông số có đơn vị) và trùng mã CSDL GXD gán cho cùng mã định mức | `ma_may` điền sẵn |
| khop_tu_dong | 425 | Khớp tự động một ứng viên rõ, GXD không có đối chứng | `ma_may` điền sẵn — kiểm tra khi dùng |
| can_xac_nhan | 187 | Nhiều ứng viên gần nhau, hoặc khớp tự động lệch với GXD | `ma_may` để trống; cột `de_xuat_tu_dong`, `ma_theo_gxd`, `ung_vien_khac` để người lập chọn |
| khong_khop | 13 | Không tìm được máy phù hợp (tên dạng "TS06 hoặc loại tương tự", ghép nhầm hai máy…) | Điền tay |

686 tên có mã, phủ 11.503/14.440 dòng hao phí. Đối chứng GXD: ghép theo mã định mức có cùng số máy (341 tên); khớp tự động "chắc" trùng GXD 244/261 trường hợp có đối chứng (17 lệch → chuyển sang can_xac_nhan). Mã GXD chỉ ghi ở dòng can_xac_nhan để tham khảo — không thay thế quyết định của người lập. **Lưu ý:** đối chứng ghép máy theo thứ tự trong cùng mã định mức, nên khi thứ tự máy của GXD khác TT 38 thì mã GXD có thể sai hẳn (vd. "Máy đào 1,25 m3" ra M101.0504 là máy ủi 140 cv) — luôn đọc tên ở cột `ten_theo_gxd` trước khi chọn.

**Xác nhận — theo từng hồ sơ, do người lập dự toán thực hiện** (người dùng quyết định 18/11/2026: bảng chung giữ nguyên trạng thái `can_xac_nhan`, không chốt hàng loạt). Lý do: cùng một tên trong TT 38 ("Cần cẩu 25 t") có thể là máy khác nhau tùy biện pháp thi công của công trình.

Tạo tệp `anh_xa_may.csv` trong thư mục hồ sơ:

```
ten_tn,ma_may,can_cu
Cần cẩu 25 t,M102.0304,Biện pháp thi công bản vẽ BPTC-03: cẩu lắp dầm trên nền yếu dùng cần cẩu bánh xích
```

- Tệp hồ sơ ưu tiên hơn bảng chung (kể cả với tên đã khớp tự động); `can-gia --ca-may` điền giá theo mã đã xác nhận, nguồn ghi kèm căn cứ.
- Soát **S24**: mã không có trong PL IV → chặn; thiếu căn cứ → cảnh báo; máy hồ sơ dùng chưa có mã và chưa có giá → cảnh báo, kèm mã đề xuất và mã GXD để chọn.
- Không sửa `anh_xa_may_tt38.csv` cho một hồ sơ riêng.
