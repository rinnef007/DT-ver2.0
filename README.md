# Skill dự toán xây dựng Việt Nam (`du-toan-xay-dung-vn`)

Skill cho Claude (claude.ai, Claude Code) để **bóc khối lượng, áp mã định mức, lập và thẩm tra dự toán** theo hệ thống văn bản áp dụng từ 01/7/2026, xuất Excel có công thức theo mẫu biểu. AI đề xuất từng bước, người lập xác nhận trước khi đi tiếp.

> Công cụ hỗ trợ lập và soát hồ sơ. Kết quả phải được người có chuyên môn kiểm tra trước khi trình duyệt. Căn cứ pháp lý thay đổi nhanh — xem ngày rà soát trong `references/can-cu-phap-ly.md`.

## Căn cứ

| Văn bản | Dùng cho | Trạng thái trong skill |
|---|---|---|
| NĐ 206/2026/NĐ-CP | Quản lý chi phí ĐTXD | Theo nguồn thứ cấp (chưa đọc nguyên văn) |
| TT 36/2026/TT-BXD (+ đính chính QĐ 1538/QĐ-BXD) | Phương pháp chi phí: Bảng 3.8 chi phí XD, PL V khảo sát, PL VI tư vấn, PL II dự toán | Đã đối chiếu toàn văn; tỷ lệ trong `data/bang_ty_le_tt36_2026.json` |
| TT 37/2026/TT-BXD | Giá nhân công (nhóm nhân công), giá ca máy | Đã đối chiếu |
| TT 38/2026/TT-BXD (bộ phụ lục thay thế CV 9947/BXD-VPB) | Định mức PL I–VI, cấp phối vữa và hao hụt PL VII, QLDA PL VIII | Đã trích thành dữ liệu `data/tt38/` |
| TT 40/2026/TT-BXD | Chi phí bảo trì: bảo dưỡng, sửa chữa trong kế hoạch bảo trì | Đã đối chiếu; tỷ lệ trong `data/bang_ty_le_tt40_2026.json` |

## Cài đặt

- **claude.ai**: tải file `.zip` của thư mục skill lên mục Skills trong phần cài đặt.
- **Claude Code**: giải nén vào `~/.claude/skills/du-toan-xay-dung-vn/`.
- Cần Python 3 và `openpyxl`; LibreOffice để đọc `.xls` và tính lại công thức; `python-docx` để trích phụ lục `.doc/.docx`; `ezdxf` để đo DXF.

## Skill làm được gì

| Việc | Cách làm | Ghi chú |
|---|---|---|
| Bóc khối lượng | Theo `references/do-boc-khoi-luong.md`; đo DXF theo layer: `scripts/boc_kl_dxf.py` | Mỗi dòng có diễn giải và nguồn bản vẽ; người lập duyệt từng hạng mục |
| Áp mã định mức | `dutoan.py tra --tu-khoa "..."` / `--ma` / `--cap-phoi` | 9.136 mã TT 38; hồ sơ sửa chữa tự áp hệ số PL VI mục 3.b; bê tông chọn mác theo cấp phối PL VII |
| Giá tài nguyên | `dutoan.py can-gia` lập danh sách tài nguyên cần giá × từng vùng (`--nhan-cong` điền sẵn giá nhân công theo văn bản Sở XD); `tra --tai-nguyen` dò tên trong danh mục ~2.381 tài nguyên TT 38 | Giá vật liệu, ca máy **không đóng gói** — mỗi hồ sơ lấy công bố kỳ hiện hành; giá nhân công chuyển đổi (HN, HY, HP) có sẵn để điền và đối chiếu |
| Lập dự toán | `dutoan.py tinh` → Excel có công thức sống, làm tròn từng bước nếu cần | 4 chế độ chi phí, 2 mẫu trình bày (dưới đây) |
| Tra tỷ lệ | `dutoan.py ty-le` | QLDA (nội suy, hệ số), quản lý chủ sở hữu TT 40, khảo sát Bảng 5.1–5.3, tư vấn Bảng 6.1, mua sắm thiết bị Bảng 2.3 |
| Tự soát | `dutoan.py soat` — 22 nhóm kiểm tra S01–S22 | Chặn khi thiếu giá, chưa xác nhận khối lượng, mẫu không phù hợp; cảnh báo tỷ lệ sai nấc, hệ số thiếu căn cứ, mã cần đối chiếu… |
| Thẩm tra hồ sơ có sẵn | `soat_file_excel.py` (ô lỗi, liên kết ngoài, sheet ẩn, văn bản hết hiệu lực…); `nhap_du_toan_excel.py` (tính lại từng khối đơn giá, chỉ ra công thức sai); `nhap_ks_excel.py` (nhập hồ sơ khảo sát có sẵn, tính lại theo PL V, chỉ ra chênh lệch, tái lập bằng skill) | Báo cáo chênh lệch kèm căn cứ |
| Tính giá ca máy | `scripts/gia_ca_may.py` theo PL IV TT 37/2026 (CCM = CKH + CSC + CNL + CNC + CCPK, giá chờ đợi, CCMĐC); `references/phuong-phap-gia-ca-may.md` | Mới ở v2.0 — hiện chỉ 3 máy mẫu kiểm chứng tay đến đồng; bảng đủ ~908 máy để v2.1 |
| Chênh lệch vật tư | Sheet `CL_VT` trong file Excel xuất ra (giá gốc vs giá hiện tại) khi nhập `don_gia_goc` trong `gia_tai_nguyen.csv` | Mới ở v2.0 — chỉ mẫu `bang_3_8`; mẫu `doan_vung` chưa có (v2.1) |
| Template Word | `templates/word/` (W1 thuyết minh/thẩm tra, W2 biên bản nghiệm thu, W3 tờ trình/quyết định/công văn); tạo lại: `python scripts/tao_mau_word.py --ra templates/word` | Mới ở v2.0 |

