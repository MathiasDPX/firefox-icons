from flask import Flask, request, render_template
from icons import *

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", 
                            foregrounds=getForegrounds(),
                            backgrounds=getBackgrounds()
                        )


@app.route("/api/foreground/<id>")
def api_foreground(id:str):
    if not hasForeground(id):
        return {"error": True, "message": "Foreground not found"}

    foreground = getForeground(id)
    return foreground.svg


@app.route("/api/background/<id>")
def api_background(id:str):
    if not hasBackground(id):
        return {"error": True, "message": "Background not found"}

    background = getBackground(id)
    return background.svg


@app.route("/api/icon/<id>")
def api_icon(id: str):
    if not hasIcon(id):
        return {"error": True, "message": "Icon not found"}

    icon = getIcon(id)

    return icon.svg


@app.route("/api/custom")
def api_custom():
    fg = request.args.get("fg", "firefox")
    bg = request.args.get("bg", "#ffffff")

    if not hasForeground(fg):
        return {"error": True, "message": "Foreground not found"}

    if not hasBackground(bg):
        if not HEX_PATTERN.match(bg):
            return {"error": True, "message": "Background not found"}
        background = Background(None, "#"+bg)
    else:
        background = getBackground(bg)

    foreground = getForeground(fg)

    return merge_svgs(foreground.svg, background.svg)


if __name__ == "__main__":
    app.run(debug=True)