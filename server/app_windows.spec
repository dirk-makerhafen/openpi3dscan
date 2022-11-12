# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import pyhtmlgui


a = Analysis(['run_windows.py'],
             pathex=[],
             binaries=[],
             datas=[
                ('static/', "static"),
                ('templates/', "templates"),
                (os.path.join(os.path.split(pyhtmlgui.__file__)[0], "assets"), "pyhtmlgui/assets")
             ],
             hiddenimports=[],
             hookspath=["app_windows"],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=True,
             win_private_assemblies=True,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='RCautomation',
          debug=False,
          strip=False,
          upx=False,
          bootloader_ignore_signals=False,
          runtime_tmpdir=None,
          console=False )

'''
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RCautomation',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='RCAutomation')

'''