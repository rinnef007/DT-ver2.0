"""Xuất dự toán theo mẫu "đoạn – vùng giá" (đơn giá chi tiết đầy đủ, khối lượng theo đoạn/xã, bảng tổng hợp cấu hình được).

Sheet: TDT (tổng hợp) · DT (bảng dự toán theo hạng mục, KL theo đoạn) · DGCT (bảng đơn giá chi tiết) · GIA_TN · THAM_SO ·
KL_DIEN_GIAI · CANH_BAO. Mọi ô kết quả là công thức; làm tròn từng bước bằng ROUND khi config "lam_tron" = "tung_buoc".
Được gọi từ dutoan.py khi config "mau_xuat" = "doan_vung".
"""
from collections import OrderedDict

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L

from dutoan_core import bien_the, ds_doan, ds_vung, gom_cong_tac, la_khao_sat, la_tt40, so, ty_le_cho_ma

FONT = "Times New Roman"
F_TH = Font(name=FONT, size=11)
F_DAM = Font(name=FONT, size=11, bold=True)
F_TD = Font(name=FONT, size=13, bold=True)
F_NHAP = Font(name=FONT, size=11, color="0000FF")
F_DO = Font(name=FONT, size=12, bold=True, color="C00000")
F_NHO = Font(name=FONT, size=9, italic=True)
FILL_NHAP = PatternFill("solid", fgColor="FFF2CC")
FILL_HDR = PatternFill("solid", fgColor="D9E1F2")
FILL_HM = PatternFill("solid", fgColor="EDEDED")
VIEN = Border(*(Side(style="thin", color="999999"),) * 4)
GIUA = Alignment(horizontal="center", vertical="center", wrap_text=True)
TRAI = Alignment(horizontal="left", vertical="center", wrap_text=True)
TIEN = "#,##0;(#,##0);-"
KL = "#,##0.00;(#,##0.00);-"
HP = "0.0000"
PT = "0.00%"


def o(ws, ref, v=None, font=F_TH, fmt=None, fill=None, align=None, border=True):
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