## Phạm vi v2.0 — tính năng mới và việc chưa làm

**Mới ở v2.0** (theo báo cáo đối chiếu GXD, `references/doi-chieu-gxd.md` mục 15):
- Tính giá ca máy từ đầu theo PL IV TT 37/2026 (`scripts/gia_ca_may.py`, 3 máy mẫu kiểm chứng tay).
- Sheet chênh lệch vật tư `CL_VT` khi có giá gốc (`don_gia_goc`).
- `nhap_du_toan_excel.py` đọc được bố cục GXD (`--kieu gxd`); `soat_file_excel.py` thêm kiểm tra
  E10/E11/E12 (công thức tổng hợp sai phạm vi, ô trống giữa công thức, nhãn mâu thuẫn công thức) và
  liệt kê tọa độ ô lỗi ở sheet ẩn.
- 3 template Word W1/W2/W3 (`templates/word/`).

**Ngoài phạm vi v2.0 — làm ở v2.1:**
- **Đơn giá tổng hợp (mã TH):** skill chưa có mô hình dữ liệu cho thành phần mã TH (hiện chỉ có chế
  độ mã `TG` là một con số trọn gói, không lưu thành phần). Thiết kế đã viết ở
  `references/thiet-ke-don-gia-tong-hop.md` (mô hình `don_gia_tong_hop.csv`, sheet `DG_TH`,
  5 câu hỏi mở cần trả lời trước khi code) — code ở v2.1.
- **Bảng giá ca máy đủ:** Mục V PL IV có khoảng 908 máy; v2.0 chỉ làm mẫu 3 máy. Trích đủ và đối
  chiếu từng số với văn bản ở v2.1 (bảng GXD đã xuất có 827 máy, 18 máy chưa có nguyên giá).
- Sheet `CL_VT` cho mẫu `doan_vung` (giá theo nhiều vùng — cần thiết kế riêng).
- Thành phần nhân công vận hành máy ngoài "nhân công vận hành" và "lái xe" (thuyền trưởng, thủy thủ,
  thợ máy…) chưa hỗ trợ trong `gia_ca_may.py` — máy đó được tính thiếu CNC và ghi cảnh báo.

### Chế độ chi phí (`che_do_chi_phi` trong config)

| Chế độ | Áp dụng | Cấu trúc |
|---|---|---|
| `tt36` (mặc định) | Xây dựng mới, cải tạo, sửa chữa lập BCKTKT/dự án | Bảng 3.8 PL III TT 36: C, TT, TL, GTGT, LT = GXDTT × tỷ lệ × (1 + TGTGT) |
| `tt40_bao_duong`, `tt40_sua_chua` | Bảo dưỡng, sửa chữa **trong kế hoạch bảo trì** | TT 40: GT = NC × 66/63/60/56%, TL, LT trên giá trị sau thuế, dự phòng ≤ 5% |
| `tt36_khao_sat` | Dự toán khảo sát, thí nghiệm chuyên ngành | PL V TT 36 (Bảng 5.4): C = NC × 70/65/60%, TT, TL, Cpa/Cbc, LT = (G + GTGT) × 2%, dự phòng ≤ 10% |

### Mẫu trình bày (`mau_xuat`)

