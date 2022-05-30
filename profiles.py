"""
https://github.com/cronosun/atrofac/blob/master/ADVANCED.md

"""
import os
from subprocess import check_output
from debug import get_logger
log = get_logger("default")

from configuration import main_config, cache_file
from paths import RES_DIR

import time


atrofac_cli = os.path.join(RES_DIR, "atrofac-cli.exe")
ryzenadj_cli = os.path.join(RES_DIR, "ryzenadj-win64", "ryzenadj.exe")
displays_cli = os.path.join(RES_DIR, "ChangeScreenResolution.exe")



PROFILE_DIRTY = False  # Tracks whether profile was changed and needs to be applied
REFRESH_RATE_DIRTY = False

def format_atrofac_curve(c):
    return f"30c:{c[0]}%,40c:{c[1]}%,50c:{c[2]}%,60c:{c[3]}%,70c:{c[4]}%,80c:{c[5]}%,90c:{c[6]}%,100c:{c[7]}%"

def apply_atrofac_profile(profile_data):

    profile = profile_data.get("profile")
    cpu_curve = profile_data.get("cpu")
    gpu_curve = profile_data.get("gpu")

    if not cpu_curve and not cpu_curve:
        cmd = f"{atrofac_cli} plan {profile}"
    else:
        cmd = f"{atrofac_cli} fan --plan {profile}"

    if cpu_curve:
        cmd += " --cpu "+format_atrofac_curve(cpu_curve)

    if gpu_curve:
        cmd += " --gpu "+format_atrofac_curve(gpu_curve)

    log.info(f"apply_atrofac_profile: {cmd}")
    log.info(check_output(cmd, shell=True))

def apply_ryzenadj_profile(profile_data):
    log.info(f"set_ryzenadj_profile: {profile_data}")
    cmd = f"{ryzenadj_cli}"
    for key, value in profile_data.items():
        if key != "name":
            milliwatts = value
            if milliwatts % 1000000 == 0:
                milliwatts = milliwatts / 1000;
            cmd += f" --{key}={milliwatts}"
    log.info(f"apply_ryzenadj_profile cmd: {cmd}")
    log.info(check_output(cmd, shell=True))
    # print(str(os.system(cmd)))

if cache_file.get("CURRENT_PROFILE") is None:
    cache_file.set("CURRENT_PROFILE", 0)
    first_launch = True
else:
    first_launch = False

# Maximum CPU frequency
# powercfg /setdcvalueindex SCHEME_CURRENT 54533251-82be-4824-96c1-47b60b740d00 75b0ae3f-bce0-45a7-8c89-c9611c25e100 0

def apply_powercfg_profile(profile_data):
    cmd = f"powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_PROCESSOR PERFBOOSTMODE {main_config['powercfg']['boost_modes'].index(profile_data['boost_mode'])}"
    log.info(f"apply_powercfg_profile: {cmd}")
    log.info(check_output(cmd, shell=True))

    cmd = f"powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_PROCESSOR PERFBOOSTMODE {main_config['powercfg']['boost_modes'].index(profile_data['boost_mode'])}"
    log.info(f"apply_powercfg_profile: {cmd}")
    log.info(check_output(cmd, shell=True))

    if main_config['powercfg'].get('gpu_instance_path') is not None:
        try:
            if profile_data.get('dgpu_disabled', False) is True:
                cmd = 'pnputil /disable-device "{}"'.format(main_config['powercfg']['gpu_instance_path'])
            else:
                cmd = 'pnputil /enable-device "{}"'.format(main_config['powercfg']['gpu_instance_path'])
            log.info(f"apply_powercfg_profile: {cmd}")
            log.info(check_output(cmd, shell=True))
        except Exception as e:
            log.info(e)

def toggle_profile():
    """
    Changes current profile in cache file, does not apply it.

    * This distinction is required to be able to toggle between profiles without applying changes until correct profile is selected.
    """
    global PROFILE_DIRTY
    i = cache_file.get("CURRENT_PROFILE") + 1
    if i >= len(main_config['power_presets']):
        i = 0

    cache_file.set("CURRENT_PROFILE", i)    
    PROFILE_DIRTY = True
    return main_config['power_presets'][i]['name']


def apply_current_profile():
    """
    Applies profile currently selected in cache file.

    * This distinction is required to be able to toggle between profiles without applying changes until correct profile is selected.
    """
    global PROFILE_DIRTY
    log.info("Applying current profile...")
    CURRENT_PROFILE = cache_file.get("CURRENT_PROFILE")

    # HINT This can be made more dynamic and less hardcoded, rely more on yaml config and key names
    power_presets = main_config['power_presets'][CURRENT_PROFILE]
    for key, value in power_presets.items():
        if key == "ryzenadj_presets":
            apply_ryzenadj_profile(main_config['ryzenadj_presets'][value])
        elif key == "atrofac":
            apply_atrofac_profile(value)
        elif key == "powercfg":
            apply_powercfg_profile(value)

    PROFILE_DIRTY = False
    return main_config['power_presets'][CURRENT_PROFILE]['name']


def apply_main_display_rate():
    global REFRESH_RATE_DIRTY
    
    CURRENT_REFRESH_RATE = cache_file.get("CURRENT_REFRESH_RATE")
    log.info(check_output(rf"{displays_cli} /d=0 /f={CURRENT_REFRESH_RATE}"))
    REFRESH_RATE_DIRTY = False

def toggle_display_refreshrate():
    global REFRESH_RATE_DIRTY

    CURRENT_REFRESH_RATE = cache_file.get("CURRENT_REFRESH_RATE")

    if CURRENT_REFRESH_RATE is None:
        cache_file.set("CURRENT_REFRESH_RATE", main_config['display']['max_refreshrate'])   
        CURRENT_REFRESH_RATE = main_config['display']['max_refreshrate']

    if CURRENT_REFRESH_RATE == main_config['display']['max_refreshrate']:
        cache_file.set("CURRENT_REFRESH_RATE", main_config['display']['min_refreshrate'])   
    elif CURRENT_REFRESH_RATE == main_config['display']['min_refreshrate']:
        cache_file.set("CURRENT_REFRESH_RATE", main_config['display']['max_refreshrate']) 

    REFRESH_RATE_DIRTY = True
    return cache_file.get("CURRENT_REFRESH_RATE")

if first_launch is False:
    # Apply current profile as set in cache on startup
    apply_current_profile()
