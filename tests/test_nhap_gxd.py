#!/usr/bin/env python3
"""Kiểm thử nhap_du_toan_excel.py trên fixture DutoanGXD1.xlsm (template GXD trống).

Kỳ vọng (xem references/doi-chieu-gxd.md mục 12 và 15.2):
- Cả hai chế độ (--kieu gxd và mặc định skill) đều báo rõ "0 khối đơn giá, 0 công tác",
  thoát mã 2 (không có dữ liệu) và chỉ ghi bao_cao_nhap.md, KHÔNG tạo file dữ liệu rỗng.
- Không còn vùng giá giả V1 = "[8]" (N-5) hay 8 đoạn giả D1–D8 từ các cột hệ số (N-6).

Chạy:  python3 -m unittest tests.test_nhap_gxd -v
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FIXTURE = os.path.join(HERE, "fixtures", "DutoanGXD1.xlsm")
SCRIPT = os.path.join(SKILL, "scripts", "nhap_du_toan_excel.py")


def _chay(kieu):
    tmp = tempfile.mkdtemp()
    ra = os.path.join(tmp, "out")
    cmd = [sys.executable, SCRIPT, "--file", FIXTURE, "--dgct", "Don gia XD",
           "--dt", "Du toan XD", "--ra", ra]
    if kieu:
        cmd += ["--kieu", kieu]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    bao_cao = ""
    p = os.path.join(ra, "bao_cao_nhap.md")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            bao_cao = f.read()
    return r.returncode, sorted(os.listdir(ra)) if os.path.isdir(ra) else [], bao_cao


class TestNhapGXDTrong(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fixture là file nhị phân, không đẩy được lên repo bằng snapshot-push:
        # trên bản clone thiếu fixture thì bỏ qua các test này thay vì lỗi.
        if not os.path.exists(FIXTURE):
            raise unittest.SkipTest(f"thiếu fixture {FIXTURE} (file nhị phân, không có trên repo)")

    def test_kieu_gxd_bang_trong(self):
        code, files, bc = _chay("gxd")
        self.assertEqual(code, 2, "file trống phải thoát mã 2 (không có dữ liệu)")
        self.assertEqual(files, ["bao_cao_nhap.md"], "chỉ ghi báo cáo, không tạo file dữ liệu rỗng")
        self.assertIn("0 khối đơn giá", bc)
        self.assertIn("0 công tác", bc)
        self.assertIn("BẢNG TRỐNG", bc)
        self.assertNotIn('"[8]"', bc)

    def test_kieu_skill_bang_trong(self):
        code, files, bc = _chay(None)
        self.assertEqual(code, 2, "file trống phải thoát mã 2 (không có dữ liệu)")
        self.assertEqual(files, ["bao_cao_nhap.md"], "chỉ ghi báo cáo, không tạo file dữ liệu rỗng")
        self.assertIn("0 khối đơn giá", bc)
        self.assertIn("0 công tác", bc)
        self.assertIn("BẢNG TRỐNG", bc)
        self.assertNotIn('V1 = "[8]"', bc)
        self.assertNotIn("D1–D8", bc)
        self.assertNotIn("Đoạn 8", bc)


if __name__ == "__main__":
    unittest.main()
