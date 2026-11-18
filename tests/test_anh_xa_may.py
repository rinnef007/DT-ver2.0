import csv, os, sys, unittest
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import anh_xa_may as a  # noqa: E402


class TestAnhXa(unittest.TestCase):
    def test_pl4(self):
        rs = list(csv.DictReader(open(os.path.join(ROOT, "data", "gia-ca-may", "danh_muc_may_pl4_tt37.csv"), encoding="utf-8-sig")))
        self.assertEqual(len(rs), 787)
        r = next(x for x in rs if x["ma_may"] == "M101.0101")
        self.assertEqual((r["ten_day_du"], r["nguyen_gia_1000d"]), ("Máy đào một gầu, bánh xích - dung tích gầu 0,40 m3", "809.944"))

    def test_ma_chi_dung_khi_da_khop(self):
        b = a.nap()
        self.assertTrue(all(not r["ma_may"] for r in b.values() if r["trang_thai"] in ("can_xac_nhan", "khong_khop")))

    def test_gia(self):
        self.assertEqual(a.gia_may("Máy ủi 110 cv", "HN-V1", date(2026, 11, 17))[0], 2571800.0)
        self.assertIsNone(a.gia_may("Cần cẩu 25 t", "HN-V1", date(2026, 11, 17))[0])   # bánh hơi hay bánh xích: chờ xác nhận


if __name__ == "__main__":
    unittest.main()


class TestXacNhanHoSo(unittest.TestCase):
    def test_uu_tien_va_soat(self):
        import tempfile, shutil
        from dutoan_core import DuLieu
        d = tempfile.mkdtemp()
        for f in os.listdir(os.path.join(ROOT, "data", "vi-du-tt38")):
            shutil.copy(os.path.join(ROOT, "data", "vi-du-tt38", f), d)
        open(os.path.join(d, "anh_xa_may.csv"), "w", encoding="utf-8-sig").write(
            "ten_tn,ma_may,can_cu\nCần cẩu 25 t,M102.0304,BPTC-03 cần cẩu bánh xích\nCần cẩu 16 t,M999.9999,\n")
        self.assertEqual(a.nap(d)["Cần cẩu 25 t"]["ma_may"], "M102.0304")
        self.assertEqual(a.nap()["Cần cẩu 25 t"]["ma_may"], "")          # bảng chung không đổi
        g, ng = a.gia_may("Cần cẩu 25 t", "HN-V1", date(2026, 11, 17), thu_muc=d)
        self.assertEqual(g, 3638400.0); self.assertIn("BPTC-03", ng)
        kq = a.soat_ho_so(DuLieu(d), {"Cần cẩu 40 t"}, lambda t: False)
        self.assertTrue(any(m == "CHAN" and "M999.9999" in t for _, m, t in kq))
        self.assertTrue(any(m == "CANH_BAO" and "Cần cẩu 40 t" in t for _, m, t in kq))
