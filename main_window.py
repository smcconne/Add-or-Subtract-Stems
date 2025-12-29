# main_window.py
#
# MainWindow implementation for MinusStems GUI.

import os
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from themes_data import THEMES
from theming import apply_theme, make_paintbrush_icon, best_text_on
from audio_io import load_audio
from drop_area import DropArea


def get_resource_path(filename):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return os.path.join(sys._MEIPASS, filename)
    else:
        # Running in development
        return os.path.join(os.path.dirname(__file__), filename)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, settings: QtCore.QSettings):
        super().__init__()

        self.settings = settings
        self.setObjectName("root")
        self.setWindowTitle("Add or Subtract Stems")
        self.setMinimumSize(720, 420)

        # Set app icon
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        self.output_format = "FLAC"
        self._fmt_pairs = []

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        self.inner = QtWidgets.QFrame()
        self.inner.setObjectName("inner")
        inner_v = QtWidgets.QVBoxLayout(self.inner)
        inner_v.setContentsMargins(12, 12, 12, 12)
        inner_v.setSpacing(10)

        self.tabs = QtWidgets.QTabWidget()
        self.lower_volume_tab = self._build_lower_volume_tab()
        self.subtract_stems_tab = self._build_subtract_stems_tab()
        self.tabs.addTab(self.lower_volume_tab, "Add Stems")
        self.tabs.addTab(self.subtract_stems_tab, "Subtract stems")

        inner_v.addWidget(self.tabs)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setObjectName("status")
        self.status_label.setOpenExternalLinks(True)
        inner_v.addWidget(self.status_label)

        outer.addWidget(self.inner)

        self._install_theme_corner()

        # Show attribution on startup
        self._show_attribution()

    def _show_attribution(self):
        """Show icon attribution with proper theme color."""
        theme_key = self.settings.value("theme", next(iter(THEMES.keys())), type=str)
        if theme_key in THEMES:
            text_color = THEMES[theme_key].get("text", "#888888")
        else:
            text_color = "#888888"
        self.status_label.setText(
            f'<a href="https://www.flaticon.com/authors/pop-vectors" style="color: {text_color};">App icon by Pop Vectors</a>'
        )

    # ---------- Theme corner ----------

    # Rainbow category definitions (name, hue range min, hue range max, folder color)
    # Hue ranges are 0-360; neutral is for low saturation colors
    RAINBOW_CATEGORIES = [
        ("Neutral", "#888888"),  # Low saturation
        ("Red", "#E41A1C"),       # 0-15, 345-360
        ("Orange", "#E0A458"),    # 15-45
        ("Yellow", "#D7A900"),    # 45-70
        ("Green", "#10B981"),     # 70-165
        ("Cyan", "#00B5C8"),      # 165-200
        ("Blue", "#268BD2"),      # 200-260
        ("Purple", "#A78BFA"),    # 260-290
        ("Pink", "#E7298A"),      # 290-345
    ]

    @staticmethod
    def _hex_to_hsv(hex_color):
        """Convert hex color to HSV (hue 0-360, sat 0-1, val 0-1)."""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        diff = max_c - min_c
        if diff == 0:
            h = 0
        elif max_c == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_c == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        s = 0 if max_c == 0 else diff / max_c
        v = max_c
        return h, s, v

    @classmethod
    def _get_color_category(cls, hex_color):
        """Return category index based on hue of hex color."""
        h, s, v = cls._hex_to_hsv(hex_color)
        # Low saturation = neutral
        if s < 0.15:
            return 0  # Neutral
        # Map hue to category
        if h < 15 or h >= 345:
            return 1  # Red
        elif h < 45:
            return 2  # Orange
        elif h < 70:
            return 3  # Yellow
        elif h < 165:
            return 4  # Green
        elif h < 200:
            return 5  # Cyan
        elif h < 260:
            return 6  # Blue
        elif h < 290:
            return 7  # Purple
        else:
            return 8  # Pink

    def _build_theme_menu(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu(self)
        group = QtWidgets.QActionGroup(menu)
        group.setExclusive(True)

        current = self.settings.value("theme", next(iter(THEMES.keys())), type=str)

        # Build category buckets based on submit color
        category_themes = [[] for _ in self.RAINBOW_CATEGORIES]
        for key in THEMES.keys():
            submit_color = THEMES[key].get("submit", "#888888")
            cat_idx = self._get_color_category(submit_color)
            category_themes[cat_idx].append(key)

        for idx, (category_name, category_color) in enumerate(self.RAINBOW_CATEGORIES):
            theme_keys = category_themes[idx]
            if not theme_keys:
                continue  # Skip empty categories
            submenu = QtWidgets.QMenu(category_name, menu)
            # Create a colored icon for the submenu title
            pm = QtGui.QPixmap(12, 12)
            pm.fill(QtGui.QColor(category_color))
            submenu.setIcon(QtGui.QIcon(pm))

            for key in theme_keys:
                title = key.replace("_", " ").title()
                act = QtWidgets.QAction(title, submenu)
                act.setCheckable(True)
                act.setData(key)
                if key == current:
                    act.setChecked(True)
                # Create colored icon from theme's submit color
                theme_color = THEMES[key].get("submit", "#888888")
                icon_pm = QtGui.QPixmap(12, 12)
                icon_pm.fill(QtGui.QColor(theme_color))
                act.setIcon(QtGui.QIcon(icon_pm))
                submenu.addAction(act)
                group.addAction(act)
            menu.addMenu(submenu)

        def _on_triggered(action: QtWidgets.QAction):
            theme_key = action.data()
            self._on_theme_selected(theme_key)
            QtCore.QTimer.singleShot(
                0, lambda: self._theme_button.setMenu(self._build_theme_menu())
            )

        group.triggered.connect(_on_triggered)
        return menu

    def _install_theme_corner(self):
        self._theme_button = QtWidgets.QToolButton(self)
        self._theme_button.setObjectName("themeBtn")
        self._theme_button.setAutoRaise(True)
        self._theme_button.setCursor(QtCore.Qt.PointingHandCursor)
        self._theme_button.setIcon(self._make_paintbrush_icon())
        self._theme_button.setIconSize(QtCore.QSize(22, 22))
        self._theme_button.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self._theme_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self._theme_button.setFixedSize(34, 34)
        self._theme_button.setMenu(self._build_theme_menu())

        self.installEventFilter(self)
        self._reposition_theme_button_window(dx=20, dy=20)
        self._theme_button.raise_()

    def _on_theme_selected(self, theme_key: str):
        if theme_key not in THEMES:
            raise ValueError("Unknown theme selected.")
        app = QtWidgets.QApplication.instance()
        apply_theme(app, theme_key)
        self.settings.setValue("theme", theme_key)
        self._theme_button.setIcon(self._make_paintbrush_icon())
        self._reposition_theme_button_window()

    def _make_paintbrush_icon(self):
        theme_key = self.settings.value("theme", None, type=str)
        if theme_key not in THEMES:
            theme_key = next(iter(THEMES.keys()))
        return make_paintbrush_icon(theme_key)

    def _reposition_theme_button_window(self, dx: int = 20, dy: int = 20):
        if not hasattr(self, "_theme_button"):
            return
        btn = self._theme_button
        x = max(0, self.width() - btn.width() - dx)
        y = max(0, dy)
        btn.move(x, y)
        btn.raise_()

    # ---------- Output format controls ----------

    def _make_format_selector(self):
        container = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        flac_btn = QtWidgets.QPushButton("FLAC")
        wav_btn = QtWidgets.QPushButton("WAV")
        for b in (flac_btn, wav_btn):
            b.setCheckable(True)
            b.setMinimumWidth(84)
            b.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            b.setStyleSheet("QPushButton { padding: 6px 8px; margin: 0; }")

        group = QtWidgets.QButtonGroup(container)
        group.setExclusive(True)
        group.addButton(flac_btn)
        group.addButton(wav_btn)

        if self.output_format == "FLAC":
            flac_btn.setChecked(True)
        else:
            wav_btn.setChecked(True)

        flac_btn.clicked.connect(lambda: self._set_output_format("FLAC"))
        wav_btn.clicked.connect(lambda: self._set_output_format("WAV"))

        self._fmt_pairs.append((flac_btn, wav_btn))

        lay.addWidget(flac_btn)
        lay.addWidget(wav_btn)
        return container, flac_btn, wav_btn

    def _set_output_format(self, fmt):
        if fmt not in ("FLAC", "WAV"):
            raise ValueError("Unsupported output format.")
        self.output_format = fmt
        for flac_btn, wav_btn in self._fmt_pairs:
            bs1 = flac_btn.blockSignals(True)
            bs2 = wav_btn.blockSignals(True)
            flac_btn.setChecked(fmt == "FLAC")
            wav_btn.setChecked(fmt == "WAV")
            flac_btn.blockSignals(bs1)
            wav_btn.blockSignals(bs2)
        self._update_lv_button_text()

    def _write_audio(self, out_path_base, data, sr):
        import soundfile as sf
        if self.output_format == "FLAC":
            out_path = f"{out_path_base}.flac"
            sf.write(out_path, data, sr, format="FLAC", subtype="PCM_16", compression_level=1.0)
            return out_path
        else:
            out_path = f"{out_path_base}.wav"
            sf.write(out_path, data, sr, format="WAV", subtype="PCM_16")
            return out_path

    # ---------- Lower volume tab ----------

    def _build_lower_volume_tab(self):
        tab = QtWidgets.QWidget()
        tab.setObjectName("tabpage")
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(0)
        layout.setContentsMargins(12, 12, 12, 8)

        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(8)
        top_row.setContentsMargins(0, 0, 0, 0)

        self.lv_drop = DropArea("Drag song audio here", allow_multiple=True)
        top_row.addWidget(self.lv_drop)

        self.lv_minus = QtWidgets.QLabel("-")
        self.lv_minus.setObjectName("minus")
        self.lv_minus.setAlignment(QtCore.Qt.AlignCenter)
        self.lv_minus.setFixedWidth(20)
        top_row.addWidget(self.lv_minus)

        self.lv_controls_container = QtWidgets.QWidget()
        self.lv_controls_container.setProperty("role", "matchpane")
        self.lv_controls_container.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        controls_v = QtWidgets.QVBoxLayout(self.lv_controls_container)
        controls_v.setContentsMargins(8, 8, 8, 8)
        controls_v.setSpacing(0)

        # Buttons row - vertically centered
        controls_v.addStretch(1)

        self.lv_row_widget = QtWidgets.QWidget()
        lv_buttons_row = QtWidgets.QHBoxLayout(self.lv_row_widget)
        lv_buttons_row.setSpacing(6)
        lv_buttons_row.setContentsMargins(0, 0, 0, 0)

        self.lv_db_values = [0, -1, -6]
        label_map = {0: "0", -1: "1", -6: "6"}
        self.lv_buttons = []
        self.lv_button_group = QtWidgets.QButtonGroup(self)
        self.lv_button_group.setExclusive(True)

        for db in self.lv_db_values:
            btn = QtWidgets.QPushButton(label_map[db])
            btn.setCheckable(True)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            btn.setMinimumWidth(0)
            btn.setStyleSheet("QPushButton { padding: 6px 12px; }")
            self.lv_button_group.addButton(btn)
            self.lv_buttons.append(btn)
            lv_buttons_row.addWidget(btn, 1)

        lv_db_label = QtWidgets.QLabel("db")
        lv_db_label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        lv_buttons_row.addWidget(lv_db_label)

        controls_v.addWidget(self.lv_row_widget)
        controls_v.addStretch(1)

        # Header as overlay, positioned above the button row
        self.lv_hdr = QtWidgets.QLabel("Lower volume then sum:", self.lv_controls_container)
        self.lv_hdr.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lv_hdr.setObjectName("sectionhdr")
        self.lv_hdr.adjustSize()
        self.lv_controls_container.installEventFilter(self)

        top_row.addWidget(self.lv_controls_container)
        top_row.setStretch(0, 1)
        top_row.setStretch(1, 0)
        top_row.setStretch(2, 1)
        layout.addLayout(top_row, 1)

        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.setContentsMargins(0, 8, 0, 0)
        self.lv_clear_button = QtWidgets.QPushButton("Clear")
        self.lv_run_button = QtWidgets.QPushButton()
        self.lv_run_button.setObjectName("primary")
        self.lv_clear_button.setFixedWidth(80)
        self.lv_run_button.setMinimumWidth(260)
        self.lv_run_button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.lv_run_button.setStyleSheet("QPushButton { padding: 8px 12px; }")
        self.lv_fmt_container, self.lv_fmt_flac, self.lv_fmt_wav = self._make_format_selector()

        bottom_row.addWidget(self.lv_clear_button)
        bottom_row.addStretch(1)
        bottom_row.addWidget(self.lv_run_button, 3)
        bottom_row.addStretch(1)
        bottom_row.addWidget(self.lv_fmt_container, 0, QtCore.Qt.AlignRight)
        layout.addLayout(bottom_row, 0)

        if self.lv_buttons:
            self.lv_buttons[0].setChecked(True)
        self._update_lv_button_text()
        self.lv_button_group.buttonClicked.connect(self._update_lv_button_text)
        self.lv_drop.files_changed.connect(self._update_lv_button_text)

        self.lv_run_button.clicked.connect(self._run_lower_volume)
        self.lv_clear_button.clicked.connect(self._clear_lower_volume)

        return tab

    def _get_selected_lv_db(self):
        for btn, db in zip(self.lv_buttons, self.lv_db_values):
            if btn.isChecked():
                return db
        if self.lv_buttons:
            self.lv_buttons[0].setChecked(True)
            return self.lv_db_values[0]
        raise RuntimeError("No dB option buttons configured.")

    def _update_lv_button_text(self):
        db = self._get_selected_lv_db()
        file_count = len(self.lv_drop.paths)
        if file_count > 1:
            if db == 0:
                self.lv_run_button.setText("Add Stems")
            else:
                self.lv_run_button.setText(f"Add stems @ {db}db")
        else:
            if db == 0:
                self.lv_run_button.setText(f"Convert to {self.output_format}")
            else:
                self.lv_run_button.setText(f"Lower volume {db}db")

    def _clear_lower_volume(self):
        self.lv_drop.clear_files()
        self.set_status("Cleared Add Stems tab.")

    def _run_lower_volume(self):
        stems = self.lv_drop.paths
        if not stems:
            raise RuntimeError("No stems provided. Drop one or more audio files in the left area.")

        db = float(self._get_selected_lv_db())

        gain = 10.0 ** (db / 20.0)

        if len(stems) == 1:
            # Single file: just lower volume
            self.set_status(f"Lowering volume {db}db...")
            path = stems[0]
            data, sr = load_audio(path)
            result = data * gain
            base = os.path.splitext(os.path.basename(path))[0]
            out_base = os.path.join(os.path.dirname(path), f"{base} {db}db")
            out_path = self._write_audio(out_base, result, sr)
            self.set_status("Done lowering volume.")
            QtWidgets.QMessageBox.information(self, "Success", f"Created:\n{out_path}")
        else:
            # Multiple files: lower volume then sum together
            self.set_status(f"Adding {len(stems)} stems at {db}db...")

            # Load first file to get reference sr and shape
            first_data, sr = load_audio(stems[0])
            first_data = first_data.astype(np.float64) * gain
            max_len = first_data.shape[0]
            channels = first_data.shape[1]

            combined = first_data.copy()

            for path in stems[1:]:
                stem_data, stem_sr = load_audio(path)
                if stem_sr != sr:
                    raise ValueError(
                        f"Sample rate mismatch: {os.path.basename(path)} has {stem_sr} Hz, expected {sr} Hz."
                    )

                # Handle channel mismatch
                if stem_data.shape[1] != channels:
                    if stem_data.shape[1] == 1 and channels == 2:
                        stem_data = np.repeat(stem_data, 2, axis=1)
                    elif stem_data.shape[1] == 2 and channels == 1:
                        stem_data = stem_data.mean(axis=1, keepdims=True)
                    else:
                        raise ValueError(f"Channel mismatch for {os.path.basename(path)}.")

                stem_data = stem_data.astype(np.float64) * gain

                # Extend combined if this stem is longer
                if stem_data.shape[0] > max_len:
                    pad = np.zeros((stem_data.shape[0] - max_len, channels), dtype=np.float64)
                    combined = np.vstack((combined, pad))
                    max_len = stem_data.shape[0]

                # Pad stem if shorter
                if stem_data.shape[0] < max_len:
                    pad = np.zeros((max_len - stem_data.shape[0], channels), dtype=stem_data.dtype)
                    stem_data = np.vstack((stem_data, pad))

                combined += stem_data

            # Check for clipping and ask user
            peak = float(np.max(np.abs(combined)))
            total_db = db  # Track total dB reduction for filename
            if peak > 1.0:
                # Calculate how much dB reduction is needed
                reduction_db = 20.0 * np.log10(peak)
                reduction_db_str = f"{reduction_db:.1f}"

                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Audio Clipping Detected")
                msg_box.setText(
                    f"The combined audio would clip (peak: {peak:.2f}).\n\n"
                    f"Would you like to lower the volume to prevent clipping?"
                )
                # Apply theme colors to message box
                theme_key = self.settings.value("theme", None, type=str)
                if theme_key and theme_key in THEMES:
                    theme = THEMES[theme_key]
                    msg_box.setStyleSheet(f"""
                        QMessageBox {{
                            background-color: {theme.get('surface', '#ffffff')};
                            color: {theme.get('text', '#000000')};
                        }}
                        QMessageBox QLabel {{
                            color: {theme.get('text', '#000000')};
                        }}
                    """)
                yes_btn = msg_box.addButton(f"Yes, lower {reduction_db_str}db", QtWidgets.QMessageBox.AcceptRole)
                no_btn = msg_box.addButton("No, let it clip", QtWidgets.QMessageBox.ActionRole)
                # Add a hidden cancel button for X/Esc handling
                cancel_btn = msg_box.addButton(QtWidgets.QMessageBox.Cancel)
                cancel_btn.hide()
                msg_box.setEscapeButton(cancel_btn)
                # Style Yes button like primary (Add Stems) button
                if theme_key and theme_key in THEMES:
                    theme = THEMES[theme_key]
                    submit_bg = theme.get('submit', '#4a90d9')
                    submit_hover_bg = theme.get('submit_hover', '#3a80c9')
                    submit_text = best_text_on(submit_bg, theme.get('text'))
                    yes_btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {submit_bg};
                            color: {submit_text};
                            padding: 6px 12px;
                            border-radius: 4px;
                            font-weight: 600;
                        }}
                        QPushButton:hover {{
                            background-color: {submit_hover_bg};
                        }}
                    """)
                    # Style No button like Clear button (regular button)
                    surface_bg = theme.get('surface', '#e0e0e0')
                    surface_text = best_text_on(surface_bg, theme.get('text'))
                    no_btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {surface_bg};
                            color: {surface_text};
                            padding: 6px 12px;
                            border-radius: 4px;
                            border: 1px solid {theme.get('border', '#cccccc')};
                        }}
                        QPushButton:hover {{
                            background-color: {theme.get('inactive_tab_drop', '#d0d0d0')};
                        }}
                    """)
                msg_box.exec_()

                clicked = msg_box.clickedButton()
                if clicked == cancel_btn or clicked is None:
                    # X button or Esc was pressed, cancel the operation
                    self.set_status("Add stems cancelled.")
                    return
                elif clicked == yes_btn:
                    combined = combined / peak
                    total_db = db - reduction_db  # Add the extra reduction to total
                # else: no_btn clicked, let it clip, continue saving

            # Use first file's directory and create output name
            first_base = os.path.splitext(os.path.basename(stems[0]))[0]
            total_db_str = f"{total_db:.1f}" if total_db != int(total_db) else str(int(total_db))
            out_base = os.path.join(os.path.dirname(stems[0]), f"{first_base} +{len(stems)-1} stems {total_db_str}db")
            out_path = self._write_audio(out_base, combined, sr)

            self.set_status(f"Saved: {os.path.basename(out_path)}")

    # ---------- Subtract stems tab ----------

    def _build_subtract_stems_tab(self):
        tab = QtWidgets.QWidget()
        tab.setObjectName("tabpage")
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setSpacing(0)
        layout.setContentsMargins(12, 12, 12, 8)

        drops_row = QtWidgets.QHBoxLayout()
        drops_row.setSpacing(8)
        drops_row.setContentsMargins(0, 0, 0, 0)

        self.ss_orig_drop = DropArea("Drag song audio here", allow_multiple=False)
        drops_row.addWidget(self.ss_orig_drop)

        ss_minus = QtWidgets.QLabel("-")
        ss_minus.setObjectName("minus")
        ss_minus.setAlignment(QtCore.Qt.AlignCenter)
        ss_minus.setFixedWidth(20)
        drops_row.addWidget(ss_minus)

        self.ss_stems_drop = DropArea("Drag your stems here", allow_multiple=True)
        drops_row.addWidget(self.ss_stems_drop)

        drops_row.setStretch(0, 1)
        drops_row.setStretch(1, 0)
        drops_row.setStretch(2, 1)
        layout.addLayout(drops_row, 1)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 8, 0, 0)
        self.ss_clear_button = QtWidgets.QPushButton("Clear")
        self.ss_run_button = QtWidgets.QPushButton("Subtract stems")
        self.ss_run_button.setObjectName("primary")

        self.ss_clear_button.setFixedWidth(80)
        self.ss_run_button.setMinimumWidth(260)
        self.ss_run_button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.ss_run_button.setStyleSheet("QPushButton { padding: 8px 12px; }")

        self.ss_fmt_container, self.ss_fmt_flac, self.ss_fmt_wav = self._make_format_selector()

        buttons_layout.addWidget(self.ss_clear_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.ss_run_button, 3)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.ss_fmt_container, 0, QtCore.Qt.AlignRight)

        layout.addLayout(buttons_layout, 0)

        self.ss_run_button.clicked.connect(self._process_subtract_stems)
        self.ss_clear_button.clicked.connect(self._clear_subtract_stems)

        return tab

    def _clear_subtract_stems(self):
        self.ss_stems_drop.clear_files()
        self.ss_orig_drop.clear_files()
        self.set_status("Cleared Subtract Stems tab.")

    def _process_subtract_stems(self):
        stems = self.ss_stems_drop.paths
        orig_list = self.ss_orig_drop.paths
        if not stems:
            raise RuntimeError("No stems provided. Drop one or more stems in the right area.")
        if not orig_list:
            raise RuntimeError("No original song provided. Drop an audio file in the left area.")

        orig_path = orig_list[-1]

        self.set_status("Loading original...")
        orig_data, sr = load_audio(orig_path)
        max_len = orig_data.shape[0]
        channels = orig_data.shape[1]
        if max_len == 0:
            raise ValueError("Original file has no audio samples.")

        self.set_status("Loading and summing stems...")
        combined = np.zeros_like(orig_data, dtype=np.float64)
        for stem_path in stems:
            stem_data, stem_sr = load_audio(stem_path)
            if stem_sr != sr:
                raise ValueError(
                    f"Sample rate mismatch: {os.path.basename(stem_path)} has {stem_sr} Hz, expected {sr} Hz."
                )

            if stem_data.shape[1] != channels:
                if stem_data.shape[1] == 1 and channels == 2:
                    stem_data = np.repeat(stem_data, 2, axis=1)
                elif stem_data.shape[1] == 2 and channels == 1:
                    stem_data = stem_data.mean(axis=1, keepdims=True)
                else:
                    raise ValueError(f"Channel mismatch for {os.path.basename(stem_path)}.")

            if stem_data.shape[0] < max_len:
                pad = np.zeros((max_len - stem_data.shape[0], channels), dtype=stem_data.dtype)
                stem_data = np.vstack((stem_data, pad))
            elif stem_data.shape[0] > max_len:
                stem_data = stem_data[:max_len, :]

            combined += stem_data.astype(np.float64)

        self.set_status("Phase inverting stems and combining with original...")
        inverted = -combined
        result = orig_data.astype(np.float64) + inverted

        peak = float(np.max(np.abs(result)))
        if peak > 1.0 and peak > 0.0:
            result = result / peak

        base = os.path.splitext(os.path.basename(orig_path))[0]
        out_base = os.path.join(os.path.dirname(orig_path), f"{base} minus stems")

        self.set_status("Writing output...")
        out_path = self._write_audio(out_base, result, sr)

        self.set_status(f"Done: {out_path}")
        QtWidgets.QMessageBox.information(self, "Success", f"Created:\n{out_path}")

    # ---------- Shared helpers ----------

    def set_status(self, text):
        self.status_label.setText(text)
        QtWidgets.QApplication.processEvents()

    def error_box(self, msg):
        QtWidgets.QMessageBox.critical(self, "Error", msg)
        self.set_status("Error.")

    def eventFilter(self, obj, ev):
        if obj is self and ev.type() in (
            QtCore.QEvent.Resize,
            QtCore.QEvent.Move,
            QtCore.QEvent.Show,
            QtCore.QEvent.LayoutRequest,
        ):
            self._reposition_theme_button_window()
        if obj is self.lv_controls_container and ev.type() in (
            QtCore.QEvent.Resize,
            QtCore.QEvent.LayoutRequest,
        ):
            self._reposition_lv_header()
        return super().eventFilter(obj, ev)

    def _reposition_lv_header(self):
        if not hasattr(self, "lv_hdr") or not hasattr(self, "lv_row_widget"):
            return
        row_pos = self.lv_row_widget.pos()
        hdr_h = self.lv_hdr.sizeHint().height()
        self.lv_hdr.move(8, row_pos.y() - hdr_h - 6)
        self.lv_hdr.adjustSize()
