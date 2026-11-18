"""Nối tên máy trong định mức TT 38 với mã máy PL IV TT 37 (data/gia-ca-may/anh_xa_may_tt38.csv) và tra giá ca máy công bố.

trang_thai: khop_doi_chieu (khớp tự động và trùng cách GXD gán mã) | khop_tu_dong (khớp tự động, chưa có đối chứng) |
can_xac_nhan (nhiều máy phù hợp hoặc lệch với GXD — người lập điền cột ma_may) | khong_khop.
Chỉ dùng cột ma_may (trống = chưa xác nhận).

Xác nhận theo từng hồ sơ: tệp <thư mục hồ sơ>/anh_xa_may.csv (ten_tn, ma_may, can_cu) — ưu tiên hơn bảng chung,
vì lựa chọn máy (vd. cần cẩu bánh hơi hay bánh xích) phụ thuộc biện pháp thi công của công trình. Bảng chung giữ
nguyên trạng thái can_xac_nhan; không sửa bảng chung cho một hồ sơ.
"""
import csv, os
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "data", "gia-ca-may", "anh_xa_may_tt38.csv")


F_PL4 = os.path.join(ROOT, "data", "gia-ca-may", "danh_muc_may_pl4_tt37.csv")


def ma_pl4():
    return {r["ma_may"]: r["ten_day_du"] for r in csv.DictReader(open(F_PL4, encoding="utf-8-sig"))}


def nap_ho_so(thu_muc):
    p = os.path.join(thu_muc or "", "anh_xa_may.csv")
    if not thu_muc or not os.path.exists(p):
        return {}
    return {r["ten_tn"].strip(): r for r in csv.DictReader(open(p, encoding="utf-8-sig")) if r.get("ten_tn", "").strip()}


def nap(thu_muc=None):
    """Bảng chung, ghi đè bằng xác nhận của hồ sơ (trang_thai = xac_nhan_ho_so)."""
    b = {r["ten_tn"]: r for r in csv.DictReader(open(F, encoding="utf-8-sig"))}
    for ten, r in nap_ho_so(thu_muc).items():
        if (r.get("ma_may") or "").strip():
            g = dict(b.get(ten, {"ten_tn": ten, "de_xuat_tu_dong": "", "ma_theo_gxd": ""}))
            g.update(ma_may=r["ma_may"].strip(), trang_thai="xac_nhan_ho_so", can_cu=(r.get("can_cu") or "").strip())
            b[ten] = g
    return b


def gia_may(ten_tn, ma_vung, ngay=None, bang=None, thu_muc=None):
    """(đơn giá, nguồn) hoặc (None, lý do)."""
    import gia_ca_may_cong_bo as g
    bang = bang or nap(thu_muc)
    r = bang.get(ten_tn)
    if not r:
        return None, "tên máy chưa có trong bảng ánh xạ"
    if not r["ma_may"]:
        return None, f"ánh xạ {r['trang_thai']} — đề xuất {r['de_xuat_tu_dong']}" + (f", GXD {r['ma_theo_gxd']}" if r["ma_theo_gxd"] else "")
    rs = g.tra(r["ma_may"], vung=ma_vung, ngay=ngay or date.today())
    if not rs or not rs[0]["don_gia"]:
        return None, f"{r['ma_may']}: không có giá công bố vùng {ma_vung} còn hiệu lực"
    x = rs[0]
    cc = f"; căn cứ chọn máy: {r['can_cu']}" if r.get("can_cu") else ""
    return float(x["don_gia"]), f"{x['van_ban']} — {r['ma_may']} {x['ten_day_du']} ({ma_vung}; ánh xạ {r['trang_thai']}{cc})"


def soat_ho_so(dl, ten_may_dung, co_gia):
    """S24: xác nhận mã máy. ten_may_dung: tên máy (M) hồ sơ dùng; co_gia(ten) → True nếu đã có giá trong gia_tai_nguyen."""
    kq = []
    b = nap(dl.thu_muc)
    rieng = nap_ho_so(dl.thu_muc)
    pl4 = ma_pl4()
    for ten, r in rieng.items():
        ma = (r.get("ma_may") or "").strip()
        if ma and ma not in pl4:
            kq.append(("S24", "CHAN", f"anh_xa_may.csv: '{ten}' → mã {ma} không có trong danh mục PL IV TT 37"))
        elif ma and not (r.get("can_cu") or "").strip():
            kq.append(("S24", "CANH_BAO", f"anh_xa_may.csv: '{ten}' → {ma} chưa ghi căn cứ chọn máy (biện pháp thi công, bản vẽ, thiết kế tổ chức thi công)"))
    cho = []
    for ten in sorted(ten_may_dung):
        r = b.get(ten)
        if (not r or not r.get("ma_may")) and not co_gia(ten):
            cho.append(ten if not r else f"{ten} (đề xuất {r.get('de_xuat_tu_dong') or '—'}" + (f", GXD {r['ma_theo_gxd']}" if r.get("ma_theo_gxd") else "") + ")")
    if cho:
        kq.append(("S24", "CANH_BAO", f"{len(cho)} máy chưa xác nhận mã PL IV và chưa có giá: " + "; ".join(cho[:15])
                   + (" …" if len(cho) > 15 else "") + " — xác nhận trong <hồ sơ>/anh_xa_may.csv (ten_tn, ma_may, can_cu) hoặc nhập giá trực tiếp"))
    if rieng:
        kq.append(("S24", "THONG_TIN", f"{sum(1 for r in rieng.values() if r.get('ma_may'))} máy được xác nhận mã riêng cho hồ sơ (anh_xa_may.csv)"))
    return kq
