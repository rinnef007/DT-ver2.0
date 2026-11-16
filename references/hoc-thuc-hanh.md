# Học / thực hành lập dự toán (skill-DT v2.0)

Tài liệu học đi kèm skill, viết lại từ 2 nguồn chính (xem mục 1). Người mới làm
theo lộ trình mục 2, mỗi chặng có bài tập kèm đáp án kiểm tra được bằng script
(mục 4). **Không cần đọc lại sách cũ** để làm theo skill — mọi quy tắc áp dụng
đều nằm trong `SKILL.md` và các file `references/` khác; tài liệu này chỉ dạy
*cách làm việc* và *cách tránh sai sót*.

## 1. Nguồn và giới hạn

| Nguồn | Dùng cho |
|---|---|
| Bài giảng Dự toán công trình (Cao đẳng, 2013; bản 2014 trùng nội dung — chỉ giữ 1 bản) — 4 chương: Khái niệm → Tiên lượng → Dự toán nhu cầu VL/NC/máy → Lập dự toán | Khung lộ trình học (mục 2) |
| Giáo trình Dự toán Xây dựng thực hành, KS. Trần Chiến Thắng, 03/2020 — 59 bài hỏi–đáp, 7 chương + Phụ lục lưu ý về đơn giá/định mức | Tình huống thực tế, bẫy thường gặp, bài tập (mục 4, 5) |

**Cảnh báo bắt buộc:** cả 2 nguồn đều thuộc **hệ văn bản cũ (trước 01/7/2026)** —
ĐM 1776/1777, TT 06/2016/TT-BXD, NĐ 32/2015/NĐ-CP, QĐ 957/QĐ-BXD, TT 04,
TT 18/2008/TT-BXD. Chỉ lấy **phương pháp, cách dạy, tình huống**; mọi mã hiệu,
đơn giá, tỷ lệ, thuế suất trong đó **không** được dùng làm quy tắc — xem bảng
đối chiếu ở mục 6. Chỗ nào sách cũ mâu thuẫn hệ 2026 thì ghi rõ, không đưa vào
như quy tắc. Không sao chép nguyên văn sách vào repo (bản quyền) — nội dung
dưới đây do Rin viết lại, có ghi nguồn từng bài.

## 2. Lộ trình học

Ánh xạ 4 chương bài giảng Cao đẳng + 7 chương giáo trình thực hành sang 7 bước
của skill (`SKILL.md` — Bước 0 cấu hình → Bước 7 thẩm tra).

