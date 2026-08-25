from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
from PIL import Image
import os
import uuid

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

import time
import shutil

def cleanup_old_sessions(max_age_hours=1):
    now = time.time()
    max_age_seconds = max_age_hours * 3600

    if not os.path.exists(UPLOAD_FOLDER):
        return

    for session_name in os.listdir(UPLOAD_FOLDER):
        session_path = os.path.join(UPLOAD_FOLDER, session_name)
        if os.path.isdir(session_path):
            folder_age = now - os.path.getmtime(session_path)
            if folder_age > max_age_seconds:
                try:
                    shutil.rmtree(session_path)
                    print(f"Cleaned up old session: {session_name}")
                except Exception as e:
                    print(f"Failed to clean up {session_name}: {e}")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    cleanup_old_sessions(max_age_hours=1)
    files = request.files.getlist("images")
    orientations = request.form.getlist("orientations")

    if not files or files[0].filename == "":
        return jsonify({"error": "No image has been uploaded"}), 400

    session_id = str(uuid.uuid4())
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)

    imagelist = []
    for i, file in enumerate(files):
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        save_path = os.path.join(session_folder, f"{i}{ext}")
        file.save(save_path)

        try:
            im = Image.open(save_path)
            im = im.convert("RGB")
            im.save(save_path, "JPEG")
            im.close()
        except Exception as e:
            print(f"Error processing image: {e}")

        imagelist.append(save_path)

    pdf = FPDF()

    for image_path, orientation in zip(imagelist, orientations):
        page_orientation = 'L' if orientation == 'landscape' else 'P'
        pdf.add_page(orientation=page_orientation)

        if page_orientation == 'L':
            pdf.image(image_path, x=10, y=10, w=277)
        else:
            pdf.image(image_path, x=10, y=10, w=190)

    output_path = os.path.join(session_folder, "dan-yap.pdf")
    pdf.output(output_path, "F")

    return jsonify({"session_id": session_id})


@app.route("/preview/<session_id>")
def preview(session_id):
    path = os.path.join(UPLOAD_FOLDER, session_id, "dan-yap.pdf")
    if not os.path.exists(path):
        return "PDF not found", 404
    return send_file(path, mimetype="application/pdf")


@app.route("/download/<session_id>")
def download(session_id):
    path = os.path.join(UPLOAD_FOLDER, session_id, "dan-yap.pdf")
    if not os.path.exists(path):
        return "PDF not found", 404
    return send_file(path, as_attachment=True, download_name="dan-yap.pdf")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)