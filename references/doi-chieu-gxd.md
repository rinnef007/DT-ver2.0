# Đối chiếu mẫu GXD với skill (GXD → skill)

- **Ngày:** 16/11/2026
- **Mẫu GXD:** `DutoanGXD1.xlsm` (687 KB, 61 sheet) — **template của phần mềm Dự toán GXD 2026, bảng dự toán trống** (0 dòng công tác, tổng 0 đồng). Giá trị đối chiếu nằm ở cấu trúc cột và công thức tổng hợp, không ở số liệu.
- **Skill:** `skill-DT-v2` — mẫu `bang_3_8` (`scripts/xuat_excel.py`) và `doan_vung` (`scripts/xuat_excel_doan.py`).
- **Nguồn đối chiếu trước:** `~/workspace/DT-ver2.0-work/phase2-4-data-gxd.md` mục 4 (đã đối chiếu 6 sheet). File này viết lại đầy đủ thành bảng tra cứu dùng cho Giai đoạn 4–5, kèm kết quả chạy thật `soat_file_excel.py` và `nhap_du_toan_excel.py` trên file mẫu.
- **Quy ước:** `[CHƯA ĐỐI CHIẾU]` = chưa xác minh được từ file mẫu trống (cần file GXD đã điền dữ liệu hoặc HDSD); không tự suy ra.

## 1. Bản đồ sheet — tổng quan

| Sheet GXD | Sheet skill tương đương | Mức khớp |
|---|---|---|
| `Du toan XD` (33 cột A–AG) | `DT_CT` (`bang_3_8`) / `DT` (`doan_vung`) | Khớp mục đích, lệch cấu trúc (xem mục 2) |
| `Don gia XD` (19 cột A–S) | `PT_DG` (`bang_3_8`) / `DGCT` (`doan_vung`) | Khớp mục đích, lệch cấu trúc (xem mục 3) |
| `THCP xay dung` (bảng 1 dòng 5–20, bảng 2 dòng 29–56) | `TH_CPXD` (`bang_3_8`) / `TDT` (`doan_vung`) | **Khớp công thức bảng 1**; bảng 2 có 3 lỗi (xem mục 4) |
| `TH vat tu XD` (16 cột) | `TH_VT` (+ `HP_CT`) | **Khác mục đích** (xem mục 7) |
| `Nhan cong XD` (8 cột) | `GIA_TN` (phần NC) — tương đương một phần | Skill không tính ĐG NC theo cấp bậc (xem mục 8) |
| `Gia ca may XD` (40 cột A–AN) | Không có | **Skill không có** (xem mục 9 và 14.1) |
| `Don gia tong hop` (32 cột, demo TH1) | Chế độ mã `TG` (không có sheet riêng) | Skill không có bảng đơn giá tổng hợp riêng (xem mục 10 và 14.3) |
| `Ts` (thông số công trình, sheet ẩn) | `THAM_SO` + `config_du_toan.json` | Khớp về vai trò, khác cách tra tỷ lệ (xem mục 5) |
| `Config` (cấu hình GXD, sheet ẩn) | `config_du_toan.json` (một phần) | Config GXD chứa tham chiếu hỏng (xem mục 11) |
| `DMTL` (bảng nội suy định mức tỷ lệ, 1.319 dòng) | `data/bang_ty_le_tt36_2026.json`, `data/bang_ty_le_tt40_2026.json` | Cùng vai trò tra tỷ lệ theo loại/quy mô (xem mục 6) |
| *(GXD không có)* | `HP_CT`, `KL_DIEN_GIAI`, `CANH_BAO` | Skill có thêm 3 sheet GXD không có trong file mẫu (GXD để diễn giải KL trong chính `Du toan XD` cột Z–AF, tham số ở `Ts`/`Config`/`Data`) |

## 2. `Du toan XD` (GXD) ↔ `DT_CT` / `DT` (skill)

Tiêu đề GXD ở dòng 5 (dòng 6 là tiêu đề con, dòng 7 là chỉ số `[1]`…`[17]`). Vùng dữ liệu dòng 8–29 **trống hoàn toàn** (chỉ có dòng tổng 30 và dòng 31 ghi `A/Ap/B/C` ở cột U–X); vì vậy mọi nhận xét về công thức từng dòng dữ liệu đều là suy từ tiêu đề/chỉ số, không phải từ công thức thật.

| Cột GXD | Nội dung GXD | Cột skill `DT_CT` | Cách xử lý khi nhập / xuất |
|---|---|---|---|
| A | ID | — | **Skill không có.** Khi nhập: bỏ qua. Khi xuất theo mẫu GXD: đánh số dòng liên tục. |
| B | STT | A STT | Khớp. |
| C | MÃ VỮA | — | **Skill không có cột mã vữa riêng.** Skill xử lý vữa qua cột `cap_phoi` trong `khoi_luong.csv` và thay dòng "Vữa bê tông" bằng thành phần cấp phối trong `PT_DG`. Khi nhập GXD: mã vữa → `cap_phoi` (xem mục 12). |
| D | MÃ HIỆU ĐỊNH MỨC | B Mã hiệu | Khớp (GXD tách 2 cột D/E; skill gộp 1 cột). Khi nhập: nếu D ≠ E thì lấy D làm `ma_hieu`, ghi chú E vào `dien_giai`. |
| E | MÃ HIỆU ĐƠN GIÁ | B Mã hiệu (gộp) | Xem trên. |
| F | NỘI DUNG CÔNG VIỆC | C Tên công tác | Khớp. |
| G | ĐƠN VỊ | D Đơn vị | Khớp. |
| H | KHỐI LƯỢNG | E Khối lượng | Khớp. |
| I | YÊU CẦU KỸ THUẬT / CHỈ DẪN KỸ THUẬT | — | **Skill không có cột YCKT.** Khi nhập: đưa vào `dien_giai` trong `khoi_luong.csv` (hoặc bỏ qua kèm cảnh báo — xem đề xuất mục 15). |
| J | Kvlc (hệ số vật liệu chính) | G HS VL (gộp) | GXD tách Kvlc/Kvlp; skill gộp 1 hệ số VL. Khi nhập: `hs_vl = Kvlc × Kvlp` nếu cả hai đều có, ghi căn cứ vào `can_cu_he_so`. |
| K | Kvlp (hệ số vật liệu phụ) | G HS VL (gộp) | Xem trên. |
| L | Knc1 | H HS NC (gộp) | GXD có **3 hệ số nhân công** (Knc1/2/3). Ý nghĩa từng hệ số `[CHƯA ĐỐI CHIẾU]` (có thể theo nhóm nhân công — cần file GXD đã điền hoặc HDSD). Khi nhập: **chưa có quy tắc gộp an toàn** — giữ nguyên 3 cột trong báo cáo nhập, chưa đưa vào `he_so_nc`. |
| M | Knc2 | H HS NC (gộp) | Xem trên. |
| N | Knc3 | H HS NC (gộp) | Xem trên. |
| O | Km | I HS M | Khớp (1 hệ số máy). |
| P | ĐƠN GIÁ — Vật liệu | J ĐG vật liệu | Khớp. |
| Q | ĐƠN GIÁ — Vật liệu phụ | (gộp vào J) | GXD tách ĐG vật liệu phụ riêng; skill gộp vào ĐG VL. Khi nhập: `ĐG VL (skill) = ĐG VL + ĐG VLP` (kiểm chứng lại bằng thành tiền). |
| R | ĐƠN GIÁ — Nhân công | K ĐG nhân công | Khớp. |
| S | ĐƠN GIÁ — Máy | L ĐG máy | Khớp. |
| T | ĐƠN GIÁ [6] (tổng đơn giá) | — | **Skill không có cột tổng đơn giá.** Skill tính thành tiền = KL × từng ĐG phần rồi cộng (P = M+N+O); GXD tính Y = KL × tổng ĐG [6]. Kết quả bằng nhau khi [6] = P+Q+R+S. |
| U | THÀNH TIỀN — Vật liệu `[15]=[5]*[12]` | M TT vật liệu `=E*J` | Khớp công thức (KL × ĐG). |
| V | THÀNH TIỀN — Vật liệu phụ `[9']=[5]*[6']` | (gộp vào M) | Xem cột Q. |
| W | THÀNH TIỀN — Nhân công `[16]=[5]*[13]` | N TT nhân công `=E*K` | Khớp. |
| X | THÀNH TIỀN — Máy `[17]=[5]*[14]` | O TT máy `=E*L` | Khớp. |
| Y | THÀNH TIỀN (tổng) `[7]=[5]*[6]` | P Thành tiền `=M+N+O` | Khớp về kết quả; khác cách tính (GXD: KL × tổng ĐG [6]; skill: cộng 3 thành tiền phần). |
| Z | SỐ BỘ PHẬN GIỐNG NHAU `[5]` | — | **Skill không có cột diễn giải KL dạng số.** Skill để diễn giải tự do trong sheet `KL_DIEN_GIAI` (cột F) và trường `dien_giai` trong `khoi_luong.csv`. Khi nhập: Z + AA–AF → chuỗi diễn giải `Z×(AA×AB×AC)×AD = AE → AF`. |
| AA–AC | KÍCH THƯỚC: DÀI `[6]`, RỘNG `[6']`, CAO (SÂU) `[7]` | — | Xem trên. |
| AD | HỆ SỐ `[8]` | F Quy đổi (tương tự một phần) | GXD: hệ số trong diễn giải KL; skill: cột Quy đổi riêng (quy đổi đơn vị ĐM về đơn vị KL). Không đồng nhất hoàn toàn — khi nhập cần xem từng dòng. |
| AE | K.L MỘT BỘ PHẬN `[9]` | — | Xem cột Z (diễn giải). |
| AF | K.L TOÀN BỘ `[10]` | E Khối lượng (kết quả) | GXD tính KL toàn bộ = số bộ phận × KL 1 bộ phận; skill nhập KL trực tiếp. Khi nhập: đối chiếu AF với H, chênh lệch thì cảnh báo. |
| AG | GHI CHÚ `[11]` | Q Loại dòng (HM/CT/CHM/TONG) — khác mục đích | Skill không có cột ghi chú trong `DT_CT`. Khi nhập: ghi chú → `dien_giai`. |

