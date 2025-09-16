from typing import List
import vd2svg
import json
import os
import re

HEX_PATTERN = re.compile(r'#[A-Fa-f0-9]{6}')
SHORT_HEX_PATTERN = re.compile(r'[A-Fa-f0-9]{6}')

def createBackground(hex:str):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="432" height="432" viewBox="0 0 432 432"><rect width="432" height="432" fill="{hex}" /></svg>'

def _extract_svg_content(svg):
    match = re.search(r'<svg[^>]*>(.*?)</svg>', svg, re.DOTALL)
    return match.group(1) if match else svg

def _extract_viewbox(svg):
    match = re.search(r'<svg[^>]*viewBox="([^"]+)"', svg)
    if match:
        return [float(x) for x in match.group(1).split()]
    
    return [0, 0, 432, 432]

def merge_svgs(fg:str, bg:str) -> str:
    scale = 0.8
    size = 432

    fg_content = _extract_svg_content(fg)
    bg_content = _extract_svg_content(bg)
    fg_viewbox = _extract_viewbox(fg)
    fg_vbx, fg_vby, fg_vbw, fg_vbh = fg_viewbox

    # Calculate scale to fit foreground to 0.8 of background size
    scale_x = (size * scale) / fg_vbw
    scale_y = (size * scale) / fg_vbh
    offset_x = (size - size * scale) / 2 - fg_vbx * scale_x
    offset_y = (size - size * scale) / 2 - fg_vby * scale_y

    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">{bg_content}<g transform="translate({offset_x},{offset_y}) scale({scale_x},{scale_y})">{fg_content}</g></svg>'


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

        self.svg = merge_svgs(self.foreground.svg, self.background.svg)


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