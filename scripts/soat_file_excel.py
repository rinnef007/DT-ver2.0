#!/usr/bin/env python3
"""Soát nhanh một file Excel dự toán / khối lượng có sẵn (của mình hoặc do tư vấn lập).

  python soat_file_excel.py du_toan.xlsx [khoi_luong.xlsx ...] [--ra bao_cao.md] [--ca-sheet-an]

Kiểm tra (không sửa file):
  E1  Ô lỗi (#REF!, #N/A, #VALUE!, #DIV/0!, #NAME?) theo sheet
  E2  Liên kết tới file ngoài ([1], [2]…) — giá trị phụ thuộc file khác
  E3  Hàm tồn dư từ Google Sheets (__xludf.DUMMYFUNCTION) — giá trị là bản lưu tạm
  E4  Số lưu dạng chữ trong cột số
  E5  Số nhập tay giữa các ô công thức cùng cột (dễ quên cập nhật)
  E6  Sheet ẩn: liệt kê, sheet ẩn có lỗi hoặc nội dung của công trình khác
  E7  Văn bản trích dẫn đã hết hiệu lực từ 01/7/2026 (NĐ 10/2021, TT 11/12/13/2021…) — trừ hồ sơ chuyển tiếp
  E8  Thuế suất GTGT ghi khác nhau giữa các sheet đang hiển thị
  E9  Ký hiệu "LT" dùng cho chi phí một số công việc không xác định được khối lượng (theo Bảng 3.8 PL III TT 36/2026 là "TT")
File .xls được chuyển sang .xlsx bằng LibreOffice trước khi đọc.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

try:
    import openpyxl
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
            # chỉ kiểm tra lỗi ở sheet ẩn
            ws_v = wv[ten]
            loi = sum(1 for row in ws_v.iter_rows(values_only=True) for v in row if isinstance(v, str) and v in LOI)
            if loi:
                muc["E6"].append(f"Sheet ẩn `{ten}` có {loi} ô lỗi — nếu không dùng nên xoá khỏi hồ sơ phát hành")
            continue
        ws_v = wv[ten]
        loi = Counter()
        loi_vt = defaultdict(list)
        ngoai, gg, so_chu = [], [], []
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
                if cf.column > 1 and la_so_chu(v) and len(so_chu) < 400:
                    so_chu.append(cf.coordinate)
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
        if so_chu:
            muc["E4"].append(f"`{ten}`: {len(so_chu)} ô (vd. {', '.join(so_chu[:6])})")
        for col, (n_ct, n_hs, vt) in cot_cong_thuc.items():
            if col > 1 and n_ct >= 8 and 0 < n_hs <= max(3, n_ct // 10):
                muc["E5"].append(f"`{ten}` cột {openpyxl.utils.get_column_letter(col)}: {n_hs} số nhập tay giữa {n_ct} công thức (vd. {', '.join(vt[:5])})")
    tat_ca_vat = Counter(v for s in vat_theo_sheet.values() for v in s)
    if len(tat_ca_vat) > 1:
        muc["E8"].append("Thuế suất GTGT ghi khác nhau: " + "; ".join(f"`{s}`: {', '.join(sorted(v))}" for s, v in vat_theo_sheet.items()))
    ten_muc = {"E1": "Ô lỗi", "E2": "Liên kết file ngoài", "E3": "Hàm tồn dư Google Sheets", "E4": "Số lưu dạng chữ",
               "E5": "Số nhập tay giữa công thức", "E6": "Sheet ẩn", "E7": "Văn bản hết hiệu lực từ 01/7/2026",
               "E8": "Thuế suất GTGT không thống nhất", "E9": "Ký hiệu LT cho chi phí không xác định được KL"}
    if not muc:
        out.append("Không phát hiện vấn đề theo các tiêu chí E1–E9.")
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
