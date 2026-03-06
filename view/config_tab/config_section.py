from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTreeWidget, QTreeWidgetItem, QStackedWidget, QSplitter,
                               QGroupBox, QScrollArea)
from PySide6.QtCore import Qt



class ConfigSection(QWidget):
    """
    A widget representing a configuration section with a sidebar navigation tree and content stack.
    """

    def __init__(self, section_items):
        """
        Initializes the navigation tree and the stacked widget for the configuration views.
        """
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setFixedWidth(220)
        self.nav_tree.setStyleSheet(
            "QTreeWidget { "
            "background: transparent; "
            "border: none; "
            "border-right: 1px solid rgba(128, 128, 128, 0.2); "
            "margin-right: 5px; "
            "font-size: 10pt; "
            "}"
            "QTreeWidget::item { padding: 4px; }"
            "QTreeWidget::item:selected { "
            "background-color: rgba(0, 120, 212, 0.15); "
            "border-radius: 3px; "
            "}"
        )

        self.gray_window = QWidget()
        self.gray_window.setObjectName("ConfigContentContainer")
        self.gray_window.setStyleSheet("QWidget#ConfigContentContainer { background: transparent; }")
        self.gray_layout = QHBoxLayout(self.gray_window)
        self.gray_layout.setContentsMargins(0, 0, 0, 0)
        self.gray_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: rgba(128, 128, 128, 0.2); width: 1px; }")

        self.restore_terminal_btn = QPushButton("<", self.gray_window)
        self.restore_terminal_btn.setToolTip("Restore Terminal")
        self.restore_terminal_btn.setFixedWidth(18)
        self.restore_terminal_btn.setStyleSheet(
            "QPushButton {"
            "font-family: Arial, sans-serif;"
            "font-size: 12px;"
            "font-weight: bold;"
            "padding-bottom: 1px;"
            "background: transparent;"
            "border: 1px solid #0078d4;"
            "border-radius: 3px;"
            "}"
            "QPushButton:hover { background-color: rgba(0, 120, 212, 0.1); }"
        )
        self.restore_terminal_btn.hide()
        self.restore_terminal_btn.clicked.connect(self._restore_terminal)

        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(400)
        self.widget_map = {}

        for section_name, subsections in section_items.items():
            top_item = QTreeWidgetItem(self.nav_tree, [section_name])

            font = self.font()
            font.setBold(True)
            font.setPointSize(10)
            top_item.setFont(0, font)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)
            page_layout.setContentsMargins(15, 15, 15, 15)
            page_layout.setSpacing(20)

            for sub_name, widget in subsections.items():
                group_box = QGroupBox(sub_name)
                group_box.setStyleSheet(
                    "QGroupBox { font-size: 11pt; font-weight: bold; border: 1px solid rgba(128, 128, 128, 0.4); border-radius: 6px; margin-top: 10px; padding-top: 15px; }"
                    "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; }"
                )
                group_layout = QVBoxLayout(group_box)
                group_layout.setContentsMargins(10, 15, 10, 10)

                if widget is not None:
                    group_layout.addWidget(widget)
                else:
                    empty_label = QLabel(f"No configuration available for {sub_name}")
                    group_layout.addWidget(empty_label)

                page_layout.addWidget(group_box)

            page_layout.addStretch()
            scroll_area.setWidget(page_widget)

            self.content_stack.addWidget(scroll_area)
            self.widget_map[id(top_item)] = self.content_stack.count() - 1

        self.nav_tree.itemClicked.connect(self._on_item_clicked)

        if self.content_stack.count() > 0:
            self.content_stack.setCurrentIndex(0)

        self.terminal_container = QWidget()
        self.terminal_layout = QVBoxLayout(self.terminal_container)
        self.terminal_layout.setContentsMargins(5, 0, 0, 38)
        self.terminal_container.setMinimumWidth(0)

        self.splitter.addWidget(self.content_stack)
        self.splitter.addWidget(self.terminal_container)

        self.splitter.setCollapsible(0, False)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([600, 400])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)

        self.gray_layout.addWidget(self.splitter)
        layout.addWidget(self.nav_tree)
        layout.addWidget(self.gray_window)

    def resizeEvent(self, event):
        """
        Keeps the floating restore button anchored to the right edge.
        """
        super().resizeEvent(event)
        btn_w = self.restore_terminal_btn.width()
        btn_h = 50
        self.restore_terminal_btn.setGeometry(
            self.gray_window.width() - btn_w,
            (self.gray_window.height() - btn_h) // 2,
            btn_w,
            btn_h
        )

    def _on_item_clicked(self, item, column):
        """
        Handles navigation item clicks to switch content.
        """
        if id(item) in self.widget_map:
            self.content_stack.setCurrentIndex(self.widget_map[id(item)])

    def _on_splitter_moved(self, pos, index):
        """
        Checks if terminal is collapsed and reveals the floating toggle.
        """
        sizes = self.splitter.sizes()
        if len(sizes) > 1 and sizes[1] <= 5:
            self.restore_terminal_btn.show()
            self.restore_terminal_btn.raise_()
        else:
            self.restore_terminal_btn.hide()

    def _restore_terminal(self):
        """
        Springs the terminal back to life.
        """
        total = sum(self.splitter.sizes())
        self.splitter.setSizes([total - 400, 400])
        self.restore_terminal_btn.hide()


