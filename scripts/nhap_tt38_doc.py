#!/usr/bin/env python3
"""Trích bảng hao phí định mức từ file Phụ lục TT 38/2026/TT-BXD (Word .doc/.docx) sang dinh_muc.csv chuẩn của Skill.

  python nhap_tt38_doc.py --file Phu_luc.doc --ra data/tt38

Đầu ra:
  dinh_muc_tt38.csv      ma_hieu, ten_cong_tac, don_vi, loai, ma_tn, ten_tn, don_vi_tn, hao_phi, he_so, can_cu_he_so, nguon, phu_luc, chuong
  danh_muc_ma_tt38.csv   ma_hieu, ten_cong_tac, don_vi, phu_luc, chuong, nhom (mã nhóm 5 số), tieu_de_nhom
  bao_cao_trich.md       số bảng đọc được, số mã, bảng không nhận dạng được (cần xem tay)

Cách đọc bảng (theo bố cục chuẩn của TT 38):
- Dòng tiêu đề có "Mã hiệu"; các cột giá trị ứng với từng biến thể (vd. cấp đất, chiều dày…).
- Dòng cuối toàn số (1, 2, 3…) là hậu tố mã: mã đầy đủ = tiền tố ở cột "Mã hiệu" + hậu tố (vd. AA.1211 + 1 → AA.12111).
- Dòng "Vật liệu" / "Nhân công" / "Máy thi công" là tiêu đề nhóm; dòng đơn vị "%" là vật liệu khác / máy khác.
- Ô "-" hoặc trống: biến thể đó không có hao phí; biến thể không có hao phí nào thì bỏ.
- Bảng không có cột "Thành phần hao phí" (chỉ ghi nhân công): lấy tên nhân công và đơn vị từ đoạn văn ngay trước bảng.
Kết quả cần đối chiếu ngẫu nhiên với văn bản gốc trước khi dùng; bảng lạ được liệt kê trong báo cáo.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter, OrderedDict

try:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    sys.exit("Thiếu python-docx: pip install python-docx")

RE_PL = re.compile(r"Phụ lục\s+([IVX]+)\s+kèm theo Thông tư số 38/2026", re.I)
RE_CHUONG = re.compile(r"^\s*CH(?:Ư|U)ƠNG\s+([IVXL]+)\b", re.I)
RE_NHOM = re.compile(r"^\s*([A-Z]{1,3}\.\d{4,5}0{0,2})\s{1,}(.+)$")
RE_DVT = re.compile(r"Đơn vị tính\s*:\s*(.+)$", re.I)
RE_MA = re.compile(r"^[A-Z]{1,3}\.\d{2,6}[a-z]?$")
TEN_PL = {"I": "PL I – Khảo sát", "II": "PL II – Dự toán xây dựng công trình", "III": "PL III – Lắp đặt hệ thống kỹ thuật",
          "IV": "PL IV – Lắp đặt máy và thiết bị công nghệ", "V": "PL V – Thí nghiệm chuyên ngành",
          "VI": "PL VI – Sửa chữa và bảo dưỡng công trình", "VII": "PL VII – Định mức sử dụng vật liệu",
          "VIII": "PL VIII – Chi phí QLDA và tư vấn"}


def so(s):
    s = (s or "").strip().replace(" ", "").replace(" ", "")
    if s in ("", "-", "–", "—", "x", "X"):
        return None
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", s):
        s = s.replace(".", "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def chuan(s):
    s = (s or "").replace("\n", " ").replace("³", "3").replace("²", "2").replace("\u00a0", " ")
    s = re.sub(r"\s*-\s+(?=loại)", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def mo_docx(path):
    if path.lower().endswith(".doc"):
        tmp = tempfile.mkdtemp()
        subprocess.run(["soffice", "--headless", "--convert-to", "docx", "--outdir", tmp, path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)
        path = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".docx")
        if not os.path.exists(path):
            sys.exit("Không chuyển được .doc sang .docx (cần LibreOffice)")
    return docx.Document(path)


def luong(d):
    for el in d.element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "p":
            yield "p", unicodedata.normalize("NFC", Paragraph(el, d).text)
        elif tag == "tbl":
            rows = []
            for r in Table(el, d).rows:
                try:
                    rows.append([unicodedata.normalize("NFC", c.text).strip() for c in r.cells])
                except Exception:
                    rows.append([])
            yield "t", rows


def loai_tu_nhom(nhom, ten, dv):
    t = ten.lower()
    if dv.strip() == "%":
        if nhom == "M" or "máy" in t:
            return "MK"
        return "VLK"
    return nhom


TIEU_DE_NHOM = {"vật liệu", "vật tư", "nhân công", "máy thi công", "máy", "máy và thiết bị thi công"}


def la_tieu_de(x):
    return x.strip().lower().rstrip(":") in TIEU_DE_NHOM


def tach_dong(rows, c_tp):
    """Ô gộp nhiều dòng (vd. 'Vật liệu\nỐng nhựa\nCùm nối' / '100,5\n19') → tách thành nhiều dòng.
    Dòng tiêu đề nhóm (Vật liệu/Nhân công/Máy thi công) trong ô thành phần có thể có hoặc không có dòng tương ứng
    ở các cột khác; thử khớp theo vị trí trước, rồi khớp bỏ qua dòng tiêu đề."""
    out = []
    for r in rows:
        if c_tp is None or c_tp >= len(r) or "\n" not in r[c_tp]:
            out.append([chuan(c) for c in r])
            continue
        tp_all = []
        for x in r[c_tp].split("\n"):
            m = re.match(r"^(.*\S)\s+(Máy thi công|Vật liệu|Nhân công)\s*:?$", x.strip())
            tp_all += [m.group(1), m.group(2)] if m and not la_tieu_de(x) else [x.strip()]
        while tp_all and not tp_all[-1]:
            tp_all.pop()
        tp_all = [x for x in tp_all if x] if not all(tp_all) and len([x for x in tp_all if x]) else tp_all
        muc = [(i, x) for i, x in enumerate(tp_all) if x and not la_tieu_de(x)]
        if len(tp_all) <= 1:
            out.append([chuan(c) for c in r])
            continue
        cols = {}
        ok = True
        for i, c in enumerate(r):
            if i == c_tp:
                continue
            raw = [x.strip() for x in c.split("\n")]
            while raw and not raw[-1]:
                raw.pop()
            nonempty = [x for x in raw if x]
            if len(nonempty) <= 1 and (i < c_tp or not any(so(x) is not None for x in nonempty)) and len(raw) <= 1:
                cols[i] = ("mot", nonempty[0] if nonempty else "")
            elif len(raw) == len(tp_all):
                cols[i] = ("vitri", raw)
            elif len(nonempty) == len(muc):
                cols[i] = ("tuantu", nonempty)
            elif len(raw) == len(muc):
                cols[i] = ("tuantu", raw)
            else:
                ok = False
                break
        if not ok:
            out.append([chuan(c) for c in r])
            continue
        k_muc = 0
        for j, x in enumerate(tp_all):
            if not x:
                continue
            dong = []
            for i in range(len(r)):
                if i == c_tp:
                    dong.append(chuan(x))
                    continue
                kieu, val = cols[i]
                if kieu == "mot":
                    dong.append(chuan(val) if i < c_tp else "")
                elif la_tieu_de(x):
                    dong.append(chuan(val[j]) if kieu == "vitri" else "")
                elif kieu == "vitri":
                    dong.append(chuan(val[j]))
                else:
                    dong.append(chuan(val[k_muc]) if k_muc < len(val) else "")
            if not la_tieu_de(x):
                k_muc += 1
            out.append(dong)
    return out


RE_MAY = re.compile(r"((?:máy|ô ?tô|xe|tàu|sà lan|cần cẩu|cẩu|xáng)[^,;()]*)", re.I)


def may_tu_ten(ten):
    """Lấy tên máy từ tên công tác khi bảng không ghi riêng (vd. 'Đào móng bằng máy đào 0,4m3' → 'Máy đào 0,4m3')."""
    t = re.sub(r"^-\s*nt\s*-\s*", "", ten or "", flags=re.I)
    m = RE_MAY.search(t)
    if not m:
        return ""
    x = m.group(1).strip()
    return x[0].upper() + x[1:]


def gop_doc(rows, c_tp):
    """Tiền xử lý bố cục bảng Word:
    1) ô 'Mã hiệu' chứa nhiều mã (vd. 'AB.1141\nAB.1142') kèm giá trị nhiều dòng → tách thành nhiều dòng;
    2) ô 'Thành phần hao phí' gộp dọc (lặp nguyên văn ở nhiều dòng) còn đơn vị/giá trị chia ra từng dòng → gộp lại một dòng."""
    out = []
    for r in rows:
        ma_lines = [x.strip() for x in (r[0] if r else "").split("\n") if x.strip()]
        if len(ma_lines) > 1 and all(RE_MA.match(x.replace(" ", "")) for x in ma_lines):
            n = len(ma_lines)
            cols = []
            for c in r:
                ls = [x.strip() for x in c.split("\n")]
                ls = [x for x in ls if x] if len([x for x in ls if x]) == n else ls
                cols.append(ls if len(ls) == n else [c.strip()] * n)
            for k in range(n):
                out.append([col[k] for col in cols])
            continue
        out.append(list(r))
    # bỏ dòng lặp nguyên văn (ô gộp dọc toàn bộ)
    loc = []
    for r in out:
        k0 = c_tp if c_tp is not None else 2
        if loc and len(r) == len(loc[-1]) and any(x.strip() for x in r[k0:]) and [x.strip() for x in r[k0:]] == [x.strip() for x in loc[-1][k0:]]:
            for i in range(k0):
                if not loc[-1][i].strip() and r[i].strip():
                    loc[-1][i] = r[i]
            continue
        loc.append(r)
    out = loc
    if c_tp is None:
        return out
    # giá trị gộp dọc (lặp ở nhiều dòng), thành phần hao phí chia từng dòng → gộp thành phần
    gop2 = []
    for r in out:
        if (gop2 and len(r) == len(gop2[-1]) and c_tp < len(r)
                and any("\n" in x for x in r[c_tp + 1:])
                and [x.strip() for x in r[c_tp + 1:]] == [x.strip() for x in gop2[-1][c_tp + 1:]]
                and r[c_tp].strip() != gop2[-1][c_tp].strip() and not r[0].strip()):
            gop2[-1][c_tp] = gop2[-1][c_tp].rstrip("\n") + "\n" + r[c_tp].strip()
            continue
        gop2.append(list(r))
    out = gop2
    gop = []
    for r in out:
        if (gop and c_tp < len(r) and "\n" in r[c_tp] and r[c_tp].strip() == gop[-1][c_tp].strip()
                and len(r) == len(gop[-1]) and (not r[0].strip() or r[0].strip() == gop[-1][0].strip() or not gop[-1][0].strip())):
            prev = gop[-1]
            for i in range(len(r)):
                if i in (c_tp,) or i < c_tp:
                    if not prev[i].strip() and r[i].strip():
                        prev[i] = r[i]
                    continue
                a, b = prev[i].rstrip("\n"), r[i].rstrip("\n")
                prev[i] = (a + "\n" + b) if a and b else (a or b)
            continue
        gop.append(list(r))
    return gop


def doc_bang(rows, ctx):
    """Trả về list (ma, ten, don_vi, [hao phí]) hoặc None nếu không nhận dạng được."""
    rows = [r for r in rows if r and any(c for c in r)]
    _h = [chuan(c) for c in rows[0]] if rows else []
    _ctp = next((i for i, c in enumerate(_h) if "hao phí" in c.lower()), None)
    rows = gop_doc(rows, _ctp)
    rows = tach_dong(rows, _ctp)
    if len(rows) < 3:
        return None
    hdr_idx = [i for i, r in enumerate(rows) if r and "mã hiệu" in r[0].lower()]
    if not hdr_idx:
        return None
    last_hdr = hdr_idx[-1]
    hdr = rows[:last_hdr + 1]
    ncol = max(len(r) for r in rows)
    # dòng hậu tố
    suf_row = rows[-1]
    vals = [c for c in suf_row if c]
    if not vals or not all(re.fullmatch(r"\d{1,3}", v) for v in vals):
        return None
    # xác định cột
    h0 = hdr[0]
    co_tp = any("hao phí" in c.lower() for c in h0)
    if co_tp:
        c_tp = next(i for i, c in enumerate(h0) if "hao phí" in c.lower())
        c_dv = c_tp + 1
        c_val0 = c_dv + 1
    else:
        c_tp = None
        c_dv = next((i for i, c in enumerate(h0) if c.lower().startswith("đơn vị")), None)
        c_val0 = (c_dv + 1) if c_dv is not None else 2
    val_cols = [i for i in range(c_val0, len(suf_row)) if re.fullmatch(r"\d{1,3}", suf_row[i] or "")]
    if not val_cols:
        return None
    # loại bỏ cột trùng do ô gộp
    seen, vc = set(), []
    for i in val_cols:
        if suf_row[i] not in seen:
            seen.add(suf_row[i])
            vc.append(i)
    val_cols = vc
    # nhãn biến thể từ dòng tiêu đề
    nhan = {}
    for i in val_cols:
        parts = []
        for r in hdr:
            if i < len(r) and r[i] and r[i] not in parts and "Mã hiệu" not in r[i]:
                parts.append(r[i])
        nhan[i] = " – ".join(parts)
    body = rows[last_hdr + 1:-1]
    ket_qua = OrderedDict()
    prefix, ten_ct, nhom = None, None, None
    for r in body:
        r = r + [""] * (ncol - len(r))
        if r[0] and RE_MA.match(r[0].replace(" ", "")):
            p = r[0].replace(" ", "")
            if p != prefix:
                prefix, ten_ct, nhom = p, r[1], None
            elif r[1]:
                ten_ct = r[1]
        elif r[0] and not prefix:
            continue
        if prefix is None:
            continue
        if co_tp:
            tp, dv = r[c_tp], r[c_dv]
            tl = tp.lower().rstrip(":").strip()
            if tl in ("vật liệu", "vật tư"):
                nhom = "VL"
                if not any(so(r[i]) is not None for i in val_cols):
                    continue
            elif tl in ("nhân công",):
                nhom = "NC"
                if not any(so(r[i]) is not None for i in val_cols):
                    continue
            elif tl in ("máy thi công", "máy", "máy và thiết bị thi công"):
                nhom = "M"
                if not any(so(r[i]) is not None for i in val_cols):
                    continue
            if not tp and dv.lower().startswith("ca") and any(so(r[i]) is not None for i in val_cols):
                tp = may_tu_ten(ten_ct) or "Máy thi công (tên theo công tác)"
            if tl in ("máy thi công", "máy") and dv.lower().startswith("ca") and any(so(r[i]) is not None for i in val_cols):
                tp = may_tu_ten(ten_ct) or tp
            if not tp:
                continue
            n = nhom
            if tp.lower().startswith("nhân công") or tp.lower().startswith("kỹ sư") or tp.lower().startswith("công nhân"):
                n = "NC"
            if n is None:
                n = "VL"
            loai = loai_tu_nhom(n, tp, dv)
            if loai == "VL" and dv.strip().lower() == "ca":
                loai = "M"
            elif loai == "VL" and dv.strip().lower() == "công":
                loai = "NC"
        else:
            dv = r[c_dv] if c_dv is not None else (ctx.get("nc_dv") or "công")
            if dv.lower().startswith("ca"):
                loai = "M"
                tp = may_tu_ten(ten_ct) or ten_ct
            elif dv.lower().startswith("công") or c_dv is None:
                loai = "NC"
                tp = ctx.get("nc_ten") or "Nhân công"
            else:
                loai = "VL"
                tp = ten_ct
        for i in val_cols:
            v = so(r[i])
            if v is None:
                continue
            ma = prefix + suf_row[i]
            ten = ten_ct + (f" ({nhan[i]})" if nhan.get(i) else "")
            e = ket_qua.setdefault(ma, {"ten": ten, "hp": []})
            e["hp"].append((loai, tp, dv, v))
    if not ket_qua:
        return None
    return ket_qua


RE_COT_VL = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")


def doc_cap_phoi(rows, ctx):
    """Bảng cấp phối vữa (PL VII): Mã hiệu | Loại vật liệu/vữa | Mác | <Vật liệu (đơn vị)>… → list dòng."""
    rows = [[chuan(c) for c in r] for r in rows if r and any(c for c in r)]
    if len(rows) < 3:
        return None
    hdr = rows[1] if len(rows) > 1 else rows[0]
    c_mac = next((i for i, c in enumerate(hdr) if c.lower().startswith("mác")), None)
    if c_mac is None:
        return None
    cot = []
    for i in range(c_mac + 1, len(hdr)):
        m = RE_COT_VL.match(hdr[i])
        if m:
            cot.append((i, m.group(1).strip(), m.group(2).strip()))
        elif hdr[i].lower().startswith("phụ gia"):
            cot.append((i, "Phụ gia", "loại"))
    if not cot:
        return None
    out, quy_cach = [], ""
    for r in rows[2:]:
        r = r + [""] * (len(hdr) - len(r))
        ma = r[0].replace(" ", "")
        if not re.fullmatch(r"\d{2}\.\d{5}", ma):
            continue
        qc = r[1]
        if qc:
            if qc[0] in "([" or qc[0].isdigit() or qc[0].islower():
                if qc not in quy_cach:
                    quy_cach = f"{quy_cach} {qc}".strip()
            elif not quy_cach.startswith(qc):
                quy_cach = qc
        for i, ten, dv in cot:
            v = r[i]
            if not v:
                continue
            if ten == "Phụ gia":
                out.append((ma, quy_cach, r[c_mac], ten, "", v))
                continue
            x = so(v)
            if x is not None:
                out.append((ma, quy_cach, r[c_mac], ten, dv, x))
    return out


def doc_hao_hut(rows, nhom):
    """Bảng hao hụt (PL VII Phần 2) → list (mã, vật liệu/công tác, chỉ tiêu, giá trị, đơn vị)."""
    rows = [[chuan(c) for c in r] for r in rows if r and any(c for c in r)]
    hdr = [r for r in rows if r and r[0].lower().startswith("mã hiệu")]
    if not hdr:
        return []
    h = hdr[-1]
    out = []
    for r in rows[len(hdr):]:
        ma = r[0].replace(" ", "")
        if not re.fullmatch(r"21\.\d{4}", ma):
            continue
        if nhom.startswith("21.4"):
            out.append((ma, r[1], f"{r[3]} cần cho {r[2]}", so(r[5]) if len(r) > 5 else None, r[4] if len(r) > 4 else ""))
        else:
            for i in range(2, len(r)):
                x = so(r[i])
                if x is not None:
                    out.append((ma, r[1], h[i] if i < len(h) else "", x, "%"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", required=True)
    ap.add_argument("--ra", required=True)
    a = ap.parse_args()
    d = mo_docx(a.file)
    os.makedirs(a.ra, exist_ok=True)
    pl, chuong, nhom_ma, nhom_ten, dvt = "", "", "", "", ""
    nc_ten, nc_dv = "", ""
    recent = []
    ma_all = OrderedDict()
    loi, dem_bang = [], Counter()
    cap_phoi, hao_hut = [], []
    ten_cp_nhom, ten_cp_sub = "", ""
    RE_NHOM_VII = re.compile(r"^\s*(\d{2}\.\d{4,5})\s*-?\s+(.+)$")
    for k, v in luong(d):
        if k == "t":
            v = [[c for c in r] for r in v]
        if k == "p":
            t = chuan(v)
            if not t:
                continue
            m = RE_PL.search(t)
            if m:
                pl = m.group(1).upper()
                chuong = ""
            m = RE_CHUONG.match(t)
            if m:
                chuong = m.group(1).upper()
            m = RE_NHOM.match(t)
            if m:
                nhom_ma, nhom_ten = m.group(1), m.group(2)
            if pl == "VII" and re.match(r"^\s*(Độ sụt|Độ xòe)", t, re.I) and "tiếp theo" not in t:
                ten_cp_sub = t.strip()
            if pl == "VII":
                m = RE_NHOM_VII.match(t)
                if m:
                    nhom_ma, nhom_ten = m.group(1), m.group(2).strip(" -")
                    tu = t.upper()
                    if "XI MĂNG" in tu or ("CẤP PHỐI" in tu and "VỮA" in tu):
                        ten_cp_nhom, ten_cp_sub = nhom_ten, ""
                    elif re.search(r"độ (sụt|xòe)", t, re.I):
                        ten_cp_sub = nhom_ten
            m = RE_DVT.search(t)
            if m:
                dvt = m.group(1).strip()
                if "/" in dvt and dvt.lower().startswith("công"):
                    nc_dv = "công"
                    dvt = dvt.split("/", 1)[1].strip()
            if re.match(r"^(Nhân công|Kỹ sư|Công nhân)\b", t) and len(t) < 60:
                nc_ten = t
            recent = (recent + [t])[-8:]
            continue
        if pl == "VII":
            if nhom_ma.startswith("21."):
                for x in doc_hao_hut(v, nhom_ma):
                    hao_hut.append((nhom_ma, nhom_ten) + x)
                continue
            cp = doc_cap_phoi(v, {})
            if cp:
                for x in cp:
                    cap_phoi.append((ten_cp_nhom, ten_cp_sub) + x)
                dem_bang["cap_phoi"] += 1
            continue
        if not pl or pl == "VIII":
            dem_bang["bo_qua_pl_" + (pl or "?")] += 1
            continue
        if not v or not v[0] or "mã hiệu" not in chuan(v[0][0] if v[0] else "").lower():
            dem_bang["khong_phai_bang_dinh_muc"] += 1
            continue
        kq = doc_bang(v, {"nc_ten": nc_ten, "nc_dv": nc_dv})
        if kq is None:
            dem_bang["khong_nhan_dang"] += 1
            loi.append(f"PL {pl} · nhóm {nhom_ma} {nhom_ten[:60]} · đoạn trước: {' / '.join(recent[-2:])[:120]}")
            continue
        dem_bang["doc_duoc"] += 1
        for ma, e in kq.items():
            if ma in ma_all:
                ma = f"{ma}@{pl}"
            ma_all[ma] = dict(e, don_vi=dvt, pl=pl, chuong=chuong, nhom=nhom_ma, nhom_ten=nhom_ten)
    out = os.path.join(a.ra, "dinh_muc_tt38.csv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_hieu", "ten_cong_tac", "don_vi", "loai", "ma_tn", "ten_tn", "don_vi_tn", "hao_phi", "he_so",
                    "can_cu_he_so", "nguon", "phu_luc", "chuong"])
        for ma, e in ma_all.items():
            goc = e["nhom"].rstrip("0").rstrip(".")
            hop = bool(goc) and ma.startswith(goc)
            ten = f"{e['nhom_ten'].capitalize()} – {e['ten']}" if hop and e["nhom_ten"].lower() not in e["ten"].lower() else e["ten"]
            for loai, tp, dv, v in e["hp"]:
                w.writerow([ma, ten, e["don_vi"], loai, "" if loai in ("VLK", "MK") else tp, tp, dv, f"{v:g}", 1, "",
                            f"TT38/2026 {TEN_PL.get(e['pl'], e['pl'])}", e["pl"], e["chuong"]])
    with open(os.path.join(a.ra, "danh_muc_ma_tt38.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_hieu", "ten_cong_tac", "don_vi", "phu_luc", "chuong", "nhom", "tieu_de_nhom"])
        for ma, e in ma_all.items():
            w.writerow([ma, e["ten"], e["don_vi"], e["pl"], e["chuong"], e["nhom"], e["nhom_ten"]])
    with open(os.path.join(a.ra, "cap_phoi_tt38.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_cap_phoi", "nhom", "do_sut_hoac_nhom_con", "quy_cach", "mac", "vat_lieu", "don_vi", "so_luong", "nguon"])
        for nh, sub, ma, qc, mac, vl, dv, x in cap_phoi:
            vl = vl[0].upper() + vl[1:].replace(" Dăm", " dăm").replace(" Vàng", " vàng") if vl else vl
            w.writerow([ma, nh, sub, qc, mac, vl, dv, x if isinstance(x, str) else f"{x:g}", "TT38/2026 PL VII – cấp phối (chưa gồm hao hụt)"])
    with open(os.path.join(a.ra, "hao_hut_tt38.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma", "nhom", "tieu_de_nhom", "vat_lieu_cong_tac", "chi_tieu", "gia_tri", "don_vi", "nguon"])
        for nm, nt, ma, vl, ct, x, dv in hao_hut:
            w.writerow([ma, nm, nt, vl, ct, "" if x is None else f"{x:g}", dv, "TT38/2026 PL VII Phần 2"])
    nghi = sorted(ma for ma, e in ma_all.items()
                  if any(tp.strip().lower().rstrip(":") in TIEU_DE_NHOM for _, tp, _, _ in e["hp"]))
    with open(os.path.join(a.ra, "ma_can_kiem_tra.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_hieu", "ly_do"])
        for ma in nghi:
            w.writerow([ma, "Bảng gốc trình bày ô gộp không đều — dữ liệu trích có thể lệch dòng, đối chiếu văn bản"])
    theo_pl = Counter(e["pl"] for e in ma_all.values())
    bc = ["# Báo cáo trích định mức TT 38/2026", "",
          f"- Bảng đọc được: {dem_bang['doc_duoc']}; bảng không nhận dạng (cần xem tay): {dem_bang['khong_nhan_dang']}",
          f"- Số mã định mức: {len(ma_all)} — " + ", ".join(f"PL {k}: {v}" for k, v in sorted(theo_pl.items())),
          f"- PL VII: {len({x[2] for x in cap_phoi})} mã cấp phối vữa ({len(cap_phoi)} dòng) → cap_phoi_tt38.csv; {len(hao_hut)} dòng hao hụt → hao_hut_tt38.csv. Các bảng PL VII khác (xây, trát, ván khuôn, hàn…) chưa trích.",
          "- PL VIII (chi phí QLDA, tư vấn) không trích bằng công cụ này.",
          "- Mã tài nguyên (`ma_tn`) = tên vật liệu/nhân công/máy như trong TT 38 — bảng giá phải dùng đúng tên này.",
          "- Mã trùng giữa các phụ lục được thêm hậu tố `@<phụ lục>`.",
          f"- {len(nghi)} mã nghi lệch dòng do ô gộp không đều → ma_can_kiem_tra.csv (soát S18 cảnh báo khi dùng).", "",
          "## Bảng không nhận dạng được (mã thuộc các bảng này chưa có trong dữ liệu — tra văn bản)"]
    bc += [f"- {x}" for x in loi[:300]]
    with open(os.path.join(a.ra, "bao_cao_trich.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(bc) + "\n")
    print("\n".join(bc[:6]))


if __name__ == "__main__":
    main()