| Chặng | Học gì (nguồn) | Tương ứng trong skill | Mục tiêu xong chặng |
|---|---|---|---|
| 1. Khái niệm | Bài giảng Ch.1; Giáo trình Bài 1–3: dự toán là gì, dự toán nhà nước khác dự toán thực tế thế nào, vì sao phải bóc tách chi tiết | `SKILL.md` Nguyên tắc bắt buộc; `references/can-cu-phap-ly.md` | Phân biệt được dự toán thực tế (KL × đơn giá thị trường) với dự toán theo hệ 2026 (định mức TT 38 + giá công bố kỳ hiện hành + tỷ lệ PL III TT 36) |
| 2. Tính khối lượng | Bài giảng Ch.2; Giáo trình Bài 4–9: bóc theo trình tự thi công, bóc ra giấy trước, kiểm tra KL bằng tương quan, lưu ý đơn vị/tách công tác/sai số | Bước 2; `references/do-boc-khoi-luong.md` | Bóc được 1 hạng mục nhỏ không sót, không trùng; diễn giải KL kiểm tra được |
| 3. Đơn giá thực tế | Giáo trình Bài 10–15: áp giá, tính giá thành (VL+NC+M+chuẩn bị+quản lý+lợi nhuận), chi phí chuẩn bị/quản lý tách bảng riêng | Bước 4; `references/chuan-bi-du-lieu.md` | Hiểu vì sao skill không chứa giá; biết lấy giá từ công bố của Sở XD và lập `can_gia.csv` |
| 4. Quản lý nhà nước về dự toán | Giáo trình Bài 16–22: định mức, đơn giá tỉnh, giá vật tư thực tế, điều chỉnh NC/máy, văn bản khác | Bước 0, 1, 3; `references/can-cu-phap-ly.md`, `references/tt38-quy-dinh-ap-dung.md` | Đọc được căn cứ pháp lý hệ 2026; biết TT 38 thay ĐM 1776 ở đâu |
| 5. Dự toán nhà nước (5 bảng) | Giáo trình Bài 23–32: bảng dự toán chi tiết → phân tích vật tư → tổng hợp vật tư → tổng hợp dự toán → tổng dự toán; vật liệu khác; công việc không có trong đơn giá | Bước 3, 5; `references/phuong-phap-chi-phi-xay-dung.md`, `references/mau-bieu-excel.md` | Hiểu dòng chảy VL/NC/M từ định mức → đơn giá chi tiết → tổng hợp (T → GT → TL → GXDTT → GTGT → GXD → LT); làm được bài tập 6 |
| 6. Dùng máy tính | Giáo trình Bài 33–48: làm dự toán trên Excel/phần mềm, link công thức, sửa định mức, kiểm tra tổng hợp vật tư | Bước 5, 6; `scripts/dutoan.py`, `scripts/soat_file_excel.py` | Chạy được `soat`/`tinh`; đọc được Excel xuất ra (công thức, không phải số chết); kiểm tra được tổng vật tư khớp giữa các bảng |
| 7. Dự toán dự thầu | Giáo trình Bài 49–60: mẫu 8A/8B/9A/9B/10, kiểm tra KL mời thầu, đơn giá gộp, điều chỉnh giá thầu, "câu thần chú" | Bước 7; `references/kiem-tra-tham-tra.md`, `references/mau-don-vi.md` | Biết vì sao không được đưa chênh lệch KL vào giá dự thầu; biết phân bổ biện pháp (ván khuôn, giàn giáo) vào đơn giá gộp |

Thứ tự học: đi hết chặng 1–5 rồi mới chạy script (chặng 6); chặng 7 chỉ học khi
làm hồ sơ thầu. Mỗi chặng xong thì làm bài tập tương ứng ở mục 4 rồi mới sang
chặng sau.

## 3. Phương pháp lập dự toán theo 7 bước của skill (tóm tắt)

1. **Bước 0 — Cấu hình:** ghi công trình, loại công trình, theo tuyến hay không,
   chi phí XD trước thuế trong TMĐT (để tra nấc tỷ lệ), vùng giá, thời điểm áp
   giá, thuế suất GTGT vào `config_du_toan.json`; chọn chế độ chi phí (`tt36`
   mặc định; `tt40_bao_duong`/`tt40_sua_chua` cho bảo trì; `tt36_khao_sat` cho
   khảo sát). ☐ Xác nhận cấu hình và tỷ lệ tra theo PL III TT 36/2026.
2. **Bước 1 — Dữ liệu nguồn:** `kiemtra-dulieu` để kiểm tra bộ định mức + giá;
   dữ liệu TT 38 đã trích sẵn trong `data/tt38/`. ☐ Xác nhận bộ dữ liệu.
3. **Bước 2 — Bóc khối lượng:** theo trình tự thi công (Giáo trình Bài 4);
   ghi vào `khoi_luong.csv`, mỗi dòng một (công tác, đoạn), có `dien_giai`,
   `nguon_ban_ve`, `trang_thai = de_xuat` rồi mới `xac_nhan`. ☐ Duyệt từng hạng mục.
