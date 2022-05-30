# NoROG

# DISCLAIMER: Use at your own risk. 
# This is alpha-quality software. It has not been extensively tested, though I personally run it daily on my laptop.


## This software, if used without caution, can cause damage to your system. It comes bundled and tested for Asus G733QS and configuration may need to be adjusted for other laptops. Refer to ryzenadj and atrofac documentations for details.

# What is it

NoROG is a replacement app for core functions of ASUS Armoury Crate, for ASUS laptops, for Windows. 
Developed and tested on G733QS.

Relies on atrofac and ryzenadj (bundled). At the moment configuration is done through config file.

## Goal

The goal of the project is to provide an alternative to core Armoury Crate functions without unnecessary bloat. Primarily this means changing fan profiles, because it's not something you can easily do with other software, as far as I know.

## Features

- Control fan profiles (silent, performance, turbo)
- Set custom fan curves
- Control Ryzen CPU attributes with ryzenadj
- Change refresh rate of main display (60, 300)
- Setup your own profiles in config file
- Bind Armoury Crate and Fan buttons on the keyboard to NoROG functions. By default:
    - Use Fan button to switch NoROG profiles
    - Use Armoury Crate button to switch primary screen refresh rate


# Installation

## With Python

1. Download and install Python from python.org (Version 3.8+)
2. Copy `config/config-example.yaml` file and rename copy to `config.yaml`. Open it and adjust to your liking.
3. Run `norog.bat` file by double clicking it (it will `pip install` dependencies and run norog.py)

### How to disable console window

If you want to disable console window that shows the log it's possible to do that. 

1. Make a copy of `norog.bat` file, you can call it anything, for example `norog_noconsole.bat`.
2. Change the second line from `python %~dp0\norog.py` to `C:\<path to your python installation>\pythonw.exe %~dp0\norog.py`
3. (Optional) You can additionally remove the first line if you want to skip dependency checking on every startup. Or you can write `@REM` in front of it to disable\comment it out, like this `@REM pip install -r %~dp0\requirements.txt`

Use this `.bat` file to start norog, and in Task Scheduler.

### How to make it start faster, skip checking for installed modules

The default `norog.bat` runs dependency check and installs required python modules. There's no reason to do it every time, for that you can use `norog_no_dependency_check.bat` instead.

## Precompiled .exe

WIP



# Autostart with Windows

To make it auto-start with Windows in it's current state you should use Task Scheduler.

1. Open Task Scheduler, click "Create Task".
2. Name it "NoROG Startup", tick "Run with highest priviliges" (Needed to allow it to call atrofac and ryzenadj, otherwise they will not work)
3. On Triggers tab click on "New..."  and select "Beging the task: At log on"
4. On Actions tab click "New..." - choose "Action: Start a program", click "Browse...", navigate to NoROG folder and select "norog.bat"
5. Go to Conditions tab and uncheck "Stop if the computer switches to battery power" THEN uncheck "Start the task only if the computer is on AC power". This is a UI\UX disaster in Windows, but you have to uncheck them in this order, otherwise "Stop if the computer switches to battery power" remains checked but greyed out. But while it's greyed out it still will kill it if you switch to battery power.


# Planned features, ToDo

- [ ] Support macro key combinations
- [ ] Support changing Windows power plans
- [ ] Support changing GPU modes, performance\power saving
- [ ] Support switching to iGPU (disabling discrete GPU)
- [ ] GUI


# Dev notes

```
const SW_DYNAMC_GRAPHICS = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
const GLOBAL_SETTINGS = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
const AC = '/setacvalueindex';
const DC = '/setdcvalueindex';

powercfg /getactivescheme

powercfg /q ${result.guid} ${SW_DYNAMC_GRAPHICS} ${GLOBAL_SETTINGS}
powercfg /q xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
powercfg ${AC} ${result.guid} ${SW_DYNAMC_GRAPHICS} ${GLOBAL_SETTINGS} ${setting}

Power Scheme GUID: xxxxxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  (High performance)
  GUID Alias: SCHEME_MIN
  Subgroup GUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  (Switchable Dynamic Graphics)
    Power Setting GUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  (Global Settings)
      Possible Setting Index: 000
      Possible Setting Friendly Name: Force power-saving graphics
      Possible Setting Index: 001
      Possible Setting Friendly Name: Optimize power savings
      Possible Setting Index: 002
      Possible Setting Friendly Name: Optimize performance
      Possible Setting Index: 003
      Possible Setting Friendly Name: Maximize performance
    Current AC Power Setting Index: 0x00000002
    Current DC Power Setting Index: 0x00000001
```