from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
from PIL import Image
import os
import uuid
from pypdf import PdfWriter
from io import BytesIO
import pikepdf
from PIL import Image as PILImage
from pikepdf import PdfImage

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB
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
        save_path = os.path.join(session_folder, f"{i}.jpg")
        file.save(save_path)

        try:
            im = Image.open(save_path)
            if im.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                im = im.convert("RGBA")
                background.paste(im, mask=im.split()[-1])
                im = background
            else:
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


@app.route("/merge-pdf", methods=["POST"])
def merge_pdf():
    cleanup_old_sessions()

    files = request.files.getlist("pdffiles")

    if not files or len(files) < 2:
        return jsonify({"error": "Please upload at least 2 PDF files to merge"}), 400

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": f"'{file.filename}' is not a PDF file"}), 400

    session_id = str(uuid.uuid4())
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)

    try:
        writer = PdfWriter()

        for file in files:
            temp_path = os.path.join(session_folder, file.filename)
            file.save(temp_path)
            writer.append(temp_path)

        output_path = os.path.join(session_folder, "dan-yap.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
        writer.close()

    except Exception as e:
        return jsonify({"error": f"Failed to merge PDFs: {e}"}), 500

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


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({"error": "The total file size more than 20MB limit. Try reducing the number or size of the photos."}), 413


@app.route("/compress-upload", methods=["POST"])
def compress_upload():
    cleanup_old_sessions()

    file = request.files.get("pdffile")
    if not file or file.filename == "":
        return jsonify({"error": "No PDF file has been uploaded"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only .pdf files are supported"}), 400

    session_id = str(uuid.uuid4())
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)

    original_path = os.path.join(session_folder, "dan-yap.pdf")
    file.save(original_path)

    return jsonify({"session_id": session_id})

    
@app.route("/compress/<session_id>")
def compress(session_id):
    original_path = os.path.join(UPLOAD_FOLDER, session_id, "dan-yap.pdf")

    if not os.path.exists(original_path):
        return jsonify({"error": "PDF not found"}), 404

    compressed_path = os.path.join(os.path.dirname(original_path), "compressed.pdf")

    try:
        pdf = pikepdf.open(original_path)

        for page in pdf.pages:
            for image_key in list(page.images.keys()):
                raw_image = page.images[image_key]
                try:
                    pdf_image = PdfImage(raw_image)
                    pil_image = pdf_image.as_pil_image()
                    if pil_image.mode != "RGB":
                        pil_image = pil_image.convert("RGB")

                    buffer = BytesIO()
                    pil_image.save(buffer, format="JPEG", quality=50, optimize=True)
                    buffer.seek(0)

                    raw_image.write(buffer.read(), filter=pikepdf.Name("/DCTDecode"))
                except Exception as img_err:
                    print(f"Skip compressing one image: {img_err}")
                    continue

        pdf.save(compressed_path, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
        pdf.close()

    except Exception as e:
        return jsonify({"error": f"Compression failed: {e}"}), 500

    original_size = os.path.getsize(original_path)
    compressed_size = os.path.getsize(compressed_path)

    return jsonify({
        "session_id": session_id,
        "original_size": original_size,
        "compressed_size": compressed_size
    })


@app.route("/download-compressed/<session_id>")
def download_compressed(session_id):
    path = os.path.join(UPLOAD_FOLDER, session_id, "compressed.pdf")
    if not os.path.exists(path):
        return "Compressed PDF not found", 404
    return send_file(path, as_attachment=True, download_name="compressed.pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)