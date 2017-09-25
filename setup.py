from cx_Freeze import setup, Executable
from versionControl import versionControl

setup(name = "SimCorpFinder" ,
      version = versionControl.version,
      description = "" ,
      executables = [Executable(
            "simCorpFinder.py",
            shortcutName="SimCorp Finder",
            shortcutDir="DesktopFolder"
      )],
      options = {
            'build_exe' : {
                  'packages':['asyncio', 'numpy', 'lxml'],
                  'include_files':['phantomjs','phantomjs.exe','statesFilter']
                  },
            # "bdist_msi": {
            #       'packages':['asyncio', 'numpy', 'lxml'],
            #       'include_files':['phantomjs','phantomjs.exe','statesFilter']
            #       }
            },
      )


# from cx_Freeze import setup, Executable
 
# # Dependencies are automatically detected, but it might need
# # fine tuning.
# buildOptions = dict(packages = [], excludes = [])
 
# import sys
# base = 'Win32GUI' if sys.platform=='win32' else None
 
# executables = [
#     Executable('simpleMenu.py', base=base)
# ]
 
# setup(
#     name='simpleMenu',
#     version = '0.1',
#     description = 'A PyQt Tetris Program',
#     options = dict(build_exe = buildOptions),
#     executables = executables
# )
