"""Kiểm tra dữ liệu giá nhân công tham chiếu: thời hạn hiệu lực không chồng lấn, mã vùng tra lý trình tồn tại."""
import csv
import os
import unittest
from collections import defaultdict
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NC = os.path.join(ROOT, "data", "nhan-cong")


def d(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s else None


class TestNhanCong(unittest.TestCase):
    def setUp(self):
        self.rows = list(csv.DictReader(open(os.path.join(NC, "gia_nhan_cong_chuyen_doi_2026.csv"), encoding="utf-8-sig")))

    def test_hieu_luc_khong_chong_lan(self):
        nhom = defaultdict(list)
        for r in self.rows:
            self.assertTrue(r["hieu_luc_tu"], f"thiếu hieu_luc_tu: {r['ma_vung']} {r['ten_tn']}")
            tu, den = d(r["hieu_luc_tu"]), d(r["hieu_luc_den"])
            self.assertTrue(den is None or tu <= den, f"tu > den: {r['ma_vung']} {r['ten_tn']}")
            float(r["don_gia"])
            nhom[(r["ma_vung"], r["ten_tn"])].append((tu, den or date.max, r["van_ban"]))
        for k, ds in nhom.items():
            ds.sort()
            for (t1, e1, v1), (t2, e2, v2) in zip(ds, ds[1:]):
                self.assertLess(e1, t2, f"{k}: {v1} chồng thời hạn với {v2}")

    def test_moi_tinh_co_van_ban_hieu_luc_hom_nay(self):
        hom_nay = date.today()
        for tinh in {r["tinh"] for r in self.rows}:
            self.assertTrue(any(r["tinh"] == tinh and d(r["hieu_luc_tu"]) <= hom_nay and (not r["hieu_luc_den"] or hom_nay <= d(r["hieu_luc_den"]))
                                for r in self.rows), f"{tinh}: không có văn bản giá nhân công hiệu lực hôm nay")

    def test_ma_vung_tuyen_ton_tai(self):
        ma = {r["ma_vung"] for r in self.rows}
        for r in csv.DictReader(open(os.path.join(NC, "xa_phuong_tuyen_hn_hp.csv"), encoding="utf-8-sig")):
            for c in ("ma_vung_nhan_cong", "ma_vung_nhan_cong_khac"):
                if r.get(c):
                    self.assertIn(r[c], ma, f"{r['xa_phuong']}: {c}={r[c]}")


if __name__ == "__main__":
    unittest.main()
