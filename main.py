import cairosvg
import vd2svg
import json

class AppIcon:
    def __init__(self,
                aliasSuffix :str,
                title :str,
                subtitle :str = None,
                iconForeground :str ="firefox",
                iconBackground :str = "#ffffff",
            ):
        self.aliasSuffix = aliasSuffix
        self.iconForeground = iconForeground
        self.iconBackground = iconBackground
        self.title = title
        self.subtitle = subtitle

    def __repr__(self):
        return f'<AppIcon title="{self.title}">'

raw_icons = json.load(open("icons.json", "r", encoding="utf-8"))
icons = {}

for key, icon in raw_icons.items():
    icons[key] = AppIcon(**icon)

def toSVG(vd:str) -> str:
    svg = vd2svg.convertVd(vd)
    return svg