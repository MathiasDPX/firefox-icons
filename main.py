from flask import Flask
from icons import *

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run()