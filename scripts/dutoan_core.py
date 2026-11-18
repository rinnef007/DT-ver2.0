"""Lõi dữ liệu và tính toán cho Skill dự toán xây dựng Việt Nam.

Không chứa định mức hay đơn giá: mọi số liệu đọc từ file người dùng cung cấp.

Mô hình dữ liệu
- dinh_muc.csv: hao phí theo mã; cột tuỳ chọn `he_so` (hệ số từng dòng hao phí) và `can_cu_he_so`.
- gia_tai_nguyen.csv: giá theo tài nguyên; cột tuỳ chọn `vung` (trống = áp chung mọi vùng).
- khoi_luong.csv: cột tuỳ chọn `doan` (đoạn/xã). Một công tác có nhiều đoạn → nhiều dòng cùng `stt`.
- config_du_toan.json: tỷ lệ, VAT, `vung`, `doan` (đoạn → vùng giá), `lam_tron`, `mau_xuat`, `tong_hop`.
"""
import csv
import json
import math
import os
import re
import sys
import unicodedata
from collections import OrderedDict, defaultdict
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
BANG_TY_LE = os.path.join(SKILL_ROOT, "data", "bang_ty_le_tt36_2026.json")
BANG_TY_LE_TT40 = os.path.join(SKILL_ROOT, "data", "bang_ty_le_tt40_2026.json")
NHAN_CONG_TC = os.path.join(SKILL_ROOT, "data", "nhan-cong", "gia_nhan_cong_chuyen_doi_2026.csv")


