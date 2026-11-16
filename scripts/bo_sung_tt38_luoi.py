#!/usr/bin/env python3
"""Bổ sung / sửa dữ liệu TT 38 bằng bộ đọc theo lưới ô (doc_bang_luoi.py).

Quy tắc gộp (an toàn trước):
  1. Mã chưa có trong dữ liệu → thêm.
  2. Mã trong ma_can_kiem_tra → thay bằng bản đọc lại nếu bản mới chứa đủ các số liệu của bản cũ; gỡ khỏi danh sách.
  3. Mã đang có, số liệu (bỏ qua tên, loại) giống hệt → lấy tên tài nguyên và loại từ bản mới (sửa tên, nhóm nhân công, VLK/MK).
  4. Còn lại (số liệu khác) → giữ bản cũ, đưa vào ma_can_kiem_tra kèm mô tả chênh lệch.
Bảng một khối mã không đọc được → liệt kê trong báo cáo.

  python scripts/bo_sung_tt38_luoi.py --file Phu_luc.docx --data data/tt38 [--ghi]
"""
import argparse, collections, csv, gzip, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nhap_tt38_doc as N  # noqa: E402
import doc_bang_luoi as G  # noqa: E402


# Mã đã đối chiếu tay với văn bản: bản đọc theo lưới đúng hơn bản trích cũ (bản cũ sót dòng vữa, nhân công 0,4 thay vì 0,74)
UU_TIEN_LUOI = {"AF.31310"}


def doc_csv_gz(p):
    return list(csv.DictReader(gzip.open(p, "rt", encoding="utf-8")))


