# Health_app_version_n8n

<img width="1177" height="978" alt="image" src="https://github.com/user-attachments/assets/7e0c9004-7ed6-4ada-9414-34dff0bd4af8" />

🧪 Lab Report Buddy — Backend + Automation Pipeline

A fully automated system to upload lab reports, extract values, store them, generate medical summaries using AI, and send results directly to users on WhatsApp.

🚀 Overview

Lab Report Buddy is a backend-driven automation pipeline that:

Accepts image/PDF lab reports from the frontend

Uploads the file to AWS S3

Extracts lab values using Azure Form Recognizer (OCR)

Parses tables → turns them into clean key–value medical data

Stores everything in MongoDB

Triggers an n8n workflow

n8n sends data to DeepSeek/OpenAI for medical summary

n8n sends report summary + image via WhatsApp Cloud API

The system is modular, clean, and production-oriented.

📁 Project Structure
lab-backend/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/
│   │     └── report_routes.py
│   ├── services/
│   │     ├── azure_ocr.py
│   │     ├── s3_upload.py
│   │     ├── db_service.py
│   │     └── n8n_trigger.py
│   ├── models/
│   │     └── report_model.py
│   └── utils/
│
├── .env
├── requirements.txt
└── README.md

⚙️ Features
🔹 1. Upload Lab Reports

Uploads via /report/upload

Accepts .jpg, .png, .pdf

Handles multipart form-data

🔹 2. AWS S3 Storage

Files stored in public-read S3 bucket

Auto-generated URLs returned

🔹 3. Azure OCR (Form Recognizer)

Uses prebuilt-document model

Extracts:

Tables

Key-value pairs

Full text

Report dates

Converts tables → clean dict format usable by AI

🔹 4. MongoDB Storage

Stores:

{
  "user_id": "...",
  "phone_number": "+91xxxx",
  "image_url": "s3-link",
  "key_value_data": { ... },
  "full_text": "...",
  "tables_raw": [...],
  "raw_ocr": {...}
}

🔹 5. n8n Automation

After saving the report:

FastAPI → n8n Webhook → DeepSeek AI → WhatsApp Cloud API

🔹 6. WhatsApp Delivery

User gets:

Their lab report image

AI-generated summary

Super clean UX.

🔌 Environment Variables (.env)
MONGO_URI=mongodb+srv://...
MONGO_DB=labapp
MONGO_COLLECTION=reports

AZURE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_KEY=your-azure-key

AWS_ACCESS_KEY_ID=xxxx
AWS_SECRET_ACCESS_KEY=xxxx
AWS_REGION=ap-south-1
S3_BUCKET_NAME=lab-reports-piyush

N8N_WEBHOOK_URL=https://your-n8n-domain.n8n.cloud/webhook/lab-summary

🧠 Azure OCR Pipeline

The backend uses a refined OCR extraction pipeline:

Polls Azure for results

Extracts text paragraphs

Extracts tables into grids

Converts first table → key-value pairs

Extracts report date using:

key-value pairs

regex fallback

Returns consolidated data:

{
  "raw_ocr": {...},
  "full_text": "...",
  "tables_raw": [...],
  "key_value_data": {...},
  "report_date": "..."
}

🗄️ MongoDB Document Example
{
  "_id": "66a8df9...",
  "user_id": "uid123",
  "phone_number": "+91999...",
  "image_url": "https://s3.amazonaws.com/....png",
  "key_value_data": {
    "hb": "12.4",
    "wbc": "7280",
    "platelet_count": "281000",
    ...
  },
  "report_date": "22/03/2025",
  "full_text": "complete extracted text...",
  "tables_raw": [...],
  "raw_ocr": {...}
}

🌐 n8n Workflow
Incoming Payload from FastAPI:
{
  "user_id": "uid123",
  "phone_number": "+91xxxx",
  "key_value_data": { ... },
  "report_date": "22/03/2025",
  "image_url": "https://s3..."
}

Workflow:

Webhook Trigger

DeepSeek / OpenAI Summary Node

WhatsApp Cloud API — Image message

WhatsApp body (in HTTP request):

{
  "messaging_product": "whatsapp",
  "to": "{{ $json.phone_number }}",
  "type": "image",
  "image": {
    "link": "{{ $json.image_url }}",
    "caption": "{{ $json.summary }}"
  }
}

▶️ Run the Backend

In project root:

uvicorn app.main:app --reload --port 8000


Swagger UI:

http://127.0.0.1:8000/docs

🧪 Testing the Upload API

Example using cURL:

curl -X POST "http://127.0.0.1:8000/report/upload" \
  -F "file=@report.jpg" \
  -F "user_id=uid123" \
  -F "phone_number=+91xxxxxx"

🧱 Tech Stack
Layer	Tech
Backend	FastAPI
OCR	Azure Form Recognizer
Storage	AWS S3
Database	MongoDB
Automation	n8n Cloud
AI Summary	DeepSeek/OpenAI
Messaging	WhatsApp Cloud API
📌 Future Enhancements

User authentication via Firebase

Dashboard to view past reports

Trends analysis (CBC charts, CRP over time)

Auto-PDF generation

Multi-language summaries

🧑‍💻 Author

Built with ❤️ and sheer stubbornness by Piyush.

<img width="1563" height="555" alt="image" src="https://github.com/user-attachments/assets/1131432d-edee-4071-81ac-24099c64bfe4" />
