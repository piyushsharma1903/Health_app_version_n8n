from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.s3_upload import upload_image_to_s3
from app.services.azure_ocr import extract_useful_data
from app.services.db_service import save_report
from app.services.n8n_trigger import send_to_n8n    # NEW IMPORT

router = APIRouter(prefix="/report", tags=["Lab Reports"])


@router.post("/upload")
async def upload_lab_report(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    phone_number: str = Form(...)
):
    # -------------------------------
    # Step 1: Read file
    # -------------------------------
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # -------------------------------
    # Step 2: Upload to S3
    # -------------------------------
    image_url = upload_image_to_s3(image_bytes, file.content_type)

    # -------------------------------
    # Step 3: Azure OCR
    # -------------------------------
    ocr_processed = await extract_useful_data(image_bytes)

    key_value_data = ocr_processed["key_value_data"]
    report_date = ocr_processed["report_date"]

    # -------------------------------
    # Step 4: Save to MongoDB
    # -------------------------------
    report_document = {
        "user_id": user_id,
        "phone_number": phone_number,
        "image_url": image_url,
        "report_date": report_date,
        "key_value_data": key_value_data,
        "full_text": ocr_processed["full_text"],
        "tables_raw": ocr_processed["tables_raw"],
        "raw_ocr": ocr_processed["raw_ocr"]
    }

    mongo_id = save_report(report_document)

    # -------------------------------
    # ⭐ STEP 5: SEND TO n8n ⭐
    # -------------------------------
    await send_to_n8n({
        "user_id": user_id,
        "phone_number": phone_number,
        "key_value_data": key_value_data,
        "report_date": report_date,
        "image_url": image_url
    })

    # -------------------------------
    # Step 6: Response back to frontend
    # -------------------------------
    return {
        "status": "success",
        "message": "Lab report uploaded and processed",
        "mongo_id": mongo_id,
        "image_url": image_url,
        "key_value_data": key_value_data,
        "report_date": report_date
    }
