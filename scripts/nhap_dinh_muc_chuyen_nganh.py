"""Trích định mức chuyên ngành (CNTT QĐ 1601/1595, viễn thông CV 258) từ .docx sang CSV cùng cấu trúc dữ liệu TT 38."""
import argparse, csv, re, sys, unicodedata
import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

COT = ["ma_hieu", "ten_cong_tac", "don_vi", "loai", "ma_tn", "ten_tn", "don_vi_tn", "hao_phi", "he_so", "can_cu_he_so", "nguon", "phu_luc", "chuong"]

BO = {
    "cntt_1601": dict(re_ma=r"\d{2}\.\d{2}\.\d{2}\.\d{2,3}(?:\.\d)?", hau_to="_", nguon="QĐ 1601/QĐ-BTTTT (sđ QĐ 1235/QĐ-BTTTT) – Lắp đặt phần cứng, cài đặt phần mềm CNTT"),
    "cntt_1595": dict(re_ma=r"\d{2}\.?\d{2}\.?\d{2}\.?\d{2}\.?\d{2}", hau_to="_", nguon="QĐ 1595/QĐ-BTTTT – Tạo lập cơ sở dữ liệu CNTT"),
    "vt_258": dict(re_ma=r"\d{2}\.\d{6}\.\d{2}", hau_to="slot", nguon="CV 258/BTTTT-KHTC – Định mức XDCB công trình bưu chính, viễn thông"),
}


def items(d):
    for el in d.element.body.iterchildren():
        tag = el.tag.split('}')[1]
        if tag == 'p':
            yield 'p', Paragraph(el, d)
        elif tag == 'tbl':
            yield 't', Table(el, d)


