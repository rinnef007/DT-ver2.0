#!/usr/bin/env python3
"""Soát nhanh một file Excel dự toán / khối lượng có sẵn (của mình hoặc do tư vấn lập).

  python soat_file_excel.py du_toan.xlsx [khoi_luong.xlsx ...] [--ra bao_cao.md] [--ca-sheet-an]

Kiểm tra (không sửa file):
  E1  Ô lỗi (#REF!, #N/A, #VALUE!, #DIV/0!, #NAME?) theo sheet
  E2  Liên kết tới file ngoài ([1], [2]…) — giá trị phụ thuộc file khác
  E3  Hàm tồn dư từ Google Sheets (__xludf.DUMMYFUNCTION) — giá trị là bản lưu tạm
  E4  Số lưu dạng chữ trong cột số (riêng bảng tra cứu tỷ lệ: số dạng chữ dấu phẩy thập phân, kiểm tra VLOOKUP)
  E5  Số nhập tay giữa các ô công thức cùng cột (dễ quên cập nhật)
  E6  Sheet ẩn: liệt kê, sheet ẩn có lỗi hoặc nội dung của công trình khác (kèm tối đa 6 tọa độ mẫu/sheet)
  E7  Văn bản trích dẫn đã hết hiệu lực từ 01/7/2026 (NĐ 10/2021, TT 11/12/13/2021…) — trừ hồ sơ chuyển tiếp
  E8  Thuế suất GTGT ghi khác nhau giữa các sheet đang hiển thị
  E9  Ký hiệu "LT" dùng cho chi phí một số công việc không xác định được khối lượng (theo Bảng 3.8 PL III TT 36/2026 là "TT")
  E10 Công thức tổng hợp SUM sai phạm vi so với nhãn/cách tính của dòng (bảng có cột "CÁCH TÍNH" + "KÝ HIỆU")
  E11 Ô giá trị trống giữa các công thức trong bảng tổng hợp (dòng có nhãn + cách tính nhưng thiếu công thức)
  E12 Nhãn/cách tính mâu thuẫn công thức tham chiếu (cách tính ghi thành phần mà dòng được tham chiếu không có)
File .xls được chuyển sang .xlsx bằng LibreOffice trước khi đọc.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict

try:
    import openpyxl
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("Thiếu openpyxl")

LOI = ("#REF!", "#N/A", "#VALUE!", "#DIV/0!", "#NAME?", "#NUM!", "#NULL!")
VB_HET_HIEU_LUC = [
    (r"10/2021/N[ĐD]-CP", "NĐ 10/2021/NĐ-CP (thay bởi NĐ 206/2026/NĐ-CP)"),
    (r"11/2021/TT-BXD", "TT 11/2021/TT-BXD (thay bởi TT 36/2026/TT-BXD)"),
    (r"12/2021/TT-BXD", "TT 12/2021/TT-BXD (thay bởi TT 38/2026/TT-BXD)"),
    (r"13/2021/TT-BXD", "TT 13/2021/TT-BXD (thay bởi TT 37/2026/TT-BXD)"),
    (r"09/2024/TT-BXD", "TT 09/2024/TT-BXD (thay bởi TT 38/2026/TT-BXD)"),
    (r"08/2025/TT-BXD", "TT 08/2025/TT-BXD (thay bởi TT 38/2026/TT-BXD)"),
    (r"14/2023/TT-BXD", "TT 14/2023/TT-BXD (bãi bỏ bởi TT 36/2026/TT-BXD)"),
    (r"14/2021/TT-BXD", "TT 14/2021/TT-BXD (bãi bỏ bởi TT 40/2026/TT-BXD — chi phí bảo trì)"),
    (r"01/2025/TT-BXD", "TT 01/2025/TT-BXD (thay bởi TT 37/2026/TT-BXD)"),
    (r"60/2025/TT-BXD", "TT 60/2025/TT-BXD (Điều 1, 2, PL III, PL V và một số khoản được thay/bãi bỏ bởi TT 36, 37, 38/2026 — kiểm tra phần viện dẫn)"),
]


def mo(path):
    if path.lower().endswith(".xls"):
        tmp = tempfile.mkdtemp()
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmp, path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        path = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".xlsx")
    # keep_links=False: một số file có phần liên kết ngoài hỏng làm openpyxl dừng; công thức vẫn giữ tham chiếu [n] để soát
    return (openpyxl.load_workbook(path, data_only=True, keep_links=False),
            openpyxl.load_workbook(path, data_only=False, keep_links=False))


def la_so_chu(v):
    return isinstance(v, str) and re.fullmatch(r"\s*-?\d{1,3}([.,]\d{3})*([.,]\d+)?\s*|\s*-?\d+([.,]\d+)?\s*", v) is not None


def _bo_dau(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def la_bang_tra_cuu(ten_sheet):
    """Sheet tra cứu tỷ lệ/bảng tra (vd. DMTL) — số dạng chữ ở đây có thể làm VLOOKUP đọc sai."""
    t = _bo_dau(ten_sheet)
    return any(k in t for k in ("dmtl", "tra cuu", "bang tra", "ty le", "bang ty le"))


def _tokens_cach_tinh(text, ky_hieu):
    """Các ký hiệu chi phí trong chuỗi cách tính (đã tính) mà có trong bảng ký hiệu của bảng tổng hợp.
    Trả về danh sách theo thứ tự xuất hiện trong nhãn (không sắp xếp lại)."""
    if not text:
        return []
    out = []
    for t in re.findall(r"[A-Z][A-Z0-9]{0,5}", str(text).upper()):
        if t in ky_hieu and t not in out:
            out.append(t)
    return out


def kiem_tra_bang_tong_hop(ws_f, ws_v, ten):
    """E10/E11/E12 — chỉ áp cho bảng tổng hợp có cả hai cột "CÁCH TÍNH" và "KÝ HIỆU"
    (kiểu THCP của GXD và TH_CPXD của skill): cột giá trị nằm ngay sau cột cách tính,
    cột ký hiệu cho biết mỗi dòng là thành phần nào (VL, NC, M, C, TT, TL…).
    Trả dict {"E10": [...], "E11": [...], "E12": [...]}."""
    out = {"E10": [], "E11": [], "E12": []}
    max_row, max_col = ws_f.max_row, ws_f.max_column
    for hr in range(1, max_row + 1):
        vals = [ws_f.cell(hr, c).value for c in range(1, max_col + 1)]
        norm = [_bo_dau(v) for v in vals]
        if not any("cach tinh" in v for v in norm) or not any("ky hieu" in v for v in norm):
            continue
        c_ct = next(i + 1 for i, v in enumerate(norm) if "cach tinh" in v)
        c_kh = next(i + 1 for i, v in enumerate(norm) if "ky hieu" in v)
        c_gt = c_ct + 1
        c_nd = c_ct - 1
        if c_gt > max_col or c_nd < 1:
            continue
        ky_hieu = {}
        block = []
        r = hr + 1
        while r <= max_row:
            nd = ws_v.cell(r, c_nd).value
            ct = ws_v.cell(r, c_ct).value
            gt_f = ws_f.cell(r, c_gt).value
            kh = ws_v.cell(r, c_kh).value
            if all(v is None or (isinstance(v, str) and not v.strip()) for v in (nd, ct, gt_f, kh)):
                break
            block.append(r)
            if isinstance(kh, str) and re.fullmatch(r"[A-Z][A-Z0-9]{0,5}", kh.strip()):
                ky_hieu.setdefault(kh.strip(), []).append(r)
            r += 1
        if not ky_hieu:
            continue
        tap_kh = set(ky_hieu)
        for r in block:
            ct_v = ws_v.cell(r, c_ct).value
            gt_f = ws_f.cell(r, c_gt).value
            toks = _tokens_cach_tinh(ct_v, tap_kh)
            if isinstance(gt_f, str) and gt_f.strip().startswith("="):
                f = gt_f.strip()
                m = re.fullmatch(r"=SUM\(\$?([A-Z]{1,3})\$?(\d+):\$?([A-Z]{1,3})\$?(\d+)\)", f, re.I)
                if m and m.group(1).upper() == m.group(3).upper() == get_column_letter(c_gt):
                    r1, r2 = int(m.group(2)), int(m.group(4))
                    if toks:
                        dong_mong, mo_ho = [], False
                        for t in toks:
                            rs = ky_hieu.get(t, [])
                            if len(rs) != 1:
                                mo_ho = True
                                break
                            dong_mong.append(rs[0])
                        if not mo_ho and dong_mong and (sorted(dong_mong) != list(range(r1, r2 + 1))):
                            out["E10"].append(f"`{ten}`!{get_column_letter(c_gt)}{r}: nhãn ghi {'+'.join(toks)} "
                                              f"(dòng {', '.join(str(x) for x in sorted(dong_mong))}) nhưng công thức `{f}` "
                                              f"cộng dòng {r1}–{r2}")
                m2 = re.fullmatch(r"=\$?([A-Z]{1,3})\$?(\d+)", f, re.I)
                if m2 and m2.group(1).upper() == get_column_letter(c_gt):
                    rr = int(m2.group(2))
                    # Dòng được tham chiếu có thể ở bảng khác trong cùng sheet (vd. bảng 2 tham chiếu bảng 1):
                    # chỉ cần dòng đó có cách tính với ký hiệu để đối chiếu.
                    if toks and rr != r and 1 <= rr <= max_row:
                        toks_ref = _tokens_cach_tinh(ws_v.cell(rr, c_ct).value, tap_kh)
                        if toks_ref:
                            thieu = set(toks) - set(toks_ref)
                            if thieu:
                                out["E12"].append(f"`{ten}`!{get_column_letter(c_gt)}{r}: nhãn ghi {'+'.join(toks)} "
                                                  f"nhưng công thức `{f}` tham chiếu dòng {rr} (nhãn dòng đó: "
                                                  f"{'+'.join(toks_ref)}) — thiếu {', '.join(sorted(thieu))}")
            if gt_f is None and ws_v.cell(r, c_gt).value is None and ct_v not in (None, "") \
                    and ws_v.cell(r, c_nd).value not in (None, ""):
                def _co_ct(rr):
                    v = ws_f.cell(rr, c_gt).value
                    return rr in block and isinstance(v, str) and v.startswith("=")
                if _co_ct(r - 1) and _co_ct(r + 1):
                    out["E11"].append(f"`{ten}`!{get_column_letter(c_gt)}{r}: ô giá trị trống giữa các công thức "
                                      f"(dòng {r - 1} và {r + 1} có công thức) — {str(ws_v.cell(r, c_nd).value)[:60]}")
    return out


def soat_file(path, ca_sheet_an=False):
    wv, wf = mo(path)
    out = [f"## {os.path.basename(path)}", ""]
    an = [ws.title for ws in wf.worksheets if ws.sheet_state != "visible"]
    hien = [ws.title for ws in wf.worksheets if ws.sheet_state == "visible"]
    out.append(f"Sheet hiển thị ({len(hien)}): {', '.join(hien)}")
    if an:
        out.append(f"Sheet ẩn ({len(an)}): {', '.join(an[:40])}{' …' if len(an) > 40 else ''}")
    out.append("")
    muc = defaultdict(list)
    vat_theo_sheet = defaultdict(set)
    for ws_f in wf.worksheets:
        ten = ws_f.title
        if ws_f.sheet_state != "visible" and not ca_sheet_an:
            # S-1: chỉ kiểm tra lỗi ở sheet ẩn, nhưng liệt kê tối đa 6 tọa độ mẫu như E1
            ws_v = wv[ten]
            loi_ct = Counter()
            loi_vt = []
            for row in ws_v.iter_rows():
                for cv in row:
                    v = cv.value
                    if isinstance(v, str) and v.strip() in LOI:
                        loi_ct[v.strip()] += 1
                        if len(loi_vt) < 6:
                            loi_vt.append(cv.coordinate)
            loi = sum(loi_ct.values())
            if loi:
                muc["E6"].append(f"Sheet ẩn `{ten}` có {loi} ô lỗi ({', '.join(f'{k} × {n}' for k, n in loi_ct.items())}; "
                                 f"vd. {', '.join(loi_vt)}) — nếu không dùng nên xoá khỏi hồ sơ phát hành")
            continue
        ws_v = wv[ten]
        loi = Counter()
        loi_vt = defaultdict(list)
        ngoai, gg = [], []
        so_chu_n, so_chu_vd = 0, []
        so_chu_phay_n, so_chu_phay_vd = 0, []
        cot_cong_thuc = defaultdict(lambda: [0, 0, []])  # col -> [công thức, hằng số, [vị trí hằng]]
        for row_f, row_v in zip(ws_f.iter_rows(), ws_v.iter_rows()):
            for cf, cv in zip(row_f, row_v):
                f, v = cf.value, cv.value
                if f is None:
                    continue
                if isinstance(v, str) and v.strip() in LOI:
                    loi[v.strip()] += 1
                    if len(loi_vt[v.strip()]) < 6:
                        loi_vt[v.strip()].append(cf.coordinate)
                if isinstance(f, str) and f.startswith("="):
                    if re.search(r"\[\d+\]", f):
                        ngoai.append(cf.coordinate)
                    if "__xludf.DUMMYFUNCTION" in f:
                        gg.append(cf.coordinate)
                    if cf.row > 5:
                        cot_cong_thuc[cf.column][0] += 1
                elif isinstance(f, (int, float)) and cf.row > 5:
                    c = cot_cong_thuc[cf.column]
                    c[1] += 1
                    if len(c[2]) < 8:
                        c[2].append(cf.coordinate)
                if cf.column > 1 and la_so_chu(v):
                    # S-5: đếm đủ (không cắt ở 400 như trước); riêng số dạng chữ dấu phẩy thập phân
                    # trong bảng tra cứu thì báo riêng để người soát biết VLOOKUP có thể đọc sai
                    so_chu_n += 1
                    if len(so_chu_vd) < 6:
                        so_chu_vd.append(cf.coordinate)
                    if re.fullmatch(r"\s*-?\d+,\d+\s*", str(v)):
                        so_chu_phay_n += 1
                        if len(so_chu_phay_vd) < 6:
                            so_chu_phay_vd.append(cf.coordinate)
                if isinstance(v, str):
                    t = v
                    for pat, mo_ta in VB_HET_HIEU_LUC:
                        if re.search(pat, t):
                            muc["E7"].append(f"`{ten}`!{cf.coordinate}: trích {mo_ta}")
                    for m in re.finditer(r"(?:VAT|GTGT|GIÁ TRỊ GIA TĂNG)[^\d%]{0,20}?(\d{1,2})\s*%", t, re.I):
                        vat_theo_sheet[ten].add(m.group(1) + "%")
                    tl = t.lower()
                    if "không xác định được khối lượng" in tl:
                        nb = ws_v.cell(cf.row, cf.column + 1).value
                        if isinstance(nb, str) and nb.strip().upper() == "LT":
                            muc["E9"].append(f"`{ten}`!{cf.coordinate}")
        if loi:
            muc["E1"].append(f"`{ten}`: " + ", ".join(f"{k} × {n} (vd. {', '.join(loi_vt[k])})" for k, n in loi.items()))
        if ngoai:
            muc["E2"].append(f"`{ten}`: {len(ngoai)} ô (vd. {', '.join(ngoai[:6])})")
        if gg:
            muc["E3"].append(f"`{ten}`: {len(gg)} ô (vd. {', '.join(gg[:6])})")
        if so_chu_n:
            muc["E4"].append(f"`{ten}`: {so_chu_n} ô (vd. {', '.join(so_chu_vd[:6])})")
            if la_bang_tra_cuu(ten) and so_chu_phay_n:
                muc["E4"].append(f"`{ten}`: {so_chu_phay_n} ô số dạng chữ dùng dấu phẩy thập phân trong BẢNG TRA CỨU — "
                                 f"kiểm tra VLOOKUP/INDEX có đọc đúng không (vd. {', '.join(so_chu_phay_vd[:6])})")
        for col, (n_ct, n_hs, vt) in cot_cong_thuc.items():
            if col > 1 and n_ct >= 8 and 0 < n_hs <= max(3, n_ct // 10):
                muc["E5"].append(f"`{ten}` cột {openpyxl.utils.get_column_letter(col)}: {n_hs} số nhập tay giữa {n_ct} công thức (vd. {', '.join(vt[:5])})")
        # E10/E11/E12 — công thức tổng hợp sai phạm vi / ô trống / nhãn mâu thuẫn công thức
        for k, ds in kiem_tra_bang_tong_hop(ws_f, ws_v, ten).items():
            muc[k].extend(ds)
    tat_ca_vat = Counter(v for s in vat_theo_sheet.values() for v in s)
    if len(tat_ca_vat) > 1:
        muc["E8"].append("Thuế suất GTGT ghi khác nhau: " + "; ".join(f"`{s}`: {', '.join(sorted(v))}" for s, v in vat_theo_sheet.items()))
    ten_muc = {"E1": "Ô lỗi", "E2": "Liên kết file ngoài", "E3": "Hàm tồn dư Google Sheets", "E4": "Số lưu dạng chữ",
               "E5": "Số nhập tay giữa công thức", "E6": "Sheet ẩn", "E7": "Văn bản hết hiệu lực từ 01/7/2026",
               "E8": "Thuế suất GTGT không thống nhất", "E9": "Ký hiệu LT cho chi phí không xác định được KL",
               "E10": "Công thức tổng hợp SUM sai phạm vi so với nhãn/cách tính",
               "E11": "Ô giá trị trống giữa các công thức trong bảng tổng hợp",
               "E12": "Nhãn/cách tính mâu thuẫn công thức tham chiếu"}
    if not muc:
        out.append("Không phát hiện vấn đề theo các tiêu chí E1–E12.")
    for k in sorted(muc):
        ds = muc[k]
        out.append(f"### {k} · {ten_muc[k]} ({len(ds)})")
        for x in ds[:25]:
            out.append(f"- {x}")
        if len(ds) > 25:
            out.append(f"- … còn {len(ds) - 25} mục")
        out.append("")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="+")
    p.add_argument("--ra")
    p.add_argument("--ca-sheet-an", action="store_true", help="Soát đầy đủ cả sheet ẩn")
    a = p.parse_args()
    rep = "# Kết quả soát file Excel\n\n" + "\n".join(soat_file(f, a.ca_sheet_an) for f in a.files)
    if a.ra:
        with open(a.ra, "w", encoding="utf-8") as f:
            f.write(rep)
    print(rep)


if __name__ == "__main__":
    main()
