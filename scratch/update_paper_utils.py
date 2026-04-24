import os

file_path = r'c:\Users\vijay\Downloads\vsk\I-AI\utils\paper_utils.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Update export_as_docx
start_index = -1
for i, line in enumerate(lines):
    if 'def export_as_docx' in line:
        start_index = i
        break

if start_index != -1:
    new_func = [
        'def export_as_docx(paper_data, template_name="Generic University", font_style="Serif"):\n',
        '    """Export formatted paper as DOCX with section-based column support."""\n',
        '    from docx import Document\n',
        '    from docx.shared import Pt\n',
        '    from docx.enum.text import WD_ALIGN_PARAGRAPH\n',
        '    from docx.oxml.ns import qn\n',
        '    \n',
        '    config = get_template_config(template_name)\n',
        '    doc = Document()\n',
        '    \n',
        '    # Font Setup\n',
        '    font_map = {\n',
        '        "Times New Roman": "Times New Roman", "Arial": "Arial", "Calibri": "Calibri",\n',
        '        "Georgia": "Georgia", "Cambria": "Cambria", "Monospace": "Courier New"\n',
        '    }\n',
        '    word_font = font_map.get(font_style, "Times New Roman")\n',
        '    is_ieee = template_name == "IEEE"\n',
        '\n',
        '    # 1. Title (Full Width)\n',
        '    title = doc.add_heading(paper_data.get("title", "Research Paper"), 0)\n',
        '    title.alignment = WD_ALIGN_PARAGRAPH.CENTER\n',
        '    for run in title.runs:\n',
        '        run.font.name = word_font\n',
        '        run.font.size = Pt(config["title_size"])\n',
        '        run._element.rPr.rFonts.set(qn(\'w:eastAsia\'), word_font)\n',
        '\n',
        '    # 2. Abstract (Full Width)\n',
        '    abs_para = doc.add_paragraph()\n',
        '    run_label = abs_para.add_run("ABSTRACT: ")\n',
        '    run_label.bold = True\n',
        '    run_label.font.name = word_font\n',
        '    \n',
        '    run_text = abs_para.add_run(str(paper_data.get("abstract", "")))\n',
        '    run_text.font.name = word_font\n',
        '    abs_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY\n',
        '\n',
        '    # 3. If IEEE, start a new section for 2-column body\n',
        '    if is_ieee:\n',
        '        new_section = doc.add_section()\n',
        '        sectPr = new_section._sectPr\n',
        '        cols = sectPr.xpath(\'./w:cols\')[0]\n',
        '        cols.set(qn(\'w:num\'), \'2\')\n',
        '        cols.set(qn(\'w:space\'), \'720\') # 0.5 inch gap\n',
        '    \n',
        '    # 4. Main Body Sections\n',
        '    sections = [\n',
        '        ("Keywords", "keywords"), ("Introduction", "introduction"),\n',
        '        ("Literature Review", "lit_review"), ("Methodology", "methodology"),\n',
        '        ("Results & Discussion", "results"), ("Conclusion", "conclusion"),\n',
        '        ("Future Scope", "future_scope"), ("References", "references"),\n',
        '    ]\n',
        '    \n',
        '    for label, key in sections:\n',
        '        content = paper_data.get(key, "")\n',
        '        if not content: continue\n',
        '        \n',
        '        # Section Header\n',
        '        h = doc.add_heading(label.upper(), level=1)\n',
        '        for run in h.runs:\n',
        '            run.font.name = word_font\n',
        '            run.font.size = Pt(config["section_size"])\n',
        '            run.font.color.rgb = None # Standard black\n',
        '            run._element.rPr.rFonts.set(qn(\'w:eastAsia\'), word_font)\n',
        '        \n',
        '        # Section Content\n',
        '        p = doc.add_paragraph(str(content))\n',
        '        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY\n',
        '        for run in p.runs:\n',
        '            run.font.name = word_font\n',
        '            run.font.size = Pt(config["body_size"])\n',
        '            run._element.rPr.rFonts.set(qn(\'w:eastAsia\'), word_font)\n',
        '            \n',
        '    import io\n',
        '    target = io.BytesIO()\n',
        '    doc.save(target)\n',
        '    return target.getvalue()\n'
    ]
    lines[start_index:] = new_func
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully updated paper_utils.py for multi-column export")
else:
    print("Could not find function")
