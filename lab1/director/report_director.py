from builders.report_builder import ReportBuilder
from data_models.report_data import ReportData


class ReportDirector:
    def __init__(self, builder: ReportBuilder) -> None:
        self.builder = builder

    def set_builder(self, builder: ReportBuilder) -> None:
        self.builder = builder

    def construct_report(self, data: ReportData) -> str:
        self.builder.reset()
        self.builder.build_header(data)
        self.builder.build_purpose(data)
        self.builder.build_task(data)
        self.builder.build_theory(data)
        self.builder.build_setup(data)
        self.builder.build_result(data)
        self.builder.build_analysis(data)
        self.builder.build_conclusion(data)
        return self.builder.get_result()

