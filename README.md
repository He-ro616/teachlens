# TeachLens - Lesson Analyzer

TeachLens is a web application that analyzes teacher lesson videos to provide insights into clarity, engagement, and other metrics. It generates a PDF report summarizing the analysis.

## Features

- Video upload and processing.
- Audio extraction and transcription using Whisper.
- Sentiment and linguistic analysis of the transcript.
- Generation of a downloadable PDF report with a rubric, summary, strengths, weaknesses, and suggestions.
- Stores reports in a SQLite database.

## Local Development

### Prerequisites

- Python 3.8+
- pip
- FFmpeg (ensure it's in your system's PATH)
- curl (for downloading the Whisper model)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/teachlens-render.git
    cd teachlens-render
    ```
2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    ./venv/Scripts/activate # On Windows
    # source venv/bin/activate # On macOS/Linux
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will be accessible at `http://127.0.0.1:5000/`. A `teachlens.db` file will be created in the root directory.

## Deployment on Render

This project is configured for easy deployment on [Render](https://render.com/).

### Prerequisites for Render Deployment

- A Render account.

### Deployment Steps

1.  **Fork this repository** to your GitHub account.
2.  **Create a new Web Service on Render:**
    *   Go to your Render Dashboard and click "New" -> "Web Service".
    *   Connect your GitHub repository.
    *   Configure the service with the following settings (these are largely covered by `render.yaml`):
        *   **Name:** `teachlens` (or your preferred name)
        *   **Environment:** `Python 3`
        *   **Region:** Choose a region close to your users.
        *   **Branch:** `main` (or your deployment branch)
        *   **Root Directory:** `/` (or your specific root if deployed as part of a monorepo)
        *   **Build Command:** `pip install -r requirements.txt`
        *   **Start Command:** `gunicorn app:app`
3.  **Deploy:**
    *   Click "Create Web Service". Render will automatically build and deploy your application.

### Important Notes for Render

-   **FFmpeg:** Render's default environment should have FFmpeg available. If you encounter issues related to FFmpeg not being found, you might need to create a custom Dockerfile to ensure it's correctly installed and in the PATH.
-   **Whisper Model Download:** The application is configured to download the `ggml-base.en.bin` Whisper model upon startup if it's not already present. This can take some time during the initial build or first deploy.
-   **Ephemeral Filesystem:** Render's filesystem is ephemeral, meaning any files written to disk (like temporary video or audio files) will be lost after the process restarts or moves. The current implementation uses temporary directories which are cleaned up after processing, aligning with this principle. The SQLite database will be reset on every deploy. For persistent storage, a managed database like PostgreSQL or a persistent disk is recommended.

## Project Structure

```
teachlens-render/
├── app.py                  # Main Flask application
├── analysis.py             # Text analysis logic
├── transcriber.py          # Audio transcription logic
├── pdf_generator.py        # PDF generation logic
├── models.py               # SQLAlchemy models for database interaction
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore file
├── render.yaml             # Render deployment configuration
├── README.md               # This file
├── models/
│   └── ggml-base.en.bin    # Downloaded Whisper model
└── templates/
    ├── index.html          # Frontend HTML
    └── static/
        ├── script.js       # Frontend JavaScript
        └── style.css       # Frontend CSS
```