import PyInstaller.__main__
import os
import sys

current_dir = os.path.abspath(os.path.dirname(__file__))

options = [
    'main.py',
    '--name=SyntheticBandManager',
    '--onefile',
    '--windowed',
    '--add-data', f'{current_dir}/prompts;prompts',
    '--add-data', f'{current_dir}/*.md;.',
    '--add-data', f'{current_dir}/*.json;.',
    '--add-data', f'{current_dir}/style.css;.',
    '--add-binary', f'{current_dir}/style.css;.',
    '--add-data', f'{current_dir}/spinner.gif;.',
    '--icon', f'{current_dir}/icon.ico',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=openai',
    '--hidden-import=dotenv',
    '--exclude-module=transformers',
    '--exclude-module=torch',
    '--exclude-module=tensorflow',
    '--noupx',
    '--strip',
]

if sys.platform.startswith('win'):
    options.extend([
        '--add-binary', f'{sys.prefix}\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Core.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{sys.prefix}\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Gui.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{sys.prefix}\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Widgets.dll;PyQt5/Qt5/bin',
    ])

PyInstaller.__main__.run(options)