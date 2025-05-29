# 🧾 Bill Splitter with OCR & Shareable Links

This Streamlit application allows users to upload a receipt image, automatically extracts items and amounts using AI (Google Gemini), and then facilitates splitting the bill among multiple people. Calculated splits can be saved and shared via a unique link.

## Features

*   **AI-Powered OCR:** Uses Google Gemini to extract details from receipt images.
*   **Step-by-Step UX:** Guides users through uploading, defining people, assigning items, and calculating the split.
*   **Item Assignment:** Flexible assignment of items to one or more people.
*   **Even Split Option:** Option to split the entire bill (after discounts, before tax/tip) evenly.
*   **Discount Handling:** Attempts to extract and apply overall bill discounts.
*   **Tax & Tip Adjustment:** Allows manual input or adjustment of tax and tip amounts.
*   **Persistent Shareable Links:** Saves split results and generates a unique link for sharing (stores images and metadata in MinIO).
*   **Idempotent Processing:** Prevents duplicate storage for identical split requests.
*   **Mobile-Friendly Design:** Aims for a good user experience on smaller screens.
*   **Dockerized Deployment:** Includes `Dockerfile` and `docker-compose.yml` for easy deployment.
*   **CI/CD Ready:** Example GitHub Actions workflow for automated build and deployment.

## Tech Stack

*   **Frontend:** Streamlit
*   **Backend AI:** Google Gemini API (for OCR and data extraction)
*   **Image Storage:** MinIO (or any S3-compatible object storage)
*   **Metadata Storage:** JSON files stored in MinIO
*   **Programming Language:** Python
*   **Containerization:** Docker, Docker Compose
*   **CI/CD:** GitHub Actions (example provided)

## 📁 Project Structure

```
bill-splitter/
│
├── .github/
│   └── workflows/    # CI/CD configuration
│
├── src/
│   ├── main.py      # Main Streamlit application
│   ├── gemini_ocr.py# AI integration logic
│   ├── minio_utils.py# Storage utilities
│   └── split_logic.py# Bill splitting core logic
│
├── .env.example     # Environment template
├── Dockerfile       # Container definition
├── docker-compose.yml# Service orchestration
├── requirements.txt # Python dependencies
└── README.md       # Documentation
```
## Setup and Installation

### Prerequisites

*   Python 3.10+ (Python 3.12 used in development)
*   Docker & Docker Compose (for containerized deployment)
*   Access to a Google Gemini API Key
*   Access to a MinIO server (or other S3-compatible storage) and its credentials
*   A registered domain or IP address for your VPS (for `APP_BASE_URL` in production)

## 🚀 Setup and Installation

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (optional)
- Google Gemini API key
- MinIO server access

### Quick Start

1. **Clone & Setup**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add your API keys and MinIO credentials:
     ```env
     GEMINI_API_KEY=your_key
     MINIO_ENDPOINT=your_minio:9000
     MINIO_ACCESS_KEY=your_access_key
     MINIO_SECRET_KEY=your_secret_key
     MINIO_BUCKET_NAME=split-bill
     MINIO_USE_SSL=False
     APP_BASE_URL=http://localhost:8501
     ```

3. **Run the App**
   ```bash
   streamlit run main.py
   ```

### Docker Deployment

```bash
docker compose up -d
```

Access the app at `http://localhost:8501` or your configured URL.

For detailed deployment guides and CI/CD setup, see our [Deployment Documentation](deployment.md).
Usage
Step 1: Upload Receipt
Click "Select a receipt image" and choose a JPG, JPEG, or PNG file (max 2MB, as per app setting).
The app will process the image.
Step 2: Who's Splitting?
Enter the name of a person and click "➕ Add Person".
Repeat for all people involved in the split. Names appear as "tags" and can be removed.
Click "Next: Assign Items ➡️".
Step 3: How to Split Items?
Option A: Split Evenly: Check the box "Split the entire bill... evenly". Individual item assignment will be skipped/disabled.
Option B: Assign Individually: For each item listed:
Select the person(s) who shared that item from the multiselect dropdown.
Ensure all items are assigned if not splitting evenly (the "Next" button will be disabled otherwise).
Click "Next: Tax & Tip ➡️".
Step 4: Tax, Tip & Calculate
Review/edit the automatically detected (or pre-filled) Tax and Tip amounts.
Click "🧮 Calculate Split & Get Link".
Step 5: Results & Share
View the calculated split per person and the itemized breakdown.
If a new split was successfully saved, a shareable link will be generated. Copy this link to share with others. They will see a read-only view of the split results.
Click "✨ Start New Split" to begin again or "⬅️ Adjust Split Details" to go back through the creation steps.
MinIO Bucket Setup
The application uses MinIO (or any S3-compatible storage) to store:
Receipt images under the prefix receipts/ (e.g., receipts/<split_id>.jpg)
JSON metadata for each split under the prefix metadata/ (e.g., metadata/<split_id>.json)
Ensure the bucket specified in MINIO_BUCKET_NAME (default: split-bill) exists in your MinIO server and that the provided access/secret keys have permissions to:
s3:PutObject (to upload images and metadata)
s3:GetObject (to retrieve images and metadata for shared links)
s3:BucketExists (or s3:ListBucket for the check in minio_utils.py)
s3:MakeBucket (if you want the application to attempt to create the bucket if it doesn't exist, as implemented in minio_utils.py)
Troubleshooting
MinIO Connection Errors: Double-check your MINIO_ENDPOINT (must be the API port, e.g., your-ip:9000), MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME, and MINIO_USE_SSL environment variables. Ensure MinIO is running and accessible from where the app is hosted.
Gemini API Errors: Verify your GEMINI_API_KEY and GEMINI_MODEL_NAME. Check the Google AI Studio for any API quotas or issues.
Share Links Not Working: Ensure APP_BASE_URL is correctly set to the public URL of your application.
Permissions: If deploying on a VPS, ensure the user running the Docker daemon/Streamlit process has necessary permissions to write to any local directories if used (though this app now primarily uses MinIO for persistence).
Future Enhancements (Ideas)
Option to edit extracted item details (name, quantity, price).
More sophisticated discount handling (item-specific discounts).
User accounts to save/manage multiple splits.
Direct payment integration (e.g., links to PayPal.me, Venmo).
Support for different currencies.
Dark mode / Theme options.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.
