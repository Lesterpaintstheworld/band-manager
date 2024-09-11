import PyInstaller.__main__
import os
import sys

# Obtenir le chemin absolu du répertoire courant
current_dir = os.path.abspath(os.path.dirname(__file__))

# Définir les options pour PyInstaller
options = [
    'main.py',
    '--name=SyntheticBandManager',
    '--onefile',
    '--windowed',
    '--add-data', f'{current_dir}/prompts;prompts',
    '--add-data', f'{current_dir}/*.md;.',
    '--add-data', f'{current_dir}/*.json;.',
    '--add-data', f'{current_dir}/style.css;.',
    '--add-data', f'{current_dir}/spinner.gif;.',
    '--icon', f'{current_dir}/icon.ico',
    '--hidden-import=PyQt5',
    '--hidden-import=openai',
    '--hidden-import=dotenv',
]

# Ajouter des options spécifiques à Windows si nécessaire
if sys.platform.startswith('win'):
    options.extend([
        '--add-binary', f'{sys.prefix}\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Core.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{sys.prefix}\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Gui.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{sys.prefix}\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Widgets.dll;PyQt5/Qt5/bin',
    ])

# Exécuter PyInstaller
PyInstaller.__main__.run(options)