Dòng tổng GXD (dòng 30): `U30=SUM(U8:U29)` (V30, W30, X30, Y30 tương tự), `A30=MAX(A8:A29)`. Skill `DT_CT`: dòng `TỔNG CỘNG` dùng `SUMIF($Q…,"CT",…)` chỉ cộng dòng công tác. **Khác biệt:** GXD cộng trực tiếp theo vùng dòng (giả định vùng 8–29 chỉ chứa công tác); skill chịu được dòng hạng mục/tổng con xen trong vùng. Trong file mẫu, các cột ĐG (P–T) ở vùng dữ liệu không có công thức nào (bảng trống — giá trị ĐG do phần mềm GXD điền, không phải công thức Excel), trong khi skill viết ĐG bằng công thức tham chiếu `PT_DG` (`=PT_DG!…*F*G`).

Mẫu `doan_vung` của skill (`DT` sheet): thêm các cột KL theo từng đoạn và ĐG theo từng vùng trong cùng một bảng. GXD `Du toan XD` **không có** phân đoạn/vùng giá trong cùng một bảng (GXD xử lý đa vùng bằng file/cấu hình khác — chưa xác minh được từ file mẫu trống này).

## 3. `Don gia XD` (GXD) ↔ `PT_DG` / `DGCT` (skill)

Tiêu đề GXD ở dòng 5, chỉ số dòng 6. Toàn bộ sheet **không có dòng dữ liệu** (dòng 7 trở đi trống).

| Cột GXD | Nội dung GXD | Cột skill `PT_DG` | Nhận xét |
|---|---|---|---|
| A | ID | — | Skill không có. |
| B | STT | — | Skill không đánh STT trong `PT_DG`. |
| C | MÃ VỮA | — | Như mục 2 (→ `cap_phoi`). |
| D | MÃ HIỆU ĐỊNH MỨC | A Mã hiệu | Khớp. |
| E | MÃ HIỆU ĐƠN GIÁ | A Mã hiệu (gộp) | GXD tách 2 mã; skill gộp. |
| F | MSVT (mã số vật tư) | C Mã TN | Khớp (tên gọi khác). |
| G | TÊN CÔNG VIỆC / THÀNH PHẦN HAO PHÍ | D Tên công tác / tài nguyên | Khớp. |
| H | ĐƠN VỊ | E ĐVT | Khớp. |
| I | KHỐI LƯỢNG | — | GXD có cột KL trong bảng phân tích (KL của công tác); skill `PT_DG` tính trên 1 đơn vị ĐM, không có KL. |
| J | ĐỊNH MỨC HAO PHÍ | F Hao phí | Khớp. |
| K | ĐƠN GIÁ VẬT TƯ | G Đơn giá | Khớp. |
| L | HỆ SỐ | I Hệ số | Khớp (GXD để hệ số sau đơn giá; skill để hệ số ở cột cuối). |
| M | THÀNH TIỀN | H Thành tiền `=F*G*I` | Khớp công thức. |
| N | HAO PHÍ | — | **GXD có thêm 2 cột hao phí** (N: hao phí; O: hao phí khác) — ý nghĩa `[CHƯA ĐỐI CHIẾU]` (có thể là hao phí sau điều chỉnh / hao phí khác; bảng trống nên không xác minh được). |
| O | HAO PHÍ KHÁC | — | Xem trên. |
| P | ĐƠN GIÁ VẬT LIỆU | (dòng "Cộng vật liệu" ở cột H) | GXD có 4 cột ĐG tổng ở cuối (P/S: VL, VLP, NC, M); skill có 3 dòng "Cộng VL/NC/M" ở cột H. |
| Q | ĐƠN GIÁ VẬT LIỆU PHỤ | — | Xem trên. |
| R | ĐƠN GIÁ NHÂN CÔNG | — | Xem trên. |
| S | ĐƠN GIÁ MÁY | — | Xem trên. |

**Khác biệt về logic:**
- Skill `PT_DG` xử lý "Vật liệu khác / Máy khác %" bằng công thức `=F/100*SUMIF(loại…)` (phần trăm trên tổng VL/M); GXD có cột riêng `HAO PHÍ KHÁC` (O) — công thức chưa rõ vì bảng trống.
- Skill `DGCT` (mẫu `doan_vung`) đi xa hơn GXD: tính luôn T, C, TT, GT, TL, G, GTGT, Gxd cho từng mã theo từng vùng giá (đơn giá/đv KL = G / số đv ĐM). GXD `Don gia XD` chỉ phân tích đến ĐG thành phần; phần tổng hợp nằm ở `THCP xay dung`.
- Ngược lại, `nhap_du_toan_excel.py` của skill (doc_dgct) được viết cho bố cục `DGCT` của chính skill (STT | Mã số | Thành phần hao phí | Đơn vị | Định mức | Đơn giá từng vùng | Hệ số | Thành tiền, kèm các dòng mục a) Vật liệu / b) Nhân công / c) Máy thi công) — **không phải** bố cục `Don gia XD` của GXD. Xem kết quả chạy thật ở mục 12.

## 4. `THCP xay dung` (GXD) ↔ `TH_CPXD` (skill) — công thức khớp (bảng 1)

Bảng 1 GXD (dòng 5–20) và skill `TH_CPXD` (Bảng 3.8 PL III TT 36/2026):

| Khoản | GXD (dòng, công thức) | Skill `TH_CPXD` (công thức) | Kết luận |
|---|---|---|---|
| T = VL+NC+M | D6 `=SUM(D7:D9)` | D7 `=D8+D9+D10` | **Khớp** |
| VL | D7 `=('Du toan XD'!U30+'Du toan XD'!V30)*F7` (cộng cả VL phụ) | D8 `=DT_CT!M{tong}` | Khớp về nguồn (tổng TT VL); GXD nhân thêm hệ số ở `Ts` (F7 = hệ số vật liệu, = 1 trong mẫu) |
| NC | D8 `='Du toan XD'!W30*F8` | D9 `=DT_CT!N{tong}*THAM_SO!Knc` | **Khớp** (cả hai đều nhân Knc) |
| M | D9 `='Du toan XD'!X30*F9` | D10 `=DT_CT!O{tong}*THAM_SO!Km` | **Khớp** (cả hai đều nhân Km) |
| GT = C+TT | D11 `=SUM(D12:D13)` | D11 `=D12+D13` | **Khớp** |
| C (chi phí chung) | D12 `=D6*F12*G12`, F12 `=Ts!$N$38`, G12 = 1 | D12 `=IF(COSO="NC",D9,D7)*C%` | **Khớp công thức**, khác nguồn tỷ lệ: GXD lấy từ sheet `Ts` (N38), skill lấy từ `THAM_SO` |
| TT | D13 `=D6*F13`, F13 `=Ts!$N$41` | D13 `=D7*TT%` | **Khớp** |
| TL = (T+GT)×tỷ lệ | D14 `=(D6+D11)*F14` | D14 `=(D7+D11)*TL%` | **Khớp** |
| GXDTT = T+GT+TL | D15 `=D6+D11+D14` | D15 `=D7+D11+D14` | **Khớp** |
| GTGT = GXDTT×TGTGT | D16 `=D15*F16` | D16 `=D15*VAT%` | **Khớp** |
| GXD (sau thuế) | D17 `=D15+D16` | D17 `=D15+D16` | **Khớp** |
| LT (nhà tạm) | D18 `=(D15+D16)*F18*G18` — tức (GXDTT+GTGT)×tỷ lệ×hệ số | D18 `=D15*LT%*(1+VAT%)` | **Khớp về kết quả** (cả hai đều = GXDTT×LT%×(1+TGTGT) khi G18=1); khác cách viết |
| GDP (dự phòng) | D19 `=(D17+D18)*F19`, F19 `=IF(CF_TDGDD<>0,0,'CP Du phong'!$D$110)` | Skill `TH_CPXD` **không có dòng dự phòng** (dự phòng nằm ở `TDT` mẫu `doan_vung` / TMDT) | **Lệch phạm vi:** GXD gộp dự phòng vào THCP; skill để dự phòng ở tổng hợp TMDT |
| Giá dự thầu | D20 `=D17+D18+D19` | Skill không có dòng "Giá dự thầu" trong `TH_CPXD` | Xem trên |

