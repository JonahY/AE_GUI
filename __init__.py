# encoding: utf-8
"""
@version: 2.0
@author: Jonah
@file: __init__.py
@Created time: 2020/12/15 00:00
@Last Modified: 2021/12/24 22:02
"""

# Step for Pyinstall
# Step 1: Copy ./ssqueezepy/configs.py To .../Lib/site-packages/ssqueezepy/configs.py
# Step 2: pyinstaller -D -w -i logo.ico Visualization.py
#         pyinstaller -F -w -i logo.ico Visualization.py
# Step 3: Copy ./lic to .../software/lic

# Step for use
# Install the latest Visual C++ Redistributable

# According to the generated .spec file can be packaged directly (Helper, Visualization-D-c, Visualization-D-w,
#                                                                 Visualization-F-c, Visualization-F-w)
# Step 1: change XXX to XXX.spec
# Step 2: pyinstaller XXX.spec
# Step 3: change XXX.spec to XXX