4. **Bước 3 — Áp mã định mức:** đúng phụ lục (XD mới PL II, lắp đặt PL III/IV,
   sửa chữa–bảo dưỡng PL VI); bê tông chọn mác ở cột `cap_phoi` (PL VII);
   hồ sơ sửa chữa dùng mã PL II/III thì nhân VL 1,02; NC 1,15; M 1,05.
   Tra mã: `dutoan.py tra --tu-khoa "..."` hoặc `--ma`. ☐ Xác nhận mã và hệ số.
5. **Bước 4 — Giá tài nguyên theo vùng:** skill không chứa giá; `can-gia` lập
   danh sách đúng tài nguyên hồ sơ dùng để điền từ công bố giá kỳ hiện hành;
   tài nguyên không có trong công bố → báo giá, ghi nguồn. ☐ Xác nhận bảng giá.
6. **Bước 5 — Tính và xuất Excel:** `tinh` (từ chối tính khi còn mục chặn;
   `--nhap` chỉ để xuất bản nháp); Excel giữ công thức; tính lại bằng
   LibreOffice và so với `*_doi_chieu.json` phải khớp đến đồng. ☐ Xem bản nháp.
7. **Bước 6 — Tự soát:** `soat` (S01–S22). **Bước 7 — Thẩm tra hồ sơ có sẵn:**
   `soat_file_excel.py`, `nhap_du_toan_excel.py`, đối chiếu KL và checklist.

Nguyên tắc xuyên suốt: **không tự nhớ số liệu, tính bằng script, mỗi số có
nguồn, dừng ở điểm xác nhận** (`[XÁC NHẬN]` / `[ĐỀ XUẤT]` / `[THIẾU DỮ LIỆU]`).

## 4. Bài tập thực hành (kèm đáp án kiểm tra bằng script)

Mọi bài tập dùng bộ ví dụ **Nhà để xe** (`data/vi-du-nha-de-xe/`, 41 dòng, đã
chuyển mã TT 38, giá giả định) và các ví dụ có sẵn. Đáp án số dưới đây lấy từ
kết quả đã kiểm chứng ngày 16/11/2026 (xem README của ví dụ).

### Bài tập 1 — Bóc khối lượng theo trình tự thi công (Giáo trình Bài 4, 8, 9)

**Đề:** Không nhìn bảng đáp án, hãy lập danh sách công việc phần móng Nhà để
xe theo trình tự thi công (đào → bê tông lót → bê tông móng → cốt thép → ván
khuôn → xây móng → đắp cát → bê tông nền), rồi đối chiếu với `khoi_luong.csv`
dòng 1–15. **Đáp án:** danh sách đúng phải có đủ 15 dòng phần móng, theo đúng
thứ tự thi công; nếu lập theo danh mục định mức (nhóm AB rồi AF rồi AE…) sẽ
dễ sót công tác xen kẽ như đắp cát nền (dòng 14) nằm giữa bê tông và cốt thép.
**Kiểm tra:** `python3 scripts/dutoan.py soat --data data/vi-du-nha-de-xe
--khoi-luong data/vi-du-nha-de-xe/khoi_luong.csv --config
data/vi-du-nha-de-xe/config_du_toan.json` — phải ra **0 chặn**; nếu thiếu
dòng, tổng sẽ lệch khỏi GXDTT 266.261.178 đồng ở bài tập 6.

### Bài tập 2 — Đơn vị 100m2 / 100m3 (Giáo trình Bài 7, 59)

**Đề:** Trong ví dụ Nhà để xe, ván khuôn móng cột (dòng 8) có KL 0,048 với đơn
vị 100m2. Tính xem nếu quên chia cho 100 (nhập KL 4,8) thì thành tiền dòng này
tăng bao nhiêu lần? **Đáp án:** tăng đúng 100 lần. Đây là lỗi đắt nhất trong
Giáo trình Bài 59 (lợp mái ngói 150 m2 tính thành 3.000.000.000 đồng thay vì
30.000.000 đồng). **Kiểm tra:** sửa tạm KL dòng 8 thành 4,8 trong bản sao
`khoi_luong.csv`, chạy `tinh --nhap`, so sánh thành tiền dòng 8 với bản gốc;
xong xóa bản sao. Trong skill, `soat` có S-check đối chiếu đơn vị định mức với
đơn vị KL — đọc `references/kiem-tra-tham-tra.md` để biết mã S nào bắt lỗi này.

