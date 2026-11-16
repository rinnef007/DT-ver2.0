"""Xuất dự toán ra Excel có công thức sống, theo Bảng 3.8 PL III TT 36/2026/TT-BXD.

Được gọi từ dutoan.py (lệnh `tinh`). Có thể sửa bố cục cho khớp mẫu biểu của đơn vị.
"""
from collections import OrderedDict

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from dutoan_core import che_do, ds_vung, la_khao_sat, la_tt40, so

FONT = "Times New Roman"
F_THUONG = Font(name=FONT, size=11)
F_DAM = Font(name=FONT, size=11, bold=True)
F_TIEU_DE = Font(name=FONT, size=13, bold=True)
F_NHAP = Font(name=FONT, size=11, color="0000FF")
F_DO = Font(name=FONT, size=12, bold=True, color="C00000")
FILL_NHAP = PatternFill("solid", fgColor="FFF2CC")
FILL_HDR = PatternFill("solid", fgColor="D9E1F2")
FILL_HM = PatternFill("solid", fgColor="EDEDED")
VIEN = Border(*(Side(style="thin", color="999999"),) * 4)
CANH_GIUA = Alignment(horizontal="center", vertical="center", wrap_text=True)
CANH_TRAI = Alignment(horizontal="left", vertical="center", wrap_text=True)
SO_TIEN = "#,##0;(#,##0);-"
SO_KL = "#,##0.000;(#,##0.000);-"
SO_HP = "0.0000"
PHAN_TRAM = "0.00%"


def _o(ws, ref, v=None, font=F_THUONG, fmt=None, fill=None, align=None, border=True):
    c = ws[ref]
    if v is not None:
        c.value = v
    c.font = font
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if align:
        c.alignment = align
    if border:
        c.border = VIEN
    return c


def _hdr(ws, row, titles, widths=None):
    for i, t in enumerate(titles, start=1):
        _o(ws, f"{get_column_letter(i)}{row}", t, F_DAM, fill=FILL_HDR, align=CANH_GIUA)
    if widths:
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w


def _tieu_de(ws, text, cfg, nhap):
    ws["A1"] = text
    ws["A1"].font = F_TIEU_DE
    ws["A2"] = f"Dự án: {cfg.get('du_an','')}   ·   Công trình: {cfg.get('cong_trinh','')}   ·   Hạng mục: {cfg.get('hang_muc','')}"
    ws["A2"].font = F_THUONG
    if nhap:
        ws["A3"] = "BẢN NHÁP — còn mục chưa xác nhận hoặc thiếu dữ liệu (xem sheet CANH_BAO). Không dùng trình duyệt."
        ws["A3"].font = F_DO


