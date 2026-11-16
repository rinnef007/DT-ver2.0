#!/usr/bin/env python3
"""Kiểm thử hồi quy: chạy lại toàn bộ 6 ví dụ và so tổng với baseline đã kiểm chứng.

Tổng kỳ vọng (đồng, đã kiểm chứng đến đồng nhiều lần, lần gần nhất 16/11/2026):
- vi-du: GXD 140.434.146
- vi-du-tt38: GXD 87.295.481
- vi-du-doan: TONG sau thuế 151.531.785
- vi-du-tt40: GXD 104.694.588
- vi-du-khao-sat: TONG sau thuế 13.115.401
- vi-du-nha-de-xe: GXD 287.562.073 (đổi 16/11/2026 sau khi áp đề xuất dữ liệu GĐ2: AF.11310/AF.12510/AK.12222 đủ dòng, AF.51122 -> AF.81122)

Lệnh `tinh` ghi file `<out>_doi_chieu.json` cạnh file .xlsx. Hai dạng cấu trúc:
- ví dụ 1 hạng mục: GXD ở cấp cao nhất của JSON;
- ví dụ nhiều hạng mục: tổng ở `tong_hop["TONG"][2]`.

Chạy:  python3 -m unittest tests.test_examples -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

EXPECTED = {
    "vi-du": 140434146,
    "vi-du-tt38": 87295481,
    "vi-du-doan": 151531785,
    "vi-du-tt40": 104694588,
    "vi-du-khao-sat": 13115401,
    "vi-du-nha-de-xe": 287562073,
}


def _tong_sau_thue(data_dir):
    """Chạy tinh cho một ví dụ, trả về tổng sau thuế (đồng, làm tròn)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.xlsx")
        cmd = [
            sys.executable,
            os.path.join(SKILL, "scripts", "dutoan.py"),
            "tinh",
            "--data", os.path.join(SKILL, "data", data_dir),
            "--khoi-luong", os.path.join(SKILL, "data", data_dir, "khoi_luong.csv"),
            "--config", os.path.join(SKILL, "data", data_dir, "config_du_toan.json"),
            "--out", out,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=SKILL)
        self_err = res.stderr.strip()
        if res.returncode != 0:
            raise AssertionError(f"tinh {data_dir} thoát mã {res.returncode}: {self_err[-500:]}")
        with open(os.path.join(tmp, "out_doi_chieu.json"), encoding="utf-8") as f:
            doi_chieu = json.load(f)
    if "GXD" in doi_chieu:
        return round(doi_chieu["GXD"])
    tong = doi_chieu.get("tong_hop", {}).get("TONG")
    if tong is None:
        raise AssertionError(f"{data_dir}: không tìm thấy GXD/TONG trong doi_chieu.json")
    return round(tong[2])


class TestExamples(unittest.TestCase):
    def test_tat_ca_vi_du_khop_baseline(self):
        for ten, ky_vong in EXPECTED.items():
            with self.subTest(vi_du=ten):
                tong = _tong_sau_thue(ten)
                self.assertEqual(
                    tong, ky_vong,
                    f"{ten}: tổng {tong:,} khác baseline {ky_vong:,}",
                )


if __name__ == "__main__":
    unittest.main()
