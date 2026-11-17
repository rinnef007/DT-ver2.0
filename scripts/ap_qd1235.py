"""Áp QĐ 1235/QĐ-BTTTT (sửa đổi QĐ 1601) lên dữ liệu đã trích từ QĐ 1601."""
import csv, re, sys, unicodedata

from nhap_dinh_muc_chuyen_nganh import items
import docx
def k(s): return re.sub(r"\s+", "", unicodedata.normalize("NFC", s or "").lower().lstrip("-+ ").strip())
def sach(s): return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip().lstrip("-").strip()
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
cols = list(rows[0])
d = docx.Document(sys.argv[2]); L = list(items(d))
phan = ""; ma_p = ""; log = []
bo = []; doi = []   # (mã, tên cũ, tên mới)
for kk, x in L:
    if kk == 'p':
        t = x.text.strip()
        if t.startswith("I. "): phan = "I"
        elif t.startswith("II."): phan = "II"
        elif t.startswith("III"): phan = "III"
        m = re.match(r"^(\d{2}\.\d{2}\.\d{2}\.\d{2,3}(?:\.\d)?)", t)
        if m: ma_p = m.group(1)
        continue
    rr = [[c.text.strip() for c in r.cells] for r in x.rows]
    code = next((r[0] for r in rr if re.match(r"^\d{2}\.\d{2}", r[0] or "")), ma_p)
    if phan == "I":
        for r in rr[1:]:
            if r[1].strip().startswith("-"):
                bo.append((code, sach(r[1])))
    elif phan == "III":
        for r in rr[1:]:
            if len(r) >= 3 and r[1] != r[2] and r[1].strip().startswith("-"):
                doi.append((code, sach(r[1]), r[2]))
# I. bỏ
out = []
for r in rows:
    base = r["ma_hieu"].split("_")[0]
    if any(base == c and k(r["ten_tn"]) == k(n) for c, n in bo):
        log.append(f"I. Bỏ {r['ma_hieu']}: {r['ten_tn']} {r['hao_phi']} {r['don_vi_tn']}"); continue
    out.append(r)
# II. tên cột 01.02.11.00
ten_cot = {"1": "Connector", "2": "Cáp quang", "3": "Cáp đồng"}
for r in out:
    if r["ma_hieu"].startswith("01.02.11.00_"):
        n = r["ma_hieu"].split("_")[1]
        r["ten_cong_tac"] = re.sub(r"\s*\([^()]*\)$", "", r["ten_cong_tac"]) + f" ({ten_cot[n]})"
log.append("II. 01.02.11.00: tên cột → Connector / Cáp quang / Cáp đồng (số liệu không đổi)")
# III. đổi tên
kq = []
chua = []
for c, cu, moi in doi:
    hit = False
    for r in list(out):
        base = r["ma_hieu"].split("_")[0]
        if (base == c or base.startswith(c + ".") or (c.endswith(".00") and base.startswith(c[:-3]))) and k(r["ten_tn"]) == k(cu):
            hit = True
            parts = [sach(p) for p in moi.split("\n") if p.strip()]
            if len(parts) == 1:
                r["ten_tn"] = r["ma_tn"] = parts[0]
            else:  # tách thành nhiều vật liệu "…; số lượng: 01"
                i = out.index(r); out.remove(r)
                for j, p in enumerate(parts):
                    m = re.match(r"^(.*?);\s*số lượng\s*:\s*([\d,\.]+)", p)
                    ten, sl = (m.group(1).strip(), float(m.group(2).replace(",", "."))) if m else (p, float(r["hao_phi"]))
                    n = dict(r); n["ten_tn"] = n["ma_tn"] = ten; n["hao_phi"] = f"{sl:g}"; out.insert(i + j, n)
                log.append(f"III. {r['ma_hieu']}: '{cu}' tách thành {len(parts)} vật liệu")
    if not hit:
        import difflib
        pham = [r for r in out if (r["ma_hieu"].split("_")[0] == c or r["ma_hieu"].split("_")[0].startswith(c + ".") or (c.endswith(".00") and r["ma_hieu"].split("_")[0].startswith(c[:-3])))]
        moi1 = sach(moi.split("\n")[0])
        if any(k(r["ten_tn"]) == k(moi1) for r in pham):
            log.append(f"III. {c}: '{cu}' đã đổi (trùng cặp trước)"); continue
        ten = sorted({r["ten_tn"] for r in pham}, key=lambda t: -difflib.SequenceMatcher(None, k(t), k(cu)).ratio())
        thu_cong = {("01.02.06.00", "Máy khoan 1kw"): "Máy khoan điện cầm tay 1KW"}
        if (c, cu) in thu_cong:
            ten = [thu_cong[(c, cu)]]
        if ten and (difflib.SequenceMatcher(None, k(ten[0]), k(cu)).ratio() >= 0.7 or (c, cu) in thu_cong):
            for r in pham:
                if r["ten_tn"] == ten[0]:
                    r["ten_tn"] = r["ma_tn"] = moi1
            log.append(f"III. {c}: khớp gần đúng '{ten[0]}' (QĐ 1235 ghi '{cu}') → '{moi1}'")
        else:
            chua.append(f"III. KHÔNG KHỚP {c}: '{cu}' → '{moi}'")
# gộp tài nguyên trùng tên trong cùng mã (vd. 2 loại đĩa cài cùng đổi thành "Đĩa CD")
gop = {}; out2 = []
for r in out:
    key = (r["ma_hieu"], r["loai"], r["ten_tn"], r["don_vi_tn"])
    if key in gop:
        g = gop[key]; g["hao_phi"] = f"{float(g['hao_phi']) + float(r['hao_phi']):g}"
        log.append(f"Gộp {r['ma_hieu']}: {r['ten_tn']} → {g['hao_phi']} {r['don_vi_tn']}")
    else:
        gop[key] = r; out2.append(r)
out = out2
w = csv.DictWriter(open(sys.argv[3], "w", encoding="utf-8-sig", newline=""), fieldnames=cols); w.writeheader(); w.writerows(out)
print(f"{len(rows)} → {len(out)} dòng; đổi tên {len(doi)} cặp; không khớp {len(chua)}")
open(sys.argv[4], "w", encoding="utf-8").write("\n".join(log + chua))
print("\n".join(chua))
