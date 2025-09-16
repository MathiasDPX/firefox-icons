from typing import List
import vd2svg
import json
import os
import re

HEX_PATTERN = re.compile(r'#[A-Fa-f0-9]{6}')

def createBackground(hex:str):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="432" height="432" viewBox="0 0 432 432"><rect width="432" height="432" fill="{hex}" /></svg>'

class Background:
    def __init__(self, id, svg=None):
        self.id = id

        if svg is None:
            self.svg = vd2svg.convert_vector_drawable_to_svg(os.path.join("icons", "background", f"{id}.xml"))
        else:
            self.svg = createBackground(svg)


class Foreground:
    def __init__(self, id, svg=None):
        self.id = id

        if svg is None:
            self.svg = vd2svg.convert_vector_drawable_to_svg(os.path.join("icons", "foreground", f"{id}.xml"))
        else:
            self.svg = createBackground(svg)


class AppIcon:
    def __init__(self,
                aliasSuffix :str,
                title :str,
                subtitle :str = None,
                iconForeground :str ="firefox",
                iconBackground :str = "#ffffff",
            ):
        self.aliasSuffix = aliasSuffix
        self.title = title
        self.subtitle = subtitle
        self.iconForeground = iconForeground
        self.iconBackground = iconBackground

        self.background = Background(iconBackground if HEX_PATTERN.match(iconBackground) else iconBackground, iconBackground if HEX_PATTERN.match(iconBackground) else None)
        self.foreground = Foreground(iconForeground)

    def __repr__(self):
        return f'<AppIcon title="{self.title}">'
    

raw_icons = json.load(open("icons.json", "r", encoding="utf-8"))
icons = {}

for key, icon in raw_icons.items():
    icons[key] = AppIcon(**icon)


_foregrounds = {}
_backgrounds = {}


for key, app_icon in icons.items():
    if app_icon.iconForeground not in _foregrounds:
        _foregrounds[app_icon.iconForeground] = app_icon.foreground
    if app_icon.iconBackground not in _backgrounds:
        _backgrounds[app_icon.iconBackground] = app_icon.background

def getForeground(id) -> Foreground:
    return _foregrounds.get(id)

def getBackground(id) -> Background:
    return _backgrounds.get(id)

def getIcon(id) -> AppIcon:
    return icons.get(id)

def hasForeground(id) -> bool:
    return id in _foregrounds

def hasBackground(id) -> bool:
    return id in _backgrounds

def hasIcon(id) -> bool:
    return id in icons

def getForegrounds() -> List[Foreground]:
    return list(_foregrounds.values())

def getBackgrounds() -> List[Background]:
    return list(_backgrounds.values())

def getIcons() -> List[AppIcon]:
    return list(icons.values())