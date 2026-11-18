"""Tra giá vật liệu CBG (định dạng GVT của GXD) — dữ liệu giả trong tests/fixtures/gvt."""
import os, subprocess, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import gia_vat_lieu as g  # noqa: E402
FX = os.path.join(HERE, "fixtures", "gvt")


class TestGVT(unittest.TestCase):
    def test_ky(self):
        self.assertEqual(g.ky_cua_tep("GVT_Q3_2026_HANOI.csv")[:2], (2026, 9))
        self.assertEqual(g.ky_cua_tep("GVT_QII_2023_HANOI.csv")[:2], (2023, 6))
        self.assertEqual(g.ky_cua_tep("GVT_T08_2026_HUNGYEN.csv")[:2], (2026, 8))
        self.assertEqual(g.ky_cua_tep("GVT_T9+Q3_2023_HANOI.csv")[:2], (2023, 9))

    def test_moi_nhat_va_doc_utf16(self):
        (k, p) = g.chon_tep(FX, "HN", None)
        self.assertEqual(k[2], "Q3/2026")
        rows = g.doc_tep(p)
        self.assertEqual(len(rows), 5); self.assertEqual(rows[0]["gia"], 600000)

    def test_khong_khop_nham_dau(self):
        rows = g.doc_tep(g.chon_tep(FX, "HN", None)[1])
        self.assertEqual(g.diem("Cáp điện", "m", next(r for r in rows if r["ten"].startswith("Cấp"))), 0.0)
        self.assertEqual(g.diem("Đá cắt", "viên", next(r for r in rows if r["ten"] == "Cát vàng")), 0.0)
        self.assertGreater(g.diem("Cáp điện", "m", next(r for r in rows if r["ten"].startswith("Cáp"))), 0.3)

    def test_tra(self):
        out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "gia_vat_lieu.py"), "--thu-muc", FX, "tra", "--tinh", "HN", "--tu-khoa", "cáp"],
                             capture_output=True, text=True, encoding="utf-8").stdout
        self.assertIn("Cáp điện", out); self.assertNotIn("Cấp phối", out)


if __name__ == "__main__":
    unittest.main()
