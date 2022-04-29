from Detector import *
from random import seed
from flask import Flask, flash, jsonify, render_template, url_for, request, redirect
from PIL import ImageColor
from colorharmonies import *
from color_generator import *
import os
import time
import cv2
import uuid

# Model
# from Wall_Detection_Model.wallDetector import WallDetector
from image_processor import ImageProcessor

# Model = WallDetector()
detector = Detector("PS")
imageProcessor = ImageProcessor()

UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MaskGen = {}
highlightColor = (8, 255, 8)

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            # flash('No file part')
            print("no file uploaded")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            # flash('No selected file')
            print("empty file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4())  # secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}.png"))
            # print(os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.png"))
            # print("file uploaded", f"{filename}.png")
            return redirect(f"{request.url}{filename}")
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/<file_name>", methods=["GET", "POST"])
def visualizer(file_name):
    # print("----------------------------------------------", file_name)
    if "favicon" in file_name:
        return {}
    colorPalatte = suggest(file_name)
    return render_template("visualizer.html", image=file_name, colors=colorPalatte)


@app.route("/<file_name>/detect", methods=["GET", "POST"])
def detect(file_name):
    imgPath = f"{app.config['UPLOAD_FOLDER']}/{file_name}.png"
    img = cv2.imread(imgPath)

    if file_name not in MaskGen:
        # detectedWall = Model.getResult(img)
        predictions, segmentInfo = detector.onImage(imgPath)
        MaskGen[file_name] = [predictions, segmentInfo]
        # SeedPoints[file_name] = (156, 213)
        # SeedPoints[file_name] = imageProcessor.getSeedPoint(detectedWall)
    predictions, segmentInfo = MaskGen[file_name]
    color = highlightColor
    if request.method == "POST":
        # print(request.json)
        color = ImageColor.getcolor(request.json["colour"], "RGB")[::-1]

    wallsDetected = imageProcessor.getDetectedWalls(img, predictions, segmentInfo)

    wallColor = imageProcessor.getWallColor(wallsDetected)

    floodFillMask = imageProcessor.getFloodfillMask(img)

    colorMask = imageProcessor.getColorMask(wallsDetected, wallColor)

    result = imageProcessor.getWallMask(img, colorMask, floodFillMask, color)

    filename = f"{file_name}-output.png"
    cv2.imwrite(f"{app.config['UPLOAD_FOLDER']}/{filename}", result)

    return jsonify({"image": url_for("static", filename=f"images/{filename}")})


@app.route("/<file_name>/paint", methods=["GET", "POST"])
def paint(file_name):
    img = cv2.imread(f"{app.config['UPLOAD_FOLDER']}/{file_name}.png")
    highlightedWall = cv2.imread(
        f"{app.config['UPLOAD_FOLDER']}/{file_name}-output.png"
    )

    paintedWall = imageProcessor.applyPaint(img, highlightedWall)

    filename = f"{file_name}-painted.png"
    cv2.imwrite(f"{app.config['UPLOAD_FOLDER']}/{filename}", paintedWall)

    # time.sleep(2)
    return jsonify({"image": url_for("static", filename=f"images/{filename}")})


@app.route("/<file_name>/suggest", methods=["GET", "POST"])
def suggest(file_name):
    # print("----------------------------------------------", file_name)
    colors = extractColors(f"{app.config['UPLOAD_FOLDER']}/{file_name}.png")
    result = {}

    def rgbToHex(color):
        return "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])

    for color in colors[:4]:
        strColor = rgbToHex(color[0])
        result[strColor] = [strColor]
        rgbColor = Color(color[0], "", "")
        result[strColor].extend(list(map(rgbToHex, splitComplementaryColor(rgbColor))))
        result[strColor].extend(list(map(rgbToHex, triadicColor(rgbColor))))

    # return jsonify(result)
    return result


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
