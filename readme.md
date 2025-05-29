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

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-name>
Use code with caution.
2. Environment Variables
This application requires several environment variables to be set for API keys and service configurations.
Create a .env file in the root of the project (for local development) or directly on your server in the deployment directory (e.g., /home/ubuntu/composes/bill-splitter-app/.env). Do NOT commit your actual .env file to Git.
Use .env.example (you should create this file) as a template:
# .env.example - Copy to .env and fill in your actual values

# Google Gemini API Configuration
GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
GEMINI_MODEL_NAME="gemini-1.5-flash-latest" # Or your preferred Gemini model

# MinIO Object Storage Configuration
MINIO_ENDPOINT="your_minio_ip_or_domain:9000" # IMPORTANT: Use the API port (default 9000)
MINIO_ACCESS_KEY="YOUR_MINIO_ACCESS_KEY"
MINIO_SECRET_KEY="YOUR_MINIO_SECRET_KEY"
MINIO_BUCKET_NAME="split-bill" # The bucket must exist or be creatable by the keys
MINIO_USE_SSL="False" # Set to "True" if your MinIO endpoint uses HTTPS

# Application Configuration
APP_BASE_URL="http://localhost:8501" # For local dev. For deployment, use your public URL (e.g., http://your.vps.ip:8501)
Use code with caution.
Env
3. Local Development (using Python Virtual Environment)
This is useful for testing and development without Docker.
# Create a virtual environment (Python 3.12 recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure your .env file is in the project root and populated with your keys

# Run the Streamlit application
streamlit run main.py
Use code with caution.
Bash
The app should now be accessible at http://localhost:8501.
4. Dockerized Deployment (Recommended for VPS)
This guide assumes you have Docker and Docker Compose installed on your VPS.
Prepare Project on VPS:
Clone your Git repository to your VPS, for example, into /home/ubuntu/apps/bill-splitter-app.
Alternatively, your CI/CD pipeline will handle checking out the code.
Create Docker Compose Directory and Configuration on VPS:
It's good practice to have a separate directory for your Docker Compose setup if deploying multiple apps. Let's assume your CI/CD deploys to a directory like /home/ubuntu/deploy/bill-splitter-app where the docker-compose.yml and .env specific to this deployment will reside. The Dockerfile and app code context will be referenced from where the CI/CD checks out the code.
On your VPS, ensure the directory for compose files exists, e.g.:
mkdir -p /home/ubuntu/composes/bill-splitter-app
Your CI/CD will typically place the docker-compose.yml here or you can place it manually.
Crucially, create the .env file (as described in "Environment Variables" above) in this same directory (/home/ubuntu/composes/bill-splitter-app/.env) with your actual production credentials and URLs. This file is not in Git.
Build and Run with Docker Compose (typically handled by CI/CD):
If deploying manually or for the first time via CI/CD:
# On your VPS, in the directory with your project code (where Dockerfile is)
# cd /home/ubuntu/apps/bill-splitter-app 

# If building locally on VPS (less common if using CI/CD for builds)
# docker build -t your-registry/bill-splitter-app:latest .

# Then, in the directory with docker-compose.yml and .env
cd /home/ubuntu/composes/bill-splitter-app

# Login to your private registry (if image is private and not built locally)
# echo "YOUR_REGISTRY_PASSWORD" | docker login your-registry.com -u YOUR_USERNAME --password-stdin

# Pull the image (if built and pushed by CI/CD)
docker compose pull bill-splitter-app 

# Start the application
docker compose up -d bill-splitter-app # Add --build if building locally via compose
Use code with caution.
Bash
The application should now be accessible via your VPS IP/domain at the mapped port (e.g., http://your_vps_ip:8501).
5. CI/CD with GitHub Actions
An example GitHub Actions workflow (e.g., .github/workflows/deploy.yml) is provided in this repository (or you can adapt the one discussed). It typically handles:
Building the Docker image.
Pushing the image to a private Docker registry.
Connecting to the VPS and instructing Docker Compose to pull the new image and restart the service.
You will need to configure the following GitHub Secrets in your repository:
REGISTRY_USERNAME: Username for your Docker registry.
REGISTRY_PASSWORD: Password/token for your Docker registry.
VPS_HOST: IP address or hostname of your VPS.
VPS_USER: SSH username for your VPS.
VPS_SSH_KEY: SSH private key to access your VPS.
(Optional) TAILSCALE_AUTHKEY (if using Tailscale for SSH access from Actions runner).
And ensure the deployment script within the GitHub Action correctly:
Navigates to the directory on your VPS where the docker-compose.yml and .env for this app are located (e.g., /home/ubuntu/composes/bill-splitter-app).
Uses the correct service name from your docker-compose.yml (e.g., bill-splitter-app).
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
