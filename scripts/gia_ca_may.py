#!/usr/bin/env python3
"""Tính giá ca máy theo Phụ lục IV Thông tư 37/2026/TT-BXD.

  python gia_ca_may.py --dinh-muc data/gia-ca-may/dinh_muc_ca_may_tt37.csv \
      --ma-vung HN-V1-KV1 --gia-diezel 20000 --gia-xang 21000 --gia-dien 2000 \
      --ra data/gia-ca-may/gia_ca_may.csv

Công thức PL IV (mục III, đã đối chiếu nguyên văn TT 37/2026):
  (4.1) CCM  = CKH + CSC + CNL + CNC + CCPK
  (4.2) CKH  = (G - GTH) x ĐKH / NCA;  GTH = 10% x G nếu G >= 30.000.000 đ, ngược lại 0
  (4.3) CSC  = G x ĐSC / NCA
  (4.4) CNL  = Σ ĐNLi x GNLi x KPi   (KP mặc định: xăng 1,02; diezel 1,03; điện 1,05)
  (4.5) CNC  = Σ Ni x CTLi           (số nhân công vận hành x đơn giá ngày công)
  (4.6) CCPK = G x ĐK / NCA
  Giá chờ đợi (mục II.3): 0,5 x CKH + 0,5 x CNC + CCPK.
  Giá điều chỉnh CCMĐC: giá ca máy tính lại theo giá nhiên liệu và tiền lương tại thời điểm điều
  chỉnh (CKH/CSC/CCPK không đổi vì chỉ phụ thuộc nguyên giá và định mức %/năm). Cho giá mới bằng
  --gia-*-moi / --ma-vung-moi thì cột gia_ca_may_dieu_chinh = CCM tính theo giá mới; nếu không cho
  giá mới thì CCMĐC = CCM.
  ĐKH, ĐSC nhân 1,05 với máy làm việc ở vùng nước mặn/nước lợ/môi trường ăn mòn cao (--an-mon).

Đầu vào:
- File định mức ca máy (CSV): ma_may, ten_may, nguyen_gia (đồng), so_ca_nam, dm_khau_hao (%/năm),
  dm_sua_chua (%/năm), dm_chi_phi_khac (%/năm), dm_tieu_hao_nl, loai_nl (diezel/xang/dien),
  he_so_nl_phu, nhan_cong_van_hanh ("1 nhân công vận hành", "2 nhân công vận hành", "1 lái xe"…),
  cong_thuc_nl (tuỳ chọn, dạng GXD: "16*diezel*1,03+5*xang*1,02" — dùng cho máy nhiều nhiên liệu),
  nguon. Máy chưa có nguyên giá hoặc định mức thì bỏ qua kèm cảnh báo (không bịa số liệu).
- Giá nhiên liệu tại thời điểm tính: --gia-diezel / --gia-xang / --gia-dien (đồng/lít, đồng/kWh).
  Giá nhân công vận hành: lấy từ data/nhan-cong/gia_nhan_cong_chuyen_doi_2026.csv theo --ma-vung
  ("Nhân công vận hành máy, điều khiển máy" cho "nhân công vận hành", "Lái xe" cho "lái xe"),
  hoặc ghi đè bằng --gia-van-hanh / --gia-lai-xe. Thành phần nhân công khác (thuyền trưởng,
  thủy thủ, thợ máy…) chưa hỗ trợ ở v2.0 — máy đó được tính thiếu CNC và ghi rõ trong báo cáo.

Đầu ra: file CSV dùng được làm gia_tai_nguyen.csv cho loại M (cột ma_tn, ten_tn, don_vi, loai, vung,
don_gia, nguon, ngay_ap_dung, khu_vuc, ty_le_luong) + các cột thành phần ckh, csc, cnl, cnc, ccpk,
gia_ca_may_cho_doi, gia_ca_may_dieu_chinh để đối chiếu. ty_le_luong = CNC / CCM (dùng tính Km).
Mọi khoản đều làm tròn đến đồng (ROUND nửa xa số 0, như Excel).
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dutoan_core import doc_csv, so, xround  # noqa: E402

SKILL_ROOT = os.path.dirname(HERE)
NHAN_CONG = os.path.join(SKILL_ROOT, "data", "nhan-cong", "gia_nhan_cong_chuyen_doi_2026.csv")

KP_MAC_DINH = {"xang": 1.02, "diezel": 1.03, "dien": 1.05}
TEN_NL = {"diezel": "diezel", "dau": "diezel", "xang": "xang", "dien": "dien", "kwh": "dien"}


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


def gia_nhan_cong(ma_vung):
    """{(tên nhóm): đơn giá ngày công} theo mã vùng trong bảng giá nhân công chuyển đổi."""
    out = {}
    for r in doc_csv(NHAN_CONG) or []:
        if r.get("ma_vung") == ma_vung:
            out[r.get("ten_tn", "")] = so(r.get("don_gia"))
    return out


def phan_tich_nhan_cong(text):
    """'1 nhân công vận hành + 1 lái xe' -> [('van_hanh', 1), ('lai_xe', 1)].
    Chỉ nhận hai loại đã có giá trong bảng nhân công; loại khác trả về ('khac', n, tên)."""
    out = []
    for part in (text or "").split("+"):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"(\d+)\s+(.+)", part)
        if not m:
            out.append(("khac", 0, part))
            continue
        n, loai = int(m.group(1)), m.group(2).strip().lower()
        if "lai xe" in loai:
            out.append(("lai_xe", n, part))
        elif "van hanh" in loai or "vận hành" in loai:
            out.append(("van_hanh", n, part))
        else:
            out.append(("khac", n, part))
    return out


def phan_tich_cong_thuc_nl(text):
    """'16*diezel*1,03+5*xang*1,02' -> [(16, 'diezel', 1.03), (5, 'xang', 1.02)]."""
    out = []
    for part in (text or "").split("+"):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"([\d.,]+)\s*\*\s*([a-zA-Z]+)\s*\*\s*([\d.,]+)", part)
        if not m:
            return None
        out.append((so(m.group(1)), TEN_NL.get(m.group(2).lower(), m.group(2).lower()), so(m.group(3))))
    return out or None


def tinh_may(r, gia_nl, gia_nc, an_mon=False, gia_nl_moi=None, gia_nc_moi=None):
    """Tính một máy. Trả (dict kết quả, list cảnh báo). None = thiếu dữ liệu, bỏ qua máy."""
    canh_bao = []
    g = so(r.get("nguyen_gia"))
    nca = so(r.get("so_ca_nam"))
    if g is None or nca is None or nca == 0:
        return None, [f"{r.get('ma_may')}: thiếu nguyên giá hoặc số ca/năm — bỏ qua"]
    dkh = so(r.get("dm_khau_hao"), 0) / 100
    dsc = so(r.get("dm_sua_chua"), 0) / 100
    dk = so(r.get("dm_chi_phi_khac"), 0) / 100
    if an_mon:
        dkh, dsc = dkh * 1.05, dsc * 1.05
    gth = g * 0.10 if g >= 30_000_000 else 0.0
    ckh = (g - gth) * dkh / nca
    csc = g * dsc / nca
    ccpk = g * dk / nca
    # nhiên liệu
    nl = []
    ct = (r.get("cong_thuc_nl") or "").strip()
    if ct:
        nl = phan_tich_cong_thuc_nl(ct)
        if nl is None:
            return None, [f"{r.get('ma_may')}: công thức nhiên liệu không đọc được ({ct!r}) — bỏ qua"]
    else:
        dm = so(r.get("dm_tieu_hao_nl"), 0) or 0
        loai = TEN_NL.get((r.get("loai_nl") or "").strip().lower(), "")
        if dm and not loai:
            return None, [f"{r.get('ma_may')}: có định mức tiêu hao ({dm:g}) nhưng không rõ loại nhiên liệu — bỏ qua"]
        kp = so(r.get("he_so_nl_phu")) or KP_MAC_DINH.get(loai)
        if dm:
            nl = [(dm, loai, kp)]

    def _cnl(gia):
        tong = 0.0
        for dm_nl, loai, kp in nl:
            gv = gia.get(loai)
            if gv is None:
                return None
            tong += dm_nl * gv * kp
        return tong

    cnl = _cnl(gia_nl)
    if cnl is None:
        loai_thieu = next(loai for _, loai, _ in nl if gia_nl.get(loai) is None)
        return None, [f"{r.get('ma_may')}: thiếu giá nhiên liệu {loai_thieu} — chạy lại với --gia-{loai_thieu}"]
    # nhân công
    thanh_phan_nc = phan_tich_nhan_cong(r.get("nhan_cong_van_hanh", ""))

    def _cnc(gia):
        tong = 0.0
        for kind, n, ten in thanh_phan_nc:
            if kind == "khac":
                continue
            gv = gia.get(kind)
            if gv is None:
                return None
            tong += n * gv
        return tong

    cnc = _cnc(gia_nc)
    if cnc is None:
        return None, [f"{r.get('ma_may')}: thiếu giá nhân công ở vùng đã chọn — kiểm tra --ma-vung"]
    for kind, n, ten in thanh_phan_nc:
        if kind == "khac":
            canh_bao.append(f"{r.get('ma_may')}: thành phần nhân công {ten!r} chưa hỗ trợ ở v2.0 — CNC tính thiếu phần này")
    # Làm tròn từng khoản về đồng TRƯỚC rồi mới cộng (quy ước "làm tròn từng bước" của skill):
    # CCM, giá chờ đợi, CCMĐC in ra luôn bằng đúng tổng các thành phần đã làm tròn.
    R = lambda x: int(xround(x))
    ckh_r, csc_r, cnl_r, cnc_r, ccpk_r = R(ckh), R(csc), R(cnl), R(cnc), R(ccpk)
    ccm_r = ckh_r + csc_r + cnl_r + cnc_r + ccpk_r
    cho_doi_r = R(0.5 * ckh_r + 0.5 * cnc_r + ccpk_r)
    # CCMĐC: CKH/CSC/CCPK giữ nguyên, chỉ CNL/CNC tính lại theo giá mới
    dieu_chinh_r = ccm_r
    if gia_nl_moi is not None or gia_nc_moi is not None:
        cnl_moi = _cnl(gia_nl_moi or {})
        cnc_moi = _cnc(gia_nc_moi or {})
        if cnl_moi is None or cnc_moi is None:
            canh_bao.append(f"{r.get('ma_may')}: thiếu giá mới (nhiên liệu/nhân công) nên CCMĐC = CCM — "
                            f"cho đủ --gia-*-moi và --ma-vung-moi để tính giá điều chỉnh")
        else:
            dieu_chinh_r = ckh_r + csc_r + R(cnl_moi) + R(cnc_moi) + ccpk_r
    return {"ma_may": r.get("ma_may", ""), "ten_may": r.get("ten_may", ""), "nguyen_gia": g,
            "ckh": ckh_r, "csc": csc_r, "cnl": cnl_r, "cnc": cnc_r, "ccpk": ccpk_r,
            "ccm": ccm_r, "cho_doi": cho_doi_r, "dieu_chinh": dieu_chinh_r,
            "ty_le_luong": round(cnc_r / ccm_r, 6) if ccm_r else 0.0}, canh_bao


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dinh-muc", required=True, help="CSV định mức ca máy (xem docstring)")
    p.add_argument("--ma-vung", default="HN-V1-KV1", help="Mã vùng nhân công trong data/nhan-cong (mặc định HN-V1-KV1)")
    p.add_argument("--gia-diezel", type=float, help="Giá diezel đ/lít tại thời điểm tính")
    p.add_argument("--gia-xang", type=float, help="Giá xăng đ/lít tại thời điểm tính")
    p.add_argument("--gia-dien", type=float, help="Giá điện đ/kWh tại thời điểm tính")
    p.add_argument("--gia-van-hanh", type=float, help="Ghi đè đơn giá ngày công 'nhân công vận hành'")
    p.add_argument("--gia-lai-xe", type=float, help="Ghi đè đơn giá ngày công 'lái xe'")
    p.add_argument("--an-mon", action="store_true", help="Máy làm việc vùng nước mặn/nước lợ/môi trường ăn mòn cao (ĐKH, ĐSC x1,05)")
    p.add_argument("--gia-diezel-moi", type=float, help="Giá diezel mới (để tính CCMĐC)")
    p.add_argument("--gia-xang-moi", type=float, help="Giá xăng mới (để tính CCMĐC)")
    p.add_argument("--gia-dien-moi", type=float, help="Giá điện mới (để tính CCMĐC)")
    p.add_argument("--ma-vung-moi", help="Mã vùng nhân công mới (để tính CCMĐC; mặc định = --ma-vung)")
    p.add_argument("--ngay-ap-dung", default="", help="Ngày áp dụng giá (yyyy-mm-dd, ghi vào cột ngay_ap_dung)")
    p.add_argument("--khu-vuc", default="", help="Khu vực (ghi vào cột khu_vuc)")
    p.add_argument("--vung", default="", help="Mã vùng giá (trống = áp chung mọi vùng)")
    p.add_argument("--ra", required=True, help="File CSV đầu ra (dạng gia_tai_nguyen.csv cho loại M)")
    a = p.parse_args()
    rows = doc_csv(a.dinh_muc)
    if rows is None:
        sys.exit(f"Không thấy file định mức: {a.dinh_muc}")
    nc = gia_nhan_cong(a.ma_vung)
    gia_nc = {"van_hanh": a.gia_van_hanh if a.gia_van_hanh is not None else nc.get("Nhân công vận hành máy, điều khiển máy"),
              "lai_xe": a.gia_lai_xe if a.gia_lai_xe is not None else nc.get("Lái xe")}
    gia_nl = {"diezel": a.gia_diezel, "xang": a.gia_xang, "dien": a.gia_dien}
    gia_nl_moi = None
    gia_nc_moi = None
    if a.gia_diezel_moi is not None or a.gia_xang_moi is not None or a.gia_dien_moi is not None or a.ma_vung_moi:
        gia_nl_moi = {"diezel": a.gia_diezel_moi, "xang": a.gia_xang_moi, "dien": a.gia_dien_moi}
        nc_moi = gia_nhan_cong(a.ma_vung_moi or a.ma_vung)
        gia_nc_moi = {"van_hanh": nc_moi.get("Nhân công vận hành máy, điều khiển máy"),
                      "lai_xe": nc_moi.get("Lái xe")}
    kq, canh_bao = [], []
    for r in rows:
        k, cb = tinh_may(r, gia_nl, gia_nc, a.an_mon, gia_nl_moi, gia_nc_moi)
        canh_bao += cb
        if k is None:
            continue
        kq.append((r, k))
    with open(a.ra, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ma_tn", "ten_tn", "don_vi", "loai", "vung", "don_gia", "nguon", "ngay_ap_dung", "khu_vuc",
                    "ty_le_luong", "ckh", "csc", "cnl", "cnc", "ccpk", "gia_ca_may_cho_doi", "gia_ca_may_dieu_chinh"])
        for r, k in kq:
            nguon = (r.get("nguon") or "").strip()
            chi_tiet = f"Tính theo PL IV TT 37/2026 từ nguyên giá {fmt(k['nguyen_gia'])} đ"
            if a.gia_diezel:
                chi_tiet += f"; diezel {fmt(a.gia_diezel)} đ/lít"
            if a.gia_xang:
                chi_tiet += f"; xăng {fmt(a.gia_xang)} đ/lít"
            if a.gia_dien:
                chi_tiet += f"; điện {fmt(a.gia_dien)} đ/kWh"
            chi_tiet += f"; NC vận hành {a.ma_vung}"
            nguon = f"{nguon}; {chi_tiet}" if nguon else chi_tiet
            w.writerow([k["ma_may"], k["ten_may"], "ca", "M", a.vung, k["ccm"], nguon, a.ngay_ap_dung,
                        a.khu_vuc, f"{k['ty_le_luong']:.6f}", k["ckh"], k["csc"], k["cnl"], k["cnc"], k["ccpk"],
                        k["cho_doi"], k["dieu_chinh"]])
    print(f"Đã tính {len(kq)}/{len(rows)} máy → {a.ra}")
    for c in canh_bao:
        print(f"[CẢNH BÁO] {c}")
    for r, k in kq:
        print(f"  {k['ma_may']}: CKH {fmt(k['ckh'])} + CSC {fmt(k['csc'])} + CNL {fmt(k['cnl'])} + "
              f"CNC {fmt(k['cnc'])} + CCPK {fmt(k['ccpk'])} = CCM {fmt(k['ccm'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
