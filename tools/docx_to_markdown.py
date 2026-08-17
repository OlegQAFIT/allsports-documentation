from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


DOC_META = {
    "partner-panel.md": {
        "lead": "Инструкция для партнеров Allsports по работе с визитами, историей посещений, документами и карточкой спортивного объекта.",
        "overview": [
            ("Для кого", "Партнеры и администраторы объектов"),
            ("Основные разделы", "Визиты, история, документы, описание объекта"),
            ("Формат", "Веб-версия инструкции + исходный DOCX"),
        ],
    },
    "company-panel.md": {
        "lead": "Инструкция по работе с HR порталом Allsports для сценариев B2B, B2C и Copay: от входа в систему до управления сотрудниками, заявками и документами.",
        "overview": [
            ("Для кого", "HR-менеджеры и представители компаний"),
            ("Модели работы", "B2B, B2C и Copay"),
            ("Основные разделы", "Сотрудники, подписки, счета, акты, аудит"),
        ],
    },
    "user-panel-docx.md": {
        "lead": "Руководство для сотрудников с корпоративной подпиской Allsports: регистрация, работа с профилем, способ оплаты и доступ к мобильному приложению.",
        "overview": [
            ("Для кого", "Пользователи моделей B2C и Copay"),
            ("Основные разделы", "Профиль, оплата, приложение, правовая информация"),
            ("Формат", "Веб-руководство + исходный DOCX"),
        ],
    },
    "mobile-app.md": {
        "lead": "Инструкция по мобильному приложению Allsports: установка, вход, поиск объектов, оформление визитов и работа с профилем пользователя.",
        "overview": [
            ("Платформы", "iOS, Android, Huawei AppGallery"),
            ("Основные сценарии", "Установка, авторизация, визиты, профиль"),
            ("Формат", "Веб-руководство + исходный DOCX"),
        ],
    },
}


def iter_block_items(parent: DocxDocument) -> Iterable[Paragraph | Table]:
    body = parent.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "document"


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def escape_md(text: str) -> str:
    return clean_text(text).replace("|", r"\|")


def extract_docx_media(docx_path: Path, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    media_map: dict[str, str] = {}
    with ZipFile(docx_path) as zf:
        for name in zf.namelist():
            if not name.startswith("word/media/"):
                continue
            filename = Path(name).name
            target = output_dir / filename
            target.write_bytes(zf.read(name))
            media_map[filename] = target.name
    return media_map


def paragraph_image_links(
    paragraph: Paragraph,
    image_dir_rel: str,
    media_map: dict[str, str],
) -> list[str]:
    rels = paragraph.part.rels
    image_paths: list[str] = []
    blips = paragraph._element.xpath(".//*[local-name()='blip']")
    for blip in blips:
        embed = blip.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        )
        if not embed or embed not in rels:
            continue
        image_part = rels[embed].target_part
        filename = Path(image_part.partname).name
        if filename not in media_map:
            continue
        image_paths.append(f"{image_dir_rel}/{media_map[filename]}")
    return image_paths


