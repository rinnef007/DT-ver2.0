"""Nối tên máy trong định mức TT 38 với mã máy PL IV TT 37 (data/gia-ca-may/anh_xa_may_tt38.csv) và tra giá ca máy công bố.

trang_thai: khop_doi_chieu (khớp tự động và trùng cách GXD gán mã) | khop_tu_dong (khớp tự động, chưa có đối chứng) |
can_xac_nhan (nhiều máy phù hợp hoặc lệch với GXD — người lập điền cột ma_may) | khong_khop.
Chỉ dùng cột ma_may (trống = chưa xác nhận). Người lập sửa trực tiếp cột ma_may để xác nhận.
"""
import csv, os
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "data", "gia-ca-may", "anh_xa_may_tt38.csv")


def nap():
    return {r["ten_tn"]: r for r in csv.DictReader(open(F, encoding="utf-8-sig"))}


def gia_may(ten_tn, ma_vung, ngay=None, bang=None):
    """(đơn giá, nguồn) hoặc (None, lý do)."""
    import gia_ca_may_cong_bo as g
    bang = bang or nap()
    r = bang.get(ten_tn)
    if not r:
        return None, "tên máy chưa có trong bảng ánh xạ"
    if not r["ma_may"]:
        return None, f"ánh xạ {r['trang_thai']} — đề xuất {r['de_xuat_tu_dong']}" + (f", GXD {r['ma_theo_gxd']}" if r["ma_theo_gxd"] else "")
    rs = g.tra(r["ma_may"], vung=ma_vung, ngay=ngay or date.today())
    if not rs or not rs[0]["don_gia"]:
        return None, f"{r['ma_may']}: không có giá công bố vùng {ma_vung} còn hiệu lực"
    x = rs[0]
    return float(x["don_gia"]), f"{x['van_ban']} — {r['ma_may']} {x['ten_day_du']} ({ma_vung}; ánh xạ {r['trang_thai']})"