### Bài tập 3 — Tách công tác theo đơn giá khác nhau (Giáo trình Bài 7)

**Đề:** Vì sao Nhà để xe tách riêng BT cột (dòng 5, 16), BT xà dầm/giằng (dòng 6),
BT lanh tô (dòng 17), BT lan can (dòng 18) thay vì gộp chung thành "bê tông
M200"? Và vì sao xây móng (dòng 7) tách khỏi xây tường (dòng 26)? **Đáp án:**
mỗi loại có mã định mức và hao phí NC/M khác nhau (vd. BT cột NC 3,15 công/m3
theo AF.12210 so với BT móng NC 1,48 công/m3 theo AF.11220); gộp chung thì
không áp đúng mã. Ngược lại,
với dự toán thực tế (tư nhân/nước ngoài) có thể gộp để gọn (Giáo trình Bài 1,
7) — nhưng hồ sơ theo hệ 2026 thì **bắt buộc tách theo định mức**.
**Kiểm tra:** `dutoan.py tra --data data/tt38 --ma AF.12210 AF.12310 AF.12510
AF.14320` và so sánh hao phí NC của 4 mã.

### Bài tập 4 — Áp mã + chọn cấp phối (Giáo trình Bài 23, 31)

**Đề:** Bảng gốc ghi AF.11223 "BT móng, đá 1x2, mác 200". Hãy tìm mã TT 38
tương đương và mã cấp phối, giải thích vì sao không dùng mã cũ nguyên xi.
**Đáp án:** mã TT 38 là **AF.11220** (BT móng, rộng >250 cm) + cấp phối
**11.12322** (PCB40, độ sụt 6÷8 cm, dmax 20mm, mác 200). Mã cũ AF.11223
không còn trong TT 38 (số cuối 223 → 220; mác chuyển sang cấp phối).
**Kiểm tra:**
`python3 scripts/dutoan.py tra --data data/tt38 --ma AF.11220` và
`python3 scripts/dutoan.py tra --data data/tt38 --cap-phoi "PCB 40 6 ÷ 8 dmax = 20mm 200"`
— phải trả về 11.12322 (cùng 11.11323 PCB30 là phương án thay thế). Làm tương
tự cho AF.11111 → AF.11110 + 11.11371 và AE.21214 → AE.21210 + 12.10134
(vữa XM M75, cát vàng). Xem bảng chuyển mã đầy đủ trong
`data/vi-du-nha-de-xe/README.md`, kể cả 2 bẫy đổi mã: AK.81120 cũ → AK.81110
mới (không phải AK.81120) và BA.18101 cũ (công tắc) → BA.17101 mới (BA.18101
trong TT 38 là đồng hồ Vol kế).

### Bài tập 5 — Giá thực tế: lập danh sách tài nguyên cần giá (Giáo trình Bài 19, 24–27)

**Đề:** Từ `khoi_luong.csv` Nhà để xe, lập danh sách tài nguyên cần giá mà
không tự đoán tên. **Đáp án:** dùng `can-gia` — hồ sơ này dùng **46 tài
nguyên** (29 vật liệu + nhân công nhóm 1/2/3 + 14 máy). **Kiểm tra:**
`python3 scripts/dutoan.py can-gia --data data/vi-du-nha-de-xe --khoi-luong
data/vi-du-nha-de-xe/khoi_luong.csv --config data/vi-du-nha-de-xe/config_du_toan.json
--ra can_gia.csv` — phải ra "46 tài nguyên × 1 vùng = 46 dòng; 0 dòng chưa có
giá". Lưu ý 2 điểm Giáo trình Bài 19: giá là giá **trước thuế** và giá **tại
chân công trình** (đã gồm cước vận chuyển); nếu công bố giá ghi giá tại nơi
bán thì phải cộng thêm cước. Vật liệu nào không có trong công bố giá của Sở XD
thì lấy báo giá nhà cung cấp / chứng thư thẩm định giá / hóa đơn, ghi nguồn —
không tự điền giá.

