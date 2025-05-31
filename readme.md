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
│       └── ci-master.yml
│
├── src/
│   ├── main.py      # Main Streamlit application
│   ├── gemini_ocr.py# AI integration logic
│   ├── minio_utils.py# Storage utilities
│   └── split_logic.py# Bill splitting core logic
│
├── .env.example     # Environment template
├── .gitignore       # Git ignore rules
├── Dockerfile       # Container definition
├── docker-compose.yml# Service orchestration
├── requirements.txt # Python dependencies
└── README.md        # Documentation
```
## Setup and Installation

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
   streamlit run src/main.py
   ```

### Docker Deployment

```bash
docker compose up -d
```

Access the app at `http://localhost:8501` or your configured URL.

For detailed deployment guides and CI/CD setup, see our [Deployment Documentation](deployment.md).

## 📱 Usage Guide

### 1️⃣ Upload Receipt
1. Select receipt image (JPG/PNG)
2. Maximum size: 2MB
3. AI will process automatically

### 2️⃣ Add Participants
1. Type each person's name
2. Click "➕ Add Person"
3. Added names appear as tags
4. Remove anyone with "➖"

### 3️⃣ Assign Items
1. Choose splitting method:
   - Even split (entire bill)
   - Individual assignment
2. If individual:
   - Select people for each item
   - Ensure all items are assigned

### 4️⃣ Finalize & Share
1. Review detected tax amount
2. Adjust tip if needed
3. Click "Calculate Split"
4. Copy generated share link

### 5️⃣ View Results
1. See per-person breakdown
2. Check itemized details
3. Share the link with others
4. Start new split or adjust details
## 🗄️ MinIO Storage Setup

The application uses MinIO to store:
- **Images**: `receipts/<split_id>.jpg`
- **Metadata**: `metadata/<split_id>.json`

### Required Permissions
Ensure your MinIO bucket (`split-bill`) has these permissions:
- `s3:PutObject`: Upload images/metadata
- `s3:GetObject`: Retrieve shared data
- `s3:BucketExists`: Check bucket status
- `s3:MakeBucket`: Create if missing
## ❗ Troubleshooting

### MinIO Issues
- Check `MINIO_ENDPOINT` (use API port, e.g., `your-ip:9000`)
- Verify credentials (`ACCESS_KEY`, `SECRET_KEY`)
- Ensure correct bucket name and SSL setting
- Check server accessibility

### API Problems
- Validate `GEMINI_API_KEY`
- Check API quotas in Google AI Studio
- Verify model name if customized

### Share Links
- Confirm correct `APP_BASE_URL`
- Check VPS/domain configuration
- Verify MinIO permissions

## 🔜 Future Plans

- [ ] Edit extracted items
- [ ] Item-specific discounts
- [ ] User accounts
- [ ] Payment integration
- [ ] Multi-currency support
- [ ] Dark mode theme

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

For bugs or feature requests, open an Issue.