Số liệu mẫu trong file GXD (để kiểm chứng, không phải số thật): C = 6,2% (`Ts!$N$38` → 0,062), TT = 2%, TL = 6%, GTGT = 8%, LT = 1,1% — khớp với các tỷ lệ mặc định trong skill cho loại công trình đã chọn trong mẫu. Các tỷ lệ này phụ thuộc loại/quy mô công trình, không phải hằng số chung.

### 4.1. Lỗi trong bảng 2 của GXD (dòng 29–56, "Tổng hợp tất cả các hạng mục") — đã kiểm chứng bằng đọc công thức thô

| Vị trí | Nội dung | Đánh giá |
|---|---|---|
| D38 (dòng "Chi phí trực tiếp", cột C ghi `VL+NC+M`) | Công thức `=SUM(D39:D41)` — tức cộng **GT + C + TT** (D39 là GT, D40 là C, D41 là TT), trong khi đúng ra phải là `=SUM(D35:D37)` (VL+NC+M) | **Công thức sai.** Giá trị đã tính đều là 0 nên không phát hiện bằng mắt thường. |
| D39 (dòng "Chi phí gián tiếp", cột C ghi `C+LT+TT`) | Công thức `=D11` — tức copy GT từ bảng 1 (GT = C+TT, không có LT) | Nhãn và công thức mâu thuẫn nhau (LT không nằm trong GT ở bảng 1). |
| Dòng 41 (dòng TT) | Cột A đánh STT `3` thay vì `2` | Lỗi đánh số. |
| D46 (dòng LT "Chi phí nhà tạm…") | Cột D **trống, không có công thức** (trong khi cột C có công thức chuỗi `="GXDtt*"&F18*100&"%"&"*(1+"&F16*100&"%)"`, và bảng 1 có D18 đầy đủ) | Ô giá trị thiếu. |
| D47/D48 | D47 `=D19` (dự phòng), D48 `=D20` (giá dự thầu) | Khớp với bảng 1. |

Ba lỗi đầu (D38, D39, D46) là test case cho `soat_file_excel.py` — xem mục 11: script hiện tại **không bắt được** lỗi nào trong ba lỗi này.

## 5. `Ts` (GXD) ↔ `THAM_SO` + `config_du_toan.json` (skill)

Sheet `Ts` là sheet ẩn, gồm thông tin công trình (dòng 1–20), chi phí đã duyệt (dòng 21–31, toàn 0), các hệ số/định mức tỷ lệ (dòng 33–42), đơn giá nhân công (dòng 44 trở đi).

### 5.1. Mapping tỷ lệ (đã kiểm chứng giá trị đã tính)

| Tỷ lệ | GXD `Ts` (cột N = phần XD, O = phần LĐ) | Skill `THAM_SO` | Giá trị trong mẫu |
|---|---|---|---|
| Hệ số vật liệu | N35 `1` (dùng ở `THCP` F7 `=ROUND(Ts!$N$35,3)`) | Không có ô riêng; skill áp HS VL theo từng dòng (`DT_CT` cột G) | 1 |
| Hệ số nhân công | N36 `1` | B17 Knc | 1 |
| Hệ số máy | N37 `1` | B18 Km | 1 |
| Chi phí chung (C) | N38 `=VLOOKUP(Data!$E$9,CF_VLHSDMTL,7,0)/100` | B12 (C) | 0,062 |
| Thu nhập chịu thuế tính trước (TL) | N39 `=VLOOKUP(Data!$E$9,CF_VLHSDMTL,8,0)/100` | B14 (TL) | 0,06 |
| Thuế GTGT (TGTGT) | N40 `=VAT` (named range) | B16 (VAT) | 0,08 |
| Chi phí một số công việc không xác định được KL (TT/CKKL) | N41 `=VLOOKUP(Data!$E$9,CF_VLHSDMTL,5,0)/100` | B13 (TT) | 0,02 |
| Chi phí nhà tạm (LT/CNT) | N42 `=INDEX(AB59:AB60,L15)/100` | B15 (LT) | 0,011 |

Ghi chú:
- GXD tra tỷ lệ bằng `VLOOKUP` từ bảng nội suy `DMTL` theo loại công trình (`Data!$E$9`, named range `CF_VLHSDMTL`); skill tra tỷ lệ từ `data/bang_ty_le_tt36_2026.json` / `bang_ty_le_tt40_2026.json` theo loại/quy mô công trình (lệnh `dutoan.py ty-le`). Cùng vai trò, khác kho dữ liệu — xem mục 6.
- Cơ sở tính C: GXD dùng `G12 = 1` (hệ số nhân thêm, luôn 1 trong mẫu) và `F12 = Ts!$N$38`; skill dùng `THAM_SO!$D$12` (COSO = "T" hoặc "NC", theo Bảng 3.3/3.4 PL III TT 36).
- `Ts` dòng 13–20 (Loại công trình = 2, Cấp công trình = 3, Số bước thiết kế = 3, Loại báo cáo = 1, Xác định = 1, VAT = 0,08) ↔ skill `config_du_toan.json` (`loai_cong_trinh`, `che_do_chi_phi`, `ty_le.thue_gtgt`) và các dòng thông tin `THAM_SO` A4–A9 (dự án / công trình / hạng mục / loại công trình / địa bàn / thời điểm áp giá).
- **Lỗi trong `Ts`:** ô N14 có giá trị `#N/A` — công thức `=ADDRESS(MATCH(V2,V4:V20,0)+1+3,64,1,1)&":"&ADDRESS(MATCH(V2,V4:V20,0)+VLOOKUP(V2,V4:AC20,6,0)+3,64,1,1)` tra cứu thất bại (không tìm thấy V2 trong V4:V20). `soat_file_excel.py` bắt được lỗi này ở E1 khi chạy với `--ca-sheet-an` (xem mục 11).

## 6. `DMTL` (GXD) ↔ `bang_ty_le_*.json` (skill)

- GXD `DMTL`: "BẢNG TÍNH NỘI SUY CÁC ĐỊNH MỨC TỶ LỆ" — 1.319 dòng, các bảng nội suy theo loại công trình và quy mô (chi phí XD và thiết bị chưa thuế, đơn vị tỷ đồng). `Ts` N38/N39/N41 tra cứu từ đây qua named range `CF_VLHSDMTL`.
- Skill: `data/bang_ty_le_tt36_2026.json` (Bảng 3.x PL III TT 36) và `data/bang_ty_le_tt40_2026.json` (PL II TT 40). Tra cứu bằng lệnh `dutoan.py ty-le` theo loại/quy mô công trình.
- **Lưu ý từ kết quả soát (mục 11):** `DMTL` có 400 ô số lưu dạng chữ (E4) — các giá trị tỷ lệ như `0,668`, `0,503`… trong bảng nội suy (từ dòng 1026) được lưu dạng text với dấu phẩy thập phân. Việc các ô text này có ảnh hưởng đến `VLOOKUP` của `Ts` hay không là `[CHƯA ĐỐI CHIẾU]` (giá trị đã tính ở `Ts` N38–N42 vẫn là số — 0,062 / 0,06 / 0,08 / 0,02 / 0,011 — nên ít nhất các tra cứu đang dùng vẫn ra số).

## 7. `TH vat tu XD` (GXD) ↔ `TH_VT` (skill) — khác mục đích