def table_to_markdown(table: Table) -> list[str]:
    rows: list[list[str]] = []
    for row in table.rows:
        rows.append([escape_md(cell.text).replace("\n", "<br>") for cell in row.cells])
    if not rows:
        return []
    width = max(len(r) for r in rows)
    padded = [r + [""] * (width - len(r)) for r in rows]
    lines = [
        "| " + " | ".join(padded[0]) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in padded[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def extract_title_block(doc: Document, fallback_title: str) -> tuple[str, list[str], int]:
    title_lines: list[str] = []
    body_start = 0
    for idx, paragraph in enumerate(doc.paragraphs):
        text = clean_text(paragraph.text)
        if not text:
            continue
        if paragraph.style.name.startswith("Heading"):
            body_start = idx
            break
        if re.search(r"\b20\d{2}\b", text):
            continue
        title_lines.append(text)
    if not title_lines:
        return fallback_title, [], body_start
    title = title_lines[0]
    subtitles = title_lines[1:]
    if title.casefold() == "allsports" and subtitles:
        title = subtitles[0]
        subtitles = subtitles[1:]
        if "allsports" not in title.casefold():
            title = f"{title} Allsports"
    return title, subtitles, body_start


def paragraph_to_markdown(
    paragraph: Paragraph,
    image_dir_rel: str,
    media_map: dict[str, str],
) -> list[str]:
    text = clean_text(paragraph.text)
    style = paragraph.style.name or "Normal"
    lines: list[str] = []

    images = paragraph_image_links(paragraph, image_dir_rel, media_map)
    for image in images:
        lines.append(f"![Иллюстрация]({image})")

    if not text:
        return lines

    if style.startswith("Heading 1"):
        lines.append(f"## {text}")
        return lines
    if style.startswith("Heading 2"):
        lines.append(f"### {text}")
        return lines
    if style.startswith("Heading 3"):
        lines.append(f"#### {text}")
        return lines
    if style == "Подпись к изображению":
        lines.append(f"*{text}*")
        return lines
    if re.match(r"^Рис(\.|унок)", text):
        lines.append(f"*{text}*")
        return lines
    if style == "Intense Quote" or text.startswith("⚠") or text.startswith("ℹ"):
        lines.append(f"> {text}")
        return lines

    ppr = paragraph._p.pPr
    numpr = ppr.numPr if ppr is not None else None
    if numpr is not None:
        lines.append(f"1. {text}")
        return lines
    if style == "List Paragraph":
        lines.append(f"- {text}")
        return lines
    if re.match(r"^\d+\.\s+Раздел", text):
        lines.append(f"## {text}")
        return lines

    lines.append(text)
    return lines


def render_page_chrome(
    target_md: Path,
    docx_download_rel: str,
) -> list[str]:
    meta = DOC_META.get(target_md.name, {})
    lead = meta.get("lead", "Короткое описание документа.")
    overview = meta.get(
        "overview",
        [
            ("Для кого", "Уточните аудиторию документа"),
            ("Основные разделы", "Уточните ключевые сценарии"),
            ("Формат", "Веб-версия + исходный DOCX"),
        ],
    )

    lines = [
        f'<div class="doc-page-actions">',
        f'  <a class="doc-download-link" href="{docx_download_rel}">Скачать исходный DOCX</a>',
        "</div>",
        "",
        '<div class="doc-hero-badge">',
        '  <div class="doc-hero-badge__logo" aria-hidden="true"></div>',
        '  <div class="doc-hero-badge__meta">',
        '    <div class="doc-hero-badge__eyebrow">Руководство пользователя</div>',
        '    <div class="doc-hero-badge__brand">Allsports Documentation</div>',
        "  </div>",
        "</div>",
        "",
        '<div class="doc-page-intro">',
        f'  <p class="doc-page-lead">{lead}</p>',
        '  <div class="doc-page-overview">',
    ]
    for label, value in overview:
        lines.extend(
            [
                '    <div class="doc-page-overview__item">',
                f'      <div class="doc-page-overview__label">{label}</div>',
                f'      <div class="doc-page-overview__value">{value}</div>',
                "    </div>",
            ]
        )
    lines.extend(["  </div>", "</div>", ""])
    return lines


def convert_docx(
    source_docx: Path,
    target_md: Path,
    docx_download_rel: str,
    image_root: Path,
    image_rel_root: str,
) -> None:
    doc = Document(source_docx)
    title, subtitles, _ = extract_title_block(doc, fallback_title=target_md.stem)
    slug = slugify(target_md.stem)
    image_output_dir = image_root / slug
    image_rel_dir = f"{image_rel_root}/{slug}"
    media_map = extract_docx_media(source_docx, image_output_dir)

    lines: list[str] = [f"# {title}", ""]
    lines.extend(render_page_chrome(target_md, docx_download_rel))
    for subtitle in subtitles:
        lines.append(f"_{subtitle}_")
        lines.append("")

    started_body = False
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            style = block.style.name or "Normal"
            text = clean_text(block.text)
            has_images = bool(paragraph_image_links(block, image_rel_dir, media_map))
            if not started_body:
                if style.startswith("Heading"):
                    started_body = True
                elif not has_images:
                    continue
            md_lines = paragraph_to_markdown(block, image_rel_dir, media_map)
            if md_lines:
                lines.extend(md_lines)
                lines.append("")
        else:
            started_body = True
            table_lines = table_to_markdown(block)
            if table_lines:
                lines.extend(table_lines)
                lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    target_md.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()

    repo = Path(args.repo)
    docs_dir = repo / "_assets" / "documents"
    image_root = repo / "_assets" / "images"
    image_rel_root = "_assets/images"

    jobs = [
        (
            docs_dir / "partner-panel-user-guide.docx",
            repo / "partner-panel.md",
            "_assets/documents/partner-panel-user-guide.docx",
        ),
        (
            docs_dir / "company-panel-user-guide-b2b-b2c-copay.docx",
            repo / "company-panel.md",
            "_assets/documents/company-panel-user-guide-b2b-b2c-copay.docx",
        ),
        (
            docs_dir / "user-panel.docx",
            repo / "user-panel-docx.md",
            "_assets/documents/user-panel.docx",
        ),
        (
            docs_dir / "mobile-app-user-guide.docx",
            repo / "mobile-app.md",
            "_assets/documents/mobile-app-user-guide.docx",
        ),
    ]

    for source_docx, target_md, docx_download_rel in jobs:
        convert_docx(source_docx, target_md, docx_download_rel, image_root, image_rel_root)
        print(f"Converted {source_docx.name} -> {target_md.name}")


if __name__ == "__main__":
    main()
