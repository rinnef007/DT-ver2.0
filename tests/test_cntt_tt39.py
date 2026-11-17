"""Chế độ chi phí CNTT (TT 39/2026/TT-BKHCN) và chọn nhóm nhân công định mức chuyên ngành."""
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from dutoan_core import DuLieu  # noqa: E402
import cntt_tt39  # noqa: E402


class TestCntt(unittest.TestCase):
    def test_chuyen_gia(self):
        k = cntt_tt39.chi_phi_chuyen_gia({"ccg": 60e6, "ck": 5e6, "vat": 0.1})
        self.assertAlmostEqual(k["CQL"], 33e6); self.assertAlmostEqual(k["TN"], 0.06 * 98e6); self.assertAlmostEqual(k["CTV"], 114268000)
        self.assertEqual(cntt_tt39.ty_le_cql(2e9), 0.50); self.assertEqual(cntt_tt39.ty_le_cql(5e9), 0.45)
        self.assertEqual(cntt_tt39.chi_phi_chuyen_gia({"ccg": 1e6, "ca_nhan": True})["CTV"], 1e6)

    def test_vi_du(self):
        kq = cntt_tt39.tinh(os.path.join(ROOT, "data", "vi-du-cntt"))
        self.assertFalse([t for m, t in kq["soat"] if m == "CHAN"])
        th = {k: v for k, _, v in kq["tong_hop"]}
        self.assertAlmostEqual(th["GDP"], (th["GTB"] + th["GQLDA"] + th["GTV"] + th["GK"]) * 0.05, places=3)
        self.assertGreater(th["GLD"], 0); self.assertGreater(th["GCSDL"], 0)

    def test_kdp_vuot(self):
        import json, shutil, tempfile
        d = tempfile.mkdtemp(); src = os.path.join(ROOT, "data", "vi-du-cntt")
        for f in os.listdir(src):
            shutil.copy(os.path.join(src, f), d)
        c = json.load(open(os.path.join(d, "config_cntt.json"), encoding="utf-8")); c["kdp"] = 0.08
        json.dump(c, open(os.path.join(d, "config_cntt.json"), "w", encoding="utf-8"), ensure_ascii=False)
        self.assertTrue(any("Kdp" in t for m, t in cntt_tt39.tinh(d)["soat"] if m == "CHAN"))


class TestNhomNhanCong(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dl = DuLieu(os.path.join(ROOT, "data", "vi-du-tt38"))

    def nc(self, ma):
        return {h["ten_tn"]: round(h["hao_phi"], 6) for h in self.dl.dinh_muc[ma]["hao_phi"] if h["loai"] == "NC"}

    def test_moi_ten_deu_co_nhom(self):
        dich = {"Nhân công nhóm 1", "Nhân công nhóm 2", "Nhân công nhóm 3", "Nhân công nhóm 4", "Kỹ sư", "Thợ lặn"}
        ten = {h["ten_tn"] for m in self.dl.bo_cn for h in self.dl.dinh_muc[m]["hao_phi"] if h["loai"] == "NC"}
        self.assertEqual(ten - dich, set())
        self.assertFalse([l for l in self.dl.anh_xa_nc_loi if "chưa có quy tắc" in l])

    def test_mau(self):
        self.assertEqual(self.nc("01.01.01.01_2"), {"Nhân công nhóm 4": 0.3, "Kỹ sư": 0.5})
        self.assertEqual(self.nc("10.010100.04"), {"Nhân công nhóm 1": 0.49})
        self.assertEqual(self.nc("02.10.01.01.01_2"), {"Kỹ sư": 21.875})   # 4,375 nhóm công × 5 người


if __name__ == "__main__":
    unittest.main()