| | GXD `TH vat tu XD` (16 cột A–P) | Skill `TH_VT` (7 cột) |
|---|---|---|
| Mục đích | **BẢNG TỔNG HỢP VÀ TÍNH CHÊNH LỆCH VẬT TƯ** — phục vụ điều chỉnh/bù giá | Tổng hợp hao phí × giá, đối chiếu với `DT_CT` |
| Cột chính | STT, MSVT, Tên vật tư, ĐVT, KL, **Giá vật tư gốc [6]**, **Giá vật tư tại thời điểm lập [7]**, Chênh lệch `[8]=[7]-[6]`, Thành tiền chênh lệch `[9]=[5]*[8]`, Thành tiền `[10]=[5]*[7]`, Tỷ trọng trong VL/NC/MTC, Tỷ trọng trong CP trực tiếp, Nguồn, KL/Chênh lệch/Thành tiền "vật tư khác" | Mã TN, Tên tài nguyên, ĐVT, Loại, Tổng hao phí (`=SUMIF(HP_CT…)`), Đơn giá (tham chiếu `GIA_TN`), Thành tiền |
| Khớp được | MSVT ↔ Mã TN; Tên; ĐVT; KL ↔ Tổng hao phí; Giá tại thời điểm lập ↔ Đơn giá; Thành tiền | — |
| Thiếu ở skill | **Khái niệm "giá gốc"** (`gia_tai_nguyen.csv` chỉ có 1 đơn giá cho mỗi (mã TN, vùng)); không có cột chênh lệch, không có "vật tư khác" | Xem đánh giá ở mục 14.2 |

Sheet này **không có dòng dữ liệu** trong file mẫu (dòng 7 trở đi trống), nên công thức `[8]`, `[9]`, `[10]` chỉ mới đối chiếu ở mức chỉ số cột, chưa đối chiếu công thức thật từng dòng.

## 8. `Nhan cong XD` (GXD) ↔ `GIA_TN` (skill, phần NC) — skill không tính ĐG NC

GXD `Nhan cong XD` (8 cột A–H, tiêu đề dòng 5, chỉ số dòng 7, **không có dòng dữ liệu**):

| Cột | Nội dung | Công thức |
|---|---|---|
| A | STT `[1]` | — |
| B | MSVT `[1']` | — |
| C | LOẠI NHÂN CÔNG `[1'']` | — |
| D | CẤP BẬC NHÂN CÔNG `[2]` | — |
| E | HỆ SỐ CẤP BẬC (HiCB) `[3]` | — |
| F | HỆ SỐ CẤP BẬC BÌNH QUÂN (HjCB) `[3']` | — |
| G | ĐGNCXD BÌNH QUÂN (GjNCXD) (đ/ngày công) `[4]` | — |
| H | ĐƠN GIÁ NHÂN CÔNG XÂY DỰNG (GiNCXD) (đ/ngày công) | `[5]=[4]*[3]/[3']` |

GXD **tính** đơn giá nhân công theo cấp bậc từ đơn giá bình quân: `GiNCXD = GjNCXD × HiCB / HjCB`. Skill **không tính** ĐG NC — lấy giá NC theo nhóm lao động từ `gia_tai_nguyen.csv` / `data/nhan-cong/` (giá chuyển đổi theo nhóm, HN/HY/HP) và đưa vào `GIA_TN`.

Mapping: `GjNCXD` ↔ giá NC nhóm trong `GIA_TN` (cùng vai trò "đơn giá nhân công bình quân của nhóm"); `GiNCXD` theo cấp bậc ↔ **không có tương đương trong skill** (skill dùng nhóm lao động TT 37, không dùng cấp bậc). Nếu v2.0 muốn đối chiếu được với bảng này thì cần thêm bước "tính ĐG NC theo cấp bậc" hoặc ít nhất ghi rõ mapping trên trong tài liệu chuyển đổi. Căn cứ: TT 37/2026 PL III (giá NC theo nhóm lao động) — skill đã có `references/chuan-bi-du-lieu.md` và `data/nhan-cong/`.

## 9. `Gia ca may XD` (GXD) — skill hoàn toàn không có

GXD `Gia ca may XD` (40 cột A–AN, tiêu đề dòng 5–7, **không có dòng dữ liệu**):

| Nhóm cột | Nội dung |
|---|---|
| A–C | STT `[1]`, MSVT `[2]`, LOẠI MÁY, THIẾT BỊ `[3]` |
| D | SỐ CA / NĂM `[4]` |
| E | HAO PHÍ CA MÁY |
| F–I | ĐỊNH MỨC KHẤU HAO, SỬA CHỮA, CHI PHÍ KHÁC / NĂM (%/GIÁ TÍNH KH): Khấu hao `[5]`, Tỷ lệ thu hồi `[6]`, Sửa chữa `[7]`, CP khác `[8]` |
| J–K | ĐỊNH MỨC TIÊU HAO NHIÊN LIỆU, NĂNG LƯỢNG 1 CA `[9]` |
| L | HỆ SỐ NHIÊN LIỆU PHỤ `[10]` |
| M | TỔNG HAO PHÍ NHIÊN LIỆU |
| N | CHÊNH LỆCH CHI PHÍ MTC DO CHÊNH LỆCH GIÁ NLNL |
| O | THÀNH PHẦN CẤP BẬC THỢ ĐIỀU KHIỂN MÁY `[11]` |
| P | NGUYÊN GIÁ (GIÁ TÍNH KHẤU HAO) `[12]` |
| Q–V | CHI PHÍ KHẤU HAO (CKH) `[13]`, CHI PHÍ SỬA CHỮA (CSC) `[14]`, CHI PHÍ NHIÊN LIỆU, NĂNG LƯỢNG (CNL) `[15]`, CHI PHÍ NHÂN CÔNG (CNC) `[16]`, CHI PHÍ KHÁC (CCPK) `[17]`, **GIÁ CA MÁY (CCM)** `[18]` |
| Z–AJ | CHI PHÍ NLNL TẠI THỜI ĐIỂM GỐC, CHI PHÍ TIỀN LƯƠNG TẠI THỜI ĐIỂM GỐC, GIÁ CA MÁY GỐC, CHI PHÍ NLNL/TIỀN LƯƠNG TẠI THỜI ĐIỂM ĐIỀU CHỈNH, **GIÁ CA MÁY ĐIỀU CHỈNH (CCMĐC)** `[18]` |

Đây là bảng **tính giá ca máy từ đầu** theo PL IV TT 37/2026: `CCM = CKH + CSC + CNL + CNC + CCPK`, kèm điều chỉnh theo giá nhiên liệu và tiền lương tại thời điểm. Skill không tính giá ca máy — lấy giá ca máy từ bảng giá công bố của Sở XD qua `GIA_TN` (cột E "Đơn giá"). Đây là lỗ hổng chức năng lớn nhất so với GXD — xem đánh giá ở mục 14.1.

## 10. `Don gia tong hop` (GXD) ↔ chế độ mã `TG` (skill)

GXD `Don gia tong hop` (32 cột A–AF, demo 1 khối "Công tác tổng hợp 1", mã TH1, giá trị 0):

| Nhóm cột | Nội dung |
|---|---|
| C–H | STT, MÃ VỮA, MH ĐỊNH MỨC, MH ĐƠN GIÁ, MSVT, THÀNH PHẦN CÔNG VIỆC |
| I–K | ĐƠN VỊ, KHỐI LƯỢNG, HAO PHÍ ĐỊNH MỨC, GIÁ VẬT TƯ |
| L | HỆ SỐ |
| M–R | Kvlc, Kvlp, Knc1, Knc2, Knc3, Km |
| S–V | Thành tiền Vật liệu, Vật liệu phụ, Nhân công, Máy |
| W–AF | TỔNG CỘNG, CHI PHÍ CHUNG, TN CT TÍNH TRƯỚC, ĐƠN GIÁ XD TRƯỚC THUẾ, THUẾ GTGT, ĐƠN GIÁ XD SAU THUẾ, CHI PHÍ DỰ PHÒNG, **ĐƠN GIÁ THẦU** |

GXD tính cho mỗi mã TH một đơn giá đầy đủ: từ hao phí thành phần → tổng cộng → chi phí chung → thu nhập chịu thuế → đơn giá trước thuế → GTGT → sau thuế → dự phòng → đơn giá thầu. Skill có chế độ mã `TG` (đơn giá trọn gói): một dòng trong `khoi_luong.csv` với `don_gia_tron_goi`, gộp vào chi phí vật liệu trong `DT_CT`/`PT_DG` (theo PL III TT 36/2026; xem `SKILL.md` mục TG và `xuat_excel.py`). **Khác biệt:** skill không có bảng đơn giá tổng hợp riêng, và không lưu thành phần cấu thành của một mã TG (TG chỉ là một con số trọn gói, không có danh sách các công tác con). Xem đánh giá ở mục 14.3. (GXD `Config` có cờ `CF_TDGTH` = "Tính đơn giá tổng hợp".)

