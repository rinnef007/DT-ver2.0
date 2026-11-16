"""Bộ đọc bảng định mức TT 38 theo lưới ô Word (bảng một khối mã, dạng 'gói' hoặc ô gộp).

Khác bộ đọc chính (nhap_tt38_doc.py): giữ dòng trống trong ô làm vị trí giữ chỗ (dòng tiêu đề 'Máy thi công',
ô không có hao phí), căn từng dòng tên với một vị trí đơn vị/số liệu và kiểm tra tiêu đề rơi vào ô đơn vị trống.
Chỉ nhận bảng có một khối mã (một tiền tố) và dòng hậu tố tăng dần; không chắc thì trả lý do, không đoán.
Dùng bởi scripts/bo_sung_tt38_luoi.py."""
import re, unicodedata
RE_MA = re.compile(r"^[A-Z]{2}\.\d{2,5}$")
TIEU_DE = {"vật liệu", "vật tư", "nhân công", "máy thi công", "máy", "máy và thiết bị thi công", "vật liệu chính", "thiết bị"}
RE_TACH = re.compile(r"\s+(?=(?:Máy thi công|Nhân công nhóm|Vật liệu khác|Máy khác)\b)")
def n(s): return unicodedata.normalize("NFC", (s or "")).replace("³", "3").replace("²", "2").replace(" ", " ")
def tieu_de(x): return x.lower().rstrip(":").strip() in TIEU_DE
def dong(cell, giu_trong=True):
    ls = [re.sub(r"\s+", " ", l).strip() for l in n(cell).split("\n")]
    while ls and not ls[-1]: ls.pop()
    while ls and not ls[0]: ls.pop(0)
    out = []
    for l in ls:
        if not l:
            if giu_trong: out.append("")
            continue
        out.extend(p.strip() for p in RE_TACH.split(l) if p.strip())
    return out
def noi(lines):
    out = []
    for l in lines:
        if out and l and out[-1] and not tieu_de(l) and (l[:1].islower() or l[:1] in "(,;/÷×") and not re.fullmatch(r"(m3|m2|m|kg|cái|ca|công|%|tấn|lít)", l):
            out[-1] += " " + l
        else:
            out.append(l)
    return out
def so(s):
    s = s.strip().replace(" ", "")
    if s in ("-", "–", "—", "x", ""): return "-"
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", s): s = s.replace(".", "")
    s = s.replace(",", ".")
    try: return float(s)
    except ValueError: return None