### Bài tập 6 — Tính tổng hợp dự toán bằng tay rồi đối chiếu script (Giáo trình Bài 28)

**Đề:** Từ kết quả chi tiết Nhà để xe (VL 121.079.905; NC 96.240.306;
M 12.534.310), tính tay T, C (7,3% trên T), TT (2,5% trên T), GT, TL (5,5%
trên T+GT), GXDTT, GTGT (8%), GXD và LT (1,1% trên GXD). **Đáp án:**
T = 229.854.521; C = 16.779.380; TT = 5.746.363; GT = 22.525.743;
TL = 13.880.915; GXDTT = 266.261.178; GTGT = 21.300.894;
GXD = 287.562.073; LT = 3.163.183; GXD + LT = 290.725.256 (đồng).
**Kiểm tra:** chạy `tinh` cho ví dụ Nhà để xe rồi mở
`vi-du-nha-de-xe_doi_chieu.json` — phải khớp đến đồng; mở file Excel, tính lại
công thức bằng LibreOffice (`soffice --headless --calc --convert-to xlsx`) rồi
so sánh sheet `TH_CPXD` — cũng phải khớp đến đồng. Đây là bài kiểm tra quan
trọng nhất của Giai đoạn 3: ví dụ chạy ra Excel khớp tay đến đồng.
Đối chiếu tay thêm 2 dòng: dòng 1 AB.11442 (1,04 công × 300.000 = 312.000
đ/m3; × 12,326 m3 = 3.845.712 đồng) và dòng 3 AF.11110+11.11371 (VL
960.599,25; NC 342.400; M 55.500 đ/m3 — xem cách tính cấp phối trong README
của ví dụ).

### Bài tập 7 — Kiểm tra khối lượng bằng tương quan (Giáo trình Bài 6)

**Đề:** Sau khi chạy `tinh` cho Nhà để xe, kiểm tra nhanh bằng 3 tương quan:
(a) giá trị ván khuôn so với giá trị bê tông tương ứng; (b) KL BT dầm so với
KL BT cột; (c) tỷ trọng phần móng trong tổng GXDTT. **Đáp án:** (a) nếu giá trị
ván khuôn sàn lớn hơn BT sàn rất nhiều thì khả năng chưa chia diện tích ván
khuôn cho 100 (xem bài tập 2); (b) BT dầm/giằng 1,447 m3 và BT cột 1,162 +
0,259 m3 cùng bậc — nếu một bên gấp vài lần bên kia thì kiểm tra lại;
(c) phần móng thường chiếm khoảng 20–30% tổng giá trị công trình (con số tham
khảo của Giáo trình Bài 6, **không phải quy tắc**) — lệch xa thì rà soát lại
KL phần móng. **Kiểm tra:** đọc sheet `DT_CT` trong Excel xuất ra, cộng thành
tiền theo hạng mục "Phần móng"/"Phần thân" và so sánh.

### Bài tập 8 — Công việc không có trong định mức (Giáo trình Bài 31)

