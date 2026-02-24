from abc import ABC, abstractmethod
from typing import List
from html import escape
import re

from data_models.report_data import ReportData
from data_models.section_content import SectionContent, ImageEntry


class ReportBuilder(ABC):
    def __init__(self) -> None:
        self.parts: List[str] = []

    def reset(self) -> None:
        self.parts = []

    def render_section(self, title: str, content: SectionContent) -> str:
        html_parts: List[str] = [f"<h3>{escape(title)}</h3>"]

        text = content.text or ""
        lines = text.splitlines()

        index_to_image = {image.index: image for image in content.images}
        used_images: set[int] = set()

        placeholder_pattern = re.compile(
            r"\[(?P<path>[^\]]+)]\(\s*Рисунок\s+(?P<index>\d+)\s*-\s*([^)]+)\)"
        )

        paragraph_lines: List[str] = []

        for line in lines:
            match = placeholder_pattern.search(line)
            if not match:
                paragraph_lines.append(line)
                continue

            before = line[: match.start()].strip()
            if before:
                paragraph_lines.append(before)

            if paragraph_lines:
                paragraph_text = "\n".join(paragraph_lines).strip()
                if paragraph_text:
                    html_parts.append(
                        f"<p>{escape(paragraph_text).replace(chr(10), '<br>')}</p>"
                    )
                paragraph_lines = []

            idx = int(match.group("index"))
            image: ImageEntry | None = index_to_image.get(idx)
            if image is not None:
                used_images.add(idx)
                caption = f"Рисунок {image.index} - {image.caption}"
                src = image.path.as_posix()
                html_parts.append(
                    "<figure>"
                    f'<img src="{src}" alt="{escape(caption)}" style="max-width: 100%;">'
                    f"<figcaption>{escape(caption)}</figcaption>"
                    "</figure>"
                )

            after = line[match.end() :].strip()
            if after:
                paragraph_lines.append(after)

        if paragraph_lines:
            paragraph_text = "\n".join(paragraph_lines).strip()
            if paragraph_text:
                html_parts.append(
                    f"<p>{escape(paragraph_text).replace(chr(10), '<br>')}</p>"
                )

        for image in content.images:
            if image.index in used_images:
                continue
            caption = f"Рисунок {image.index} - {image.caption}"
            src = image.path.as_posix()
            html_parts.append(
                "<figure>"
                f'<img src="{src}" alt="{escape(caption)}" style="max-width: 100%;">'
                f"<figcaption>{escape(caption)}</figcaption>"
                "</figure>"
            )

        return "\n".join(html_parts)

    def build_header(self, data: ReportData) -> None:
        self.parts.append(
            f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Лабораторная работа №{data.work_number}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    h1 {{ text-align: center; margin: 4px 0 }}
    h2.title-line {{ text-align: center; margin: 4px 0; }}
    p.meta-line {{ text-align: justify; margin: 4px 0; }}
    h3 {{ text-align: justify; margin-top: 24px; }}
    p {{ text-align: justify; }}
    figure {{ text-align: center; margin: 20px auto; }}
    figcaption {{ font-size: 0.9em; color: #555; }}
    pre {{ background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>ЛАБОРАТОРНАЯ РАБОТА №{data.work_number}</h1>
  <h2 class="title-line">по дисциплине "{escape(data.subject)}"</h2>
  <h2 class="title-line">на тему "{escape(data.work_theme)}"</h2>
  <p class="meta-line">Студент группы {escape(data.student_group)} {escape(data.student_name)}</p>
  <p class="meta-line">Руководитель {escape(data.teacher_name)}</p>
  <hr>
"""
        )
    @abstractmethod
    def build_purpose(self, data: ReportData) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_task(self, data: ReportData) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_theory(self, data: ReportData) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_setup(self, data: ReportData) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_result(self, data: ReportData) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_analysis(self, data: ReportData) -> None:
        raise NotImplementedError

    @abstractmethod
    def build_conclusion(self, data: ReportData) -> None:
        raise NotImplementedError

    def get_result(self) -> str:
        return "\n".join(self.parts) + "\n</body>\n</html>"