def doc(rows):
    rows = [[n(c) for c in r] for r in rows if r]
    if not rows: return None, None, "rỗng"
    hdr = [re.sub(r"\s+", " ", c).strip().lower() for c in rows[0]]
    try:
        c_tp = next(i for i, c in enumerate(hdr) if "thành phần" in c)
        c_dv = next(i for i, c in enumerate(hdr) if c.startswith("đơn vị"))
    except StopIteration:
        return None, None, "không thấy cột thành phần/đơn vị"
    i0 = next((i for i, r in enumerate(rows) if RE_MA.match(re.sub(r"\s", "", r[0] or ""))), None)
    if i0 is None: return None, None, "không thấy mã"
    prefix = re.sub(r"\s", "", rows[i0][0])
    cac_ma = {re.sub(r"\s", "", r[0]) for r in rows[i0:] if RE_MA.match(re.sub(r"\s", "", r[0] or ""))}
    if len(cac_ma) > 1:
        return prefix, None, f"bảng nhiều khối mã ({', '.join(sorted(cac_ma)[:4])}) — dùng bộ đọc cũ"
    last = rows[-1]
    hau = [re.sub(r"\s", "", c) for c in last[c_dv + 1:]]
    hh = [h for h in hau if h]
    if not hh or not all(re.fullmatch(r"\d{1,3}", h) for h in hh) or (last[c_tp] or "").strip() \
            or any(int(a) >= int(b) for a, b in zip(hh, hh[1:])):
        return prefix, None, "không thấy dòng hậu tố"
    cols = [j for j, h in zip(range(c_dv + 1, len(last)), hau) if h]
    data = rows[i0:-1]
    uniq = []
    for r in data:
        if not uniq or r[1:] != uniq[-1][1:]: uniq.append(r)
    gop_tp = len(uniq) > 1 and len({r[c_tp] for r in uniq}) == 1
    names, slots = [], []   # slot = (dv, {j: v})
    prev = None
    for r in uniq:
        if not gop_tp and r[c_tp] != prev:
            names += noi(dong(r[c_tp])); prev = r[c_tp]
        ru = dong(r[c_dv] if c_dv < len(r) else "")
        rv = {j: dong(r[j] if j < len(r) else "") for j in cols}
        k = max([len(ru)] + [len(v) for v in rv.values()])
        if k == 0:
            slots.append(("", {j: "" for j in cols})); continue
        # ô nhiều đơn vị trên một dòng chữ ('kg kg') → tách
        if len(ru) == 1 and k > 1 and len(ru[0].split()) == k: ru = ru[0].split()
        for j in cols:
            if len(rv[j]) == 1 and k > 1 and len(rv[j][0].split()) == k: rv[j] = rv[j][0].split()
        if len(ru) == 1 and k == 1 and len(ru[0].split()) > 1 and all(len(rv[j]) == 1 and len(rv[j][0].split()) == len(ru[0].split()) for j in cols):
            ru = ru[0].split(); rv = {j: rv[j][0].split() for j in cols}; k = len(ru)
        ru += [""] * (k - len(ru))
        for j in cols: rv[j] += [""] * (k - len(rv[j]))
        for t in range(k): slots.append((ru[t], {j: rv[j][t] for j in cols}))
    if gop_tp: names = noi(dong(uniq[0][c_tp]))
    # căn tên ↔ vị trí: thử bỏ tiêu đề đầu, bỏ tiêu đề + vị trí trống
    def hop(nm, sl):
        if len(nm) != len(sl): return False
        for x, (dv, v) in zip(nm, sl):
            if tieu_de(x) and (dv or any(v.values())): return False
            if not x and (dv or any(v.values())): return False
            if x and not tieu_de(x) and not dv: return False
        return True
    cach = [(names, slots)]
    nm2 = list(names)
    while nm2 and tieu_de(nm2[0]) and len(nm2) > len(slots): nm2 = nm2[1:]
    cach.append((nm2, slots))
    cach.append(([x for x in names if x and not tieu_de(x)], [s for s in slots if s[0]]))
    chon = next(((nm, sl) for nm, sl in cach if hop(nm, sl)), None)
    if not chon:
        return prefix, None, f"lệch: {len([x for x in names if x and not tieu_de(x)])} tên, {len([s for s in slots if s[0]])} đơn vị, {len(names)}/{len(slots)} dòng"
    nm, sl = chon
    out = {h: [] for h in hh}
    nhom = "VL"
    for x, (dv, v) in zip(nm, sl):
        xl = x.lower().rstrip(":")
        if not x: continue
        if tieu_de(x):
            nhom = "NC" if xl == "nhân công" else ("M" if xl.startswith("máy") else "VL"); continue
        lo = nhom
        if re.match(r"(Nhân công nhóm|Kỹ sư|Thợ lặn|Nghệ nhân|Công nhân)", x) or (dv == "công" and nhom != "M"): lo = "NC"; nhom = "NC"
        elif dv in ("ca", "giờ") and not re.match(r"(Nhân công|Kỹ sư|Thợ lặn|Nghệ nhân|Công nhân)", x): lo = "M"; nhom = "M"
        if dv == "%": lo = "MK" if (nhom == "M" or xl.startswith("máy")) else "VLK"
        for j, h in zip(cols, hh):
            val = so(v[j])
            if val is None: return prefix, None, f"giá trị không phải số '{v[j]}' ({x})"
            if val == "-": continue
            out[h].append((lo, x, dv, val))
    return prefix, out, ""
