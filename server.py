from flask import Flask, request, jsonify, send_file
from playwright.sync_api import sync_playwright
import os, time, uuid

app = Flask(__name__)

OUTPUT = "output"
os.makedirs(OUTPUT, exist_ok=True)

def render_html(html):

    # Generate safe filename – NO SPACES EVER
    name = str(uuid.uuid4()).replace(" ", "").replace("-", "")

    filename = f"{name}.png"

    path = f"{OUTPUT}/{filename}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":1080,"height":1350})

        page.set_content(html, wait_until="load")
        time.sleep(0.8)

        page.screenshot(path=path, full_page=True)
        browser.close()

    return filename   # only clean filename



@app.post("/render")
def render():

    data = request.json
    slides = data.get("slides", [])

    paths = []

    for html in slides:
        p = render_html(html)
        paths.append(p)

    return jsonify({"paths": paths})


@app.get("/file/<name>")
def get_file(name):
    return send_file(f"{OUTPUT}/{name}", mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
