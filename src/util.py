import os
import jc
import enum
import typing

import subprocess

PathLike = typing.Union[str, bytes, os.PathLike]
List = typing.List


def set_picture_spanned(to:str="background"):
    """
    Set the BG picture to spanned mode
    """
    if not to in ["background","screensaver"]:
        raise ValueError("to should either be 'background' or 'screensaver'")
    
    result = subprocess.run(['which', 'gsettings'], 
            capture_output=True, text=True, check=True)
    
    if not result.stdout.strip():
        raise Exception("gsettings not found or not in $PATH")

    subprocess.run(['gsettings', 'set', f'org.gnome.desktop.{to}', 
        'picture-options', 'spanned'], check=True)
    

def set_wallpaper_from(image_path):
    result = subprocess.run(['which', 'gsettings'], 
            capture_output=True, text=True, check=True)
    
    if not result.stdout.strip():
        raise Exception("gsettings not found or not in $PATH")
    
    image_path = os.path.abspath(image_path)
    
    command = ['gsettings', 'set', 'org.gnome.desktop.background', 
            'picture-uri', f'file://{image_path}']
    
    subprocess.run(command, check=True)
 
    command = ['gsettings', 'set', 'org.gnome.desktop.background', 
            'picture-uri-dark', f'file://{image_path}']
    
    subprocess.run(command, check=True)

def get_monitor_info():
    xrandr_command_output = subprocess.run(['xrandr'],
            capture_output=True, text=True, check=True).stdout.strip()
    if not xrandr_command_output:
        raise Exception("Something wrong with xrandr")
    return jc.parse('xrandr', xrandr_command_output)