def _ngay_iso(s):
    try:
        return datetime.strptime((s or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def con_hieu_luc(r, ngay):
    """Dòng giá nhân công còn hiệu lực tại `ngay` (hieu_luc_tu <= ngay <= hieu_luc_den; trống = không giới hạn)."""
    tu, den = _ngay_iso(r.get("hieu_luc_tu")), _ngay_iso(r.get("hieu_luc_den"))
    return (tu is None or tu <= ngay) and (den is None or ngay <= den)


def nhan_cong_tat_ca():
    """Mọi dòng giá nhân công tham chiếu (mọi văn bản, mọi kỳ)."""
    return doc_csv(NHAN_CONG_TC) or []


def nhan_cong_tham_chieu(ngay=None):
    """Giá nhân công theo văn bản Sở XD còn hiệu lực tại `ngay` — {(ma_vung, khoá tên): bản ghi}.

    `ngay` = None: lấy dòng đang hiệu lực hôm nay; mã vùng không còn dòng nào hiệu lực hôm nay thì
    giữ dòng có hieu_luc_tu muộn nhất (để tra cứu tên vùng, lịch sử)."""
    rows = nhan_cong_tat_ca()
    ngay_xet = ngay or date.today()
    out = {}
    for r in sorted(rows, key=lambda r: r.get("hieu_luc_tu") or ""):
        k = (r["ma_vung"], khoa_ten(r["ten_tn"]))
        if con_hieu_luc(r, ngay_xet):
            out[k] = r
        elif ngay is None and k not in out:
            out[k] = r
    return out


def ngay_ap_gia(cfg):
    """(ngày dùng để chọn văn bản giá, ghi chú). thoi_diem_ap_gia: yyyy-mm-dd, yyyy-mm (lấy ngày cuối tháng) hoặc trống (hôm nay)."""
    s = ((cfg or {}).get("thoi_diem_ap_gia") or "").strip()
    d = _ngay_iso(s)
    if d:
        return d, ""
    m = re.fullmatch(r"(\d{4})-(\d{1,2})", s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        nxt = date(y + (mo == 12), mo % 12 + 1, 1)
        return date.fromordinal(nxt.toordinal() - 1), f"thoi_diem_ap_gia '{s}' chỉ có tháng — lấy ngày cuối tháng"
    return date.today(), ("thoi_diem_ap_gia trống — lấy ngày hôm nay" if not s else f"thoi_diem_ap_gia '{s}' không đọc được (dùng yyyy-mm-dd) — lấy ngày hôm nay")


def vung_nhan_cong(cfg):
    """{mã vùng giá của hồ sơ: mã vùng nhân công tham chiếu} từ cfg['vung'][i]['nhan_cong']."""
    return {v["id"]: v["nhan_cong"] for v in (cfg or {}).get("vung", []) or [] if v.get("nhan_cong")}


CHE_DO = ("tt36", "tt40_bao_duong", "tt40_sua_chua", "tt36_khao_sat")


def che_do(cfg):
    """Chế độ xác định chi phí: tt36 (Bảng 3.8 PL III TT 36/2026, mặc định) hoặc tt40_bao_duong / tt40_sua_chua
    (dự toán chi phí thực hiện bảo dưỡng – Bảng 2.5 PL II, sửa chữa trong bảo trì – Bảng 3.2 PL III TT 40/2026)."""
    return (cfg or {}).get("che_do_chi_phi", "tt36")


def la_tt40(cfg):
    return che_do(cfg).startswith("tt40")


def la_khao_sat(cfg):
    """Dự toán chi phí khảo sát xây dựng (và thí nghiệm chuyên ngành) — PL V TT 36/2026, Bảng 5.4."""
    return che_do(cfg) == "tt36_khao_sat"


def noi_suy(moc, ty_le, gia_tri):
    """Nội suy tuyến tính Nt = Nb − (Nb − Na) × (Gt − Gb) / (Ga − Gb); ngoài khoảng lấy giá trị biên.
    Trả (Nt, ghi_chu)."""
    if gia_tri <= moc[0]:
        return ty_le[0], f"≤ {moc[0]:g} tỷ: lấy mốc đầu"
    if gia_tri >= moc[-1]:
        return ty_le[-1], f"≥ {moc[-1]:g} tỷ: lấy mốc cuối (ngoài bảng → xem xét lập dự toán)"
    for i in range(1, len(moc)):
        if gia_tri <= moc[i]:
            gb, ga, nb, na = moc[i - 1], moc[i], ty_le[i - 1], ty_le[i]
            nt = nb - (nb - na) * (gia_tri - gb) / (ga - gb)
            return nt, f"nội suy giữa {gb:g} tỷ ({nb:g}%) và {ga:g} tỷ ({na:g}%)"
    return ty_le[-1], ""
LOAI_HOP_LE = {"VL", "NC", "M", "VLK", "MK"}
DOAN_MAC_DINH = ""


# ----------------------------------------------------------------- tiện ích
_DAU_CU = {"oà": "òa", "oá": "óa", "oả": "ỏa", "oã": "õa", "oạ": "ọa", "oè": "òe", "oé": "óe", "oẻ": "ỏe", "oẽ": "õe", "oẹ": "ọe",
           "uỳ": "ủy", "uý": "úy", "uỷ": "ủy", "uỹ": "ũy", "uỵ": "ụy"}


def khoa_ten(x):
    """Khoá so khớp tên tài nguyên: bỏ khoảng trắng, hoa/thường, dấu ngoặc; thống nhất m³/m², kiểu bỏ dấu cũ (thuỷ → thủy).
    Giữ dấu phẩy, chấm (2,5kW ≠ 25kW)."""
    x = unicodedata.normalize("NFC", x or "").lower().replace("³", "3").replace("²", "2")
    x = re.sub(r"(oà|oá|oả|oã|oạ|oè|oé|oẻ|oẽ|oẹ|uỳ|uý|uỷ|uỹ|uỵ)(?=$|[^a-zà-ỹđ])", lambda m: _DAU_CU[m.group(1)], x)
    x = x.replace("uỷ", "ủy").replace("uý", "úy")
    return re.sub(r"[\s\u00a0()\[\]]+", "", x)


def bo_dau(s):
    s = unicodedata.normalize("NFD", str(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def so(x, mac_dinh=None):
    if x is None:
        return mac_dinh
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(" ", "")
    if s == "":
        return mac_dinh
    pct = s.endswith("%")
    if pct:
        s = s[:-1].strip()
    try:
        v = float(s)
    except ValueError:
        try:
            v = float(s.replace(".", "").replace(",", "."))
        except ValueError:
            return mac_dinh
    return v / 100 if pct else v


def xround(x, n=0):
    """Làm tròn như hàm ROUND của Excel (nửa xa số 0)."""
    if x is None:
        return 0.0
    k = 10 ** n
    q = abs(x) * k
    r = math.floor(q + 0.5 + 1e-9)
    return math.copysign(r / k, x) if r else 0.0


def quy_tac_nhan_cong_cn(cn_dir):
    out = []
    for r in doc_csv(os.path.join(cn_dir, "anh_xa_nhan_cong.csv")) or []:
        out.append(dict(r, re=re.compile(r["mau_ten"], re.I)))
    return out


def anh_xa_mot(qt, bo, ma, ten):
    """Quy tắc áp cho tên nhân công `ten` của mã `ma` thuộc bộ `bo` (tiền tố mã dài nhất thắng)."""
    ten0 = re.sub(r"\s+", " ", ten.replace(":", " ")).strip()
    ten0 = re.sub(r"^nhân công\s*[-–]\s*", "", ten0, flags=re.I)
    hop = [q for q in qt if q["bo"] == bo and ma.startswith(q["tien_to_ma"]) and q["re"].search(ten0)]
    if not hop:
        return None, None
    q = max(hop, key=lambda q: len(q["tien_to_ma"]))
    return q, q["re"].search(ten0)


def anh_xa_nhan_cong_cn(dl, cn_dir):
    """Đổi tên nhân công theo cấp bậc (định mức chuyên ngành) sang nhóm nhân công TT 37 Bảng 3.1.

    Hao phí giữ nguyên (TT 37 Điều 2 k3: chọn nhóm theo tính chất công tác, không quy đổi cấp bậc);
    "nhóm công" của QĐ 1595 nhân với số người trong nhóm. Nhiều cấp bậc cùng về một nhóm trong một mã thì cộng dồn."""
    qt = quy_tac_nhan_cong_cn(cn_dir)
    loi = []
    if not qt:
        return loi
    for ma in dl.bo_cn:
        d = dl.dinh_muc[ma]
        bo = d.get("phu_luc", "")
        moi = []
        for h in d["hao_phi"]:
            if h["loai"] != "NC":
                moi.append(h); continue
            q, m = anh_xa_mot(qt, bo, ma, h["ten_tn"])
            if not q:
                loi.append(f"{ma}: chưa có quy tắc nhóm cho '{h['ten_tn']}'"); moi.append(h); continue
            hs = 1.0
            if q["he_so"] == "n":
                so = sum(int(x) for x in m.groups() if x)
                if "nhóm" in h["don_vi_tn"].lower():
                    hs = float(so)
                elif so > 1:
                    loi.append(f"{ma}: '{h['ten_tn']}' ghi {so} người nhưng đơn vị '{h['don_vi_tn']}' — giữ hệ số 1")
            h2 = dict(h, ma_tn=q["ten_tn_gia"], ten_tn=q["ten_tn_gia"], don_vi_tn="công", hao_phi=h["hao_phi"] * hs,
                      ten_goc=h["ten_tn"], can_cu_nhom=q["can_cu"])
            cu = next((x for x in moi if x["loai"] == "NC" and x["ma_tn"] == h2["ma_tn"]), None)
            if cu:
                cu["hao_phi"] += h2["hao_phi"]; cu["ten_goc"] += " + " + h2["ten_goc"]
            else:
                moi.append(h2)
        d["hao_phi"] = moi
    return loi


def doc_csv(path):
    """Đọc CSV (hoặc CSV.gz nếu chỉ có bản nén)."""
    import gzip
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path = path + ".gz"
    if not os.path.exists(path):
        return None
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8-sig", newline="") as f:
        nfc = unicodedata.normalize
        return [{nfc("NFC", k.strip()): nfc("NFC", (v or "").strip()) for k, v in r.items() if k} for r in csv.DictReader(f)]


TT38_DIR = os.path.join(SKILL_ROOT, "data", "tt38")


def fmt(v):
    return f"{v:,.0f}".replace(",", ".")


# ----------------------------------------------------------------- dữ liệu
class DuLieu:
    """Bộ dữ liệu của hồ sơ + định mức TT 38/2026 dùng chung (data/tt38).

    Định mức của hồ sơ (dinh_muc.csv, nếu có) ưu tiên; mã không có thì lấy từ TT 38/2026 đã trích.
    """

    def __init__(self, thu_muc, dung_tt38=True):
        self.thu_muc = thu_muc
        self.loi, self.canh_bao = [], []
        dm = doc_csv(os.path.join(thu_muc, "dinh_muc.csv"))
        gia = doc_csv(os.path.join(thu_muc, "gia_tai_nguyen.csv"))
        if dm is None:
            dm = []
            if not dung_tt38:
                self.loi.append(f"Không thấy {thu_muc}/dinh_muc.csv")
        if gia is None:
            self.loi.append(f"Không thấy {thu_muc}/gia_tai_nguyen.csv")
            gia = []
        self.dinh_muc = OrderedDict()
        for i, r in enumerate(dm, start=2):
            ma = r.get("ma_hieu", "")
            loai = r.get("loai", "").upper()
            if not ma:
                self.loi.append(f"dinh_muc.csv dòng {i}: thiếu ma_hieu")
                continue
            if loai not in LOAI_HOP_LE:
                self.loi.append(f"dinh_muc.csv dòng {i} ({ma}): loai '{loai}' không hợp lệ (VL/NC/M/VLK/MK)")
                continue
            hp = so(r.get("hao_phi"))
            if hp is None:
                self.loi.append(f"dinh_muc.csv dòng {i} ({ma}): hao_phi không phải số")
                continue
            if loai in ("VL", "NC", "M") and not r.get("ma_tn"):
                self.loi.append(f"dinh_muc.csv dòng {i} ({ma}): thiếu ma_tn")
                continue
            if not r.get("nguon"):
                self.canh_bao.append(f"dinh_muc.csv dòng {i} ({ma}): thiếu nguồn")
            hs = so(r.get("he_so"), 1.0)
            if abs(hs - 1) > 1e-12 and not r.get("can_cu_he_so"):
                self.canh_bao.append(f"dinh_muc.csv dòng {i} ({ma}): hệ số {hs:g} chưa ghi căn cứ")
            d = self.dinh_muc.setdefault(ma, {"ten": r.get("ten_cong_tac", ""), "don_vi": r.get("don_vi", ""),
                                              "nguon": r.get("nguon", ""), "hao_phi": []})
            if d["don_vi"] != r.get("don_vi", "") and r.get("don_vi"):
                self.loi.append(f"dinh_muc.csv dòng {i} ({ma}): đơn vị không thống nhất trong cùng mã")
            d["hao_phi"].append({"loai": loai, "ma_tn": r.get("ma_tn", ""), "ten_tn": r.get("ten_tn", ""),
                                 "don_vi_tn": r.get("don_vi_tn", ""), "hao_phi": hp, "he_so": hs,
                                 "can_cu_he_so": r.get("can_cu_he_so", ""), "ly_do": r.get("ly_do", "").strip()})
        self.ma_rieng = set(self.dinh_muc)
        self.co_tt38 = False
        self.pl_tt38 = {}
        self.hp_tt38 = {}
        self.ma_can_kiem_tra = {r["ma_hieu"]: r["ly_do"] for r in (doc_csv(os.path.join(TT38_DIR, "ma_can_kiem_tra.csv")) or [])} if dung_tt38 else {}
        if dung_tt38:
            dm_tt38 = doc_csv(os.path.join(TT38_DIR, "dinh_muc_tt38.csv")) or []
            if not dm_tt38:
                # Dữ liệu trên repo chia thành 3 phần (dinh_muc_tt38_p1..p3.csv) vì
                # file gộp 13 MB vượt giới hạn kích thước khi đẩy lên GitHub.
                import glob
                for p in sorted(glob.glob(os.path.join(TT38_DIR, "dinh_muc_tt38_p*.csv"))):
                    dm_tt38 += doc_csv(p) or []
            if dm_tt38:
                self.co_tt38 = True
                for r in dm_tt38:
                    ma = r["ma_hieu"]
                    self.pl_tt38[ma] = r.get("phu_luc", "")
                    self.hp_tt38.setdefault(ma, []).append((r["loai"], r["ten_tn"], float(r["hao_phi"])))
                    if ma in self.ma_rieng:
                        continue
                    d = self.dinh_muc.setdefault(ma, {"ten": r["ten_cong_tac"], "don_vi": r["don_vi"], "nguon": r["nguon"], "hao_phi": [],
                                                      "phu_luc": r.get("phu_luc", "")})
                    d["hao_phi"].append({"loai": r["loai"], "ma_tn": r["ma_tn"], "ten_tn": r["ten_tn"], "don_vi_tn": r["don_vi_tn"],
                                         "hao_phi": float(r["hao_phi"]), "he_so": 1.0, "can_cu_he_so": ""})
        # Định mức chuyên ngành (data/chuyen-nganh/*/dinh_muc_*.csv): chỉ thêm mã chưa có trong hồ sơ và TT 38
        self.bo_cn, self.ma_kt_cn, self.ghi_chu_cn = {}, {}, {}
        if dung_tt38:
            import glob
            cn_dir = os.path.join(SKILL_ROOT, "data", "chuyen-nganh")
            for f in sorted(glob.glob(os.path.join(cn_dir, "*", "dinh_muc_*.csv"))):
                for r in doc_csv(f) or []:
                    ma = r["ma_hieu"]
                    if ma in self.ma_rieng or (ma in self.pl_tt38):
                        continue
                    self.bo_cn[ma] = r.get("nguon", "")
                    d = self.dinh_muc.setdefault(ma, {"ten": r["ten_cong_tac"], "don_vi": r["don_vi"], "nguon": r["nguon"], "hao_phi": [],
                                                      "phu_luc": r.get("phu_luc", "")})
                    d["hao_phi"].append({"loai": r["loai"], "ma_tn": r["ma_tn"], "ten_tn": r["ten_tn"], "don_vi_tn": r["don_vi_tn"],
                                         "hao_phi": float(r["hao_phi"]), "he_so": 1.0, "can_cu_he_so": ""})
            self.anh_xa_nc_loi = anh_xa_nhan_cong_cn(self, cn_dir) if getattr(self, "anh_xa_nc", True) else []
            for r in doc_csv(os.path.join(cn_dir, "ma_can_kiem_tra_chuyen_nganh.csv")) or []:
                self.ma_kt_cn.setdefault(r["ma_hieu"], []).append(r["ly_do"])
            for f in sorted(glob.glob(os.path.join(cn_dir, "*", "ghi_chu_*.csv"))):
                for r in doc_csv(f) or []:
                    self.ghi_chu_cn.setdefault(r["ma_hieu"], []).append(r["ghi_chu"])
        for ma, d in self.dinh_muc.items():
            if ma not in self.ma_rieng:
                continue
            seen = set()
            for h in d["hao_phi"]:
                key = (h["loai"], h["ma_tn"])
                if h["ma_tn"] and key in seen:
                    self.canh_bao.append(f"Mã {ma}: tài nguyên {h['ma_tn']} lặp lại")
                seen.add(key)
        # giá: (ma_tn, vung) -> bản ghi
        self.gia = OrderedDict()
        self.ten_tn = {}
        for i, r in enumerate(gia, start=2):
            ma = r.get("ma_tn", "")
            vung = r.get("vung", "")
            if not ma:
                self.loi.append(f"gia_tai_nguyen.csv dòng {i}: thiếu ma_tn")
                continue
            dg = so(r.get("don_gia"))
            if dg is None:
                self.loi.append(f"gia_tai_nguyen.csv dòng {i} ({ma}): don_gia không phải số")
                continue
            if (ma, vung) in self.gia:
                self.loi.append(f"gia_tai_nguyen.csv: {ma}{' vùng ' + vung if vung else ''} có nhiều giá — giữ một dòng cho mỗi (mã, vùng)")
                continue
            if not r.get("nguon") or not r.get("ngay_ap_dung"):
                self.canh_bao.append(f"gia_tai_nguyen.csv dòng {i} ({ma}): thiếu nguồn hoặc ngày áp dụng")
            self.gia[(ma, vung)] = {"ma": ma, "vung": vung, "ten": r.get("ten_tn", ""), "don_vi": r.get("don_vi", ""),
                                    "loai": r.get("loai", "").upper(), "don_gia": dg, "nguon": r.get("nguon", ""),
                                    "ngay": r.get("ngay_ap_dung", ""), "khu_vuc": r.get("khu_vuc", ""),
                                    "ty_le_luong": so(r.get("ty_le_luong")),
                                    "don_gia_goc": so(r.get("don_gia_goc"))}
            self.ten_tn.setdefault(ma, (r.get("ten_tn", ""), r.get("don_vi", ""), r.get("loai", "").upper()))

        # cấp phối vữa (PL VII TT 38/2026), tuỳ chọn
        self.cap_phoi = OrderedDict()
        cp = doc_csv(os.path.join(thu_muc, "cap_phoi.csv")) or []
        if dung_tt38:
            cp = cp + (doc_csv(os.path.join(TT38_DIR, "cap_phoi_tt38.csv")) or [])
        for r in cp:
            x = so(r.get("so_luong"))
            if x is None or not r.get("ma_cap_phoi"):
                continue
            if r["ma_cap_phoi"] in self.cap_phoi and self.cap_phoi[r["ma_cap_phoi"]].get("_xong"):
                continue
            e = self.cap_phoi.setdefault(r["ma_cap_phoi"], {"mo_ta": " · ".join(v for v in (r.get("nhom", ""), r.get("do_sut_hoac_nhom_con", ""),
                                                                                         r.get("quy_cach", ""), f"mác {r.get('mac', '')}") if v),
                                                          "tp": [], "nguon": r.get("nguon", "")})
            if r.get("vat_lieu") == "Phụ gia":
                continue
            e["tp"].append((r.get("vat_lieu", ""), r.get("don_vi", ""), x))
        for e in self.cap_phoi.values():
            e["_xong"] = True

    @staticmethod
    def khoa_ten(x):
        return khoa_ten(x)

    def gia_cua(self, ma_tn, vung=""):
        g = self.gia.get((ma_tn, vung)) or self.gia.get((ma_tn, ""))
        if g:
            return g
        if not hasattr(self, "_gia_chuan"):
            self._gia_chuan = {}
            for (m, v), rec in self.gia.items():
                self._gia_chuan.setdefault((self.khoa_ten(m), v), rec)
        k = self.khoa_ten(ma_tn)
        return self._gia_chuan.get((k, vung)) or self._gia_chuan.get((k, ""))

    def cac_vung(self):
        return sorted({v for (_, v) in self.gia if v})

    def tai_nguyen_dung(self, cac_ma=None):
        out = OrderedDict()
        for ma, d in self.dinh_muc.items():
            if cac_ma is None and ma not in self.ma_rieng:
                continue
            if cac_ma is not None and ma not in cac_ma:
                continue
            for h in d["hao_phi"]:
                if h["ma_tn"]:
                    out.setdefault(h["ma_tn"], h)
        return out

    def thieu_gia(self, cac_ma=None, cac_vung=("",)):
        out = []
        co_hp = {h["ma_tn"] for ma, d in self.dinh_muc.items()
                 if (ma in cac_ma if cac_ma is not None else ma in self.ma_rieng)
                 for h in d["hao_phi"] if h["ma_tn"] and abs(h["hao_phi"] * h.get("he_so", 1.0)) > 1e-12}
        for m in self.tai_nguyen_dung(cac_ma):
            if m not in co_hp:
                continue  # hao phí = 0 ở mọi mã dùng tài nguyên này: không cần giá
            for v in cac_vung:
                g = self.gia_cua(m, v)
                if not g or not g["don_gia"]:
                    out.append(m + (f" (vùng {v})" if v else ""))
        return out


RE_VUA = re.compile(r"^\s*vữa\b", re.I)


def ap_cap_phoi(dl, kl_rows):
    """Dòng KL có cột cap_phoi: thay dòng vật liệu 'Vữa …' của định mức bằng thành phần cấp phối (PL VII).
    Tạo mã ảo '<mã>+<mã cấp phối>' trong dl.dinh_muc; trả về danh sách lỗi."""
    loi = []
    for r in kl_rows:
        cp = r.get("cap_phoi", "")
        if not cp or r["ma_hieu"].upper() == "TG":
            continue
        ma = r["ma_hieu"]
        key = f"{ma}+{cp}"
        if key not in dl.dinh_muc:
            d = dl.dinh_muc.get(ma)
            c = dl.cap_phoi.get(cp)
            if not d:
                continue
            if not c:
                loi.append(f"Dòng {r['dong']}: mã cấp phối {cp} không có trong cap_phoi.csv")
                continue
            hp, thay = [], 0
            for h in d["hao_phi"]:
                if h["loai"] == "VL" and RE_VUA.match(h["ten_tn"] or h["ma_tn"]) and thay == 0:
                    thay += 1
                    for vl, dv, x in c["tp"]:
                        hp.append({"loai": "VL", "ma_tn": vl, "ten_tn": f"{vl} (cấp phối {cp})", "don_vi_tn": dv,
                                   "hao_phi": h["hao_phi"] * x, "he_so": h["he_so"], "can_cu_he_so": h["can_cu_he_so"]})
                else:
                    hp.append(h)
            if not thay:
                loi.append(f"Dòng {r['dong']}: mã {ma} không có dòng vật liệu 'Vữa…' để thay bằng cấp phối {cp}")
                continue
            dl.dinh_muc[key] = dict(d, hao_phi=hp, ten=f"{d['ten']} — vữa theo cấp phối {cp} ({c['mo_ta']})",
                                    nguon=f"{d['nguon']}; cấp phối {c['nguon'] or 'PL VII TT 38/2026'}")
        r["ma_goc"] = ma
        r["ma_hieu"] = key
    return loi


HE_SO_SUA_CHUA = {"VL": 1.02, "NC": 1.15, "M": 1.05}
CAN_CU_SUA_CHUA = "PL VI TT 38/2026, mục 3.b thuyết minh: công tác sửa chữa chưa có trong tập định mức sửa chữa áp định mức dự toán XD và điều chỉnh VL 1,02; NC 1,15; M 1,05"


def phu_luc_cua(dl, ma):
    """Phụ lục TT 38/2026 của mã: theo dữ liệu, nguồn ghi 'PL …', hoặc tra mã gốc trong TT 38 đã trích."""
    ma = ma.split("+")[0]
    d = dl.dinh_muc.get(ma) or {}
    if d.get("phu_luc"):
        return d["phu_luc"]
    m = re.search(r"PL\s*([IVX]+)\b", d.get("nguon", ""))
    if m:
        return m.group(1)
    goc = re.split(r"[#\s]", ma)[0]
    return getattr(dl, "pl_tt38", {}).get(goc, "")


def ap_he_so_sua_chua(dl, kl_rows, cfg):
    """Hồ sơ sửa chữa (cfg loai_ho_so = 'sua_chua'): công tác dùng định mức PL II/III TT 38 được nhân hệ số theo
    PL VI mục 3.b (VL 1,02; NC 1,15; M 1,05) — chỉ khi dòng KL chưa khai hệ số riêng. Trả về số dòng đã áp."""
    if (cfg or {}).get("loai_ho_so") != "sua_chua" or not cfg.get("tu_dong_he_so_sua_chua", True):
        return 0
    n = 0
    for r in kl_rows:
        ma = r.get("ma_goc", r["ma_hieu"])
        if r["ma_hieu"].upper() == "TG" or phu_luc_cua(dl, ma) not in ("II", "III"):
            continue
        if all(abs(x - 1) < 1e-12 for x in (r["hs_vl"], r["hs_nc"], r["hs_m"])):
            r["hs_vl"], r["hs_nc"], r["hs_m"] = HE_SO_SUA_CHUA["VL"], HE_SO_SUA_CHUA["NC"], HE_SO_SUA_CHUA["M"]
            r["can_cu_hs"] = r["can_cu_hs"] or CAN_CU_SUA_CHUA
            n += 1
    return n


def nap_khoi_luong(path):
    rows = doc_csv(path)
    if rows is None:
        sys.exit(f"Không thấy file khối lượng: {path}")
    out = []
    for i, r in enumerate(rows, start=2):
        out.append({
            "dong": i, "stt": r.get("stt", ""), "hang_muc": r.get("hang_muc", "") or "(Chưa phân hạng mục)",
            "ma_hieu": r.get("ma_hieu", ""), "ten": r.get("ten_cong_tac", ""), "don_vi": r.get("don_vi", ""),
            "doan": r.get("doan", "") or DOAN_MAC_DINH, "cap_phoi": r.get("cap_phoi", ""),
            "kl": so(r.get("khoi_luong")), "quy_doi": so(r.get("quy_doi"), 1.0),
            "hs_vl": so(r.get("he_so_vl"), 1.0), "hs_nc": so(r.get("he_so_nc"), 1.0), "hs_m": so(r.get("he_so_m"), 1.0),
            "can_cu_hs": r.get("can_cu_he_so", ""), "dg_tg": so(r.get("don_gia_tron_goi")),
            "dien_giai": r.get("dien_giai", ""), "ban_ve": r.get("nguon_ban_ve", ""),
            "trang_thai": (r.get("trang_thai", "") or "de_xuat").lower(),
        })
    return out


def nap_config(path):
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    tl = c.setdefault("ty_le", {})
    cd = c.get("che_do_chi_phi", "tt36")
    if cd not in CHE_DO:
        sys.exit(f"config: che_do_chi_phi '{cd}' không hợp lệ ({', '.join(CHE_DO)})")
    if cd.startswith("tt40"):
        tl.setdefault("cong_viec_khong_xd_kl", {"gia_tri": 0, "can_cu": "TT 40/2026: chi phí gián tiếp chỉ gồm NC × tỷ lệ (Bảng 2.2 PL II) — không có khoản này"})
        if "chi_phi_chung" in tl:
            tl["chi_phi_chung"].setdefault("co_so", "NC")
            if str(tl["chi_phi_chung"]["co_so"]).upper() != "NC":
                sys.exit("config: chế độ TT 40 — chi phí gián tiếp tính trên NC (ty_le.chi_phi_chung.co_so = 'NC')")
        if so(tl["cong_viec_khong_xd_kl"].get("gia_tri"), 0) != 0:
            sys.exit("config: chế độ TT 40 — cong_viec_khong_xd_kl phải bằng 0 (TT 40 không có khoản này)")
    can = ["chi_phi_chung", "cong_viec_khong_xd_kl", "thu_nhap_chiu_thue_tt", "nha_tam", "thue_gtgt"]
    if cd == "tt36_khao_sat":
        can += ["lap_phuong_an_ks", "lap_bao_cao_ks"]
        tl.setdefault("du_phong", {"gia_tri": 0, "can_cu": "Không tính dự phòng"})
        if "chi_phi_chung" in tl:
            tl["chi_phi_chung"].setdefault("co_so", "NC")
            if str(tl["chi_phi_chung"]["co_so"]).upper() != "NC":
                sys.exit("config: dự toán khảo sát — chi phí chung tính trên NC (Bảng 5.1 PL V TT 36), ty_le.chi_phi_chung.co_so = 'NC'")
    for k in can:
        if k not in tl or so(tl[k].get("gia_tri")) is None:
            sys.exit(f"config: thiếu ty_le.{k}.gia_tri")
    c.setdefault("lam_tron", "khong")
    return c


def ds_doan(cfg, kl_rows):
    """Danh sách đoạn [(id, ten, vung)] theo thứ tự khai báo; đoạn không khai báo dùng vùng ''."""
    out = OrderedDict()
    for d in cfg.get("doan", []) or []:
        out[d["id"]] = (d.get("ten", d["id"]), d.get("vung", ""))
    for r in kl_rows:
        if r["doan"] not in out:
            out[r["doan"]] = (r["doan"] or "Toàn tuyến", "")
    return out


def ds_vung(cfg, dl):
    out = OrderedDict()
    for v in cfg.get("vung", []) or []:
        out[v["id"]] = v.get("ten", v["id"])
    if not out:
        for v in dl.cac_vung():
            out[v] = v
    if not out:
        out[""] = "Chung"
    return out


def ty_le_cho_ma(cfg, ma):
    """Tỷ lệ áp cho một mã (cho phép ghi đè theo mã tại cfg['ty_le_theo_ma'])."""
    t = {k: dict(v) for k, v in cfg["ty_le"].items()}
    for k, v in (cfg.get("ty_le_theo_ma", {}) or {}).get(ma, {}).items():
        t[k] = dict(v)
    return t


# ----------------------------------------------------------------- đơn giá chi tiết
def don_gia_chi_tiet(dl, cfg, r, vung):
    """Phân tích đơn giá cho dòng khối lượng r tại vùng `vung`.

    Trả về dict: dong (list hao phí đã tính), VL, NC, M, T, C, TT, GT, TL, G, E (số đơn vị KL / 1 đơn vị định mức),
    DG (đơn giá trên 1 đơn vị khối lượng, trước thuế, đã gồm C, TT, TL), DG_VL/DG_NC/DG_M (phần trực tiếp / 1 đv KL).
    """
    rt = cfg.get("lam_tron", "khong") == "tung_buoc"
    R = (lambda x: xround(x)) if rt else (lambda x: x)
    t = ty_le_cho_ma(cfg, r["ma_hieu"])
    hs_loai = {"VL": r["hs_vl"], "NC": r["hs_nc"], "M": r["hs_m"], "VLK": 1.0, "MK": 1.0}
    E = round(1 / r["quy_doi"], 9) if r["quy_doi"] else 1.0
    out = {"dong": [], "E": E}
    if r["ma_hieu"].upper() == "TG":
        g = r["dg_tg"] or 0.0
        out.update(VL=g * E, NC=0.0, M=0.0)
        T = out["VL"]
    else:
        d = dl.dinh_muc.get(r["ma_hieu"])
        tong = {"VL": 0.0, "NC": 0.0, "M": 0.0}
        goc_pct = {"VL": 0.0, "M": 0.0, "NC": 0.0}
        cho_pct = []
        for h in (d["hao_phi"] if d else []):
            if h["loai"] in ("VLK", "MK"):
                cho_pct.append(h)
                continue
            g = dl.gia_cua(h["ma_tn"], vung)
            gia = g["don_gia"] if g else 0.0
            hs = h["he_so"] * hs_loai[h["loai"]]
            tt = R(h["hao_phi"] * gia * hs)
            out["dong"].append(dict(h, gia=gia, hs=hs, thanh_tien=tt))
            tong[h["loai"]] += tt
            goc_pct[h["loai"]] += tt
        for h in cho_pct:
            goc = "VL" if h["loai"] == "VLK" else "M"
            tt = R(h["hao_phi"] / 100 * goc_pct[goc])
            out["dong"].append(dict(h, gia=goc_pct[goc], hs=1.0, thanh_tien=tt))
            tong[goc] += tt
        out.update(VL=R(tong["VL"]), NC=R(tong["NC"]), M=R(tong["M"]))
        T = R(out["VL"] + out["NC"] + out["M"])
    co_so_c = out["NC"] if t["chi_phi_chung"].get("co_so", "T").upper() == "NC" else T
    C = R(co_so_c * so(t["chi_phi_chung"]["gia_tri"]))
    TT = R(T * so(t["cong_viec_khong_xd_kl"]["gia_tri"]))
    GT = R(C + TT)
    TL = R((T + GT) * so(t["thu_nhap_chiu_thue_tt"]["gia_tri"]))
    CPA = CBC = 0.0
    if la_khao_sat(cfg):
        CPA = R((T + GT + TL) * so(t["lap_phuong_an_ks"]["gia_tri"], 0))
        CBC = R((T + GT + TL) * so(t["lap_bao_cao_ks"]["gia_tri"], 0))
    G = R(T + GT + TL + CPA + CBC)
    out.update(T=T, C=C, TT=TT, GT=GT, TL=TL, CPA=CPA, CBC=CBC, G=G,
               DG=R(G / E), DG_VL=out["VL"] / E, DG_NC=out["NC"] / E, DG_M=out["M"] / E,
               DG_T=T / E, DG_TGT=(T + GT + TL) / E)
    return out


def vung_cua_doan(cfg, kl_rows, doan_id):
    return ds_doan(cfg, kl_rows)[doan_id][1]


# ----------------------------------------------------------------- tính theo Bảng 3.8 (không phân đoạn)
def tinh_bang_3_8(dl, kl_rows, cfg):
    vung0 = next(iter(ds_vung(cfg, dl)))
    vl = nc = m = 0.0
    for r in kl_rows:
        v = vung_cua_doan(cfg, kl_rows, r["doan"]) or vung0
        if r["ma_hieu"].upper() == "TG":
            dvl, dnc, dm = (r["dg_tg"] or 0.0), 0.0, 0.0
        elif r["ma_hieu"] in dl.dinh_muc:
            c = don_gia_chi_tiet(dl, dict(cfg, lam_tron="khong"), r, v)
            dvl, dnc, dm = c["DG_VL"], c["DG_NC"], c["DG_M"]
        else:
            dvl = dnc = dm = 0.0
        q = r["kl"] or 0.0
        vl += q * dvl
        nc += q * dnc
        m += q * dm
    t = cfg["ty_le"]
    knc = so(cfg.get("he_so", {}).get("knc", {}).get("gia_tri"), 1.0)
    km = so(cfg.get("he_so", {}).get("km", {}).get("gia_tri"), 1.0)
    NC, M = nc * knc, m * km
    T = vl + NC + M
    C = (NC if t["chi_phi_chung"].get("co_so", "T").upper() == "NC" else T) * so(t["chi_phi_chung"]["gia_tri"])
    TT = T * so(t["cong_viec_khong_xd_kl"]["gia_tri"])
    GT = C + TT
    TL = (T + GT) * so(t["thu_nhap_chiu_thue_tt"]["gia_tri"])
    GXDTT = T + GT + TL
    vat = so(t["thue_gtgt"]["gia_tri"])
    if la_khao_sat(cfg):
        CPA = GXDTT * so(t["lap_phuong_an_ks"]["gia_tri"], 0)
        CBC = GXDTT * so(t["lap_bao_cao_ks"]["gia_tri"], 0)
        CK = so((cfg.get("khao_sat") or {}).get("chi_phi_khac_phuc_vu_ks", {}).get("gia_tri"), 0.0)
        G = GXDTT + CPA + CBC + CK
        GTGT = G * vat
        LT = (G + GTGT) * so(t["nha_tam"]["gia_tri"])
        DP = (G + GTGT) * so(t["du_phong"]["gia_tri"], 0)
        return {"VL": vl, "NC": NC, "M": M, "T": T, "C": C, "TT": TT, "GT": GT, "TL": TL, "TGT": GXDTT,
                "CPA": CPA, "CBC": CBC, "CK": CK, "CPVKS": CPA + CBC + CK, "G": G, "GTGT": GTGT, "LT": LT, "DP": DP,
                "GKS": G + GTGT + LT + DP, "GXDTT": G}
    return {"VL": vl, "NC": NC, "M": M, "T": T, "C": C, "TT": TT, "GT": GT, "TL": TL, "GXDTT": GXDTT,
            "GTGT": GXDTT * vat, "GXD": GXDTT * (1 + vat), "LT": GXDTT * so(t["nha_tam"]["gia_tri"]) * (1 + vat)}


# ----------------------------------------------------------------- tính theo đoạn – vùng (đơn giá đầy đủ)
def gom_cong_tac(kl_rows):
    """Gom các dòng khối lượng theo (hạng mục, stt) → công tác với KL theo đoạn."""
    items = OrderedDict()
    for r in kl_rows:
        key = (r["hang_muc"], r["stt"])
        it = items.get(key)
        if it is None:
            it = items[key] = {"r": r, "kl": OrderedDict(), "dong": []}
        elif it["r"]["ma_hieu"] != r["ma_hieu"]:
            it.setdefault("loi", []).append(f"STT {r['stt']} ({r['hang_muc']}): nhiều mã hiệu khác nhau ({it['r']['ma_hieu']}, {r['ma_hieu']})")
        it["kl"][r["doan"]] = it["kl"].get(r["doan"], 0.0) + (r["kl"] or 0.0)
        it["dong"].append(r)
    return items


def bien_the(r):
    return (r["ma_hieu"], round(r["quy_doi"], 12), r["hs_vl"], r["hs_nc"], r["hs_m"], r["dg_tg"] if r["ma_hieu"].upper() == "TG" else None)


def tinh_doan_vung(dl, kl_rows, cfg):
    rt = cfg.get("lam_tron", "khong") == "tung_buoc"
    R = (lambda x: xround(x)) if rt else (lambda x: x)
    doan = ds_doan(cfg, kl_rows)
    vung = ds_vung(cfg, dl)
    vat = so(cfg["ty_le"]["thue_gtgt"]["gia_tri"])
    items = gom_cong_tac(kl_rows)
    dg_cache = {}
    hang_muc = OrderedDict()
    for (hm, stt), it in items.items():
        r = it["r"]
        bt = bien_the(r)
        if bt not in dg_cache:
            dg_cache[bt] = {v: don_gia_chi_tiet(dl, cfg, r, v) for v in vung}
        dgv = dg_cache[bt]
        tt_doan = OrderedDict()
        it["nc"] = it["t"] = it["tgt"] = 0.0
        for d_id, q in it["kl"].items():
            v = doan[d_id][1] or next(iter(vung))
            tt_doan[d_id] = R(q * dgv[v]["DG"])
            it["nc"] += q * dgv[v]["DG_NC"]
            it["t"] += q * dgv[v]["DG_T"]
            it["tgt"] += q * dgv[v]["DG_TGT"]
        it["dg"] = {v: dgv[v]["DG"] for v in vung}
        it["tt_doan"] = tt_doan
        it["tong"] = R(sum(tt_doan.values()))
        h = hang_muc.setdefault(hm, {"items": [], "truoc_thue": 0.0})
        h["items"].append(it)
    for hm, h in hang_muc.items():
        h["truoc_thue"] = R(sum(it["tong"] for it in h["items"]))
        h["vat"] = R(h["truoc_thue"] * vat)
        h["sau_thue"] = R(h["truoc_thue"] + h["vat"])
    out = {"hang_muc": hang_muc, "dg_cache": dg_cache, "doan": doan, "vung": vung,
           "NC": sum(it["nc"] for h in hang_muc.values() for it in h["items"]),
           "T": sum(it["t"] for h in hang_muc.values() for it in h["items"]),
           "TGT": sum(it["tgt"] for h in hang_muc.values() for it in h["items"]),
           "truoc_thue": sum(h["truoc_thue"] for h in hang_muc.values())}
    out["tong_hop"] = tinh_tong_hop(cfg, hang_muc, R)
    return out


def tong_hop_mac_dinh(cfg, hang_muc):
    """Bảng tổng hợp theo Bảng 3.1 PL III TT 36/2026 khi người dùng chưa khai báo `tong_hop`."""
    t = cfg["ty_le"]
    items = []
    ma_tong = []
    for i, hm in enumerate(hang_muc, start=1):
        nhan = {"tt40_bao_duong": "Chi phí thực hiện bảo dưỡng", "tt40_sua_chua": "Chi phí thực hiện sửa chữa",
                "tt36_khao_sat": "Chi phí khảo sát"}.get(che_do(cfg), "Chi phí xây dựng")
        items.append({"ma": f"HM{i}", "stt": f"{i}", "ten": f"{nhan} – {hm}", "kieu": "hang_muc", "hang_muc": [hm]})
        ma_tong.append(f"HM{i}")
    items.append({"ma": "LT", "stt": f"{len(hang_muc)+1}", "ten": "Chi phí nhà tạm" if la_tt40(cfg) else "Chi phí nhà tạm để ở và điều hành thi công",
                  "kieu": "ty_le", "ty_le": so(t["nha_tam"]["gia_tri"]), "co_so": list(ma_tong),
                  "can_cu": t["nha_tam"].get("can_cu", "")})
    if la_khao_sat(cfg):
        items[-1]["can_cu"] = (t["nha_tam"].get("can_cu") or "") + " — (G + GTGT) × tỷ lệ, mục 1.6 PL V TT 36"
        items[-1]["tren_sau_thue"] = True
        items.append({"ma": "DP", "stt": f"{len(hang_muc)+2}", "ten": "Chi phí dự phòng", "kieu": "ty_le",
                      "ty_le": so(t["du_phong"]["gia_tri"], 0), "co_so": list(ma_tong),
                      "can_cu": (t["du_phong"].get("can_cu") or "") + " — (G + GTGT) × tỷ lệ, tối đa 10% (mục 1.7 PL V TT 36)"})
        items.append({"ma": "TONG", "stt": "", "ten": "TỔNG CỘNG CHI PHÍ KHẢO SÁT (Gks)", "kieu": "tong", "gom": ma_tong + ["LT", "DP"], "dam": True})
        return items
    items.append({"ma": "TONG", "stt": "", "ten": "TỔNG CỘNG", "kieu": "tong", "gom": ma_tong + ["LT"], "dam": True})
    return items


def tinh_tong_hop(cfg, hang_muc, R):
    items = cfg.get("tong_hop") or tong_hop_mac_dinh(cfg, hang_muc)
    vat = so(cfg["ty_le"]["thue_gtgt"]["gia_tri"])
    by = {it["ma"]: it for it in items}
    kq = {}

    def tinh(ma, chain=()):
        if ma in kq:
            return kq[ma]
        if ma in chain:
            raise ValueError(f"tong_hop: vòng lặp tại {ma}")
        it = by.get(ma)
        if it is None:
            raise ValueError(f"tong_hop: không có mục '{ma}'")
        k = it.get("kieu", "ty_le")
        if k == "hang_muc":
            tt = R(sum(hang_muc[h]["truoc_thue"] for h in it["hang_muc"] if h in hang_muc))
            g = R(tt * vat) if it.get("vat", True) else 0.0
        elif k == "gia_tri":
            tt = so(it.get("gia_tri"), 0.0)
            g = R(tt * vat) if it.get("vat", True) else 0.0
        elif k == "tong":
            parts = [tinh(m, chain + (ma,)) for m in it["gom"]]
            tt = R(sum(p[0] for p in parts))
            g = R(sum(p[1] for p in parts))
        else:  # ty_le
            base_tt = base_g = 0.0
            for b in it.get("co_so", []):
                if isinstance(b, (int, float)):
                    base_tt += b
                else:
                    p = tinh(b, chain + (ma,))
                    base_tt += p[0]
                    base_g += p[1]
            if it.get("tren_sau_thue"):
                st = R(so(it.get("ty_le"), 0.0) * so(it.get("he_so"), 1.0) * (base_tt + base_g))
                tt = R(st / (1 + vat))
                kq[ma] = (tt, st - tt, st)
                return kq[ma]
            raw = so(it.get("ty_le"), 0.0) * so(it.get("he_so"), 1.0) * base_tt
            if it.get("toi_thieu") is not None and raw <= it["toi_thieu"]:
                raw = it["toi_thieu"]
            if it.get("toi_da") is not None and raw > it["toi_da"]:
                raw = it["toi_da"]
            tt = R(raw)
            v = it.get("vat", True)
            if v == "theo_co_so":
                g = R(so(it.get("ty_le"), 0.0) * so(it.get("he_so"), 1.0) * base_g)
            else:
                g = R(tt * vat) if v else 0.0
        kq[ma] = (tt, g, R(tt + g))
        return kq[ma]

    for it in items:
        tinh(it["ma"])
    return {"items": items, "gia_tri": kq}


# ----------------------------------------------------------------- soát
def tra_nac(nac, gia_tri):
    for i, n in enumerate(nac):
        if n is None or gia_tri <= n:
            return i
    return len(nac) - 1


def ty_le_chuan_tt40(cfg):
    try:
        with open(BANG_TY_LE_TT40, encoding="utf-8") as f:
            b = json.load(f)
    except OSError:
        return None
    out = {}
    nc = so(cfg.get("quy_mo_nc_ty"))
    if nc is not None:
        bg = b["bang_2_2_gian_tiep_tren_nc"]
        out["chi_phi_chung"] = bg["ty_le"][tra_nac(bg["nac_nc_ty_dong"], nc)]
    loai = cfg.get("loai_cong_trinh")
    if loai in b["bang_2_3_thu_nhap_chiu_thue_tt"]:
        out["thu_nhap_chiu_thue_tt"] = b["bang_2_3_thu_nhap_chiu_thue_tt"][loai]
    g = so(cfg.get("quy_mo_truoc_thue_ty"))
    if g is not None:
        bn = b["bang_2_4_nha_tam"]
        out["nha_tam"] = bn["theo_tuyen" if cfg.get("theo_tuyen") else "con_lai"][tra_nac(bn["nac_ty_dong"], g)]
    return out


def kiem_tra_nac_tt40(cfg, nc_dong, g_truoc_thue_dong):
    """Sau khi tính: đối chiếu nấc Bảng 2.2 (theo NC thực tế) và Bảng 2.4 (theo chi phí thực hiện trước thuế thực tế)."""
    if not la_tt40(cfg):
        return []
    kq = []
    c = dict(cfg, quy_mo_nc_ty=nc_dong / 1e9, quy_mo_truoc_thue_ty=g_truoc_thue_dong / 1e9)
    chuan = ty_le_chuan_tt40(c) or {}
    for k, ten, bang, qm in (("chi_phi_chung", "chi phí gián tiếp", "Bảng 2.2", f"NC = {fmt(nc_dong)} đ"),
                             ("nha_tam", "nhà tạm", "Bảng 2.4", f"chi phí thực hiện trước thuế = {fmt(g_truoc_thue_dong)} đ")):
        khai = so(cfg["ty_le"].get(k, {}).get("gia_tri"))
        if k in chuan and khai is not None and abs(khai * 100 - chuan[k]) > 1e-6:
            if k == "chi_phi_chung" and cfg.get("vung_nui_hai_dao") and 1.05 * chuan[k] - 1e-6 <= khai * 100 <= 1.1 * chuan[k] + 1e-6:
                continue
            kq.append(("S19", "CANH_BAO", f"Tỷ lệ {ten} khai {khai*100:g}% khác {bang} TT 40 theo quy mô thực tế ({qm}) → {chuan[k]:g}%"))
    return kq


def _bac(t, x):
    for i, (n, ss) in enumerate(zip(t["nac"], t["so_sanh"])):
        if n is None or (x < n if ss == "lt" else x <= n):
            return t["ty_le"][i]
    return t["ty_le"][-1]


def ty_le_chuan_ks(cfg, nc=None, t=None, tgt=None):
    try:
        with open(BANG_TY_LE, encoding="utf-8") as f:
            b = json.load(f)["pl_v_khao_sat"]
    except (OSError, KeyError):
        return None
    nc = so(cfg.get("quy_mo_nc_ty")) if nc is None else nc
    t = so(cfg.get("quy_mo_t_ty")) if t is None else t
    tgt = so(cfg.get("quy_mo_t_gt_tl_ty")) if tgt is None else tgt
    out = {"thu_nhap_chiu_thue_tt": b["thu_nhap_chiu_thue_tt"], "nha_tam": b["nha_tam_tren_g_cong_gtgt"]}
    if nc is not None:
        out["chi_phi_chung"] = _bac(b["bang_5_1_chi_phi_chung_tren_nc"], nc)
    if t is not None:
        out["cong_viec_khong_xd_kl"] = _bac(b["bang_5_2_khong_xd_kl_tren_t"], t)
    if tgt is not None:
        out["lap_phuong_an_ks"] = _bac(b["bang_5_3_lap_phuong_an_ks"], tgt)
        out["lap_bao_cao_ks"] = _bac(b["bang_5_3_lap_bao_cao_ks"], tgt)
    return out


def kiem_tra_nac_ks(cfg, nc_dong, t_dong, tgt_dong):
    """Sau khi tính: đối chiếu nấc Bảng 5.1–5.3 theo NC, T, T+GT+TL thực tế (chỉ các tỷ lệ khai khác 0)."""
    if not la_khao_sat(cfg):
        return []
    chuan = ty_le_chuan_ks(cfg, nc_dong / 1e9, t_dong / 1e9, tgt_dong / 1e9) or {}
    kq = []
    for k in ("chi_phi_chung", "cong_viec_khong_xd_kl", "lap_phuong_an_ks", "lap_bao_cao_ks"):
        khai = so(cfg["ty_le"].get(k, {}).get("gia_tri"))
        if k in chuan and khai and abs(khai * 100 - chuan[k]) > 1e-6:
            kq.append(("S19", "CANH_BAO", f"Tỷ lệ {k} khai {khai*100:g}% khác Bảng 5.x PL V TT 36 theo quy mô thực tế "
                       f"(NC {fmt(nc_dong)} · T {fmt(t_dong)} · T+GT+TL {fmt(tgt_dong)} đ) → {chuan[k]:g}%"))
    return kq


def ty_le_chuan(cfg):
    if la_khao_sat(cfg):
        return ty_le_chuan_ks(cfg)
    if la_tt40(cfg):
        return ty_le_chuan_tt40(cfg)
    try:
        with open(BANG_TY_LE, encoding="utf-8") as f:
            b = json.load(f)
    except OSError:
        return None
    loai = cfg.get("loai_cong_trinh")
    gtri = so(cfg.get("chi_phi_xd_truoc_thue_tmdt_ty"))
    out = {}
    if loai in b["bang_3_3_chi_phi_chung_du_toan"] and gtri is not None:
        bang = b["bang_3_3_chi_phi_chung_du_toan"]
        v = bang[loai][tra_nac(bang["nac_ty_dong"], gtri)]
        if cfg.get("vung_nui_hai_dao"):
            v = round(v * b["he_so_vung_nui_bien_gioi_bien_hai_dao"], 4)
        out["chi_phi_chung"] = v
    if loai in b["bang_3_5_cong_viec_khong_xd_kl"]:
        out["cong_viec_khong_xd_kl"] = b["bang_3_5_cong_viec_khong_xd_kl"][loai]
    if loai in b["bang_3_6_thu_nhap_chiu_thue_tt"]:
        out["thu_nhap_chiu_thue_tt"] = b["bang_3_6_thu_nhap_chiu_thue_tt"][loai]
    if gtri is not None:
        bang = b["bang_3_7_nha_tam"]
        out["nha_tam"] = bang["theo_tuyen" if cfg.get("theo_tuyen") else "con_lai"][tra_nac(bang["nac_ty_dong"], gtri)]
    return out


def soat(dl, kl_rows, cfg, ngay_lap=None):
    """Trả về list (ma, muc, noi_dung). muc: CHAN / CANH_BAO / THONG_TIN."""
    kq = []
    ngay_lap = ngay_lap or date.today()
    ma_dung = set()
    seen = defaultdict(list)
    doan_kb = {d["id"] for d in (cfg or {}).get("doan", []) or []}
    for r in kl_rows:
        tag = f"Dòng {r['dong']} (STT {r['stt']}, {r['ma_hieu']}{', ' + r['doan'] if r['doan'] else ''})"
        if r["trang_thai"] != "xac_nhan":
            kq.append(("S01", "CHAN", f"{tag}: chưa xác nhận (trang_thai = {r['trang_thai']})"))
        if r["kl"] is None:
            kq.append(("S01", "CHAN", f"{tag}: khối lượng trống/không phải số"))
        if doan_kb and r["doan"] not in doan_kb:
            kq.append(("S11", "CHAN", f"{tag}: đoạn '{r['doan']}' chưa khai báo trong config (doan)"))
        if r["ma_hieu"].upper() == "TG":
            if not r["dg_tg"]:
                kq.append(("S02", "CHAN", f"{tag}: dòng trọn gói thiếu don_gia_tron_goi"))
            kq.append(("S10", "THONG_TIN", f"{tag}: đơn giá trọn gói gộp vào VL; nếu thuộc trường hợp Bảng 3.9 PL III thì C, TT, TL tính 50% — dùng ty_le_theo_ma"))
        elif r["ma_hieu"] not in dl.dinh_muc:
            kq.append(("S03", "CHAN", f"{tag}: mã không có trong bộ định mức đã nạp"))
        else:
            ma_dung.add(r["ma_hieu"])
            def tach_dv(x):
                x = bo_dau(x).strip()
                m = re.match(r"^([\d.,]*)\s*([^\s]+)", x)
                if not m:
                    return 1.0, x
                return (so(m.group(1), 1.0) or 1.0), m.group(2)
            hs_dm, dv_dm = tach_dv(dl.dinh_muc[r["ma_hieu"]]["don_vi"])
            hs_kl, dv_kl = tach_dv(r["don_vi"])
            lech = (dv_kl and dv_dm and dv_kl != dv_dm) or abs(hs_dm / hs_kl * r["quy_doi"] - 1) > 1e-9
            if lech and abs(r["quy_doi"] - 1) < 1e-12:
                kq.append(("S04", "CANH_BAO", f"{tag}: đơn vị KL '{r['don_vi']}' khác đơn vị định mức '{dl.dinh_muc[r['ma_hieu']]['don_vi']}' nhưng quy_doi = 1"))
            if r["ma_hieu"].upper().startswith("TT"):
                kq.append(("S12", "CANH_BAO", f"{tag}: mã tạm tính — cần thuyết minh cách lập hao phí"))
        if any(abs(h - 1) > 1e-12 for h in (r["hs_vl"], r["hs_nc"], r["hs_m"])) and not r["can_cu_hs"]:
            kq.append(("S05", "CANH_BAO", f"{tag}: có hệ số điều chỉnh nhưng thiếu căn cứ"))
        if not r["dien_giai"] or not r["ban_ve"]:
            kq.append(("S06", "CANH_BAO", f"{tag}: thiếu diễn giải hoặc nguồn bản vẽ"))
        seen[(r["hang_muc"], r["ma_hieu"], r["doan"], r["dien_giai"])].append(r["stt"])
    for key, stts in seen.items():
        if len(set(stts)) > 1:
            kq.append(("S08", "CANH_BAO", f"Có thể trùng: hạng mục '{key[0]}', mã {key[1]}, đoạn '{key[2]}', diễn giải giống nhau ở STT {', '.join(stts)}"))
    if cfg:
        vungs = list(ds_vung(cfg, dl)) if (cfg.get("vung") or dl.cac_vung()) else [""]
    else:
        vungs = [""]
    for x in dl.thieu_gia(ma_dung, vungs):
        goi_y = " — chọn mác vữa ở cột cap_phoi (PL VII TT 38/2026) hoặc nhập giá vữa/bê tông thương phẩm" if RE_VUA.match(x) else ""
        kq.append(("S02", "CHAN", f"Tài nguyên {x} thiếu giá hoặc giá = 0{goi_y}"))
    for ma_tn in dl.tai_nguyen_dung(ma_dung):
        for v in vungs:
            g = dl.gia_cua(ma_tn, v)
            if not g:
                continue
            if not g["nguon"] or not g["ngay"]:
                kq.append(("S07", "CANH_BAO", f"Giá {ma_tn}{' (' + v + ')' if v else ''}: thiếu nguồn hoặc ngày áp dụng"))
                continue
            try:
                d = datetime.strptime(g["ngay"], "%Y-%m-%d").date()
                if (ngay_lap - d).days > 183:
                    kq.append(("S07", "CANH_BAO", f"Giá {ma_tn}{' (' + v + ')' if v else ''}: ngày áp dụng {g['ngay']} cách thời điểm lập hơn 6 tháng"))
            except ValueError:
                kq.append(("S07", "CANH_BAO", f"Giá {ma_tn}: ngày áp dụng '{g['ngay']}' sai định dạng yyyy-mm-dd"))
    vnc = vung_nhan_cong(cfg)
    if vnc:
        d_gia, gc_ngay = ngay_ap_gia(cfg)
        tc = nhan_cong_tham_chieu(d_gia)
        tat_ca = nhan_cong_tat_ca()
        ma_vung_all = {r["ma_vung"] for r in tat_ca}
        if gc_ngay:
            kq.append(("S22", "THONG_TIN", f"Chọn văn bản giá nhân công theo ngày {d_gia:%d/%m/%Y} ({gc_ngay})"))
        for v, mv in vnc.items():
            if mv not in ma_vung_all:
                kq.append(("S22", "CANH_BAO", f"Vùng {v}: mã vùng nhân công '{mv}' không có trong data/nhan-cong (có: {', '.join(sorted(ma_vung_all))})"))
                continue
            dong = [r for r in tat_ca if r["ma_vung"] == mv]
            hl = [r for r in dong if con_hieu_luc(r, d_gia)]
            if not hl:
                tinh = dong[0]["tinh"]
                thay = sorted({r["ma_vung"] for r in tat_ca if r["tinh"] == tinh and con_hieu_luc(r, d_gia)})
                vb = "; ".join(sorted({f"{r['van_ban']} ({r.get('hieu_luc_tu') or '…'} → {r.get('hieu_luc_den') or '…'})" for r in dong}))
                kq.append(("S22", "CANH_BAO", f"Vùng {v}: mã '{mv}' không có văn bản giá nhân công hiệu lực tại {d_gia:%d/%m/%Y} ({vb})"
                           + (f" — văn bản hiệu lực của {tinh}: mã {', '.join(thay)}" if thay else "")))
                continue
            if "chỉ có tháng" in gc_ngay:
                dau_thang = d_gia.replace(day=1)
                moc = sorted({x for r in [r for r in tat_ca if r["tinh"] == dong[0]["tinh"]]
                              for x in (_ngay_iso(r.get("hieu_luc_tu")), _ngay_iso(r.get("hieu_luc_den")))
                              if x and dau_thang < x <= d_gia})
                if moc:
                    kq.append(("S22", "CANH_BAO", f"Vùng {v} ({mv}): văn bản giá nhân công {dong[0]['tinh']} thay đổi trong tháng áp giá (mốc {', '.join(f'{x:%d/%m/%Y}' for x in moc)}) — ghi thoi_diem_ap_gia đủ ngày (yyyy-mm-dd)"))
            r0 = hl[0]
            nvb = _ngay_iso(r0.get("ngay_van_ban"))
            if nvb and (d_gia - nvb).days > 365:
                kq.append(("S22", "THONG_TIN", f"Vùng {v} ({mv}): {r0['van_ban']} ngày {nvb:%d/%m/%Y} đã hơn 12 tháng — kiểm tra Sở XD đã công bố giá nhân công mới chưa"))
            gc = next((r["ghi_chu_soat"] for r in hl if r.get("ghi_chu_soat")), "")
            if gc:
                kq.append(("S22", "THONG_TIN", f"Vùng {v} ({mv}): {gc}"))
            for ma_tn, h in dl.tai_nguyen_dung(ma_dung).items():
                if h["loai"] != "NC":
                    continue
                r = tc.get((mv, khoa_ten(ma_tn)))
                g = dl.gia_cua(ma_tn, v)
                if r and g and abs(g["don_gia"] - float(r["don_gia"])) > 0.5:
                    kq.append(("S22", "CANH_BAO", f"Giá {ma_tn} vùng {v}: {fmt(g['don_gia'])} khác {r['van_ban']} ({r['ten_vung']}: {fmt(float(r['don_gia']))})"))
    # S23 — định mức chuyên ngành (CNTT, viễn thông)
    cn_dung = sorted({m for m in ma_dung if m.split("+")[0] in getattr(dl, "bo_cn", {})})
    if cn_dung:
        bo = sorted({dl.bo_cn[m.split("+")[0]] for m in cn_dung})
        kq.append(("S23", "THONG_TIN", f"{len(cn_dung)} mã dùng định mức chuyên ngành ({'; '.join(bo)}): chỉ dùng khi TT 38 không có công tác tương ứng, ghi căn cứ "
                   "(CNTT: NĐ 224/2026 Điều 49 k4 điểm đ — định mức chuyên ngành là một trong các phương pháp; xem references/can-cu-phap-ly.md). "
                   "Nhân công theo cấp bậc đã đổi sang nhóm TT 37 Bảng 3.1 theo tính chất công tác (TT 37 Điều 2 k3; quy tắc data/chuyen-nganh/anh_xa_nhan_cong.csv, cột can_xem_xet nêu điểm có thể bị thẩm định khác); "
                   "kỹ sư CNTT xếp vào 'Kỹ sư' (mục III.1) là gần nhất — dự án CNTT có thể định giá theo TT 07/2026/TT-BNV hoặc báo giá"))
        for m in cn_dung:
            g = m.split("+")[0]; goc = g.split("_")[0]
            for ld in dl.ma_kt_cn.get(g, []) + dl.ma_kt_cn.get(goc, []):
                kq.append(("S23", "CANH_BAO", f"Mã {m}: {ld}"))
            for ld in getattr(dl, "anh_xa_nc_loi", []):
                if ld.startswith(g + ":"):
                    kq.append(("S23", "CANH_BAO", f"Nhân công {ld}"))
            n = len(dl.ghi_chu_cn.get(goc, []) or dl.ghi_chu_cn.get(g[:-2] + "00", []))
            if n:
                kq.append(("S23", "THONG_TIN", f"Mã {m}: có {n} dòng ghi chú áp dụng (hệ số, điều kiện) trong data/chuyen-nganh — kiểm tra trước khi dùng"))
    # S24 — xác nhận mã máy (ánh xạ tên máy TT 38 → mã PL IV) theo hồ sơ
    try:
        import anh_xa_may
        ten_m = {m for m, h in dl.tai_nguyen_dung(ma_dung).items() if h["loai"] == "M"}
        vung_ds = [v["id"] for v in (cfg or {}).get("vung", []) or []] or [""]
        kq.extend(anh_xa_may.soat_ho_so(dl, ten_m, lambda t: all((dl.gia_cua(t, v) or {}).get("don_gia") for v in vung_ds)))
    except ImportError:
        pass
    sua_chua = (cfg or {}).get("loai_ho_so") == "sua_chua"
    for ma in ma_dung:
        goc0 = ma.split("+")[0]
        if goc0 in dl.ma_can_kiem_tra and goc0 not in dl.ma_rieng:
            kq.append(("S18", "CANH_BAO", f"Mã {goc0}: {dl.ma_can_kiem_tra[goc0]}"))
        hs_vl = set()
        for h in dl.dinh_muc[ma]["hao_phi"]:
            if abs(h["he_so"] - 1) > 1e-12 and not h["can_cu_he_so"]:
                kq.append(("S05", "CANH_BAO", f"Mã {ma}, {h['ma_tn'] or h['ten_tn']}: hệ số {h['he_so']:g} chưa có căn cứ"))
            if h["loai"] == "VL" and h["he_so"] > 1 + 1e-12:
                hs_vl.add(f"{h['he_so']:g}")
        pl = phu_luc_cua(dl, ma.split("+")[0])
        if hs_vl and not (sua_chua and pl in ("II", "III") and hs_vl == {"1.02"}):
            kq.append(("S14", "CANH_BAO", f"Mã {ma} (PL {pl or '?'}): vật liệu nhân hệ số {', '.join(sorted(hs_vl))} — hao phí VL trong định mức TT 38 đã gồm hao hụt thi công; "
                       "chỉ nhân 1,02 cho công tác sửa chữa dùng định mức PL II/III (PL VI mục 3.b)"))
        ng = bo_dau(dl.dinh_muc[ma]["nguon"]).replace(" ", "")
        cac_goc = re.findall(r"[A-Z]{1,3}\.\d{5}", ma.split("+")[0]) or [re.split(r"[#\s+]", ma)[0]]
        goc = cac_goc[0]
        tt = [x for g in cac_goc for x in dl.hp_tt38.get(g, [])]
        if tt and ma in dl.ma_rieng:
            lech, chu_y = [], []
            for h in dl.dinh_muc[ma]["hao_phi"]:
                cung = [v for l, n, v in tt if l == h["loai"]]
                ten_h = bo_dau(h.get("ten_tn") or h.get("ma_tn") or "").lower().replace(" ", "")
                cung_ten = [v for l, n, v in tt if l == h["loai"] and ten_h and bo_dau(n).lower().replace(" ", "") == ten_h]
                if cung_ten:
                    cung = cung_ten
                if cung and not any(abs(v - h["hao_phi"]) < 1e-9 for v in cung):
                    mo_ta = f"{h['ten_tn'] or h['loai']} {h['hao_phi']:g} (TT 38: {', '.join(f'{v:g}' for v in cung)})"
                    if h.get("ly_do"):
                        chu_y.append(f"{mo_ta} – lý do: {h['ly_do']}")
                    else:
                        lech.append(mo_ta)
            if lech:
                kq.append(("S17", "CANH_BAO", f"Mã {ma}: hao phí khác TT 38/2026 — " + "; ".join(lech[:4]) + (" …" if len(lech) > 4 else "")
                           + " — nếu là chủ ý, ghi cột ly_do trong dinh_muc.csv"))
            if chu_y:
                kq.append(("S17", "THONG_TIN", f"Mã {ma}: điều chỉnh hao phí có chủ ý so với TT 38/2026 — " + "; ".join(chu_y[:4])
                           + (" …" if len(chu_y) > 4 else "") + " — đưa lý do vào thuyết minh dự toán"))
        elif "38/2026" not in ng and "tt38" not in ng and not (dl.co_tt38 and goc in dl.pl_tt38):
            kq.append(("S15", "CANH_BAO", f"Mã {ma}: không có trong TT 38/2026 (nguồn '{dl.dinh_muc[ma]['nguon'][:50]}') — nêu lý do TT 38 không có công tác tương ứng"))
    da_bao = set()
    for r in kl_rows:
        ma = r.get("ma_goc", r["ma_hieu"])
        if r["ma_hieu"] not in dl.dinh_muc or (r["stt"], r["hang_muc"], ma) in da_bao:
            continue
        da_bao.add((r["stt"], r["hang_muc"], ma))
        pl = phu_luc_cua(dl, ma)
        hs_dong = {}
        for h in dl.dinh_muc[r["ma_hieu"]]["hao_phi"]:
            if h["loai"] in ("VL", "NC", "M"):
                hs_dong.setdefault(h["loai"], set()).add(round(h["he_so"], 6))
        hs = tuple(x * (next(iter(hs_dong[l])) if len(hs_dong.get(l, ())) == 1 else 1.0)
                   for x, l in ((r["hs_vl"], "VL"), (r["hs_nc"], "NC"), (r["hs_m"], "M")))
        tag = f"Dòng {r['dong']} (STT {r['stt']}, {ma})"
        if sua_chua and pl == "VI" and any(abs(x - 1) > 1e-12 for x in hs) and not r["can_cu_hs"]:
            kq.append(("S14", "CANH_BAO", f"{tag}: mã PL VI (sửa chữa) có hệ số {hs} — PL VI đã là định mức sửa chữa, không nhân hệ số 3.b"))
        if sua_chua and pl in ("II", "III") and all(abs(x - 1) < 1e-12 for x in hs) and not r["can_cu_hs"]:
            kq.append(("S14", "THONG_TIN", f"{tag}: hồ sơ sửa chữa dùng mã PL {pl} chưa nhân hệ số PL VI mục 3.b (VL 1,02; NC 1,15; M 1,05)"))
        if not sua_chua and hs[0] > 1 + 1e-12:
            kq.append(("S14", "CANH_BAO", f"{tag}: hệ số vật liệu {hs[0]:g} — hao phí VL TT 38 đã gồm hao hụt thi công; nếu là hồ sơ sửa chữa, khai loai_ho_so = 'sua_chua'"))
    if cfg:
        chuan = ty_le_chuan(cfg) or {}
        for k, v in chuan.items():
            khai = so(cfg["ty_le"].get(k, {}).get("gia_tri"))
            if khai is not None and abs(khai * 100 - v) > 1e-6:
                if che_do(cfg) == "tt36" and k == "chi_phi_chung" and cfg["ty_le"][k].get("co_so", "T").upper() == "NC":
                    continue  # Bảng 3.4 (NC) — không đối chiếu với Bảng 3.3
                if la_khao_sat(cfg):
                    if k in ("lap_phuong_an_ks", "lap_bao_cao_ks") and khai == 0:
                        kq.append(("S09", "THONG_TIN", f"Không tính {'chi phí lập phương án kỹ thuật khảo sát' if k == 'lap_phuong_an_ks' else 'chi phí lập báo cáo kết quả khảo sát'} (Bảng 5.3: {v:g}%) — ghi lý do trong thuyết minh"))
                        continue
                    kq.append(("S09", "CANH_BAO", f"Tỷ lệ {k} khai {khai*100:g}% khác PL V TT 36 ({v:g}%) theo quy mô khai báo"))
                    continue
                if la_tt40(cfg):
                    if k == "chi_phi_chung" and cfg.get("vung_nui_hai_dao") and 1.05 * v - 1e-6 <= khai * 100 <= 1.1 * v + 1e-6:
                        continue
                    kq.append(("S09", "CANH_BAO", f"Tỷ lệ {k} khai {khai*100:g}% khác bảng TT 40/2026 ({v:g}%) theo loại '{cfg.get('loai_cong_trinh')}' và quy mô khai báo"))
                else:
                    kq.append(("S09", "CANH_BAO", f"Tỷ lệ {k} khai {khai*100:g}% khác bảng PL III ({v:g}%) theo loại '{cfg.get('loai_cong_trinh')}' và nấc giá trị khai báo"))
        if not chuan:
            kq.append(("S09", "THONG_TIN", "Không đối chiếu được tỷ lệ với bảng TT 40/2026 (thiếu loai_cong_trinh, quy_mo_nc_ty hoặc quy_mo_truoc_thue_ty)"
                       if la_tt40(cfg) else "Không đối chiếu được tỷ lệ với bảng PL III (thiếu loai_cong_trinh hoặc chi_phi_xd_truoc_thue_tmdt_ty)"))
        if cfg.get("mau_xuat", "bang_3_8") == "bang_3_8":
            vung_dung = {(ds_doan(cfg, kl_rows).get(r["doan"]) or ("", ""))[1] for r in kl_rows}
            if len({v for v in vung_dung if v}) > 1:
                kq.append(("S21", "CHAN", f"Khối lượng dùng {len(vung_dung)} vùng giá ({', '.join(sorted(v for v in vung_dung if v))}) nhưng mẫu Bảng 3.8/5.4 chỉ tính một vùng — "
                           "khai mau_xuat = 'doan_vung'"))
            if cfg.get("ty_le_theo_ma"):
                kq.append(("S21", "CANH_BAO", "Tỷ lệ riêng theo mã (ty_le_theo_ma) chỉ áp dụng ở mẫu 'doan_vung'; mẫu Bảng 3.8/5.4 tính một tỷ lệ chung"))
        if la_khao_sat(cfg):
            dp = so(cfg["ty_le"].get("du_phong", {}).get("gia_tri"), 0)
            if dp > 0.10 + 1e-12:
                kq.append(("S09", "CANH_BAO", f"Dự phòng khảo sát {dp*100:g}% vượt mức tối đa 10% (mục 1.7 PL V TT 36)"))
            khong = [ma for ma, ov in (cfg.get("ty_le_theo_ma", {}) or {}).items()
                     if any(so(ov.get(k, {}).get("gia_tri"), 1) == 0 for k in ("lap_bao_cao_ks", "lap_phuong_an_ks"))]
            if khong:
                kq.append(("S20", "THONG_TIN", f"Các mã {', '.join(khong)}: không tính lập phương án/báo cáo khảo sát. Nếu là chi phí khác phục vụ "
                           "khảo sát (di chuyển máy, ĐBATGT, bảo hiểm), PL V xếp vào Cpvks và lập dự toán riêng — thống nhất cách trình bày"))
        if la_tt40(cfg):
            kq.append(("S20", "THONG_TIN", "Chế độ TT 40/2026 (" + ("bảo dưỡng – Bảng 2.5 PL II" if che_do(cfg) == "tt40_bao_duong" else "sửa chữa trong bảo trì – Bảng 3.2 PL III")
                       + "): chỉ áp dụng khi công việc thuộc kế hoạch bảo trì. Điều 7 TT 40: công trình chuyên ngành có quy định riêng về bảo trì thì theo quy định chuyên ngành; "
                       "nguồn vốn khác chi thường xuyên NSNN/PPP thì chủ sở hữu tự quyết định áp dụng — ghi rõ căn cứ chọn chế độ này."))
            if che_do(cfg) == "tt40_sua_chua" and cfg.get("loai_ho_so") != "sua_chua":
                kq.append(("S20", "THONG_TIN", "Chế độ sửa chữa TT 40 nhưng chưa khai loai_ho_so = 'sua_chua' — nếu dùng mã PL II/III cho công tác sửa chữa cần hệ số PL VI mục 3.b TT 38"))
        for k, v in cfg["ty_le"].items():
            if isinstance(v, dict) and not v.get("can_cu"):
                kq.append(("S09", "CANH_BAO", f"Tỷ lệ {k}: thiếu căn cứ"))
        for ma, ov in (cfg.get("ty_le_theo_ma", {}) or {}).items():
            for k, v in ov.items():
                if not v.get("can_cu"):
                    kq.append(("S09", "CANH_BAO", f"Tỷ lệ riêng của mã {ma} ({k}): thiếu căn cứ"))
        for it in cfg.get("tong_hop", []) or []:
            if it.get("kieu", "ty_le") in ("ty_le", "gia_tri") and not it.get("can_cu"):
                kq.append(("S13", "CANH_BAO", f"Bảng tổng hợp – mục {it.get('stt','')} {it.get('ten','')}: thiếu căn cứ"))
            if so(it.get("he_so"), 1.0) != 1.0 and not it.get("can_cu_he_so"):
                kq.append(("S13", "CANH_BAO", f"Bảng tổng hợp – mục {it.get('stt','')} {it.get('ten','')}: hệ số {it.get('he_so')} chưa ghi căn cứ"))
    return kq


def in_soat(kq):
    if not kq:
        print("Không phát hiện vấn đề.")
        return
    thu_tu = {"CHAN": 0, "CANH_BAO": 1, "THONG_TIN": 2}
    for ma, muc, nd in sorted(kq, key=lambda x: (thu_tu[x[1]], x[0])):
        print(f"[{muc}] {ma}  {nd}")
    print(f"\nTổng: {sum(1 for x in kq if x[1]=='CHAN')} chặn, {sum(1 for x in kq if x[1]=='CANH_BAO')} cảnh báo, {sum(1 for x in kq if x[1]=='THONG_TIN')} thông tin")
