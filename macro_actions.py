import os
from subprocess import check_output

import profiles
from debug import catch_errors


@catch_errors
def toggle_profile(*args, **kwargs):
    """
    name: Profile
    description: Cycle through fan, cpu and gpu profiles
    """
    return f"{str(profiles.toggle_profile())}"

@catch_errors
def toggle_refresh_rate(*args, **kwargs):
    """
    name: Refresh Rate
    description: Cycle through refresh rates of primary monitor
    """
    return f"{str(profiles.toggle_display_refreshrate())}"

@catch_errors
def system_command(*args, **kwargs):
    """
    name: System Command
    description: Run any system command like you would in CMD
    """
    print (f"Shell command: {args[0]}")
    return str(check_output(args[0], shell=True))
