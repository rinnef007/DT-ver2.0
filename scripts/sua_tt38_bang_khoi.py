#!/usr/bin/env python3
"""Sửa các mã TT 38 trích sai do bảng trình bày theo khối (tên – đơn vị – số liệu tách rời).

Lỗi điển hình sau khi trích bằng nhap_tt38_doc.py:
  - cột đơn vị bị gộp thành một ô ("m3 m3 m3 công ca ca %"), hai tên vật liệu dính nhau;
  - "Máy khác", "Vật liệu khác" bị ghi thành máy/vật liệu thường (hao phí % thành số ca);
  - tên nhân công dính tiêu đề ("Nhân công nhóm 2 Máy thi công"), đơn vị là số.

Cách làm: tìm các mã có dấu hiệu trên, đọc lại bảng gốc từ bản text của phụ lục (pandoc/antiword),
tách thành các đoạn [tên…][đơn vị…][số…], gán theo cột mã. Chỉ thay khi kết quả đọc lại nhất quán
(số giá trị = số tài nguyên × số mã) và khớp phần lớn số liệu cũ; còn lại ghi vào ma_can_kiem_tra.

  python scripts/sua_tt38_bang_khoi.py --txt Phu_luc.txt --data data/tt38 [--ghi]
"""
import argparse
import collections
import csv
import gzip
import os
import re
import unicodedata

HDR_VL = {"Vật liệu", "Vật liệu:"}
HDR_NC = {"Nhân công", "Nhân công:"}
HDR_M = {"Máy thi công", "Máy thi công:", "Máy và thiết bị thi công"}
DV = {"m3", "m2", "m", "kg", "tấn", "công", "ca", "%", "cái", "bộ", "lít", "viên", "tờ", "cây", "thanh", "đôi", "hộp", "chiếc",
      "quả", "gói", "cuộn", "lọ", "tấm", "cặp", "mẫu", "kWh", "md", "tuýp", "g", "ống", "bình", "lần", "giờ", "km", "sợi", "túi",
      "bao", "can", "chai", "que", "con", "cục", "lít/ca", "m3/ca", "100m", "tạ", "đoạn", "mét", "chai", "kw", "kW"}
RE_SO = re.compile(r"^(?:-?\d+(?:[.,]\d+)*|-|–)$")
RE_TIEU_DE = re.compile(r"^[A-Z]{2}\.\d{5}\s+\S")
RE_TACH = re.compile(r"\s+(?=(?:Vật liệu khác|Máy khác|Nhân công nhóm|Máy thi công|Kỹ sư\b))")


def nfc(s):
    s = unicodedata.normalize("NFC", s).replace("m³", "m3").replace("m²", "m2").strip()
    return re.sub(r"\s+", " ", s)


def so(t):
    t = t.strip()
    if t in ("-", "–"):
        return None
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return float(t)


