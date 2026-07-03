import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QFileDialog,
    QMessageBox, QGraphicsDropShadowEffect, QAbstractItemView,
    QSizePolicy, QSpacerItem,
)

from scanner import PortScannerThread
from utils import (
    validate_target, validate_port_range, get_port_list, export_to_csv,
)


STYLE_SHEET = """
QMainWindow {
    background-color: #eef3fb;
}

QWidget#centralWidget {
    background-color: #eef3fb;
}

QLabel#appTitle {
    color: #10233f;
    font-size: 26px;
    font-weight: 700;
}

QLabel#appSubtitle {
    color: #5b7191;
    font-size: 13px;
}

QLabel#statusPill {
    background-color: rgba(59, 130, 246, 0.15);
    color: #1d4ed8;
    border-radius: 14px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
}

QFrame.card {
    background-color: rgba(255, 255, 255, 0.72);
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 0.9);
}

QLabel.sectionLabel {
    color: #1e3a5f;
    font-size: 14px;
    font-weight: 700;
}

QLabel.fieldLabel {
    color: #46628a;
    font-size: 12px;
    font-weight: 600;
}

QLineEdit {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1.5px solid rgba(148, 180, 224, 0.6);
    border-radius: 12px;
    padding: 9px 12px;
    font-size: 13px;
    color: #10233f;
}

QLineEdit:focus {
    border: 1.5px solid #3b82f6;
}

QComboBox {
    background-color: rgba(255, 255, 255, 0.85);
    border: 1.5px solid rgba(148, 180, 224, 0.6);
    border-radius: 12px;
    padding: 8px 12px;
    font-size: 13px;
    color: #10233f;
}

QComboBox:focus {
    border: 1.5px solid #3b82f6;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border-radius: 8px;
    selection-background-color: #dbeafe;
    selection-color: #1d4ed8;
    outline: none;
}

QPushButton {
    border-radius: 13px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#startButton {
    background-color: #2563eb;
    color: #ffffff;
}

QPushButton#startButton:hover {
    background-color: #1d4ed8;
}

QPushButton#startButton:disabled {
    background-color: #b7c8e6;
    color: #eef3fb;
}

QPushButton#stopButton {
    background-color: #ef4444;
    color: #ffffff;
}

QPushButton#stopButton:hover {
    background-color: #dc2626;
}

QPushButton#stopButton:disabled {
    background-color: #f3b9b9;
    color: #fdf2f2;
}

QPushButton#clearButton, QPushButton#exportButton {
    background-color: rgba(255, 255, 255, 0.9);
    color: #1e3a5f;
    border: 1.5px solid rgba(148, 180, 224, 0.6);
}

QPushButton#clearButton:hover, QPushButton#exportButton:hover {
    background-color: #dbeafe;
    border: 1.5px solid #3b82f6;
}

QProgressBar {
    background-color: rgba(148, 180, 224, 0.25);
    border-radius: 9px;
    height: 16px;
    text-align: center;
    color: #10233f;
    font-size: 11px;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 9px;
}

QLabel.statValue {
    color: #10233f;
    font-size: 22px;
    font-weight: 700;
}

QLabel.statLabel {
    color: #5b7191;
    font-size: 11px;
    font-weight: 600;
}

QLabel.liveValue {
    color: #1e3a5f;
    font-size: 13px;
    font-weight: 600;
}

QLabel.liveLabel {
    color: #7c8fac;
    font-size: 11px;
}

QTableWidget {
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 16px;
    border: 1px solid rgba(148, 180, 224, 0.4);
    gridline-color: rgba(148, 180, 224, 0.25);
    font-size: 12px;
    color: #10233f;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #dbeafe;
    color: #10233f;
}

QHeaderView::section {
    background-color: rgba(219, 234, 254, 0.85);
    color: #1e3a5f;
    font-weight: 700;
    font-size: 12px;
    padding: 8px;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: rgba(148, 180, 224, 0.6);
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(59, 130, 246, 0.7);
}
"""


