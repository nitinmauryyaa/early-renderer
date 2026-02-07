from flask import Flask, request, jsonify, send_file
from playwright.sync_api import sync_playwright
import os, time, uuid

app = Flask(__name__)

BASE_DIR = os.getcwd()
OUTPUT = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT, exist_ok=True)


def render_html(html):

    # SAFE FILENAME
    name = uuid.uuid4().hex
    filename = name + ".png"

    path = os.path.join(OUTPUT, filename)

    with sync_playwright() as p:

        # ---- CRITICAL FIX FOR RENDER FREE ----
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        page = browser.new_page(
            viewport={"width":1080, "height":1350}
        )

        page.set_default_timeout(15000)

        page.set_content(html, wait_until="load")

        time.sleep(1)

        page.screenshot(path=path, full_page=True)

        browser.close()

    if not os.path.exists(path):
        raise Exception("Screenshot not created")

    return filename



@app.post("/render")
def render():

    data = request.json or {}

    slides = data.get("slides", [])

    paths = []

    for html in slides:

        filename = render_html(html)

        paths.append(filename)

    return jsonify({"paths": paths})



@app.get("/file/<name>")
def get_file(name):

    file_path = os.path.join(OUTPUT, name)

    if not os.path.exists(file_path):
        return "File not found", 404

    return send_file(file_path, mimetype="image/png")



@app.get("/")
def home():
    return "renderer alive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
