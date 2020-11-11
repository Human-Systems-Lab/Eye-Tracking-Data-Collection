# Eye Tracking Data Collection
This repository provides a graphical user interface for a tool which is used for collecting eye tracking data from a webcam.  The program is written using pyqt5 to enable cross platform distribution.  Although it it not currently offered through PYPI, it will on the first stable release.

### Setup

##### Windows

Currently, the only method of running this application is from source.

If python is not yet installed on your computer, you can download it from [here](https://www.python.org/downloads/).  Ensure that in the setup, python is added to your path variables.  This can be checked using the following command:

 ```
python -V
```

You will also have to download this repository to your computer, which can be done using git.  If git is not installed on your computer, you can download it from [here](https://git-scm.com/download/win).  To make sure that git is installed on your computer and run the following command:

```
git --version
```

After you have verified that both python and git are installed on your computer, run the following command to install the Eye Tracking Data Collection software.

```
git clone https://github.com/Human-Systems-Lab/Eye-Tracking-Data-Collection.git
cd Eye-Tracking-Data-Collection
pip install -r requirements.txt
python main.py
```

To build the enitre program (including all dependancies) into a single execuable file, run the following command in the Python terminal. Building from the spec file allows for the inclusion of the assets.

```
pyinstaller "Eye Tracking Data Collector.spec" --onefile
```

This command requires the pyinstaller module, which can be installed using:

```
pip install pyinstaller
```

Runnning pyinstaller with these parameters will output a single exe file to the /dist folder within the project directory.

##### Ubuntu

##### Mac
