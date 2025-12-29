# theming.py
#
# Theme utilities + Qt stylesheet generation for MinusStems GUI.

from PyQt5 import QtCore, QtGui
from PyQt5.QtSvg import QSvgRenderer

from themes_data import THEMES


def _hex_to_rgb1(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return r, g, b


def _rel_lum(rgb):
    def _c(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * _c(r) + 0.7152 * _c(g) + 0.0722 * _c(b)


def _contrast_ratio(hex1, hex2):
    L1 = _rel_lum(_hex_to_rgb1(hex1))
    L2 = _rel_lum(_hex_to_rgb1(hex2))
    lighter, darker = (L1, L2) if L1 >= L2 else (L2, L1)
    return (lighter + 0.05) / (darker + 0.05)


def best_text_on(bg_hex, prefer_hex=None, target=4.5):
    """Return the best text color for a given background color."""
    if prefer_hex and _contrast_ratio(bg_hex, prefer_hex) >= target:
        return prefer_hex

    black = "#000000"
    white = "#FFFFFF"
    c_black = _contrast_ratio(bg_hex, black)
    c_white = _contrast_ratio(bg_hex, white)
    candidate = white if c_white >= c_black else black
    if _contrast_ratio(bg_hex, candidate) >= target:
        return candidate
    return candidate


# Keep the private alias for internal use
_best_text_on = best_text_on


LUCIDE_BRUSH_SVG = r'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
 viewBox="0 0 24 24" fill="none" stroke="{STROKE}" stroke-width="2"
 stroke-linecap="round" stroke-linejoin="round">
  <path d="M9.06 11.9l8.07-8.06a2.85 2.85 0 114.03 4.03l-8.06 8.08"/>
  <path d="M7.07 14.94c-1.66 0-3 1.35-3 3.02 0 1.33-2.5 1.52-2 2.02
           1.08 1.1 2.49 2.02 4 2.02 2.2 0 4-1.8 4-4.04a3.01 3.01 0 00-3-3.02z"/>
</svg>'''


def _svg_icon_from_string(svg_text, size_px=26):
    data = QtCore.QByteArray(svg_text.encode("utf-8"))
    renderer = QSvgRenderer(data)
    pm = QtGui.QPixmap(size_px, size_px)
    pm.fill(QtCore.Qt.transparent)
    p = QtGui.QPainter(pm)
    p.setRenderHint(QtGui.QPainter.Antialiasing, True)
    renderer.render(p, QtCore.QRectF(0, 0, size_px, size_px))
    p.end()
    return QtGui.QIcon(pm)


def make_paintbrush_icon(theme_key):
    if theme_key not in THEMES:
        theme_key = next(iter(THEMES.keys()))
    stroke = THEMES[theme_key]["submit"]
    svg = LUCIDE_BRUSH_SVG.format(STROKE=stroke)
    return _svg_icon_from_string(svg, size_px=26)


def apply_theme(app, name):
    if name not in THEMES:
        raise ValueError(
            f"Unknown theme '{name}'. Pick one of: {', '.join(THEMES.keys())}"
        )

    base = THEMES[name]

    def _lum(h):
        r, g, b = _hex_to_rgb1(h)
        return 0.2126 * (r ** 2.2) + 0.7152 * (g ** 2.2) + 0.0722 * (b ** 2.2)

    def _shift(h, pct):
        r, g, b = _hex_to_rgb1(h)
        if pct >= 0:
            r = r + (1.0 - r) * pct
            g = g + (1.0 - g) * pct
            b = b + (1.0 - b) * pct
        else:
            r = r * (1.0 + pct)
            g = g * (1.0 + pct)
            b = b * (1.0 + pct)
        return "#{:02x}{:02x}{:02x}".format(
            int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
        )

    def _hover_from(base_hex):
        return _shift(base_hex, +0.10 if _lum(base_hex) < 0.5 else -0.10)

    bg                = base["bg"]
    surface           = base["surface"]
    active_tab        = base["active_tab"]
    inactive_tab_drop = base["inactive_tab_drop"]
    border            = base["border"]
    submit            = base["submit"]
    submit_hover      = base["submit_hover"]
    active_option     = base["active_option"]
    text_color        = base["text"]

    tab_bg    = inactive_tab_drop
    tab_hover = _hover_from(inactive_tab_drop)

    btn       = surface
    btn_hover = _hover_from(surface)
    drop_bg   = inactive_tab_drop

    fg_global       = _best_text_on(bg, text_color)
    tab_text        = _best_text_on(tab_bg, fg_global)
    panel_text      = _best_text_on(active_tab, fg_global)
    btn_text        = _best_text_on(btn, fg_global)
    drop_text       = _best_text_on(drop_bg, fg_global)
    submit_text     = _best_text_on(submit, fg_global)
    active_opt_text = _best_text_on(active_option, fg_global)

    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window,          QtGui.QColor(bg))
    pal.setColor(QtGui.QPalette.WindowText,      QtGui.QColor(fg_global))
    pal.setColor(QtGui.QPalette.Base,            QtGui.QColor(surface))
    pal.setColor(QtGui.QPalette.AlternateBase,   QtGui.QColor(bg))
    pal.setColor(QtGui.QPalette.Text,            QtGui.QColor(fg_global))
    pal.setColor(QtGui.QPalette.Button,          QtGui.QColor(btn))
    pal.setColor(QtGui.QPalette.ButtonText,      QtGui.QColor(btn_text))
    pal.setColor(QtGui.QPalette.Highlight,       QtGui.QColor(active_option))
    pal.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(active_opt_text))
    pal.setColor(QtGui.QPalette.ToolTipBase,     QtGui.QColor(surface))
    pal.setColor(QtGui.QPalette.ToolTipText,     QtGui.QColor(fg_global))
    app.setPalette(pal)

    style = f"""
    QWidget#root {{
        background-color: {bg};
        color: {fg_global};
    }}

    QFrame#inner {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 10px;
    }}

    QTabBar {{
        background: {surface};
        color: {tab_text};
    }}
    QTabBar::tab {{
        background: {tab_bg};
        color: {tab_text};
        padding: 6px 12px;
        border: 1px solid {border};
        border-bottom: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        margin-right: 2px;
    }}
    QTabBar::tab:hover {{
        background: {tab_hover};
        color: {tab_text};
    }}
    QTabBar::tab:selected {{
        background: {active_tab};
        color: {panel_text};
        border: 1px solid {border};
        border-bottom: none;
        margin-bottom: -1px;
        margin-left: 0px;
    }}

    QTabWidget::pane {{
        background: {active_tab};
        border: 1px solid {border};
        border-top-left-radius: 0px;
        border-top-right-radius: 10px;
        border-bottom-left-radius: 10px;
        border-bottom-right-radius: 10px;
        top: -1px;
        padding-top: 6px;
    }}

    QWidget#tabpage {{
        background-color: transparent;
        border: none;
        color: {panel_text};
    }}

    QWidget[role="matchpane"] {{
        background: transparent;
        border: none;
        color: {panel_text};
    }}

    QLabel {{
        background-color: transparent;
        color: {panel_text};
    }}

    QLabel#drop {{
        background: {drop_bg};
        color: {drop_text};
        border: 2px solid {border};
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
    }}

    QLabel#minus {{
        color: {panel_text}AA;
        font-weight: bold;
    }}
    QLabel#status {{
        color: {panel_text}CC;
    }}

    QPushButton {{
        background-color: {btn};
        color: {btn_text};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 6px 12px;
        margin: 0;
    }}
    QPushButton:!checked:hover {{
        background-color: {btn_hover};
        color: {btn_text};
    }}
    QPushButton:checked {{
        background-color: {active_option};
        color: {active_opt_text};
        border: 2px solid {submit};
        font-weight: 600;
    }}
    QPushButton:checked:hover {{
        background-color: {active_option};
        color: {active_opt_text};
        border: 2px solid {submit};
    }}

    QPushButton#primary {{
        background-color: {submit};
        color: {submit_text};
        border: 1px solid {submit};
        font-weight: 600;
        padding: 8px 12px;
    }}
    QPushButton#primary:hover {{
        background-color: {submit_hover};
        color: {submit_text};
        border: 1px solid {submit_hover};
    }}

    QToolButton#themeBtn {{
        background: {btn};
        color: {btn_text};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 4px;
    }}
    QToolButton#themeBtn:hover {{
        background: {btn_hover};
        color: {btn_text};
        border: 1px solid {border};
    }}
    QToolButton#themeBtn::menu-indicator {{
        image: none;
        width: 0px;
        height: 0px;
    }}
    """
    app.setStyleSheet(style)
