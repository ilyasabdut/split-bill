# 🧾 Bill Splitter with OCR & Shareable Links

This application is now split into a Streamlit frontend and a FastAPI backend, allowing users to upload a receipt image, automatically extracts items and amounts using AI (Google Gemini), and then facilitates splitting the bill among multiple people. Calculated splits can be saved and shared via a unique link.

## Features

*   **AI-Powered OCR:** Uses Google Gemini to extract details from receipt images.
*   **Decoupled Architecture:** Separate Streamlit frontend for UI and FastAPI backend for API logic.
*   **API Key Authentication:** Secure API endpoints with a simple bearer token API key.
*   **Step-by-Step UX:** Guides users through uploading, defining people, assigning items, and calculating the split.
*   **Item Assignment:** Flexible assignment of items to one or more people.
*   **Even Split Option:** Option to split the entire bill (after discounts, before tax/tip) evenly.
*   **Discount Handling:** Attempts to extract and apply overall bill discounts.
*   **Tax & Tip Adjustment:** Allows manual input or adjustment of tax and tip amounts.
*   **Persistent Shareable Links:** Saves split results and generates a unique link for sharing (stores images and metadata in MinIO).
*   **Idempotent Processing:** Prevents duplicate storage for identical split requests.
*   **Mobile-Friendly Design:** Aims for a good user experience on smaller screens.
*   **Dockerized Deployment:** Includes `Dockerfile`s and `docker-compose.yml` for easy deployment of both services.
*   **CI/CD Ready:** Example GitHub Actions workflow for automated build and deployment.

## Tech Stack

*   **Frontend:** Streamlit
*   **Backend API:** FastAPI, Uvicorn
*   **Backend AI:** Google Gemini API (for OCR and data extraction)
*   **Image Storage:** MinIO (or any S3-compatible object storage)
*   **Metadata Storage:** JSON files stored in MinIO
*   **Programming Language:** Python
*   **Containerization:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions (example provided)
*   **Build/Automation:** Makefile

## 📁 Project Structure

```
bill-splitter/
│
├── .github/
│   └── workflows/          # CI/CD configuration
│       └── ci-master.yml
│
├── app/
│   └── src/                # Frontend (Streamlit) source code
│       └── main.py
│
├── api/
│   └── src/                # Backend (FastAPI) source code
│       ├── __init__.py
│       ├── api.py
│       ├── gemini_ocr.py
│       ├── minio_utils.py
│       └── split_logic.py
│
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── .streamlit/             # Streamlit configuration
│   └── config.toml
├── Dockerfile              # Frontend Dockerfile (Streamlit app)
├── Dockerfile.api          # Backend Dockerfile (FastAPI API)
├── Makefile                # Build automation commands
├── docker-compose.yml      # Development docker-compose
├── docker-compose.prod.yml # Production docker-compose
└── README.md               # Documentation
```
## Setup and Installation

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (optional, but recommended for full setup)
- Google Gemini API key
- MinIO server access
- An API Key (a simple string secret for authenticating API requests)

### Quick Start (Local Development)

For convenience, this project utilizes `Makefile` commands to streamline common development tasks.

1.  **Clone & Setup**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    make install
    make check_dotenv
    ```

2.  **Configure Environment**
    - Copy `.env.example` to `.env` and edit with your credentials:
      ```bash
      cp .env.example .env
      nano .env  # or use your favorite editor
      ```
    - Update these values in `.env`:
        - `API_KEY`: Strong random string for API authentication
        - `GEMINI_API_KEY`: Your Google Gemini API key
        - MinIO credentialsn

    Example `.env` content:
    ```env
    APP_BASE_URL=http://localhost:8501
    FASTAPI_API_URL=http://localhost:8000
    API_KEY=your_secure_random_api_key_here  # IMPORTANT: Change this!
    GEMINI_API_KEY=your_gemini_api_key
    GEMINI_MODEL_NAME=gemini-1.5-flash
    MINIO_ENDPOINT=your_minio_ip:9000
    MINIO_ACCESS_KEY=your_minio_access_key
    MINIO_SECRET_KEY=your_minio_secret_key
    MINIO_BUCKET_NAME=split-bill
    MINIO_USE_SSL=False
    ```

3.  **Run the Applications**
    From the project root directory, open two separate terminal windows:

    *   **Terminal 1 (Backend API):**
        ```bash
        make run-api
        ```
        Starts FastAPI on `http://localhost:8000` (docs at `http://localhost:8000/docs`)

    *   **Terminal 2 (Frontend App):**
        ```bash
        make run-streamlit
        ```
        Starts Streamlit on `http://localhost:8501`

### Docker Deployment

#### Development
```bash
docker compose -f docker-compose.yml up --build
```

#### Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

Access the Streamlit app at `http://localhost:8501` and the FastAPI API docs at `http://localhost:8000/docs` (if exposed).

For detailed deployment guides and CI/CD setup, see our [Deployment Documentation](deployment.md).

## 📱 Usage Guide

### Authentication

To interact with the API directly (e.g., via `curl` or Swagger UI), you must provide the `API_KEY` as a Bearer token in the `Authorization` header: `Authorization: Bearer YOUR_API_KEY`.

### 1️⃣ Upload Receipt
1.  Select receipt image (JPG/PNG)
2.  Maximum size: 2MB
3.  AI will process automatically

### 2️⃣ Add Participants
1.  Type each person's name
2.  Click "➕ Add Person"
3.  Added names appear as tags
4.  Remove anyone with "➖"

### 3️⃣ Assign Items
1.  Choose splitting method:
    -   Even split (entire bill)
    -   Individual assignment
2.  If individual:
    -   Select people for each item
    -   Ensure all items are assigned

### 4️⃣ Finalize & Share
1.  Review detected tax amount
2.  Adjust tip if needed
3.  Click "🧮 Calculate Split & Get Link"
4.  Copy generated share link

### 5️⃣ View Results
1.  See per-person breakdown
2.  Check itemized details
3.  Share the link with others
4.  Start new split or adjust details

## 🗄️ MinIO Storage Setup

The application uses MinIO to store:
-   **Images**: `receipts/<split_id>.jpg`
-   **Metadata**: `metadata/<split_id>.json`

### Required Permissions
Ensure your MinIO bucket (`split-bill`) has these permissions:
-   `s3:PutObject`: Upload images/metadata
-   `s3:GetObject`: Retrieve shared data
-   `s3:BucketExists`: Check bucket status
-   `s3:MakeBucket`: Create if missing

## ❗ Troubleshooting

### API Key Issues
-   Ensure `API_KEY` is set in your `.env` file (for local development) or as an environment variable (for Docker deployment).
-   Verify the `Authorization: Bearer YOUR_API_KEY` header is correctly sent with requests.

### MinIO Issues
-   Check `MINIO_ENDPOINT` (use API port, e.g., `your-ip:9000`)
-   Verify credentials (`ACCESS_KEY`, `SECRET_KEY`)
-   Ensure correct bucket name and SSL setting
-   Check server accessibility

### API Problems
-   Validate `GEMINI_API_KEY`
-   Check API quotas in Google AI Studio
-   Verify model name if customized

### Share Links
-   Confirm correct `APP_BASE_URL`
-   Check VPS/domain configuration
-   Verify MinIO permissions

## 🔜 Future Plans

-   [ ] Edit extracted items
-   [ ] Item-specific discounts
-   [ ] User accounts
-   [ ] Payment integration
-   [ ] Multi-currency support

## 🤝 Contributing

We welcome contributions! Please:
1.  Fork the repository
2.  Create a feature branch
3.  Submit a Pull Request

For bugs or feature requests, open an Issue.
