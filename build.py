import PyInstaller.__main__
import os

# Obtenir le chemin absolu du répertoire courant
current_dir = os.path.abspath(os.path.dirname(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--add-data', f'{current_dir}\\prompts;prompts',
    '--add-data', f'{current_dir}\\*.md;.',
    '--add-data', f'{current_dir}\\*.json;.',
    '--name', 'SyntheticBandManager',
    '--icon', f'{current_dir}/icon.ico',  # Assurez-vous d'avoir une icône icon.ico dans votre dossier
])