def sach(s):
    s = unicodedata.normalize("NFC", s or "").replace("\xa0", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", s).strip()


def so(s):
    s = sach(s).replace(" ", "")
    if not s or s in ("-", "–"):
        return None
    s = s.rstrip("%")
    if re.fullmatch(r"\d+(?:[.,]\d+)?", s):
        return float(s.replace(",", "."))
    return "X"  # có chữ, không phải số


def raw(r):
    return [sach(c.text) for c in r.cells]


def dong_hau_to(v):
    """Dòng số cột 1..n ở cuối bảng: trả về danh sách số (chuỗi) theo vị trí, hoặc None."""
    khac = [x for x in v if x]
    if not khac:
        return None
    if all(re.fullmatch(r"\d{1,2}", x) for x in khac):
        # loại bỏ trùng do ô gộp
        out = []
        for x in v:
            out.append(x)
        nums = [int(x) for x in khac]
        uniq = []
        for n in nums:
            if not uniq or uniq[-1] != n:
                uniq.append(n)
        if uniq == list(range(1, len(uniq) + 1)):
            return out
    return None


def loai_nhom(ten):
    t = ten.lower()
    if "vật liệu" in t or "vật tư" in t:
        return "VL"
    if "nhân công" in t or "công nhân" in t or "lao động" in t:
        return "NC"
    if "máy" in t:
        return "M"
    return None


def trich(path, bo, phu_luc=""):
    cfg = BO[bo]
    re_ma = re.compile(r"^(" + cfg["re_ma"] + r")\.?\s*(.*)$")
    d = docx.Document(path)
    out, bao_cao = [], []
    tieu_de = {}           # mã → tên trong đoạn văn
    ghi_chu = []           # (mã, nội dung)
    bang_cuoi = [False]; dang_gc = [False]; ma_bang = [""]
    truoc = ""; ten_ung = ""; co_tp = False   # tiêu đề không mã (vd. "Lắp đặt tủ quang từ")
    ma_dv = ""             # mã gần nhất trong đoạn văn
    don_vi = ""
    nc_ngam = ""           # "Công nhân: 3,0/7" trong đoạn văn
    chuong = ""
    for k, x in items(d):
        if k == 'p':
            t = sach(x.text)
            if not t:
                continue
            if re.match(r"^Ghi chú", t, re.I) and bang_cuoi[0]:
                dang_gc[0] = True
                ghi_chu.append((ma_bang[0], t)); continue
            m = re_ma.match(t)
            if m:
                dang_gc[0] = False; bang_cuoi[0] = False
                ten_ung = ""; co_tp = False
                ma_dv = m.group(1)
                tieu_de[ma_dv] = sach(m.group(2))
                nc_ngam = ""
                continue
            if dang_gc[0]:
                ghi_chu.append((ma_bang[0], t)); continue
            if re.match(r"^\+?\s*Thành phần công việc", t, re.I) or re.match(r"^Đơn vị tính", t, re.I):
                if truoc and not truoc.startswith(("-", "+", "Đơn vị", "Ghi chú")) and not re_ma.match(truoc) and not co_tp:
                    ten_ung = truoc
                if re.match(r"^\+?\s*Thành phần", t, re.I):
                    co_tp = True
            truoc = t
            m = re.match(r"^Đơn vị tính\s*:\s*(.+)$", t, re.I)
            if m:
                don_vi = m.group(1).strip(); continue
            m = re.match(r"^\+?\s*(Nhân công|Công nhân|Thợ)\s*(?:bậc)?\s*:?\s*([\d,\.]+\s*/\s*\d)\s*$", t, re.I)
            if m:
                nc_ngam = "Công nhân " + m.group(2).replace(" ", ""); continue
            m = re.match(r"^Chương\s*(\d+)", t, re.I)
            if m:
                chuong = m.group(1)
            m = re.match(r"^Phần\s+([IVX]+)\b", t)
            if m:
                chuong = m.group(1)
            continue
        rows = [raw(r) for r in x.rows]
        if not rows:
            continue
        if len(rows) == 1 and len(x.rows[0].cells) == 1 and "\t" in x.rows[0].cells[0].text:
            rows = [[sach(c) for c in ln.split("\t")] for ln in x.rows[0].cells[0].text.split("\n") if ln.strip()]
            bao_cao.append(f"Bảng 1 ô (tách theo tab): {rows[1][0] if len(rows) > 1 else ''}")
        bang_cuoi[0] = True
        ten_ung_bang = ten_ung
        # đơn vị trong dòng đầu bảng
        for r in rows[:2]:
            for c in r:
                m = re.search(r"Đơn vị tính\s*:\s*(.+)$", c, re.I)
                if m:
                    don_vi = m.group(1).strip()
        # dòng hậu tố
        hau = None
        for i in range(len(rows) - 1, -1, -1):
            if any(rows[i]):
                hau = dong_hau_to(rows[i]); break
        # vị trí cột giá trị
        if hau:
            vt = [j for j, c in enumerate(hau) if c]
            # bỏ cột trùng do ô gộp
            vt2, seen = [], set()
            for j in vt:
                if hau[j] not in seen:
                    vt2.append(j); seen.add(hau[j])
            vt = vt2
            nhan = [int(hau[j]) for j in vt]
        else:
            vt, nhan = [], []
        # tìm dòng đầu dữ liệu
        dau = None
        for i, r in enumerate(rows):
            if any(re_ma.match(c) and not c.startswith("Mã") for c in r[:1]) or any(c.startswith(("+", "-", "–")) for c in r):
                dau = i; break
        if dau is None:
            bao_cao.append(f"Bảng hệ số/ghi chú (không phải bảng hao phí): {' | '.join(rows[0])[:120]}")
            txt = " ; ".join(" | ".join(dict.fromkeys(c for c in r if c)) for r in rows)
            ghi_chu.append((ma_bang[0] or ma_dv, "Bảng: " + txt[:1500]))
            continue
        if not vt:
            # đoán: các cột cuối có số ở dòng dữ liệu
            w = max(len(r) for r in rows)
            vt = [j for j in range(w) if any(j < len(r) and isinstance(so(r[j]), float) for r in rows[dau:])]
            vt = [j for j in vt if j >= 2]
            nhan = list(range(1, len(vt) + 1))
            if not vt:
                bao_cao.append(f"Bỏ bảng (không thấy cột số): {' | '.join(rows[0])[:120]}"); continue
        # cột hậu tố lệch (vd. hậu tố "1 | 2" nhưng chỉ có 1 cột số)
        co_so = [j for j in vt if any(j < len(r) and isinstance(so(r[j]), float) for r in rows[dau:-1 if hau else None])]
        if hau and co_so != vt:
            w = max(len(r) for r in rows)
            vt2 = [j for j in range(2, w) if any(j < len(r) and isinstance(so(r[j]), float) for r in rows[dau:-1])]
            vt2 = [j for j in vt2 if not all((r[j] if j < len(r) else "") in ("", ) or re.fullmatch(r"[a-zA-Zà-ỹÀ-Ỹ%/ 0-9]*", r[j] or "") and not isinstance(so(r[j]), float) for r in rows[dau:-1])]
            bao_cao.append(f"Dòng số hiệu cột lệch, dùng cột có số: {rows[dau][0]} {vt}->{vt2}")
            vt = vt2; nhan = list(range(1, len(vt) + 1))
            if len(vt) == 1:
                hau = None
        # tiêu đề cột
        tdc = {}
        for r in rows[:dau]:
            for j in vt:
                if j < len(r) and r[j] and not re.match(r"Đơn vị tính", r[j], re.I):
                    tdc.setdefault(j, [])
                    if r[j] not in tdc[j]:
                        tdc[j].append(r[j])
        ma_bang[0] = next((re_ma.match(c).group(1) for r in rows[dau:] for c in r[:1] if re_ma.match(c or "")), ma_dv)
        dang_gc[0] = False
        cot_dau_gt = min(vt)
        CAT = re.compile(r"^[+]?\s*(vật liệu( phụ| chính)?|vật tư|nhân công|lao động|máy thi công|máy|thiết bị thi công)\s*:?$", re.I)
        co_nhom = any(c.startswith("+") or CAT.match(c) for r in rows[dau:] for c in r[:cot_dau_gt] if c)
        ma_ht = None
        ten_phu = ""
        nhom = None
        for r in rows[dau:]:
            if hau is not None and r is rows[-1] and dong_hau_to(r):
                break
            if not any(r):
                continue
            tr0 = r[:cot_dau_gt]
            # mã
            if tr0 and re_ma.match(tr0[0] or ""):
                ma_moi = re_ma.match(tr0[0]).group(1)
                if ma_moi != ma_ht:
                    ma_ht = ma_moi; nhom = None
            if ma_ht is None:
                ma_ht = ma_dv
            # bỏ trùng ô gộp liền nhau trong phần trước
            tr = []
            for c in tr0:
                if not tr or tr[-1] != c:
                    tr.append(c)
            # phần tên/đv: phần tử cuối là đơn vị (trừ khi là tên hao phí)
            ten_hp = next((c for c in tr if c.startswith(("+", "-", "–"))), "")
            goc = ten_hp
            if not ten_hp and co_nhom:
                cand = [c for c in tr if c and not re_ma.match(c)]
                if cand:
                    if CAT.match(cand[0]):
                        goc = cand[0]; ten_hp = "+ " + cand[0]
                    elif len(cand) >= 2:
                        goc = cand[-2]; ten_hp = "- " + cand[-2]
                    else:
                        goc = cand[0]; ten_hp = "- " + cand[0]
            if ten_hp:
                idx = tr.index(goc)
                dv_tn = tr[idx + 1] if idx + 1 < len(tr) else ""
                giua = [c for c in tr[:idx] if c and not re_ma.match(c)]
                if giua:
                    ten_phu = giua[-1]
                if ten_hp.startswith("+"):
                    nhom = loai_nhom(ten_hp) or nhom
                    # "+ Nhân công: 3,5/7" kiểu dòng nhóm có số → coi như dòng hao phí
                    if not any(isinstance(so(r[j]), float) for j in vt if j < len(r)):
                        continue
                ten = re.sub(r"^[+\-–]\s*", "", ten_hp).strip(" :").rstrip("*").strip()
                dvl = dv_tn.lower()
                lo = nhom or loai_nhom(ten) or ("NC" if dvl.startswith("công") else "M" if dvl.startswith("ca") else "VL")
                if re.match(r"(công nhân|kỹ sư|thợ|lao động)", ten, re.I):
                    lo = "NC"
            else:
                # bảng kiểu "mỗi dòng một mã/vật liệu, giá trị = công": nhân công ngầm
                giua = [c for c in tr if c and not re_ma.match(c)]
                if not giua:
                    continue
                if not nc_ngam:
                    bao_cao.append(f"{ma_ht}: dòng không rõ tài nguyên: {' | '.join(r)[:120]}"); continue
                ten_phu = giua[0] if len(giua) >= 1 else ""
                ten, lo, dv_tn = nc_ngam, "NC", "công"
                if len(giua) >= 2 and not don_vi:
                    pass
            if lo is None:
                bao_cao.append(f"{ma_ht}: không xác định loại cho '{ten}'"); continue
            ten = re.sub(r"^(Nhân công|Vật liệu|Máy thi công)\s*[-–]\s*", "", ten)
            dv_tn = {"coõng": "công", "coâng": "công", "cong": "công"}.get(dv_tn.lower(), dv_tn.lower() if dv_tn.lower() in ("công", "ca") else dv_tn)
            if not dv_tn and lo == "NC":
                dv_tn = "công"; bao_cao.append(f"DV_TRONG|{ma_ht}|{ten}|công")
            elif not dv_tn and lo == "M":
                dv_tn = "ca"; bao_cao.append(f"DV_TRONG|{ma_ht}|{ten}|ca")
            ten_tn, ma_tn = ten, ten
            if re.match(r"vật liệu khác", ten, re.I) or (lo == "VL" and dv_tn == "%"):
                lo, ma_tn, ten_tn = "VLK", "", "Vật liệu khác"
            elif re.match(r"máy khác", ten, re.I) or (lo == "M" and dv_tn == "%"):
                lo, ma_tn, ten_tn = "MK", "", "Máy khác"
            for j, n in zip(vt, nhan):
                if j >= len(r):
                    continue
                v = so(r[j])
                if v is None:
                    continue
                if v == "X":
                    bao_cao.append(f"CONG_THUC|{ma_ht}|{n}|{ten}|{r[j]}"); continue
                if len(vt) > 1 or hau:
                    if cfg["hau_to"] == "slot" and ma_ht.endswith(".00"):
                        ma = ma_ht[:-2] + f"{n:02d}"
                    elif len(vt) > 1:
                        ma = f"{ma_ht}_{n}"
                    else:
                        ma = ma_ht
                else:
                    ma = ma_ht
                ten_ct = tieu_de.get(ma_ht) or ten_ung or tieu_de.get(ma_dv, "")
                if ten_phu and ten_phu not in ten_ct:
                    ten_ct = f"{ten_ct} – {ten_phu}" if ten_ct else ten_phu
                if len(vt) > 1 and tdc.get(j):
                    ten_ct += " (" + " – ".join(tdc[j]) + ")"
                out.append(dict(ma_hieu=ma, ten_cong_tac=ten_ct, don_vi=don_vi, loai=lo, ma_tn=ma_tn, ten_tn=ten_tn,
                                don_vi_tn=dv_tn, hao_phi=f"{v:g}", he_so="1", can_cu_he_so="", nguon=cfg["nguon"],
                                phu_luc=phu_luc, chuong=chuong))
    return out, bao_cao, ghi_chu


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True); ap.add_argument("--bo", required=True, choices=list(BO))
    ap.add_argument("--ra", required=True); ap.add_argument("--bao-cao", default="")
    a = ap.parse_args()
    out, bc, gc = trich(a.file, a.bo)
    with open(a.ra, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT); w.writeheader(); w.writerows(out)
    ma = {r["ma_hieu"] for r in out}
    print(f"{a.bo}: {len(out)} dòng hao phí, {len(ma)} mã; {len(bc)} ghi chú")
    with open(a.ra.replace(".csv", "_ghi_chu.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["ma_hieu", "ghi_chu"]); w.writerows(gc)
    print(f"  {len(gc)} dòng ghi chú áp dụng")
    if a.bao_cao:
        open(a.bao_cao, "w", encoding="utf-8").write("\n".join(bc))


def trich_1595(path):
    """QĐ 1595: ô nhiều dòng (Lao động/Vật liệu/Thiết bị), giá trị 'a / b' tương ứng từng dòng."""
    cfg = BO["cntt_1595"]
    re_ma = re.compile(r"^(\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2}(?:\.\d{2})?)\s*(.*)$")
    d = docx.Document(path)
    out, bc, gc = [], [], []
    tieu_de, don_vi, ma_dv, chuong = {}, "", "", ""
    da_dung = set(); sau_bang = [False]
    nhan_muc = re.compile(r"^(lao động|vật liệu|thiết bị)( chính)?\s*:?$", re.I)
    for k, x in items(d):
        if k == 'p':
            t = sach(x.text)
            m = re_ma.match(t)
            if m:
                sau_bang[0] = False
                ma_dv = m.group(1); tieu_de[ma_dv] = sach(m.group(2)).capitalize(); continue
            if re.match(r"^(\+\s*Thành phần|Chương|\+\s*Bảng định mức)", t, re.I):
                sau_bang[0] = False
            elif sau_bang[0] and t:
                gc.append((ma_dv, t))
            m = re.match(r"^Đơn vị tính\s*:\s*(.+)$", t, re.I)
            if m:
                don_vi = m.group(1).strip(); continue
            m = re.match(r"^Chương\s*(\d+)", t, re.I)
            if m:
                chuong = m.group(1)
            continue
        rows = [[c.text for c in r.cells] for r in x.rows]
        if not rows or "THÀNH PHẦN HAO PHÍ" not in sach(rows[0][1] if len(rows[0]) > 1 else "").upper():
            continue
        hdr = [sach(c) for c in rows[1]] if len(rows) > 1 and not re_ma.match(sach(rows[1][0])) else [sach(c) for c in rows[0]]
        vt = list(range(3, len(rows[0])))
        # bỏ cột trùng do gộp
        dau = next((i for i, r in enumerate(rows) if re_ma.match(sach(r[0]))), None)
        if dau is None:
            bc.append(f'Bỏ bảng không mã: {sach(rows[0][0])}'); continue
        ten_cot = {j: hdr[j] for j in vt if j < len(hdr)}
        vt = [j for j in vt if not (j > 3 and j < len(hdr) and hdr[j] == hdr[j - 1] and all(r[j] == r[j - 1] for r in rows[dau:]))]
        ma = ma_dv; nhom = None; sau_bang[0] = True
        for r in rows[dau:]:
            if re_ma.match(sach(r[0])):
                ma = re_ma.match(sach(r[0])).group(1)
                if ma != ma_dv and (ma in da_dung or ma_dv.count(".") > ma.count(".")):
                    bc.append(f"MA_BANG_SAI|bảng ghi {ma}, đoạn văn ghi {ma_dv} → dùng {ma_dv}")
                    ma = ma_dv
                da_dung.add(ma)
            ten_l = [sach(s) for s in r[1].split("\n") if sach(s)]
            dv_l = [sach(s) for s in r[2].split("\n") if sach(s)]
            gt_l = {j: [sach(s) for s in r[j].split("\n") if sach(s)] for j in vt if j < len(r)}
            ten_tn_l = []
            for t in ten_l:
                if nhan_muc.match(t):
                    nhom = {"lao động": "NC", "vật liệu": "VL", "thiết bị": "M"}[nhan_muc.match(t).group(1).lower()]
                else:
                    ten_tn_l.append(t)
            for i, t in enumerate(ten_tn_l):
                t2 = t.rstrip(":").strip()
                dv = dv_l[i] if i < len(dv_l) else ""
                lo = nhom or "VL"
                ma_tn, ten_tn = t2, t2
                if re.match(r"vật liệu khác", t2, re.I):
                    lo, ma_tn, ten_tn = "VLK", "", "Vật liệu khác"
                elif re.match(r"thiết bị khác|máy khác", t2, re.I):
                    lo, ma_tn, ten_tn = "MK", "", "Máy khác"
                for n, j in enumerate(vt, start=1):
                    vals = gt_l.get(j, [])
                    if i >= len(vals):
                        continue
                    v = so(vals[i])
                    if v is None:
                        continue
                    if v == "X":
                        bc.append(f"CONG_THUC|{ma}|{n}|{t2}|{vals[i]}"); continue
                    mh = f"{ma}_{n}" if len(vt) > 1 else ma
                    ten_ct = tieu_de.get(ma, "") + (f" ({ten_cot.get(j)})" if len(vt) > 1 and ten_cot.get(j) else "")
                    out.append(dict(ma_hieu=mh, ten_cong_tac=ten_ct, don_vi=don_vi, loai=lo, ma_tn=ma_tn, ten_tn=ten_tn,
                                    don_vi_tn=dv.lower(), hao_phi=f"{v:g}", he_so="1", can_cu_he_so="", nguon=cfg["nguon"],
                                    phu_luc="", chuong=chuong))
                    if lo == "NC" and "nhóm" in dv.lower():
                        bc.append(f"NHOM_CONG|{mh}|{t2}|{dv}")
    return out, bc, gc
