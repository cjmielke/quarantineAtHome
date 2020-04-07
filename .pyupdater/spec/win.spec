# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['C:\\Users\\14157\\Desktop\\quarantineAtHome\\quarantine.py'],
             pathex=[
                'C:\\Users\\14157\\Desktop\\quarantineAtHome',
                'C:\\Users\\14157\\Desktop\\quarantineAtHome\\.pyupdater\\spec',
                'C:\\Users\\14157\\Desktop\\qah\\docking\\mglmin'
                ],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[u'c:\\users\\14157\\venv\\lib\\site-packages\\pyupdater\\hooks'],
             runtime_hooks=[],
             #excludes=[],
             excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += Tree('./docking/win32', prefix='docking/win32')
a.datas += Tree('./docking/mglmin', prefix='docking/mglmin')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='win',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon="icon.ico",
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='win')
