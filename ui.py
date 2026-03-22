"""
DocMarkdownConverter - 批量文档转换工具
UI 层 (PyQt6)
"""
import os
from pathlib import Path

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QComboBox,
    QProgressBar, QMessageBox, QFileDialog, QFrame,
    QSplitter, QListWidgetItem, QCheckBox,
)

from converter import (
    get_available_formats, get_format_display_name,
    batch_convert, is_pandoc_available,
    detect_format,
)


# ---------------------------------------------------------------
# 转换线程
# ---------------------------------------------------------------

class ConvertThread(QThread):
    progress = pyqtSignal(int, int, str, bool, str)  # current, total, filename, success, msg
    finished = pyqtSignal(list, list)  # successes, failures

    def __init__(self, file_list, target_format):
        super().__init__()
        self.file_list = file_list
        self.target_format = target_format

    def run(self):
        successes, failures = batch_convert(
            self.file_list,
            self.target_format,
            callback=lambda c, t, f, s, m: self.progress.emit(c, t, f, s, m),
        )
        self.finished.emit(successes, failures)


# ---------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------

class MainWindow(QWidget):
    # 颜色主题
    COLOR_BG = "#F5F7FA"
    COLOR_CARD = "#FFFFFF"
    COLOR_PRIMARY = "#4A90D9"
    COLOR_PRIMARY_HOVER = "#3A7BC8"
    COLOR_PRIMARY_LIGHT = "#EBF3FC"
    COLOR_TEXT = "#333333"
    COLOR_TEXT_SEC = "#888888"
    COLOR_BORDER = "#E0E6F0"
    COLOR_SUCCESS = "#27AE60"
    COLOR_ERROR = "#E74C3C"
    COLOR_WARNING = "#F39C12"

    # 支持的文件格式
    SUPPORTED_FORMATS = ["*.docx", "*.doc", "*.pdf", "*.md", "*.markdown", "*.txt"]

    def __init__(self):
        super().__init__()
        self.file_list = []
        self.convert_thread = None
        self.setup_ui()
        self.update_ui_state()

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------

    def setup_ui(self):
        self.setWindowTitle("DocMarkdown 批量转换工具")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"background-color: {self.COLOR_BG};")

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # ===== 标题栏 =====
        title_bar = self._build_title_bar()
        main_layout.addLayout(title_bar)

        # ===== 主体：左侧文件列表 + 右侧设置 =====
        body = self._build_body()
        main_layout.addWidget(body, stretch=1)

        # ===== 底部：进度条 + 操作按钮 =====
        bottom = self._build_bottom()
        main_layout.addLayout(bottom)

        # 启用拖放
        self.setAcceptDrops(True)

    def _build_title_bar(self):
        """标题栏"""
        layout = QHBoxLayout()

        # 图标 + 标题
        icon_label = QLabel()
        icon_label.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage.fromData(self._icon_data())
            ).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio)
        )

        title = QLabel("DocMarkdown 批量转换工具")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.COLOR_TEXT};")

        subtitle = QLabel("批量转换 doc · docx · pdf · md · txt 互转")
        subtitle.setFont(QFont("Microsoft YaHei", 9))
        subtitle.setStyleSheet(f"color: {self.COLOR_TEXT_SEC};")

        left = QVBoxLayout()
        left.addWidget(title)
        left.addWidget(subtitle)
        left.setSpacing(2)

        layout.addWidget(icon_label)
        layout.addLayout(left)
        layout.addStretch()

        # pandoc 状态标签
        self.pandoc_label = QLabel()
        self._check_pandoc_status()
        layout.addWidget(self.pandoc_label)

        return layout

    def _check_pandoc_status(self):
        if is_pandoc_available():
            self.pandoc_label.setText("✅ Pandoc 已就绪")
            self.pandoc_label.setStyleSheet(
                f"color: {self.COLOR_SUCCESS}; font-size: 12px; "
                f"background: {self.COLOR_PRIMARY_LIGHT}; "
                f"padding: 4px 10px; border-radius: 12px;"
            )
        else:
            self.pandoc_label.setText("⚠️ Pandoc 未检测到（PDF/.doc 转换将受限）")
            self.pandoc_label.setStyleSheet(
                f"color: {self.COLOR_WARNING}; font-size: 12px; "
                f"background: #FEF9E7; padding: 4px 10px; border-radius: 12px;"
            )

    def _build_body(self):
        """主体区域"""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：文件列表
        left_panel = self._build_file_panel()
        left_panel.setMinimumWidth(420)

        # 右侧：设置面板
        right_panel = self._build_settings_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1.4)
        splitter.setStretchFactor(1, 1)
        splitter.setHandleWidth(1)

        # 分隔线样式
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background-color: {self.COLOR_BORDER}; }}"
        )

        return splitter

    def _build_file_panel(self):
        """文件列表面板"""
        panel = QFrame()
        panel.setStyleSheet(
            f"background-color: {self.COLOR_CARD}; "
            f"border-radius: 12px; "
            f"border: 1px solid {self.COLOR_BORDER};"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # 标题栏
        header = QHBoxLayout()
        lbl = QLabel("📂 已选文件")
        lbl.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {self.COLOR_TEXT};")
        header.addWidget(lbl)

        self.file_count_label = QLabel("0 个文件")
        self.file_count_label.setFont(QFont("Microsoft YaHei", 9))
        self.file_count_label.setStyleSheet(f"color: {self.COLOR_TEXT_SEC};")
        header.addWidget(self.file_count_label)
        header.addStretch()

        # 清空按钮
        clear_btn = QPushButton("清空列表")
        clear_btn.setFont(QFont("Microsoft YaHei", 9))
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(self._clear_btn_style())
        clear_btn.clicked.connect(self.clear_files)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # 文件列表
        self.file_list_widget = QListWidget()
        self.file_list_widget.setStyleSheet(self._file_list_style())
        self.file_list_widget.setFont(QFont("Microsoft YaHei", 9))
        self.file_list_widget.setSpacing(4)
        self.file_list_widget.setAcceptDrops(False)  # 我们用整个窗口拖放
        layout.addWidget(self.file_list_widget)

        # 按钮组
        btn_layout = QHBoxLayout()

        add_btn = self._make_primary_btn("➕ 添加文件", self.add_files)
        add_folder_btn = self._make_primary_btn("📁 添加文件夹", self.add_folder)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(add_folder_btn)
        layout.addLayout(btn_layout)

        # 拖放提示
        hint = QLabel("💡 也可直接拖拽文件或文件夹到窗口中")
        hint.setFont(QFont("Microsoft YaHei", 8))
        hint.setStyleSheet(f"color: {self.COLOR_TEXT_SEC};")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        return panel

    def _build_settings_panel(self):
        """设置面板"""
        panel = QFrame()
        panel.setStyleSheet(
            f"background-color: {self.COLOR_CARD}; "
            f"border-radius: 12px; "
            f"border: 1px solid {self.COLOR_BORDER};"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        # 标题
        lbl = QLabel("⚙️ 转换设置")
        lbl.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {self.COLOR_TEXT};")
        layout.addWidget(lbl)

        # 目标格式
        fmt_layout = QVBoxLayout()
        fmt_title = QLabel("目标格式")
        fmt_title.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.DemiBold))
        fmt_title.setStyleSheet(f"color: {self.COLOR_TEXT};")
        fmt_layout.addWidget(fmt_title)

        self.format_combo = QComboBox()
        self.format_combo.setFont(QFont("Microsoft YaHei", 11))
        self.format_combo.setStyleSheet(self._combo_style())
        formats = get_available_formats()
        for fmt in formats:
            self.format_combo.addItem(get_format_display_name(fmt), fmt)
        fmt_layout.addWidget(self.format_combo)
        layout.addLayout(fmt_layout)

        # 分隔线
        layout.addWidget(self._make_separator())

        # 输出说明
        info_box = QFrame()
        info_box.setStyleSheet(
            f"background-color: {self.COLOR_PRIMARY_LIGHT}; "
            f"border-radius: 8px;"
        )
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(12, 10, 12, 10)

        info_title = QLabel("📋 输出说明")
        info_title.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.DemiBold))
        info_title.setStyleSheet(f"color: {self.COLOR_PRIMARY};")
        info_layout.addWidget(info_title)

        info_items = [
            "• 保存位置：源文件所在目录",
            "• 重名自动编号：file_1.md, file_2.md…",
            "• 支持批量同时转换",
        ]
        for item in info_items:
            l = QLabel(item)
            l.setFont(QFont("Microsoft YaHei", 8))
            l.setStyleSheet(f"color: {self.COLOR_TEXT};")
            info_layout.addWidget(l)

        layout.addWidget(info_box)

        layout.addStretch()

        return panel

    def _build_bottom(self):
        """底部：进度条 + 按钮"""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # 状态标签
        self.status_label = QLabel("准备就绪，请添加文件后点击开始转换")
        self.status_label.setFont(QFont("Microsoft YaHei", 9))
        self.status_label.setStyleSheet(f"color: {self.COLOR_TEXT_SEC};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self._progress_style())
        self.progress_bar.setMinimumHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 按钮行
        btn_layout = QHBoxLayout()

        # 统计标签
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Microsoft YaHei", 9))
        self.stats_label.setStyleSheet(f"color: {self.COLOR_TEXT_SEC};")
        btn_layout.addWidget(self.stats_label)

        btn_layout.addStretch()

        # 开始按钮
        self.convert_btn = QPushButton("🚀 开始转换")
        self.convert_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.setStyleSheet(self._convert_btn_style())
        self.convert_btn.setMinimumHeight(44)
        self.convert_btn.clicked.connect(self.start_convert)
        btn_layout.addWidget(self.convert_btn)

        layout.addLayout(btn_layout)

        return layout

    # ------------------------------------------------------------------
    # 样式定义
    # ------------------------------------------------------------------

    def _make_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {self.COLOR_BORDER}; max-height: 1px;")
        return sep

    def _make_primary_btn(self, text, slot):
        btn = QPushButton(text)
        btn.setFont(QFont("Microsoft YaHei", 9))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"background-color: {self.COLOR_PRIMARY_LIGHT}; "
            f"color: {self.COLOR_PRIMARY}; "
            f"border: 1px solid {self.COLOR_PRIMARY}; "
            f"border-radius: 8px; "
            f"padding: 8px 16px;"
        )
        btn.clicked.connect(slot)
        return btn

    def _btn_style(self, bg, color, border_color=None):
        bc = border_color or bg
        return (
            f"background-color: {bg}; color: {color}; "
            f"border: 1px solid {bc}; border-radius: 8px; "
            f"padding: 8px 16px;"
        )

    def _clear_btn_style(self):
        return (
            f"background-color: transparent; color: {self.COLOR_ERROR}; "
            f"border: 1px solid {self.COLOR_ERROR}; border-radius: 6px; "
            f"padding: 3px 10px; font-size: 9px;"
        )

    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: {self.COLOR_BG};
                color: {self.COLOR_TEXT};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border-color: {self.COLOR_PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {self.COLOR_TEXT_SEC};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.COLOR_CARD};
                color: {self.COLOR_TEXT};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {self.COLOR_PRIMARY_LIGHT};
            }}
        """

    def _file_list_style(self):
        return f"""
            QListWidget {{
                background-color: {self.COLOR_BG};
                border: 1px solid {self.COLOR_BORDER};
                border-radius: 8px;
                padding: 6px;
                outline: none;
            }}
            QListWidget::item {{
                background-color: {self.COLOR_CARD};
                border-radius: 6px;
                padding: 6px 8px;
                margin-bottom: 3px;
                border: 1px solid transparent;
            }}
            QListWidget::item:hover {{
                border-color: {self.COLOR_BORDER};
                background-color: #F0F4FC;
            }}
            QListWidget::item:selected {{
                background-color: {self.COLOR_PRIMARY_LIGHT};
                border-color: {self.COLOR_PRIMARY};
                color: {self.COLOR_PRIMARY};
            }}
        """

    def _progress_style(self):
        return f"""
            QProgressBar {{
                background-color: {self.COLOR_BORDER};
                border-radius: 4px;
                min-height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {self.COLOR_PRIMARY};
                border-radius: 4px;
            }}
        """

    def _convert_btn_style(self, enabled=True):
        if enabled:
            return (
                f"background-color: {self.COLOR_PRIMARY}; color: white; "
                f"border: none; border-radius: 10px; "
                f"padding: 10px 28px; font-size: 13px; font-weight: bold;"
            )
        else:
            return (
                f"background-color: {self.COLOR_BORDER}; color: {self.COLOR_TEXT_SEC}; "
                f"border: none; border-radius: 10px; "
                f"padding: 10px 28px; font-size: 13px;"
            )

    # ------------------------------------------------------------------
    # 文件操作
    # ------------------------------------------------------------------

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择要转换的文件",
            "",
            "支持的文件 (*.docx *.doc *.pdf *.md *.markdown *.txt);;所有文件 (*)",
        )
        if files:
            self.add_file_paths(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            paths = []
            for fmt in self.SUPPORTED_FORMATS:
                paths.extend(Path(folder).glob(fmt))
                # 递归
                paths.extend(Path(folder).rglob(fmt))
            # 去重
            unique = list({str(p) for p in paths})
            if unique:
                self.add_file_paths(unique)
            else:
                QMessageBox.information(
                    self, "提示", f"文件夹中未找到支持的文件：\n{', '.join(self.SUPPORTED_FORMATS)}"
                )

    def add_file_paths(self, paths):
        """添加文件路径，自动过滤重复"""
        fmt_names = {
            "md": "📝",
            "docx": "📄",
            "doc": "📋",
            "pdf": "📕",
            "txt": "📃",
        }
        added = 0
        for p in paths:
            if p not in self.file_list:
                self.file_list.append(p)
                ext = detect_format(p) or "txt"
                icon = fmt_names.get(ext, "📄")
                item = QListWidgetItem(f"{icon}  {os.path.basename(p)}")
                item.setData(Qt.ItemDataRole.UserRole, p)
                item.setFont(QFont("Microsoft YaHei", 9))
                self.file_list_widget.addItem(item)
                added += 1

        self.update_ui_state()
        if added > 0:
            self.status_label.setText(f"已添加 {added} 个文件（双击可移除）")
            self.status_label.setStyleSheet(f"color: {self.COLOR_SUCCESS}; font-size: 9px;")

    def clear_files(self):
        self.file_list.clear()
        self.file_list_widget.clear()
        self.update_ui_state()
        self.status_label.setText("文件列表已清空")
        self.status_label.setStyleSheet(f"color: {self.COLOR_TEXT_SEC}; font-size: 9px;")

    def remove_selected_file(self):
        """双击移除文件"""
        row = self.file_list_widget.currentRow()
        if row >= 0:
            self.file_list_widget.takeItem(row)
            self.file_list.pop(row)
            self.update_ui_state()

    def update_ui_state(self):
        """根据状态更新 UI"""
        count = len(self.file_list)
        self.file_count_label.setText(f"{count} 个文件")

        if count > 0:
            self.convert_btn.setEnabled(True)
            self.convert_btn.setStyleSheet(self._convert_btn_style(enabled=True))
        else:
            self.convert_btn.setEnabled(False)
            self.convert_btn.setStyleSheet(self._convert_btn_style(enabled=False))

    # ------------------------------------------------------------------
    # 拖放
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                paths.append(path)
            elif os.path.isdir(path):
                for fmt in self.SUPPORTED_FORMATS:
                    paths.extend(Path(path).glob(fmt))
                    paths.extend(Path(path).rglob(fmt))
        if paths:
            self.add_file_paths([str(p) for p in paths])
        event.acceptProposedAction()

    # ------------------------------------------------------------------
    # 转换
    # ------------------------------------------------------------------

    def start_convert(self):
        if not self.file_list:
            return

        target_format = self.format_combo.currentData()
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("转换中…")
        self.progress_bar.setValue(0)
        self.stats_label.setText("")
        self.status_label.setText("正在转换，请稍候…")
        self.status_label.setStyleSheet(f"color: {self.COLOR_PRIMARY}; font-size: 9px;")
        self.file_list_widget.clear()

        self.convert_thread = ConvertThread(self.file_list, target_format)
        self.convert_thread.progress.connect(self.on_convert_progress)
        self.convert_thread.finished.connect(self.on_convert_finished)
        self.convert_thread.start()

    def on_convert_progress(self, current, total, filename, success, msg):
        self.progress_bar.setValue(int(current / total * 100))
        self.status_label.setText(
            f"[{current}/{total}] 正在处理：{filename}  {'✅' if success else '❌'}"
        )

    def on_convert_finished(self, successes, failures):
        total = len(self.file_list)
        self.progress_bar.setValue(100)

        # 恢复按钮
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("🚀 开始转换")
        self.update_ui_state()

        # 重新显示文件列表
        self.file_list_widget.clear()
        self.file_list.clear()
        fmt_names = {
            "md": "📝", "docx": "📄", "doc": "📋",
            "pdf": "📕", "txt": "📃",
        }
        for path in successes + [f for f, _ in failures]:
            basename = os.path.basename(path)
            ext = detect_format(path) or "txt"
            icon = fmt_names.get(ext, "📄")
            item = QListWidgetItem(f"{icon}  {basename}")
            item.setFont(QFont("Microsoft YaHei", 9))
            if path not in successes:
                item.setForeground(Qt.GlobalColor.red)
            self.file_list_widget.addItem(item)
            self.file_list.append(path)

        # 结果提示
        success_count = len(successes)
        fail_count = len(failures)

        msg = []
        if success_count > 0:
            msg.append(f"✅ 成功转换 {success_count} 个文件")
        if fail_count > 0:
            msg.append(f"❌ {fail_count} 个文件失败")
            for path, err in failures:
                msg.append(f"  • {os.path.basename(path)}: {err[:60]}")

        self.status_label.setText(" | ".join(msg))
        self.stats_label.setText(f"✅ {success_count} 成功  ❌ {fail_count} 失败")

        # 弹出通知
        if success_count > 0:
            QMessageBox.information(
                self,
                "转换完成 ✅",
                f"成功: {success_count} 个文件\n失败: {fail_count} 个文件\n\n文件已保存到源文件目录"
            )

    # ------------------------------------------------------------------
    # 图标
    # ------------------------------------------------------------------

    @staticmethod
    def _icon_data():
        """返回一个简单的 SVG 矢量图标（转为 PNG bytes）"""
        import base64
        # 1x1 透明 PNG 占位，真实项目用资源文件
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
            "AAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGRSURB"
            "VFiF7ZcxTsNAEEX/rBMFCooUKSgoKFAoKCgoKLgAFVfgClyBK3AFrkBBQUFBQUFBwX9MJi6xN+JF"
            "iy08s+uZXdvxSm+1Wu1vjPkvRJRdA4DrAMC1uwPAbQBgdQ4AmgBANgOqAMDVBACuAgDZDOBqAADX"
            "AIDrAMB1AGAXAMBmAL8CAPkCANhNAMC1ACDfAAD5BgDYHAC4DgC4DgCY8wDQ/1ICmDMAYM4CwBwA"
            "gM0BANcBgFwAALoJAFwHALYTANgFALA5AGBzAGBzAGDOAMCeAQA9AwB6BgD0DACwOQBgMwDA5gCA"
            "awDAdQBgdwDA7ACAnQEAM+cBYBYA2BwAsAcAbA4A2BwAsDkAkAsAYDMAsAsAbA4AbA4AbA4AbA4A"
            "bA4AbA4AZgEAewYAzBkAsGcAwJwBgD0DAGYBANgM4P8C/A8A9QwAmDMAYO8BANkDAHYBANgTAHIX"
            "AMAeAIBdAAD5BgD0DACYOQBgzgDAngEAvQAA9gQAzBkAMGcAYBYAsGcAwJwBAHMGAOwJANgTAKBn"
            "AEDPAICeAQCbAwA2BwD2DADsGQCwJwBgTwDAngAAeQAA9gQAmDMAYO4AgM0BAHMGAPQMAAAAAACi"
            "2+12u93+N1T8Afd8e+0+4xZcAAAAAElFTkSuQmCC"
        )

    # ------------------------------------------------------------------
    # 双击删除
    # ------------------------------------------------------------------

    def mouseDoubleClickEvent(self, event):
        # 拦截双击事件，如果点在列表上则删除
        item = self.file_list_widget.itemAt(event.pos())
        if item:
            self.remove_selected_file()
        super().mouseDoubleClickEvent(event)


# ---------------------------------------------------------------
# 入口
# ---------------------------------------------------------------

def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # 全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