**Đề:** Nhà để xe có 3 dòng bảng gốc ghi mã `TT` (tôn úp nóc, sản xuất cửa gỗ,
sản xuất lắp dựng cửa sổ nhôm kính). Xử lý thế nào theo skill? **Đáp án:**
dùng `ma_hieu = TG` + `don_gia_tron_goi` (55.000 đ/md; 700.000 đ/m2;
500.000 đ/m2 — giá giả định, lấy theo đơn giá gộp của chính bảng gốc).
Không bịa mã định mức. Giáo trình Bài 31 nêu 3 trường hợp: (1) có đơn giá
tương đương thì vận dụng và sửa tên (vd. đắp cát tôn nền lấy mã AB.13411);
(2) gần giống nhưng khác tính chất thì sửa định mức/đơn giá; (3) hoàn toàn
không có thì tính định mức/đơn giá từ đầu hoặc khoán theo m2. Trường hợp (3)
trong skill chính là dòng `TG`. **Kiểm tra:** `soat` báo 3 thông tin S10 về
Bảng 3.9 PL III — đọc ghi chú trong README của ví dụ để biết vì sao 3 dòng
này không thuộc Bảng 3.9 (không phải công việc thiết kế riêng/công nghệ đặc thù).

### Bài tập 9 — Đơn giá gộp và biện pháp trong dự thầu (Giáo trình Bài 49–59)

**Đề:** Hồ sơ mời thầu chỉ mời khối lượng bê tông, không mời ván khuôn. Nhà
thầu phải làm gì? Và vì sao Giáo trình Bài 59 dặn "công tác nào làm trước, để
giá cao"? **Đáp án:** phải phân bổ chi phí ván khuôn (và giàn giáo, vận chuyển
lên cao, shoring…) vào đơn giá bê tông — nếu quên tính biện pháp thì khi trúng
thầu sẽ lỗ hoặc phải bỏ bảo lãnh (ví dụ Bài 59). "Làm trước để giá cao" là để
được thanh toán trước, tránh hụt vốn khi biện pháp phải làm ngay từ đầu mà
tiền lại phân bổ đều cả công trình. **Kiểm tra trong skill:** đây là việc của
Bước 7 (thẩm tra hồ sơ mời thầu/dự thầu) — đọc `references/kiem-tra-tham-tra.md`
mục checklist và `references/mau-don-vi.md` mục 3 (lỗi thường gặp); riêng lỗi
đơn vị 100 thì xem bài tập 2.

### Bài tập 10 — Bài tập cuối sách, làm lại theo hệ 2026 (Giáo trình, "Thay lời kết")

