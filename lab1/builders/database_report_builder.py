from builders.report_builder import ReportBuilder
from data_models.report_data import ReportData


class DatabaseReportBuilder(ReportBuilder):
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
                "Теоретические сведения по базам данных", data.theory
            )
        )

    def build_setup(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Описание используемой СУБД и структуры базы данных", data.setup
            )
        )

    def build_result(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Результаты работы", data.result
            )
        )

    def build_analysis(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Анализ результатов работы", data.analysis
            )
        )

    def build_conclusion(self, data: ReportData) -> None:
        self.parts.append(
            self.render_section(
                "Выводы", data.conclusion
            )
        )
