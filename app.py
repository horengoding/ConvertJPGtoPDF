from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from PIL import Image
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("images")
    if not files or files[0].filename == "":
        return "Tidak ada gambar yang diupload", 400

    session_id = str(uuid.uuid4())
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)

    imagelist = []
    for i, file in enumerate(files):
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        save_path = os.path.join(session_folder, f"{i}{ext}")
        file.save(save_path)
        imagelist.append(save_path)

    for path in imagelist:
        im = Image.open(path)
        im = im.convert("RGB")
        width, height = im.size
        if width > height:
            im = im.transpose(Image.ROTATE_270)
        im.save(path)

    pdf = FPDF()
    for image in imagelist:
        pdf.add_page()
        pdf.image(image, 0, 0, 210, 297)

    output_path = os.path.join(session_folder, "dan yap.pdf")
    pdf.output(output_path, "F")

    return send_file(output_path, as_attachment=True, download_name="dan yap.pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
