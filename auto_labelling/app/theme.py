# Purple dark theme — QSS stylesheet + SVG icon set

STYLESHEET = r"""
/* === Global === */
QMainWindow {
    background-color: #1e1e2e;
    color: #e0e0e0;
}
QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
    font-size: 13px;
    font-family: "Segoe UI", system-ui, sans-serif;
}

/* === Toolbar === */
QToolBar {
    background-color: #252536;
    border-bottom: 1px solid #3a3a50;
    padding: 4px 6px;
    spacing: 4px;
}
QToolBar::separator {
    width: 1px;
    background: #3a3a50;
    margin: 4px 6px;
}
QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 5px 10px;
    color: #c0c0d0;
    font-weight: 500;
}
QToolButton:hover {
    background-color: #2d2d44;
    border-color: #3a3a50;
    color: #e0e0e0;
}
QToolButton:pressed, QToolButton:checked {
    background-color: #7c3aed;
    border-color: #7c3aed;
    color: #ffffff;
}
QToolButton:disabled {
    color: #606070;
}

/* === Menu === */
QMenuBar {
    background-color: #252536;
    color: #c0c0d0;
    border-bottom: 1px solid #3a3a50;
    padding: 2px;
}
QMenuBar::item {
    padding: 4px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #2d2d44;
}
QMenu {
    background-color: #252536;
    border: 1px solid #3a3a50;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 32px 6px 16px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #7c3aed;
}
QMenu::separator {
    height: 1px;
    background: #3a3a50;
    margin: 4px 8px;
}

/* === Status Bar === */
QStatusBar {
    background-color: #252536;
    border-top: 1px solid #3a3a50;
    color: #9090a0;
    padding: 2px 8px;
    font-size: 12px;
}

/* === Splitter === */
QSplitter::handle {
    background-color: #3a3a50;
    width: 1px;
}
QSplitter::handle:hover {
    background-color: #7c3aed;
}

/* === Scrollbar === */
QScrollBar:vertical {
    background: #1e1e2e;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #3a3a50;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #7c3aed;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #1e1e2e;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #3a3a50;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #7c3aed;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

/* === List Widget (Track List) === */
QListWidget {
    background-color: #1e1e2e;
    border: none;
    outline: none;
    padding: 4px;
}
QListWidget::item {
    background-color: #252536;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 10px;
    margin: 2px 0;
    color: #c0c0d0;
}
QListWidget::item:hover {
    background-color: #2d2d44;
    border-color: #3a3a50;
}
QListWidget::item:selected {
    background-color: #7c3aed;
    color: #ffffff;
    border-color: #7c3aed;
}

/* === Tree Widget (Properties Panel) === */
QTreeWidget, QTableWidget {
    background-color: #1e1e2e;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    outline: none;
    gridline-color: #2d2d44;
}
QTreeWidget::item, QTableWidget::item {
    padding: 4px 8px;
}
QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #7c3aed;
}
QHeaderView::section {
    background-color: #252536;
    color: #9090a0;
    border: none;
    border-bottom: 1px solid #3a3a50;
    padding: 6px 8px;
    font-weight: 600;
    font-size: 12px;
}

/* === Group Box === */
QGroupBox {
    background-color: #252536;
    border: 1px solid #3a3a50;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
    color: #c0c0d0;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* === Push Button === */
QPushButton {
    background-color: #2d2d44;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    padding: 6px 16px;
    color: #c0c0d0;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3a3a50;
    border-color: #7c3aed;
    color: #e0e0e0;
}
QPushButton:pressed {
    background-color: #7c3aed;
    color: #ffffff;
}
QPushButton:disabled {
    background-color: #252536;
    color: #606070;
    border-color: #2d2d44;
}
QPushButton#accent {
    background-color: #7c3aed;
    border-color: #7c3aed;
    color: #ffffff;
}
QPushButton#accent:hover {
    background-color: #6d28d9;
}

/* === Line Edit === */
QLineEdit {
    background-color: #1e1e2e;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e0e0e0;
    selection-background-color: #7c3aed;
}
QLineEdit:focus {
    border-color: #7c3aed;
}
QLineEdit:read-only {
    background-color: #252536;
    color: #9090a0;
}

/* === Combo Box === */
QComboBox {
    background-color: #2d2d44;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    padding: 6px 10px;
    color: #e0e0e0;
}
QComboBox:hover {
    border-color: #7c3aed;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #252536;
    border: 1px solid #3a3a50;
    border-radius: 4px;
    selection-background-color: #7c3aed;
    outline: none;
}

/* === Spin Box === */
QSpinBox, QDoubleSpinBox {
    background-color: #2d2d44;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    padding: 6px 8px;
    color: #e0e0e0;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #7c3aed;
}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #252536;
    border-radius: 4px;
    margin: 2px;
}

/* === Slider === */
QSlider::groove:horizontal {
    background: #2d2d44;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #7c3aed;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #a78bfa;
}
QSlider::sub-page:horizontal {
    background: #7c3aed;
    border-radius: 3px;
}

/* === Progress Bar === */
QProgressBar {
    background-color: #2d2d44;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: #c0c0d0;
    font-size: 11px;
}
QProgressBar::chunk {
    background-color: #7c3aed;
    border-radius: 5px;
}

/* === Dialog === */
QDialog {
    background-color: #1e1e2e;
    color: #e0e0e0;
}

/* === Check Box === */
QCheckBox {
    color: #c0c0d0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #3a3a50;
    border-radius: 4px;
    background: #1e1e2e;
}
QCheckBox::indicator:checked {
    background: #7c3aed;
    border-color: #7c3aed;
}
QCheckBox::indicator:hover {
    border-color: #7c3aed;
}

/* === Tab Widget === */
QTabWidget::pane {
    border: 1px solid #3a3a50;
    border-radius: 6px;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #252536;
    border: 1px solid #3a3a50;
    padding: 6px 16px;
    border-radius: 6px 6px 0 0;
    margin-right: 2px;
    color: #9090a0;
}
QTabBar::tab:selected {
    background: #1e1e2e;
    border-bottom-color: #1e1e2e;
    color: #e0e0e0;
}
QTabBar::tab:hover:!selected {
    background: #2d2d44;
    color: #c0c0d0;
}

/* === Label === */
QLabel {
    color: #c0c0d0;
    background: transparent;
}
QLabel#title {
    font-size: 14px;
    font-weight: 600;
    color: #e0e0e0;
}
QLabel#subtitle {
    font-size: 11px;
    color: #9090a0;
}

/* === Graphics View (Canvas) === */
QGraphicsView {
    background-color: #16161e;
    border: none;
    border-radius: 4px;
}

/* === Tooltips === */
QToolTip {
    background-color: #252536;
    color: #e0e0e0;
    border: 1px solid #3a3a50;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 12px;
}
"""

