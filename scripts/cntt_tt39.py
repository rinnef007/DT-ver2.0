"""Tổng mức đầu tư / dự toán dự án chuyển đổi số (CNTT) dùng NSNN theo NĐ 224/2026/NĐ-CP Điều 49 và TT 39/2026/TT-BKHCN Điều 5.

  G   = GTB + GQLDA + GTV + GK + GDP
  GTB = GMS + GCSDL + GLĐ + GĐT + GTK + GVC + GK_TB
  GDP = (GTB + GQLDA + GTV + GK) × Kdp   (Kdp ≤ 10 % tổng mức, 7 % dự toán, 5 % BCKTKT)

Phần tính bằng định mức (NĐ 224 Điều 49 k4 điểm đ — định mức chuyên ngành, data/chuyen-nganh): khoi_luong.csv,
mỗi dòng ma_hieu, khoi_luong, khoan_muc (GLD | GCSDL; trống: QĐ 1595 → GCSDL, còn lại → GLD).
Các khoản khác nhập trong config["khoan_muc"] (giá trị + phương pháp + căn cứ) hoặc config["chuyen_gia"]
(phương pháp chuyên gia, PL mục III TT 39: CTV = CCG + CQL + CK + TN + VAT; CQL theo Bảng 3.2; TN = 6 %).

Dùng: python scripts/cntt_tt39.py --data data/vi-du-cntt [--ra tong_hop_cntt.xlsx]
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dutoan_core import DuLieu, doc_csv  # noqa: E402

PHUONG_PHAP = {
    "bao_gia": "Báo giá (NĐ 224 Đ49 k4a)", "ket_qua_lcnt": "Kết quả LCNT tương tự (Đ49 k4b)",
    "tham_dinh_gia": "Thẩm định giá (Đ49 k4c)", "gia_niem_yet": "Giá niêm yết (Đ49 k4d)",
    "dinh_muc": "Định mức chuyên ngành (Đ49 k4đ)", "ket_hop": "Kết hợp (Đ49 k4e)",
    "chuyen_gia": "Chuyên gia tư vấn (Đ49 k5c; PL mục III TT 39)", "tu_thuc_hien": "Tự thực hiện (Đ49 k6; TT 39 Đ5 k6)",
    "theo_quy_dinh": "Theo quy định riêng (kiểm toán, thẩm tra quyết toán, phí, lệ phí…)",
}
KM_TB = ["GMS", "GCSDL", "GLD", "GDT", "GTK", "GVC", "GK_TB"]
TEN_KM = {"GMS": "Chi phí mua sắm trang thiết bị công nghệ số", "GCSDL": "Chi phí tạo lập cơ sở dữ liệu",
          "GLD": "Chi phí lắp đặt, cài đặt, kiểm tra, hiệu chỉnh; lắp đặt mạng", "GDT": "Chi phí đào tạo, tập huấn",
          "GTK": "Chi phí triển khai, tích hợp, kết nối, hỗ trợ, quản trị, vận hành trước bàn giao",
          "GVC": "Chi phí vận chuyển, bảo hiểm thiết bị", "GK_TB": "Chi phí khác có liên quan của chi phí trang thiết bị",
          "GQLDA": "Chi phí quản lý dự án", "GTV": "Chi phí tư vấn đầu tư", "GK": "Chi phí khác", "GDP": "Chi phí dự phòng"}
KDP_TOI_DA = {"tong_muc": 0.10, "du_toan": 0.07, "bcktkt": 0.05}


def ty_le_cql(ccg):
    """Bảng 3.2 PL TT 39: CCG ≤ 1 tỷ: 55 %; 1 < CCG < 5 tỷ: 50 %; CCG ≥ 5 tỷ: 45 %."""
    t = ccg / 1e9
    return 0.55 if t <= 1 else (0.50 if t < 5 else 0.45)


def chi_phi_chuyen_gia(c):
    ccg, ck = float(c.get("ccg", 0)), float(c.get("ck", 0))
    if c.get("ca_nhan"):
        return dict(CCG=ccg, CQL=0.0, CK=ck, TN=0.0, VAT=0.0, CTV=ccg + ck, ty_le_cql=0.0)
    cql = ccg * ty_le_cql(ccg)
    tn = 0.06 * (ccg + cql + ck)
    vat = float(c.get("vat", 0.0)) * (ccg + cql + ck + tn)
    return dict(CCG=ccg, CQL=cql, CK=ck, TN=tn, VAT=vat, CTV=ccg + cql + ck + tn + vat, ty_le_cql=ty_le_cql(ccg))


def tinh(thu_muc, cfg_path=None, kl_path=None):
    cfg = json.load(open(cfg_path or os.path.join(thu_muc, "config_cntt.json"), encoding="utf-8"))
    dl = DuLieu(thu_muc)
    vung = cfg.get("vung_gia", "")
    soat = []
    kl = doc_csv(kl_path or os.path.join(thu_muc, "khoi_luong.csv")) or []
    chung = cfg.get("dinh_muc_chi_phi_chung", {}) or {}
    tnct = cfg.get("dinh_muc_thu_nhap", {}) or {}
    tl_c, tl_t = float(chung.get("ty_le", 0) or 0), float(tnct.get("ty_le", 0) or 0)
    thue = float(cfg.get("thue_gtgt_dinh_muc", 0.1))
    chi_tiet, tong = [], {k: 0.0 for k in KM_TB + ["GQLDA", "GTV", "GK"]}
    thieu = set()
    for i, r in enumerate(kl, start=1):
        ma = r["ma_hieu"].strip()
        d = dl.dinh_muc.get(ma)
        if not d:
            soat.append(("CHAN", f"Dòng {i}: mã {ma} không có trong định mức hồ sơ, TT 38 hay chuyên ngành")); continue
        q = float(r["khoi_luong"])
        km = (r.get("khoan_muc") or "").strip().upper() or ("GCSDL" if d.get("phu_luc") == "CNTT-1595" else "GLD")
        if km not in ("GLD", "GCSDL"):
            soat.append(("CHAN", f"Dòng {i} ({ma}): khoan_muc '{km}' — chỉ GLD hoặc GCSDL tính bằng định mức")); continue
        vl = nc = m = 0.0; pct_vl = pct_m = 0.0
        for h in d["hao_phi"]:
            hp = h["hao_phi"] * h.get("he_so", 1.0)
            if h["loai"] == "VLK":
                pct_vl += hp; continue
            if h["loai"] == "MK":
                pct_m += hp; continue
            g = dl.gia_cua(h["ma_tn"], vung)
            if not g:
                thieu.add((h["loai"], h["ma_tn"], h["don_vi_tn"])); continue
            v = hp * g["don_gia"]
            if h["loai"] == "VL":
                vl += v
            elif h["loai"] == "NC":
                nc += v
            else:
                m += v
        vl *= 1 + pct_vl / 100; m *= 1 + pct_m / 100
        t = vl + nc + m
        c = t * tl_c; tl = (t + c) * tl_t
        dg = t + c + tl
        chi_tiet.append(dict(stt=i, ma=ma, ten=d["ten"], don_vi=d["don_vi"], khoi_luong=q, khoan_muc=km, VL=vl, NC=nc, M=m,
                             T=t, C=c, TL=tl, don_gia=dg, thanh_tien=dg * q, nguon=d.get("nguon", "")))
        tong[km] += dg * q * (1 + thue)
    for (lo, ten, dv) in sorted(thieu):
        soat.append(("CHAN", f"Thiếu giá {lo} '{ten}' ({dv}) trong gia_tai_nguyen.csv (vùng '{vung}')"))
    if chi_tiet:
        soat.append(("THONG_TIN", "Phần GLĐ/GCSDL tính bằng định mức chuyên ngành — phương pháp NĐ 224/2026 Điều 49 k4 điểm đ; ghi căn cứ trong thuyết minh. "
                     "Nhân công đã chọn nhóm theo data/chuyen-nganh/anh_xa_nhan_cong.csv (TT 37 Điều 2 k3); kỹ sư CNTT có thể định giá theo TT 07/2026/TT-BNV hoặc báo giá"))
        if not tl_c and not tl_t:
            soat.append(("CANH_BAO", "Chưa tính chi phí chung, thu nhập chịu thuế tính trước cho phần định mức: TT 39 không quy định tỷ lệ cho phương pháp định mức "
                         "(báo giá thì gộp các khoản này) — nếu tính, ghi dinh_muc_chi_phi_chung/dinh_muc_thu_nhap kèm căn cứ"))
        for k, v in (("dinh_muc_chi_phi_chung", chung), ("dinh_muc_thu_nhap", tnct)):
            if float(v.get("ty_le", 0) or 0) and not v.get("can_cu"):
                soat.append(("CHAN", f"{k}: có tỷ lệ nhưng thiếu căn cứ"))
    bang = []
    for km in cfg.get("khoan_muc", []):
        ma, gt = km["ma"].upper(), float(km.get("gia_tri", 0))
        pp = km.get("phuong_phap", "")
        if ma not in tong:
            soat.append(("CHAN", f"khoan_muc '{ma}' không hợp lệ ({', '.join(tong)})")); continue
        if pp not in PHUONG_PHAP:
            soat.append(("CHAN", f"{ma} – {km.get('ten', '')}: phương pháp '{pp}' không thuộc NĐ 224 Điều 49 k4–k6 ({', '.join(PHUONG_PHAP)})"))
        if not km.get("can_cu"):
            soat.append(("CANH_BAO", f"{ma} – {km.get('ten', '')}: thiếu căn cứ (số báo giá, gói thầu tương tự, chứng thư thẩm định…)"))
        if pp == "bao_gia" and int(km.get("so_bao_gia", 1)) < 2 and not km.get("ly_do_mot_bao_gia"):
            soat.append(("CANH_BAO", f"{ma} – {km.get('ten', '')}: chỉ 01 báo giá — PL mục I.1 TT 39 yêu cầu nêu rõ lý do"))
        if pp == "ket_qua_lcnt" and int(km.get("so_thang_truoc", 0)) > 12:
            soat.append(("CHAN", f"{ma} – {km.get('ten', '')}: kết quả LCNT quá 12 tháng (PL mục II.1 TT 39)"))
        tong[ma] += gt
        bang.append(dict(ma=ma, ten=km.get("ten", TEN_KM.get(ma, "")), gia_tri=gt, phuong_phap=PHUONG_PHAP.get(pp, pp), can_cu=km.get("can_cu", "")))
    for c in cfg.get("chuyen_gia", []):
        ma = c["ma"].upper()
        kq = chi_phi_chuyen_gia(c)
        if ma not in tong:
            soat.append(("CHAN", f"chuyen_gia '{ma}' không hợp lệ")); continue
        tong[ma] += kq["CTV"]
        bang.append(dict(ma=ma, ten=c.get("ten", ""), gia_tri=kq["CTV"], phuong_phap=PHUONG_PHAP["chuyen_gia"],
                         can_cu=f"CCG {kq['CCG']:,.0f} (TT 07/2026/TT-BNV) + CQL {kq['ty_le_cql']:.0%} (Bảng 3.2) + CK {kq['CK']:,.0f} + TN 6 % + VAT {kq['VAT']:,.0f}"
                         + (" — cá nhân: không tính CQL, TN, VAT" if c.get("ca_nhan") else "") + (f"; {c['can_cu']}" if c.get("can_cu") else "")))
    gtb = sum(tong[k] for k in KM_TB)
    loai = cfg.get("loai_ho_so", "du_toan")
    kdp = float(cfg.get("kdp", 0))
    if loai not in KDP_TOI_DA:
        soat.append(("CHAN", f"loai_ho_so '{loai}' (tong_muc | du_toan | bcktkt)")); loai = "du_toan"
    if kdp > KDP_TOI_DA[loai] + 1e-12:
        soat.append(("CHAN", f"Kdp {kdp:.0%} vượt tối đa {KDP_TOI_DA[loai]:.0%} cho {loai} (TT 39 Điều 5 k5)"))
    gdp = (gtb + tong["GQLDA"] + tong["GTV"] + tong["GK"]) * kdp
    g = gtb + tong["GQLDA"] + tong["GTV"] + tong["GK"] + gdp
    if not tong["GQLDA"]:
        soat.append(("CANH_BAO", "Chưa có GQLDA — CĐT tự thực hiện: TT 70/2024/TT-BTC; giám sát, đánh giá đầu tư: NĐ 19/2026 (TT 39 Điều 5 k6 c, d)"))
    tong_hop = [(k, TEN_KM[k], tong[k]) for k in KM_TB] + [("GTB", "Chi phí trang thiết bị", gtb)] + \
               [(k, TEN_KM[k], tong[k]) for k in ("GQLDA", "GTV", "GK")] + [("GDP", f"{TEN_KM['GDP']} (Kdp {kdp:.0%})", gdp), ("G", "TỔNG CỘNG", g)]
    return dict(cfg=cfg, chi_tiet=chi_tiet, bang=bang, tong_hop=tong_hop, G=g, GTB=gtb, GDP=gdp, soat=soat, thue=thue)


def xuat_excel(kq, path):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook(); ws = wb.active; ws.title = "Tong hop"
    ws.append([kq["cfg"].get("du_an", ""), "", "TT 39/2026/TT-BKHCN Điều 5; NĐ 224/2026/NĐ-CP Điều 49"]); ws["A1"].font = Font(bold=True)
    ws.append(["Mã", "Khoản mục chi phí", "Giá trị (đồng)"])
    for k, t, v in kq["tong_hop"]:
        ws.append([k, t, round(v)])
    ws2 = wb.create_sheet("Khoan muc"); ws2.append(["Mã", "Nội dung", "Giá trị", "Phương pháp", "Căn cứ"])
    for b in kq["bang"]:
        ws2.append([b["ma"], b["ten"], round(b["gia_tri"]), b["phuong_phap"], b["can_cu"]])
    ws3 = wb.create_sheet("Chi tiet dinh muc")
    cols = ["stt", "ma", "ten", "don_vi", "khoi_luong", "khoan_muc", "VL", "NC", "M", "T", "C", "TL", "don_gia", "thanh_tien", "nguon"]
    ws3.append(cols)
    for r in kq["chi_tiet"]:
        ws3.append([round(r[c]) if isinstance(r[c], float) and c not in ("khoi_luong",) else r[c] for c in cols])
    ws3.append(["", "", f"Cộng (chưa VAT); VAT {kq['thue']:.0%} cộng vào GLĐ/GCSDL ở bảng tổng hợp"])
    ws4 = wb.create_sheet("Soat"); ws4.append(["Mức", "Nội dung"])
    for m, t in kq["soat"]:
        ws4.append([m, t])
    wb.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True); ap.add_argument("--config"); ap.add_argument("--khoi-luong"); ap.add_argument("--ra")
    a = ap.parse_args()
    kq = tinh(a.data, a.config, a.khoi_luong)
    for k, t, v in kq["tong_hop"]:
        print(f"{k:6} {t[:70]:72} {v:>18,.0f}")
    for m, t in kq["soat"]:
        print(f"[{m}] {t}")
    if a.ra:
        xuat_excel(kq, a.ra); print("Đã ghi", a.ra)
    sys.exit(1 if any(m == "CHAN" for m, _ in kq["soat"]) else 0)


if __name__ == "__main__":
    main()