def doc_so_tien(n):
    """Đọc số tiền bằng chữ (đồng)."""
    so_chu = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    n = int(round(n))
    if n == 0:
        return "Không đồng"
    am = n < 0
    n = abs(n)

    def ba_so(x, day_du):
        tr, ch, dv = x // 100, (x // 10) % 10, x % 10
        w = []
        if day_du or tr:
            w += [so_chu[tr], "trăm"]
        if ch == 0:
            if dv and (day_du or tr):
                w.append("linh")
        elif ch == 1:
            w.append("mười")
        else:
            w += [so_chu[ch], "mươi"]
        if dv:
            if dv == 1 and ch >= 2:
                w.append("mốt")
            elif dv == 5 and ch >= 1:
                w.append("lăm")
            else:
                w.append(so_chu[dv])
        return w

    nhom = []
    while n:
        nhom.append(n % 1000)
        n //= 1000
    words = []
    for i in range(len(nhom) - 1, -1, -1):
        g = nhom[i]
        if g == 0:
            continue
        words += ba_so(g, day_du=(i != len(nhom) - 1))
        unit = (["", "nghìn", "triệu"][i % 3] + " tỷ" * (i // 3)).strip()
        if unit:
            words.append(unit)
    s = " ".join(w for w in words if w).replace("  ", " ").strip()
    s = (("Âm " + s) if am else s[0].upper() + s[1:]) + " đồng"
    return s


def xuat(path, dl, kl_rows, cfg, soat_kq, py, nhap=False):
    rt = cfg.get("lam_tron", "khong") == "tung_buoc"

    def R(e):
        return f"ROUND({e},0)" if rt else f"({e})"

    vung = ds_vung(cfg, dl)
    vids = list(vung)
    nv = len(vids)
    doan = ds_doan(cfg, kl_rows)
    dids = [d for d in doan if any(r["doan"] == d for r in kl_rows)]
    nd = len(dids)
    items = gom_cong_tac(kl_rows)
    wb = Workbook()
    ws_tdt = wb.active
    ws_tdt.title = "TDT"
    ws_dt = wb.create_sheet("DT")
    ws_dg = wb.create_sheet("DGCT")
    ws_gia = wb.create_sheet("GIA_TN")
    ws_ts = wb.create_sheet("THAM_SO")
    ws_kl = wb.create_sheet("KL_DIEN_GIAI")

    def tieu_de(ws, text, sub=None):
        ws["A1"] = text
        ws["A1"].font = F_TD
        ws["A2"] = f"Dự án: {cfg.get('du_an','')}   ·   Công trình: {cfg.get('cong_trinh','')}"
        ws["A2"].font = F_TH
        if sub:
            ws["A3"] = sub
            ws["A3"].font = F_DAM
        if nhap:
            ws["A4"] = "BẢN NHÁP — còn mục chưa xác nhận hoặc thiếu dữ liệu (xem sheet CANH_BAO)."
            ws["A4"].font = F_DO

    # ------------------------------------------------ THAM_SO
    ws = ws_ts
    tieu_de(ws, "THAM SỐ TÍNH TOÁN")
    for col, w in zip("ABCD", (48, 18, 70, 10)):
        ws.column_dimensions[col].width = w
    for c, t in zip("ABCD", ("Tham số", "Giá trị", "Căn cứ", "Cơ sở")):
        o(ws, f"{c}11", t, F_DAM, fill=FILL_HDR, align=GIUA)
    t = cfg["ty_le"]
    tt40 = la_tt40(cfg)
    for r, ten, k in ((12, "Chi phí gián tiếp (NC × tỷ lệ, Bảng 2.2 TT 40)" if tt40 else "Chi phí chung (C)", "chi_phi_chung"),
                      (13, "TT — không áp dụng theo TT 40 (để 0)" if tt40 else "Chi phí một số công việc không xác định được KL (TT)", "cong_viec_khong_xd_kl"),
                      (14, "Thu nhập chịu thuế tính trước (TL)", "thu_nhap_chiu_thue_tt"),
                      (15, "Chi phí nhà tạm (LT, Bảng 2.4 TT 40)" if tt40 else "Chi phí nhà tạm để ở và điều hành thi công (LT)", "nha_tam"),
                      (16, "Thuế suất GTGT", "thue_gtgt")):
        o(ws, f"A{r}", ten)
        o(ws, f"B{r}", so(t[k]["gia_tri"], 0), F_NHAP, PT, FILL_NHAP)
        o(ws, f"C{r}", t[k].get("can_cu", ""), align=TRAI)
        o(ws, f"D{r}", "")
    o(ws, "D12", t["chi_phi_chung"].get("co_so", "T").upper(), F_NHAP, fill=FILL_NHAP, align=GIUA)
    o(ws, "D16", "")
    TS = {"C": "THAM_SO!$B$12", "TT": "THAM_SO!$B$13", "TL": "THAM_SO!$B$14", "LT": "THAM_SO!$B$15", "VAT": "THAM_SO!$B$16",
          "COSO": "THAM_SO!$D$12"}
    r_note = 17
    if la_khao_sat(cfg):
        o(ws, "A15", "Chi phí nhà tạm để ở và điều hành thi công (LT = (G + GTGT) × tỷ lệ)")
        for r, ten, k, ts in ((17, "Lập phương án kỹ thuật khảo sát (Cpa = (T+GT+TL) × tỷ lệ, Bảng 5.3)", "lap_phuong_an_ks", "CPA"),
                              (18, "Lập báo cáo kết quả khảo sát (Cbc = (T+GT+TL) × tỷ lệ, Bảng 5.3)", "lap_bao_cao_ks", "CBC"),
                              (19, "Dự phòng (Cdp = (G + GTGT) × tỷ lệ, tối đa 10%)", "du_phong", "DP")):
            o(ws, f"A{r}", ten)
            o(ws, f"B{r}", so(t[k]["gia_tri"], 0), F_NHAP, PT, FILL_NHAP)
            o(ws, f"C{r}", t[k].get("can_cu", ""), align=TRAI)
            TS[ts] = f"THAM_SO!$B${r}"
        r_note = 20
    ws[f"A{r_note}"] = f"Làm tròn: {'từng bước (ROUND đến đồng)' if rt else 'không làm tròn trung gian'}"
    ws[f"A{r_note}"].font = F_NHO
    r = r_note + 2
    o(ws, f"A{r}", "Vùng giá", F_DAM, fill=FILL_HDR)
    o(ws, f"B{r}", "Mã", F_DAM, fill=FILL_HDR)
    for i, (vid, ten) in enumerate(vung.items(), start=1):
        o(ws, f"A{r+i}", ten, align=TRAI)
        o(ws, f"B{r+i}", vid or "(chung)", align=GIUA)
    r = r + nv + 2
    o(ws, f"A{r}", "Đoạn / xã", F_DAM, fill=FILL_HDR)
    o(ws, f"B{r}", "Mã", F_DAM, fill=FILL_HDR)
    o(ws, f"C{r}", "Vùng giá áp dụng", F_DAM, fill=FILL_HDR)
    for i, d in enumerate(dids, start=1):
        o(ws, f"A{r+i}", doan[d][0], align=TRAI)
        o(ws, f"B{r+i}", d or "(chung)", align=GIUA)
        o(ws, f"C{r+i}", vung.get(doan[d][1] or vids[0], doan[d][1]), align=TRAI)

    # ------------------------------------------------ GIA_TN
    ma_dung = OrderedDict()
    for it in items.values():
        if it["r"]["ma_hieu"] in dl.dinh_muc:
            ma_dung.setdefault(it["r"]["ma_hieu"], True)
    tn = dl.tai_nguyen_dung(set(ma_dung))
    ws = ws_gia
    tieu_de(ws, "BẢNG GIÁ TÀI NGUYÊN (chưa thuế GTGT)")
    hdr = ["Mã TN", "Tên tài nguyên", "ĐVT", "Loại"] + [vung[v] for v in vids] + ["Nguồn", "Ngày áp dụng"]
    for i, h in enumerate(hdr, start=1):
        o(ws, f"{L(i)}6", h, F_DAM, fill=FILL_HDR, align=GIUA)
    for i, w in enumerate([16, 40, 9, 7] + [18] * nv + [55, 13], start=1):
        ws.column_dimensions[L(i)].width = w
    ws.row_dimensions[6].height = 45
    row = 7
    for ma, h in tn.items():
        g0 = dl.gia_cua(ma, vids[0])
        o(ws, f"A{row}", ma)
        o(ws, f"B{row}", (g0 or {}).get("ten") or h["ten_tn"], align=TRAI)
        o(ws, f"C{row}", (g0 or {}).get("don_vi") or h["don_vi_tn"], align=GIUA)
        o(ws, f"D{row}", h["loai"], align=GIUA)
        nguon = []
        for k, v in enumerate(vids):
            g = dl.gia_cua(ma, v)
            o(ws, f"{L(5+k)}{row}", g["don_gia"] if g else 0, F_NHAP, TIEN, FILL_NHAP)
            if not g:
                ws[f"{L(5+k)}{row}"].comment = Comment("THIẾU GIÁ", "du-toan-vn")
            elif g["nguon"] and g["nguon"] not in nguon:
                nguon.append(g["nguon"])
        o(ws, f"{L(5+nv)}{row}", "; ".join(nguon) or "THIẾU", align=TRAI)
        o(ws, f"{L(6+nv)}{row}", (g0 or {}).get("ngay", ""), align=GIUA)
        row += 1
    gia_cuoi = max(row - 1, 7)
    RG_MA = f"GIA_TN!$A$7:$A${gia_cuoi}"

    def f_gia(ref, k):
        return f"IFERROR(INDEX(GIA_TN!${L(5+k)}$7:${L(5+k)}${gia_cuoi},MATCH({ref},{RG_MA},0)),0)"

    # ------------------------------------------------ DGCT
    ws = ws_dg
    tieu_de(ws, "BẢNG ĐƠN GIÁ CHI TIẾT")
    cF, cH, cI = 6, 6 + nv, 7 + nv
    hdr = ["STT", "Mã số", "Thành phần hao phí", "Đơn vị", "Định mức"] + [f"Đơn giá\n{vung[v]}" for v in vids] + ["Hệ số"] + \
          [f"Thành tiền\n{vung[v]}" for v in vids]
    for i, h in enumerate(hdr, start=1):
        o(ws, f"{L(i)}6", h, F_DAM, fill=FILL_HDR, align=GIUA)
    for i, w in enumerate([6, 16, 52, 10, 10] + [14] * nv + [8] + [15] * nv, start=1):
        ws.column_dimensions[L(i)].width = w
    ws.row_dimensions[6].height = 60
    ws.freeze_panes = "D7"
    dg_o = {}  # bien_the -> {vid: cell}
    row, seq = 7, 0
    for it in items.values():
        r0 = it["r"]
        bt = bien_the(r0)
        if bt in dg_o:
            continue
        seq += 1
        tg = r0["ma_hieu"].upper() == "TG"
        d = dl.dinh_muc.get(r0["ma_hieu"])
        Edm = round(1 / r0["quy_doi"], 9) if r0["quy_doi"] else 1
        hrow = row
        ten = r0["ten"] or (d["ten"] if d else "")
        for c in range(1, cI + nv):
            o(ws, f"{L(c)}{row}", fill=FILL_HM)
        o(ws, f"A{row}", seq, F_DAM, fill=FILL_HM, align=GIUA)
        o(ws, f"B{row}", r0["ma_hieu"], F_DAM, fill=FILL_HM)
        o(ws, f"C{row}", ten, F_DAM, fill=FILL_HM, align=TRAI)
        o(ws, f"D{row}", r0["don_vi"], F_DAM, fill=FILL_HM, align=GIUA)
        o(ws, f"E{row}", Edm, F_DAM, "0.###", FILL_HM)
        if d and d.get("nguon"):
            ws[f"B{row}"].comment = Comment(f"Nguồn định mức: {d['nguon']}", "du-toan-vn")
        row += 1
        tl = ty_le_cho_ma(cfg, r0["ma_hieu"])
        hs_loai = {"VL": r0["hs_vl"], "NC": r0["hs_nc"], "M": r0["hs_m"]}
        sub = {}
        nhom = OrderedDict((("VL", "a) Vật liệu"), ("NC", "b) Nhân công"), ("M", "c) Máy thi công")))
        hao_phi = d["hao_phi"] if d else []
        if tg:
            hao_phi = [{"loai": "VL", "ma_tn": "", "ten_tn": "Đơn giá trọn gói (gộp vào vật liệu theo PL III TT 36/2026)",
                        "don_vi_tn": r0["don_vi"], "hao_phi": Edm, "he_so": 1.0, "_tg": r0["dg_tg"] or 0}]
        for loai, nhan in nhom.items():
            lines = [h for h in hao_phi if h["loai"] == loai]
            pct = [h for h in hao_phi if h["loai"] == ("VLK" if loai == "VL" else "MK" if loai == "M" else "_")]
            if not lines and not pct:
                continue
            srow = row
            o(ws, f"C{row}", nhan, F_DAM)
            row += 1
            l0 = row
            for h in lines:
                o(ws, f"B{row}", h["ma_tn"])
                o(ws, f"C{row}", h["ten_tn"], align=TRAI)
                o(ws, f"D{row}", h["don_vi_tn"], align=GIUA)
                o(ws, f"E{row}", h["hao_phi"], fmt=HP)
                hs = h["he_so"] * hs_loai[loai]
                o(ws, f"{L(cH)}{row}", hs, F_NHAP, "0.000", FILL_NHAP)
                if h.get("can_cu_he_so") or (abs(hs_loai[loai] - 1) > 1e-12 and r0["can_cu_hs"]):
                    ws[f"{L(cH)}{row}"].comment = Comment("; ".join(x for x in (h.get("can_cu_he_so", ""), r0["can_cu_hs"]) if x), "du-toan-vn")
                for k in range(nv):
                    if "_tg" in h:
                        o(ws, f"{L(cF+k)}{row}", h["_tg"], F_NHAP, TIEN, FILL_NHAP)
                    else:
                        o(ws, f"{L(cF+k)}{row}", "=" + f_gia(f"$B{row}", k), fmt=TIEN)
                    o(ws, f"{L(cI+k)}{row}", "=" + R(f"$E{row}*{L(cF+k)}{row}*${L(cH)}{row}"), fmt=TIEN)
                row += 1
            l1 = row - 1
            for h in pct:
                o(ws, f"C{row}", h["ten_tn"] or "Khác", align=TRAI)
                o(ws, f"D{row}", "%", align=GIUA)
                o(ws, f"E{row}", h["hao_phi"], fmt="0.###")
                for k in range(nv):
                    if lines:
                        o(ws, f"{L(cF+k)}{row}", f"=SUM({L(cI+k)}{l0}:{L(cI+k)}{l1})", fmt=TIEN)
                    else:
                        o(ws, f"{L(cF+k)}{row}", 0, fmt=TIEN)
                    o(ws, f"{L(cI+k)}{row}", "=" + R(f"$E{row}*{L(cF+k)}{row}/100"), fmt=TIEN)
                row += 1
            for k in range(nv):
                o(ws, f"{L(cI+k)}{srow}", "=" + R(f"SUM({L(cI+k)}{srow+1}:{L(cI+k)}{row-1})"), F_DAM, TIEN)
            sub[loai] = srow
        # chi phí trực tiếp và các khoản theo tỷ lệ
        rT = row
        o(ws, f"C{row}", "Cộng chi phí trực tiếp (VL + NC + M)", F_DAM)
        o(ws, f"D{row}", "T", F_DAM, align=GIUA)
        for k in range(nv):
            parts = "+".join(f"{L(cI+k)}{sub[x]}" for x in sub) or "0"
            o(ws, f"{L(cI+k)}{row}", "=" + R(parts), F_DAM, TIEN)
        row += 1

        def ty_le_o(key, ts_key, ref_row):
            v = tl[key]
            ov = (cfg.get("ty_le_theo_ma", {}) or {}).get(r0["ma_hieu"], {}).get(key)
            if ov:
                o(ws, f"E{ref_row}", so(ov["gia_tri"]), F_NHAP, PT, FILL_NHAP)
                ws[f"E{ref_row}"].comment = Comment(f"Tỷ lệ riêng cho mã này. Căn cứ: {ov.get('can_cu') or 'CHƯA GHI'}", "du-toan-vn")
            else:
                o(ws, f"E{ref_row}", f"={TS[ts_key]}", fmt=PT)
            return v

        rC = row
        v = ty_le_o("chi_phi_chung", "C", row)
        co_so_nc = v.get("co_so", "T").upper() == "NC"
        o(ws, f"C{row}", "Chi phí gián tiếp (tính trên chi phí nhân công – TT 40)" if la_tt40(cfg) else
          "Chi phí chung" + (" (tính trên chi phí nhân công)" if co_so_nc else " (tính trên chi phí trực tiếp)"))
        o(ws, f"D{row}", "C", align=GIUA)
        for k in range(nv):
            base = (f"{L(cI+k)}{sub['NC']}" if "NC" in sub else "0") if co_so_nc else f"{L(cI+k)}{rT}"
            if not (cfg.get("ty_le_theo_ma", {}) or {}).get(r0["ma_hieu"], {}).get("chi_phi_chung") and not co_so_nc:
                base = f'IF({TS["COSO"]}="NC",{L(cI+k)}{sub["NC"]},{L(cI+k)}{rT})' if "NC" in sub else f"{L(cI+k)}{rT}"
            o(ws, f"{L(cI+k)}{row}", "=" + R(f"{base}*$E{row}"), fmt=TIEN)
        row += 1
        rTT = row
        ty_le_o("cong_viec_khong_xd_kl", "TT", row)
        o(ws, f"C{row}", "(TT 40 không có khoản này)" if la_tt40(cfg) else "Chi phí một số công việc không xác định được khối lượng từ thiết kế", align=TRAI)
        o(ws, f"D{row}", "TT", align=GIUA)
        for k in range(nv):
            o(ws, f"{L(cI+k)}{row}", "=" + R(f"{L(cI+k)}{rT}*$E{row}"), fmt=TIEN)
        row += 1
        rGT = row
        o(ws, f"C{row}", "Cộng chi phí gián tiếp" if la_tt40(cfg) else "Cộng chi phí gián tiếp (C + TT)", F_DAM)
        o(ws, f"D{row}", "GT", F_DAM, align=GIUA)
        for k in range(nv):
            o(ws, f"{L(cI+k)}{row}", "=" + R(f"{L(cI+k)}{rC}+{L(cI+k)}{rTT}"), F_DAM, TIEN)
        row += 1
        rTL = row
        ty_le_o("thu_nhap_chiu_thue_tt", "TL", row)
        o(ws, f"C{row}", "Thu nhập chịu thuế tính trước (T + GT) × tỷ lệ")
        o(ws, f"D{row}", "TL", align=GIUA)
        for k in range(nv):
            o(ws, f"{L(cI+k)}{row}", "=" + R(f"({L(cI+k)}{rT}+{L(cI+k)}{rGT})*$E{row}"), fmt=TIEN)
        row += 1
        cong_them = ""
        if la_khao_sat(cfg):
            o(ws, f"C{row}", "Chi phí phục vụ công tác khảo sát", F_DAM)
            o(ws, f"D{row}", "Cpvks", F_DAM, align=GIUA)
            row += 1
            rPA = row
            for key, ts_key, ten, kh in (("lap_phuong_an_ks", "CPA", "Lập phương án kỹ thuật khảo sát (T + GT + TL) × tỷ lệ", "Cpa"),
                                         ("lap_bao_cao_ks", "CBC", "Lập báo cáo kết quả khảo sát (T + GT + TL) × tỷ lệ", "Cbc")):
                ty_le_o(key, ts_key, row)
                o(ws, f"C{row}", ten, align=TRAI)
                o(ws, f"D{row}", kh, align=GIUA)
                for k in range(nv):
                    o(ws, f"{L(cI+k)}{row}", "=" + R(f"({L(cI+k)}{rT}+{L(cI+k)}{rGT}+{L(cI+k)}{rTL})*$E{row}"), fmt=TIEN)
                row += 1
            cong_them = f"+{{c}}{rPA}+{{c}}{rPA + 1}"
        rG = row
        o(ws, f"C{row}", "Chi phí khảo sát trước thuế (T + GT + TL + Cpvks)" if la_khao_sat(cfg) else "Chi phí trước thuế (T + GT + TL)", F_DAM)
        o(ws, f"D{row}", "G", F_DAM, align=GIUA)
        for k in range(nv):
            c = L(cI + k)
            o(ws, f"{c}{row}", "=" + R(f"{c}{rT}+{c}{rGT}+{c}{rTL}" + cong_them.format(c=c)), F_DAM, TIEN)
        row += 1
        o(ws, f"C{row}", "Thuế giá trị gia tăng (G × TGTGT)")
        o(ws, f"D{row}", "GTGT", align=GIUA)
        o(ws, f"E{row}", f"={TS['VAT']}", fmt=PT)
        for k in range(nv):
            o(ws, f"{L(cI+k)}{row}", "=" + R(f"{L(cI+k)}{rG}*$E{row}"), fmt=TIEN)
        row += 1
        o(ws, f"C{row}", "Chi phí sau thuế (G + GTGT)")
        o(ws, f"D{row}", "Gxd", align=GIUA)
        for k in range(nv):
            o(ws, f"{L(cI+k)}{row}", f"={L(cI+k)}{rG}+{L(cI+k)}{row-1}", fmt=TIEN)
        row += 1
        cells = {}
        for k, v in enumerate(vids):
            o(ws, f"{L(cF+k)}{hrow}", "=" + R(f"{L(cI+k)}{rG}/$E{hrow}"), F_DAM, TIEN, FILL_HM)
            cells[v] = f"DGCT!${L(cF+k)}${hrow}"
        dg_o[bt] = cells
        row += 1

    # ------------------------------------------------ DT
    ws = ws_dt
    tieu_de(ws, "BẢNG DỰ TOÁN")
    cKL, cDG = 5, 5 + nd
    cTT = cDG + nv
    cTong = cTT + nd
    o(ws, "A6", "TT", F_DAM, fill=FILL_HDR, align=GIUA)
    o(ws, "B6", "Mã hiệu", F_DAM, fill=FILL_HDR, align=GIUA)
    o(ws, "C6", "Hạng mục công việc", F_DAM, fill=FILL_HDR, align=GIUA)
    o(ws, "D6", "Đơn vị", F_DAM, fill=FILL_HDR, align=GIUA)
    for k, d in enumerate(dids):
        o(ws, f"{L(cKL+k)}6", f"Khối lượng\n{doan[d][0]}", F_DAM, fill=FILL_HDR, align=GIUA)
        o(ws, f"{L(cTT+k)}6", f"Thành tiền\n{doan[d][0]}", F_DAM, fill=FILL_HDR, align=GIUA)
    for k, v in enumerate(vids):
        o(ws, f"{L(cDG+k)}6", f"Đơn giá\n{vung[v]}", F_DAM, fill=FILL_HDR, align=GIUA)
    o(ws, f"{L(cTong)}6", "Tổng thành tiền (đồng)", F_DAM, fill=FILL_HDR, align=GIUA)
    ws.row_dimensions[6].height = 75
    for i, w in enumerate([6, 16, 46, 9] + [12] * nd + [13] * nv + [15] * nd + [17], start=1):
        ws.column_dimensions[L(i)].width = w
    ws.freeze_panes = "E7"
    row = 7
    hm_o = OrderedDict()
    nhom_hm = OrderedDict()
    for (hm, stt), it in items.items():
        nhom_hm.setdefault(hm, []).append(it)
    dong_kl = {}
    for hm, its in nhom_hm.items():
        for c in range(1, cTong + 1):
            o(ws, f"{L(c)}{row}", fill=FILL_HM)
        o(ws, f"C{row}", f"HẠNG MỤC: {hm}", F_DAM, fill=FILL_HM)
        row += 1
        b0 = row
        for it in its:
            r0 = it["r"]
            o(ws, f"A{row}", r0["stt"], align=GIUA)
            o(ws, f"B{row}", r0["ma_hieu"])
            d = dl.dinh_muc.get(r0["ma_hieu"])
            o(ws, f"C{row}", r0["ten"] or (d["ten"] if d else ""), align=TRAI)
            o(ws, f"D{row}", r0["don_vi"], align=GIUA)
            cells = dg_o[bien_the(r0)]
            for k, v in enumerate(vids):
                o(ws, f"{L(cDG+k)}{row}", f"={cells[v]}", fmt=TIEN)
            parts = []
            for k, dd in enumerate(dids):
                q = it["kl"].get(dd, 0.0)
                o(ws, f"{L(cKL+k)}{row}", q, F_NHAP, KL, FILL_NHAP)
                v = doan[dd][1] or vids[0]
                kv = vids.index(v) if v in vids else 0
                o(ws, f"{L(cTT+k)}{row}", "=" + R(f"${L(cKL+k)}{row}*${L(cDG+kv)}{row}"), fmt=TIEN)
                parts.append(f"{L(cTT+k)}{row}")
            o(ws, f"{L(cTong)}{row}", "=" + R(f"SUM({L(cTT)}{row}:{L(cTT+nd-1)}{row})"), F_DAM, TIEN)
            for rr in it["dong"]:
                dong_kl[id(rr)] = row
            row += 1
        b1 = row - 1
        o(ws, f"C{row}", "Cộng chi phí trước thuế", F_DAM)
        for c in list(range(cTT, cTT + nd)) + [cTong]:
            o(ws, f"{L(c)}{row}", "=" + R(f"SUM({L(c)}{b0}:{L(c)}{b1})"), F_DAM, TIEN)
        rtt = row
        row += 1
        o(ws, f"C{row}", "Thuế giá trị gia tăng", F_DAM)
        for c in list(range(cTT, cTT + nd)) + [cTong]:
            o(ws, f"{L(c)}{row}", "=" + R(f"{L(c)}{rtt}*{TS['VAT']}"), F_DAM, TIEN)
        row += 1
        o(ws, f"C{row}", "Cộng chi phí sau thuế", F_DAM)
        for c in list(range(cTT, cTT + nd)) + [cTong]:
            o(ws, f"{L(c)}{row}", "=" + R(f"{L(c)}{rtt}+{L(c)}{row-1}"), F_DAM, TIEN)
        hm_o[hm] = {"tt": f"DT!${L(cTong)}${rtt}", "vat": f"DT!${L(cTong)}${rtt+1}", "st": f"DT!${L(cTong)}${row}"}
        row += 2

    # ------------------------------------------------ TDT
    ws = ws_tdt
    tieu_de(ws, "BẢNG TỔNG HỢP DỰ TOÁN")
    hdr = ["STT", "Nội dung chi phí", "Tỷ lệ", "Hệ số", "Cách tính", "Giá trị trước thuế", "Thuế GTGT", "Giá trị sau thuế", "Căn cứ / ghi chú"]
    for i, (h, w) in enumerate(zip(hdr, (7, 46, 10, 8, 26, 18, 16, 18, 42)), start=1):
        o(ws, f"{L(i)}6", h, F_DAM, fill=FILL_HDR, align=GIUA)
        ws.column_dimensions[L(i)].width = w
    ws["I5"] = "Đơn vị tính: đồng"
    ws["I5"].font = F_NHO
    th = py["tong_hop"]["items"]
    hang = {it["ma"]: 7 + i for i, it in enumerate(th)}
    ten = {it["ma"]: (it.get("stt") or it["ma"]) for it in th}
    for it in th:
        r = hang[it["ma"]]
        k = it.get("kieu", "ty_le")
        dam = F_DAM if it.get("dam") or k == "tong" else F_TH
        o(ws, f"A{r}", it.get("stt", ""), dam, align=GIUA)
        o(ws, f"B{r}", it["ten"], dam, align=TRAI)
        o(ws, f"C{r}", "")
        o(ws, f"D{r}", "")
        o(ws, f"I{r}", it.get("can_cu", ""), F_NHO, align=TRAI)
        co_vat = it.get("vat", True)
        if k == "hang_muc":
            refs = [hm_o[h]["tt"] for h in it["hang_muc"] if h in hm_o]
            o(ws, f"E{r}", "Bảng dự toán: " + ", ".join(it["hang_muc"]), align=TRAI)
            o(ws, f"F{r}", "=" + R("+".join(refs) or "0"), dam, TIEN)
            o(ws, f"G{r}", "=" + R(f"F{r}*{TS['VAT']}") if co_vat else 0, dam, TIEN)
        elif k == "gia_tri":
            o(ws, f"E{r}", "Giá trị nhập", align=TRAI)
            o(ws, f"F{r}", so(it.get("gia_tri"), 0), F_NHAP, TIEN, FILL_NHAP)
            o(ws, f"G{r}", "=" + R(f"F{r}*{TS['VAT']}") if co_vat else 0, dam, TIEN)
        elif k == "tong":
            o(ws, f"E{r}", " + ".join(ten[m] for m in it["gom"]), align=TRAI)
            o(ws, f"F{r}", "=" + R("+".join(f"F{hang[m]}" for m in it["gom"])), dam, TIEN)
            o(ws, f"G{r}", "=" + R("+".join(f"G{hang[m]}" for m in it["gom"])), dam, TIEN)
        else:
            o(ws, f"C{r}", so(it.get("ty_le"), 0), F_NHAP, "0.000%", FILL_NHAP)
            o(ws, f"D{r}", so(it.get("he_so"), 1), F_NHAP, "0.###", FILL_NHAP)
            base_f, base_g, mo_ta = [], [], []
            for b in it.get("co_so", []):
                if isinstance(b, (int, float)):
                    base_f.append(f"{b}")
                    mo_ta.append(f"{b:,.0f}".replace(",", "."))
                else:
                    base_f.append(f"F{hang[b]}")
                    base_g.append(f"G{hang[b]}")
                    mo_ta.append(ten[b])
            raw = f"$C{r}*$D{r}*({'+'.join(base_f) or 0})"
            if it.get("toi_thieu") is not None:
                raw = f"MAX({raw},{it['toi_thieu']})"
            if it.get("toi_da") is not None:
                raw = f"MIN({raw},{it['toi_da']})"
            gh = ""
            if it.get("toi_thieu") is not None or it.get("toi_da") is not None:
                gh = f" (tối thiểu {it.get('toi_thieu')}, tối đa {it.get('toi_da')})"
            o(ws, f"E{r}", "Tỷ lệ × hệ số × (" + " + ".join(mo_ta) + ")" + gh, align=TRAI)
            if it.get("tren_sau_thue"):
                # (G + GTGT) × tỷ lệ, rồi tách phần trước thuế (cách của mẫu đơn vị, đúng nguyên văn PL V TT 36)
                o(ws, f"E{r}", "Tỷ lệ × hệ số × (" + " + ".join(mo_ta) + ") sau thuế; tách trước thuế = sau thuế / (1 + TGTGT)", align=TRAI)
                o(ws, f"H{r}", "=" + R(f"$C{r}*$D{r}*({'+'.join(base_f + base_g) or 0})"), dam, TIEN)
                o(ws, f"F{r}", "=" + R(f"H{r}/(1+{TS['VAT']})"), dam, TIEN)
                o(ws, f"G{r}", f"=H{r}-F{r}", dam, TIEN)
                continue
            o(ws, f"F{r}", "=" + R(raw), dam, TIEN)
            if co_vat == "theo_co_so":
                o(ws, f"G{r}", "=" + R(f"$C{r}*$D{r}*({'+'.join(base_g) or 0})"), dam, TIEN)
            else:
                o(ws, f"G{r}", "=" + R(f"F{r}*{TS['VAT']}") if co_vat else 0, dam, TIEN)
            if it.get("he_so") not in (None, 1, 1.0) and it.get("can_cu_he_so"):
                ws[f"D{r}"].comment = Comment(it["can_cu_he_so"], "du-toan-vn")
        o(ws, f"H{r}", "=" + R(f"F{r}+G{r}"), dam, TIEN)
    cuoi = 7 + len(th)
    tong_ma = next((it["ma"] for it in th[::-1] if it.get("kieu") == "tong"), None)
    if tong_ma:
        v = py["tong_hop"]["gia_tri"][tong_ma][2]
        so_vn = f"{v:,.0f}".replace(",", ".")
        ws[f"B{cuoi+1}"] = f"Bằng chữ (theo giá trị lúc xuất file: {so_vn} đồng): {doc_so_tien(v)}"
        ws[f"B{cuoi+1}"].font = Font(name=FONT, size=11, italic=True)
    ws[f"B{cuoi+3}"] = "NGƯỜI LẬP"
    ws[f"G{cuoi+3}"] = "NGƯỜI CHỦ TRÌ"
    ws[f"B{cuoi+6}"] = cfg.get("nguoi_lap", "")
    ws[f"G{cuoi+6}"] = cfg.get("nguoi_chu_tri", "")
    for ref in (f"B{cuoi+3}", f"G{cuoi+3}", f"B{cuoi+6}", f"G{cuoi+6}"):
        ws[ref].font = F_DAM
        ws[ref].alignment = GIUA

    # ------------------------------------------------ KL_DIEN_GIAI
    ws = ws_kl
    tieu_de(ws, "BẢNG KHỐI LƯỢNG VÀ DIỄN GIẢI")
    hdr = ["STT", "Hạng mục", "Mã hiệu", "Đoạn", "Đơn vị", "Khối lượng", "Diễn giải", "Nguồn bản vẽ", "Trạng thái"]
    for i, (h, w) in enumerate(zip(hdr, (8, 22, 18, 30, 9, 12, 50, 20, 11)), start=1):
        o(ws, f"{L(i)}6", h, F_DAM, fill=FILL_HDR, align=GIUA)
        ws.column_dimensions[L(i)].width = w
    for i, r in enumerate(kl_rows, start=7):
        vals = [r["stt"], r["hang_muc"], r["ma_hieu"], doan.get(r["doan"], (r["doan"],))[0], r["don_vi"], r["kl"],
                r["dien_giai"], r["ban_ve"], r["trang_thai"]]
        for c, v in enumerate(vals, start=1):
            o(ws, f"{L(c)}{i}", v, fmt=KL if c == 6 else None, align=TRAI if c in (2, 4, 7) else None)

    if soat_kq:
        ws = wb.create_sheet("CANH_BAO")
        tieu_de(ws, "KẾT QUẢ SOÁT")
        for i, (h, w) in enumerate(zip(("Mã", "Mức", "Nội dung"), (7, 12, 120)), start=1):
            o(ws, f"{L(i)}6", h, F_DAM, fill=FILL_HDR, align=GIUA)
            ws.column_dimensions[L(i)].width = w
        thu_tu = {"CHAN": 0, "CANH_BAO": 1, "THONG_TIN": 2}
        for i, (ma, muc, nd_) in enumerate(sorted(soat_kq, key=lambda x: (thu_tu[x[1]], x[0])), start=7):
            o(ws, f"A{i}", ma)
            o(ws, f"B{i}", muc, F_DO if muc == "CHAN" else F_TH)
            o(ws, f"C{i}", nd_, align=TRAI)

    for w in wb.worksheets:
        w.sheet_view.showGridLines = False
        w.page_setup.orientation = "landscape"
        w.page_setup.paperSize = w.PAPERSIZE_A3 if w.title == "DT" else w.PAPERSIZE_A4
        w.page_setup.fitToWidth = 1
        w.page_setup.fitToHeight = 0
        w.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(path)
