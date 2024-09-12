import PyInstaller.__main__
import os
import sys
import site
import PyQt5
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ajouter le répertoire courant au chemin de recherche
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)
logging.info(f"Répertoire courant ajouté au chemin de recherche: {current_dir}")

# Obtenir le chemin des packages site-packages
site_packages = site.getsitepackages()[0]
logging.info(f"Chemin des packages site-packages: {site_packages}")

# Obtenir le chemin d'installation de PyQt5
pyqt5_path = os.path.dirname(PyQt5.__file__)
logging.info(f"Chemin d'installation de PyQt5: {pyqt5_path}")

options = [
    'main.py',
    '--name=BandManager',
    '--onefile',
    '--windowed',
    '--add-data', f'{current_dir}\\prompts;prompts',
    '--add-data', f'{current_dir}\\*.md;.',
    '--add-data', f'{current_dir}\\*.json;.',
    '--add-data', f'{current_dir}\\style.css;.',
    '--add-data', f'{current_dir}\\spinner.gif;.',
    '--add-data', f'{current_dir}\\.env;.',
    '--add-data', f'{current_dir}\\splash.png;.',
    '--icon', f'{current_dir}/icon.ico',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=openai',
    '--hidden-import=dotenv',
    '--exclude-module=transformers',
    '--exclude-module=torch',
    '--exclude-module=tensorflow',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    f'--add-data={site_packages}\\Lib\\site-packages\\numpy;numpy',
    '--noupx',
    '--log-level=DEBUG',
    '--add-data', f'{site_packages}\\Lib\\site-packages\\numpy;numpy',
    '--add-data', f'{site_packages}\\Lib\\site-packages\\matplotlib;matplotlib',
]

if sys.platform.startswith('win'):
    options.extend([
        '--add-binary', f'{pyqt5_path}\\Qt5\\bin\\Qt5Core.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{pyqt5_path}\\Qt5\\bin\\Qt5Gui.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{pyqt5_path}\\Qt5\\bin\\Qt5Widgets.dll;PyQt5/Qt5/bin',
        '--add-binary', f'{pyqt5_path}\\Qt5\\plugins\\platforms\\qwindows.dll;PyQt5/Qt5/plugins/platforms',
    ])

try:
    logging.info("Démarrage du processus de construction...")
    PyInstaller.__main__.run(options)
    logging.info("Construction terminée avec succès.")

    # Afficher le chemin de l'exécutable généré
    output_path = os.path.join(current_dir, 'dist', 'BandManager.exe')
    logging.info(f"Exécutable généré : {output_path}")
    
    if os.path.exists(output_path):
        logging.info("L'exécutable a été créé avec succès.")
    else:
        logging.error("L'exécutable n'a pas été trouvé à l'emplacement attendu.")

except Exception as e:
    logging.error(f"Une erreur s'est produite lors de la construction : {str(e)}")
    sys.exit(1)

logging.info("Processus de construction terminé.")
