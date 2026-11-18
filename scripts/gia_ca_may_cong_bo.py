"""Tra giá ca máy do Sở Xây dựng công bố (data/gia-ca-may/cong-bo/gia_ca_may_cong_bo.csv).

  python scripts/gia_ca_may_cong_bo.py --ma M101.0101 [--vung HN-V1] [--ngay 2026-11-17]
  python scripts/gia_ca_may_cong_bo.py --nhom M101.0100 [--vung HN-V2]

Chọn văn bản còn hiệu lực tại --ngay (mặc định hôm nay) theo hieu_luc_tu/hieu_luc_den, giống dữ liệu nhân công.
Mã máy theo Phụ lục IV TT 37/2026 (M101.0101…); tên ngắn trong tệp chỉ là phần ghi ở dòng máy của bảng công bố —
tên đầy đủ đọc theo mã ở PL IV TT 37 hoặc bản công bố gốc. Giá chưa VAT. Khi lập dự toán ở thời điểm khác thời điểm
công bố, được bổ sung chênh lệch nhiên liệu và nhân công (QĐ 2075 Phần IV mục 2) — dùng scripts/gia_ca_may.py để
tính lại theo PL IV với giá nhiên liệu, nhân công tại thời điểm lập.
"""
import argparse, csv, os, sys
from datetime import date, datetime
F = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "gia-ca-may", "cong-bo", "gia_ca_may_cong_bo.csv")


def d(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s else None


def con_hieu_luc(r, ngay):
    tu, den = d(r["hieu_luc_tu"]), d(r["hieu_luc_den"])
    return (tu is None or tu <= ngay) and (den is None or ngay <= den)


def tra(ma=None, nhom=None, vung=None, ngay=None):
    ngay = ngay or date.today()
    out = []
    for r in csv.DictReader(open(F, encoding="utf-8-sig")):
        if ma and r["ma_may"].upper() != ma.upper():
            continue
        if nhom and r["nhom_may"].upper() != nhom.upper():
            continue
        if vung and r["ma_vung"] != vung:
            continue
        if con_hieu_luc(r, ngay):
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ma"); ap.add_argument("--nhom"); ap.add_argument("--vung"); ap.add_argument("--ngay")
    a = ap.parse_args()
    if not a.ma and not a.nhom:
        sys.exit("Cần --ma hoặc --nhom")
    rs = tra(a.ma, a.nhom, a.vung, d(a.ngay) if a.ngay else None)
    if not rs:
        sys.exit("Không có giá công bố còn hiệu lực cho điều kiện này")
    for r in rs:
        g = f"{int(r['don_gia']):>13,}" if r["don_gia"] else "   (để trống)"
        print(f"{r['ma_may']:<11} {r['ten_may'][:40]:<40} {r['ma_vung']:<6} {g} đ/ca  {r['van_ban']} (từ {r['hieu_luc_tu']}) {r['ghi_chu']}")


if __name__ == "__main__":
    main()