def make_shadow(blur=28, x_offset=0, y_offset=8, alpha=40):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(x_offset, y_offset)
    shadow.setColor(QColor(30, 58, 95, alpha))
    return shadow


def make_card():
    frame = QFrame()
    frame.setProperty("class", "card")
    frame.setObjectName("card")
    frame.setStyleSheet(STYLE_SHEET)
    frame.setGraphicsEffect(make_shadow())
    return frame


class StatCard(QFrame):
    def __init__(self, title, initial_value="0", parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setGraphicsEffect(make_shadow(blur=20, y_offset=6, alpha=30))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self.value_label = QLabel(initial_value)
        self.value_label.setProperty("class", "statValue")
        self.title_label = QLabel(title.upper())
        self.title_label.setProperty("class", "statLabel")

        layout.addWidget(self.value_label)
        layout.addWidget(self.title_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class LiveField(QFrame):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.value_label = QLabel("--")
        self.value_label.setProperty("class", "liveValue")
        self.caption_label = QLabel(label_text.upper())
        self.caption_label.setProperty("class", "liveLabel")

        layout.addWidget(self.value_label)
        layout.addWidget(self.caption_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SWAG Port Scanner")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(STYLE_SHEET)

        self.scanner_thread = None
        self.scan_results = []
        self.total_ports_to_scan = 0
        self.scan_start_time = 0.0

        self.duration_timer = QTimer(self)
        self.duration_timer.setInterval(100)
        self.duration_timer.timeout.connect(self._tick_duration)

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(28, 22, 28, 22)
        root_layout.setSpacing(18)

        root_layout.addLayout(self._build_header())
        root_layout.addWidget(self._build_input_card())
        root_layout.addWidget(self._build_live_status_card())
        root_layout.addLayout(self._build_stats_row())

        body_layout = QHBoxLayout()
        body_layout.setSpacing(18)
        body_layout.addWidget(self._build_results_card(), 3)
        body_layout.addWidget(self._build_details_card(), 1)
        root_layout.addLayout(body_layout, 1)

    def _build_header(self):
        layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel("SWAG Port Scanner")
        title.setObjectName("appTitle")
        subtitle = QLabel("Modern TCP connectivity scanning dashboard")
        subtitle.setObjectName("appSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        layout.addLayout(title_layout)
        layout.addStretch(1)

        self.status_pill = QLabel("IDLE")
        self.status_pill.setObjectName("statusPill")
        layout.addWidget(self.status_pill, alignment=Qt.AlignmentFlag.AlignVCenter)

        return layout

    def _build_input_card(self):
        card = make_card()
        outer = QVBoxLayout(card)
        outer.setContentsMargins(22, 20, 22, 20)
        outer.setSpacing(14)

        label = QLabel("Scan Configuration")
        label.setProperty("class", "sectionLabel")
        outer.addWidget(label)

        row1 = QHBoxLayout()
        row1.setSpacing(16)

        target_layout = QVBoxLayout()
        target_layout.setSpacing(6)
        target_label = QLabel("TARGET IP / DOMAIN")
        target_label.setProperty("class", "fieldLabel")
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("192.168.1.1, google.com, scanme.nmap.org")
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_input)
        row1.addLayout(target_layout, 3)

        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(6)
        mode_label = QLabel("PORT MODE")
        mode_label.setProperty("class", "fieldLabel")
        self.port_mode_combo = QComboBox()
        self.port_mode_combo.addItems(
            ["Common Ports", "Top 100", "Top 1000", "Custom Range"]
        )
        self.port_mode_combo.currentTextChanged.connect(self._on_port_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.port_mode_combo)
        row1.addLayout(mode_layout, 2)

        start_layout = QVBoxLayout()
        start_layout.setSpacing(6)
        start_label = QLabel("START PORT")
        start_label.setProperty("class", "fieldLabel")
        self.start_port_input = QLineEdit()
        self.start_port_input.setPlaceholderText("1")
        self.start_port_input.setEnabled(False)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_port_input)
        row1.addLayout(start_layout, 1)

        end_layout = QVBoxLayout()
        end_layout.setSpacing(6)
        end_label = QLabel("END PORT")
        end_label.setProperty("class", "fieldLabel")
        self.end_port_input = QLineEdit()
        self.end_port_input.setPlaceholderText("1024")
        self.end_port_input.setEnabled(False)
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_port_input)
        row1.addLayout(end_layout, 1)

        outer.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(16)

        timeout_layout = QVBoxLayout()
        timeout_layout.setSpacing(6)
        timeout_label = QLabel("TIMEOUT")
        timeout_label.setProperty("class", "fieldLabel")
        self.timeout_combo = QComboBox()
        self.timeout_combo.addItems(["100ms", "250ms", "500ms", "1000ms"])
        self.timeout_combo.setCurrentIndex(1)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_combo)
        row2.addLayout(timeout_layout, 1)

        threads_layout = QVBoxLayout()
        threads_layout.setSpacing(6)
        threads_label = QLabel("THREADS")
        threads_label.setProperty("class", "fieldLabel")
        self.thread_combo = QComboBox()
        self.thread_combo.addItems(["10", "25", "50", "100"])
        self.thread_combo.setCurrentIndex(1)
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.thread_combo)
        row2.addLayout(threads_layout, 1)

        row2.addStretch(2)

        self.start_button = QPushButton("Start Scan")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.start_scan)

        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_results)

        self.export_button = QPushButton("Export CSV")
        self.export_button.setObjectName("exportButton")
        self.export_button.clicked.connect(self.export_csv)

        row2.addWidget(self.start_button)
        row2.addWidget(self.stop_button)
        row2.addWidget(self.clear_button)
        row2.addWidget(self.export_button)

        outer.addLayout(row2)

        return card

    def _build_live_status_card(self):
        card = make_card()
        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.setSpacing(24)

        self.live_host_field = LiveField("Current Host")
        self.live_port_field = LiveField("Current Port")
        self.live_elapsed_field = LiveField("Elapsed Time")

        layout.addWidget(self.live_host_field)
        layout.addWidget(self.live_port_field)
        layout.addWidget(self.live_elapsed_field)

        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)
        progress_label = QLabel("SCAN PROGRESS")
        progress_label.setProperty("class", "liveLabel")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)

        layout.addLayout(progress_layout, 2)

        return card

    def _build_stats_row(self):
        layout = QHBoxLayout()
        layout.setSpacing(16)

        self.open_stat = StatCard("Open Ports")
        self.closed_stat = StatCard("Closed Ports")
        self.filtered_stat = StatCard("Filtered Ports")
        self.total_stat = StatCard("Total Scanned")
        self.duration_stat = StatCard("Scan Duration", "0.0s")

        for stat in (
            self.open_stat, self.closed_stat, self.filtered_stat,
            self.total_stat, self.duration_stat,
        ):
            layout.addWidget(stat)

        return layout

    def _build_results_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        label = QLabel("Scan Results")
        label.setProperty("class", "sectionLabel")
        header_row.addWidget(label)
        header_row.addStretch(1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by port, service, or status")
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self._filter_table)
        header_row.addWidget(self.search_input)

        layout.addLayout(header_row)

        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels(
            ["Port", "State", "Service", "Protocol", "Description"]
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.results_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.results_table.setSortingEnabled(True)
        self.results_table.itemSelectionChanged.connect(self._on_row_selected)
        self.results_table.cellDoubleClicked.connect(self._on_row_double_clicked)

        layout.addWidget(self.results_table, 1)

        return card

    def _build_details_card(self):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        label = QLabel("Port Information")
        label.setProperty("class", "sectionLabel")
        layout.addWidget(label)

        self.detail_port_field = LiveField("Port Number")
        self.detail_protocol_field = LiveField("Protocol")
        self.detail_service_field = LiveField("Service Name")
        self.detail_status_field = LiveField("Status")

        for field in (
            self.detail_port_field, self.detail_protocol_field,
            self.detail_service_field, self.detail_status_field,
        ):
            layout.addWidget(field)

        desc_label = QLabel("DESCRIPTION")
        desc_label.setProperty("class", "liveLabel")
        self.detail_description_label = QLabel(
            "Select a row in the results table to view details."
        )
        self.detail_description_label.setWordWrap(True)
        self.detail_description_label.setProperty("class", "liveValue")

        layout.addWidget(desc_label)
        layout.addWidget(self.detail_description_label)
        layout.addStretch(1)

        return card

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------
    def _on_port_mode_changed(self, mode):
        is_custom = mode == "Custom Range"
        self.start_port_input.setEnabled(is_custom)
        self.end_port_input.setEnabled(is_custom)

    def start_scan(self):
        target = self.target_input.text().strip()
        valid, message = validate_target(target)
        if not valid:
            QMessageBox.warning(self, "Invalid Target", message)
            return

        mode = self.port_mode_combo.currentText()
        start_port = None
        end_port = None

        if mode == "Custom Range":
            valid, message, start_port, end_port = validate_port_range(
                self.start_port_input.text().strip(),
                self.end_port_input.text().strip(),
            )
            if not valid:
                QMessageBox.warning(self, "Invalid Port Range", message)
                return

        ports = get_port_list(mode, start_port, end_port)
        if not ports:
            QMessageBox.warning(self, "Invalid Configuration", "No ports to scan")
            return

        timeout_ms = int(self.timeout_combo.currentText().replace("ms", ""))
        thread_count = int(self.thread_combo.currentText())

        self.clear_results()
        self.total_ports_to_scan = len(ports)
        self.scan_start_time = time.time()

        self.scanner_thread = PortScannerThread(
            target, ports, timeout_ms, thread_count
        )
        self.scanner_thread.status_updated.connect(self._on_status_updated)
        self.scanner_thread.progress_updated.connect(self._on_progress_updated)
        self.scanner_thread.port_scanned.connect(self._on_port_scanned)
        self.scanner_thread.scan_finished.connect(self._on_scan_finished)
        self.scanner_thread.scan_error.connect(self._on_scan_error)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_pill.setText("SCANNING")
        self.duration_timer.start()

        self.scanner_thread.start()

    def stop_scan(self):
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.status_pill.setText("STOPPING")
            self.stop_button.setEnabled(False)

    def clear_results(self):
        self.results_table.setRowCount(0)
        self.scan_results = []
        self.open_stat.set_value(0)
        self.closed_stat.set_value(0)
        self.filtered_stat.set_value(0)
        self.total_stat.set_value(0)
        self.duration_stat.set_value("0.0s")
        self.progress_bar.setValue(0)
        self.live_host_field.set_value("--")
        self.live_port_field.set_value("--")
        self.live_elapsed_field.set_value("--")
        self.detail_port_field.set_value("--")
        self.detail_protocol_field.set_value("--")
        self.detail_service_field.set_value("--")
        self.detail_status_field.set_value("--")
        self.detail_description_label.setText(
            "Select a row in the results table to view details."
        )
        self.status_pill.setText("IDLE")

    def export_csv(self):
        if not self.scan_results:
            QMessageBox.information(self, "No Data", "There are no scan results to export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "scan_results.csv", "CSV Files (*.csv)"
        )
        if not filepath:
            return

        try:
            count = export_to_csv(filepath, self.scan_results)
            QMessageBox.information(
                self, "Export Complete", f"Exported {count} open port(s) to CSV."
            )
        except OSError as error:
            QMessageBox.critical(self, "Export Failed", f"Could not write file: {error}")
        except Exception as error:
            QMessageBox.critical(self, "Export Failed", f"Unexpected error: {error}")

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------
    def _on_status_updated(self, host, port, elapsed):
        self.live_host_field.set_value(host)
        self.live_port_field.set_value(port)
        self.live_elapsed_field.set_value(f"{elapsed:.1f}s")

    def _on_progress_updated(self, scanned, total):
        if total <= 0:
            return
        percentage = int((scanned / total) * 100)
        self.progress_bar.setValue(percentage)
        self.total_stat.set_value(scanned)

    def _on_port_scanned(self, result):
        self.scan_results.append(result)

        state = result["state"]
        if state == "Open":
            self.open_stat.set_value(int(self.open_stat.value_label.text()) + 1)
        elif state == "Closed":
            self.closed_stat.set_value(int(self.closed_stat.value_label.text()) + 1)
        else:
            self.filtered_stat.set_value(int(self.filtered_stat.value_label.text()) + 1)

        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        port_item = QTableWidgetItem()
        port_item.setData(Qt.ItemDataRole.DisplayRole, result["port"])
        self.results_table.setItem(row, 0, port_item)
        self.results_table.setItem(row, 1, QTableWidgetItem(result["state"]))
        self.results_table.setItem(row, 2, QTableWidgetItem(result["service"]))
        self.results_table.setItem(row, 3, QTableWidgetItem(result["protocol"]))
        self.results_table.setItem(row, 4, QTableWidgetItem(result["description"]))

        self.results_table.scrollToBottom()

    def _on_scan_finished(self, scanned_count):
        self.duration_timer.stop()
        elapsed = time.time() - self.scan_start_time
        self.duration_stat.set_value(f"{elapsed:.1f}s")
        self.total_stat.set_value(scanned_count)
        self.progress_bar.setValue(100 if scanned_count >= self.total_ports_to_scan else self.progress_bar.value())

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_pill.setText("COMPLETE")

        QMessageBox.information(
            self, "Scan Complete",
            f"Scan finished. {scanned_count} port(s) scanned in {elapsed:.1f} seconds.",
        )

    def _on_scan_error(self, message):
        self.duration_timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_pill.setText("ERROR")
        QMessageBox.critical(self, "Scan Error", message)

    def _tick_duration(self):
        elapsed = time.time() - self.scan_start_time
        self.duration_stat.set_value(f"{elapsed:.1f}s")

    def _on_row_selected(self):
        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        port = self.results_table.item(row, 0).text()
        state = self.results_table.item(row, 1).text()
        service = self.results_table.item(row, 2).text()
        protocol = self.results_table.item(row, 3).text()
        description = self.results_table.item(row, 4).text()

        self.detail_port_field.set_value(port)
        self.detail_protocol_field.set_value(protocol)
        self.detail_service_field.set_value(service)
        self.detail_status_field.set_value(state)
        self.detail_description_label.setText(description)

    def _on_row_double_clicked(self, row, column):
        values = [
            self.results_table.item(row, col).text()
            for col in range(self.results_table.columnCount())
        ]
        clipboard_text = "\t".join(values)
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(clipboard_text)
        self.status_pill.setText("ROW COPIED")
        QTimer.singleShot(1500, lambda: self.status_pill.setText(
            "SCANNING" if self.scanner_thread and self.scanner_thread.isRunning() else "IDLE"
        ))

    def _filter_table(self, text):
        text = text.strip().lower()
        for row in range(self.results_table.rowCount()):
            match = False
            if not text:
                match = True
            else:
                for col in (0, 1, 2):
                    item = self.results_table.item(row, col)
                    if item and text in item.text().lower():
                        match = True
                        break
            self.results_table.setRowHidden(row, not match)

    def closeEvent(self, event):
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait(2000)
        event.accept()
