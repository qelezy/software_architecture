from dataclasses import dataclass
from data_models.section_content import SectionContent


@dataclass
class ReportData:
    subject: str
    work_number: int
    work_theme: str
    student_name: str
    student_group: str
    teacher_name: str
    purpose: SectionContent
    task: SectionContent
    theory: SectionContent
    setup: SectionContent
    result: SectionContent
    analysis: SectionContent
    conclusion: SectionContent