## 11. Kiểm chứng `soat_file_excel.py` trên file mẫu

Lệnh chạy (ngày 16/11/2026, không sửa file mẫu):

```bash
python3 scripts/soat_file_excel.py ~/workspace/user/files/DutoanGXD1.xlsm --ra /tmp/soat_gxd.md
python3 scripts/soat_file_excel.py ~/workspace/user/files/DutoanGXD1.xlsm --ca-sheet-an --ra /tmp/soat_gxd_all.md
```

File có 61 sheet (26 hiển thị, 35 ẩn). Script đọc được toàn bộ (chỉ cảnh báo openpyxl về print area của các defined name — không ảnh hưởng kết quả).

### 11.1. Kết quả — chạy mặc định (không `--ca-sheet-an`)

| Mục | Kết quả |
|---|---|
| E1 · Ô lỗi (1) | `BC tham tra`: #REF! × 2 (AA2, AA3) |
| E4 · Số lưu dạng chữ (4) | `DMTL`: 400 ô (vd. D1026…); `BC tham tra`: 2 ô (C23, C35); `TH DTXD`: 6 ô (B8, B9, B13, B14, B27, B28); `THCP thiet bi`: 7 ô (B7–B10, B17) |
| E5 · Số nhập tay giữa công thức (1) | `DMTL` cột Q: 3 số nhập tay giữa 46 công thức (Q444, Q450, Q451) |
| E6 · Sheet ẩn (6) | `Config` 17 ô lỗi; `Ts` 1; `BC tham dinh` 2; `TH gia du thau` 2; `Tai lieu` 1; `Dich thuat` 1 — **chỉ đếm số lượng, không liệt kê tọa độ** |
| E7 · Văn bản hết hiệu lực (1) | `DMTL`!B952: trích TT 60/2025/TT-BXD |
| E2, E3, E8, E9 | Không phát hiện |

### 11.2. Kết quả — chạy với `--ca-sheet-an`

| Mục | Kết quả |
|---|---|
| E1 · Ô lỗi (7) | `Config`: #REF! × 17 (vd. AB1, AE1, AG1, AH1, AT1, AZ1); `Ts`: #N/A × 1 (N14); `BC tham dinh`: #REF! × 2 (AA2, AA3); `BC tham tra`: #REF! × 2 (AA2, AA3); `TH gia du thau`: #REF! × 2 (L30, L31); `Tai lieu`: #NAME? × 1 (A2); `Dich thuat`: #VALUE! × 1 (B5) |
| E4 · Số lưu dạng chữ (5) | Thêm `TH gia du thau`: 2 ô (C28, C29) so với chạy mặc định |
| E5 · Số nhập tay giữa công thức (3) | Thêm `TMDT-SVDT` cột E: 1 số giữa 59 công thức (E18); `TH gia du thau` cột M: 3 số giữa 16 công thức (M28, M29, M31) |
| E7 · Văn bản hết hiệu lực (2) | Thêm `TMDT-SVDT`!M141: trích NĐ 10/2021/NĐ-CP |
| E2, E3, E8, E9 | Không phát hiện |

### 11.3. (a) Các ô `#REF!` ở sheet `Config` — bắt được, nhưng tọa độ chỉ có khi dùng cờ

17 ô `#REF!` trong `Config` (đã kiểm chứng bằng đọc công thức thô, toàn bộ ở dòng 1–2):

- `='THCP xay dung'!#REF!` — AB1, AE1, AG1, AH1, AB2, AE2, AG2, AH2 (8 ô, tham chiếu tới `THCP xay dung`).
- `='THCP Lap dat'!#REF!` — AT1, AZ1, BA1, AP2, AT2, AU2, AW2, AZ2, BA2 (9 ô, tham chiếu tới `THCP Lap dat`).

Chạy mặc định: E6 chỉ báo "`Config` có 17 ô lỗi" mà **không liệt kê tọa độ**; muốn biết ô nào phải chạy thêm `--ca-sheet-an`. Đây là điểm cần cải thiện ở Giai đoạn 5 (xem mục 15): E6 nên liệt kê tối đa 6 tọa độ mẫu như E1, vì `Config` là sheet ẩn nhưng lại là sheet cấu hình quan trọng nhất của file GXD.

### 11.4. (b) Công thức sai ở bảng 2 sheet `THCP xay dung` — KHÔNG bắt được

Ba lỗi ở mục 4.1 đều **không xuất hiện** trong cả hai lần chạy:

| Lỗi | Vì sao script bỏ sót |
|---|---|
| D38 `=SUM(D39:D41)` cộng nhầm GT+C+TT thay vì VL+NC+M | Script chỉ kiểm tra **giá trị đã tính** có phải mã lỗi (`#REF!`, `#VALUE!`…) hay không; giá trị đã tính của D38 là 0 (bảng trống) nên không bị coi là lỗi. Script **không đối chiếu công thức với nhãn/cách tính** của dòng. |
| Dòng GT ở bảng 2 ghi `C+LT+TT` nhưng công thức `=D11` (GT = C+TT, không có LT) | Như trên — nhãn (cột C) và công thức (cột D) không được đối chiếu với nhau. |
| Dòng LT ở bảng 2 (D46) trống, không có công thức | Script không có kiểm tra "ô giá trị trống trong khi các dòng kề có công thức". E5 chỉ phát hiện **số nhập tay** giữa các công thức, không phát hiện **ô trống** giữa các công thức. |

Kết luận: `soat_file_excel.py` bắt được lỗi **giá trị** (ô lỗi, số dạng chữ, số nhập tay, văn bản hết hiệu lực) nhưng **không bắt được lỗi logic công thức** (cộng sai phạm vi, nhãn sai công thức, thiếu công thức). Các lỗi logic chỉ phát hiện được bằng đọc công thức thô và đối chiếu với nhãn — đúng như cách phát hiện ra 3 lỗi trên. Đề xuất kiểm tra mới ở mục 15 (E10).

Lưu ý thêm: E4 bắt 400 ô số dạng chữ trong `DMTL` (giá trị tỷ lệ như `0,668` lưu dạng text, dấu phẩy thập phân, từ dòng 1026). Đây là phát hiện đúng về định dạng ô, nhưng ảnh hưởng thực tế đến tra cứu `VLOOKUP` của `Ts` là `[CHƯA ĐỐI CHIẾU]` (xem mục 6).

## 12. Kiểm chứng `nhap_du_toan_excel.py` trên file mẫu

Lệnh chạy (ngày 16/11/2026, ghi ra thư mục tạm `/tmp/nhap-gxd-test2`, không sửa file mẫu):

```bash
python3 scripts/nhap_du_toan_excel.py --file ~/workspace/user/files/DutoanGXD1.xlsm \
  --dgct "Don gia XD" --dt "Du toan XD" --ra /tmp/nhap-gxd-test2
```

### 12.1. Kết quả — chạy "thành công" nhưng bộ dữ liệu rỗng, rồi dừng lỗi ở bước cuối

- **Thoát với mã lỗi 1.** Thông báo lỗi duy nhất trên stderr: `config: thiếu ty_le.chi_phi_chung.gia_tri`.
- **Không có file `bao_cao_nhap.md`** — báo cáo nhập (đáng lẽ giải thích chuyện gì đã xảy ra) không được ghi, vì lệnh dừng ở bước đối chiếu đơn giá cuối cùng (`nap_config` gọi `sys.exit`) **trước khi** ghi báo cáo. Người dùng chỉ còn 4 file rỗng + 1 dòng lỗi khó hiểu.
- 4 file đã ghi đều rỗng (chỉ có dòng tiêu đề): `dinh_muc.csv` (90 byte), `gia_tai_nguyen.csv` (78 byte), `khoi_luong.csv` (156 byte), `config_du_toan.json` (1.554 byte).

### 12.2. Vì sao rỗng — mapping cột bị lệch