def xuat(path, dl, kl_rows, cfg, soat_kq, py, nhap=False):
    wb = Workbook()
    ws_th = wb.active
    ws_th.title = "TH_CPXD"
    ws_dt = wb.create_sheet("DT_CT")
    ws_pt = wb.create_sheet("PT_DG")
    ws_vt = wb.create_sheet("TH_VT")
    ws_hp = wb.create_sheet("HP_CT")
    ws_gia = wb.create_sheet("GIA_TN")
    ws_ts = wb.create_sheet("THAM_SO")
    ws_kl = wb.create_sheet("KL_DIEN_GIAI")

    # ------------------------------------------------ THAM_SO
    ws = ws_ts
    _tieu_de(ws, "THAM SỐ TÍNH TOÁN", cfg, False)
    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 10
    info = [("Dự án", cfg.get("du_an", "")), ("Công trình", cfg.get("cong_trinh", "")),
            ("Hạng mục", cfg.get("hang_muc", "")), ("Loại công trình", cfg.get("loai_cong_trinh", "")),
            ("Địa bàn", cfg.get("dia_ban", "")), ("Thời điểm áp giá", cfg.get("thoi_diem_ap_gia", ""))]
    for i, (k, v) in enumerate(info, start=4):
        _o(ws, f"A{i}", k)
        _o(ws, f"B{i}", v, F_NHAP, fill=FILL_NHAP)
    _hdr(ws, 11, ["Tham số", "Giá trị", "Căn cứ", "Cơ sở"])
    t = cfg["ty_le"]
    hs = cfg.get("he_so", {})
    tt40 = la_tt40(cfg)
    tham_so = [
        (12, "Tỷ lệ chi phí gián tiếp (GT = NC × tỷ lệ, Bảng 2.2 TT 40)" if tt40 else "Tỷ lệ chi phí chung (C)", t["chi_phi_chung"], PHAN_TRAM),
        (13, "Tỷ lệ TT (không áp dụng theo TT 40 — để 0)" if tt40 else "Tỷ lệ chi phí một số công việc không xác định được KL (TT)", t["cong_viec_khong_xd_kl"], PHAN_TRAM),
        (14, "Tỷ lệ thu nhập chịu thuế tính trước (TL)", t["thu_nhap_chiu_thue_tt"], PHAN_TRAM),
        (15, "Tỷ lệ chi phí nhà tạm (LT, Bảng 2.4 TT 40)" if tt40 else "Tỷ lệ chi phí nhà tạm để ở và điều hành thi công (LT)", t["nha_tam"], PHAN_TRAM),
        (16, "Thuế suất GTGT (TGTGT)", t["thue_gtgt"], PHAN_TRAM),
        (17, "Hệ số nhân công Knc", hs.get("knc", {"gia_tri": 1, "can_cu": "Mặc định"}), "0.000"),
        (18, "Hệ số máy Km", hs.get("km", {"gia_tri": 1, "can_cu": "Mặc định"}), "0.000"),
    ]
    for r, ten, d, f in tham_so:
        _o(ws, f"A{r}", ten)
        _o(ws, f"B{r}", float(d.get("gia_tri", 0)), F_NHAP, f, FILL_NHAP)
        _o(ws, f"C{r}", d.get("can_cu", ""), align=CANH_TRAI)
        _o(ws, f"D{r}", "")
    _o(ws, "D12", t["chi_phi_chung"].get("co_so", "T").upper(), F_NHAP, fill=FILL_NHAP, align=CANH_GIUA)
    ws["A20"] = "Ô tô vàng, chữ xanh là ô nhập. Cơ sở chi phí chung: T (Bảng 3.3) hoặc NC (Bảng 3.4)."
    ws["A20"].font = Font(name=FONT, size=10, italic=True)
    TS = {k: f"THAM_SO!$B${r}" for k, r in
          [("C", 12), ("TT", 13), ("TL", 14), ("LT", 15), ("VAT", 16), ("KNC", 17), ("KM", 18)]}
    TS["COSO"] = "THAM_SO!$D$12"
    if la_khao_sat(cfg):
        _o(ws, "A15", "Tỷ lệ chi phí nhà tạm (LT = (G + GTGT) × tỷ lệ, mục 1.6 PL V TT 36)")
        ck = (cfg.get("khao_sat") or {}).get("chi_phi_khac_phuc_vu_ks", {"gia_tri": 0, "can_cu": "Không có"})
        for r, ten, d, f, k in ((22, "Tỷ lệ lập phương án kỹ thuật khảo sát (Cpa, Bảng 5.3)", t["lap_phuong_an_ks"], PHAN_TRAM, "CPA"),
                                (23, "Tỷ lệ lập báo cáo kết quả khảo sát (Cbc, Bảng 5.3)", t["lap_bao_cao_ks"], PHAN_TRAM, "CBC"),
                                (24, "Chi phí khác phục vụ khảo sát (di chuyển máy, ĐBATGT, bảo hiểm — lập dự toán)", ck, SO_TIEN, "CK"),
                                (25, "Tỷ lệ dự phòng (Cdp = (G + GTGT) × tỷ lệ, tối đa 10%)", t["du_phong"], PHAN_TRAM, "DP")):
            _o(ws, f"A{r}", ten)
            _o(ws, f"B{r}", float(so(d.get("gia_tri"), 0)), F_NHAP, f, FILL_NHAP)
            _o(ws, f"C{r}", d.get("can_cu", ""), align=CANH_TRAI)
            TS[k] = f"THAM_SO!$B${r}"

    # ------------------------------------------------ GIA_TN
    ma_dung = OrderedDict()
    for r in kl_rows:
        if r["ma_hieu"] in dl.dinh_muc:
            ma_dung.setdefault(r["ma_hieu"], True)
    tn_dung = dl.tai_nguyen_dung(set(ma_dung))
    vung0 = next(iter(ds_vung(cfg, dl)))
    ws = ws_gia
    _tieu_de(ws, "BẢNG GIÁ TÀI NGUYÊN (chưa thuế GTGT)", cfg, False)
    _hdr(ws, 4, ["Mã TN", "Tên tài nguyên", "ĐVT", "Loại", "Đơn giá (đồng)", "Nguồn", "Ngày áp dụng", "Khu vực"],
         [14, 40, 9, 7, 16, 50, 13, 14])
    row = 5
    for ma, h in tn_dung.items():
        g = dl.gia_cua(ma, vung0)
        _o(ws, f"A{row}", ma)
        _o(ws, f"B{row}", g["ten"] if g else h["ten_tn"], align=CANH_TRAI)
        _o(ws, f"C{row}", g["don_vi"] if g else h["don_vi_tn"], align=CANH_GIUA)
        _o(ws, f"D{row}", h["loai"], align=CANH_GIUA)
        _o(ws, f"E{row}", g["don_gia"] if g else 0, F_NHAP, SO_TIEN, FILL_NHAP)
        if not g:
            ws[f"E{row}"].comment = Comment("THIẾU GIÁ — cần bổ sung", "du-toan-vn")
        _o(ws, f"F{row}", g["nguon"] if g else "THIẾU", align=CANH_TRAI)
        _o(ws, f"G{row}", g["ngay"] if g else "", align=CANH_GIUA)
        _o(ws, f"H{row}", g["khu_vuc"] if g else "")
        row += 1
    gia_cuoi = max(row - 1, 5)
    RG_MA = f"GIA_TN!$A$5:$A${gia_cuoi}"
    RG_GIA = f"GIA_TN!$E$5:$E${gia_cuoi}"

    def f_gia(ref_ma):
        return f"=IFERROR(INDEX({RG_GIA},MATCH({ref_ma},{RG_MA},0)),0)"

    # ------------------------------------------------ PT_DG
    ws = ws_pt
    _tieu_de(ws, "BẢNG PHÂN TÍCH ĐƠN GIÁ (trên 1 đơn vị định mức)", cfg, False)
    _hdr(ws, 4, ["Mã hiệu", "Loại", "Mã TN", "Tên công tác / tài nguyên", "ĐVT", "Hao phí", "Đơn giá", "Thành tiền", "Hệ số"],
         [13, 7, 13, 50, 9, 11, 14, 16, 8])
    pt_o = {}  # ma -> (cell VL, NC, M)
    row = 5
    for ma in ma_dung:
        d = dl.dinh_muc[ma]
        for col in "ABCDEFGH":
            _o(ws, f"{col}{row}", fill=FILL_HM)
        _o(ws, f"A{row}", ma, F_DAM, fill=FILL_HM)
        _o(ws, f"D{row}", d["ten"], F_DAM, fill=FILL_HM, align=CANH_TRAI)
        _o(ws, f"E{row}", d["don_vi"], F_DAM, fill=FILL_HM, align=CANH_GIUA)
        _o(ws, f"H{row}", f"Nguồn: {d['nguon']}", Font(name=FONT, size=9, italic=True), fill=FILL_HM)
        row += 1
        r0 = row
        vl_rows = []
        pending_pct = []
        for h in d["hao_phi"]:
            _o(ws, f"B{row}", h["loai"], align=CANH_GIUA)
            _o(ws, f"C{row}", h["ma_tn"])
            _o(ws, f"D{row}", h["ten_tn"], align=CANH_TRAI)
            _o(ws, f"E{row}", h["don_vi_tn"] or ("%" if h["loai"] in ("VLK", "MK") else ""), align=CANH_GIUA)
            _o(ws, f"F{row}", h["hao_phi"], fmt=SO_HP)
            if h["loai"] in ("VLK", "MK"):
                _o(ws, f"G{row}", "")
                pending_pct.append((row, h["loai"]))
            else:
                _o(ws, f"G{row}", f_gia(f"C{row}"), fmt=SO_TIEN)
                _o(ws, f"I{row}", h["he_so"], F_NHAP, "0.000", FILL_NHAP)
                if h.get("can_cu_he_so"):
                    ws[f"I{row}"].comment = Comment(h["can_cu_he_so"], "du-toan-vn")
                _o(ws, f"H{row}", f"=F{row}*G{row}*I{row}", fmt=SO_TIEN)
                if h["loai"] == "VL":
                    vl_rows.append(row)
            row += 1
        r1 = row - 1
        for pr, loai in pending_pct:
            goc = "VL" if loai == "VLK" else "M"
            _o(ws, f"H{pr}", f'=F{pr}/100*SUMIF($B${r0}:$B${r1},"{goc}",$H${r0}:$H${r1})', fmt=SO_TIEN)
        cells = {}
        for nhan, loai, them in (("Cộng vật liệu", "VL", "VLK"), ("Cộng nhân công", "NC", None), ("Cộng máy thi công", "M", "MK")):
            _o(ws, f"D{row}", nhan, F_DAM)
            f = f'=SUMIF($B${r0}:$B${r1},"{loai}",$H${r0}:$H${r1})'
            if them:
                f += f'+SUMIF($B${r0}:$B${r1},"{them}",$H${r0}:$H${r1})'
            _o(ws, f"H{row}", f, F_DAM, SO_TIEN)
            cells[loai] = f"PT_DG!$H${row}"
            row += 1
        pt_o[ma] = cells
        row += 1

    # ------------------------------------------------ DT_CT
    ws = ws_dt
    _tieu_de(ws, "BẢNG DỰ TOÁN CHI TIẾT CHI PHÍ XÂY DỰNG", cfg, nhap)
    _hdr(ws, 5, ["STT", "Mã hiệu", "Tên công tác", "Đơn vị", "Khối lượng", "Quy đổi", "HS VL", "HS NC", "HS M",
                 "ĐG vật liệu", "ĐG nhân công", "ĐG máy", "TT vật liệu", "TT nhân công", "TT máy", "Thành tiền", "Loại dòng"],
         [6, 12, 48, 8, 12, 8, 7, 7, 7, 14, 14, 14, 16, 16, 16, 17, 9])
    ws.freeze_panes = "D6"
    nhom = OrderedDict()
    for r in kl_rows:
        nhom.setdefault(r["hang_muc"], []).append(r)
    row = 6
    dong_kl = {}  # id(r) -> row
    for hm, rs in nhom.items():
        for col in "ABCDEFGHIJKLMNOPQ":
            _o(ws, f"{col}{row}", fill=FILL_HM)
        _o(ws, f"C{row}", hm, F_DAM, fill=FILL_HM)
        _o(ws, f"Q{row}", "HM", fill=FILL_HM)
        row += 1
        b0 = row
        for r in rs:
            dong_kl[id(r)] = row
            tg = r["ma_hieu"].upper() == "TG"
            co_dm = r["ma_hieu"] in dl.dinh_muc
            ten = r["ten"] or (dl.dinh_muc[r["ma_hieu"]]["ten"] if co_dm else "")
            _o(ws, f"A{row}", r["stt"], align=CANH_GIUA)
            _o(ws, f"B{row}", r["ma_hieu"])
            _o(ws, f"C{row}", ten, align=CANH_TRAI)
            _o(ws, f"D{row}", r["don_vi"], align=CANH_GIUA)
            _o(ws, f"E{row}", r["kl"] if r["kl"] is not None else 0, F_NHAP, SO_KL, FILL_NHAP)
            _o(ws, f"F{row}", r["quy_doi"], F_NHAP, "0.0000", FILL_NHAP)
            _o(ws, f"G{row}", r["hs_vl"], F_NHAP, "0.000", FILL_NHAP)
            _o(ws, f"H{row}", r["hs_nc"], F_NHAP, "0.000", FILL_NHAP)
            _o(ws, f"I{row}", r["hs_m"], F_NHAP, "0.000", FILL_NHAP)
            if tg:
                _o(ws, f"J{row}", r["dg_tg"] or 0, F_NHAP, SO_TIEN, FILL_NHAP)
                ws[f"J{row}"].comment = Comment("Đơn giá trọn gói, gộp vào chi phí vật liệu (PL III TT 36/2026). Kiểm tra trường hợp Bảng 3.9.", "du-toan-vn")
                _o(ws, f"K{row}", 0, fmt=SO_TIEN)
                _o(ws, f"L{row}", 0, fmt=SO_TIEN)
            elif co_dm:
                c = pt_o[r["ma_hieu"]]
                _o(ws, f"J{row}", f"={c['VL']}*F{row}*G{row}", fmt=SO_TIEN)
                _o(ws, f"K{row}", f"={c['NC']}*F{row}*H{row}", fmt=SO_TIEN)
                _o(ws, f"L{row}", f"={c['M']}*F{row}*I{row}", fmt=SO_TIEN)
            else:
                for col in "JKL":
                    _o(ws, f"{col}{row}", 0, fmt=SO_TIEN)
                ws[f"B{row}"].comment = Comment("Mã không có trong bộ định mức đã nạp", "du-toan-vn")
            _o(ws, f"M{row}", f"=E{row}*J{row}", fmt=SO_TIEN)
            _o(ws, f"N{row}", f"=E{row}*K{row}", fmt=SO_TIEN)
            _o(ws, f"O{row}", f"=E{row}*L{row}", fmt=SO_TIEN)
            _o(ws, f"P{row}", f"=M{row}+N{row}+O{row}", fmt=SO_TIEN)
            _o(ws, f"Q{row}", "CT")
            if r["trang_thai"] != "xac_nhan":
                ws[f"A{row}"].comment = Comment(f"Trạng thái: {r['trang_thai']}", "du-toan-vn")
            row += 1
        b1 = row - 1
        _o(ws, f"C{row}", f"Cộng {hm}", F_DAM)
        for col in "MNOP":
            _o(ws, f"{col}{row}", f"=SUM({col}{b0}:{col}{b1})", F_DAM, SO_TIEN)
        _o(ws, f"Q{row}", "CHM")
        row += 1
    dt_cuoi = row - 1
    tong = row
    _o(ws, f"C{tong}", "TỔNG CỘNG", F_DAM)
    for col in "MNOP":
        _o(ws, f"{col}{tong}", f'=SUMIF($Q$6:$Q${dt_cuoi},"CT",{col}6:{col}{dt_cuoi})', F_DAM, SO_TIEN)
    _o(ws, f"Q{tong}", "TONG")

    # ------------------------------------------------ HP_CT + TH_VT
    ws = ws_hp
    _tieu_de(ws, "HAO PHÍ CHI TIẾT (phục vụ tổng hợp vật tư)", cfg, False)
    _hdr(ws, 4, ["STT KL", "Mã hiệu", "Mã TN", "Loại", "Hao phí ĐM × hệ số", "Tổng hao phí"], [8, 13, 13, 7, 14, 16])
    row = 5
    cot_hs = {"VL": "G", "NC": "H", "M": "I"}
    for r in kl_rows:
        if r["ma_hieu"] not in dl.dinh_muc:
            continue
        rr = dong_kl[id(r)]
        for h in dl.dinh_muc[r["ma_hieu"]]["hao_phi"]:
            if h["loai"] not in cot_hs:
                continue
            _o(ws, f"A{row}", r["stt"])
            _o(ws, f"B{row}", r["ma_hieu"])
            _o(ws, f"C{row}", h["ma_tn"])
            _o(ws, f"D{row}", h["loai"])
            _o(ws, f"E{row}", h["hao_phi"] * h["he_so"], fmt=SO_HP)
            _o(ws, f"F{row}", f"=DT_CT!E{rr}*DT_CT!F{rr}*DT_CT!{cot_hs[h['loai']]}{rr}*E{row}", fmt=SO_HP)
            row += 1
    hp_cuoi = max(row - 1, 5)

    ws = ws_vt
    _tieu_de(ws, "BẢNG TỔNG HỢP VẬT TƯ, NHÂN CÔNG, MÁY THI CÔNG", cfg, nhap)
    _hdr(ws, 5, ["Mã TN", "Tên tài nguyên", "ĐVT", "Loại", "Tổng hao phí", "Đơn giá", "Thành tiền"],
         [14, 42, 9, 7, 16, 14, 18])
    row = 6
    for loai, ten_nhom in (("VL", "VẬT LIỆU"), ("NC", "NHÂN CÔNG"), ("M", "MÁY THI CÔNG")):
        ds = [(m, h) for m, h in tn_dung.items() if h["loai"] == loai]
        for col in "ABCDEFG":
            _o(ws, f"{col}{row}", fill=FILL_HM)
        _o(ws, f"B{row}", ten_nhom, F_DAM, fill=FILL_HM)
        row += 1
        b0 = row
        for m, h in ds:
            g = dl.gia_cua(m, vung0)
            _o(ws, f"A{row}", m)
            _o(ws, f"B{row}", g["ten"] if g else h["ten_tn"], align=CANH_TRAI)
            _o(ws, f"C{row}", g["don_vi"] if g else h["don_vi_tn"], align=CANH_GIUA)
            _o(ws, f"D{row}", loai, align=CANH_GIUA)
            _o(ws, f"E{row}", f"=SUMIF(HP_CT!$C$5:$C${hp_cuoi},A{row},HP_CT!$F$5:$F${hp_cuoi})", fmt=SO_KL)
            _o(ws, f"F{row}", f_gia(f"A{row}"), fmt=SO_TIEN)
            _o(ws, f"G{row}", f"=E{row}*F{row}", fmt=SO_TIEN)
            row += 1
        _o(ws, f"B{row}", f"Cộng {ten_nhom.lower()}", F_DAM)
        _o(ws, f"G{row}", f"=SUM(G{b0}:G{max(row-1,b0)})" if ds else 0, F_DAM, SO_TIEN)
        ws[f"G{row}"].number_format = SO_TIEN
        if loai == "VL":
            vt_vl = f"G{row}"
        elif loai == "NC":
            vt_nc = f"G{row}"
        else:
            vt_m = f"G{row}"
        row += 2
    _o(ws, f"B{row}", "Đối chiếu với DT_CT (chênh lệch = vật liệu khác/máy khác %, đơn giá trọn gói)", F_DAM)
    row += 1
    for nhan, o_vt, col in (("Vật liệu", vt_vl, "M"), ("Nhân công (trước Knc)", vt_nc, "N"), ("Máy (trước Km)", vt_m, "O")):
        _o(ws, f"B{row}", nhan)
        _o(ws, f"E{row}", f"={o_vt}", fmt=SO_TIEN)
        _o(ws, f"F{row}", f"=DT_CT!{col}{tong}", fmt=SO_TIEN)
        _o(ws, f"G{row}", f"=F{row}-E{row}", fmt=SO_TIEN)
        row += 1
    ws[f"E{row}"] = "TH_VT"
    ws[f"F{row}"] = "DT_CT"
    ws[f"G{row}"] = "Chênh lệch"

    # ------------------------------------------------ TH_CPXD (Bảng 3.8)
    ws = ws_th
    tt40 = la_tt40(cfg)
    bd = che_do(cfg) == "tt40_bao_duong"
    if tt40:
        _tieu_de(ws, "DỰ TOÁN CHI PHÍ THỰC HIỆN " + ("BẢO DƯỠNG" if bd else "SỬA CHỮA") + " CÔNG TRÌNH", cfg, nhap)
        ws["A4"] = ("(Theo Bảng 2.5 Phụ lục II" if bd else "(Theo Bảng 3.2 Phụ lục III") + " Thông tư 40/2026/TT-BXD)    Đơn vị tính: đồng"
    else:
        _tieu_de(ws, "BẢNG TỔNG HỢP DỰ TOÁN CHI PHÍ XÂY DỰNG", cfg, nhap)
        ws["A4"] = "(Theo Bảng 3.8 Phụ lục III Thông tư 36/2026/TT-BXD; đính chính QĐ 1538/QĐ-BXD)    Đơn vị tính: đồng"
    ws["A4"].font = Font(name=FONT, size=10, italic=True)
    _hdr(ws, 6, ["STT", "Nội dung chi phí", "Cách tính", "Giá trị", "Ký hiệu"], [6, 52, 30, 20, 10])
    dong = [
        ("I", "Chi phí trực tiếp", "VL + NC + M", "=D8+D9+D10", "T", True),
        ("1", "Chi phí vật liệu", "Σ Qj × Djvl", f"=DT_CT!M{tong}", "VL", False),
        ("2", "Chi phí nhân công", "Σ Qj × Djnc × Knc", f"=DT_CT!N{tong}*{TS['KNC']}", "NC", False),
        ("3", "Chi phí máy và thiết bị thi công", "Σ Qj × Djm × Km", f"=DT_CT!O{tong}*{TS['KM']}", "M", False),
        ("II", "Chi phí gián tiếp", "C + TT", "=D12+D13", "GT", True),
        ("1", "Chi phí chung", "T × tỷ lệ (hoặc NC × tỷ lệ)", f'=IF({TS["COSO"]}="NC",D9,D7)*{TS["C"]}', "C", False),
        ("2", "Chi phí một số công việc không xác định được khối lượng từ thiết kế", "T × tỷ lệ", f"=D7*{TS['TT']}", "TT", False),
        ("III", "Thu nhập chịu thuế tính trước", "(T + GT) × tỷ lệ", f"=(D7+D11)*{TS['TL']}", "TL", True),
        ("", "Chi phí xây dựng trước thuế", "T + GT + TL", "=D7+D11+D14", "GXDTT", True),
        ("IV", "Thuế giá trị gia tăng", "GXDTT × TGTGT", f"=D15*{TS['VAT']}", "GTGT", True),
        ("", "CHI PHÍ XÂY DỰNG SAU THUẾ", "GXDTT + GTGT", "=D15+D16", "GXD", True),
        ("V", "Chi phí nhà tạm để ở và điều hành thi công", "GXDTT × tỷ lệ × (1 + TGTGT)", f"=D15*{TS['LT']}*(1+{TS['VAT']})", "LT", True),
    ]
    if tt40:
        ten_g = "bảo dưỡng" if bd else "sửa chữa"
        dong[4] = ("II", "Chi phí gián tiếp", "NC × tỷ lệ", "=D12+D13", "GT", True)
        dong[5] = ("1", "Chi phí gián tiếp tính trên chi phí nhân công", "NC × tỷ lệ (Bảng 2.2 TT 40)", f"=D9*{TS['C']}", "", False)
        dong[6] = ("2", "(TT 40 không có khoản chi phí một số công việc không xác định được KL)", "—", f"=D7*{TS['TT']}", "", False)
        dong[8] = ("", f"Chi phí thực hiện {ten_g} trước thuế", "T + GT + TL", "=D7+D11+D14", "GTHTT", True)
        dong[9] = ("IV", "Thuế giá trị gia tăng (nếu có)", "GTHTT × TGTGT", f"=D15*{TS['VAT']}", "GTGT", True)
        dong[10] = ("", f"CHI PHÍ THỰC HIỆN {ten_g.upper()} SAU THUẾ", "GTHTT + GTGT", "=D15+D16", "GTH", True)
        dong[11] = ("V", "Chi phí nhà tạm", "GTH × tỷ lệ (Bảng 2.4 TT 40)", f"=D17*{TS['LT']}", "LT", True)
    if la_khao_sat(cfg):
        ws["A1"] = "BẢNG TỔNG HỢP DỰ TOÁN CHI PHÍ KHẢO SÁT XÂY DỰNG"
        ws["A4"] = "(Theo Bảng 5.4 Phụ lục V Thông tư 36/2026/TT-BXD — bộ phụ lục thay thế CV 9947/BXD-VPB)    Đơn vị tính: đồng"
        dong = dong[:8] + [
            ("IV", "Chi phí phục vụ công tác khảo sát xây dựng", "Cpa + Cbc + Ck", "=D16+D17+D18", "Cpvks", True),
            ("1", "Chi phí lập phương án kỹ thuật khảo sát xây dựng", "(T + GT + TL) × tỷ lệ", f"=(D7+D11+D14)*{TS['CPA']}", "", False),
            ("2", "Chi phí lập báo cáo kết quả khảo sát xây dựng", "(T + GT + TL) × tỷ lệ", f"=(D7+D11+D14)*{TS['CBC']}", "", False),
            ("3", "Chi phí khác phục vụ khảo sát", "Lập dự toán", f"={TS['CK']}", "", False),
            ("", "Chi phí khảo sát xây dựng trước thuế", "(T + GT + TL) + Cpvks", "=D7+D11+D14+D15", "G", True),
            ("V", "Thuế giá trị gia tăng", "G × TGTGT", f"=D19*{TS['VAT']}", "GTGT", True),
            ("VI", "Chi phí nhà tạm để ở và điều hành thi công", "(G + GTGT) × tỷ lệ", f"=(D19+D20)*{TS['LT']}", "LT", True),
            ("VII", "Chi phí dự phòng", "(G + GTGT) × tỷ lệ", f"=(D19+D20)*{TS['DP']}", "Cdp", True),
            ("", "CHI PHÍ KHẢO SÁT XÂY DỰNG", "G + GTGT + LT + Cdp", "=D19+D20+D21+D22", "Gks", True),
        ]
        dong[5] = ("1", "Chi phí chung", "NC × tỷ lệ (Bảng 5.1)", f"=D9*{TS['C']}", "C", False)
        dong[6] = ("2", "Chi phí một số công việc không xác định được khối lượng từ thiết kế", "T × tỷ lệ (Bảng 5.2)", f"=D7*{TS['TT']}", "TT", False)
    for i, (stt, nd, ct, f, kh, dam) in enumerate(dong, start=7):
        fnt = F_DAM if dam else F_THUONG
        _o(ws, f"A{i}", stt, fnt, align=CANH_GIUA)
        _o(ws, f"B{i}", nd, fnt, align=CANH_TRAI)
        _o(ws, f"C{i}", ct, fnt, align=CANH_TRAI)
        _o(ws, f"D{i}", f, fnt, SO_TIEN)
        _o(ws, f"E{i}", kh, fnt, align=CANH_GIUA)
    k0 = 7 + len(dong) + 2
    ws[f"B{k0}"] = "NGƯỜI LẬP"
    ws[f"D{k0}"] = "NGƯỜI CHỦ TRÌ"
    ws[f"B{k0+1}"] = "(Ký, họ tên)"
    ws[f"D{k0+1}"] = "(Ký, họ tên)"
    ws[f"B{k0+4}"] = cfg.get("nguoi_lap", "")
    ws[f"D{k0+4}"] = cfg.get("nguoi_chu_tri", "")
    for ref in (f"B{k0}", f"D{k0}", f"B{k0+4}", f"D{k0+4}"):
        ws[ref].font = F_DAM
        ws[ref].alignment = CANH_GIUA
    for ref in (f"B{k0+1}", f"D{k0+1}"):
        ws[ref].font = Font(name=FONT, size=10, italic=True)
        ws[ref].alignment = CANH_GIUA

    # ------------------------------------------------ KL_DIEN_GIAI
    ws = ws_kl
    _tieu_de(ws, "BẢNG KHỐI LƯỢNG VÀ DIỄN GIẢI", cfg, False)
    _hdr(ws, 4, ["STT", "Hạng mục", "Mã hiệu", "Đơn vị", "Khối lượng", "Diễn giải", "Nguồn bản vẽ", "Hệ số / căn cứ", "Trạng thái"],
         [6, 22, 12, 8, 12, 50, 16, 30, 11])
    for i, r in enumerate(kl_rows, start=5):
        _o(ws, f"A{i}", r["stt"])
        _o(ws, f"B{i}", r["hang_muc"], align=CANH_TRAI)
        _o(ws, f"C{i}", r["ma_hieu"])
        _o(ws, f"D{i}", r["don_vi"], align=CANH_GIUA)
        _o(ws, f"E{i}", r["kl"], fmt=SO_KL)
        _o(ws, f"F{i}", r["dien_giai"], align=CANH_TRAI)
        _o(ws, f"G{i}", r["ban_ve"])
        hsx = "" if all(abs(x - 1) < 1e-12 for x in (r["hs_vl"], r["hs_nc"], r["hs_m"])) else \
            f"VL {r['hs_vl']:g}, NC {r['hs_nc']:g}, M {r['hs_m']:g}; {r['can_cu_hs']}"
        _o(ws, f"H{i}", hsx, align=CANH_TRAI)
        _o(ws, f"I{i}", r["trang_thai"], align=CANH_GIUA)

    # ------------------------------------------------ CANH_BAO
    if soat_kq:
        ws = wb.create_sheet("CANH_BAO")
        _tieu_de(ws, "KẾT QUẢ SOÁT", cfg, False)
        _hdr(ws, 4, ["Mã", "Mức", "Nội dung"], [7, 12, 120])
        thu_tu = {"CHAN": 0, "CANH_BAO": 1, "THONG_TIN": 2}
        for i, (ma, muc, nd) in enumerate(sorted(soat_kq, key=lambda x: (thu_tu[x[1]], x[0])), start=5):
            _o(ws, f"A{i}", ma)
            _o(ws, f"B{i}", muc, F_DO if muc == "CHAN" else F_THUONG)
            _o(ws, f"C{i}", nd, align=CANH_TRAI)

    for w in wb.worksheets:
        w.sheet_view.showGridLines = False
        w.page_setup.orientation = "landscape"
        w.page_setup.paperSize = w.PAPERSIZE_A4
        w.page_setup.fitToWidth = 1
        w.page_setup.fitToHeight = 0
        w.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(path)
