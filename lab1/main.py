import sys
import re
from pathlib import Path
from typing import List

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)

from builders.database_report_builder import DatabaseReportBuilder
from builders.network_report_builder import NetworkReportBuilder
from builders.programming_report_builder import ProgrammingReportBuilder
from data_models.report_data import ReportData
from data_models.section_content import SectionContent, ImageEntry
from director.report_director import ReportDirector


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.load_ui()
        self.init_state()
        self.setup_connections()

    def load_ui(self) -> None:
        ui_file = QFile("ui/mainwindow.ui")
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось открыть файл UI: {ui_file.errorString()}"
            )
            sys.exit(-1)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        if not self.ui:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить UI")
            sys.exit(-1)

        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("Генератор отчетов")

    def init_state(self) -> None:
        self.ui.subjectComboBox.addItems(
            ["Базы данных", "Компьютерные сети", "Программирование"]
        )

        self.theory_images: List[ImageEntry] = []
        self.setup_images: List[ImageEntry] = []
        self.result_images: List[ImageEntry] = []
        self.analysis_images: List[ImageEntry] = []
        self.image_counter: int = 0

        self.director = ReportDirector(DatabaseReportBuilder())

    def setup_connections(self) -> None:
        self.ui.theoryAddImageBtn.clicked.connect(
            lambda: self.add_image(self.theory_images, self.ui.theoryTextEdit)
        )
        self.ui.setupAddImageBtn.clicked.connect(
            lambda: self.add_image(self.setup_images, self.ui.setupTextEdit)
        )
        self.ui.resultAddImageBtn.clicked.connect(
            lambda: self.add_image(self.result_images, self.ui.resultTextEdit)
        )
        self.ui.analysisAddImageBtn.clicked.connect(
            lambda: self.add_image(self.analysis_images, self.ui.analysisTextEdit)
        )

        self.ui.generateReportBtn.clicked.connect(self.on_generate_report)

    def add_image(self, storage: List[ImageEntry], text_edit: QTextEdit) -> None:
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите изображения",
            "",
            "Изображения (*.png *.jpg *.jpeg);;Все файлы (*.*)",
        )
        for name in filenames:
            self.image_counter += 1
            index = self.image_counter
            path = Path(name)
            entry = ImageEntry(index=index, path=path)
            storage.append(entry)

            current_text = text_edit.toPlainText()
            placeholder = f"[{path}](Рисунок {index} - {entry.caption})"
            if current_text and not current_text.endswith("\n"):
                current_text += "\n"
            current_text += placeholder + "\n"
            text_edit.setPlainText(current_text)

    def sync_captions_from_text(self, text: str, images: List[ImageEntry]) -> None:
        index_to_image = {image.index: image for image in images}
        for line in text.splitlines():
            match = re.search(r"Рисунок\s+(\d+)\s*-\s*([^)]+)", line)
            if not match:
                continue
            idx = int(match.group(1))
            caption = match.group(2).strip()
            image = index_to_image.get(idx)
            if image is not None and caption:
                image.caption = caption

    def collect_report_data(self) -> ReportData:
        self.sync_captions_from_text(self.ui.theoryTextEdit.toPlainText(), self.theory_images)
        self.sync_captions_from_text(self.ui.setupTextEdit.toPlainText(), self.setup_images)
        self.sync_captions_from_text(self.ui.resultTextEdit.toPlainText(), self.result_images)
        self.sync_captions_from_text(self.ui.analysisTextEdit.toPlainText(), self.analysis_images)

        subject = self.ui.subjectComboBox.currentText()

        return ReportData(
            subject=subject,
            work_number=self.ui.workNumber.value(),
            work_theme=self.ui.workTheme.text(),
            student_name=self.ui.studentName.text(),
            student_group=self.ui.studentGroup.text(),
            teacher_name=self.ui.teacherName.text(),
            purpose=SectionContent(text=self.ui.purposeTextEdit.toPlainText()),
            task=SectionContent(text=self.ui.taskTextEdit.toPlainText()),
            theory=SectionContent(
                text=self.ui.theoryTextEdit.toPlainText(),
                images=list(self.theory_images),
            ),
            setup=SectionContent(
                text=self.ui.setupTextEdit.toPlainText(),
                images=list(self.setup_images),
            ),
            result=SectionContent(
                text=self.ui.resultTextEdit.toPlainText(),
                images=list(self.result_images),
            ),
            analysis=SectionContent(
                text=self.ui.analysisTextEdit.toPlainText(),
                images=list(self.analysis_images),
            ),
            conclusion=SectionContent(text=self.ui.conclusionTextEdit.toPlainText()),
        )

    def select_builder_for_subject(self, subject: str):
        if subject == "Базы данных":
            return DatabaseReportBuilder()
        if subject == "Компьютерные сети":
            return NetworkReportBuilder()
        if subject == "Программирование":
            return ProgrammingReportBuilder()
        return DatabaseReportBuilder()

    def on_generate_report(self) -> None:
        data = self.collect_report_data()

        builder = self.select_builder_for_subject(data.subject)
        self.director.set_builder(builder)

        html = self.director.construct_report(data)

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            f"lab_report_{data.work_number}.html",
            "HTML файлы (*.html);;Все файлы (*.*)",
        )
        if not file_name:
            return

        try:
            Path(file_name).write_text(html, encoding="utf-8")
        except OSError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
            return

        QMessageBox.information(self, "Готово", "Отчёт успешно сформирован.")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