| Bước | Chuyện gì xảy ra | Nguyên nhân |
|---|---|---|
| Đọc `Don gia XD` (doc_dgct) | Tìm được dòng tiêu đề ("Thành phần hao phí" có trong tiêu đề cột G) nhưng **0 khối đơn giá** | Sheet trống, không có dòng dữ liệu nào dưới tiêu đề. Ngoài ra bố cục GXD không có các dòng mục a) Vật liệu / b) Nhân công / c) Máy thi công mà script dựa vào để phân loại hao phí. |
| Vùng giá | Phát hiện **1 vùng giả: V1 = "[8]"** | Script lấy tên vùng từ dòng ngay dưới tiêu đề (dòng 6) — ở GXD đó là dòng chỉ số `[1]…[15]`, không phải tên vùng. Cột "Đơn giá" đầu tiên script tìm được là cột K (ĐƠN GIÁ VẬT TƯ), cột "Hệ số" là cột L — nên `n_vung = cH - cF = 1`, tên vùng đọc từ ô K6 trống → rơi vào chỉ số `[8]` ở dòng 6? (thực tế tên V1 đọc được là `"[8]"` — giá trị ở hàng chỉ số). |
| Đọc `Du toan XD` (doc_dt) | **0 công tác**; tạo ra **8 "đoạn" giả D1–D8** | Script coi mọi cột giữa cột "Khối lượng" (H) và cột "Đơn giá" đầu tiên (P) là cột đoạn: H (KHỐI LƯỢNG), I (YCKT), J (Kvlc), K (Kvlp), L (Knc1), M (Knc2), N (Knc3), O (Km). Tức là chính cột KL và 7 cột hệ số/yêu cầu kỹ thuật bị hiểu nhầm thành 8 đoạn. |
| Ghi config | `ty_le` toàn `null` (không tìm được tỷ lệ nào trong `Don gia XD` trống) | — |
| Đối chiếu đơn giá | `nap_config` (`dutoan_core.py:436`) dừng chương trình vì `ty_le.chi_phi_chung.gia_tri` là `null` | Lỗi dừng toàn bộ tiến trình, kể cả việc ghi `bao_cao_nhap.md`. |

### 12.3. Các cột GXD map được / không map được về `khoi_luong.csv` (theo logic hiện tại của script)

| Cột GXD trong `Du toan XD` | Map được không | Ghi chú |
|---|---|---|
| B STT | Có (qua cột TT/STT đơn giá) — nhưng script cần cột "STT đơn giá" riêng, GXD không có | Script lấy `cB = 2` mặc định khi không tìm thấy "stt don gia" — trùng cột STT của GXD nên tạm đúng. |
| D MÃ HIỆU ĐỊNH MỨC | Có (→ `ma_hieu`) | Script tìm "ma hieu" — khớp cột D. |
| E MÃ HIỆU ĐƠN GIÁ | Không | Không có cột đích; nếu D ≠ E thì mất thông tin. |
| F NỘI DUNG CÔNG VIỆC | **Không** — script tìm "hang muc cong viec" (không có trong GXD) nên rơi về cột E (Mã hiệu đơn giá) làm tên công tác | Lỗi map âm thầm: tên công tác sẽ bị ghi bằng mã đơn giá. |
| G ĐƠN VỊ | Có (→ `don_vi`) | — |
| H KHỐI LƯỢNG | **Không** — bị hiểu nhầm thành "đoạn D1" | Xem mục 12.2. |
| I YCKT | Không | Không có cột đích trong `khoi_luong.csv`. |
| J–O (Kvlc/Kvlp/Knc1-3/Km) | **Không** — bị hiểu nhầm thành đoạn D2–D8 | Xem mục 12.2. `Km` (cột O) về nguyên tắc map được vào `he_so_m`, nhưng script không tới được bước đó vì coi nó là đoạn. |
| P–S ĐƠN GIÁ VL/VLP/NC/M | Không | Script chỉ đọc 1 cột đơn giá theo vùng từ `Don gia XD`, không đọc ĐG từ `Du toan XD`. |
| Z–AF diễn giải KL | Không | Không có cột đích; `dien_giai` trong `khoi_luong.csv` đang là chuỗi tự do — có thể ghép từ Z–AF (xem mục 2). |
| AG GHI CHÚ | Không | Không có cột đích. |

Kết luận: `nhap_du_toan_excel.py` hiện tại được viết cho bố cục `DGCT`/`DT` của chính skill (hoặc file Excel theo mẫu đơn giá chi tiết cũ), **không đọc được bố cục GXD**. Muốn nhập file GXD cần thêm chế độ `--kieu gxd` (xem đề xuất mục 15) và cần file GXD đã điền dữ liệu để kiểm chứng (file mẫu hiện tại trống nên không kiểm chứng được bước map số).

## 13. Đối chiếu Word — chuẩn Styles GXD

Nguồn: `Gxd.vn-Word-trong-van-phong-xay-dung-Chuan-Styles-GXD.pdf` (77 trang, Công ty CP Giá Xây Dựng) — đã trích text tại `~/workspace/DT-ver2.0-work/refs-pdf/Gxd.vn-Word-trong-van-phong-xay-dung-Chuan-Styles-GXD.txt` (2.069 dòng). Sách là **sách hướng dẫn dùng Word**, không phải tài liệu kỹ thuật định mức: giá trị nằm ở hệ thống Style thống nhất và quy trình soạn thảo, không ở nội dung chuyên môn.

### 13.1. Hệ thống Style GXD (tên Style trong sách)

| Style | Dùng cho | Ghi chú |
|---|---|---|
| `A Noi dung gxd.vn` | Nội dung văn bản thường (style dùng nhiều nhất) | Đặt tên bắt đầu bằng "A" để Word sắp xếp lên đầu panel Styles (theo alphabet), tiện chọn. Áp cho toàn bộ văn bản (Ctrl + A) rồi mới đi chi tiết. |
| `Heading 1` – `Heading 4` | Đề mục các cấp | Dùng để tạo mục lục tự động (chèn và cập nhật mục lục trong vài giây) và điều hướng bằng Navigation Pane (Promote/Demote). |
| `Gxd.vn Noi dung Ban can Giua Dam B` | Nội dung bảng, căn giữa, đậm | Áp cho nội dung ô bảng. |
| `Style Hình ảnh` | Ảnh trong văn bản | Áp cho tất cả ảnh để thống nhất trình bày. |
| `GXD Danh list số` | Danh sách đánh số | Thay cho nút Numbering mặc định. |
| Các Style tiêu đề / nơi nhận / chữ ký | Phần tiêu đề văn bản (quốc hiệu, tên cơ quan), phần nơi nhận, chữ ký | Sách có bài tập trình bày riêng (chương 7). |

Nền tảng: file mẫu `Normal.dotm` của GXD (chứa sẵn các Style trên) — sách hướng dẫn tải tại `giaxaydung.vn/threads/mau-Word-chuan-Styles-GXD.97639` (link dự phòng `bom.to/mau-chuan-styles-GXD`, `bom.to/normal-chuan-Styles-GXD`), copy đè lên `Normal.dotm` của Word. **Lưu ý bản quyền:** `Normal.dotm` là file mẫu của Công ty CP Giá Xây Dựng — skill **không copy file này vào repo**. Skill chỉ định nghĩa lại các Style tương đương (cùng tên gọi và cấu trúc phân cấp) bằng `python-docx` trong template của mình, với thông số định dạng theo quy định văn bản hành chính hiện hành (cần đối chiếu lại, không lấy số đo từ sách cũ mà không kiểm chứng).

Các kỹ thuật trong sách có ích cho template Word của skill: lặp lại tiêu đề bảng sang trang mới, header/footer, chèn/cập nhật mục lục tự động, chèn hình ảnh (logo) vào biên bản, khái niệm CDE / teamwork / đám mây khi làm việc nhóm (chương 6).

### 13.2. Các mẫu Word cần tạo (chỉ liệt kê — chưa tạo file `.docx`)

| # | Mẫu | Nội dung chính | Style dùng |
|---|---|---|---|
| W1 | Thuyết minh dự toán / Báo cáo thẩm tra dự toán | Bìa, căn cứ pháp lý, tóm tắt TMĐT/dự toán, bảng tổng hợp (dán từ Excel skill), kết luận thẩm tra, chữ ký | Heading 1–4, `A Noi dung gxd.vn`, bảng (`Gxd.vn Noi dung Ban can Giua Dam B`), mục lục tự động |
| W2 | Biên bản nghiệm thu / biên bản hiện trường | Tiêu đề, thành phần, nội dung, kết luận, chữ ký các bên, logo | Tiêu đề/nơi nhận/chữ ký, `A Noi dung gxd.vn`, bảng |
| W3 | Tờ trình / Quyết định / Công văn (khung chung) | Quốc hiệu, tên cơ quan, số/ký hiệu, trích yếu, nội dung, nơi nhận, chữ ký | Tiêu đề/nơi nhận/chữ ký, `A Noi dung gxd.vn`, `GXD Danh list số` |

