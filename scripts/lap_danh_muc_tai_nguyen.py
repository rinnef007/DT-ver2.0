#!/usr/bin/env python3
"""Lập danh mục tài nguyên (vật liệu, nhân công, máy) dùng trong định mức TT 38/2026 đã trích.

Mỗi tài nguyên một dòng: loại, tên đúng như TT 38 (khớp cột ma_tn của bảng giá), đơn vị thường gặp,
số mã sử dụng, phụ lục, ví dụ mã, các cách viết khác của cùng tài nguyên (sau chuẩn hoá dấu cách/hoa thường).
Dùng để đối chiếu tên với công bố giá của Sở Xây dựng.

  python scripts/lap_danh_muc_tai_nguyen.py --data data/tt38
"""
import argparse
import collections
import csv
import gzip
import os
import re
import unicodedata


import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dutoan_core import khoa_ten as khoa  # noqa: E402  — cùng khoá với khâu tra giá


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    a = ap.parse_args()
    rows = csv.DictReader(gzip.open(os.path.join(a.data, "dinh_muc_tt38.csv.gz"), "rt", encoding="utf-8"))
    kt = {r["ma_hieu"] for r in csv.DictReader(gzip.open(os.path.join(a.data, "ma_can_kiem_tra.csv.gz"), "rt", encoding="utf-8"))}
    d = collections.OrderedDict()
    for r in rows:
        if r["loai"] not in ("VL", "NC", "M") or not r["ma_tn"]:
            continue
        e = d.setdefault((r["loai"], r["ma_tn"]), {"dv": collections.Counter(), "ma": set(), "pl": set(), "kt": 0})
        e["dv"][r["don_vi_tn"]] += 1
        e["ma"].add(r["ma_hieu"])
        e["pl"].add(r.get("phu_luc", ""))
        if r["ma_hieu"] in kt:
            e["kt"] += 1
    nhom = collections.defaultdict(list)
    for (lo, t) in d:
        nhom[(lo, khoa(t))].append(t)
    thu_tu = {"NC": 0, "M": 1, "VL": 2}
    out = []
    for (lo, t), e in sorted(d.items(), key=lambda x: (thu_tu[x[0][0]], khoa(x[0][1]))):
        bt = [x for x in nhom[(lo, khoa(t))] if x != t]
        dv = [u for u, _ in e["dv"].most_common() if u]
        chi_o_ma_kt = e["kt"] == len(e["ma"])
        out.append({"loai": lo, "ten_tn": t, "don_vi": dv[0] if dv else "", "don_vi_khac": " / ".join(dv[1:3]),
                    "so_ma": len(e["ma"]), "phu_luc": ",".join(sorted(p for p in e["pl"] if p)),
                    "vi_du_ma": " ".join(sorted(e["ma"])[:3]), "cach_viet_khac": " | ".join(bt),  # cùng một dòng giá dùng được cho mọi cách viết
                    "ghi_chu": "chỉ xuất hiện ở mã cần kiểm tra — có thể là lỗi trích" if chi_o_ma_kt else ""})
    p = os.path.join(a.data, "danh_muc_tai_nguyen_tt38.csv.gz")
    with gzip.open(p, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    c = collections.Counter(r["loai"] for r in out)
    print(f"Đã ghi {p}: {len(out)} tài nguyên (NC {c['NC']}, máy {c['M']}, vật liệu {c['VL']}); "
          f"{sum(1 for r in out if r['cach_viet_khac'])} có cách viết khác; {sum(1 for r in out if r['ghi_chu'])} chỉ ở mã cần kiểm tra")


if __name__ == "__main__":
    main()
