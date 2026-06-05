"""
file_extractor.py
Extracts heart disease patient data from uploaded PDF or image files
using Gemini AI vision capabilities.
"""
import io
import base64
import json
import re

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except ImportError:
        return ""
    except Exception as e:
        print(f"PDF text extraction error: {e}")
        return ""


def extract_images_from_pdf(file_bytes: bytes) -> list:
    """Extract first page of PDF as image (base64)."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        images = []
        for page_num in range(min(2, len(doc))):  # max 2 pages
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            images.append(base64.b64encode(img_bytes).decode("utf-8"))
        doc.close()
        return images
    except Exception as e:
        print(f"PDF to image error: {e}")
        return []


def image_to_base64(file_bytes: bytes, mime_type: str) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(file_bytes).decode("utf-8")


EXTRACTION_PROMPT = """You are a medical data extraction AI for a Heart Disease Prediction System.

Analyze this medical document/report/prescription/lab result and extract the following 13 heart disease parameters.
Return ONLY a valid JSON object with these exact keys and numeric values.
If a value is not found or unclear, use null.

Parameters to extract:
- age: patient age in years (integer, 29-77)
- sex: 1 for Male, 0 for Female
- cp: chest pain type (0=Typical Angina, 1=Atypical Angina, 2=Non-anginal pain, 3=Asymptomatic)
- trestbps: resting blood pressure in mmHg (integer, 94-200)
- chol: serum cholesterol in mg/dl (integer, 126-564)
- fbs: fasting blood sugar > 120 mg/dl (1=True, 0=False)
- restecg: resting ECG results (0=Normal, 1=ST-T abnormality, 2=Left ventricular hypertrophy)
- thalach: maximum heart rate achieved (integer, 71-202)
- exang: exercise induced angina (1=Yes, 0=No)
- oldpeak: ST depression induced by exercise (decimal, 0-6.2)
- slope: slope of peak exercise ST segment (0=Upsloping, 1=Flat, 2=Downsloping)
- ca: number of major vessels colored by fluoroscopy (0-3)
- thal: thalassemia (1=Fixed Defect, 2=Normal, 3=Reversible Defect)

Return ONLY this JSON format, nothing else:
{
  "age": <number or null>,
  "sex": <0 or 1 or null>,
  "cp": <0-3 or null>,
  "trestbps": <number or null>,
  "chol": <number or null>,
  "fbs": <0 or 1 or null>,
  "restecg": <0-2 or null>,
  "thalach": <number or null>,
  "exang": <0 or 1 or null>,
  "oldpeak": <number or null>,
  "slope": <0-2 or null>,
  "ca": <0-3 or null>,
  "thal": <1-3 or null>,
  "extracted_fields": <count of non-null fields>,
  "notes": "<brief note about what was found in the document>"
}"""


def extract_patient_data_with_gemini(file_bytes: bytes, mime_type: str, api_key: str) -> dict:
    """
    Use Gemini Vision to extract patient data from uploaded file.
    Supports both PDF and image files.
    """
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    parts = []

    if mime_type == "application/pdf":
        # For PDF: extract text + convert pages to images
        pdf_text = extract_text_from_pdf(file_bytes)
        
        if pdf_text:
            parts.append(f"Document text content:\n{pdf_text}\n\n")
        
        # Also send page images for visual context
        page_images = extract_images_from_pdf(file_bytes)
        for img_b64 in page_images:
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": img_b64
                }
            })
    else:
        # For images: send directly
        img_b64 = image_to_base64(file_bytes, mime_type)
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": img_b64
            }
        })

    parts.append(EXTRACTION_PROMPT)

    try:
        response = model.generate_content(parts)
        raw_text = response.text.strip()

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            data = json.loads(json_match.group())
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": "Could not parse extracted data", "raw": raw_text}

    except Exception as e:
        print(f"Gemini extraction error: {e}")
        return {"success": False, "error": str(e)}