def khoa(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")
    return re.sub(r"[\s.,;:\-–()]+", "", s)


def ma_loi(rs):
    for r in rs:
        u, n = r["don_vi_tn"], r["ma_tn"]
        if len(u.split()) > 1 or RE_SO.match(u or "x"):
            return True
        if re.search(r"khác$", n, re.I) and r["loai"] in ("VL", "M", "NC"):
            return True
        if r["loai"] == "NC" and not re.match(r"(Nhân công nhóm [1-4]|Kỹ sư|Thợ lặn|Nghệ nhân)$", n):
            return True
        if r["loai"] == "M" and u not in ("ca", "%", ""):
            return True
    return False


def doc_bang(L, i0, cac_hau_to):
    """Đọc token của bảng bắt đầu sau dòng tiền tố i0; trả list tài nguyên mỗi mã {hau_to: [(loai, ten, dv, hp)]}."""
    tok = []
    i = i0 + 1
    title_skipped = False
    while i < len(L) and len(tok) < 600:
        l = L[i]
        i += 1
        if not l:
            continue
        if RE_TIEU_DE.match(l) or l.startswith(("Quy định áp dụng", "Ghi chú", "Thành phần công việc")):
            break
        if re.fullmatch(r"[A-Z]{2}\.\d{2,5}", l.replace(" ", "")):
            break
        if not title_skipped:
            title_skipped = True
            continue
        for p in RE_TACH.split(l):
            p = nfc(p)
            if not p:
                continue
            w = p.split()
            if len(w) > 1 and all(x in DV or x.lower() in DV for x in w):
                tok.extend(w)  # nhiều đơn vị trong một ô
            else:
                tok.append(p)
    # bỏ dãy hậu tố mã ở cuối (vd. 11 12 13 14 hoặc 01 02 …)
    k = len(cac_hau_to)
    if tok[-k:] == cac_hau_to:
        tok = tok[:-k]
    elif tok[:k] == cac_hau_to:
        tok = tok[k:]
    # không thấy dãy hậu tố: vẫn thử đọc — kiểm tra số lượng số liệu bên dưới sẽ loại trường hợp lệch
    # phân đoạn
    seg = []  # mỗi phần tử: {"ten": [...], "dv": [...], "so": [...], "loai": [...]}
    loai_ht = "VL"
    cur = None
    for t in tok:
        if t in HDR_VL:
            loai_ht = "VL"
            continue
        if t in HDR_NC:
            loai_ht = "NC"
            continue
        if t in HDR_M:
            loai_ht = "M"
            continue
        if RE_SO.match(t):
            if cur is None:
                return None, f"số đứng trước tên ({t})"
            cur["so"].append(so(t))
            continue
        if t in DV or t.lower() in DV:
            if cur is None or cur["so"]:
                cur = {"ten": [], "loai": [], "dv": [], "so": []}
                seg.append(cur)
            cur["dv"].append(t)
            continue
        # tên
        if all(w in DV or w.lower() in DV for w in t.split()):
            return None, f"token đơn vị dính nhau '{t}'"
        t = re.sub(r"^nhóm ([1-4])$", r"Nhân công nhóm \1", t)
        if cur is None or cur["so"] or cur["dv"]:
            cur = {"ten": [], "loai": [], "dv": [], "so": []}
            seg.append(cur)
        if re.match(r"Nhân công nhóm|Kỹ sư|Thợ lặn|Nghệ nhân", t):
            lo = "NC"
        elif t.startswith("Vật liệu khác"):
            lo = "VLK"
        elif t.startswith("Máy khác"):
            lo = "MK"
        else:
            lo = "NC" if loai_ht == "NC" and not re.match(r"Máy|Ô tô|Cần|Tàu|Sà lan|Xà lan", t) else loai_ht
            if lo == "NC":
                lo = "M" if loai_ht == "M" else "VL"
        cur["ten"].append(t)
        cur["loai"].append(lo)
    # khối đơn vị đứng riêng (không tên) → gán tuần tự cho các tài nguyên thiếu đơn vị phía sau
    kq = {h: [] for h in cac_hau_to}
    cho_dv = []
    for s in seg:
        if not s["ten"]:
            cho_dv.extend(s["dv"])
            continue
        n = len(s["ten"])
        if s["so"] and len(s["so"]) != n * k:
            return None, f"đoạn {s['ten'][:2]}: {len(s['so'])} số ≠ {n}×{k}"
        dv = list(s["dv"])
        if not dv and cho_dv:
            dv, cho_dv = cho_dv[:n], cho_dv[n:]
        if dv and len(dv) != n:
            return None, f"đoạn {s['ten'][:2]}: {len(dv)} đơn vị ≠ {n} tên"
        if not s["so"]:
            return None, f"đoạn {s['ten'][:2]} không có số"
        for j, (ten, lo) in enumerate(zip(s["ten"], s["loai"])):
            d = dv[j] if dv else {"NC": "công", "M": "ca", "VLK": "%", "MK": "%"}.get(lo, "")
            if lo in ("VLK", "MK"):
                d = "%"
            if lo == "VL" and not d:
                return None, f"vật liệu '{ten}' không có đơn vị"
            for c, h in enumerate(cac_hau_to):
                v = s["so"][c * n + j] if n > 1 else s["so"][c]
                if v is not None:
                    kq[h].append((lo, ten, d, v))
    if cho_dv:
        return None, f"thừa {len(cho_dv)} đơn vị chưa gán"
    return kq, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--txt", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--ghi", action="store_true")
    a = ap.parse_args()
    L = [nfc(l) for l in open(a.txt, encoding="utf-8").read().split("\n")]
    p_dm = os.path.join(a.data, "dinh_muc_tt38.csv.gz")
    rows = list(csv.DictReader(gzip.open(p_dm, "rt", encoding="utf-8")))
    cot = list(rows[0].keys())
    by = collections.OrderedDict()
    for r in rows:
        by.setdefault(r["ma_hieu"], []).append(r)
    loi = {m for m, rs in by.items() if ma_loi(rs)}
    pref = collections.defaultdict(list)
    for i, l in enumerate(L):
        x = l.replace(" ", "")
        if re.fullmatch(r"[A-Z]{2}\.\d{2,5}", x):
            pref[x].append(i)
    nhom = collections.defaultdict(list)
    for m in loi:
        for k in range(len(m), 5, -1):
            if m[:k] in pref:
                nhom[m[:k]].append(m)
                break
    da_sua, khong_sua, bao_cao, ghi_chu = {}, {}, [], {}
    for p, cac_ma in sorted(nhom.items()):
        ca_bang = sorted(m for m in by if m.startswith(p) and len(m) - len(p) <= 3 and m[len(p):].isdigit())
        hau = [m[len(p):] for m in ca_bang]
        kq, ly_do = None, "không đọc được"
        for i0 in pref[p]:
            kq, ly_do = doc_bang(L, i0, hau)
            if kq:
                break
        if not kq:
            for m in cac_ma:
                khong_sua[m] = ly_do
            bao_cao.append(f"- {p}: GIỮ NGUYÊN ({ly_do}) — {', '.join(cac_ma)}")
            continue
        # đối chiếu với số cũ
        khop = tong = 0
        for m in ca_bang:
            moi = {(khoa(t), round(v, 6)) for _, t, _, v in kq[m[len(p):]]}
            moi_v = collections.Counter(round(v, 6) for _, _, _, v in kq[m[len(p):]])
            for r in by[m]:
                tong += 1
                if round(float(r["hao_phi"]), 6) in moi_v:
                    khop += 1
        ty_le = khop / tong if tong else 0
        if ty_le < 0.7:
            for m in cac_ma:
                khong_sua[m] = f"đọc lại khớp {ty_le:.0%} số cũ — cần đối chiếu tay"
            bao_cao.append(f"- {p}: GIỮ NGUYÊN (khớp {ty_le:.0%}) — {', '.join(cac_ma)}")
            continue
        for m in ca_bang:
            ghi = [f"'{t}' đơn vị nhân công không theo nhóm" for lo, t, d, v in kq[m[len(p):]] if lo == "NC" and not re.match(r"(Nhân công nhóm [1-4]|Kỹ sư|Thợ lặn|Nghệ nhân)$", t)]
            ghi += [f"'{t}' là máy nhưng văn bản ghi đơn vị '{d}'" for lo, t, d, v in kq[m[len(p):]] if lo == "M" and d not in ("ca", "%")]
            if any(r["ma_tn"] == "Máy khác" and r["don_vi_tn"] == "ca" for r in by[m]):
                ghi.append("'Máy khác' văn bản ghi đơn vị 'ca' — skill hiểu là % máy khác")
            if ghi:
                ghi_chu[m] = "; ".join(ghi)
            r0 = by[m][0]
            moi = []
            for lo, t, d, v in kq[m[len(p):]]:
                r = {c: r0.get(c, "") for c in cot}
                r.update(loai=lo, ma_tn=t if lo not in ("VLK", "MK") else "", ten_tn=t, don_vi_tn=d, hao_phi=f"{v:g}", he_so="1",
                         can_cu_he_so="")
                moi.append(r)
            da_sua[m] = moi
        bao_cao.append(f"- {p}: SỬA {len(ca_bang)} mã (khớp {ty_le:.0%} số cũ) — vd. {ca_bang[0]}: "
                       + "; ".join(f"{t} {v:g} {d}" for _, t, d, v in kq[hau[0]][:6]))
    print(f"Mã có dấu hiệu lỗi: {len(loi)} · bảng: {len(nhom)} · sửa: {len(da_sua)} mã · giữ nguyên cần kiểm tra: {len(khong_sua)} mã")
    print("\n".join(bao_cao))
    if not a.ghi:
        return
    out = []
    for m, rs in by.items():
        out.extend(da_sua.get(m, rs))
    # "Máy khác" / "Vật liệu khác" còn sót loại M/VL → MK/VLK (%) — trong TT 38 hai khoản này luôn tính theo %
    for r in out:
        if r["loai"] in ("M", "VL") and re.fullmatch(r"(Máy|Vật liệu) khác", r["ma_tn"].strip()):
            r["loai"] = "MK" if r["ma_tn"].startswith("Máy") else "VLK"
            ghi_chu.setdefault(r["ma_hieu"], f"'{r['ma_tn']}' văn bản ghi đơn vị '{r['don_vi_tn']}' — skill hiểu là %")
            r["ma_tn"], r["don_vi_tn"] = "", "%"
    # điền đơn vị trống cho NC/M
    for r in out:
        if not r["don_vi_tn"]:
            r["don_vi_tn"] = {"NC": "công", "M": "ca", "VLK": "%", "MK": "%"}.get(r["loai"], "")
    with gzip.open(p_dm, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot)
        w.writeheader()
        w.writerows(out)
    p_kt = os.path.join(a.data, "ma_can_kiem_tra.csv.gz")
    kt = list(csv.DictReader(gzip.open(p_kt, "rt", encoding="utf-8")))
    co = {r["ma_hieu"] for r in kt}
    for m, ly in sorted(ghi_chu.items()):
        if m not in co:
            kt.append({"ma_hieu": m, "ly_do": f"Đã đọc lại bảng gốc; lưu ý: {ly} — đối chiếu văn bản"})
            co.add(m)
    for m, ly in sorted(khong_sua.items()):
        if m not in co:
            kt.append({"ma_hieu": m, "ly_do": f"Bảng gốc trình bày theo khối, dữ liệu trích có thể sai loại/đơn vị/tên ({ly}) — đối chiếu văn bản"})
    with gzip.open(p_kt, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ma_hieu", "ly_do"])
        w.writeheader()
        w.writerows(kt)
    with open(os.path.join(a.data, "bao_cao_sua_bang_khoi.md"), "w", encoding="utf-8") as f:
        f.write("# Sửa mã TT 38 trích sai do bảng trình bày theo khối\n\n"
                f"Mã có dấu hiệu lỗi: {len(loi)}; đã sửa {len(da_sua)} mã; giữ nguyên và đưa vào `ma_can_kiem_tra`: {len(khong_sua)} mã.\n\n"
                + "\n".join(bao_cao) + "\n")
    print("Đã ghi.")


if __name__ == "__main__":
    main()
