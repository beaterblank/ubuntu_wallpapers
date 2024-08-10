# Upaper

## Overview

This Python project provides a utility for dynamically creating and applying wallpapers across multiple monitors with various fit types (e.g., fill, fit, stretch, tile, and center). It includes functionality to retrieve monitor information, generate wallpapers that span across multiple monitors, and apply these wallpapers in a Linux environment using gsettings.

## Installation

### Prerequisites
- Python 3.6 or above
- PIL (Pillow)
- jc
- Linux environment with gsettings and xrandr

### Install Dependencies

```{bash}
pip install pillow jc
```

finally clone this project
```{git}
git clone 
```

## Usage

This is currently a command-line utility this support will remain with a simple UI in future maybe support to gifs and across mutiple different types of os
There are 2 ways to run the command line utility one to set wallpaper to each monitor manually or set up a directory to select images randomly
both of them will set the `config.json` from which the wallpapers are generated

in src folder first run

```{bash}
chmod +x upaper
```

then run either

```{bash}
./upaper set
./upaper random <dir to randomly select wallpapers from>
```

idea to this is that ubuntu with multiple monitors and with positions setup will generate a bigger rectange of view we in that big rectangle place our wallpapers stategically to get the full wallpaper
