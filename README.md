# JPG to PDF Converter

A simple web app that bundles multiple photos into a single PDF. Arrange the page order, set each photo's orientation, preview the result, then download.

Live demo: https://calicocalpico.pythonanywhere.com

## Features

- **Drag & drop or click to upload** multiple JPG/JPEG images at once.
- **Reorder by drag-and-drop** the filmstrip shows numbered frames; drag a frame to change its position in the final PDF.
- **Automatic orientation detection** each photo's page orientation (portrait/landscape) is detected from its actual width/height on upload, with a manual toggle button to override per photo.
- **Delete individual photos** before converting.
- **Preview before download** the generated PDF is shown inline (desktop) with a "Open in new tab" fallback for mobile browsers that don't render PDFs inside an iframe.
- Responsive light-table / film-strip themed UI.

## Tech Stack

- [Flask](https://flask.palletsprojects.com/) — web server
- [fpdf](https://pyfpdf.readthedocs.io/) — PDF generation
- [Pillow (PIL)](https://python-pillow.org/) — image processing
- [Gunicorn](https://gunicorn.org/) — production WSGI server
- Vanilla HTML/CSS/JS on the frontend (no framework)

## Project Structure

```
app.py                  # Flask app: upload, convert, preview, download routes
templates/
  index.html             # Upload UI, filmstrip, preview panel
requirements.txt         # Python dependencies
Procfile                 # Process command for platform deploys (gunicorn app:app)
uploads/                 # Generated per-session folders (images + hasil.pdf) — gitignored in practice
```

## Getting Started

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the development server:

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## How It Works

1. Select or drag in one or more JPG/JPEG images.
2. Reorder them by dragging frames in the filmstrip; toggle each frame's orientation if the auto-detected one isn't right.
3. Click **Preview PDF** the backend saves the images, rotates/normalizes them, and builds a PDF page-by-page matching each photo's chosen orientation.
4. The PDF opens in an inline preview with **Download PDF**, **Open in new tab** and **Arrange** options.

## Deployment

Currently deployed on [PythonAnywhere](https://www.pythonanywhere.com) (free tier) using a manual WSGI configuration pointing at `app.py`.

To deploy your own copy:

1. Push this repo to GitHub.
2. On PythonAnywhere: clone the repo via a Bash console, then `pip install --user -r requirements.txt`.
3. Create a new **Web app** with **Manual configuration**, and point the WSGI file to import `app` from this project.
4. Reload the web app after every code change (`git pull` + Reload button).

Free-tier PythonAnywhere sites need a login + "Run until..." click roughly once a month to stay active.

## Notes

- Uploaded images and generated PDFs are stored per-session under `uploads/<uuid>/` on the server. These are automatically cleaned up clear the folder after 1 hour occasionally if disk usage grows.
- Mobile browsers often can't render a PDF inside an `<iframe>`; the "Open in new tab" button is a fallback, though some mobile browsers will auto-download instead of previewing.