- `bang_3_8`: theo mẫu biểu thông tư — tổng hợp (Bảng 3.8 / 5.4 / 2.5 TT 40), dự toán chi tiết, phân tích đơn giá, tổng hợp vật tư. Dùng khi **một vùng giá**.
- `doan_vung`: theo mẫu đơn vị — khối lượng theo đoạn/xã, nhiều vùng giá, đơn giá chi tiết đầy đủ từng mã, bảng tổng hợp kiểu TDT (QLDA, tư vấn, chi phí khác, dự phòng), số tiền bằng chữ.

## Bắt đầu nhanh

```bash
# Xây dựng / sửa chữa — mã TT 38 thật, giá giả
python scripts/dutoan.py tinh --data data/vi-du-tt38 --khoi-luong data/vi-du-tt38/khoi_luong.csv --config data/vi-du-tt38/config_du_toan.json --out thu_tt38.xlsx

# Mẫu đơn vị theo đoạn – vùng giá
python scripts/dutoan.py tinh --data data/vi-du-doan --khoi-luong data/vi-du-doan/khoi_luong.csv --config data/vi-du-doan/config_du_toan.json --out thu_doan.xlsx

# Sửa chữa trong kế hoạch bảo trì (TT 40)
python scripts/dutoan.py tinh --data data/vi-du-tt40 --khoi-luong data/vi-du-tt40/khoi_luong.csv --config data/vi-du-tt40/config_du_toan.json --out thu_tt40.xlsx

# Dự toán khảo sát (PL V TT 36, mẫu đơn vị)
python scripts/dutoan.py tinh --data data/vi-du-khao-sat --khoi-luong data/vi-du-khao-sat/khoi_luong.csv --config data/vi-du-khao-sat/config_du_toan.json --out thu_ks.xlsx

# Lập danh sách tài nguyên cần giá cho một hồ sơ
python scripts/dutoan.py can-gia --data <thư mục hồ sơ> --khoi-luong khoi_luong.csv --config config_du_toan.json --ra can_gia.csv

# Tra định mức, tài nguyên, tỷ lệ
python scripts/dutoan.py tra --tu-khoa "ống nhựa gân xoắn"
python scripts/dutoan.py tra --tai-nguyen "máy lu" --loai M
python scripts/dutoan.py ty-le --bang qlda --loai giao_thong --gia-tri 15 --he-so 0.8
```

Tất cả ví dụ trong `data/vi-du*` dùng **giá giả**, chỉ để chạy thử. Sau khi xuất, tính lại công thức bằng LibreOffice và so với file `*_doi_chieu.json` — phải khớp đến đồng.

## Lập một hồ sơ thật

1. **Cấu hình** (`config_du_toan.json`, mẫu tại `data/mau/`): công trình, loại công trình, chế độ chi phí, quy mô để tra nấc tỷ lệ, vùng giá và đoạn/xã, thuế suất GTGT, mẫu xuất, cách làm tròn. Mỗi tỷ lệ, hệ số phải ghi căn cứ.
2. **Khối lượng** (`khoi_luong.csv`): mỗi dòng một công tác × đoạn, có diễn giải, nguồn bản vẽ, trạng thái `xac_nhan`.
3. **Định mức**: mặc định lấy TT 38 trong `data/tt38/`. Định mức riêng hoặc điều chỉnh có chủ ý ghi vào `dinh_muc.csv` của hồ sơ (được ưu tiên; cột `ly_do` cho hao phí khác TT 38).
4. **Giá**: `can-gia` → điền từ công bố giá Sở XD kỳ hiện hành → `gia_tai_nguyen.csv` (ghi nguồn, ngày áp dụng).
5. **Soát → tính → xuất**: `soat`, rồi `tinh`; còn mục chặn thì dừng (hoặc `--nhap` để xuất bản nháp có đánh dấu).

Cấu trúc file dữ liệu: `references/chuan-bi-du-lieu.md`. Dữ liệu từ G8/Eta/F1: lệnh `chuyendoi` với file ánh xạ cột.

## Dữ liệu định mức TT 38 (`data/tt38/`)

| File | Nội dung |
|---|---|
| `dinh_muc_tt38_p1..p3.csv` | 9.136 mã PL I–VI, 54.190 dòng hao phí (tên tài nguyên đúng như TT 38); trên repo chia 3 phần, script đọc được cả file gộp hoặc `.csv.gz` |
| `danh_muc_tai_nguyen_tt38.csv` | 2.433 tài nguyên (nhân công, máy, vật liệu), đơn vị, số mã dùng, cách viết khác |
| `cap_phoi_tt38.csv`, `hao_hut_tt38.csv` | 378 cấp phối vữa (PL VII), bảng hao hụt PL VII Phần 2 |
| `danh_muc_ma_tt38.csv` | Danh mục mã, phụ lục, chương, nhóm |
| `ma_can_kiem_tra.csv` | 6 mã chưa kết luận (DA.50002/03, DB.10201, DB.17001/02, MS.07201) — soát S18 cảnh báo khi dùng |
| `bao_cao_trich.md`, `bao_cao_sua_bang_khoi.md`, `bao_cao_bo_sung_luoi.md`, `so_sanh_ban_goc_cv9947.md` | Báo cáo trích, sửa lỗi trích, so sánh bản gốc và bản thay thế |

