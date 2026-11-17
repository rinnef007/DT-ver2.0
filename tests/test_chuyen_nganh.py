"""Định mức chuyên ngành: số mã, không trùng TT 38, đối chiếu tay vài giá trị."""
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from dutoan_core import DuLieu  # noqa: E402


class TestChuyenNganh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dl = DuLieu(os.path.join(os.path.dirname(HERE), "data", "vi-du-tt38"))

    def hp(self, ma, ten):
        return next(h["hao_phi"] for h in self.dl.dinh_muc[ma]["hao_phi"] if h["ten_tn"] == ten)

    def test_so_ma(self):
        from collections import Counter
        c = Counter(self.dl.dinh_muc[m]["phu_luc"] for m in self.dl.bo_cn)
        self.assertEqual((c["CNTT-1601"], c["CNTT-1595"], c["VT-258"]), (319, 61, 2133))

    def test_khong_trung_tt38(self):
        self.assertFalse(set(self.dl.bo_cn) & set(self.dl.pl_tt38))

    def test_doi_chieu_tay(self):
        self.assertAlmostEqual(self.hp("01.01.01.01_2", "Kỹ sư 2/8"), 0.5)
        self.assertAlmostEqual(self.hp("10.010100.04", "Công nhân 3,5/7"), 0.49)
        self.assertAlmostEqual(self.hp("10.010100.04", "Máy cưa 0,7 kW"), 0.24)
        self.assertAlmostEqual(self.hp("02.10.01.01.01_2", "Nhóm 03 KS3 và 02 KS4"), 4.375)

    def test_qd1235_da_ap(self):
        ten = {h["ten_tn"] for h in self.dl.dinh_muc["01.01.01.01_1"]["hao_phi"]}
        self.assertIn("Khoan điện cầm tay đa năng 550w", ten)
        self.assertNotIn("Máy khoan 1KW", ten)


if __name__ == "__main__":
    unittest.main()
