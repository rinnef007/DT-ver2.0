#!/usr/bin/env python3
"""Nhập một hồ sơ dự toán khảo sát có sẵn (mẫu đơn vị: khối đơn giá theo vùng + bảng giá trị khảo sát + TH KP),
tính lại theo PL V TT 36/2026 và chỉ ra chênh lệch.

  python scripts/nhap_ks_excel.py --file DT_KS.xls [--ra du-lieu/ks-x] [--vung-nc HN-V1-KV1,HY-V2,HY-V3,HP-V1,HP-V2] [--tinh-lai]

Tự nhận diện (theo nội dung, không cố định tên sheet):
- Sheet đơn giá chi tiết: tiêu đề "Thành phần hao phí", mỗi vùng một cột đơn giá và một cột thành tiền; khối mỗi công việc
  gồm các dòng hao phí (a/b/c), dòng % và các dòng có ký hiệu ở cột Đơn vị: T, C, LT/TT, GT, TL, Cpa, Cbc, G, GTGT.
- Sheet giá trị khảo sát (bảng khối lượng): Đơn giá là công thức trỏ sang sheet đơn giá chi tiết; dòng cuối có ký hiệu
  G, GTGT, LT, Cdp, Gks ở cột Đơn vị.
- Sheet tổng hợp (TH KP): tiêu đề "Khoản mục chi phí".

Kiểm tra: từng khối × từng vùng (thành tiền dòng hao phí, %, T, C, TT, GT, TL, Cpa, Cbc, G, GTGT) tính lại từ hao phí,
đơn giá, hệ số và tỷ lệ ghi trong file; nhãn và ký hiệu (LT/TT, nhãn ghi nhầm); công thức lấy tỷ lệ ở dòng khác; tỷ lệ
so với nấc Bảng 5.1–5.3 theo quy mô thực tế; bảng giá trị (đơn giá đúng vùng của khu vực, thành tiền, G, GTGT, LT, Cdp,
Gks); tổng hợp (sau thuế = trước thuế + thuế, khớp bảng giá trị); diễn giải số người so với khối lượng; giá nhân công
so với văn bản của Sở XD (khi có --vung-nc).

--ra: ghi bộ dữ liệu của skill (dinh_muc, gia_tai_nguyen, khoi_luong, config) để `dutoan.py tinh` tái lập hồ sơ;
--tinh-lai: chạy luôn và so tổng với file. Số liệu trích từ file là số của hồ sơ đó, không thay văn bản gốc.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dutoan_core import bo_dau, so, ty_le_chuan_ks, nhan_cong_tham_chieu, khoa_ten  # noqa: E402
from nhap_du_toan_excel import mo_file, txt  # noqa: E402
from openpyxl.utils import column_index_from_string  # noqa: E402

TAG_DG = {"t", "c", "lt", "tt", "gt", "tl", "cpa", "cbc", "g", "gtgt", "gxd", "cpvks"}
RE_REF = re.compile(r"(?:'([^']+)'|([A-Za-z_][\w\.]*))!\$?([A-Z]{1,3})\$?(\d+)")


def r0(x):
    """Làm tròn kiểu Excel ROUND(x, 0) (nửa lên, xa 0)."""
    return float(int(abs(x) + 0.5 + 1e-9)) * (1 if x >= 0 else -1)


def sg(x):
    """Số ghi CSV không mất chữ số (tránh định dạng :g chỉ giữ 6 chữ số)."""
    x = float(x)
    return str(int(x)) if x.is_integer() else repr(round(x, 10))


def f(x):
    return f"{x:,.0f}".replace(",", ".")


# ----------------------------------------------------------------- sheet đơn giá chi tiết
def tim_sheet_dg(wv):
    for ws in wv.worksheets:
        for r in range(1, 12):
            vals = [bo_dau(txt(ws.cell(r, c).value)) for c in range(1, min(ws.max_column, 30) + 1)]
            if any("thanh phan hao phi" in v for v in vals) and any(v.startswith("don gia") for v in vals) \
                    and any(v.startswith("thanh tien") for v in vals):
                tags = {bo_dau(txt(ws.cell(x, 4).value)) for x in range(r, min(ws.max_row, r + 80) + 1)}
                if {"cpa", "cbc"} & tags or "cpvks" in tags:
                    return ws.title, r
    return None, None


def doc_dg(wv, wf, ten, r_td):
    ws, wsf = wv[ten], wf[ten]
    vals = [bo_dau(txt(ws.cell(r_td, c).value)) for c in range(1, ws.max_column + 1)]
    c_dg = next(i + 1 for i, v in enumerate(vals) if v.startswith("don gia"))
    c_hs = next((i + 1 for i, v in enumerate(vals) if v.startswith("he so")), None)
    c_tt = next(i + 1 for i, v in enumerate(vals) if v.startswith("thanh tien"))
    n = (c_hs or c_tt) - c_dg
    r_vung = r_td + 1
    vung = [txt(ws.cell(r_vung, c_dg + j).value) or f"Vùng {j+1}" for j in range(n)]
    blocks, cur, sec = [], None, None
    for r in range(r_vung + 1, ws.max_row + 1):
        A, B, C, D, E = (ws.cell(r, c).value for c in range(1, 6))
        Af = wsf.cell(r, 1).value
        tag = bo_dau(txt(D))
        if (A not in (None, "") or (isinstance(Af, str) and Af.startswith("="))) and txt(C) and tag not in TAG_DG:
            cur = dict(row=r, stt=A, ma=txt(B), ten=txt(C), dv=txt(D), dong=[], tag={}, sec=None)
            blocks.append(cur); sec = None
            continue
        if cur is None:
            continue
        ct = bo_dau(txt(C))
        if re.match(r"^[abc]\)", ct):
            sec = {"a": "VL", "b": "NC", "c": "M"}[ct[0]]
            continue
        if tag in TAG_DG:
            cur["tag"].setdefault(tag, []).append(r)
            continue
        if so(E) is not None and txt(D) and sec:
            gia = [so(ws.cell(r, c_dg + j).value, 0) for j in range(n)]
            tien = [so(ws.cell(r, c_tt + j).value, 0) for j in range(n)]
            hs = so(ws.cell(r, c_hs).value, 1) if c_hs else 1
            loai = sec + "K" if txt(D) == "%" else sec
            cur["dong"].append(dict(row=r, loai=loai, ma=txt(B), ten=txt(C), dv=txt(D), hp=so(E), hs=hs, gia=gia, tien=tien))
    return dict(sheet=ten, ws=ws, wsf=wsf, c_dg=c_dg, c_tt=c_tt, c_hs=c_hs, n=n, vung=vung, blocks=blocks)


def ty_le_dong(ws, r):
    v = ws.cell(r, 5).value
    x = so(v)
    if x is None:
        return None
    return x / 100 if x > 1 else x


def tinh_khoi(dg, b, bc):
    """Tính lại một khối cho từng vùng; ghi chênh lệch vào bc. Trả về {tag: [giá trị theo vùng]} và tỷ lệ."""
    ws, wsf, n = dg["ws"], dg["wsf"], dg["n"]
    ten = f"Khối {b['stt']} {b['ma']} ({b['ten'][:45]})"
    rate = {}
    for k in ("c", "lt", "tt", "tl", "cpa", "cbc", "gtgt"):
        if k in b["tag"]:
            rate[k] = ty_le_dong(ws, b["tag"][k][0])
    if "lt" in rate and "tt" not in rate:
        rate["tt"] = rate.pop("lt"); b["tag"]["tt"] = b["tag"].pop("lt")
        bc["nhom"].setdefault("Chi phí không xác định được KL mang ký hiệu 'LT' — theo PL V TT 36 là khoản thuộc GT "
                              "(ký hiệu TT); LT là nhà tạm. Sửa ký hiệu ở các dòng", []).append(str(b['tag']['tt'][0]))
    # nhãn: nội dung cột Thành phần hao phí so với ký hiệu
    for k, rows in b["tag"].items():
        for r in rows:
            nhan = bo_dau(txt(ws.cell(r, 3).value))
            sai = (k == "tt" and "thue gia tri gia tang" in nhan) or (k == "gtgt" and "khong xac dinh" in nhan) \
                or (k == "c" and "thue" in nhan)
            if sai:
                bc["nhan"].append(f"{ten}: dòng {r} ký hiệu {k.upper()} nhưng nhãn ghi \"{txt(ws.cell(r, 3).value)[:60]}\" — sửa nhãn.")
            m = re.search(r"x\s*(\d+(?:[.,]\d+)?)\s*%", nhan)
            if m and rate.get(k) is not None and abs(float(m.group(1).replace(",", ".")) / 100 - rate[k]) > 1e-9:
                bc["nhom"].setdefault(f"Nhãn {k.upper()} ghi {m.group(1)}% nhưng tỷ lệ dùng {rate[k]*100:g}% — sửa nhãn cho khớp, "
                                      "các dòng", []).append(str(r))
            fm = wsf.cell(r, dg["c_tt"]).value
            if isinstance(fm, str):
                for mm in re.finditer(r"\$?E\$?(\d+)", fm):
                    if int(mm.group(1)) != r:
                        bc["cong_thuc"].append(f"{ten}: dòng {r} ({k.upper()}) lấy tỷ lệ ở ô E{mm.group(1)} của dòng khác "
                                               f"(công thức {fm[:50]}) — nên trỏ về E{r}.")
    out = defaultdict(lambda: [0.0] * n)
    for j in range(n):
        sec_sum = defaultdict(float)
        for d in b["dong"]:
            if d["loai"] in ("VLK", "NCK", "MK"):
                tien = r0(d["hp"] * sec_sum[d["loai"][:-1] if d["loai"] != "NCK" else "NC"] / 100)
            else:
                tien = r0(d["hp"] * d["gia"][j] * d["hs"])
            if abs(tien - d["tien"][j]) > 0.5:
                bc["so"].append(f"{ten}, {dg['vung'][j]}: dòng {d['row']} {d['ten'][:30]} file {f(d['tien'][j])} — tính lại {f(tien)}")
            sec_sum[d["loai"].rstrip("K") if d["loai"] != "NCK" else "NC"] += tien
        VL, NC, M = (r0(sec_sum[k]) for k in ("VL", "NC", "M"))
        T = VL + NC + M
        C = r0(NC * (rate.get("c") or 0))
        TT = r0(T * (rate.get("tt") or 0))
        GT = C + TT
        TL = r0((T + GT) * (rate.get("tl") or 0))
        base = T + GT + TL
        CPA = r0(base * (rate.get("cpa") or 0))
        CBC = r0(base * (rate.get("cbc") or 0))
        G = base + CPA + CBC
        GTGT = r0(G * (rate.get("gtgt") or 0))
        for k, v in (("vl", VL), ("nc", NC), ("m", M), ("t", T), ("c", C), ("tt", TT), ("gt", GT), ("tl", TL),
                     ("cpa", CPA), ("cbc", CBC), ("g", G), ("gtgt", GTGT)):
            out[k][j] = v
            if k in b["tag"]:
                fv = so(ws.cell(b["tag"][k][0], dg["c_tt"] + j).value, 0)
                if abs(fv - v) > 0.5:
                    bc["so"].append(f"{ten}, {dg['vung'][j]}: {k.upper()} file {f(fv)} — tính lại {f(v)} (lệch {f(fv - v)})")
    return out, rate


# ----------------------------------------------------------------- bảng giá trị khảo sát
def tim_bang_gt(wv, wf, dg_sheet):
    kq = []
    for ws in wv.worksheets:
        if ws.title == dg_sheet:
            continue
        wsf = wf[ws.title]
        r_td, vals = None, None
        for r in range(1, 12):
            v = [bo_dau(txt(ws.cell(r, c).value)) for c in range(1, min(ws.max_column, 12) + 1)]
            if any("khoi luong" in x for x in v) and any(x.startswith("don gia") for x in v) and any("thanh tien" in x for x in v):
                r_td, vals = r, v
                break
        if not r_td:
            continue
        c_ten = next((i + 1 for i, x in enumerate(vals) if "hang muc" in x or "noi dung" in x or "cong viec" in x), None)
        c_dv = next((i + 1 for i, x in enumerate(vals) if x.startswith("don vi")), None)
        c_kl = next((i + 1 for i, x in enumerate(vals) if "khoi luong" in x), None)
        c_dg = next((i + 1 for i, x in enumerate(vals) if x.startswith("don gia")), None)
        c_tt = next((i + 1 for i, x in enumerate(vals) if "thanh tien" in x), None)
        if None in (c_ten, c_dv, c_kl, c_dg, c_tt):
            continue
        so_ref = sum(1 for r in range(r_td + 1, ws.max_row + 1)
                     if isinstance(wsf.cell(r, c_dg).value, str) and dg_sheet in wsf.cell(r, c_dg).value)
        if so_ref:
            kq.append((ws.sheet_state == "visible", so_ref, ws.title, r_td, c_ten, c_dv, c_kl, c_dg, c_tt))
    kq.sort(reverse=True)
    return kq


def doc_bang_gt(wv, wf, info, dg, khoi_cua_dong):
    _, _, ten, r_td, c_ten, c_dv, c_kl, c_dg, c_tt = info
    ws, wsf = wv[ten], wf[ten]
    dong, tong, nhom, nhom2 = [], {}, "", ""
    for r in range(r_td + 1, ws.max_row + 1):
        A = txt(ws.cell(r, 1).value)
        T = txt(ws.cell(r, c_ten).value)
        DV = txt(ws.cell(r, c_dv).value)
        tag = bo_dau(DV)
        if tag in ("g", "gtgt", "lt", "cdp", "gks"):
            tong.setdefault(tag, dict(row=r, ten=T, gt=so(ws.cell(r, c_tt).value), ghi_chu=" ".join(
                txt(ws.cell(r, c).value) for c in range(c_tt + 1, c_tt + 3)).strip()))
            continue
        fm = wsf.cell(r, c_dg).value
        kl = so(ws.cell(r, c_kl).value)
        if isinstance(fm, str) and dg["sheet"] in fm and kl is not None:
            m = RE_REF.search(fm)
            col, row = column_index_from_string(m.group(3)), int(m.group(4))
            if dg["c_dg"] <= col < dg["c_dg"] + dg["n"]:
                j = col - dg["c_dg"]
            elif dg["c_tt"] <= col < dg["c_tt"] + dg["n"]:
                j = col - dg["c_tt"]
            else:
                j = None
            b = khoi_cua_dong.get(row)
            dong.append(dict(row=r, nhom=nhom, nhom2=nhom2, ten=T, dv=DV, kl=kl, dg=so(ws.cell(r, c_dg).value, 0),
                             tt=so(ws.cell(r, c_tt).value, 0), khoi=b, vung=j, ref=fm))
        elif T and not DV:
            if re.match(r"^[IVXLC]+$", A) or re.match(r"^[A-Z]$", A):
                nhom, nhom2 = T, ""
            elif A:
                nhom2 = T
    return dict(sheet=ten, dong=dong, tong=tong, ws=ws)


def doan_vung_nhom(ten, dg):
    """Đoán vùng giá từ tên nhóm (vd. 'Khu vực Hưng Yên (vùng II)') — chỉ dùng để cảnh báo, không gán."""
    t = bo_dau(ten)
    tinh = next((k for k in ("ha noi", "hung yen", "hai phong") if k in t), None)
    if not tinh:
        return None
    ung = [j for j, v in enumerate(dg["vung"]) if tinh in bo_dau(v)]
    m = re.search(r"vung\s*(i{1,3}v?|iv|\d)", t)
    if m and len(ung) > 1:
        so_v = {"i": "1", "ii": "2", "iii": "3", "iv": "4"}.get(m.group(1), m.group(1))
        u2 = [j for j in ung if re.search(rf"vung\s*{so_v}\b", bo_dau(dg["vung"][j]))]
        ung = u2 or ung
    return ung or None


# ----------------------------------------------------------------- tổng hợp
def tim_th(wv, wf):
    for ws in wv.worksheets:
        if ws.sheet_state != "visible":
            continue
        for r in range(1, 10):
            v = [bo_dau(txt(ws.cell(r, c).value)) for c in range(1, min(ws.max_column, 12) + 1)]
            if any("khoan muc chi phi" in x for x in v):
                c_tr = next((i + 1 for i, x in enumerate(v) if "truoc thue" in x), None)
                c_th = next((i + 1 for i, x in enumerate(v) if x.startswith("thue gtgt")), None)
                c_st = next((i + 1 for i, x in enumerate(v) if "sau thue" in x), None)
                c_km = next(i + 1 for i, x in enumerate(v) if "khoan muc chi phi" in x)
                if c_tr and c_st:
                    return ws.title, r, c_km, c_tr, c_th, c_st
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", required=True)
    ap.add_argument("--ra", help="Thư mục ghi báo cáo và bộ dữ liệu tái lập (mặc định: cạnh file)")
    ap.add_argument("--vung-nc", help="Mã vùng nhân công (data/nhan-cong) theo thứ tự các cột vùng, cách nhau bởi dấu phẩy")
    ap.add_argument("--xac-nhan", action="store_true", help="Đánh dấu khối lượng là đã xác nhận (chỉ dùng khi tái lập để đối chiếu)")
    ap.add_argument("--tinh-lai", action="store_true", help="Chạy dutoan.py tinh trên bộ dữ liệu và so tổng với file")
    a = ap.parse_args()
    wv, wf, path = mo_file(a.file)
    ra = a.ra or os.path.splitext(a.file)[0] + "_nhap"
    os.makedirs(ra, exist_ok=True)
    bc = dict(nhom={}, so=[], nhan=[], cong_thuc=[], ty_le=[], bang=[], tong=[], dien_giai=[], gia=[], thong_tin=[])

    ten_dg, r_td = tim_sheet_dg(wv)
    if not ten_dg:
        sys.exit("Không tìm thấy sheet đơn giá chi tiết khảo sát (tiêu đề 'Thành phần hao phí' và các dòng Cpa/Cbc).")
    dg = doc_dg(wv, wf, ten_dg, r_td)
    khoi_cua_dong, KQ = {}, {}
    for b in dg["blocks"]:
        rows = [b["row"]] + [r for rs in b["tag"].values() for r in rs]
        for r in rows:
            khoi_cua_dong[r] = b["row"]
        KQ[b["row"]], b["rate"] = tinh_khoi(dg, b, bc)
    stt = [b["stt"] for b in dg["blocks"]]
    trung = [s for s, c in Counter(stt).items() if c > 1]
    if trung:
        bc["nhan"].append(f"Số thứ tự khối trùng ở sheet {ten_dg}: {', '.join(map(str, trung))} (khối {', '.join(b['ma'] for b in dg['blocks'] if b['stt'] in trung)}).")
    ma_trung = [m for m, c in Counter(b["ma"] for b in dg["blocks"]).items() if c > 1]
    for m in ma_trung:
        bc["thong_tin"].append(f"Mã {m} dùng cho nhiều khối khác nhau ({'; '.join(b['ten'][:40] for b in dg['blocks'] if b['ma'] == m)}) — "
                               "nên phân biệt mã (vd. thêm hậu tố theo thời gian chiếm dụng).")

    # bảng giá trị
    ds = tim_bang_gt(wv, wf, ten_dg)
    if not ds:
        sys.exit("Không tìm thấy bảng giá trị khảo sát (cột Đơn giá trỏ sang sheet đơn giá chi tiết).")
    bgt = doc_bang_gt(wv, wf, ds[0], dg, khoi_cua_dong)
    if len(ds) > 1:
        bc["thong_tin"].append("Các sheet khác cũng trỏ sang đơn giá chi tiết (không dùng để đối chiếu): " +
                               ", ".join(x[2] for x in ds[1:]))
    G = 0.0
    nc_t = t_t = tgt_t = 0.0
    for d in bgt["dong"]:
        b = next((x for x in dg["blocks"] if x["row"] == d["khoi"]), None)
        if b is None or d["vung"] is None:
            bc["bang"].append(f"Dòng {d['row']} \"{d['ten'][:50]}\": đơn giá {d['ref']} không trỏ vào ô đơn giá/G của một khối — kiểm tra.")
            continue
        j = d["vung"]
        k = KQ[b["row"]]
        if abs(d["dg"] - k["g"][j]) > 0.5:
            bc["bang"].append(f"Dòng {d['row']} \"{d['ten'][:50]}\": đơn giá {f(d['dg'])} — tính lại {f(k['g'][j])}.")
        tt = r0(d["kl"] * k["g"][j])
        if abs(tt - d["tt"]) > 0.5:
            bc["bang"].append(f"Dòng {d['row']} \"{d['ten'][:50]}\": thành tiền {f(d['tt'])} — tính lại {f(tt)}.")
        G += tt
        nc_t += d["kl"] * k["nc"][j]; t_t += d["kl"] * k["t"][j]; tgt_t += d["kl"] * (k["t"][j] + k["gt"][j] + k["tl"][j])
        for nh in (d["nhom2"], d["nhom"]):
            u = doan_vung_nhom(nh, dg) if nh else None
            if u:
                if j not in u:
                    bc["bang"].append(f"Dòng {d['row']} \"{d['ten'][:45]}\" thuộc \"{nh[:45]}\" nhưng lấy đơn giá cột "
                                      f"\"{dg['vung'][j][:40]}\" — kiểm tra vùng giá.")
                break
        m = re.search(r"\(\s*0?(\d+)\s*(?:kỹ sư|ky su|người|nguoi)", bo_dau(d["ten"]))
        if m and bo_dau(d["dv"]) == "cong" and int(m.group(1)) > 1 and d["kl"] < int(m.group(1)):
            bc["dien_giai"].append(f"Dòng {d['row']} \"{d['ten'][:60]}\": diễn giải {m.group(1)} người, khối lượng {d['kl']:g} công — "
                                   f"ghi rõ số ngày mỗi người (vd. {m.group(1)} người × {d['kl']/int(m.group(1)):g} ngày).")
        d["j"], d["b"] = j, b
    # tổng bảng giá trị
    tg = bgt["tong"]
    vat = next((b["rate"].get("gtgt") for b in dg["blocks"] if b["rate"].get("gtgt")), 0.08)

    def ty_le_nhan(t):
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", t or "")
        return float(m.group(1).replace(",", ".")) / 100 if m else None
    GTGT = r0(G * vat)
    tl_lt = ty_le_nhan(tg.get("lt", {}).get("ten"))
    tl_dp = ty_le_nhan(tg.get("cdp", {}).get("ten"))
    LT = r0((G + GTGT) * tl_lt) if tl_lt and tg.get("lt", {}).get("gt") else 0
    DP = r0((G + GTGT) * tl_dp) if tl_dp and tg.get("cdp", {}).get("gt") is not None else 0
    GKS = G + GTGT + LT + DP
    for k, v in (("g", G), ("gtgt", GTGT), ("lt", LT), ("cdp", DP), ("gks", GKS)):
        if k in tg:
            fv = tg[k]["gt"] or 0
            if abs(fv - v) > 0.5:
                bc["tong"].append(f"{bgt['sheet']} dòng {tg[k]['row']} ({k.upper()}): file {f(fv)} — tính lại {f(v)} (lệch {f(fv - v)}).")
    if "lt" in tg and not tg["lt"]["gt"]:
        bc["thong_tin"].append(f"Không tính nhà tạm (LT){' — ghi chú: ' + tg['lt']['ghi_chu'] if tg['lt']['ghi_chu'] else ''}: "
                               "ghi lý do trong thuyết minh (vd. thời gian khảo sát ngắn ngày).")
    if tl_dp:
        if tl_dp > 0.10 + 1e-9:
            bc["ty_le"].append(f"Dự phòng {tl_dp*100:g}% vượt mức tối đa 10% (PL V TT 36).")
        elif abs(tl_dp - 0.10) < 1e-9:
            bc["thong_tin"].append("Dự phòng lấy mức tối đa 10% — nêu cơ sở trong thuyết minh.")

    # nấc tỷ lệ theo quy mô thực tế
    chuan = ty_le_chuan_ks({}, nc_t / 1e9, t_t / 1e9, tgt_t / 1e9) or {}
    map_k = {"c": "chi_phi_chung", "tt": "cong_viec_khong_xd_kl", "cpa": "lap_phuong_an_ks", "cbc": "lap_bao_cao_ks"}
    for b in dg["blocks"]:
        for k, ck in map_k.items():
            v = b["rate"].get(k)
            if v and ck in chuan and abs(v * 100 - chuan[ck]) > 1e-6:
                bc["ty_le"].append(f"Khối {b['stt']} {b['ma']}: {k.upper()} {v*100:g}% khác Bảng 5.x theo quy mô thực tế → {chuan[ck]:g}%.")
            if k in ("cpa", "cbc") and not v and k in b["tag"]:
                bc["thong_tin"].append(f"Khối {b['stt']} {b['ma']} ({b['ten'][:40]}): {k.upper()} = 0 — ghi lý do trong thuyết minh.")
        if b["rate"].get("tl") not in (None, 0.06):
            bc["ty_le"].append(f"Khối {b['stt']} {b['ma']}: TL {b['rate']['tl']*100:g}% (PL V: 6%).")
        if not b["dong"]:
            bc["thong_tin"].append(f"Khối {b['stt']} {b['ma']}: không có dòng hao phí.")
    ma_pl1 = [b for b in dg["blocks"] if not re.match(r"^C[A-Z]\.\d{5}", b["ma"])]
    if ma_pl1:
        bc["thong_tin"].append("Khối không theo mã định mức khảo sát PL I TT 38 (lập theo công, ca hoặc định mức khác) — ghi lý do: " +
                               ", ".join(f"{b['ma'] or '(trống)'}" for b in ma_pl1))

    # giá nhân công theo văn bản
    if a.vung_nc:
        mv = [x.strip() for x in a.vung_nc.split(",")]
        NCT = nhan_cong_tham_chieu()
        thay = set()
        for b in dg["blocks"]:
            for d in b["dong"]:
                if d["loai"] != "NC":
                    continue
                for j, gia in enumerate(d["gia"]):
                    if j >= len(mv) or not mv[j]:
                        continue
                    ref = NCT.get((mv[j], khoa_ten(d["ten"])))
                    if ref and abs(so(ref["don_gia"], 0) - gia) > 0.5 and (d["ten"], j) not in thay:
                        thay.add((d["ten"], j))
                        bc["gia"].append(f"{d['ten']} tại \"{dg['vung'][j][:40]}\" ({mv[j]}): file {f(gia)} — {ref.get('van_ban') or ref.get('nguon', '')} {f(so(ref['don_gia'], 0))}.")
                    elif ref is None and (d["ten"], -1) not in thay:
                        thay.add((d["ten"], -1))
                        bc["gia"].append(f"{d['ten']}: không tìm được tên nhân công tương ứng trong data/nhan-cong ({mv[j]}).")

    # tổng hợp TH KP
    th = tim_th(wv, wf)
    th_rows = []
    if th:
        tn, rt, c_km, c_tr, c_th, c_st = th
        ws = wv[tn]
        for r in range(rt + 1, ws.max_row + 1):
            km = txt(ws.cell(r, c_km).value)
            if not km or bo_dau(km).startswith("bang chu"):
                continue
            tr, th_, st = (so(ws.cell(r, c).value) if c else None for c in (c_tr, c_th, c_st))
            if tr is None and st is None:
                continue
            th_rows.append((r, km, tr, th_, st))
            if tr is not None and th_ is not None and st is not None and abs(tr + th_ - st) > 0.5:
                bc["tong"].append(f"{tn} dòng {r} \"{km[:40]}\": trước thuế + thuế = {f(tr + th_)} ≠ sau thuế {f(st)}.")
            kb = bo_dau(km)
            mong = None
            if "khao sat xay dung" in kb:
                mong = GKS
            elif "nha tam" in kb:
                mong = LT
            elif "du phong" in kb:
                mong = DP
            elif kb.startswith("chi phi khao sat"):
                mong = G + GTGT
            if mong is not None and st is not None and abs(st - mong) > 0.5:
                bc["tong"].append(f"{tn} dòng {r} \"{km[:40]}\": sau thuế {f(st)} — tính lại {f(mong)}.")
        bc["thong_tin"].append(f"Sheet tổng hợp: {tn}. Các khoản ngoài chi phí khảo sát (vd. lập dự toán phương án sửa chữa) "
                               "không tính lại ở đây — kiểm tra theo PL VIII TT 38 (`dutoan.py ty-le`).")

    # ----- báo cáo
    L = [f"# Nhập và tính lại hồ sơ khảo sát — {os.path.basename(a.file)}", "",
         f"- Sheet đơn giá chi tiết: **{ten_dg}** — {len(dg['blocks'])} khối, {dg['n']} vùng giá: " +
         "; ".join(f"V{j+1} = {v}" for j, v in enumerate(dg["vung"])),
         f"- Bảng giá trị khảo sát: **{bgt['sheet']}** — {len(bgt['dong'])} dòng công việc", "",
         "## Kết quả tính lại", "",
         "| Khoản | File | Tính lại | Chênh lệch |", "|---|---:|---:|---:|"]
    for k, v, ten in (("g", G, "Chi phí khảo sát trước thuế (G)"), ("gtgt", GTGT, "Thuế GTGT"), ("lt", LT, "Nhà tạm (LT)"),
                      ("cdp", DP, "Dự phòng (Cdp)"), ("gks", GKS, "Chi phí khảo sát (Gks)")):
        fv = (tg.get(k) or {}).get("gt") or 0
        L.append(f"| {ten} | {f(fv)} | {f(v)} | {f(fv - v)} |")
    L += ["", f"Quy mô thực tế: NC {f(nc_t)} · T {f(t_t)} · T+GT+TL {f(tgt_t)} đ → nấc PL V: " +
          ", ".join(f"{k} {v:g}%" for k, v in chuan.items() if k in map_k.values()), ""]
    muc = [("so", "Số liệu khối đơn giá tính lại khác file"), ("bang", "Bảng giá trị khảo sát"), ("tong", "Tổng hợp"),
           ("ty_le", "Tỷ lệ so với PL V TT 36"), ("nhan", "Nhãn, ký hiệu, số thứ tự"), ("cong_thuc", "Công thức"),
           ("dien_giai", "Diễn giải và khối lượng"), ("gia", "Giá nhân công so với văn bản của Sở XD"),
           ("thong_tin", "Ghi nhận (cần lý do trong thuyết minh, không phải lỗi tính)")]
    for k, v in bc["nhom"].items():
        bc["nhan"].append(f"{k} {', '.join(v)} (sheet {ten_dg}).")
    for k, t in muc:
        L += [f"## {t} ({len(bc[k])})", ""] + ([f"- {x}" for x in dict.fromkeys(bc[k])] or ["- Không có."]) + [""]
    L += ["Ghi chú: tính lại dùng hao phí, đơn giá, hệ số và tỷ lệ ghi trong file (làm tròn từng bước như mẫu). "
          "Không kiểm tra nguồn đơn giá vật liệu, ca máy (công bố giá thay đổi liên tục) — đối chiếu với công bố của Sở XD tại thời điểm lập."]

    # ----- bộ dữ liệu tái lập
    vids = [f"V{j+1}" for j in range(dg["n"])]
    ma_khoi, dm_rows, gia, gia_key = {}, [], OrderedDict(), {}
    for b in dg["blocks"]:
        ma = re.sub(r"\s+", "", b["ma"]) or f"KS.K{b['stt']}"
        goc, i = ma, 2
        while ma in ma_khoi.values():
            ma = f"{goc}-{i}"; i += 1
        ma_khoi[b["row"]] = ma
        for d in b["dong"]:
            if d["loai"] in ("VLK", "NCK", "MK"):
                dm_rows.append(dict(ma_hieu=ma, ten_cong_tac=b["ten"], don_vi=b["dv"], loai=d["loai"].replace("NCK", "NC"), ma_tn="",
                                    ten_tn=d["ten"], don_vi_tn="%", hao_phi=sg(d['hp']), he_so="1", can_cu_he_so="", ly_do="",
                                    nguon=f"Trích từ {os.path.basename(a.file)}"))
                continue
            key = (d["ten"], tuple(d["gia"]))
            if key not in gia_key:
                ten_tn, i = d["ten"], 2
                while any(k[0] == d["ten"] for k in gia_key) and ten_tn in gia_key.values():
                    ten_tn = f"{d['ten']} ({i})"; i += 1
                gia_key[key] = ten_tn
                for j, v in enumerate(vids):
                    gia[(ten_tn, v)] = dict(ma_tn=ten_tn, ten_tn=ten_tn, don_vi=d["dv"], loai=d["loai"], vung=v, don_gia=sg(d['gia'][j]),
                                            nguon=f"Trích từ {os.path.basename(a.file)}", ngay_ap_dung="", khu_vuc="", ty_le_luong="")
            ten_tn = gia_key[key]
            dm_rows.append(dict(ma_hieu=ma, ten_cong_tac=b["ten"], don_vi=b["dv"], loai=d["loai"], ma_tn=ten_tn, ten_tn=ten_tn,
                                don_vi_tn=d["dv"], hao_phi=sg(d['hp']), he_so=sg(d['hs']),
                                can_cu_he_so="trích từ hồ sơ" if d["hs"] != 1 else "", ly_do="", nguon=f"Trích từ {os.path.basename(a.file)}"))
    b0 = next((b for b in dg["blocks"] if b["rate"].get("cbc")), dg["blocks"][0])

    def tl(k, ck, can):
        return {"gia_tri": b0["rate"].get(k) or 0, "can_cu": can, **({"co_so": "NC"} if ck == "chi_phi_chung" else {})}
    ty_le = {"chi_phi_chung": tl("c", "chi_phi_chung", "Bảng 5.1 PL V TT 36 (theo file)"),
             "cong_viec_khong_xd_kl": tl("tt", "", "Bảng 5.2 PL V TT 36 (theo file)"),
             "thu_nhap_chiu_thue_tt": tl("tl", "", "PL V TT 36 (theo file)"),
             "lap_phuong_an_ks": tl("cpa", "", "Bảng 5.3 PL V TT 36 (theo file)"),
             "lap_bao_cao_ks": tl("cbc", "", "Bảng 5.3 PL V TT 36 (theo file)"),
             "nha_tam": {"gia_tri": tl_lt if LT else 0, "can_cu": "PL V TT 36 (theo file)" + ("" if LT else " — file không tính")},
             "du_phong": {"gia_tri": tl_dp or 0, "can_cu": "PL V TT 36 (theo file)"},
             "thue_gtgt": {"gia_tri": vat, "can_cu": "theo file"}}
    theo_ma = {}
    for b in dg["blocks"]:
        for k, ck in (("c", "chi_phi_chung"), ("tt", "cong_viec_khong_xd_kl"), ("tl", "thu_nhap_chiu_thue_tt"),
                      ("cpa", "lap_phuong_an_ks"), ("cbc", "lap_bao_cao_ks")):
            v = b["rate"].get(k) or 0
            if abs(v - ty_le[ck]["gia_tri"]) > 1e-12:
                theo_ma.setdefault(ma_khoi[b["row"]], {})[ck] = {"gia_tri": v, "can_cu": "Theo file (khối này dùng tỷ lệ riêng)",
                                                                **({"co_so": "NC"} if ck == "chi_phi_chung" else {})}
    dung = sorted({d["j"] for d in bgt["dong"] if "j" in d})
    cfg = {"du_an": f"Tái lập {os.path.basename(a.file)}", "cong_trinh": os.path.basename(a.file),
           "loai_cong_trinh": "giao_thong", "che_do_chi_phi": "tt36_khao_sat", "mau_xuat": "doan_vung", "lam_tron": "tung_buoc",
           "quy_mo_nc_ty": round(nc_t / 1e9, 6), "quy_mo_t_ty": round(t_t / 1e9, 6), "quy_mo_t_gt_tl_ty": round(tgt_t / 1e9, 6),
           "vung": [{"id": v, "ten": dg["vung"][j]} for j, v in enumerate(vids)],
           "doan": [{"id": vids[j], "ten": dg["vung"][j], "vung": vids[j]} for j in dung],
           "ty_le": ty_le, "ty_le_theo_ma": theo_ma}
    if a.vung_nc:
        mv = [x.strip() for x in a.vung_nc.split(",")]
        for j, v in enumerate(cfg["vung"]):
            if j < len(mv) and mv[j]:
                v["nhan_cong"] = mv[j]
    kl_rows = []
    for i, d in enumerate([d for d in bgt["dong"] if "j" in d], 1):
        kl_rows.append(dict(stt=i, hang_muc=d["nhom"] or "Khảo sát", ma_hieu=ma_khoi[d["b"]["row"]], cap_phoi="", ten_cong_tac=d["ten"],
                            don_vi=d["dv"], doan=vids[d["j"]], khoi_luong=sg(d['kl']), quy_doi="1", he_so_vl="1", he_so_nc="1",
                            he_so_m="1", can_cu_he_so="", don_gia_tron_goi="", dien_giai=d["ten"],
                            nguon_ban_ve=f"{bgt['sheet']} dòng {d['row']}", trang_thai="xac_nhan" if a.xac_nhan else "de_xuat"))

    def ghi(ten, rows):
        with open(os.path.join(ra, ten), "w", encoding="utf-8", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    ghi("dinh_muc.csv", dm_rows); ghi("gia_tai_nguyen.csv", list(gia.values())); ghi("khoi_luong.csv", kl_rows)
    json.dump(cfg, open(os.path.join(ra, "config_du_toan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if a.tinh_lai:
        out = os.path.join(ra, "tai_lap.xlsx")
        p = subprocess.run([sys.executable, os.path.join(HERE, "dutoan.py"), "tinh", "--data", ra, "--khoi-luong",
                            os.path.join(ra, "khoi_luong.csv"), "--config", os.path.join(ra, "config_du_toan.json"), "--out", out, "--nhap"],
                           capture_output=True, text=True)
        js = os.path.splitext(out)[0] + "_doi_chieu.json"
        L += ["", "## Tái lập bằng skill (`dutoan.py tinh`)", ""]
        if os.path.exists(js):
            t = json.load(open(js, encoding="utf-8"))["tong_hop"]
            sk_g = sum(v[0] for k, v in t.items() if k.startswith("HM"))
            sk_tong = t.get("TONG", [0, 0, 0])[2]
            L += [f"- G: file {f((tg.get('g') or {}).get('gt') or 0)} · skill {f(sk_g)}",
                  f"- Gks: file {f((tg.get('gks') or {}).get('gt') or 0)} · skill {f(sk_tong)}",
                  f"- File tái lập: `{out}` (bản nháp nếu còn mục chặn)."]
        else:
            L += ["- Không tính được: " + (p.stderr or p.stdout)[-600:]]
    open(os.path.join(ra, "bao_cao_nhap_ks.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:20]))
    print(f"... Báo cáo đầy đủ: {os.path.join(ra, 'bao_cao_nhap_ks.md')}")


if __name__ == "__main__":
    main()
