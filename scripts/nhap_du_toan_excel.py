#!/usr/bin/env python3
"""Nhập một file dự toán Excel đã lập (mẫu "Bảng đơn giá chi tiết" + "Bảng dự toán" theo đoạn) thành bộ dữ liệu chuẩn.

Dùng để: (1) tái lập và đối chiếu một hồ sơ có sẵn; (2) lấy hồ sơ cũ làm điểm xuất phát cho hồ sơ mới.

  python nhap_du_toan_excel.py --file du_toan.xls --dgct "dtct-sc" --dt "dt-xd,dt-dbgt" --ra du-lieu/ten-ho-so

Bố cục được nhận diện theo tiêu đề cột (không cố định vị trí):
- Sheet đơn giá chi tiết: STT | Mã số | Thành phần hao phí | Đơn vị | Định mức | Đơn giá (mỗi vùng 1 cột) | Hệ số | Thành tiền …
  Khối mỗi công tác: dòng tiêu đề (STT số, mã, tên), các mục a) Vật liệu / b) Nhân công / c) Máy thi công,
  dòng % (vật liệu khác, máy khác), dòng Chi phí chung, dòng chi phí không xác định KL, TL, GTGT.
- Sheet dự toán: TT | STT đơn giá | Mã hiệu | Hạng mục công việc | Đơn vị | Khối lượng (mỗi đoạn 1 cột) | Đơn giá (mỗi vùng) | Thành tiền …
  Đoạn → vùng giá nhận từ công thức thành tiền (vd. =ROUND($F6*$N6,0)).

Chế độ GXD (--kieu gxd): đọc file theo bố cục phần mềm Dự toán GXD 2026 —
- Sheet đơn giá: "Don gia XD" (19 cột: MÃ HIỆU ĐỊNH MỨC | MÃ HIỆU ĐƠN GIÁ | MSVT | TÊN CÔNG VIỆC / THÀNH PHẦN HAO PHÍ |
  ĐƠN VỊ | KHỐI LƯỢNG | ĐỊNH MỨC HAO PHÍ | ĐƠN GIÁ VẬT TƯ | HỆ SỐ | THÀNH TIỀN …). Loại hao phí nhận theo tiền tố MSVT
  (V… → VL, NC… → NC, M… → M); MÃ VỮA → cap_phoi; chỉ có 1 cột đơn giá nên 1 vùng giá duy nhất.
- Sheet dự toán: "Du toan XD" (33 cột: STT | MÃ VỮA | MÃ HIỆU ĐỊNH MỨC | MÃ HIỆU ĐƠN GIÁ | NỘI DUNG CÔNG VIỆC | ĐƠN VỊ |
  KHỐI LƯỢNG | YCKT | Kvlc | Kvlp | Knc1 | Knc2 | Knc3 | Km | ĐƠN GIÁ VL/VLP/NC/M | THÀNH TIỀN … | GHI CHÚ).
  he_so_vl = Kvlc × Kvlp, he_so_m = Km; Knc1–3 CHƯA gộp (ý nghĩa chưa xác minh — giữ nguyên 3 cột trong báo cáo);
  YCKT + ghi chú + diễn giải KL (cột Z–AF) → dien_giai; AF đối chiếu với H (khối lượng).
- File GXD trống (template, 0 khối đơn giá, 0 công tác) thì báo rõ "bảng trống" và thoát mã 2, không tạo file dữ liệu rỗng.
  Tỷ lệ C/TT/TL/GTGT của GXD nằm ở sheet THCP (không nhập ở chế độ này) nên bước đối chiếu đơn giá cuối sẽ báo thiếu
  config và dừng sau khi đã ghi đủ dữ liệu + báo cáo — bổ sung tỷ lệ rồi chạy lại `dutoan.py tinh` để đối chiếu.

Kết quả: dinh_muc.csv, gia_tai_nguyen.csv, khoi_luong.csv, config_du_toan.json, bao_cao_nhap.md.
Số liệu trích từ file là số của hồ sơ đó — nguồn ghi rõ "trích từ file", không thay cho văn bản gốc.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dutoan_core import bo_dau, so  # noqa: E402

try:
    import openpyxl
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("Thiếu openpyxl")


def mo_file(path):
    if path.lower().endswith(".xls"):
        tmp = tempfile.mkdtemp()
        subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmp, path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        out = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".xlsx")
        if not os.path.exists(out):
            sys.exit("Không chuyển được .xls sang .xlsx (cần LibreOffice). Hãy lưu file dạng .xlsx rồi chạy lại.")
        path = out
    return (openpyxl.load_workbook(path, data_only=True, keep_links=False),
            openpyxl.load_workbook(path, data_only=False, keep_links=False), path)


def txt(v):
    import unicodedata
    return "" if v is None else unicodedata.normalize("NFC", str(v)).strip()


def tim_tieu_de(ws, can_co, max_row=30):
    for r in range(1, max_row + 1):
        vals = [bo_dau(txt(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        if all(any(k in v for v in vals) for k in can_co):
            return r, vals
    return None, None


def cot_co(vals, khoa, bat_dau=0):
    for i, v in enumerate(vals):
        if i >= bat_dau and khoa in v:
            return i + 1
    return None


# ----------------------------------------------------------------- sheet đơn giá chi tiết
def doc_dgct(wv, ten_sheet, bc, wf=None):
    ws = wv[ten_sheet]
    wsf = wf[ten_sheet] if wf is not None else None
    r0, vals = tim_tieu_de(ws, ["thanh phan hao phi"])
    if not r0:
        sys.exit(f"Không thấy dòng tiêu đề 'Thành phần hao phí' trong sheet {ten_sheet}")
    cA = cot_co(vals, "stt") or 1
    cB = cot_co(vals, "ma so") or cot_co(vals, "ma hieu") or 2
    cC = cot_co(vals, "thanh phan hao phi")
    cD = cot_co(vals, "don vi", cC)
    cE = cot_co(vals, "dinh muc", cC)
    cF = cot_co(vals, "don gia", cC)
    cH = cot_co(vals, "he so", cF)
    cI = cot_co(vals, "thanh tien", cF)
    n_vung = cH - cF
    vung = OrderedDict()
    for k in range(n_vung):
        # N-5: tên vùng KHÔNG lấy từ dòng chỉ số "[n]" dưới tiêu đề (GXD ghi "[8]"… ở dòng này)
        ten_o = txt(ws.cell(r0 + 1, cF + k).value)
        if not ten_o or _la_chi_so(ten_o):
            ten = f"Vùng {k + 1}"
            bc.append(f"- Sheet {ten_sheet}: không đọc được tên vùng giá ở cột {get_column_letter(cF + k)} "
                      f"(ô chứa {ten_o!r}) — tạm đặt '{ten}'")
        else:
            ten = ten_o
        vung[f"V{k + 1}"] = ten
    blocks, cur, sec = [], None, None
    for r in range(r0 + 2, ws.max_row + 1):
        A, B, C, D, E = (ws.cell(r, c).value for c in (cA, cB, cC, cD, cE))
        Cs = txt(C)
        Cl = bo_dau(Cs)
        if isinstance(A, (int, float)) and txt(B) and Cs and not re.match(r"^[abc]\)", Cl):
            cur = {"row": r, "stt": int(A), "ma": txt(B).replace("\n", " "), "ten": Cs, "dvkl": txt(D),
                   "E": so(E, 1.0) or 1.0, "lines": [], "rates": {},
                   "dg": {v: so(ws.cell(r, cF + k).value) for k, v in enumerate(vung)}}
            blocks.append(cur)
            sec = None
            continue
        if cur is None:
            continue
        if re.match(r"^a\)", Cl):
            sec = "VL"; continue
        if re.match(r"^b\)", Cl):
            sec = "NC"; continue
        if re.match(r"^c\)", Cl):
            sec = "M"; continue
        Dl = bo_dau(txt(D))
        if Dl == "t":
            cur["row_T"] = r
        if Dl == "gt":
            cur["row_GT"] = r
        if "cong chi phi truc tiep" in Cl:
            sec = None; continue
        if "chi phi chung" in Cl:
            cur["rates"]["chi_phi_chung"] = {"gia_tri": so(E), "co_so": "NC" if "nc x" in Cl else "T"}
            continue
        if ("khong xac dinh" in Cl or Dl in ("lt", "tt")) and "chi_phi_chung" in cur["rates"] and "cong_viec_khong_xd_kl" not in cur["rates"]:
            cur["rates"]["cong_viec_khong_xd_kl"] = {"gia_tri": so(E), "nhan": Cs, "ky_hieu": txt(D)}
            continue
        if Dl == "tl":
            cur["row_TL"] = r
            cur["rates"]["thu_nhap_chiu_thue_tt"] = {"gia_tri": so(E)}; continue
        if Dl == "gtgt":
            cur["rates"]["thue_gtgt"] = {"gia_tri": so(E)}; continue
        if Dl in ("cpa", "cbc") and so(E, 0):
            bc.append(f"- Dòng {r} (mã {cur['ma']}): có chi phí phục vụ khảo sát ({Cs}) — chưa hỗ trợ, cần xem lại")
            continue
        if sec and Cs and not Cl.startswith("cong") and so(E) is not None:
            if Dl == "%":
                cur["lines"].append({"loai": "VLK" if sec == "VL" else "MK", "ma_tn": "", "ten_tn": Cs, "dvt": "%",
                                     "hp": so(E), "hs": 1.0, "row": r, "sec": sec})
            else:
                ma_tn = txt(B) or Cs
                gia = {v: so(ws.cell(r, cF + k).value) for k, v in enumerate(vung)}
                hs = so(ws.cell(r, cH).value, 1.0)
                cur["lines"].append({"loai": sec, "ma_tn": ma_tn, "ten_tn": Cs, "dvt": txt(D), "hp": so(E),
                                     "hs": 1.0 if hs is None else hs, "gia": gia, "row": r})
    # soát công thức trong khối (khi có bản công thức)
    if wsf is not None:
        for b in blocks:
            if b.get("row_TL"):
                fm = txt(wsf.cell(b["row_TL"], cI).value)
                refs = {int(x) for x in re.findall(r"[A-Z]{1,3}\$?(\d+)", fm)}
                can = {b.get("row_T"), b.get("row_GT")} - {None}
                if refs and can and refs != can:
                    bc.append(f"- Khối {b['ma']} (dòng {b['row']}): công thức TL dòng {b['row_TL']} `{fm}` tham chiếu dòng {sorted(refs)}, "
                              f"theo (T + GT) phải là dòng {sorted(can)}")
            for l in b["lines"]:
                if l["loai"] not in ("VLK", "MK"):
                    continue
                fm = txt(wsf.cell(l["row"], cF).value)
                m = re.search(r"SUM\(\$?[A-Z]{1,3}\$?(\d+):\$?[A-Z]{1,3}\$?(\d+)\)", fm)
                goc = [x["row"] for x in b["lines"] if x["loai"] == ("VL" if l["loai"] == "VLK" else "M")]
                if m and goc:
                    r1, r2 = int(m.group(1)), int(m.group(2))
                    ngoai = [x for x in goc if not (r1 <= x <= r2)]
                    if ngoai:
                        bc.append(f"- Khối {b['ma']} (dòng {b['row']}): dòng {l['ten_tn']} (dòng {l['row']}) tính % trên `{fm}`, "
                                  f"không gồm dòng {ngoai} — kiểm tra phạm vi tính")
                        l["co_so_rows"] = (r1, r2)
    return blocks, vung


# ----------------------------------------------------------------- sheet dự toán
def doc_dt(wv, wf, ten_sheet, vung_ids):
    ws, wsf = wv[ten_sheet], wf[ten_sheet]
    r0, vals = tim_tieu_de(ws, ["ma hieu", "don gia"])
    if not r0:
        sys.exit(f"Không thấy tiêu đề 'Mã hiệu' / 'Đơn giá' trong sheet {ten_sheet}")
    hm = ten_sheet
    for r in range(1, r0):
        for c in range(1, 4):
            t = txt(ws.cell(r, c).value)
            if bo_dau(t).startswith("hang muc"):
                hm = t.split(":", 1)[-1].strip() or hm
    cA = cot_co(vals, "tt") or 1
    cB = cot_co(vals, "stt don gia") or 2
    cC = cot_co(vals, "ma hieu")
    cD = cot_co(vals, "hang muc cong viec") or cC + 1
    cE = cot_co(vals, "don vi", cD)
    cK = cot_co(vals, "khoi luong") or (cE + 1)
    cG = cot_co(vals, "don gia", cK)
    cT = cot_co(vals, "thanh tien", cG)
    doan = OrderedDict()
    # N-6: chỉ nhận cột KL khi tiêu đề cột chứa tên đoạn/xã cụ thể — không nhận mọi cột giữa KL và ĐG
    # (bố cục GXD có YCKT, Kvlc/Kvlp, Knc1–3, Km ở giữa; dòng chỉ số "[n]" cũng không phải tên đoạn).
    # Lưu ý: cột đoạn của bố cục skill cũng mang tiêu đề "Khối lượng" nên KHÔNG loại theo tiêu đề đó —
    # cột KL đầu tiên (cK) chính là đoạn đầu tiên; cột GXD bị loại nhờ dòng chỉ số "[n]" ở hàng dưới tiêu đề.
    _KHONG_PHAI_DOAN = {"yeu cau ky thuat", "chi dan ky thuat", "yckt", "kvlc", "kvlp",
                        "knc1", "knc2", "knc3", "km"}
    n_doan = 0
    for c in range(cK, cG):
        ten_o = txt(ws.cell(r0 + 1, c).value)
        tieu_de_o = bo_dau(txt(ws.cell(r0, c).value))
        if ten_o and _la_chi_so(ten_o):
            continue
        # tiêu đề có thể gộp bằng "/": "Yêu cầu kỹ thuật/Chỉ dẫn kỹ thuật" → tách từng phần rồi đối chiếu
        if {p.strip() for p in tieu_de_o.split("/")} & _KHONG_PHAI_DOAN:
            continue
        n_doan += 1
        doan[f"D{n_doan}"] = {"ten": ten_o or f"Đoạn {n_doan}", "cot": c, "vung": None}
    if not doan:
        # không có cột đoạn nào (vd. GXD: 1 cột khối lượng duy nhất) → 1 đoạn ngầm lấy từ cột KL
        doan["D1"] = {"ten": "Toàn bộ", "cot": cK, "vung": None}
    gia_cols = {get_column_letter(cG + k): vid for k, vid in enumerate(vung_ids)}
    items = []
    for r in range(r0 + 2, ws.max_row + 1):
        B, C = ws.cell(r, cB).value, ws.cell(r, cC).value
        if not txt(C) or not isinstance(B, (int, float)):
            continue
        it = {"row": r, "tt": txt(ws.cell(r, cA).value), "stt_dg": int(B), "ma": txt(C).replace("\n", " "),
              "ten": txt(ws.cell(r, cD).value), "dv": txt(ws.cell(r, cE).value), "kl": OrderedDict(),
              "dg": {vid: so(ws.cell(r, cG + k).value) for k, vid in enumerate(vung_ids)}}
        for k, (did, d) in enumerate(doan.items()):
            it["kl"][did] = so(ws.cell(r, d["cot"]).value, 0.0) or 0.0
            f = txt(wsf.cell(r, cT + k).value)
            m = re.findall(r"\$?([A-Z]{1,3})\$?\d+", f)
            for col in m:
                if col in gia_cols and d["vung"] is None:
                    d["vung"] = gia_cols[col]
        items.append(it)
    tong = {}
    for r in range(r0 + 2, ws.max_row + 1):
        t = bo_dau(txt(ws.cell(r, cD).value))
        if "truoc thue" in t:
            tong["truoc_thue"] = so(ws.cell(r, cT + len(doan)).value)
        elif "sau thue" in t:
            tong["sau_thue"] = so(ws.cell(r, cT + len(doan)).value)
        elif t.startswith("thue"):
            tong["vat"] = so(ws.cell(r, cT + len(doan)).value)
    return hm, doan, items, tong


def _la_chi_so(v):
    """Giá trị chỉ số kiểu GXD: "[1]", "[1a]", "[6']", "[15]=[5]*[12]"… — đều bắt đầu bằng "["."""
    return isinstance(v, str) and v.strip().startswith("[")


def _la_dong_bo(ws, r):
    """Dòng trống hoàn toàn hoặc dòng chỉ số [..] (hàng dưới tiêu đề của GXD)."""
    vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
    co_gia_tri = [v for v in vals if v is not None and (not isinstance(v, str) or v.strip())]
    if not co_gia_tri:
        return True
    return all(_la_chi_so(v) for v in co_gia_tri)


# ----------------------------------------------------------------- bố cục GXD (--kieu gxd)
def doc_dgct_gxd(wv, ten_sheet, bc, wf=None):
    """Đọc sheet "Don gia XD" của GXD (19 cột) thành các khối đơn giá như doc_dgct.
    Loại hao phí nhận theo tiền tố MSVT (V… → VL, NC… → NC, M… → M); GXD chỉ có 1 cột đơn giá
    nên chỉ có 1 vùng giá (V1). Tỷ lệ C/TT/TL/GTGT không có trong sheet này (nằm ở THCP) nên
    blocks có rates = {} — bước đối chiếu đơn giá cuối sẽ báo rõ và dừng sau khi đã ghi dữ liệu."""
    ws = wv[ten_sheet]
    r0, vals = tim_tieu_de(ws, ["ma hieu dinh muc", "ten cong viec"])
    if not r0:
        sys.exit(f"Không thấy dòng tiêu đề 'Mã hiệu định mức' / 'Tên công việc' trong sheet {ten_sheet} (chế độ GXD)")
    cA = cot_co(vals, "stt") or 1
    cDM = cot_co(vals, "ma hieu dinh muc")
    cDG = cot_co(vals, "ma hieu don gia", cDM) if cDM else None
    cMSVT = cot_co(vals, "msvt", cDM) if cDM else None
    cTen = cot_co(vals, "ten cong viec")
    cDVT = cot_co(vals, "don vi", cTen) if cTen else None
    cHP = cot_co(vals, "dinh muc hao phi", cTen) if cTen else None
    cGia = cot_co(vals, "don gia vat tu", cTen) if cTen else None
    cHS = cot_co(vals, "he so", cGia) if cGia else None
    cHPK = cot_co(vals, "hao phi khac", cGia) if cGia else None
    cVua = cot_co(vals, "ma vua")
    vung = OrderedDict([("V1", "Chung")])
    blocks, cur = [], None
    for r in range(r0 + 2, ws.max_row + 1):
        if _la_dong_bo(ws, r):
            continue
        ma_dm = txt(ws.cell(r, cDM).value) if cDM else ""
        msvt = txt(ws.cell(r, cMSVT).value) if cMSVT else ""
        ten = txt(ws.cell(r, cTen).value) if cTen else ""
        if ma_dm and not msvt:
            if cDG:
                ma_dg = txt(ws.cell(r, cDG).value)
                if ma_dg and ma_dg != ma_dm:
                    bc.append(f"- Dòng {r} (mã {ma_dm}): mã hiệu đơn giá ({ma_dg}) khác mã định mức — "
                              f"lấy mã định mức làm ma_hieu, ghi mã đơn giá vào diễn giải")
            stt_o = ws.cell(r, cA).value
            cur = {"row": r, "stt": int(stt_o) if isinstance(stt_o, (int, float)) else len(blocks) + 1,
                   "ma": ma_dm, "ten": ten, "dvkl": txt(ws.cell(r, cDVT).value) if cDVT else "",
                   "E": 1.0, "lines": [], "rates": {},
                   "dg": {"V1": so(ws.cell(r, cGia).value) if cGia else None},
                   "cap_phoi": txt(ws.cell(r, cVua).value) if cVua else "",
                   "ma_don_gia": txt(ws.cell(r, cDG).value) if cDG else ""}
            blocks.append(cur)
            continue
        if cur is None or not msvt:
            continue
        if msvt.startswith("NC"):
            loai = "NC"
        elif msvt.startswith("M"):
            loai = "M"
        elif msvt.startswith("V"):
            loai = "VL"
        else:
            bc.append(f"- Dòng {r} (mã {cur['ma']}): MSVT {msvt} không rõ loại (không bắt đầu bằng V/NC/M) — bỏ qua, cần xem lại")
            continue
        dvt = txt(ws.cell(r, cDVT).value) if cDVT else ""
        hp = so(ws.cell(r, cHP).value) if cHP else None
        if hp is None:
            continue
        if dvt == "%":
            cur["lines"].append({"loai": "VLK" if loai == "VL" else "MK", "ma_tn": "", "ten_tn": ten, "dvt": "%",
                                 "hp": hp, "hs": 1.0, "row": r, "sec": loai})
            continue
        gia = so(ws.cell(r, cGia).value) if cGia else None
        hs = so(ws.cell(r, cHS).value, 1.0) if cHS else 1.0
        cur["lines"].append({"loai": loai, "ma_tn": msvt, "ten_tn": ten, "dvt": dvt, "hp": hp,
                             "hs": 1.0 if hs is None else hs, "gia": {"V1": gia}, "row": r})
        if cHPK and ws.cell(r, cHPK).value not in (None, ""):
            bc.append(f"- Dòng {r} (mã {cur['ma']}, {msvt}): có 'Hao phí khác' ({ws.cell(r, cHPK).value}) — "
                      f"ý nghĩa cột này [CHƯA ĐỐI CHIẾU], chưa nhập")
    return blocks, vung


def doc_dt_gxd(wv, wf, ten_sheet, vung_ids, bc):
    """Đọc sheet "Du toan XD" của GXD (33 cột) thành (hạng mục, đoạn, công tác, tổng).
    GXD chỉ có 1 cột khối lượng → 1 đoạn ngầm "Toàn bộ". he_so_vl = Kvlc × Kvlp, he_so_m = Km;
    Knc1–3 KHÔNG gộp (N-4: ý nghĩa chưa xác minh — giữ nguyên 3 cột trong báo cáo nhập).
    Tổng trước/sau thuế của GXD nằm ở sheet THCP nên tong = {} (không nhập tổng từ đây)."""
    ws, wsf = wv[ten_sheet], wf[ten_sheet]
    r0, vals = tim_tieu_de(ws, ["ma hieu dinh muc", "noi dung cong viec"])
    if not r0:
        sys.exit(f"Không thấy tiêu đề 'Mã hiệu định mức' / 'Nội dung công việc' trong sheet {ten_sheet} (chế độ GXD)")
    hm = ten_sheet
    for r in range(1, r0):
        for c in range(1, 4):
            t = txt(ws.cell(r, c).value)
            if bo_dau(t).startswith("hang muc"):
                hm = t.split(":", 1)[-1].strip() or hm
    cB = cot_co(vals, "stt") or 2
    cVua = cot_co(vals, "ma vua")
    cDM = cot_co(vals, "ma hieu dinh muc")
    cDG = cot_co(vals, "ma hieu don gia", cDM) if cDM else None
    cTen = cot_co(vals, "noi dung cong viec")
    cDV = cot_co(vals, "don vi", cTen) if cTen else None
    cKL = cot_co(vals, "khoi luong", cTen) if cTen else None
    cYCKT = cot_co(vals, "yeu cau ky thuat", cKL) or cot_co(vals, "chi dan ky thuat", cKL) if cKL else None
    cKvlc = cot_co(vals, "kvlc", cKL) if cKL else None
    cKvlp = cot_co(vals, "kvlp", cKL) if cKL else None
    cKnc1 = cot_co(vals, "knc1", cKL) if cKL else None
    cKnc2 = cot_co(vals, "knc2", cKL) if cKL else None
    cKnc3 = cot_co(vals, "knc3", cKL) if cKL else None
    cKm = cot_co(vals, "km", cKL) if cKL else None
    cDGvl = cot_co(vals, "don gia", cKL) if cKL else None
    cTT = cot_co(vals, "thanh tien", cDGvl) if cDGvl else None
    cGC = cot_co(vals, "ghi chu", cTT) if cTT else None
    doan = OrderedDict([("D1", {"ten": "Toàn bộ", "cot": cKL, "vung": vung_ids[0] if vung_ids else None})])
    items = []
    for r in range(r0 + 2, ws.max_row + 1):
        if _la_dong_bo(ws, r):
            continue
        ma = txt(ws.cell(r, cDM).value) if cDM else ""
        if not ma:
            continue
        ten = txt(ws.cell(r, cTen).value) if cTen else ""
        if not ten or "tong cong" in bo_dau(ten):
            continue
        stt_o = ws.cell(r, cB).value
        stt_dg = int(stt_o) if isinstance(stt_o, (int, float)) else 0
        kl = so(ws.cell(r, cKL).value, 0.0) if cKL else 0.0
        kvlc = so(ws.cell(r, cKvlc).value) if cKvlc else None
        kvlp = so(ws.cell(r, cKvlp).value) if cKvlp else None
        hs_vl = (kvlc or 1.0) * (kvlp or 1.0)
        if (kvlc is not None and kvlc != 1) or (kvlp is not None and kvlp != 1):
            bc.append(f"- Dòng {r} ({ma}): he_so_vl = Kvlc × Kvlp = {hs_vl:g} (Kvlc={kvlc}, Kvlp={kvlp})")
        km = so(ws.cell(r, cKm).value, 1.0) if cKm else 1.0
        knc = {}
        for k, c in (("Knc1", cKnc1), ("Knc2", cKnc2), ("Knc3", cKnc3)):
            v = so(ws.cell(r, c).value) if c else None
            if v is not None:
                knc[k] = v
        if knc and any(abs(v - 1) > 1e-12 for v in knc.values()):
            bc.append(f"- Dòng {r} ({ma}): Knc1–3 = {knc} — CHƯA gộp vào he_so_nc (ý nghĩa từng hệ số chưa xác minh, "
                      f"xem doi-chieu-gxd.md mục 2); giữ nguyên trong báo cáo này")
        dg_tong = so(ws.cell(r, cTT - 1).value) if cTT else None
        dg = {vid: dg_tong for vid in vung_ids}
        dien = []
        yckt = txt(ws.cell(r, cYCKT).value) if cYCKT else ""
        if yckt:
            dien.append(f"YCKT: {yckt}")
        gc = txt(ws.cell(r, cGC).value) if cGC else ""
        if gc:
            dien.append(f"Ghi chú: {gc}")
        z_af = [txt(ws.cell(r, c).value) for c in range(26, 33)]  # Z..AF: diễn giải KL dạng số
        if any(z_af):
            z, aa, ab, ac, ad, ae, af = z_af
            dien.append(f"Diễn giải KL: {z or '?'}×({aa or '?'}×{ab or '?'}×{ac or '?'})×{ad or '?'} = {ae or '?'} → {af or '?'}")
            if af and kl is not None and abs(so(af, kl) - kl) > 1e-9:
                bc.append(f"- Dòng {r} ({ma}): KL toàn bộ ở cột AF ({af}) khác khối lượng cột H ({kl:g}) — đã lấy theo cột H, cần kiểm tra")
        ma_dg = txt(ws.cell(r, cDG).value) if cDG else ""
        if ma_dg and ma_dg != ma:
            dien.append(f"Mã hiệu đơn giá: {ma_dg}")
        items.append({"row": r, "tt": str(stt_dg), "stt_dg": stt_dg, "ma": ma, "ten": ten,
                      "dv": txt(ws.cell(r, cDV).value) if cDV else "",
                      "kl": OrderedDict([("D1", kl or 0.0)]), "dg": dg,
                      "hs_vl": hs_vl, "hs_m": km or 1.0, "knc": knc,
                      "cap_phoi": txt(ws.cell(r, cVua).value) if cVua else "",
                      "dien_giai_gxd": "; ".join(dien)})
    return hm, doan, items, {}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True)
    p.add_argument("--dgct", required=True, help="Tên sheet đơn giá chi tiết")
    p.add_argument("--dt", required=True, help="Các sheet dự toán, cách nhau bởi dấu phẩy")
    p.add_argument("--ra", required=True, help="Thư mục ghi bộ dữ liệu")
    p.add_argument("--kieu", choices=["skill", "gxd"], default="skill",
                   help="Bố cục file nguồn: skill (DGCT/DT của skill) hoặc gxd (Don gia XD / Du toan XD của GXD)")
    p.add_argument("--vung", default="Chung", help="Tên vùng giá duy nhất khi --kieu gxd (GXD chỉ có 1 cột đơn giá)")
    p.add_argument("--xac-nhan", action="store_true", help="Đánh dấu khối lượng nhập là đã xác nhận (chỉ dùng khi tái lập đối chiếu)")
    a = p.parse_args()
    wv, wf, path = mo_file(a.file)
    ten_file = os.path.basename(a.file)
    bc = [f"# Báo cáo nhập từ `{ten_file}`", ""]
    if a.kieu == "gxd":
        blocks, vung = doc_dgct_gxd(wv, a.dgct, bc, wf)
        vung["V1"] = a.vung
        bc.append(f"- Sheet đơn giá chi tiết `{a.dgct}` (chế độ GXD): {len(blocks)} khối đơn giá, 1 vùng giá: V1 = {vung['V1']}")
    else:
        blocks, vung = doc_dgct(wv, a.dgct, bc, wf)
        bc.append(f"- Sheet đơn giá chi tiết `{a.dgct}`: {len(blocks)} khối đơn giá, {len(vung)} vùng giá: " +
                  "; ".join(f"{k} = {v}" for k, v in vung.items()))

    # mã hiệu duy nhất theo nội dung
    sig_to_key, key_of_row = {}, {}
    dem = Counter()
    for b in blocks:
        sig = (b["ma"], b["E"], tuple((l["loai"], l["ma_tn"], l["hp"], l["hs"]) for l in b["lines"]))
        if sig in sig_to_key:
            key_of_row[b["row"]] = sig_to_key[sig]
            continue
        dem[b["ma"]] += 1
        key = b["ma"] if dem[b["ma"]] == 1 else f"{b['ma']}#{dem[b['ma']]}"
        sig_to_key[sig] = key
        key_of_row[b["row"]] = key
        b["key"] = key
    trung = [m for m, n in dem.items() if n > 1]
    if trung:
        bc.append(f"- Mã hiệu có nhiều biến thể nội dung (đặt hậu tố #2, #3…): {', '.join(trung)}")

    # giá theo (mã TN, vùng); xung đột → biến thể ~k
    gia, xung_dot = OrderedDict(), []
    for b in blocks:
        if "key" not in b:
            continue
        for l in b["lines"]:
            if l["loai"] not in ("VL", "NC", "M"):
                continue
            ma = l["ma_tn"]
            k = 1
            while True:
                ma_k = ma if k == 1 else f"{ma}~{k}"
                cu = [gia.get((ma_k, v)) for v in vung]
                if all(x is None for x in cu) or all(x is not None and abs((x["don_gia"] or 0) - (l["gia"][v] or 0)) < 0.5 for x, v in zip(cu, vung)):
                    break
                k += 1
            if k > 1:
                xung_dot.append(f"{ma} (mã {b['ma']}, dòng {l['row']})")
            l["ma_tn_chuan"] = ma_k
            for v in vung:
                gia.setdefault((ma_k, v), {"ma_tn": ma_k, "ten_tn": l["ten_tn"], "don_vi": l["dvt"], "loai": l["loai"],
                                           "vung": v, "don_gia": l["gia"][v] or 0,
                                           "nguon": f"Trích từ {ten_file}, sheet {a.dgct}, dòng {l['row']}"})
    if xung_dot:
        bc.append(f"- Cùng tài nguyên nhưng giá khác nhau giữa các khối (tách mã ~2, ~3): {'; '.join(xung_dot[:20])}")

    # tỷ lệ phổ biến
    def mode(k, field="gia_tri"):
        c = Counter(json.dumps(b["rates"].get(k, {}), sort_keys=True) for b in blocks if b["rates"].get(k))
        return json.loads(c.most_common(1)[0][0]) if c else {}
    chuan = {k: mode(k) for k in ("chi_phi_chung", "cong_viec_khong_xd_kl", "thu_nhap_chiu_thue_tt", "thue_gtgt")}
    rieng = {}
    for b in blocks:
        if "key" not in b:
            continue
        for k in ("chi_phi_chung", "cong_viec_khong_xd_kl", "thu_nhap_chiu_thue_tt"):
            x = b["rates"].get(k)
            if x and (abs((x.get("gia_tri") or 0) - (chuan[k].get("gia_tri") or 0)) > 1e-12 or x.get("co_so", "T") != chuan[k].get("co_so", "T")):
                rieng.setdefault(b["key"], {})[k] = {"gia_tri": x["gia_tri"], "co_so": x.get("co_so", "T"), "can_cu": ""}
    nhan_lt = Counter(b["rates"].get("cong_viec_khong_xd_kl", {}).get("ky_hieu", "") for b in blocks)
    if nhan_lt.get("LT"):
        bc.append(f"- {nhan_lt['LT']} khối ghi ký hiệu **LT** cho dòng chi phí một số công việc không xác định được KL; theo Bảng 3.8 PL III TT 36/2026 ký hiệu là **TT** (LT là chi phí nhà tạm).")

    # sheet dự toán
    kl_rows, doan_all, tong_dt = [], OrderedDict(), {}
    stt_to_row = {}
    for b in blocks:
        stt_to_row.setdefault(b["stt"], b["row"])
    tong_items = 0
    for ten_sheet in [s.strip() for s in a.dt.split(",") if s.strip()]:
        if a.kieu == "gxd":
            hm, doan, items, tong = doc_dt_gxd(wv, wf, ten_sheet, list(vung), bc)
        else:
            hm, doan, items, tong = doc_dt(wv, wf, ten_sheet, list(vung))
        tong_items += len(items)
        dem_tt = Counter(it["tt"] for it in items)
        trung_tt = sorted((t for t, n in dem_tt.items() if n > 1 and t), key=lambda x: (len(x), x))
        if trung_tt:
            bc.append(f"- Sheet {ten_sheet}: số thứ tự (cột TT) bị trùng: {', '.join(trung_tt)} — đã gán STT duy nhất dạng 'TT/dòng'")
        for it in items:
            if dem_tt[it["tt"]] > 1 or not it["tt"]:
                it["tt"] = f"{it['tt'] or it['stt_dg']}/{it['row']}"
        tong_dt[hm] = tong
        for did, d in doan.items():
            if did in doan_all and doan_all[did]["ten"] != d["ten"]:
                bc.append(f"- Sheet {ten_sheet}: tên đoạn {did} khác sheet trước ('{d['ten']}')")
            doan_all.setdefault(did, d)
        bc.append(f"- Sheet dự toán `{ten_sheet}` (hạng mục: {hm}): {len(items)} công tác; tổng trước thuế trong file: {tong.get('truoc_thue')}")
        for it in items:
            brow = stt_to_row.get(it["stt_dg"])
            if brow is None:
                bc.append(f"  - Dòng {it['row']}: STT đơn giá {it['stt_dg']} không có trong sheet đơn giá")
                continue
            key = key_of_row[brow]
            b = next(x for x in blocks if x["row"] == brow)
            if bo_dau(b["ma"]) != bo_dau(it["ma"]):
                bc.append(f"  - Dòng {it['row']}: mã trong dự toán ({it['ma']}) khác mã khối đơn giá ({b['ma']})")
            co_kl = [(d, q) for d, q in it["kl"].items() if q]
            if not co_kl:
                co_kl = [(next(iter(it["kl"])), 0.0)]
                bc.append(f"  - Dòng {it['row']} ({it['ma']} – {it['ten'][:50]}): khối lượng bằng 0 ở mọi đoạn")
            for did, q in co_kl:
                dien = it.get("dien_giai_gxd", "")
                dien = (dien + "; " if dien else "") + f"Nhập từ {ten_file}, sheet {ten_sheet}, dòng {it['row']}"
                kl_rows.append({"stt": it["tt"] or str(it["stt_dg"]), "hang_muc": hm, "ma_hieu": key,
                                "cap_phoi": it.get("cap_phoi", ""), "ten_cong_tac": it["ten"],
                                "don_vi": it["dv"], "doan": did, "khoi_luong": f"{q:g}", "quy_doi": f"{1/b['E']:.12g}",
                                "he_so_vl": it.get("hs_vl", 1), "he_so_nc": 1, "he_so_m": it.get("hs_m", 1),
                                "can_cu_he_so": "Kvlc × Kvlp (file GXD)" if it.get("hs_vl", 1) != 1 else "",
                                "don_gia_tron_goi": "",
                                "dien_giai": dien,
                                "nguon_ban_ve": "Theo bảng khối lượng của hồ sơ",
                                "trang_thai": "xac_nhan" if a.xac_nhan else "de_xuat"})
    for did, d in doan_all.items():
        if d["vung"] is None:
            bc.append(f"- Không xác định được vùng giá cho đoạn {did} ({d['ten']}) — gán vùng đầu tiên, cần kiểm tra")
            d["vung"] = next(iter(vung))

    # N-2: bảng trống thì báo rõ, không tạo bộ dữ liệu rỗng
    if not blocks and tong_items == 0:
        bc.append("")
        bc.append("## Kết luận: BẢNG TRỐNG — không có dữ liệu để nhập")
        bc.append("- File này là template/mẫu trống (0 khối đơn giá, 0 công tác) hoặc các sheet không có dòng dữ liệu "
                  "dưới tiêu đề. Không tạo dinh_muc.csv / gia_tai_nguyen.csv / khoi_luong.csv / config_du_toan.json.")
        bc.append("- Cần file đã điền dữ liệu (khối đơn giá + bảng dự toán) rồi chạy lại lệnh nhập.")
        os.makedirs(a.ra, exist_ok=True)
        with open(os.path.join(a.ra, "bao_cao_nhap.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(bc) + "\n")
        print("\n".join(bc))
        print(f"\nĐã ghi báo cáo vào {a.ra}/bao_cao_nhap.md (không tạo file dữ liệu — bảng trống)")
        return 2

    os.makedirs(a.ra, exist_ok=True)
    with open(os.path.join(a.ra, "dinh_muc.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_hieu", "ten_cong_tac", "don_vi", "loai", "ma_tn", "ten_tn", "don_vi_tn", "hao_phi", "he_so", "can_cu_he_so", "nguon"])
        for b in blocks:
            if "key" not in b:
                continue
            dv = f"{b['E']:g}{b['dvkl']}" if abs(b["E"] - 1) > 1e-12 else b["dvkl"]
            for l in b["lines"]:
                w.writerow([b["key"], b["ten"], dv, l["loai"], l.get("ma_tn_chuan", ""), l["ten_tn"], l["dvt"],
                            f"{l['hp']:.12g}", f"{l['hs']:.12g}", "", f"Trích từ {ten_file}, sheet {a.dgct}, dòng {b['row']} — đối chiếu định mức gốc"])
    with open(os.path.join(a.ra, "gia_tai_nguyen.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_tn", "ten_tn", "don_vi", "loai", "vung", "don_gia", "nguon", "ngay_ap_dung", "khu_vuc", "ty_le_luong"])
        for g in gia.values():
            w.writerow([g["ma_tn"], g["ten_tn"], g["don_vi"], g["loai"], g["vung"], f"{g['don_gia']:.12g}", g["nguon"], "", vung[g["vung"]], ""])
    with open(os.path.join(a.ra, "khoi_luong.csv"), "w", encoding="utf-8", newline="") as f:
        cols = ["stt", "hang_muc", "ma_hieu", "cap_phoi", "ten_cong_tac", "don_vi", "doan", "khoi_luong", "quy_doi", "he_so_vl", "he_so_nc",
                "he_so_m", "can_cu_he_so", "don_gia_tron_goi", "dien_giai", "nguon_ban_ve", "trang_thai"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(kl_rows)
    cfg = {
        "_ghi_chu": f"Sinh tự động từ {ten_file}. Tỷ lệ là tỷ lệ đang dùng trong file — cần đối chiếu PL III TT 36/2026 và ghi căn cứ.",
        "du_an": "", "cong_trinh": "", "hang_muc": "", "loai_cong_trinh": "", "theo_tuyen": True,
        "chi_phi_xd_truoc_thue_tmdt_ty": None, "mau_xuat": "doan_vung", "lam_tron": "tung_buoc",
        "vung": [{"id": k, "ten": v} for k, v in vung.items()],
        "doan": [{"id": k, "ten": d["ten"], "vung": d["vung"]} for k, d in doan_all.items()],
        "ty_le": {
            "chi_phi_chung": {"gia_tri": chuan["chi_phi_chung"].get("gia_tri"), "co_so": chuan["chi_phi_chung"].get("co_so", "T"), "can_cu": ""},
            "cong_viec_khong_xd_kl": {"gia_tri": chuan["cong_viec_khong_xd_kl"].get("gia_tri"), "can_cu": ""},
            "thu_nhap_chiu_thue_tt": {"gia_tri": chuan["thu_nhap_chiu_thue_tt"].get("gia_tri"), "can_cu": ""},
            "nha_tam": {"gia_tri": 0, "can_cu": "CHƯA KHAI BÁO — nhập theo Bảng 3.7 PL III TT 36/2026"},
            "thue_gtgt": {"gia_tri": chuan["thue_gtgt"].get("gia_tri"), "can_cu": ""},
        },
        "ty_le_theo_ma": rieng,
        "tong_hop": [],
    }
    with open(os.path.join(a.ra, "config_du_toan.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    def _ghi_bao_cao():
        with open(os.path.join(a.ra, "bao_cao_nhap.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(bc) + "\n")

    # N-1: ghi báo cáo TRƯỚC bước đối chiếu đơn giá — không để lỗi nap_config làm mất báo cáo
    _ghi_bao_cao()
    # đối chiếu đơn giá khối: tính lại từ hao phí × giá theo PL III, so với đơn giá trong file
    try:
        from dutoan_core import DuLieu, nap_config, don_gia_chi_tiet
        dl = DuLieu(a.ra)
        cfg_l = nap_config(os.path.join(a.ra, "config_du_toan.json"))
        lech = []
        for b in blocks:
            if "key" not in b:
                continue
            r = {"ma_hieu": b["key"], "quy_doi": 1 / b["E"], "hs_vl": 1.0, "hs_nc": 1.0, "hs_m": 1.0, "dg_tg": None}
            for v in vung:
                got = don_gia_chi_tiet(dl, cfg_l, r, v)["DG"]
                file_v = b["dg"].get(v)
                if file_v is not None and abs(got - file_v) > 0.5:
                    lech.append(f"- Khối {b['ma']} (dòng {b['row']}), {v}: file {file_v:,.0f} — tính lại {got:,.0f} (chênh {got - file_v:+,.0f})")
        bc.append("")
        bc.append("## Đối chiếu đơn giá từng khối (tính lại theo PL III TT 36/2026, làm tròn từng bước)")
        bc.extend(lech or ["- Tất cả khối khớp."])
    except SystemExit as e:
        bc.append("")
        bc.append("## Đối chiếu đơn giá từng khối — CHƯA ĐỐI CHIẾU ĐƯỢC")
        bc.append(f"- Lỗi ở bước đối chiếu: {e}")
        bc.append("- Dữ liệu đã ghi đủ (dinh_muc.csv, gia_tai_nguyen.csv, khoi_luong.csv, config_du_toan.json); "
                  "bổ sung tỷ lệ còn thiếu vào config_du_toan.json rồi chạy `dutoan.py tinh` để đối chiếu.")
        if a.kieu == "gxd":
            bc.append("- Chế độ GXD: tỷ lệ C/TT/TL/GTGT nằm ở sheet THCP của file GXD, chưa nhập ở chế độ này — "
                      "nhập tay tỷ lệ từ THCP vào config rồi tính lại.")
        _ghi_bao_cao()
        print("\n".join(bc))
        print(f"\nĐã ghi bộ dữ liệu vào {a.ra} (chưa đối chiếu đơn giá — xem bao_cao_nhap.md)")
        return 1
    bc.append("")
    bc.append("## Tổng trong file gốc (để đối chiếu sau khi tính lại)")
    for hm, t in tong_dt.items():
        if t.get("truoc_thue") is None and t.get("vat") is None and t.get("sau_thue") is None:
            bc.append(f"- {hm}: (tổng nằm ở sheet THCP của file gốc, chưa nhập)")
        else:
            bc.append(f"- {hm}: trước thuế {t.get('truoc_thue')}, VAT {t.get('vat')}, sau thuế {t.get('sau_thue')}")
    if rieng:
        bc.append("")
        bc.append("## Mã có tỷ lệ riêng (khác tỷ lệ phổ biến)")
        for k, v in rieng.items():
            bc.append(f"- {k}: " + ", ".join(f"{kk} = {vv['gia_tri']} ({vv.get('co_so','T')})" for kk, vv in v.items()))
    _ghi_bao_cao()
    print("\n".join(bc))
    print(f"\nĐã ghi bộ dữ liệu vào {a.ra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
