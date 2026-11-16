#!/usr/bin/env python3
"""Kiểm thử soat_file_excel.py trên fixture DutoanGXD1.xlsm (template GXD 2026, 61 sheet).

Các phát hiện kỳ vọng đều đã kiểm chứng bằng đọc công thức thô (xem
references/doi-chieu-gxd.md mục 4.1 và 11):
- E1: sheet ẩn Config có 17 ô #REF! (cần --ca-sheet-an mới thấy đủ tọa độ);
- E6 (chạy mặc định): Config vẫn phải hiện 17 ô kèm tọa độ mẫu;
- E7: DMTL!B952 trích TT 60/2025, TMDT-SVDT!M141 trích NĐ 10/2021;
- E5: DMTL cột Q có số nhập tay giữa công thức;
- E4: DMTL có số dạng chữ dấu phẩy thập phân trong bảng tra cứu;
- E10: THCP xay dung D38 =SUM(D39:D41) trong khi nhãn ghi VL+NC+M;
- E11: THCP xay dung D46 (dòng LT) trống giữa các công thức;
- E12: THCP xay dung D39 nhãn ghi C+LT+TT nhưng công thức =D11 (GT = C+TT).

Chạy:  python3 -m unittest tests.test_soat_gxd -v
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from soat_file_excel import soat_file  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "DutoanGXD1.xlsm")


def _muc(rep, ma):
    """Trả về khối text của mục E.. trong báo cáo (từ dòng '### E..' đến mục tiếp theo)."""
    lines = rep.splitlines()
    bat, ket = None, len(lines)
    for i, ln in enumerate(lines):
        if ln.startswith(f"### {ma} "):
            bat = i
        elif bat is not None and ln.startswith("### "):
            ket = i
            break
    return "\n".join(lines[bat:ket]) if bat is not None else ""


class TestSoatGXD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fixture là file nhị phân, không đẩy được lên repo bằng snapshot-push:
        # trên bản clone thiếu fixture thì bỏ qua các test này thay vì lỗi.
        if not os.path.exists(FIXTURE):
            raise unittest.SkipTest(f"thiếu fixture {FIXTURE} (file nhị phân, không có trên repo)")
        cls.rep_all = soat_file(FIXTURE, ca_sheet_an=True)
        cls.rep_mac_dinh = soat_file(FIXTURE, ca_sheet_an=False)

    def test_e1_config_17_ref(self):
        e1 = _muc(self.rep_all, "E1")
        self.assertIn("`Config`", e1)
        self.assertIn("#REF! × 17", e1)
        for toa_do in ("AB1", "AE1", "AG1", "AH1", "AT1", "AZ1"):
            self.assertIn(toa_do, e1, f"thiếu tọa độ {toa_do} trong E1 Config")

    def test_e6_mac_dinh_co_toa_do(self):
        e6 = _muc(self.rep_mac_dinh, "E6")
        self.assertIn("`Config`", e6)
        self.assertIn("17", e6)
        self.assertIn("AB1", e6, "E6 phải liệt kê tọa độ mẫu, không chỉ đếm số lượng")

    def test_e7_van_ban_het_hieu_luc(self):
        e7 = _muc(self.rep_all, "E7")
        self.assertIn("`DMTL`!B952", e7)
        self.assertIn("60/2025", e7)
        self.assertIn("`TMDT-SVDT`!M141", e7)
        self.assertIn("10/2021", e7)

    def test_e5_dmtl_cot_q(self):
        e5 = _muc(self.rep_all, "E5")
        self.assertIn("`DMTL`", e5)
        self.assertIn("cột Q", e5)

    def test_e4_dmtl_bang_tra_cuu(self):
        e4 = _muc(self.rep_all, "E4")
        self.assertIn("`DMTL`", e4)
        self.assertIn("BẢNG TRA CỨU", e4)
        self.assertIn("VLOOKUP", e4)

    def test_e10_d38_sum_sai_pham_vi(self):
        e10 = _muc(self.rep_all, "E10")
        self.assertIn("`THCP xay dung`!D38", e10)
        self.assertIn("VL+NC+M", e10)
        self.assertIn("SUM(D39:D41)", e10)

    def test_e11_d46_trong(self):
        e11 = _muc(self.rep_all, "E11")
        self.assertIn("`THCP xay dung`!D46", e11)

    def test_e12_d39_nhan_mau_thuan(self):
        e12 = _muc(self.rep_all, "E12")
        self.assertIn("`THCP xay dung`!D39", e12)
        self.assertIn("C+LT+TT", e12)
        self.assertIn("LT", e12)


if __name__ == "__main__":
    unittest.main()
