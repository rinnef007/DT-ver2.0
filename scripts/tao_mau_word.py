#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo 3 template Word cho skill du-toan-xay-dung-vn (W-1/W-2/W-3, Giai đoạn 5).

Chạy:  python scripts/tao_mau_word.py [--ra templates/word]

Định dạng theo quy định văn bản hành chính (Nghị định 30/2020/NĐ-CP): khổ A4,
font Times New Roman cỡ 13, giãn dòng 1,5; lề trên/dưới 2 cm, trái 3 cm, phải 2 cm.
Hệ Style định nghĩa lại tương đương hệ Style GXD (mục 13 báo cáo đối chiếu):
  A Noi dung gxd.vn · Heading 1–4 · Gxd.vn Noi dung Ban can Giua Dam B ·
  Style Hình ảnh · GXD Danh list số · các Style tiêu đề / nơi nhận / chữ ký.
KHÔNG copy file Normal.dotm của Công ty CP Giá Xây Dựng — mọi Style đều tạo mới
bằng python-docx trong script này. Chạy lại script để tạo lại file .docx khi cần sửa.
"""
import argparse
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

FONT = "Times New Roman"
CO_CHU = Pt(13)
CO_CHU_BANG = Pt(12)


def _set_run_font(run, size=CO_CHU, bold=False, italic=False, all_caps=False, underline=False):
    run.font.name = FONT
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(a), FONT)
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.all_caps = all_caps
    run.font.underline = underline


def _para(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6), space_before=Pt(0),
          line_spacing=1.5, first_line_indent=None, keep_next=False):
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_after = space_after
    pf.space_before = space_before
    pf.line_spacing = line_spacing
    pf.widow_control = True
    if first_line_indent is not None:
        pf.first_line_indent = first_line_indent
    if keep_next:
        pf.keep_with_next = True
    return p


def _field(paragraph, instr):
    """Chèn một field Word (TOC, PAGE…) vào đoạn."""
    run = paragraph.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate")
    f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
    run._r.append(f1); run._r.append(it); run._r.append(f2); run._r.append(f3)


def _lap_tieu_de_bang(bang):
    """Lặp lại dòng tiêu đề bảng sang trang mới (kỹ thuật trong sách GXD)."""
    trPr = bang.rows[0]._tr.get_or_add_trPr()
    h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true")
    trPr.append(h)


def _them_bang(doc, tieu_de_cot, dong_du_lieu, do_rong_cot=None):
    bang = doc.add_table(rows=1, cols=len(tieu_de_cot))
    bang.style = "Table Grid"
    bang.alignment = WD_TABLE_ALIGNMENT.CENTER
    bang.autofit = False
    if do_rong_cot:
        for i, w in enumerate(do_rong_cot):
            bang.columns[i].width = Cm(w)
    hdr = bang.rows[0].cells
    for i, t in enumerate(tieu_de_cot):
        p = _para(hdr[i].paragraphs[0], align=WD_ALIGN_PARAGRAPH.CENTER,
                  space_after=Pt(2), line_spacing=1.0)
        _set_run_font(p.add_run(t), size=CO_CHU_BANG, bold=True)
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "D9D9D9")
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    _lap_tieu_de_bang(bang)
    for dong in dong_du_lieu:
        cells = bang.add_row().cells
        for i, gia_tri in enumerate(dong):
            p = _para(cells[i].paragraphs[0], align=WD_ALIGN_PARAGRAPH.CENTER,
                      space_after=Pt(2), line_spacing=1.0)
            _set_run_font(p.add_run(str(gia_tri)), size=CO_CHU_BANG)
    return bang


def _danh_sach_so(doc, muc):
    """Danh sách đánh số theo Style 'GXD Danh list số'."""
    for m in muc:
        p = doc.add_paragraph(style="GXD Danh list số")
        _para(p, space_after=Pt(6), first_line_indent=Cm(1))
        _set_run_font(p.add_run(m))


def _khoi_chu_ky(doc, ben_trai, ben_phai):
    """Khối chữ ký hai cột (bảng không viền)."""
    bang = doc.add_table(rows=2, cols=2)
    for row in bang.rows:
        for cell in row.cells:
            for border in ("top", "left", "bottom", "right", "insideH", "insideV"):
                el = OxmlElement(f"w:{border}")
                el.set(qn("w:val"), "nil"); el.set(qn("w:sz"), "0")
                el.set(qn("w:space"), "0"); el.set(qn("w:color"), "auto")
                cell._tc.get_or_add_tcPr().append(el)
    for i, ten in enumerate((ben_trai, ben_phai)):
        p = _para(bang.cell(0, i).paragraphs[0], align=WD_ALIGN_PARAGRAPH.CENTER,
                  space_after=Pt(2), line_spacing=1.0)
        _set_run_font(p.add_run(ten), bold=True)
        p = _para(bang.cell(1, i).paragraphs[0], align=WD_ALIGN_PARAGRAPH.CENTER,
                  space_after=Pt(2), line_spacing=1.0)
        _set_run_font(p.add_run("(Ký, ghi rõ họ tên)"), italic=True)
    return bang


def _dinh_nghia_styles(doc):
    """Định nghĩa lại hệ Style tương đương GXD (tạo mới, không copy Normal.dotm)."""
    st = doc.styles
    # --- A Noi dung gxd.vn: nội dung thường (style dùng nhiều nhất) ---
    body = st.add_style("A Noi dung gxd.vn", WD_STYLE_TYPE.PARAGRAPH)
    body.base_style = st["Normal"]
    body.font.name = FONT
    body.font.size = CO_CHU
    body.paragraph_format.space_after = Pt(6)
    body.paragraph_format.line_spacing = 1.5
    body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    body.paragraph_format.first_line_indent = Cm(1)
    # --- Heading 1–4: đề mục các cấp, dùng làm mục lục tự động ---
    cau_hinh = {1: (Pt(14), True, False, True), 2: (Pt(13), True, False, False),
                3: (Pt(13), True, True, False), 4: (Pt(13), False, True, False)}
    for cap, (co, dam, nghieng, hoa) in cau_hinh.items():
        h = st[f"Heading {cap}"]
        h.font.name = FONT
        h.font.size = co
        h.font.bold = dam
        h.font.italic = nghieng
        h.font.all_caps = hoa
        h.paragraph_format.space_before = Pt(12 if cap == 1 else 6)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.line_spacing = 1.5
        h.paragraph_format.keep_with_next = True
    # --- Gxd.vn Noi dung Ban can Giua Dam B: nội dung bảng, căn giữa, đậm ---
    bang_st = st.add_style("Gxd.vn Noi dung Ban can Giua Dam B", WD_STYLE_TYPE.PARAGRAPH)
    bang_st.base_style = st["Normal"]
    bang_st.font.name = FONT
    bang_st.font.size = CO_CHU_BANG
    bang_st.font.bold = True
    bang_st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    bang_st.paragraph_format.space_after = Pt(2)
    bang_st.paragraph_format.line_spacing = 1.0
    # --- Style Hình ảnh: ảnh trong văn bản, căn giữa ---
    anh = st.add_style("Style Hình ảnh", WD_STYLE_TYPE.PARAGRAPH)
    anh.base_style = st["Normal"]
    anh.font.name = FONT
    anh.font.size = Pt(11)
    anh.font.italic = True
    anh.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    anh.paragraph_format.space_after = Pt(6)
    anh.paragraph_format.space_before = Pt(6)
    # --- GXD Danh list số: danh sách đánh số ---
    ds = st.add_style("GXD Danh list số", WD_STYLE_TYPE.PARAGRAPH)
    ds.base_style = st["List Number"]
    ds.font.name = FONT
    ds.font.size = CO_CHU
    ds.paragraph_format.space_after = Pt(6)
    ds.paragraph_format.line_spacing = 1.5
    ds.paragraph_format.left_indent = Cm(1.25)
    ds.paragraph_format.first_line_indent = Cm(-0.5)
    # --- Style tiêu đề / nơi nhận / chữ ký ---
    qh = st.add_style("Tieu de Quoc hieu", WD_STYLE_TYPE.PARAGRAPH)
    qh.base_style = st["Normal"]
    qh.font.name = FONT; qh.font.size = CO_CHU; qh.font.bold = True
    qh.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    qh.paragraph_format.space_after = Pt(0)
    qh.paragraph_format.line_spacing = 1.0
    cq = st.add_style("Tieu de Co quan", WD_STYLE_TYPE.PARAGRAPH)
    cq.base_style = st["Normal"]
    cq.font.name = FONT; cq.font.size = CO_CHU; cq.font.bold = True
    cq.font.size = CO_CHU
    cq.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cq.paragraph_format.space_after = Pt(6)
    cq.paragraph_format.line_spacing = 1.0
    nn = st.add_style("Noi nhan", WD_STYLE_TYPE.PARAGRAPH)
    nn.base_style = st["Normal"]
    nn.font.name = FONT; nn.font.size = Pt(12)
    nn.paragraph_format.space_after = Pt(0)
    nn.paragraph_format.line_spacing = 1.0
    return st


def _khoi_tai_lieu(doc, tieu_de):
    """Khổ giấy, lề, header/footer, cập nhật field khi mở."""
    doc.core_properties.title = tieu_de
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(2.0)
    sec.header_distance = Cm(1.0)
    sec.footer_distance = Cm(1.0)
    # footer: số trang ở giữa
    p = _para(sec.footer.paragraphs[0], align=WD_ALIGN_PARAGRAPH.CENTER,
              space_after=Pt(0), line_spacing=1.0)
    _set_run_font(p.add_run("Trang "), size=Pt(11))
    _field(p, "PAGE")
    # cập nhật field (mục lục, số trang) khi mở file trong Word
    settings = doc.settings.element
    upd = OxmlElement("w:updateFields"); upd.set(qn("w:val"), "true")
    settings.append(upd)
    return sec


def _noi_dung(doc, text, style="A Noi dung gxd.vn", **kw):
    p = doc.add_paragraph(style=style)
    _para(p, **kw)
    _set_run_font(p.add_run(text))
    return p


def _tieu_de_cap(doc, text, cap=1):
    p = doc.add_heading(level=cap)
    _set_run_font(p.add_run(text))
    return p


def _quoc_hieu(doc, co_quan):
    p = doc.add_paragraph(style="Tieu de Quoc hieu")
    _set_run_font(p.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"))
    p = doc.add_paragraph(style="Tieu de Quoc hieu")
    _set_run_font(p.add_run("Độc lập – Tự do – Hạnh phúc"))
    p = doc.add_paragraph(style="Tieu de Co quan")
    _set_run_font(p.add_run(co_quan))
    return p


def _muc_luc(doc):
    p = doc.add_paragraph()
    _para(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(6))
    _set_run_font(p.add_run("MỤC LỤC"), bold=True)
    p = doc.add_paragraph()
    _field(p, 'TOC \\o "1-3" \\h \\z \\u')
    doc.add_paragraph().add_run(
        "(Nhấn chuột phải vào mục lục → Update Field → Update entire table để cập nhật sau khi soạn xong.)"
    ).italic = True


# ---------------------------------------------------------------- W1
def lam_w1(ra):
    doc = Document()
    _dinh_nghia_styles(doc)
    _khoi_tai_lieu(doc, "Thuyết minh dự toán / Báo cáo thẩm tra dự toán")
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(120))
    _set_run_font(p.add_run("[TÊN DỰ ÁN]"), size=Pt(16), bold=True, all_caps=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER)
    _set_run_font(p.add_run("[TÊN CÔNG TRÌNH / HẠNG MỤC]"), size=Pt(14), bold=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(24))
    _set_run_font(p.add_run("THUYẾT MINH DỰ TOÁN"), size=Pt(16), bold=True, all_caps=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER)
    _set_run_font(p.add_run("(Kèm theo Báo cáo thẩm tra dự toán — xóa dòng này nếu chỉ làm thuyết minh)"),
                  italic=True)
    _noi_dung(doc, "Chủ đầu tư: [tên chủ đầu tư].", first_line_indent=None)
    _noi_dung(doc, "Đơn vị lập dự toán: [tên đơn vị].", first_line_indent=None)
    _noi_dung(doc, "Địa điểm: [địa điểm]. Thời gian lập: tháng [..]/năm [....].", first_line_indent=None)
    doc.add_page_break()
    _muc_luc(doc)
    doc.add_page_break()
    _tieu_de_cap(doc, "I. Căn cứ pháp lý", 1)
    _noi_dung(doc, "Dự toán được lập trên các căn cứ sau (ghi đủ số hiệu có hậu tố và bộ ban hành):")
    _danh_sach_so(doc, [
        "Luật Xây dựng số 50/2014/QH13 và Luật sửa đổi, bổ sung một số điều của Luật Xây dựng số 62/2020/QH14.",
        "Nghị định số 06/2021/NĐ-CP ngày 26/01/2021 của Chính phủ quy định chi tiết một số nội dung về quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng.",
        "Nghị định số 10/2021/NĐ-CP ngày 09/02/2021 của Chính phủ về quản lý chi phí đầu tư xây dựng.",
        "Nghị định số 206/2026/NĐ-CP ngày [..] của Chính phủ quy định chi tiết một số điều của Luật Xây dựng về quản lý chi phí đầu tư xây dựng.",
        "Thông tư số 36/2026/TT-BXD ngày [..] của Bộ Xây dựng về quản lý chi phí đầu tư xây dựng.",
        "Thông tư số 37/2026/TT-BXD ngày [..] của Bộ Xây dựng quy định về định mức, giá xây dựng.",
        "Thông tư số 38/2026/TT-BXD ngày [..] của Bộ Xây dựng ban hành định mức xây dựng.",
        "[Bổ sung: quyết định phê duyệt dự án, công bố giá của Sở Xây dựng, báo giá nhà cung cấp…]",
    ])
    _tieu_de_cap(doc, "II. Tóm tắt nội dung dự toán", 1)
    _noi_dung(doc, "Tổng mức đầu tư / tổng dự toán (lấy từ sheet TH_CPXD của file Excel do skill xuất):")
    _them_bang(doc, ["STT", "Nội dung chi phí", "Giá trị (đồng)", "Ghi chú"],
               [["I", "Chi phí trực tiếp (VL + NC + M)", "[dán từ TH_CPXD]", ""],
                ["II", "Chi phí gián tiếp", "[dán từ TH_CPXD]", ""],
                ["III", "Thu nhập chịu thuế tính trước", "[dán từ TH_CPXD]", ""],
                ["IV", "Thuế GTGT", "[dán từ TH_CPXD]", ""],
                ["", "TỔNG CỘNG (sau thuế)", "[dán từ TH_CPXD]", ""],
                ["V", "Chi phí nhà tạm", "[dán từ TH_CPXD]", ""]],
               do_rong_cot=[1.5, 7.0, 4.0, 3.5])
    _tieu_de_cap(doc, "III. Kết quả thẩm tra", 1)
    _noi_dung(doc, "Đơn vị thẩm tra đối chiếu khối lượng, định mức, đơn giá và tỷ lệ theo từng nội dung:")
    _them_bang(doc, ["STT", "Nội dung thẩm tra", "Kết quả", "Kiến nghị"],
               [["1", "Khối lượng", "[Đạt / Chưa đạt — ghi rõ]", ""],
                ["2", "Định mức áp dụng (TT 38/2026)", "[Đạt / Chưa đạt — ghi rõ]", ""],
                ["3", "Đơn giá vật liệu, nhân công, ca máy", "[Đạt / Chưa đạt — ghi rõ]", ""],
                ["4", "Tỷ lệ C, TT, TL, GTGT", "[Đạt / Chưa đạt — ghi rõ]", ""]],
               do_rong_cot=[1.5, 6.0, 5.0, 3.5])
    _tieu_de_cap(doc, "IV. Kết luận và kiến nghị", 1)
    _noi_dung(doc, "[Kết luận: dự toán đủ điều kiện trình phê duyệt / cần chỉnh sửa theo các kiến nghị trên.]")
    _noi_dung(doc, "[Kiến nghị cụ thể (nếu có): …]")
    doc.add_paragraph()
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=Pt(0))
    _set_run_font(p.add_run("[Địa danh], ngày [..] tháng [..] năm [....]"), italic=True)
    _khoi_chu_ky(doc, "NGƯỜI LẬP", "NGƯỜI CHỦ TRÌ")
    doc.save(ra)
    return ra


# ---------------------------------------------------------------- W2
def lam_w2(ra):
    doc = Document()
    _dinh_nghia_styles(doc)
    _khoi_tai_lieu(doc, "Biên bản nghiệm thu / Biên bản hiện trường")
    _quoc_hieu(doc, "[TÊN CƠ QUAN / CHỦ ĐẦU TƯ]")
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(12))
    _set_run_font(p.add_run("BIÊN BẢN NGHIỆM THU"), size=Pt(14), bold=True, all_caps=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER)
    _set_run_font(p.add_run("[Nghiệm thu công việc / bộ phận công trình / giai đoạn — ghi rõ]"), italic=True)
    _noi_dung(doc, "Hôm nay, ngày [..] tháng [..] năm [....], tại [địa điểm], chúng tôi gồm:", first_line_indent=None)
    _tieu_de_cap(doc, "I. Thành phần", 1)
    _them_bang(doc, ["STT", "Họ và tên", "Chức vụ", "Đơn vị", "Chữ ký"],
               [["1", "", "", "", ""],
                ["2", "", "", "", ""],
                ["3", "", "", "", ""]],
               do_rong_cot=[1.5, 4.5, 3.5, 4.0, 2.5])
    p = doc.add_paragraph(style="Style Hình ảnh")
    _set_run_font(p.add_run("[Chèn ảnh hiện trường / logo tại đây — áp Style Hình ảnh]"))
    _tieu_de_cap(doc, "II. Nội dung nghiệm thu", 1)
    _danh_sach_so(doc, [
        "Công trình / hạng mục: [tên].",
        "Công việc nghiệm thu: [tên công việc, khối lượng, vị trí].",
        "Hồ sơ kèm theo: [bản vẽ, biên bản, kết quả thí nghiệm…].",
        "Kết quả kiểm tra tại hiện trường: [ghi rõ].",
    ])
    _tieu_de_cap(doc, "III. Kết luận", 1)
    _noi_dung(doc, "[Đồng ý nghiệm thu / nghiệm thu có điều kiện / không nghiệm thu — ghi rõ lý do và yêu cầu khắc phục (nếu có).]")
    doc.add_paragraph()
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=Pt(0))
    _set_run_font(p.add_run("[Địa danh], ngày [..] tháng [..] năm [....]"), italic=True)
    _khoi_chu_ky(doc, "ĐẠI DIỆN CHỦ ĐẦU TƯ", "ĐẠI DIỆN NHÀ THẦU")
    doc.add_paragraph()
    _khoi_chu_ky(doc, "ĐẠI DIỆN TƯ VẤN GIÁM SÁT", "ĐẠI DIỆN ĐƠN VỊ THIẾT KẾ")
    doc.save(ra)
    return ra


# ---------------------------------------------------------------- W3
def lam_w3(ra):
    doc = Document()
    _dinh_nghia_styles(doc)
    _khoi_tai_lieu(doc, "Tờ trình / Quyết định / Công văn")
    _quoc_hieu(doc, "[TÊN CƠ QUAN BAN HÀNH]")
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER, space_before=Pt(12))
    _set_run_font(p.add_run("[TỜ TRÌNH / QUYẾT ĐỊNH / CÔNG VĂN — chọn một, xóa hai loại còn lại]"),
                  size=Pt(14), bold=True, all_caps=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER)
    _set_run_font(p.add_run("V/v [trích yếu: phê duyệt dự toán / thẩm định…]"), bold=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.CENTER)
    _set_run_font(p.add_run("Số: [....]/[ký hiệu]"), italic=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.RIGHT)
    _set_run_font(p.add_run("[Địa danh], ngày [..] tháng [..] năm [....]"), italic=True)
    _noi_dung(doc, "Kính gửi: [cơ quan / người nhận].", first_line_indent=None)
    _noi_dung(doc, "Căn cứ [văn bản căn cứ — ghi đủ số hiệu có hậu tố và bộ ban hành];")
    _noi_dung(doc, "[Tên cơ quan] trình / quyết định / đề nghị như sau:")
    _danh_sach_so(doc, [
        "[Nội dung 1: …]",
        "[Nội dung 2: …]",
        "[Nội dung 3: …]",
    ])
    _noi_dung(doc, "[Kính trình / Đề nghị cơ quan có thẩm quyền xem xét, phê duyệt.]")
    doc.add_paragraph()
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=Pt(0))
    _set_run_font(p.add_run("[CHỨC VỤ NGƯỜI KÝ]"), bold=True, all_caps=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=Pt(0))
    _set_run_font(p.add_run("(Ký, đóng dấu, ghi rõ họ tên)"), italic=True)
    p = _para(doc.add_paragraph(), align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=Pt(48))
    _set_run_font(p.add_run("[Họ và tên người ký]"), bold=True)
    p = doc.add_paragraph(style="Noi nhan")
    _set_run_font(p.add_run("Nơi nhận:"), bold=True)
    for dong in ["- Như trên;",
                 "- [Cơ quan liên quan];",
                 "- Lưu: VT, [phòng ban]."]:
        p = doc.add_paragraph(style="Noi nhan")
        _set_run_font(p.add_run(dong))
    doc.save(ra)
    return ra


def main():
    ap = argparse.ArgumentParser(description="Tạo 3 template Word (W1/W2/W3) cho skill du-toan-xay-dung-vn")
    ap.add_argument("--ra", default="templates/word", help="Thư mục chứa file .docx")
    a = ap.parse_args()
    thu_muc = Path(a.ra)
    thu_muc.mkdir(parents=True, exist_ok=True)
    for ten, ham in (("W1-thuyet-minh-bao-cao-tham-tra.docx", lam_w1),
                     ("W2-bien-ban-nghiem-thu.docx", lam_w2),
                     ("W3-to-trinh-quyet-dinh-cong-van.docx", lam_w3)):
        p = thu_muc / ten
        ham(str(p))
        print(f"Đã tạo {p}")


if __name__ == "__main__":
    main()
