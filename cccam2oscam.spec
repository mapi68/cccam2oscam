# -*- mode: python ; coding: utf-8 -*-


block_cipher = None



# Importa il modulo datetime
import datetime

now = datetime.datetime.now()
VERSIONE = f"1.0.{now.month}.{now.day}"

# Determina la lista di tutti i .py nella cartella
import glob
py_files = glob.glob("*.py")


a = Analysis(
    py_files,
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=f'cccam2oscam_{VERSIONE}.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
	icon='icon.ico',
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)




import msvcrt
import shutil
import os

# Cerca se nella cartella di base c'è un file .exe e se esiste eliminalo
file_exe = [file for file in os.listdir(os.getcwd()) if file.endswith(".exe")]
if file_exe:
	for file in file_exe:
		os.remove(file)

# Domanda all'utente
print("\nVuoi spostare il file .exe dalla cartella 'dist/' alla cartella corrente? (s/n): ", end='', flush=True)

# Verifica della risposta
spostare_file = msvcrt.getwche().lower()
if spostare_file == 's':
    # Ottieni il percorso completo del file .exe nella cartella 'dist'
    dist_path = os.path.join(os.getcwd(), 'dist', exe.name)
	
    # Sposta il file .exe dalla cartella 'dist' alla cartella corrente
    shutil.move(dist_path, os.getcwd())

    # Rimuovi la cartella 'build' e 'dist' se esistono
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
	