def ghi_csv_gz(p, rows, cot):
    with gzip.open(p, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cot); w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--file", required=True); ap.add_argument("--data", required=True)
    ap.add_argument("--ghi", action="store_true"); a = ap.parse_args()
    d = N.mo_docx(a.file)
    p_dm, p_kt, p_dm_ma = (os.path.join(a.data, x) for x in ("dinh_muc_tt38.csv.gz", "ma_can_kiem_tra.csv.gz", "danh_muc_ma_tt38.csv.gz"))
    dm = doc_csv_gz(p_dm); cot = list(dm[0].keys())
    by = collections.OrderedDict()
    for r in dm: by.setdefault(r["ma_hieu"], []).append(r)
    kt = {r["ma_hieu"]: r["ly_do"] for r in doc_csv_gz(p_kt)}
    dmm = doc_csv_gz(p_dm_ma); cot_m = list(dmm[0].keys()); dm_ma = {r["ma_hieu"]: r for r in dmm}
    pl, chuong, nhom, nhom_ten, dvt = "", "", "", "", ""
    moi, loi_bang = {}, []
    for k, v in N.luong(d):
        if k == "p":
            t = N.chuan(v)
            if not t: continue
            m = N.RE_PL.search(t)
            if m: pl = m.group(1).upper(); chuong = ""
            m = N.RE_CHUONG.match(t)
            if m: chuong = m.group(1).upper()
            m = N.RE_NHOM.match(t)
            if m: nhom, nhom_ten = m.group(1), m.group(2)
            m = N.RE_DVT.search(t)
            if m: dvt = m.group(1).strip()
            continue
        if pl in ("", "VII", "VIII") or not v or not v[0] or "mã hiệu" not in N.chuan(v[0][0] if v[0] else "").lower():
            continue
        p, kq, ly = G.doc(v)
        if not kq:
            if p and "nhiều khối mã" not in ly and not any(x.startswith(p) for x in by):
                loi_bang.append(f"PL {pl} · {p} ({nhom} {nhom_ten[:50]}) — {ly}")
            continue
        ten_ct = N.chuan(v[[i for i, r in enumerate(v) if G.RE_MA.match(re.sub(r'\s', '', r[0] or ''))][0]][1])
        for h, lst in kq.items():
            moi.setdefault(p + h, dict(lst=lst, pl=pl, chuong=chuong, nhom=nhom, nhom_ten=nhom_ten, dvt=dvt, ten=ten_ct))
    ten_pl = N.TEN_PL
    def dong_moi(ma, e):
        return [{**{c: "" for c in cot}, "ma_hieu": ma, "ten_cong_tac": (by[ma][0]["ten_cong_tac"] if ma in by else e["ten"]),
                 "don_vi": (by[ma][0]["don_vi"] if ma in by else e["dvt"]), "loai": lo, "ma_tn": "" if lo in ("VLK", "MK") else t,
                 "ten_tn": t, "don_vi_tn": dv, "hao_phi": f"{x:g}", "he_so": "1", "can_cu_he_so": "",
                 "nguon": f"TT38/2026 {ten_pl.get(e['pl'], e['pl'])}", "phu_luc": e["pl"], "chuong": e["chuong"]} for lo, t, dv, x in e["lst"]]
    them, thay_kt, sua_ten, lech, giu_kt = [], [], [], [], []
    for ma, e in moi.items():
        so_moi = sorted(round(x, 6) for _, _, _, x in e["lst"])
        if ma not in by:
            by[ma] = dong_moi(ma, e); them.append(ma)
            dm_ma[ma] = {**{c: "" for c in cot_m}, "ma_hieu": ma, "ten_cong_tac": e["ten"], "don_vi": e["dvt"], "phu_luc": e["pl"],
                         "chuong": e["chuong"], "nhom": e["nhom"], "tieu_de_nhom": e["nhom_ten"]}
            continue
        so_cu = sorted(round(float(r["hao_phi"]), 6) for r in by[ma])
        if ma in kt:
            c = collections.Counter(so_moi); c.subtract(collections.Counter(so_cu))
            if all(v >= 0 for v in c.values()):
                by[ma] = dong_moi(ma, e); thay_kt.append(ma); kt.pop(ma)
            else:
                giu_kt.append(ma)
            continue
        if ma in UU_TIEN_LUOI:
            by[ma] = dong_moi(ma, e); sua_ten.append(ma); continue
        if so_moi == so_cu:
            cu = sorted((r["loai"], r["ten_tn"]) for r in by[ma]); mo = sorted((lo, t) for lo, t, _, _ in e["lst"])
            if cu != mo:
                by[ma] = dong_moi(ma, e); sua_ten.append(ma)
        else:
            lech.append(ma)
            kt.setdefault(ma, "Đọc lại theo lưới ô cho số liệu khác bản trích — đối chiếu văn bản")
    print(f"Mã đọc theo lưới: {len(moi)} · thêm mới {len(them)} · thay mã cần kiểm tra {len(thay_kt)} (còn giữ {len(giu_kt)}) · "
          f"sửa tên/loại {len(sua_ten)} · số liệu lệch → kiểm tra {len(lech)} · bảng một khối không đọc được {len(loi_bang)}")
    bc = ["# Bổ sung TT 38 bằng bộ đọc theo lưới ô", "",
          f"- Thêm mới {len(them)} mã: " + ", ".join(them), f"- Thay {len(thay_kt)} mã trong danh sách cần kiểm tra: " + ", ".join(thay_kt),
          f"- Sửa tên tài nguyên / loại (số liệu không đổi) {len(sua_ten)} mã: " + ", ".join(sua_ten),
          f"- Số liệu khác bản trích, giữ bản cũ và đưa vào danh sách kiểm tra {len(lech)} mã: " + ", ".join(lech),
          f"- Mã cần kiểm tra đọc lại được nhưng thiếu số liệu so với bản cũ (giữ nguyên) {len(giu_kt)}: " + ", ".join(giu_kt), "",
          "## Bảng một khối mã chưa đọc được (mã chưa có trong dữ liệu — tra văn bản)"] + [f"- {x}" for x in loi_bang]
    if not a.ghi:
        print("\n".join(bc[:8])); return
    ghi_csv_gz(p_dm, [r for rs in by.values() for r in rs], cot)
    ghi_csv_gz(p_kt, [{"ma_hieu": m, "ly_do": l} for m, l in sorted(kt.items())], ["ma_hieu", "ly_do"])
    ghi_csv_gz(p_dm_ma, list(dm_ma.values()), cot_m)
    open(os.path.join(a.data, "bao_cao_bo_sung_luoi.md"), "w", encoding="utf-8").write("\n".join(bc) + "\n")
    print("Đã ghi.")


if __name__ == "__main__":
    main()