# SVG icons — minimal custom icons
ICONS = {
    "folder": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
</svg>""",
    "extract": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <rect x="2" y="3" width="20" height="14" rx="2"/>
  <path d="M8 21h8m-4-4v4"/>
  <polyline points="17 8 12 3 7 8"/>
</svg>""",
    "auto_label": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="3"/>
  <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
</svg>""",
    "export": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="17 8 12 3 7 8"/>
  <line x1="12" y1="3" x2="12" y2="15"/>
</svg>""",
    "undo": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <polyline points="1 4 1 10 7 10"/>
  <path d="M4.51 16.41A9 9 0 1 0 2 11"/>
</svg>""",
    "redo": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <polyline points="23 4 23 10 17 10"/>
  <path d="M19.49 16.41A9 9 0 1 1 22 11"/>
</svg>""",
    "play": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="5 3 19 12 5 21 5 3"/>
</svg>""",
    "pause": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>
</svg>""",
    "prev": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <polyline points="15 18 9 12 15 6"/>
</svg>""",
    "next": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <polyline points="9 18 15 12 9 6"/>
</svg>""",
    "crosshair": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="9"/>
  <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
  <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
</svg>""",
    "box_select": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <rect x="4" y="4" width="16" height="16" rx="2"/>
  <path d="M9 2v2m6-2v2M9 20v2m6-2v2M2 9h2m16 0h2M2 15h2m16 0h2"/>
</svg>""",
    "edit": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
</svg>""",
    "plus": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
</svg>""",
    "trash": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <polyline points="3 6 5 6 21 6"/>
  <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
  <path d="M10 11v6m4-6v6"/><line x1="9" y1="6" x2="10" y2="3h4l1 3"/>
</svg>""",
    "mask": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/>
  <line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/>
  <line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/>
</svg>""",
    "settings": """
<svg viewBox="0 0 24 24" fill="none" stroke="#c0c0d0" stroke-width="2" stroke-linecap="round">
  <circle cx="12" cy="12" r="3"/>
  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
</svg>""",
}


def make_icon(svg: str) -> "QIcon":
    from PySide6.QtGui import QIcon, QPixmap, QPainter
    from PySide6.QtSvg import QSvgRenderer
    from PySide6.QtCore import QByteArray, Qt

    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def icon(key: str) -> "QIcon":
    svg = ICONS.get(key)
    if svg:
        return make_icon(svg)
    from PySide6.QtGui import QIcon
    return QIcon()