Chưa tạo file `.docx` trong Giai đoạn 4 vì: (a) nội dung thuyết minh/thẩm tra phụ thuộc kết quả Giai đoạn 1–2 (căn cứ pháp lý, dữ liệu TT 38); (b) cần chốt công cụ tạo (đề xuất `python-docx`, định nghĩa Style trong code, không phụ thuộc file `Normal.dotm` của GXD). Đề xuất đưa vào Giai đoạn 5 (xem mục 15).

## 14. Ba chức năng skill còn thiếu so với GXD — đánh giá từng chức năng

### 14.1. Tính giá ca máy theo PL IV TT 37/2026

- **GXD làm gì:** sheet `Gia ca may XD` (40 cột, mục 9): tính `CCM = CKH + CSC + CNL + CNC + CCPK` từ nguyên giá, định mức khấu hao/sửa chữa/chi phí khác %/năm, định mức tiêu hao nhiên liệu 1 ca, hệ số nhiên liệu phụ, thành phần cấp bậc thợ lái máy, số ca/năm; kèm giá điều chỉnh `CCMĐC` theo giá nhiên liệu và tiền lương tại thời điểm.
- **Skill hiện tại:** không có module nào. Giá ca máy lấy từ bảng giá công bố của Sở XD qua `gia_tai_nguyen.csv` (mã TN = tên máy, `don_gia` = giá công bố). Các chỗ nhắc đến PL IV TT 37 trong skill chỉ là ghi chú: `references/can-cu-phap-ly.md` (CV 14502/SXD-KTXD: "ca máy theo PL IV TT 37, nhiên liệu Petrolimex"), `data/nhan-cong/README.md`, `references/du-toan-khao-sat.md` (công thức xe khảo sát nói chung). **Không có file dữ liệu PL IV TT 37 nào trong skill** (không có bảng định mức khấu hao/sửa chữa/tiêu hao nhiên liệu theo máy).
- **Cần thêm gì:**
  - File dữ liệu mới `data/gia-ca-may/dinh_muc_ca_may_tt37.csv` (mã máy, tên máy, nguyên giá tham chiếu, định mức khấu hao/sửa chữa/chi phí khác %/năm, định mức tiêu hao NLNL 1 ca, hệ số NL phụ, cấp bậc thợ lái) — trích từ PL IV TT 37/2026, ghi rõ `[CHƯA ĐỐI CHIẾU]` cho đến khi trích xong.
  - Script mới `scripts/gia_ca_may.py` (tính CKH/CSC/CNL/CNC/CCPK/CCM/CCMĐC; đầu vào: bảng định mức trên + giá nhiên liệu Petrolimex tại thời điểm + giá NC nhóm lái xe từ `data/nhan-cong/`; đầu ra: `gia_ca_may.csv` dùng được làm `gia_tai_nguyen.csv` cho loại M).
  - Tài liệu mới `references/phuong-phap-gia-ca-may.md` (công thức PL IV TT 37, ví dụ tính tay 2–3 máy đối chiếu với `Gia ca may XD`).
- **Đề xuất: đưa vào v2.0** (script + tài liệu + file dữ liệu mẫu với 2–3 máy làm ví dụ kiểm chứng; bảng đầy đủ ~908 máy để v2.1, sau khi trích xong PL IV). Lý do: đây là lỗ hổng lớn nhất so với GXD và ảnh hưởng trực tiếp đến mọi chi phí M; công thức PL IV là chuẩn, kiểm chứng được từ văn bản TT 37 mà không cần file GXD đã điền.

### 14.2. Bảng chênh lệch vật tư gốc vs hiện tại

- **GXD làm gì:** sheet `TH vat tu XD` (mục 7): chênh lệch `[8]=[7]-[6]`, thành tiền chênh lệch `[9]=[5]*[8]`, thành tiền `[10]=[5]*[7]`, tỷ trọng, cột "vật tư khác".
- **Skill hiện tại:** `TH_VT` chỉ tổng hợp hao phí × 1 đơn giá; `gia_tai_nguyen.csv` không có khái niệm "giá gốc".
- **Cần thêm gì:**
  - Thêm cột `don_gia_goc` (không bắt buộc) vào `gia_tai_nguyen.csv` — giá gốc là giá trong hồ sơ gốc/hợp đồng, do người dùng nhập, không phải giá công bố.
  - Thêm sheet mới `CL_VT` trong `xuat_excel.py` (chỉ xuất khi có `don_gia_goc`): MSVT, tên, ĐVT, KL (từ `HP_CT`), giá gốc, giá hiện tại, chênh lệch, thành tiền chênh lệch, thành tiền, tỷ trọng — công thức theo đúng chỉ số cột của GXD.
  - Cập nhật `references/mau-bieu-excel.md` (mô tả sheet `CL_VT`) và `references/chuan-bi-du-lieu.md` (cách nhập giá gốc).
- **Đề xuất: đưa vào v2.0** (sheet tùy chọn, chỉ hiện khi có dữ liệu giá gốc). Lý do: thay đổi nhỏ, công thức đã rõ từ GXD, phục vụ trực tiếp nhu cầu bù giá/điều chỉnh giá — không cần dữ liệu mới ngoài giá gốc do người dùng cung cấp.

### 14.3. Bảng đơn giá tổng hợp (mã TH)

- **GXD làm gì:** sheet `Don gia tong hop` (mục 10): mỗi mã TH có thành phần công việc, hao phí, hệ số Kvlc/Kvlp/Knc1-3/Km, thành tiền phần, rồi cộng chi phí chung → TL → đơn giá trước thuế → GTGT → sau thuế → dự phòng → đơn giá thầu.
- **Skill hiện tại:** chế độ mã `TG` (đơn giá trọn gói) — một con số, gộp vào VL, không lưu thành phần cấu thành, không có sheet riêng. `DGCT` (`doan_vung`) đã tính T/C/TT/GT/TL/G/GTGT/Gxd cho từng mã thường — gần với TH nhất trong skill hiện tại.
- **Cần thêm gì:**
  - Mô hình dữ liệu mới: file `data/mau/don_gia_tong_hop.mau.csv` (mã TH, mã công tác con, KL con, ghi chú) — vì hiện tại skill không có chỗ nào lưu "mã TH gồm những công tác nào".
  - Sheet mới `DG_TH` trong `xuat_excel.py` (hoặc mở rộng `DGCT`): liệt kê mã TH, thành phần, hao phí, thành tiền phần, C/TL/GTGT/dự phòng, đơn giá thầu — theo đúng cột của GXD (mục 10).
  - Cập nhật `references/mau-bieu-excel.md` và `SKILL.md` (mục TG).
- **Đề xuất: ghi "ngoài phạm vi v2.0" trong README, làm ở v2.1.** Lý do: chưa có mô hình dữ liệu cho thành phần mã TH — tự bịa mô hình lúc này dễ lệch với ngữ nghĩa TH của GXD (file demo TH1 trống, giá trị 0, không đủ để suy ra quy tắc gộp). Trong v2.0 chỉ ghi thiết kế mô hình + bảng mapping ở file này và trong `README.md` mục "Ngoài phạm vi".

## 15. Đề xuất cho Giai đoạn 5 (chỉ liệt kê — chưa sửa code)

### 15.1. `scripts/soat_file_excel.py`

| # | Đề xuất | Căn cứ (mục) |
|---|---|---|
| S-1 | **E6 liệt kê tọa độ mẫu** (tối đa 6 ô/sheet như E1) thay vì chỉ đếm số lượng — áp dụng cho cả sheet ẩn | 11.3: `Config` 17 ô `#REF!` chỉ hiện số lượng khi chạy mặc định |
| S-2 | **Kiểm tra mới E10 — công thức tổng hợp sai phạm vi:** trong bảng tổng hợp, đối chiếu công thức `SUM(phạm vi)` với nhãn/cách tính của dòng (vd. nhãn `VL+NC+M` nhưng `SUM` bao phủ các dòng nhãn GT/C/TT) và với cột "Cách tính" | 4.1 / 11.4: D38 `=SUM(D39:D41)` |
| S-3 | **Kiểm tra mới E11 — ô giá trị trống giữa các công thức:** trong bảng tổng hợp, dòng có nhãn + cột "Cách tính" nhưng ô giá trị trống trong khi các dòng kề có công thức | 4.1 / 11.4: D46 (LT) trống |
| S-4 | **Kiểm tra mới E12 — nhãn mâu thuẫn công thức:** cột "Cách tính" ghi một công thức, cột giá trị tham chiếu sang bảng khác không chứa thành phần đó (vd. GT ghi `C+LT+TT` nhưng `=D11` với GT = C+TT) | 4.1: D39 |
| S-5 | E4: phân biệt số dạng chữ trong **bảng tra cứu tỷ lệ** (dấu phẩy thập phân kiểu Việt Nam) với số dạng chữ trong bảng dữ liệu — báo riêng để người soát biết có cần chuyển đổi khi `VLOOKUP` hay không | 6 / 11.1: `DMTL` 400 ô |
| S-6 | Thêm file mẫu `DutoanGXD1.xlsm` làm **fixture kiểm thử** (copy vào `tests/fixtures/`, giữ bản gốc ở `~/workspace/user/files/`): test soat phải bắt được E1 ở `Config` (17 ô), E7 ở `DMTL`!B952 và `TMDT-SVDT`!M141, E5 ở `DMTL` cột Q; test E10/E11/E12 phải bắt được D38/D39/D46 sau khi thêm các kiểm tra mới | 11 |

