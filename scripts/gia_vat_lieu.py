"""Tra giá vật liệu theo công bố giá (CBG) của Sở Xây dựng Hà Nội, Hải Phòng, Hưng Yên.

Nguồn dữ liệu: các tệp GVT_<kỳ>_<năm>_<TỈNH>.csv (UTF-16 hoặc UTF-8, phân tách bằng tab; cột: tên vật tư, đơn vị tính,
giá vật liệu, nguồn, ghi chú, khu vực) trong <thư mục>/<HaNoi|HaiPhong|HungYen>/GVT/. Đây là định dạng thư viện giá của
phần mềm Dự toán GXD (D:\\GXD\\Dulieu) — skill chỉ ĐỌC trên máy người dùng, không chép dữ liệu này vào repo. Có thể tự
lập tệp cùng định dạng từ bản CBG gốc.

  python scripts/gia_vat_lieu.py ds    [--thu-muc D:\\GXD\\Dulieu]
  python scripts/gia_vat_lieu.py tra   --tinh HN --tu-khoa "cát vàng" [--ky Q3/2026] [--khu-vuc "Sơn Tây"] [--top 20]
  python scripts/gia_vat_lieu.py goi-y --tinh HN --data <thư mục hồ sơ> [--ky T8/2026] [--ra goi_y_gia_vat_lieu.csv]

goi-y: với mỗi vật liệu (VL) trong hồ sơ, đề xuất tối đa 3 dòng CBG giống nhất — KHÔNG tự điền gia_tai_nguyen.csv;
người lập chọn, ghi giá và nguồn (số CBG, trang, địa điểm giao) rồi mới dùng.
"""
import argparse
import csv
import glob
import os
import re
import sys
import unicodedata

TINH = {"HN": ("HaNoi", "Hà Nội"), "HP": ("HaiPhong", "Hải Phòng"), "HY": ("HungYen", "Hưng Yên")}
LA_MA = {"I": 1, "II": 2, "III": 3, "IV": 4}
MAC_DINH = os.environ.get("DT_GVT_DIR") or (r"D:\GXD\Dulieu" if os.name == "nt" else "")


def nfc(s):
    return unicodedata.normalize("NFC", (s or "").replace("\xa0", " ")).strip()


