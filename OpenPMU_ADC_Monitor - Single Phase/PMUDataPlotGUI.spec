# -*- mode: python -*-

block_cipher = None


a = Analysis(['PMUPhasorPlotGUI.py'],
             pathex=['.',
             '..\\..'],
             binaries=None,
             datas=None,
             hiddenimports=["estimation.interface"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PMUPhasorPlotGUI',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PMUPhasorPlotGUI')
