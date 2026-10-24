import os
import re
import zipfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape


ROOT = r"D:/Research"
INPUT_MD = os.path.join(ROOT, "FINAL_THESIS_UPDATED.md")
OUTPUT_DOCX = os.path.join(ROOT, "FINAL_THESIS_UPDATED.docx")


def p(text, style=None, spacing_240=True, bold=False):
    style_xml = f"<w:pStyle w:val=\"{style}\"/>" if style else ""
    spacing_xml = "<w:spacing w:line=\"360\" w:lineRule=\"auto\"/>" if spacing_240 else "<w:spacing w:line=\"240\" w:lineRule=\"auto\"/>"
    rpr = "<w:b/>" if bold else ""
    t = escape(text)
    if not t:
        return f"<w:p><w:pPr>{style_xml}{spacing_xml}</w:pPr></w:p>"
    return (
        f"<w:p><w:pPr>{style_xml}{spacing_xml}</w:pPr>"
        f"<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space=\"preserve\">{t}</w:t></w:r></w:p>"
    )


def is_chapter(line: str) -> bool:
    return bool(re.match(r"^CHAPTER\s+\d+:", line))


def is_section(line: str) -> bool:
    return bool(re.match(r"^\d+\.\d+\s+", line))


def is_subsection(line: str) -> bool:
    return bool(re.match(r"^\d+\.\d+\.\d+\s+", line))


def parse_md_to_paragraphs(lines):
  out = []
  in_abstract = False

  for raw in lines:
    line = raw.rstrip("\n").rstrip("\r")

    if line.strip() == "---":
      out.append(p("", style="BodyText"))
      continue

    if not line.strip():
      out.append(p("", style="BodyText"))
      continue

    if line.strip() == "ABSTRACT":
      in_abstract = True
      out.append(p(line.strip(), style="ChapterHeading", bold=True))
      continue

    if line.strip() == "ACKNOWLEDGEMENTS":
      in_abstract = False
      out.append(p(line.strip(), style="ChapterHeading", bold=True))
      continue

    if line.startswith("![") and "](" in line and line.endswith(")"):
      out.append(p("[Figure] " + line, style="BodyText"))
      continue

    if line.startswith("|") and line.endswith("|"):
      txt = " | ".join([c.strip() for c in line.strip("|").split("|")])
      out.append(p(txt, style="TableText", spacing_240=False))
      continue

    if line.lstrip().startswith("- "):
      out.append(p("• " + line.lstrip()[2:], style="BodyText"))
      continue

    if is_chapter(line.strip()):
      out.append(p(line.strip().upper(), style="ChapterHeading", bold=True))
      continue

    if is_subsection(line.strip()):
      out.append(p(line.strip(), style="SubSectionHeading", bold=True))
      continue

    if is_section(line.strip()):
      out.append(p(line.strip(), style="SectionHeading", bold=True))
      continue

    if re.match(r"^[A-Z][A-Z\s:&\-]+$", line.strip()):
      out.append(p(line.strip(), style="ChapterHeading", bold=True))
      continue

    if in_abstract:
      out.append(p(line, style="AbstractBody", spacing_240=False))
    else:
      out.append(p(line, style="BodyText"))

  return out


def build_document_xml(paragraphs_xml):
    body = "".join(paragraphs_xml)
    # Margins: left/bottom 40mm, top/right 25mm converted to twips.
    # 1 inch = 25.4mm, 1 inch = 1440 twips.
    # 40mm -> 2268 twips, 25mm -> 1417 twips.
    sect = (
        "<w:sectPr>"
        "<w:pgSz w:w=\"11906\" w:h=\"16838\"/>"
        "<w:pgMar w:top=\"1417\" w:right=\"1417\" w:bottom=\"2268\" w:left=\"2268\" w:header=\"708\" w:footer=\"708\" w:gutter=\"0\"/>"
        "</w:sectPr>"
    )
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" mc:Ignorable=\"w14 wp14\">"
        "<w:body>"
        + body
        + sect
        + "</w:body></w:document>"
    )


def build_styles_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:line="360" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>

  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="ChapterHeading">
    <w:name w:val="Chapter Heading"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:b/>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="SectionHeading">
    <w:name w:val="Section Heading"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:b/>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="SubSectionHeading">
    <w:name w:val="Subsection Heading"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:b/>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="BodyText">
    <w:name w:val="Body Text"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="AbstractBody">
    <w:name w:val="Abstract Body"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr>
      <w:spacing w:line="240" w:lineRule="auto"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="TableText">
    <w:name w:val="Table Text"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
      <w:sz w:val="20"/>
      <w:szCs w:val="20"/>
    </w:rPr>
  </w:style>
</w:styles>
"""


def build_content_types_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def build_root_rels_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def build_document_rels_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""


def build_app_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office Word</Application>
</Properties>
"""


def build_core_xml():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>AI-Based Poultry Farm Management System</dc:title>
  <dc:creator>Samaraweera S N S</dc:creator>
  <cp:lastModifiedBy>GitHub Copilot</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def main():
    with open(INPUT_MD, "r", encoding="utf-8") as f:
        lines = f.readlines()

    paragraphs = parse_md_to_paragraphs(lines)

    with zipfile.ZipFile(OUTPUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", build_content_types_xml())
        z.writestr("_rels/.rels", build_root_rels_xml())
        z.writestr("word/document.xml", build_document_xml(paragraphs))
        z.writestr("word/styles.xml", build_styles_xml())
        z.writestr("word/_rels/document.xml.rels", build_document_rels_xml())
        z.writestr("docProps/app.xml", build_app_xml())
        z.writestr("docProps/core.xml", build_core_xml())

    print(f"Created: {OUTPUT_DOCX}")


if __name__ == "__main__":
    main()
