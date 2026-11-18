"""Giá ca máy công bố QĐ 2075 Hà Nội: đủ 778 máy × 2 vùng; công thức PL IV của skill khớp bảng công bố (làm tròn 100 đ)."""
import csv, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gia_ca_may_cong_bo as g  # noqa: E402
from datetime import date  # noqa: E402


class TestGCM(unittest.TestCase):
    def test_du(self):
        rs = list(csv.DictReader(open(g.F, encoding="utf-8-sig")))
        self.assertEqual(len(rs), 1556); self.assertEqual(len({r["ma_may"] for r in rs}), 778)

    def test_gia_mau_va_hieu_luc(self):
        self.assertEqual(g.tra("M101.0101", vung="HN-V1", ngay=date(2026, 11, 17))[0]["don_gia"], "2524500")
        self.assertEqual(g.tra("M105.0202", vung="HN-V2", ngay=date(2026, 11, 17))[0]["don_gia"], "4347900")
        self.assertEqual(g.tra("M101.0101", ngay=date(2026, 10, 28)), [])   # trước QĐ 2075 (QĐ 2037 chưa nhập)

    def test_cong_thuc_pl4_khop_cong_bo(self):
        ra = os.path.join(tempfile.mkdtemp(), "g.csv")
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "gia_ca_may.py"), "--dinh-muc",
                        os.path.join(ROOT, "data", "gia-ca-may", "dinh_muc_ca_may_tt37.csv"), "--ma-vung", "HN-V1", "--ngay", "2026-11-01",
                        "--gia-diezel", "29250", "--gia-xang", "24910", "--gia-dien", "1987", "--ra", ra], check=True, capture_output=True)
        tinh = {r["ma_tn"]: float(r["don_gia"]) for r in csv.DictReader(open(ra, encoding="utf-8-sig"))}
        for ma, v in tinh.items():
            cb = float(g.tra(ma, vung="HN-V1", ngay=date(2026, 11, 17))[0]["don_gia"])
            self.assertLessEqual(abs(round(v, -2) - cb), 100, ma)


if __name__ == "__main__":
    unittest.main()
