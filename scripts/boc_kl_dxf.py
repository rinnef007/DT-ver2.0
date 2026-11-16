#!/usr/bin/env python3
"""Đo hình học từ bản vẽ DXF để hỗ trợ bóc khối lượng.

  python boc_kl_dxf.py layers ban_ve.dxf
  python boc_kl_dxf.py do ban_ve.dxf [--layer L1 L2 ...] [--ty-le 0.001] [--csv ket_qua.csv]

Kết quả chỉ là số đo hình học (chiều dài, diện tích, số block) theo layer.
Ý nghĩa và hệ số (chiều dày, chiều cao, quy cách) do người dùng xác nhận trước khi
đưa vào khoi_luong.csv. File DWG cần chuyển sang DXF trước (AutoCAD: SAVEAS → DXF).
Cần: pip install ezdxf
"""
import argparse
import csv
import math
import sys
from collections import defaultdict

try:
    import ezdxf
    from ezdxf import path as ezpath
except ImportError:
    sys.exit("Thiếu thư viện ezdxf: pip install ezdxf")


def dien_tich_poly(pts):
    s = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i][0], pts[i][1]
        x2, y2 = pts[(i + 1) % n][0], pts[(i + 1) % n][1]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def do_dai(e):
    t = e.dxftype()
    if t == "LINE":
        return e.dxf.start.distance(e.dxf.end)
    if t == "ARC":
        a = (e.dxf.end_angle - e.dxf.start_angle) % 360
        return math.radians(a) * e.dxf.radius
    if t == "CIRCLE":
        return 2 * math.pi * e.dxf.radius
    if t in ("LWPOLYLINE", "POLYLINE", "SPLINE", "ELLIPSE"):
        try:
            p = ezpath.make_path(e)
            v = list(p.flattening(0.01))
            return sum(v[i].distance(v[i + 1]) for i in range(len(v) - 1))
        except Exception:
            return 0.0
    return 0.0


def dien_tich(e):
    t = e.dxftype()
    if t == "LWPOLYLINE" and e.closed:
        try:
            p = ezpath.make_path(e)
            return dien_tich_poly(list(p.flattening(0.01)))
        except Exception:
            return dien_tich_poly(list(e.get_points("xy")))
    if t == "POLYLINE" and e.is_closed:
        return dien_tich_poly([v.dxf.location for v in e.vertices])
    if t == "CIRCLE":
        return math.pi * e.dxf.radius ** 2
    if t == "HATCH":
        tong = 0.0
        for bp in e.paths:
            try:
                p = ezpath.from_hatch_boundary_path(bp) if hasattr(ezpath, "from_hatch_boundary_path") else None
                if p is None:
                    continue
                a = dien_tich_poly(list(p.flattening(0.01)))
                # đường biên ngoài cộng, lỗ trừ (cờ 16 = outermost/external tuỳ phiên bản)
                tong += a if (bp.path_type_flags & 1) else -a
            except Exception:
                continue
        return abs(tong)
    return 0.0


def cmd_layers(a):
    doc = ezdxf.readfile(a.file)
    dem = defaultdict(lambda: defaultdict(int))
    for e in doc.modelspace():
        dem[e.dxf.layer][e.dxftype()] += 1
    print(f"Đơn vị bản vẽ ($INSUNITS): {doc.header.get('$INSUNITS', 'không khai báo')}  (4 = mm, 6 = m)")
    for lay in sorted(dem):
        print(f"{lay}: " + ", ".join(f"{k} {v}" for k, v in sorted(dem[lay].items())))


def cmd_do(a):
    doc = ezdxf.readfile(a.file)
    k = a.ty_le
    kq = defaultdict(lambda: {"chieu_dai": 0.0, "dien_tich": 0.0, "so_doi_tuong": 0, "block": defaultdict(int)})
    for e in doc.modelspace():
        lay = e.dxf.layer
        if a.layer and lay not in a.layer:
            continue
        r = kq[lay]
        r["so_doi_tuong"] += 1
        if e.dxftype() == "INSERT":
            r["block"][e.dxf.name] += 1
            continue
        if e.dxftype() != "HATCH":
            r["chieu_dai"] += do_dai(e) * k
        r["dien_tich"] += dien_tich(e) * k * k
    rows = []
    for lay in sorted(kq):
        r = kq[lay]
        rows.append({"layer": lay, "chieu_dai_m": round(r["chieu_dai"], 3), "dien_tich_m2": round(r["dien_tich"], 3),
                     "so_doi_tuong": r["so_doi_tuong"],
                     "block": "; ".join(f"{n} x{c}" for n, c in sorted(r["block"].items()))})
    for r in rows:
        print(f"{r['layer']}: dài {r['chieu_dai_m']:,} · diện tích {r['dien_tich_m2']:,} · {r['so_doi_tuong']} đối tượng"
              + (f" · block: {r['block']}" if r["block"] else ""))
    print(f"(Đã nhân tỷ lệ {k} cho chiều dài, {k}² cho diện tích. Diện tích chỉ tính polyline kín, circle, hatch.)")
    if a.csv:
        with open(a.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["layer"])
            w.writeheader()
            w.writerows(rows)
        print(f"Đã ghi {a.csv}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="lenh", required=True)
    s = sp.add_parser("layers"); s.add_argument("file"); s.set_defaults(f=cmd_layers)
    s = sp.add_parser("do"); s.add_argument("file"); s.add_argument("--layer", nargs="+")
    s.add_argument("--ty-le", type=float, default=1.0, help="Hệ số đổi đơn vị bản vẽ sang m (mm → 0.001)")
    s.add_argument("--csv"); s.set_defaults(f=cmd_do)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
