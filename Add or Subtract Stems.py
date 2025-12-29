# Add or Subtract Stems.py
#   Main entry point for Add or Subtract Stems application.
#
#   Build EXE with:
#   pyinstaller "Add or Subtract Stems.spec" --noconfirm
#
#   Windows: after building, make the correct icon show by copying the EXE to your Desktop with:
#   Copy-Item "dist\Add or Subtract Stems.exe" -Destination "$env:USERPROFILE\OneDrive\Desktop\Add or Subtract Stems.exe" -Force

import sys
from PyQt5 import QtWidgets, QtCore
from theming import apply_theme
from themes_data import THEMES
from main_window import MainWindow

ORG_NAME = "MinusStems"
APP_NAME = "MinusStemsGUI"
DEFAULT_THEME = "desert_hc"


def main():
    app = QtWidgets.QApplication(sys.argv)

    settings = QtCore.QSettings(ORG_NAME, APP_NAME)
    saved_theme = settings.value("theme", DEFAULT_THEME, type=str)
    if saved_theme not in THEMES:
        saved_theme = DEFAULT_THEME

    apply_theme(app, saved_theme)

    w = MainWindow(settings)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
