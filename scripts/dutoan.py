#!/usr/bin/env python3
"""Công cụ dự toán xây dựng Việt Nam (NĐ 206/2026, TT 36/37/38/40/2026).

Lệnh:
  kiemtra-dulieu  Kiểm tra bộ dữ liệu định mức + giá
  tra             Tra định mức theo mã / từ khoá / liệt kê chương
  soat            Soát bảng khối lượng + cấu hình trước khi tính
  tinh            Tính dự toán và xuất Excel có công thức
                  (config "mau_xuat": "bang_3_8" mặc định, hoặc "doan_vung" cho mẫu theo đoạn/xã – vùng giá)
  can-gia         Lập danh sách tài nguyên cần giá của một hồ sơ (theo từng vùng) để điền từ công bố giá kỳ hiện hành
  ty-le           Tra/nội suy định mức tỷ lệ: QLDA (Bảng 1.1 PL VIII TT 38), chi phí quản lý của chủ sở hữu (Bảng 4 TT 40),
                  khảo sát (Bảng 5.1–5.3 TT 36), quản lý trong dự toán tư vấn (Bảng 6.1), quản lý mua sắm thiết bị (Bảng 2.3)
  chuyendoi       Chuyển file Excel xuất từ phần mềm khác sang CSV chuẩn bằng file ánh xạ cột

Định mức TT 38/2026 trích sẵn trong data/tt38/, bảng tỷ lệ TT 36/TT 40 trong data/*.json; skill không chứa đơn giá —
giá lấy từ file người dùng cung cấp theo công bố kỳ hiện hành.
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dutoan_core import (BANG_TY_LE_TT40, DuLieu, khoa_ten, nhan_cong_tham_chieu, vung_nhan_cong, ap_cap_phoi, ap_he_so_sua_chua, bo_dau, fmt, in_soat,  # noqa: E402
                         kiem_tra_nac_ks, kiem_tra_nac_tt40, la_khao_sat, la_tt40, nap_config, nap_khoi_luong, noi_suy, soat, tinh_bang_3_8,
                         tinh_doan_vung)


def in_bang(rows, cols):
    if not rows:
        return
    widths = [min(60, max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows))) for c in cols]
    print("  ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(str(r.get(c, ""))[:w].ljust(w) for c, w in zip(cols, widths)))


def cmd_kiemtra(a):
    dl = DuLieu(a.data)
    print(f"Thư mục: {a.data}")
    vung = dl.cac_vung()
    print(f"Số mã định mức riêng của hồ sơ: {len(dl.ma_rieng)}  ·  Định mức TT 38/2026 dùng chung: {'có' if dl.co_tt38 else 'không'} ({len(dl.dinh_muc) - len(dl.ma_rieng)} mã)  ·  Số dòng giá: {len(dl.gia)}" + (f"  ·  Vùng giá: {', '.join(vung)}" if vung else ""))
    tn = dl.tai_nguyen_dung()
    print(f"Số tài nguyên được định mức sử dụng: {len(tn)}")
    for m in dl.loi:
        print(f"[LỖI] {m}")
    for m in dl.canh_bao:
        print(f"[CẢNH BÁO] {m}")
    thieu = dl.thieu_gia(None, vung or [""])
    if thieu:
        print(f"[THIẾU GIÁ] {len(thieu)}: " + ", ".join(thieu[:50]) + (" …" if len(thieu) > 50 else ""))
    for m, h in tn.items():
        g = dl.gia_cua(m, vung[0] if vung else "")
        if g and g["loai"] and h["loai"] != g["loai"]:
            print(f"[CẢNH BÁO] {m}: loại trong định mức ({h['loai']}) khác loại trong bảng giá ({g['loai']})")
    ngay = sorted({g["ngay"] for g in dl.gia.values() if g["ngay"]})
    if ngay:
        print(f"Ngày áp dụng giá: từ {ngay[0]} đến {ngay[-1]}")
    nguon = sorted({g["nguon"] for g in dl.gia.values() if g["nguon"]})
    print("Nguồn giá: " + ("; ".join(nguon[:12]) + (" …" if len(nguon) > 12 else "") if nguon else "(không có)"))
    return 1 if dl.loi else 0


def doc_ly_trinh(x):
    """'Km36+200' | '36+200' | '36.2' → km (float)."""
    t = x.strip().lower().replace("km", "").replace(" ", "")
    m = re.fullmatch(r"(-?\d+)\+(\d+(?:[.,]\d+)?)", t)
    if m:
        return int(m.group(1)) + float(m.group(2).replace(",", ".")) / 1000
    return float(t.replace(",", "."))


def cmd_tra(a):
    if a.ly_trinh:
        from dutoan_core import SKILL_ROOT, doc_csv, nhan_cong_tham_chieu
        km = doc_ly_trinh(a.ly_trinh)
        rows = doc_csv(os.path.join(SKILL_ROOT, "data", "nhan-cong", "xa_phuong_tuyen_hn_hp.csv")) or []
        kq = [r for r in rows if float(r["tu_km"]) - 1e-9 <= km <= float(r["den_km"]) + 1e-9]
        if not kq:
            print(f"Km{int(km)}+{round((km - int(km)) * 1000):03d}: ngoài danh sách xã, phường tuyến cao tốc Hà Nội – Hải Phòng (Km0-420 ÷ Km105+450)")
            return 1
        tc = nhan_cong_tham_chieu()
        ten_vung = {k[0]: v["ten_vung"] for k, v in tc.items()}
        print(f"Km{int(km)}+{round((km - int(km)) * 1000):03d} — tuyến cao tốc Hà Nội – Hải Phòng:")
        for r in kq:
            mv = r["ma_vung_nhan_cong"]
            print(f"  {r['xa_phuong']} ({r['tinh']}, {r['khu_vuc_tuyen']})" + (f" — chiều {r['chieu']}" if r["chieu"] else "")
                  + f" · lý trình: {r['ly_trinh_goc']}")
            print(f"    Vùng nhân công: {(mv + ' – ' + ten_vung.get(mv, '')) if mv else 'chưa xác định'} · {r['can_cu_vung']}")
        if len({r['xa_phuong'] for r in kq}) > 1 and not any(r["chieu"] for r in kq):
            print("  [CHÚ Ý] Lý trình nằm ở đoạn chồng lấn giữa hai xã trong danh sách — kiểm tra lại ranh giới")
        return 0
    if a.tai_nguyen is not None:
        from dutoan_core import TT38_DIR, doc_csv
        tu = [bo_dau(t) for t in a.tai_nguyen.split()]
        kq = [r for r in (doc_csv(os.path.join(TT38_DIR, "danh_muc_tai_nguyen_tt38.csv")) or [])
              if (not a.loai or r["loai"] == a.loai.upper()) and all(any(w.startswith(t) for w in re.split(r"[\s,()/]+", bo_dau(r["ten_tn"] + " " + r["cach_viet_khac"]))) for t in tu)]
        def diem(r):
            w = set(re.split(r"[\s,()/]+", bo_dau(r["ten_tn"])))
            return (-sum(t in w for t in tu), -int(r["so_ma"] or 0))
        kq.sort(key=diem)
        print(f"{len(kq)} tài nguyên (danh mục TT 38/2026 — tên dùng cho cột ma_tn của bảng giá)")
        in_bang(kq[: a.gioi_han], ["loai", "ten_tn", "don_vi", "so_ma", "phu_luc", "vi_du_ma", "cach_viet_khac", "ghi_chu"])
        if len(kq) > a.gioi_han:
            print(f"… còn {len(kq) - a.gioi_han}, thu hẹp từ khoá hoặc tăng --gioi-han")
        return 0
    dl = DuLieu(a.data)
    if a.cap_phoi:
        tu = [bo_dau(t) for t in a.cap_phoi.split()]
        kq = [{"ma": m, "mo_ta": c["mo_ta"][:110], "thanh_phan": "; ".join(f"{v} {x:g} {d}" for v, d, x in c["tp"])}
              for m, c in dl.cap_phoi.items() if all(t in bo_dau(m + " " + c["mo_ta"]) for t in tu)]
        print(f"{len(kq)} mã cấp phối")
        in_bang(kq[: a.gioi_han], ["ma", "mo_ta", "thanh_phan"])
        return 0
    if a.chuong:
        dem = defaultdict(int)
        for ma in dl.dinh_muc:
            dem[ma.split(".")[0] if "." in ma else ma[:2]] += 1
        for k in sorted(dem):
            print(f"{k}: {dem[k]} mã")
        return 0
    if a.ma:
        vung = dl.cac_vung() or [""]
        for ma in a.ma:
            d = dl.dinh_muc.get(ma)
            if not d:
                print(f"{ma}: không có trong dữ liệu")
                continue
            print(f"\n{ma}  {d['ten']}  [{d['don_vi']}]  — nguồn: {d['nguon']}")
            rows = []
            for h in d["hao_phi"]:
                r = {"loai": h["loai"], "ma_tn": h["ma_tn"], "ten": h["ten_tn"], "dvt": h["don_vi_tn"],
                     "hao_phi": f"{h['hao_phi']:g}", "he_so": f"{h['he_so']:g}"}
                for v in vung:
                    g = dl.gia_cua(h["ma_tn"], v)
                    r[f"gia {v}".strip()] = fmt(g["don_gia"]) if g else ("%" if h["loai"] in ("VLK", "MK") else "THIẾU")
                rows.append(r)
            in_bang(rows, ["loai", "ma_tn", "ten", "dvt", "hao_phi", "he_so"] + [f"gia {v}".strip() for v in vung])
        return 0
    if a.tu_khoa:
        tu = [bo_dau(t) for t in a.tu_khoa.split()]
        kq = [{"ma": ma, "ten": d["ten"], "dv": d["don_vi"]} for ma, d in dl.dinh_muc.items()
              if all(t in bo_dau(d["ten"]) or t in bo_dau(ma) for t in tu)]
        print(f"{len(kq)} kết quả")
        in_bang(kq[: a.gioi_han], ["ma", "ten", "dv"])
        if len(kq) > a.gioi_han:
            print(f"… còn {len(kq) - a.gioi_han} kết quả, thu hẹp từ khoá hoặc tăng --gioi-han")
        return 0
    print("Cần --ma, --tu-khoa hoặc --chuong")
    return 2


def cmd_soat(a):
    dl = DuLieu(a.data)
    for m in dl.loi:
        print(f"[LỖI DỮ LIỆU] {m}")
    kl = nap_khoi_luong(a.khoi_luong)
    cfg = nap_config(a.config) if a.config else None
    loi_cp = ap_cap_phoi(dl, kl)
    n_sc = ap_he_so_sua_chua(dl, kl, cfg)
    if n_sc:
        print(f"Hồ sơ sửa chữa: đã áp hệ số PL VI mục 3.b (VL 1,02; NC 1,15; M 1,05) cho {n_sc} dòng dùng định mức PL II/III.")
    kq = soat(dl, kl, cfg) + [("S16", "CHAN", x) for x in loi_cp]
    in_soat(kq)
    return 1 if any(x[1] == "CHAN" for x in kq) or dl.loi else 0


def cmd_tinh(a):
    dl = DuLieu(a.data)
    if dl.loi:
        for m in dl.loi:
            print(f"[LỖI DỮ LIỆU] {m}")
        if not a.nhap:
            print("Dừng: sửa lỗi dữ liệu trước (hoặc dùng --nhap để xuất bản nháp).")
            return 1
    kl = nap_khoi_luong(a.khoi_luong)
    cfg = nap_config(a.config)
    loi_cp = ap_cap_phoi(dl, kl)
    n_sc = ap_he_so_sua_chua(dl, kl, cfg)
    if n_sc:
        print(f"Hồ sơ sửa chữa: đã áp hệ số PL VI mục 3.b (VL 1,02; NC 1,15; M 1,05) cho {n_sc} dòng dùng định mức PL II/III.")
    kq = soat(dl, kl, cfg) + [("S16", "CHAN", x) for x in loi_cp]
    chan = [x for x in kq if x[1] == "CHAN"]
    if chan and not a.nhap:
        in_soat(kq)
        print("\nDừng: còn mục CHẶN. Xử lý xong rồi chạy lại, hoặc dùng --nhap để xuất BẢN NHÁP có đánh dấu.")
        return 1
    nhap = bool(chan) or a.nhap
    mau = cfg.get("mau_xuat", "bang_3_8")
    if mau == "doan_vung":
        from xuat_excel_doan import xuat as xuat_doan
        py = tinh_doan_vung(dl, kl, cfg)
        kq += kiem_tra_nac_tt40(cfg, py["NC"], py["truoc_thue"]) + kiem_tra_nac_ks(cfg, py["NC"], py["T"], py["TGT"])
        xuat_doan(a.out, dl, kl, cfg, kq, py, nhap=nhap)
        print(f"Đã xuất: {a.out}" + ("  (BẢN NHÁP)" if nhap else ""))
        print("Kết quả tính đối chiếu (Python):")
        for hm, h in py["hang_muc"].items():
            print(f"  {hm[:48]:48s} trước thuế {fmt(h['truoc_thue']):>18s} · VAT {fmt(h['vat']):>15s} · sau thuế {fmt(h['sau_thue']):>18s}")
        th = py["tong_hop"]
        for it in th["items"]:
            tt, g, s = th["gia_tri"][it["ma"]]
            print(f"  [{it.get('stt',''):>4s}] {it['ten'][:52]:52s} {fmt(tt):>16s} {fmt(g):>14s} {fmt(s):>16s}")
        doi_chieu = {"hang_muc": {hm: {k: h[k] for k in ("truoc_thue", "vat", "sau_thue")} for hm, h in py["hang_muc"].items()},
                     "tong_hop": {m: v for m, v in th["gia_tri"].items()}}
    else:
        from xuat_excel import xuat
        py = tinh_bang_3_8(dl, kl, cfg)
        kq += kiem_tra_nac_tt40(cfg, py["NC"], py["GXDTT"]) + kiem_tra_nac_ks(cfg, py["NC"], py["T"], py.get("TGT", 0))
        xuat(a.out, dl, kl, cfg, kq, py, nhap=nhap)
        print(f"Đã xuất: {a.out}" + ("  (BẢN NHÁP)" if nhap else ""))
        print("Kết quả tính đối chiếu (Python):")
        cac_k = (("VL", "NC", "M", "T", "C", "TT", "GT", "TL", "CPA", "CBC", "CK", "G", "GTGT", "LT", "DP", "GKS") if la_khao_sat(cfg)
                 else ("VL", "NC", "M", "T", "C", "TT", "GT", "TL", "GXDTT", "GTGT", "GXD", "LT"))
        for k in cac_k:
            print(f"  {k:6s} {fmt(py[k]):>20s}")
        doi_chieu = py
    for x in kq:
        if x[0] == "S19":
            print(f"[{x[1]}] {x[0]}  {x[2]}")
    if kq:
        print(f"\n{len(kq)} mục soát — xem sheet CANH_BAO.")
    with open(os.path.splitext(a.out)[0] + "_doi_chieu.json", "w", encoding="utf-8") as f:
        json.dump(doi_chieu, f, ensure_ascii=False, indent=2)
    return 0


def cmd_chuyendoi(a):
    import openpyxl
    with open(a.anh_xa, encoding="utf-8") as f:
        mp = json.load(f)
    wb = openpyxl.load_workbook(a.nguon, data_only=True, read_only=True)
    ws = wb[mp["sheet"]] if mp.get("sheet") in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = int(mp.get("dong_tieu_de", 1)) - 1
    hdr = [str(c).strip() if c is not None else "" for c in rows[hdr_i]]
    idx = {}
    for chuan, ten_nguon in mp["cot"].items():
        if ten_nguon not in hdr:
            sys.exit(f"Không thấy cột '{ten_nguon}' (cho '{chuan}') trong dòng tiêu đề: {hdr}")
        idx[chuan] = hdr.index(ten_nguon)
    cot_ra = {"dinh_muc": ["ma_hieu", "ten_cong_tac", "don_vi", "loai", "ma_tn", "ten_tn", "don_vi_tn", "hao_phi", "he_so", "can_cu_he_so", "nguon"],
              "gia_tai_nguyen": ["ma_tn", "ten_tn", "don_vi", "loai", "vung", "don_gia", "nguon", "ngay_ap_dung", "khu_vuc", "ty_le_luong"],
              "khoi_luong": ["stt", "hang_muc", "ma_hieu", "cap_phoi", "ten_cong_tac", "don_vi", "doan", "khoi_luong", "quy_doi", "he_so_vl", "he_so_nc",
                             "he_so_m", "can_cu_he_so", "don_gia_tron_goi", "dien_giai", "nguon_ban_ve", "trang_thai"]}[mp["loai_file"]]
    co_dinh = mp.get("gia_tri_co_dinh", {})
    anh_loai = mp.get("anh_xa_loai", {})
    out, cha = [], {}
    for r in rows[hdr_i + 1:]:
        if r is None or all(c is None or str(c).strip() == "" for c in r):
            continue
        d = {c: "" for c in cot_ra}
        for chuan, i in idx.items():
            v = r[i] if i < len(r) else None
            d[chuan] = "" if v is None else str(v).strip()
        if mp.get("kieu") == "phan_cap" and mp["loai_file"] == "dinh_muc":
            if d.get("ma_hieu") and not d.get("ma_tn"):
                cha = {k: d[k] for k in ("ma_hieu", "ten_cong_tac", "don_vi")}
                continue
            for k, v in cha.items():
                if not d.get(k):
                    d[k] = v
        if "loai" in d and d["loai"] in anh_loai:
            d["loai"] = anh_loai[d["loai"]]
        for k, v in co_dinh.items():
            if not d.get(k):
                d[k] = v
        out.append(d)
    with open(a.ra, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot_ra)
        w.writeheader()
        w.writerows(out)
    print(f"Đã ghi {len(out)} dòng vào {a.ra}. Chạy kiemtra-dulieu và đối chiếu ngẫu nhiên với văn bản gốc.")
    return 0


def cmd_can_gia(a):
    """Liệt kê tài nguyên mà khối lượng của hồ sơ thực sự dùng, × từng vùng giá, giữ giá đã có (nếu có)."""
    dl = DuLieu(a.data)
    kl = nap_khoi_luong(a.khoi_luong)
    cfg = nap_config(a.config) if a.config else {}
    ap_cap_phoi(dl, kl)
    ma_dung = {r["ma_hieu"] for r in kl if r["ma_hieu"] in dl.dinh_muc and r.get("dg_tg") is None}
    khong_co = sorted({r["ma_hieu"] for r in kl if r["ma_hieu"] not in dl.dinh_muc and r.get("dg_tg") is None})
    vung = [v["id"] for v in (cfg or {}).get("vung", []) or []] or dl.cac_vung() or [""]
    dung_o, co_hp = defaultdict(set), set()
    for ma in ma_dung:
        for h in dl.dinh_muc[ma]["hao_phi"]:
            if h["ma_tn"]:
                dung_o[h["ma_tn"]].add(ma.split("+")[0])
                if abs(h["hao_phi"] * h["he_so"]) > 1e-12:
                    co_hp.add(h["ma_tn"])
    tn = {m: h for m, h in dl.tai_nguyen_dung(ma_dung).items() if m in co_hp}  # bỏ tài nguyên hao phí = 0 ở mọi mã
    thu_tu = {"VL": 0, "NC": 1, "M": 2}
    cot = ["ma_tn", "ten_tn", "don_vi", "loai", "vung", "don_gia", "nguon", "ngay_ap_dung", "khu_vuc", "ty_le_luong", "dung_o_ma"]
    out, thieu, dien = [], 0, 0
    tc = nhan_cong_tham_chieu() if a.nhan_cong else {}
    vnc = vung_nhan_cong(cfg)
    for m, h in sorted(tn.items(), key=lambda x: (thu_tu.get(x[1]["loai"], 9), bo_dau(x[0]))):
        for v in vung:
            g = dl.gia_cua(m, v)
            if (not g or not g["don_gia"]) and h["loai"] == "NC" and v in vnc and (vnc[v], khoa_ten(m)) in tc:
                r = tc[(vnc[v], khoa_ten(m))]
                g = {"don_gia": float(r["don_gia"]), "nguon": f"{r['van_ban']} ngày {r['ngay_van_ban']} — {r['ten_vung']}",
                     "ngay": r["ngay_van_ban"], "khu_vuc": r["ten_vung"], "ty_le_luong": None}
                dien += 1
            if not g or not g["don_gia"]:
                thieu += 1
            out.append({"ma_tn": m, "ten_tn": h["ten_tn"] or m, "don_vi": h["don_vi_tn"], "loai": h["loai"], "vung": v,
                        "don_gia": f"{g['don_gia']:g}" if g and g["don_gia"] else "",
                        "nguon": g["nguon"] if g else "", "ngay_ap_dung": g["ngay"] if g else "",
                        "khu_vuc": g["khu_vuc"] if g else "", "ty_le_luong": (f"{g['ty_le_luong']:g}" if g and g["ty_le_luong"] is not None else ""),
                        "dung_o_ma": " ".join(sorted(dung_o[m]))})
    with open(a.ra, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot)
        w.writeheader()
        w.writerows(out)
    print(f"{len(tn)} tài nguyên × {len(vung)} vùng = {len(out)} dòng; {thieu} dòng chưa có giá"
          + (f"; điền sẵn {dien} giá nhân công từ văn bản Sở XD (data/nhan-cong)" if dien else "") + f". Đã ghi {a.ra}")
    if a.nhan_cong and not vnc:
        print("[CHÚ Ý] --nhan-cong: config chưa gán vùng nhân công — thêm \"nhan_cong\": \"HN-V1-KV1\" (HY-V2, HP-V1…) vào từng vùng")
    if khong_co:
        print(f"[CHÚ Ý] {len(khong_co)} mã trong khối lượng không có trong dữ liệu định mức: " + ", ".join(khong_co[:20]))
    print("Điền don_gia (chưa GTGT), nguon (số/ngày công bố của Sở XD), ngay_ap_dung (yyyy-mm-dd) theo công bố giá kỳ hiện hành, "
          "lưu thành gia_tai_nguyen.csv trong thư mục hồ sơ rồi chạy soat. Tên ma_tn giữ nguyên như TT 38.")
    return 0


BAC_TT36 = {  # lệnh ty-le --bang <khoá>: (đường dẫn trong bang_ty_le_tt36_2026.json, tên bảng)
    "ks-chung": (("pl_v_khao_sat", "bang_5_1_chi_phi_chung_tren_nc"), "Bảng 5.1 PL V TT 36 — chi phí chung khảo sát (% × NC)"),
    "ks-khong-xd-kl": (("pl_v_khao_sat", "bang_5_2_khong_xd_kl_tren_t"), "Bảng 5.2 PL V TT 36 — chi phí không xác định được KL (% × T)"),
    "ks-phuong-an": (("pl_v_khao_sat", "bang_5_3_lap_phuong_an_ks"), "Bảng 5.3 PL V TT 36 — lập phương án kỹ thuật khảo sát (% × (T+GT+TL))"),
    "ks-bao-cao": (("pl_v_khao_sat", "bang_5_3_lap_bao_cao_ks"), "Bảng 5.3 PL V TT 36 — lập báo cáo kết quả khảo sát (% × (T+GT+TL))"),
    "tv-quan-ly": (("pl_vi_tu_van", "bang_6_1_chi_phi_quan_ly_tren_cg"), "Bảng 6.1 PL VI TT 36 — chi phí quản lý trong dự toán tư vấn (% × chi phí chuyên gia)"),
    "tb-quan-ly-mua-sam": (("bang_2_3_quan_ly_mua_sam_thiet_bi",), "Bảng 2.3 PL II TT 36 — quản lý mua sắm thiết bị nhập khẩu (% × chi phí mua sắm)"),
}


def tra_bac(t, gia_tri):
    for i, (n, ss) in enumerate(zip(t["nac"], t["so_sanh"])):
        if n is None or (gia_tri < n if ss == "lt" else gia_tri <= n):
            return t["ty_le"][i], i
    return t["ty_le"][-1], len(t["ty_le"]) - 1


def cmd_ty_le(a):
    if a.bang in BAC_TT36:
        from dutoan_core import BANG_TY_LE
        with open(BANG_TY_LE, encoding="utf-8") as f:
            t = json.load(f)
        duong, ten = BAC_TT36[a.bang]
        for k in duong:
            t = t[k]
        v, i = tra_bac(t, a.gia_tri)
        moc = " / ".join(f"{'<' if ss == 'lt' else '≤'} {n:g}" if n is not None else "còn lại" for n, ss in zip(t["nac"], t["so_sanh"]))
        print(f"{ten}\nCơ sở: {t['_co_so']} = {a.gia_tri:g} → nấc {i + 1} ({moc}) → {v:g}%")
        print(f"Chi phí ≈ {fmt(a.gia_tri * 1e9 * v / 100)} đ")
        return 0
    if not a.loai:
        print("Cần --loai cho bảng qlda / ql-chu-so-huu")
        return 2
    with open(BANG_TY_LE_TT40, encoding="utf-8") as f:
        b = json.load(f)
    bang = {"qlda": "pl8_tt38_bang_1_1_qlda", "ql-chu-so-huu": "bang_4_quan_ly_chu_so_huu"}[a.bang]
    t = b[bang]
    if a.loai not in t:
        print(f"Loại '{a.loai}' không có. Chọn: " + ", ".join(k for k in t if not k.startswith("_") and isinstance(t[k], list) and k != "moc_ty_dong"))
        return 2
    nt, gc = noi_suy(t["moc_ty_dong"], t[a.loai], a.gia_tri)
    hs = 1.0
    for x in a.he_so or []:
        hs *= x
    nguon = "Bảng 1.1 PL VIII TT 38/2026" if a.bang == "qlda" else "Bảng 4 PL IV TT 40/2026"
    print(f"{nguon} · loại {a.loai} · quy mô {a.gia_tri:g} tỷ → Nt = {nt:.4f}% ({gc})")
    if hs != 1.0:
        print(f"Hệ số điều chỉnh: {' × '.join(f'{x:g}' for x in a.he_so)} = {hs:g} → tỷ lệ áp dụng {nt*hs:.4f}%")
    gt = a.gia_tri * 1e9 * nt * hs / 100
    if a.bang == "ql-chu-so-huu" and gt < t["toi_thieu_dong"]:
        print(f"Giá trị {fmt(gt)} đ < mức tối thiểu {fmt(t['toi_thieu_dong'])} đ → lấy {fmt(t['toi_thieu_dong'])} đ")
        gt = t["toi_thieu_dong"]
    print(f"Chi phí ≈ {fmt(gt)} đ (trên quy mô {a.gia_tri:g} tỷ, chưa GTGT)")
    if a.bang == "ql-chu-so-huu":
        print("Lưu ý: TT 40 không ghi công thức nội suy cho Bảng 4 — skill nội suy tuyến tính như PL VIII TT 38; xác nhận trước khi dùng.")
    else:
        print("Hệ số PL VIII Chương I: biển/đảo/biên giới/xã ĐBKK 1,35 · tuyến ≥ 2 tỉnh 1,1 · CĐT tự thực hiện QLDA 0,8 · thiết bị ≥ 50% 0,8. "
              "Chưa gồm chi phí CĐT trực tiếp thẩm định (tính bổ sung: 80% chi phí thẩm tra tương ứng).")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="lenh", required=True)
    s = sp.add_parser("kiemtra-dulieu"); s.add_argument("--data", required=True); s.set_defaults(f=cmd_kiemtra)
    s = sp.add_parser("tra"); s.add_argument("--data", default="."); s.add_argument("--ma", nargs="+")
    s.add_argument("--tu-khoa"); s.add_argument("--chuong", action="store_true"); s.add_argument("--gioi-han", type=int, default=30)
    s.add_argument("--cap-phoi", help="Tra mã cấp phối vữa theo từ khoá, vd. 'PCB 40 6 ÷ 8 dmax = 20mm 250'")
    s.add_argument("--tai-nguyen", help="Tra danh mục tài nguyên TT 38 (vật liệu, nhân công, máy) theo từ khoá; '' = tất cả")
    s.add_argument("--loai", help="Lọc loại tài nguyên: VL | NC | M")
    s.add_argument("--ly-trinh", help="Tra xã/phường, tỉnh, vùng nhân công theo lý trình tuyến cao tốc HN–HP, vd. Km36+200")
    s.set_defaults(f=cmd_tra)
    s = sp.add_parser("soat"); s.add_argument("--data", required=True); s.add_argument("--khoi-luong", required=True)
    s.add_argument("--config"); s.set_defaults(f=cmd_soat)
    s = sp.add_parser("tinh"); s.add_argument("--data", required=True); s.add_argument("--khoi-luong", required=True)
    s.add_argument("--config", required=True); s.add_argument("--out", required=True)
    s.add_argument("--nhap", action="store_true", help="Xuất bản nháp dù còn mục chặn"); s.set_defaults(f=cmd_tinh)
    s = sp.add_parser("can-gia"); s.add_argument("--data", required=True); s.add_argument("--khoi-luong", required=True)
    s.add_argument("--config"); s.add_argument("--ra", required=True)
    s.add_argument("--nhan-cong", action="store_true", help="Điền sẵn giá nhân công từ văn bản chuyển đổi của Sở XD (data/nhan-cong) theo vùng khai trong config")
    s.set_defaults(f=cmd_can_gia)
    s = sp.add_parser("ty-le"); s.add_argument("--bang", required=True, choices=["qlda", "ql-chu-so-huu"] + list(BAC_TT36))
    s.add_argument("--loai", help="qlda, ql-chu-so-huu: dan_dung | cong_nghiep | giao_thong | nn_mt | htkt")
    s.add_argument("--gia-tri", type=float, required=True, help="Quy mô làm cơ sở tra bảng (tỷ đồng, chưa GTGT)")
    s.add_argument("--he-so", type=float, nargs="*", help="Các hệ số điều chỉnh, vd. 0.8")
    s.set_defaults(f=cmd_ty_le)
    s = sp.add_parser("chuyendoi"); s.add_argument("--nguon", required=True); s.add_argument("--anh-xa", required=True)
    s.add_argument("--ra", required=True); s.set_defaults(f=cmd_chuyendoi)
    a = p.parse_args()
    sys.exit(a.f(a))


if __name__ == "__main__":
    main()
