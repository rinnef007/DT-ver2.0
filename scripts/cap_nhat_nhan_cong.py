"""Thêm một văn bản công bố giá nhân công mới của Sở XD vào data/nhan-cong (kỳ năm/quý/khi có công bố).

Dùng:
  python scripts/cap_nhat_nhan_cong.py --tinh "Hà Nội" --file moi.csv --van-ban "QĐ xxxx/QĐ-SXD Sở XD Hà Nội" \
      --ngay 2027-01-15 --tu 2027-01-15 [--phuong-phap moi] [--ghi]

moi.csv (utf-8): ma_vung,ten_vung,ten_tn,ten_trong_van_ban,don_vi,don_gia
- ten_tn phải đúng tên tài nguyên TT 38 (Nhân công nhóm 1…4, Nhân công vận hành máy, điều khiển máy, Lái xe, Kỹ sư, Thợ lặn, Nghệ nhân…).
- Các dòng đang hiệu lực (hieu_luc_den trống) của cùng tỉnh được đóng lại tại ngày (--tu − 1).
- Không có --ghi: chỉ in thay đổi để kiểm tra (chạy thử).
Sau khi ghi: cập nhật phạm vi vùng trong data/nhan-cong/README.md, ma_vung trong xa_phuong_tuyen_hn_hp.csv
nếu mã vùng đổi, references/can-cu-phap-ly.md, rồi chạy tests.
"""
import argparse
import csv
import os
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(os.path.dirname(HERE), "data", "nhan-cong", "gia_nhan_cong_chuyen_doi_2026.csv")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tinh", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--van-ban", required=True)
    ap.add_argument("--ngay", required=True, help="ngày văn bản yyyy-mm-dd")
    ap.add_argument("--tu", required=True, help="ngày bắt đầu áp dụng yyyy-mm-dd")
    ap.add_argument("--phuong-phap", default="moi", choices=["moi", "chuyen_doi", "dieu_chinh"])
    ap.add_argument("--ghi", action="store_true")
    a = ap.parse_args()
    tu = datetime.strptime(a.tu, "%Y-%m-%d").date()
    datetime.strptime(a.ngay, "%Y-%m-%d")
    den_cu = (tu - timedelta(days=1)).isoformat()
    rows = list(csv.DictReader(open(F, encoding="utf-8-sig")))
    cols = list(rows[0])
    moi = list(csv.DictReader(open(a.file, encoding="utf-8-sig")))
    can = {"ma_vung", "ten_vung", "ten_tn", "don_gia"}
    if not moi or not can <= set(moi[0]):
        sys.exit(f"{a.file}: cần các cột {', '.join(sorted(can))}")
    dong = 0
    for r in rows:
        if r["tinh"] == a.tinh and not r.get("hieu_luc_den"):
            if (r.get("hieu_luc_tu") or "") >= a.tu:
                sys.exit(f"Dòng {r['ma_vung']} / {r['ten_tn']} ({r['van_ban']}) bắt đầu {r['hieu_luc_tu']} ≥ --tu {a.tu} — kiểm tra lại ngày")
            r["hieu_luc_den"] = den_cu
            dong += 1
    for m in moi:
        float(m["don_gia"])
        rows.append({c: "" for c in cols} | {
            "tinh": a.tinh, "ma_vung": m["ma_vung"], "ten_vung": m["ten_vung"], "ten_tn": m["ten_tn"],
            "ten_trong_van_ban": m.get("ten_trong_van_ban") or m["ten_tn"], "don_vi": m.get("don_vi") or "công",
            "don_gia": m["don_gia"], "van_ban": a.van_ban, "ngay_van_ban": a.ngay,
            "hieu_luc": f"Từ {tu:%d/%m/%Y}", "hieu_luc_tu": a.tu, "hieu_luc_den": "", "phuong_phap": a.phuong_phap})
    print(f"{a.tinh}: đóng {dong} dòng đang hiệu lực tại {den_cu}; thêm {len(moi)} dòng {a.van_ban} từ {a.tu}")
    if a.ghi:
        with open(F, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"Đã ghi {F}")
    else:
        print("(chạy thử — thêm --ghi để ghi)")


if __name__ == "__main__":
    main()
