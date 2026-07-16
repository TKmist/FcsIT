import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import urllib.request

version_path='VERSION'#os.path.join('src',)

with open(version_path, 'r') as file:
    VERSION = file.read()

win_packages = ['pywin32']
basic_packages = [
"dearpygui<2.0.0",
    "phconvert",
    "numpy==1.26.4",
    "pandas==2.2.3",
    "matplotlib==3.9.2",
    "scipy==1.15.3",
    'colorama',
    "sympy",
    "Pillow",
    "lmfit",
    "multipletau",
    "screeninfo==0.8.1",
    "numba==0.60.0",
    "requests==2.32.3",
    "decorator==5.2.1",
    "opencv-python==4.11.0.86",
    "scikit-image==0.25.2",
]
req_pack = []
if os.name == 'nt':
    req_pack = basic_packages + win_packages
elif os.name == 'posix':
    req_pack = basic_packages


class runInstall(install):
    """Download `readPTU_FLIM.py` from GitHub."""

        
    def run(self):
        # Run the standard install first
        install.run(self)
        
        # Read installer decision from environment
        flag = os.environ.get("FCSIT_DOWNLOAD_READPTU_FLIM", "").strip().lower()
        download_enabled = flag in ("1", "true", "yes", "y", "on")
        
        if not download_enabled:
            print("Skipping download of readPTU_FLIM.py (FCSIT_DOWNLOAD_READPTU_FLIM=0).")
            return
        
        # Specify the URL of the file on GitHub
        url = "https://raw.githubusercontent.com/TKmist/readPTU_FLIM/refs/heads/NIKON_correction/readPTU_FLIM.py"
        
        # Specify the target directory (e.g., where your package installs files)
        target_directory = os.path.join(os.path.dirname(__file__), "src","Methods","PTU_Corr","include","Third_party")
        target_file = os.path.join(target_directory, "readPTU_FLIM.py")
        
        # Ensure the target directory exists
        os.makedirs(target_directory, exist_ok=True)
        
        # Download the file
        try:
            print(f"Downloading `readPTU_FLIM.py` from {url} to {target_file}...")
            urllib.request.urlretrieve(url, target_file)
            print("\nDownload complete.\n")
        except Exception as e:
            print(f"\nFailed to download `readPTU_FLIM.py`: {e}")
            print(f"Please manually download the file from: {url}")
            print(f"Once downloaded, place it in the following directory: {target_directory}\n")


setup(
    name='FcsIT',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=req_pack,
    python_requires='>=3.11.5',
    cmdclass={
        'install': runInstall,  # Replace the install command
    },
    author='TKmist',
    license='GPL-3.0+',

)