**Đề (gốc, Bài 8):** Tính lại móng M1 với 3 thay đổi: (a) BT lót mác 75 (giảm
30 kg XM so với mác 100, cát đá không đổi); (b) BT móng thêm phụ gia đông cứng
nhanh 1,2 kg/m3, giá 60.000 đ/kg; (c) trên lớp BT lót có lớp nilon chống thấm,
hao hụt 15%, giá 20.000 đ/m2. **Làm theo hệ 2026:** (a) BT lót mác 75 **không có cấp phối trong PL VII
TT 38** — cấp phối bê tông bắt đầu từ mác 100 (mác 75 chỉ có ở vữa xây/trát,
vd. 12.10134). Vì vậy không thể chỉ đổi mã cấp phối: hoặc dùng mác 100
(11.11371, cùng họ với ví dụ) và ghi rõ thay đổi thiết kế, hoặc lập cấp phối
riêng cho mác 75 làm định mức riêng của hồ sơ (`dinh_muc.csv`) với căn cứ
thí nghiệm/thiết kế — **không** tự trừ 30 kg xi măng khỏi cấp phối chuẩn
(như sách cũ gợi ý) vì tỷ lệ XM/cát/đá/nước của cấp phối không suy ra bằng
phép trừ; (b) phụ gia không có trong cấp phối chuẩn (script bỏ qua dòng "Phụ
gia" khi nạp `cap_phoi.csv`) — ghi thành dòng `TG` riêng hoặc thêm tài nguyên
phụ gia vào `dinh_muc.csv` của hồ sơ với căn cứ là tài liệu kỹ thuật của nhà
sản xuất; (c) nilon chống thấm cũng là dòng riêng (KL = diện tích BT lót × 1,15
hao hụt). **Kiểm tra:** chạy `tinh` cho bản sao ví dụ Nhà để xe đã sửa dòng 3
sang 11.11371 (giữ mác 100) và thêm 2 dòng mới; `soat` phải 0 chặn; so sánh
GXDTT mới với 266.261.178 đồng của bản gốc và giải thích chênh lệch từng phần.

## 5. Bẫy thường gặp (tổng hợp từ Giáo trình Bài 6, 7, 31, 32, 59 + Phụ lục 1)

1. **Quên chia 100** ở công tác có đơn vị 100m2/100m3/100md (ván khuôn, lợp
   mái, đào đất bằng máy, đóng cừ tràm) — giá trị tăng 100 lần (Bài 7, 59).
2. **Không tách công tác** theo chiều cao, chiều dày, mác vữa/bê tông — sau
   áp mã không được, phải tách lại (Bài 7).
3. **Trừ thể tích cốt thép khỏi khối lượng bê tông** — sai: KL BT là KL hình
   học theo thiết kế, không trừ thép chiếm chỗ (Bài 32, Phụ lục 1 mục 10).
4. **Trừ diện tích ván khuôn ở lỗ rỗng <1 m2** — sai: không trừ và không tính
   thêm ván khuôn cho gờ/thành lỗ (Bài 32).
5. **Thống kê cốt thép thiếu nối chồng, thép chờ, thép biện pháp (ngựa kê)** —
   định mức chỉ tính hao hụt thi công; phải cộng nối chồng vào thống kê, vì
   mỗi cây thép chỉ dài 11,7 m (Bài 17, Phụ lục 1 mục 11).
6. **Quên giàn giáo và vận chuyển lên cao** — giàn giáo ngoài tính theo diện
   tích hình chiếu đứng; giàn giáo trong chỉ tính khi làm việc cao >3,6 m
   (Phụ lục 1 mục 19, 20). Trong TT 38, tra mã AL tương ứng, đừng bỏ sót.
7. **Áp nhầm mã bả matit** (Bài 59, Phụ lục 1 mục 18): matit keo (định mức
   0,4 kg/m2) khác bột bả tường; kiểm tra tên mã trong TT 38 trước khi dùng.
8. **Vật liệu khác:** tính theo % trên tổng đơn giá vật liệu — kiểu tính bù giá
   không tính được phần này nên 2 cách tính luôn chênh nhau (Bài 27). Skill
   tính vật liệu khác (VLK) theo % trên tổng VL của từng mã — kiểm tra dòng
   VLK trong `PT_DG`.
9. **Tin máy tuyệt đối:** tổng hợp vật tư có thể sai mà không ai dò ra; phải
   đối chiếu tổng vật tư giữa bảng phân tích và bảng tổng hợp (Bài 44). Trong
   skill: so `TH_VT` với `PT_DG` trong Excel xuất ra.
10. **Giá trước thuế / sau thuế và giá tại chân công trình / tại nơi bán** —
    nhầm là làm lại cả bảng (Bài 19). Ghi rõ nguồn + ngày áp dụng cho mọi giá.

## 6. Những gì trong sách cũ KHÔNG được dùng làm quy tắc hệ 2026

| Sách cũ viết (Bài) | Hệ 2026 áp dụng | Ghi chú |
|---|---|---|
| ĐM 1776/1777, mã 5 chữ số cuối (AF.11223, AK.81120…) (Bài 17, 23, 31) | **TT 38/2026/TT-BXD**, mã rút gọn 4 chữ số + cấp phối PL VII | Xem bảng chuyển mã trong `data/vi-du-nha-de-xe/README.md`; 2 bẫy đổi mã AK.81120 và BA.18101 |
| TT 06/2016/TT-BXD + NĐ 32/2015/NĐ-CP (Bài 16, 28) | **NĐ 206/2026/NĐ-CP + TT 36/37/38/40/2026/TT-BXD** | Đọc `references/can-cu-phap-ly.md` (ngày rà soát 16/11/2026) |
| Đơn giá tỉnh + nhân hệ số NC/M theo lương tối thiểu (Bài 18, 20, 24) | Tính lại đơn giá từ **định mức TT 38 × giá công bố kỳ hiện hành**; nhân công theo **nhóm lao động TT 37** (phương pháp mới từ 01/01/2027) | Không nhân hệ số lương tối thiểu |
| Chi phí chung 6,5%, TL 5,5% (dân dụng) (Bài 13, 28) | CPC **7,3%** (Bảng 3.3, nấc ≤40 tỷ), TL **5,5%** (Bảng 3.6), TT **2,5%** (Bảng 3.5), LT **1,1%** (Bảng 3.7) — tra theo loại/quy mô trong `data/bang_ty_le_tt36_2026.json` | TL trùng số nhưng căn cứ khác; CPC khác số — phải tra lại |
| Thuế GTGT 10% (Bài 22) | **8%** trong các ví dụ của skill (kiểm tra thuế suất hiện hành khi lập hồ sơ thật) | |
| QĐ 957/QĐ-BXD cho QLDA/tư vấn (Bài 22, 48) | Bảng 1.1 **PL VIII TT 38** (QLDA) + PL VI TT 36 (tư vấn) — tra bằng `dutoan.py ty-le` | |
| 4 cách tính (giá thực tế / bù giá / TT18 / tính lại đơn giá) (Bài 30) | Skill dùng **1 cách**: tính lại đơn giá từ định mức TT 38 và giá hiện hành (tương đương cách 3/4 của sách) | Không làm kiểu bù giá |
| TT 17/2000 phân loại vật tư/thiết bị, QĐ 89/2000 cước vận chuyển (Bài 22) | **[CHƯA ĐỐI CHIẾU]** — chưa rà soát lại theo hệ 2026; không đưa vào skill cho đến khi đối chiếu | Hỏi người dùng trước khi áp dụng vào hồ sơ thật |

## 7. Hướng dẫn dùng các ví dụ có sẵn

| Ví dụ | Dạy cái gì | Lệnh chạy |
|---|---|---|
| `data/vi-du/` | Bộ nhỏ nhất, mã + định mức + giá đều là số giả (tiền tố VD.) — học cấu trúc file và lệnh `tinh` lần đầu | `tinh --data data/vi-du ...` → GXD 140.434.146 |
| `data/vi-du-tt38/` | Mã TT 38 thật + cấp phối (AF.11210 + 11.12323) + hồ sơ sửa chữa (hệ số PL VI mục 3.b) | → GXD 87.295.481 |
| `data/vi-du-nha-de-xe/` | **Bài tập chính của tài liệu này:** 41 dòng, chuyển mã đầy đủ, 3 dòng TG, 3 điểm dữ liệu TT 38 đã khép 16/11/2026 (xem README của ví dụ) | → GXDTT 266.261.178; GXD 287.562.073 |
| `data/vi-du-doan/` | Mẫu đơn vị: KL theo đoạn/xã, nhiều vùng giá, TDT (`mau_xuat: doan_vung`) | → tổng sau thuế 151.531.785 |
| `data/vi-du-tt40/` | Bảo dưỡng/sửa chữa trong kế hoạch bảo trì (TT 40) | → GXD 104.694.588 |
| `data/vi-du-khao-sat/` | Dự toán khảo sát (PL V TT 36) | → tổng sau thuế 13.115.401 |

Tất cả 6 bộ đều là **giá giả** — chạy thử và học, không dùng lập hồ sơ thật.
Sau mỗi lần sửa skill, chạy lại cả 6 bộ và so với các tổng trên: phải khớp đến
đồng (quy trình kiểm chứng của Giai đoạn 5).
