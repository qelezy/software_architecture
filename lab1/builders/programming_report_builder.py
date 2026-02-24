from html import escape
import re

from builders.report_builder import ReportBuilder
from data_models.report_data import ReportData
from data_models.section_content import SectionContent


class ProgrammingReportBuilder(ReportBuilder):
    def build_purpose(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section("Цель работы", data.purpose)
        )

    def build_task(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section("Задание", data.task)
        )

    def build_theory(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Теоретические сведения", data.theory
            )
        )

    def build_setup(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Описание средств разработки", data.setup
            )
        )

    def build_result(self, data: ReportData) -> None:
        content = SectionContent(text=data.result.text, images=data.result.images)
        text_without_images = re.sub(
            r"\[.*?\]\(\s*Рисунок\s+\d+\s*-\s*.*?\)", "", content.text
        ).strip()

        html = ["<h3>Текст программы и результаты выполнения</h3>"]
        if text_without_images:
            html.append(
                "<pre><code>"
                f"{escape(text_without_images)}"
                "</code></pre>"
            )
        for image in content.images:
            caption = f"Рисунок {image.index} - {image.caption}"
            src = image.path.as_posix()
            html.append(
                "<figure>"
                f'<img src="{src}" alt="{escape(caption)}" style="max-width: 100%;">'
                f"<figcaption>{escape(caption)}</figcaption>"
                "</figure>"
            )

        self.parts.append("\n".join(html))

    def build_analysis(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Анализ результатов выполнения программы", data.analysis
            )
        )

    def build_conclusion(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Выводы", data.conclusion
            )
        )
