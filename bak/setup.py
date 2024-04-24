import os
cwd = os.getcwd()
from distutils.core import setup
from Cython.Build import cythonize
 
setup(ext_modules=cythonize([f"{cwd}/bak/secret_telegram.py"]))
setup(ext_modules=cythonize([f"{cwd}/bak/secret_hostname.py"]))
setup(ext_modules=cythonize([f"{cwd}/bak/secret_account.py"]))