def khong_dau(s):
    s = unicodedata.normalize("NFD", nfc(s).lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def tu(s, bo_dau=False):
    s = khong_dau(s) if bo_dau else nfc(s).lower()
    return [t for t in re.split(r"[^\w.,/]+", s) if t]


def ky_cua_tep(path):
    """GVT_Q3_2026_HANOI.csv → (2026, 9, 'Q3/2026'); T8 → tháng 8; QII → quý 2; 'T9+Q3' → tháng 9."""
    m = re.match(r"GVT_(.+?)_(\d{4})_", os.path.basename(path), re.I)
    if not m:
        return None
    k, nam = m.group(1).upper(), int(m.group(2))
    t = re.search(r"T(\d{1,2})", k)
    if t:
        return nam, int(t.group(1)), f"{k}/{nam}"
    q = re.search(r"Q(\d|IV|III|II|I)\b", k)
    if q:
        n = int(q.group(1)) if q.group(1).isdigit() else LA_MA[q.group(1)]
        return nam, n * 3, f"{k}/{nam}"
    return nam, 12, f"{k}/{nam}"


def danh_sach(thu_muc, tinh):
    out = []
    for p in glob.glob(os.path.join(thu_muc, TINH[tinh][0], "GVT", "GVT_*.csv")):
        k = ky_cua_tep(p)
        if k:
            out.append((k, p))
    return sorted(out)


def doc_tep(path):
    raw = open(path, "rb").read()
    enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8-sig"
    rows = list(csv.reader(raw.decode(enc).splitlines(), delimiter="\t"))
    out = []
    for r in rows[1:]:
        if len(r) < 3 or not r[0].strip():
            continue
        try:
            gia = float(r[2].replace(",", "").strip())
        except ValueError:
            continue
        out.append(dict(ten=nfc(r[0]), dvt=nfc(r[1]), gia=gia, nguon=nfc(r[3]).strip('"; ') if len(r) > 3 else "",
                        ghi_chu=nfc(r[4]) if len(r) > 4 else "", khu_vuc=nfc(r[5]) if len(r) > 5 else ""))
    return out


def chon_tep(thu_muc, tinh, ky):
    ds = danh_sach(thu_muc, tinh)
    if not ds:
        sys.exit(f"Không thấy tệp GVT_*.csv trong {os.path.join(thu_muc, TINH[tinh][0], 'GVT')}")
    if ky:
        hop = [x for x in ds if x[0][2].replace(" ", "").upper() == ky.replace(" ", "").upper()]
        if not hop:
            sys.exit(f"Không có kỳ {ky}. Có: {', '.join(x[0][2] for x in ds)}")
        return hop[-1]
    return ds[-1]


def diem(ten_tim, dvt_tim, r):
    a, b = set(tu(ten_tim)), set(tu(r["ten"]))
    if not a or not b:
        return 0.0
    d = len(a & b) / len(a | b)
    if d == 0:   # không so khớp bỏ dấu khi đề xuất: "cắt" khác "cát", "cáp" khác "cấp"
        return 0.0
    if dvt_tim and khong_dau(dvt_tim).replace(" ", "") == khong_dau(r["dvt"]).replace(" ", ""):
        d += 0.15
    return d


def cmd_ds(a):
    for t in TINH:
        ds = danh_sach(a.thu_muc, t)
        print(f"{TINH[t][1]}: {len(ds)} kỳ — " + ", ".join(x[0][2] for x in ds))


def cmd_tra(a):
    (nam, thang, ky), p = chon_tep(a.thu_muc, a.tinh, a.ky)
    rows = doc_tep(p)
    q = nfc(a.tu_khoa).lower()
    hit = [r for r in rows if q in r["ten"].lower()]
    loai = "khớp đúng chuỗi"
    if not hit:
        qk = khong_dau(q)
        hit = [r for r in rows if qk in khong_dau(r["ten"])]
        loai = "khớp KHÔNG DẤU — kiểm tra kỹ (vd. 'cap' khớp cả 'cáp' và 'cấp')"
    if a.khu_vuc:
        k = khong_dau(a.khu_vuc)
        hit = [r for r in hit if k in khong_dau(r["ghi_chu"] + " " + r["khu_vuc"])]
    print(f"{TINH[a.tinh][1]} kỳ {ky} ({os.path.basename(p)}): {len(hit)} dòng, {loai}")
    for r in hit[: a.top]:
        print(f"  {r['gia']:>14,.0f} đ/{r['dvt']:<8} {r['ten'][:70]}")
        print(f"      {r['nguon'][:110]} | {(r['ghi_chu'] + ' ' + r['khu_vuc']).strip()[:110]}")
    if len(hit) > a.top:
        print(f"  … còn {len(hit) - a.top} dòng (--top)")


def cmd_goi_y(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dutoan_core import DuLieu, doc_csv
    (nam, thang, ky), p = chon_tep(a.thu_muc, a.tinh, a.ky)
    rows = doc_tep(p)
    dl = DuLieu(a.data)
    kl = doc_csv(os.path.join(a.data, "khoi_luong.csv")) or []
    vl = {}
    for r in kl:
        d = dl.dinh_muc.get(r["ma_hieu"].strip())
        for h in (d or {}).get("hao_phi", []):
            if h["loai"] == "VL":
                vl[h["ma_tn"]] = h["don_vi_tn"]
    out = []
    for ten, dv in sorted(vl.items()):
        top = sorted(rows, key=lambda r: -diem(ten, dv, r))[:3]
        for i, r in enumerate(top, 1):
            s = diem(ten, dv, r)
            if s <= 0:
                continue
            out.append(dict(ten_tn=ten, don_vi=dv, hang=i, do_khop=f"{s:.2f}", ten_cbg=r["ten"], dvt_cbg=r["dvt"], gia=f"{r['gia']:.0f}",
                            nguon=r["nguon"], dia_diem=(r["ghi_chu"] + " " + r["khu_vuc"]).strip(), ky=ky,
                            luu_y="đơn vị khác — quy đổi" if khong_dau(r["dvt"]).replace(" ", "") != khong_dau(dv).replace(" ", "") else ""))
    ra = a.ra or os.path.join(a.data, "goi_y_gia_vat_lieu.csv")
    with open(ra, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]) if out else ["ten_tn"]); w.writeheader(); w.writerows(out)
    print(f"{len(vl)} vật liệu, {len(out)} đề xuất từ CBG {TINH[a.tinh][1]} kỳ {ky} → {ra}")
    print("Chưa điền gia_tai_nguyen.csv — chọn dòng phù hợp, ghi giá, nguồn (số CBG, trang), địa điểm giao, cước vận chuyển nếu có.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thu-muc", default=MAC_DINH, help="thư mục chứa HaNoi/HaiPhong/HungYen (mặc định D:\\GXD\\Dulieu hoặc biến DT_GVT_DIR)")
    sp = ap.add_subparsers(dest="lenh", required=True)
    sp.add_parser("ds")
    t = sp.add_parser("tra"); t.add_argument("--tinh", choices=TINH, required=True); t.add_argument("--tu-khoa", required=True)
    t.add_argument("--ky"); t.add_argument("--khu-vuc"); t.add_argument("--top", type=int, default=20)
    g = sp.add_parser("goi-y"); g.add_argument("--tinh", choices=TINH, required=True); g.add_argument("--data", required=True)
    g.add_argument("--ky"); g.add_argument("--ra")
    a = ap.parse_args()
    if not a.thu_muc:
        sys.exit("Chưa có thư mục dữ liệu: --thu-muc hoặc biến môi trường DT_GVT_DIR")
    {"ds": cmd_ds, "tra": cmd_tra, "goi-y": cmd_goi_y}[a.lenh](a)


if __name__ == "__main__":
    main()
