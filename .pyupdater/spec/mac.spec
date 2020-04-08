# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['/Users/me/PycharmProjects/quarantineAtHome/quarantine.py'],
             pathex=[
             	'/Users/me/PycharmProjects/quarantineAtHome',
             	'/Users/me/PycharmProjects/quarantineAtHome/.pyupdater/spec',
             	'/Users/me/PycharmProjects/quarantineAtHome/docking/mglmin'
             	],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[u'/Users/me/PycharmProjects/quarantineAtHome/venv/lib/python2.7/site-packages/pyupdater/hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += Tree('./docking/MacOSX', prefix='docking/MacOSX')
a.datas += Tree('./docking/mglmin', prefix='docking/mglmin')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='mac',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon=None,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mac')

app = BUNDLE(coll, name='QuarantineAtHome.app', icon='icon.icns', bundle_identifier='QuarantineAtHome')

