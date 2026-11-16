# Template Word (W1/W2/W3)

Ba mẫu văn bản kèm theo hồ sơ dự toán, dùng khi trình/thẩm tra/nghiệm thu. Nội dung trong
`[...]` là chỗ điền — thay bằng số liệu thật của hồ sơ rồi xóa dấu ngoặc.

| File | Mẫu | Dùng cho |
|---|---|---|
| `W1-thuyet-minh-bao-cao-tham-tra.docx` | W1 | Thuyết minh dự toán / Báo cáo thẩm tra dự toán: bìa, căn cứ pháp lý, tóm tắt dự toán (dán số từ sheet `TH_CPXD` của file Excel do skill xuất), kết quả thẩm tra, kết luận, chữ ký |
| `W2-bien-ban-nghiem-thu.docx` | W2 | Biên bản nghiệm thu / biên bản hiện trường: thành phần, nội dung, kết luận, chữ ký các bên, chỗ chèn ảnh hiện trường |
| `W3-to-trinh-quyet-dinh-cong-van.docx` | W3 | Khung chung Tờ trình / Quyết định / Công văn: quốc hiệu, số/ký hiệu, trích yếu, nội dung, nơi nhận, chữ ký — chọn một loại, xóa hai loại còn lại |

## Cách dùng

1. Copy file mẫu ra thư mục hồ sơ, đổi tên theo dự án.
2. Điền các chỗ `[...]`; bảng tổng hợp ở W1 dán số từ file Excel do `dutoan.py tinh` xuất
   (sheet `TH_CPXD`).
3. W1 có mục lục tự động: mở bằng Word, nhấn chuột phải vào mục lục → **Update Field** →
   **Update entire table** (file đã bật cập nhật field khi mở).
4. Danh sách đánh số dùng Style `GXD Danh list số`; nội dung bảng dùng Style
   `Gxd.vn Noi dung Ban can Giua Dam B`; ảnh chèn vào đoạn áp Style `Style Hình ảnh`.

## Định dạng

Theo Nghị định 30/2020/NĐ-CP: khổ A4, font Times New Roman cỡ 13, giãn dòng 1,5;
lề trên/dưới 2 cm, trái 3 cm, phải 2 cm. Tiêu đề bảng lặp lại sang trang mới; footer đánh số
trang ("Trang N").

Hệ Style định nghĩa lại tương đương hệ Style GXD (xem `references/doi-chieu-gxd.md` mục 13):
`A Noi dung gxd.vn` (nội dung thường), `Heading 1`–`Heading 4` (đề mục, làm mục lục tự động),
`Gxd.vn Noi dung Ban can Giua Dam B` (nội dung bảng, căn giữa, đậm), `Style Hình ảnh`,
`GXD Danh list số`, các Style `Tieu de Quoc hieu` / `Tieu de Co quan` / `Noi nhan` (tiêu đề,
nơi nhận, chữ ký).

**Không copy file `Normal.dotm` của Công ty CP Giá Xây Dựng** — mọi Style đều được định nghĩa
mới bằng `python-docx`.

## Tạo lại file

File `.docx` được tạo bằng script (không sửa trực tiếp rồi mong giữ được khi tạo lại):

```bash
python scripts/tao_mau_word.py --ra templates/word
```

Sửa nội dung/kiểu trình bày thì sửa `scripts/tao_mau_word.py` rồi chạy lại. Cần `python-docx`
(đã kiểm chứng với 1.1.0).