**Giá nhân công tham chiếu** (`data/nhan-cong/`): giá chuyển đổi theo nhóm của Sở XD Hà Nội (CV 14502), Hưng Yên (CV 3385), Hải Phòng (CV 7546, phạm vi vùng theo QĐ 65/QĐ-SXD) và giá theo phương pháp mới của Hà Nội (QĐ 2036/QĐ-SXD, 26/10/2026 — chọn văn bản theo `references/can-cu-phap-ly.md`), kèm phạm vi vùng, khu vực; dùng cho `can-gia --nhan-cong` và soát S22. Kèm danh sách 32 xã, phường theo lý trình tuyến cao tốc Hà Nội – Hải Phòng: `dutoan.py tra --ly-trinh Km36+200` → xã, tỉnh, vùng nhân công.

Giới hạn: 14 khối mã thiếu ở v1 đã bổ sung (16/11/2026); còn 58 mã lệch GXD chưa kết luận (`references/doi-chieu-gxd.md`). PL VII (ngoài cấp phối bê tông, hao hụt) và các bảng tư vấn PL VIII chưa trích thành dữ liệu — PL VIII mới có Bảng 1.1 QLDA. **Trước khi dùng cho hồ sơ thật, đối chiếu ngẫu nhiên vài mã với văn bản gốc.**

Tạo lại khi có bộ phụ lục mới:

```bash
python scripts/nhap_tt38_doc.py --file Phu_luc.doc --ra data/tt38          # trích, rồi nén .gz
python scripts/sua_tt38_bang_khoi.py --txt Phu_luc.txt --data data/tt38 --ghi
python scripts/bo_sung_tt38_luoi.py --file Phu_luc.docx --data data/tt38 --ghi
python scripts/lap_danh_muc_tai_nguyen.py --data data/tt38
```

## Cấu trúc thư mục

```
SKILL.md                 Quy trình 7 bước, nguyên tắc, điểm xác nhận
references/              Căn cứ pháp lý; phương pháp chi phí (TT 36); bảo trì (TT 40); dự toán khảo sát;
                         quy định áp dụng TT 38; áp mã; bóc khối lượng; chuẩn bị dữ liệu; mẫu biểu Excel;
                         mẫu đơn vị; kiểm tra – thẩm tra
scripts/                 dutoan.py (dòng lệnh), dutoan_core.py (tính toán, soát), xuat_excel*.py (xuất Excel),
                         soat_file_excel.py, nhap_du_toan_excel.py, nhap_ks_excel.py (thẩm tra),
                         gia_ca_may.py (giá ca máy PL IV TT 37), tao_mau_word.py (template Word),
                         nhap_tt38_doc.py, sua_tt38_bang_khoi.py, doc_bang_luoi.py, bo_sung_tt38_luoi.py, lap_danh_muc_tai_nguyen.py (dữ liệu TT 38), boc_kl_dxf.py
data/                    tt38/ (định mức), bang_ty_le_tt36_2026.json, bang_ty_le_tt40_2026.json,
                         mau/ (mẫu file), vi-du*/ (ví dụ giá giả), gia-ca-may/ (định mức ca máy mẫu + giá ca máy mẫu),
                         nhan-cong/ (giá nhân công chuyển đổi và theo phương pháp mới),
                         bao-hiem/ (phí, mức khấu trừ bảo hiểm công trình — PL III NĐ 220/2026),
                         chuyen-nganh/ (định mức CNTT QĐ 1601/1235/1595, viễn thông CV 258)
templates/word/          W1/W2/W3 (thuyết minh, biên bản, tờ trình/quyết định/công văn) + README cách dùng
```

## Nguyên tắc

- Không tự nhớ số liệu: định mức, giá, tỷ lệ chỉ lấy từ dữ liệu và văn bản; thiếu thì báo thiếu, không ước lượng.
- Phép tính chạy bằng script; Excel giữ công thức để kiểm tra ngược.
- Mỗi số có nguồn; mỗi hệ số, tỷ lệ có căn cứ; phân biệt rõ điều đã xác nhận, điều suy luận, điều còn thiếu.
- Dừng ở mỗi điểm xác nhận; người lập quyết định.
