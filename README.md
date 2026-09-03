# PDF Tools

**v1.6** A simple web toolkit for converting, merging, and compressing PDFs (bundle multiple photos into a single PDF, merge existing PDFs together, and shrink file sizes when needed).

Live demo: https://calicocalpico.pythonanywhere.com

## Features

### Image to PDF
- **Drag & drop or click to upload** multiple JPG/JPEG/PNG images at once.
- **Reorder by drag-and-drop** the filmstrip shows numbered frames; drag a frame to change its position in the final PDF.
- **Automatic orientation detection** each photo's page orientation (portrait/landscape) is detected from its actual width/height on upload, with a manual toggle button to override per photo.
- **Delete individual photos** before converting.
- **Transparent PNGs** are automatically flattened onto a white background.
- **20MB total upload limit**, enforced on both frontend and backend.

### Merge PDF
- Upload two or more existing PDF files and combine them into a single PDF, in the order selected.

### Compress PDF
- Available from the preview panel after any conversion or merge.
- Re-encodes embedded images at a lower quality to shrink file size, showing a before/after size comparison.

### Preview & Download
- The generated PDF is shown inline (desktop) with an "Open in new tab" fallback for mobile browsers that don't render PDFs inside an iframe.
- Separate download links for the original and compressed versions.

### Housekeeping
- **Auto-cleanup** session folders older than 1 hour are automatically deleted on each new conversion, keeping disk usage in check.

### Interface
- **Feature menu** on load lets users pick between Image-to-PDF and Merge PDF, instead of showing both tools at once.
- **Loading spinners** on action buttons during conversion, merging, and compression.
- **English/Indonesian language toggle**, remembered across visits.
- **Light/dark mode toggle**, remembered across visits.

## Tech Stack

- [Flask](https://flask.palletsprojects.com/) — web server
- [fpdf](https://pyfpdf.readthedocs.io/) — PDF generation from images
- [Pillow (PIL)](https://python-pillow.org/) — image processing
- [pypdf](https://pypdf.readthedocs.io/) — merging PDFs
- [pikepdf](https://pikepdf.readthedocs.io/) — PDF compression (image re-encoding)
- [Gunicorn](https://gunicorn.org/) — production WSGI server
- Vanilla HTML/CSS/JS on the frontend (no framework)

## Project Structure

```
app.py                  # Flask app: upload, convert, merge, compress, preview, download routes
templates/
  index.html             # Upload UI, filmstrip, merge dropzone, preview panel
requirements.txt         # Python dependencies
Procfile                 # Process command for platform deploys (gunicorn app:app)
uploads/                 # Generated per-session folders (gitignored, auto-cleaned)
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

**Image to PDF:** select or drag in JPG/PNG images, reorder and set orientation as needed, then click **Bind into PDF**. The backend normalizes each image (flattening transparency, converting to RGB) and builds a PDF page-by-page.

**Merge PDF:** select two or more PDF files, click **Merge PDFs** pages are combined in the order the files were added.

**Compress PDF:** after any conversion or merge, click **Compress PDF** in the preview panel to re-encode embedded images at reduced quality and see the size savings.

## Deployment

Currently deployed on [PythonAnywhere](https://www.pythonanywhere.com) (free tier) using a manual WSGI configuration pointing at `app.py`.

To deploy your own copy:

1. Push this repo to GitHub.
2. On PythonAnywhere: clone the repo via a Bash console, then `pip install --user -r requirements.txt`.
3. Create a new **Web app** with **Manual configuration**, and point the WSGI file to import `app` from this project.
4. Reload the web app after every code change (`git pull` + Reload button).

Free-tier PythonAnywhere sites need a login + "Run until..." click roughly once a month to stay active.

## Notes

- Uploaded files and generated PDFs are stored per-session under `uploads/<uuid>/` and auto-deleted after 1 hour.
- Mobile browsers often can't render a PDF inside an `<iframe>`; the "Open in new tab" button is a fallback, though some mobile browsers will auto-download instead of previewing.
- Compression works by re-encoding embedded JPEG images at lower quality, it's most effective on image-heavy PDFs and has little effect on text-only documents.

## Changelog

### v1.6
- Added a feature menu on load, separating Image-to-PDF and Merge PDF into distinct entry points
- Added standalone Compress PDF feature (upload any existing PDF to compress directly)
- Added loading spinners on action buttons
- Added English/Indonesian language toggle
- Added light/dark mode toggle
- Fixed mobile layout: language and theme toggles no longer overlap the header

### v1.5
- Added PNG upload support (with transparency flattening)
- Added Merge PDF feature (combine multiple PDFs into one)
- Added Compress PDF feature (reduce file size via image re-encoding)
- Added auto-cleanup for session folders older than 1 hour
- Added 20MB total upload limit

### v1.0
- Initial release: JPG to PDF conversion with drag-and-drop reordering, per-photo orientation control, and inline PDF preview before download
