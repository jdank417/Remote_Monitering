"""
setup.py - the py2app setup script
"""
from setuptools import setup

APP = ['DankSquashPieMonitor.py']  # Your main entry point (contains if __name__ == '__main__':)
DATA_FILES = ['machines.json']  # Data files to include in the .app bundle
OPTIONS = {
    'argv_emulation': True,
    # If you have an icon, put its path here:
    'iconfile': 'icon.icns',
    'packages': ['paramiko', 'PyQt5'],
    # If you want to exclude some modules, you can do:
    # 'excludes': ['tkinter', 'unittest', ...],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
