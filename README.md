# <h1 align="center">FcsIT</h1>

<p align="center">A simple and easy-to-use tool for correlating and fitting the fluorescence correlation spectroscopy (FCS) data.</p>

<h1></h1>

<p align="center">
  <a href="https://TKmist.github.io/FcsIT/">
    <img src="https://img.shields.io/badge/manual-online-darkgreen" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey" />
  <img src="https://img.shields.io/badge/version-v1.0.5-green" />
  
</p>
<p align="center">
  
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/license-GPLv3-blue.svg" />
  </a>
  <a href="https://github.com/TKmist/FcsIT/releases/latest">
    <img src="https://img.shields.io/github/v/release/TKmist/FcsIT?label=download" />
  </a>
  <a href="https://doi.org/10.5281/zenodo.19589716"><img src="https://zenodo.org/badge/1194606839.svg" alt="DOI"/></a>
</p>

<p align="center">
  <a href="#information">Information</a> •
  <a href="#installation">Installation</a> •
  <a href="#release-notes">Release notes</a> •
  <a href="#license">License</a>
</p>
<h1></h1>

## Information
FcsIT is a tool designed for analysing fluorescence correlation spectroscopy data in a platform-independent manner. It features an intuitive, easy-to-navigate interface powered by [Dear PyGui](https://github.com/hoffstadt/DearPyGui). 
It provides:    
- Reading the TTTR data,    
- TCSPC-based filtering,    
- Correlation of the TTTR data,    
- The calculation of the correlation data and its variance is based on the circular-block bootstrap method,    
- Nine predefined mathematical models for fitting FCS data,    
- Flexibility and user-friendlyness in adding user-defined models.

## Installation
On Linux machines, it is highly recommended to install Python 3.11 or 3.12. The Windows installation files are distributed together with the Python Embedded Distribution for Windows. Follow the steps below to install the software.    
1. Go to the release folder. Choose your OS version (Windows or Linux), download the proper *FcsIT_(version)_(OS)* file and extract it to the desired location.

2. Go to the extracted directory and run the installation script:

    1. On Linux in a terminal, run the bash script by typing:
   
       ./install.sh
       
    2. On Windows, double-click the _install_win.bat_ executable script.
  
Make sure you are not using a VPN, as it may block the installation of PIP in the Python embedded distribution. 
  
The installation script will download all required packages, create the run_FcsIT script or run_FcsIT.bat (on Windows), and create the shortcuts. 

## Release notes

#### v1.0.5
 - Python embedded folder fixed.
#### v1.0.4
 - Optimalisation of operations on chunks,
#### v1.0.3

 - Optional _light_ theme added,
 - Settings window moved to the new class in the INIT.py file.

#### v1.0.0
This is an initial release of the FcsIT software
## License

This project is licensed under the GNU General Public License v3.0 or later.
See the [LICENSE](LICENSE) file for the full license text.

This program is distributed WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

### Third-party components

This software incorporates a modified version of the `correlation_methods.py`
file [originally developed by Dominic Waithe](https://github.com/dwaithe/FCS_point_correlator/blob/master/focuspoint/correlation_methods/correlation_methods.py).

The original work is licensed under the GNU General Public License v2 or later.

Modifications were made for integration and customisation for this project.
Details of modifications are provided in the [modified file](src/Methods/PTU_Corr/include/correlation_methods.py).

---

During installation, this program may optionally download the `readPTU_FLIM.py`
component from an [external repository](https://github.com/TKmist/readPTU_FLIM/tree/NIKON_correction).

This component is licensed under the MIT License and is not distributed as part of this repository.

---

This software includes the Python Embedded Distribution for Windows,
which is licensed under the Python Software Foundation License (PSF).
License information is provided within the embedded distribution.

---

This repository includes DejaVu Sans Condensed font files (TTF),
which are distributed under their own license.
Please refer to the font files or accompanying license information for details.

---

### Academic use

If you use the FcsIT software or any part of it in your academic work, 
citation of the relevant publications listed below is appreciated.    
1. Kalwarczyk, T. (2026). FcsIT: An Open-Source, Cross-Platform Tool for Correlation and Analysis of Fluorescence Correlation Spectroscopy Data. https://doi.org/10.48550/arXiv.2603.29684
2. Kalwarczyk, T. (2026). FcsIT - A simple and easy-to-use tool for correlating and fitting the fluorescence correlation spectroscopy (FCS) data. https://doi.org/10.5281/zenodo.19351493
