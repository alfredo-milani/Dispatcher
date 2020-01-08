# Table of contents
1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Installation](#installation)
    1. [Optional](#installation-optional)
    2. [Mandatory](#installation-mandatory)
4. [Usage](#usage)
5. [Note](#note)



## 1. Introduction <a name="introduction"></a>
Tool to categorize files once they are moved to a directory.

This tool allows you to define multiple directories to observe 
and allows you to define custom file formats and rules to follow.

## 2. Requirements <a name="requirements"></a>
The use of [pip-tools](https://pypi.org/project/pip-tools/) 
is recommended to install required dependencies.

## 3. Installation <a name="installation"></a>

### 3.1 Optional <a name="installation-optional"></a>

```bash
# Install virtualenv package for Python:
pip install virtualenv

# Create virtual environment named Dispatcher:
virtualenv Dispatcher
# or
virtualenv -p python3 Dispatcher

# Activate virtual environment:
source Dispatcher/bin/activate

# Deactivate virtual environment:
deactivate
```

### 3.2 Mandatory <a name="installation-mandatory"></a>

```bash
# Install required pip-tools for requirements installation:
alias py='python -m pip'
py install pip-tools

# Move to root project directory:
cd /project_root/

# Read requirements to install:
pip-compile --output-file requirements.txt requirements.in

# Install required packages:
pip-sync
```

## 4. Usage <a name="usage"></a>

Launch tool:

```bash
# Start main:
python src/Application.py

# or you can specify a configuration file:
python src/Application.py /path/custom_config.ini
```

Configurations file example:
```ini
# Legend
#   [opt] := optional parameter
#   [dft] := default value
#   [mnd] := mandatory parameter


[GENERAL]
# [opt] - Log directory. If no directory will be specified no log file will be created
# [dft] -
log.dir = /var/log

# [opt] - Directory for temporary files
# [dft] - /tmp
# tmp = /Volumes/Ramdisk/tmp

# [opt] - Threads for files handling
# [dft] - 2
threads = 3


[DISPATCHER]
# [mnd] - Specify files' extensions
# NOTE: directories and files without extension will be ignored
formats = {
            'F1' : [ '.jpg', '.jpeg', '.mp4', '.mp3', '.gif', '.png' ],
            'F2' : [ '.odt', '.txt', '.pdf', '.doc', '.docx', '.pptx', '.ppt' ]
          }

# [mnd] - Specify source directories to observe
sources = {
            'S1' : '/Volumes/Ramdisk/Downloads',
            'S2' : '/Volumes/Ramdisk/Downloads_2'
          }

# [opt] - Frequency (seconds) for checking new files
# [dft] - 1
sources.timeout = 0.5

# [mnd] - Specify destination directories
# NOTE: all not existing destinations directories will be created
# NOTE 2: files with the same name of new ones will be overwritten
destinations = {
                'D1' : '/Volumes/Ramdisk/ALL',
                'D2' : '/Volumes/Ramdisk/Media',
                'D3' : '/Volumes/Ramdisk/Documents'
               }

# [mnd] - Create rules
#   Every rule must have 'format', 'sources' and 'destinations' keys.
#   - 'format' key specify which file format to filter
#   - 'sources' key specify which directory to observe
#   - 'destinations' key specify where files, which match 'format' key, will be moved in
rules = {
            'R1' : {
                'formats' : [ 'F1' ],
                'sources' : [ 'S2' ],
                'destinations' : [ 'D2' ]
            },
            'R2' : {
                'formats' : [ 'F2' ],
                'sources' : [ 'S1', 'S2' ],
                'destinations' : [ 'D3' ]
            },
            'R3' : {
                'formats' : [ 'F1', 'F2' ],
                'sources' : [ 'S1', 'S2' ],
                'destinations' : [ 'D1' ]
            }
        }
```