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

## Precompiled .exe

WIP



# Autostart with Windows

To make it auto-start with Windows in it's current state you should use Task Scheduler.

1. Open Task Scheduler, click "Create Task".
2. Name it "NoROG Startup", tick "Run with highest priviliges" (Needed to allow it to call atrofac and ryzenadj, otherwise they will not work)
3. On Triggers tab click on "New..."  and select "Beging the task: At log on"
4. On Actions tab click "New..." - choose "Action: Start a program", click "Browse...", navigate to NoROG folder and select "norog.bat"
5. Go to Conditions tab and uncheck "Stop if the computer switches to battery power" THEN uncheck "Start the task only if the computer is on AC power". This is a UI\UX disaster in Windows, but you have to uncheck them in this order, otherwise "Stop if the computer switches to battery power" remains checked but greyed out. But while it's greyed out it still will kill it if you switch to battery power.