### 15.2. `scripts/nhap_du_toan_excel.py`

| # | Đề xuất | Căn cứ (mục) |
|---|---|---|
| N-1 | **Không để `nap_config` dừng chương trình trước khi ghi báo cáo:** ghi `bao_cao_nhap.md` trước bước đối chiếu đơn giá (hoặc bắt lỗi `SystemExit` ở bước đối chiếu, ghi lỗi vào báo cáo rồi thoát với mã lỗi rõ ràng) | 12.1: báo cáo nhập bị mất khi dừng lỗi |
| N-2 | **Bảng trống thì báo rõ, không tạo bộ dữ liệu rỗng:** nếu 0 khối đơn giá và 0 công tác thì ghi báo cáo "bảng trống — file mẫu, không có dữ liệu để nhập" và thoát mã 0 (hoặc mã riêng cho "không có dữ liệu"), thay vì tạo 4 file rỗng rồi dừng lỗi ở bước sau | 12.1–12.2 |
| N-3 | **Thêm chế độ `--kieu gxd`:** đọc `Don gia XD` (19 cột) + `Du toan XD` (33 cột) theo mapping ở mục 2–3: MSVT → `ma_tn`, MÃ HIỆU ĐM → `ma_hieu`, MÃ VỮA → `cap_phoi`, Kvlc×Kvlp → `he_so_vl`, Km → `he_so_m`, Z–AF → `dien_giai`, AF đối chiếu H, YCKT + Ghi chú → `dien_giai` (kèm cảnh báo mất thông tin) | 12.3 |
| N-4 | Knc1/Knc2/Knc3: **chưa gộp** cho đến khi xác minh được ý nghĩa từng hệ số (cần file GXD đã điền hoặc HDSD) — chế độ `--kieu gxd` phải cảnh báo và giữ nguyên 3 cột trong báo cáo nhập | 2 (mục L/M/N) |
| N-5 | Tên vùng giá: không lấy từ dòng chỉ số `[n]` dưới tiêu đề — lấy từ dòng tiêu đề vùng (nếu có) hoặc yêu cầu người dùng khai báo `--vung` khi tên vùng không đọc được | 12.2: vùng giả V1 = `"[8]"` |
| N-6 | Cột "đoạn": chỉ nhận cột KL khi tiêu đề cột chứa tên đoạn/xã cụ thể, không nhận mọi cột giữa KL và ĐG — tránh hiểu nhầm cột hệ số thành đoạn | 12.2: 8 "đoạn" giả D1–D8 |

### 15.3. `scripts/xuat_excel.py` / `references/mau-bieu-excel.md`

| # | Đề xuất | Căn cứ (mục) |
|---|---|---|
| X-1 | Thêm sheet tùy chọn `CL_VT` (bảng chênh lệch vật tư) + cột `don_gia_goc` trong `gia_tai_nguyen.csv` | 14.2 |
| X-2 | Cập nhật `mau-bieu-excel.md`: mô tả sheet `CL_VT` (khi có) và ghi rõ các cột GXD chưa có tương đương (mã vữa, YCKT, Knc1-3, diễn giải KL dạng số, tổng đơn giá) | 2–3 |
| X-3 | Thiết kế (chỉ viết tài liệu, chưa code): mô hình dữ liệu mã TH + sheet `DG_TH` | 14.3 |

### 15.4. `scripts/gia_ca_may.py` (mới) + tài liệu

| # | Đề xuất | Căn cứ (mục) |
|---|---|---|
| M-1 | Script mới `scripts/gia_ca_may.py` + `references/phuong-phap-gia-ca-may.md` + `data/gia-ca-may/dinh_muc_ca_may_tt37.csv` (mẫu 2–3 máy kiểm chứng trước) | 14.1 |

### 15.5. Mẫu Word (chưa tạo file `.docx`)

| # | Đề xuất | Căn cứ (mục) |
|---|---|---|
| W-1 | Tạo template W1 (Thuyết minh dự toán / Báo cáo thẩm tra) bằng `python-docx`: định nghĩa Style tương đương GXD (Heading 1–4, `A Noi dung gxd.vn`, bảng căn giữa đậm, mục lục tự động) — không copy file `Normal.dotm` của GXD | 13 |
| W-2 | Tạo template W2 (Biên bản nghiệm thu) và W3 (Tờ trình / Quyết định / Công văn) sau W1 | 13.2 |
| W-3 | Ghi rõ trong `README.md`: mẫu Word dùng Style tương đương chuẩn GXD, không phải file `Normal.dotm` gốc | 13.1 |

### 15.6. `README.md` (ghi chú phạm vi)

- Ghi rõ: bảng đơn giá tổng hợp (mã TH) **ngoài phạm vi v2.0** (làm ở v2.1); tính giá ca máy và bảng chênh lệch vật tư là tính năng mới của v2.0 theo mục 14.1–14.2.
- Ghi rõ: `nhap_du_toan_excel.py` đọc được bố cục `DGCT`/`DT` của skill và (sau N-3) bố cục GXD; file GXD trống (template) không nhập được dữ liệu — cần file đã điền.

## 16. Những gì chưa đối chiếu được (không suy đoán)

1. Ý nghĩa từng hệ số Knc1/Knc2/Knc3 trong `Du toan XD` (mục 2) — cần file GXD đã điền dữ liệu hoặc HDSD.
2. Ý nghĩa cột N (HAO PHÍ) và O (HAO PHÍ KHÁC) trong `Don gia XD` (mục 3).
3. Công thức từng dòng dữ liệu trong `Don gia XD` / `TH vat tu XD` / `Nhan cong XD` / `Gia ca may XD` (file mẫu trống, chỉ có tiêu đề).
4. Các ô số dạng chữ trong `DMTL` có ảnh hưởng đến `VLOOKUP` của `Ts` hay không (mục 6).
5. Cách GXD xử lý đa vùng giá trong một bảng dự toán (mục 2, cuối).
6. Thông số định dạng cụ thể của từng Style GXD (cỡ chữ, font, khoảng cách) — sách Word chỉ nêu tên Style và cách dùng, không cho bảng thông số đầy đủ; cần đối chiếu với quy định văn bản hành chính hiện hành khi tạo template W1–W3.
7. File `HDSD` (Google Doc) và các tài liệu trong `Library/` trên Drive GXD chưa đọc được (Google Docs chưa nối) — có thể chứa quy trình GXD làm rõ các mục 1–5 trên.

## Nguồn

- `~/workspace/user/files/DutoanGXD1.xlsm` (687 KB, 61 sheet, template GXD 2026).
- `~/workspace/DT-ver2.0-work/phase2-4-data-gxd.md` mục 4 (đối chiếu 6 sheet, đã kiểm chứng lại các công thức D38/D39/D46 và tọa độ `#REF!` ở `Config` bằng đọc trực tiếp file trong đợt này).
- `~/workspace/DT-ver2.0-work/skill-DT-v2/scripts/xuat_excel.py` (mẫu `bang_3_8`), `xuat_excel_doan.py` (mẫu `doan_vung`), `soat_file_excel.py` (E1–E9), `nhap_du_toan_excel.py`, `dutoan_core.py` (`nap_config`).
- `~/workspace/DT-ver2.0-work/skill-DT-v2/references/mau-bieu-excel.md`, `chuan-bi-du-lieu.md`, `can-cu-phap-ly.md`, `du-toan-khao-sat.md`, `data/nhan-cong/README.md`.
- `~/workspace/DT-ver2.0-work/refs-pdf/Gxd.vn-Word-trong-van-phong-xay-dung-Chuan-Styles-GXD.txt` (77 trang, Công ty CP Giá Xây Dựng).
- Kết quả chạy thật ngày 16/11/2026: `/tmp/soat_gxd.md` (chạy mặc định), `/tmp/soat_gxd_all.md` (chạy `--ca-sheet-an`), `/tmp/nhap-gxd-test2/` (4 file rỗng, thoát mã 1).
