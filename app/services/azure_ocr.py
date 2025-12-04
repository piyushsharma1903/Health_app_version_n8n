import time
import asyncio
import httpx
import re
from app.config import settings


# ---------------------------------------------
# 1) CALL AZURE OCR (FORM RECOGNIZER v4)
# ---------------------------------------------
async def call_azure_ocr(image_bytes: bytes):
    url = f"{settings.AZURE_ENDPOINT}/formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"

    headers = {
        "Ocp-Apim-Subscription-Key": settings.AZURE_KEY,
        "Content-Type": "application/octet-stream"
    }

    # Step 1 → Submit OCR request
    async with httpx.AsyncClient(timeout=40.0) as client:
        response = await client.post(url, headers=headers, content=image_bytes)

    if response.status_code != 202:
        raise Exception(f"Azure OCR failed: {response.text}")

    # Step 2 → Poll the operation URL
    result_url = response.headers.get("operation-location")

    async with httpx.AsyncClient(timeout=40.0) as client:
        for _ in range(15):  
            await asyncio.sleep(1)
            result = await client.get(
                result_url,
                headers={"Ocp-Apim-Subscription-Key": settings.AZURE_KEY}
            )
            json_data = result.json()

            if json_data.get("status") == "succeeded":
                return json_data

        raise Exception("Azure OCR polling timed out")


# ---------------------------------------------
# 2) FULL TEXT EXTRACTION
# ---------------------------------------------
def extract_full_text(ocr_json):
    analyze_result = ocr_json.get("analyzeResult", {})

    # Best method → paragraphs
    paragraphs = analyze_result.get("paragraphs", [])
    if paragraphs:
        return "\n".join([p.get("content", "") for p in paragraphs]).strip()

    # Fallback → lines
    pages = analyze_result.get("pages", [])
    full_text = ""

    for page in pages:
        lines = page.get("lines", [])
        full_text += "\n".join([line.get("content", "") for line in lines]) + "\n"

    return full_text.strip()


# ---------------------------------------------
# 3) TABLE EXTRACTION (GRID FORMAT)
# ---------------------------------------------
def extract_tables(ocr_json):
    analyze_result = ocr_json.get("analyzeResult", {})
    tables = analyze_result.get("tables", [])

    parsed_tables = []

    for table in tables:
        rows = table.get("rowCount", 0)
        cols = table.get("columnCount", 0)
        cells = table.get("cells", [])

        # empty grid
        grid = [["" for _ in range(cols)] for _ in range(rows)]

        # fill grid
        for cell in cells:
            r = cell.get("rowIndex")
            c = cell.get("columnIndex")
            text = cell.get("content", "")
            grid[r][c] = text

        parsed_tables.append(grid)

    return parsed_tables


# ---------------------------------------------
# 4) CONVERT FIRST TABLE TO KEY-VALUE PAIRS
# ---------------------------------------------
def table_to_dict(parsed_tables):
    """
    Converts the first horizontal table to key → value dict
    Example:
    [ ["HB", "12.1"], ["WBC", "6.5"], ["Platelets", "250k"] ]
    """
    if not parsed_tables:
        return {}

    table = parsed_tables[0]
    data_dict = {}

    for row in table:
        if len(row) >= 2:  
            key = row[0].strip().replace(" ", "_").lower()
            value = row[1].strip()
            data_dict[key] = value

    return data_dict


# ---------------------------------------------
# 5) DATE EXTRACTION
# ---------------------------------------------
def extract_report_date(ocr_json, full_text):
    analyze_result = ocr_json.get("analyzeResult", {})

    # Try key-value pairs
    for kv in analyze_result.get("keyValuePairs", []):
        key = kv.get("key", {}).get("content", "").lower()
        val = kv.get("value", {}).get("content", "")
        if "date" in key and val:
            return val

    # Fallback → Regex from full text
    patterns = [
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
        r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            return match.group()

    return None


# ---------------------------------------------
# 6) MASTER FUNCTION → CLEAN PIPELINE
# ---------------------------------------------
async def extract_useful_data(image_bytes: bytes):
    """
    The only function you will call from routes.
    It performs:
        - Azure OCR
        - table extraction
        - convert to key=value pairs
        - date extraction
        - full text fallback
    """

    ocr_json = await call_azure_ocr(image_bytes)

    full_text = extract_full_text(ocr_json)
    tables = extract_tables(ocr_json)
    kv_dict = table_to_dict(tables)
    report_date = extract_report_date(ocr_json, full_text)

    return {
        "raw_ocr": ocr_json,
        "full_text": full_text,
        "tables_raw": tables,
        "key_value_data": kv_dict,     # ★ YOU WILL SAVE THIS IN MONGO
        "report_date": report_date
    }
