import os
import io
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.config import settings, update_api_key, UPLOAD_DIR, SAMPLE_DIR
from app.sarvam_client import sarvam_client
from app.document_parser import document_parser
from app.knowledge_base import knowledge_base
from app.tender_analyzer import tender_analyzer
from app.eligibility_matcher import eligibility_matcher
from app.bid_generator import bid_generator

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Tender Document Analyzer & Bid Response Generator powered by Sarvam AI"
)

# Static and Templates
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# --- Pydantic Request Models ---
class ApiKeyUpdate(BaseModel):
    api_key: str
    model: Optional[str] = "sarvam-105b"

class AnalyzeTenderRequest(BaseModel):
    text: str
    filename: Optional[str] = "Tender_Document.pdf"

class EvaluateEligibilityRequest(BaseModel):
    tender_data: Dict[str, Any]

class GenerateBidRequest(BaseModel):
    tender_data: Dict[str, Any]
    tone: Optional[str] = "Formal Government Procurement"
    detail_level: Optional[str] = "Comprehensive"
    custom_instructions: Optional[str] = ""

class TranslateRequest(BaseModel):
    text: str
    target_language: str = "hi-IN"
    source_language: str = "en-IN"

class TTSRequest(BaseModel):
    text: str
    target_language: str = "hi-IN"
    speaker: str = "manisha"

# --- Web UI Route ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "sarvam_key_set": bool(settings.SARVAM_API_KEY)
        }
    )

# --- Status & Settings Endpoints ---
@app.get("/api/status")
async def get_status():
    has_key = bool(settings.SARVAM_API_KEY and settings.SARVAM_API_KEY.strip())
    masked_key = ""
    if has_key:
        k = settings.SARVAM_API_KEY.strip()
        masked_key = k[:6] + "..." + k[-4:] if len(k) > 10 else "***"
        
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "has_api_key": has_key,
        "masked_key": masked_key,
        "model": settings.SARVAM_CHAT_MODEL,
        "company": knowledge_base.get_company_profile().get("company_name"),
        "past_proposals_count": len(knowledge_base.get_past_proposals()),
        "team_size": len(knowledge_base.get_team_profiles())
    }

@app.post("/api/settings/sarvam")
async def set_sarvam_settings(data: ApiKeyUpdate):
    if data.api_key:
        update_api_key(data.api_key)
        sarvam_client.api_key = data.api_key.strip()
    if data.model:
        settings.SARVAM_CHAT_MODEL = data.model
        
    # Test key validity
    verification = sarvam_client.verify_key(data.api_key)
    return {
        "success": True,
        "message": "Settings updated successfully.",
        "verification": verification,
        "model": settings.SARVAM_CHAT_MODEL
    }

@app.get("/api/settings/verify")
async def verify_sarvam():
    return sarvam_client.verify_key()

# --- Sample Tenders Endpoints ---
@app.get("/api/sample-tenders")
async def list_sample_tenders():
    samples = []
    if SAMPLE_DIR.exists():
        for f in SAMPLE_DIR.glob("*.txt"):
            samples.append({
                "id": f.stem,
                "filename": f.name,
                "title": f.stem.replace("_", " ").title(),
                "size_kb": round(f.stat().st_size / 1024, 1)
            })
    return {"samples": samples}

@app.get("/api/sample-tenders/{sample_id}")
async def get_sample_tender(sample_id: str):
    file_path = SAMPLE_DIR / f"{sample_id}.txt"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample tender not found")
    
    parsed = document_parser.extract_text(file_path)
    return {
        "sample_id": sample_id,
        "filename": file_path.name,
        "text": parsed["text"],
        "metadata": parsed["metadata"]
    }

# --- Document Upload & Parsing ---
@app.post("/api/upload-tender")
async def upload_tender(file: UploadFile = File(...)):
    filename = file.filename
    clean_filename = f"{int(datetime.now().timestamp())}_{filename}"
    save_path = UPLOAD_DIR / clean_filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed = document_parser.extract_text(save_path)
        return {
            "success": True,
            "filename": filename,
            "saved_as": clean_filename,
            "text": parsed["text"],
            "metadata": parsed["metadata"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")

# --- Tender Analysis with Sarvam AI ---
@app.post("/api/analyze-tender")
async def analyze_tender(data: AnalyzeTenderRequest):
    if not data.text or len(data.text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Insufficient tender text for analysis (minimum 50 characters required).")
    
    try:
        analysis_result = tender_analyzer.analyze(data.text, data.filename or "Uploaded_Tender")
        return {
            "success": True,
            "analysis": analysis_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# --- Eligibility & Go/No-Go Match Engine ---
@app.post("/api/evaluate-eligibility")
async def evaluate_eligibility(data: EvaluateEligibilityRequest):
    try:
        evaluation = eligibility_matcher.evaluate_fit(data.tender_data)
        return {
            "success": True,
            "evaluation": evaluation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eligibility evaluation failed: {str(e)}")

# --- Bid Response Generation with Sarvam AI ---
@app.post("/api/generate-bid")
async def generate_bid(data: GenerateBidRequest):
    try:
        bid = bid_generator.generate_bid_response(
            tender_data=data.tender_data,
            tone=data.tone or "Formal Government Procurement",
            detail_level=data.detail_level or "Comprehensive",
            custom_instructions=data.custom_instructions or ""
        )
        return {
            "success": True,
            "bid": bid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bid generation failed: {str(e)}")

# --- DOCX Export ---
@app.post("/api/export-docx")
async def export_bid_docx(bid_data: Dict[str, Any]):
    try:
        docx_buffer = bid_generator.export_to_docx(bid_data)
        filename = f"Technical_Bid_Proposal_{bid_data.get('tender_id', 'NIT').replace('/', '_')}.docx"
        
        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX export failed: {str(e)}")

# --- Knowledge Base Endpoints ---
@app.get("/api/company-profile")
async def get_company_profile():
    return knowledge_base.get_company_profile()

@app.post("/api/company-profile")
async def update_company_profile(data: Dict[str, Any]):
    knowledge_base.save_company_profile(data)
    return {"success": True, "message": "Company profile updated successfully."}

@app.get("/api/past-proposals")
async def get_past_proposals():
    return {"proposals": knowledge_base.get_past_proposals()}

@app.post("/api/past-proposals")
async def add_past_proposal(proposal: Dict[str, Any]):
    knowledge_base.add_past_proposal(proposal)
    return {"success": True, "message": "Past proposal added successfully."}

@app.get("/api/team-profiles")
async def get_team_profiles():
    return {"team": knowledge_base.get_team_profiles()}

# --- Sarvam Indic Translation & TTS Audio Studio ---
@app.post("/api/translate")
async def translate_text(data: TranslateRequest):
    try:
        res = sarvam_client.translate(
            text=data.text,
            target_language_code=data.target_language,
            source_language_code=data.source_language
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/text-to-speech")
async def text_to_speech(data: TTSRequest):
    try:
        res = sarvam_client.text_to_speech(
            text=data.text,
            target_language_code=data.target_language,
            speaker=data.speaker
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
