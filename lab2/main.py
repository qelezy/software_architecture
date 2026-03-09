import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QFile, QIODevice
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QMainWindow,
)
from PySide6.QtUiTools import QUiLoader

from product_component import ProductComponent, component_from_dict
from assembly_unit import AssemblyUnit
from part import Part


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_root: ProductComponent | None = None
        self.root_quantity: int = 1
        self.catalog_items: list[dict] = []
        self._init_ui()
        self._load_catalog()
        self._populate_catalog()

    def _init_ui(self) -> None:
        ui_file = QFile("ui/mainwindow.ui")
        if not ui_file.open(QIODevice.ReadOnly):
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл UI: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        if not self.ui:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить UI")
            sys.exit(-1)
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("САПР изделий")
        self.catalog_list: QListWidget = self.ui.catalog_list
        self.quantity_spin: QSpinBox = self.ui.quantity_spin
        self.show_from_catalog_btn: QPushButton = self.ui.show_from_catalog_btn
        self.load_btn: QPushButton = self.ui.load_btn
        self.save_btn: QPushButton = self.ui.save_btn
        self.tree: QTreeWidget = self.ui.tree
        self.total_cost_label: QLabel = self.ui.total_cost_label
        self.total_time_label: QLabel = self.ui.total_time_label
        self.tree.setColumnWidth(0, 260)
        self.total_cost_label.setAlignment(Qt.AlignLeft)
        self.total_time_label.setAlignment(Qt.AlignLeft)
        self.show_from_catalog_btn.clicked.connect(self.on_show_from_catalog)
        self.load_btn.clicked.connect(self.on_load_from_file)
        self.save_btn.clicked.connect(self.on_save_to_file)
        self.quantity_spin.valueChanged.connect(self.on_quantity_changed)

    def _load_catalog(self) -> None:
        try:
            catalog_path = Path(__file__).with_name("catalog_data.json")
            raw_text = catalog_path.read_text(encoding="utf-8")
            data = json.loads(raw_text)
            items = data.get("items", [])
            if isinstance(items, list):
                self.catalog_items = [item for item in items if isinstance(item, dict)]
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка каталога", f"Не удалось загрузить каталог:\n{exc}")
            self.catalog_items = []

    def _populate_catalog(self) -> None:
        self.catalog_list.clear()
        for item in self.catalog_items:
            name = item.get("name")
            if not isinstance(name, str):
                continue
            list_item = QListWidgetItem(name)
            list_item.setData(Qt.UserRole, item)
            self.catalog_list.addItem(list_item)

    def on_show_from_catalog(self) -> None:
        current_item = self.catalog_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "Каталог", "Выберите изделие в каталоге.")
            return
        item_data = current_item.data(Qt.UserRole)
        if not isinstance(item_data, dict):
            QMessageBox.critical(self, "Каталог", "Некорректная запись в каталоге.")
            return
        root_data = item_data.get("root")
        if not isinstance(root_data, dict):
            QMessageBox.critical(self, "Каталог", "В записи каталога отсутствует корневой элемент.")
            return
        try:
            self.current_root = component_from_dict(root_data)
        except Exception as exc:
            QMessageBox.critical(self, "Каталог", f"Не удалось построить изделие:\n{exc}")
            return
        self.root_quantity = self.quantity_spin.value()
        self._refresh_view()

    def on_load_from_file(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить изделие из файла",
            "",
            "JSON файлы (*.json);;Все файлы (*.*)",
        )
        if not file_name:
            return
        try:
            raw_text = Path(file_name).read_text(encoding="utf-8")
            data = json.loads(raw_text)
            if not isinstance(data, dict):
                raise ValueError("Ожидался объект верхнего уровня.")
            self.current_root = component_from_dict(data)
        except Exception as exc:
            QMessageBox.critical(self, "Загрузка", f"Не удалось загрузить файл:\n{exc}")
            return
        self.root_quantity = self.quantity_spin.value()
        self._refresh_view()

    def on_save_to_file(self) -> None:
        if self.current_root is None:
            QMessageBox.information(self, "Сохранение", "Нет изделия для сохранения.")
            return
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить изделие в файл",
            "product.json",
            "JSON файлы (*.json);;Все файлы (*.*)",
        )
        if not file_name:
            return
        try:
            data = self.current_root.serialize()
            Path(file_name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            QMessageBox.critical(self, "Сохранение", f"Не удалось сохранить файл:\n{exc}")

    def on_quantity_changed(self, value: int) -> None:
        self.root_quantity = value
        self._refresh_totals_only()

    def _refresh_view(self) -> None:
        self._populate_tree()
        self._refresh_totals_only()

    def _populate_tree_for_component(
        self,
        component: ProductComponent,
        parent_item: QTreeWidgetItem | None,
        quantity: int,
    ) -> QTreeWidgetItem:
        if isinstance(component, AssemblyUnit):
            type_name = "Сборочная единица"
        elif isinstance(component, Part):
            type_name = "Деталь"
        else:
            type_name = "Компонент"
        unit_cost = component.get_cost()
        unit_time = component.get_time()
        columns = [
            component.name,
            type_name,
            str(quantity),
            f"{unit_cost:.2f}",
            f"{unit_time:.2f}",
        ]
        if parent_item is None:
            item = QTreeWidgetItem(self.tree, columns)
        else:
            item = QTreeWidgetItem(parent_item, columns)
        if isinstance(component, AssemblyUnit):
            for child, qty in component.children():
                self._populate_tree_for_component(child, item, qty)
        return item

    def _populate_tree(self) -> None:
        self.tree.clear()
        if self.current_root is None:
            return
        self._populate_tree_for_component(self.current_root, None, quantity=1)
        self.tree.expandAll()

    def _refresh_totals_only(self) -> None:
        if self.current_root is None:
            self.total_cost_label.setText("Общая стоимость: -")
            self.total_time_label.setText("Общее время: -")
            return
        unit_cost = self.current_root.get_cost()
        unit_time = self.current_root.get_time()
        total_cost = unit_cost * self.root_quantity
        total_time = unit_time * self.root_quantity
        self.total_cost_label.setText(f"Общая стоимость: {total_cost:.2f}")
        self.total_time_label.setText(f"Общее время: {total_time:.2f}")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

