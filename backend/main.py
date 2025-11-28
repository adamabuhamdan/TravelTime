import os
import json
import time
from typing import List

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ===================== تحميل متغيرات البيئة =====================

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("الرجاء ضبط متغير البيئة GEMINI_API_KEY في ملف .env.")

WAVESPEED_API_KEY = os.environ.get("WAVESPEED_API_KEY")
if not WAVESPEED_API_KEY:
    raise RuntimeError("الرجاء ضبط متغير البيئة WAVESPEED_API_KEY في ملف .env.")

# ===================== إعداد Gemini =====================

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# ===================== إعداد WaveSpeed Qwen Image Edit =====================

WAVESPEED_JOB_URL = "https://api.wavespeed.ai/api/v3/wavespeed-ai/qwen-image/edit-plus"
WAVESPEED_RESULT_URL = "https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"

WAVESPEED_HEADERS_JSON = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {WAVESPEED_API_KEY}",
}

WAVESPEED_HEADERS_AUTH = {
    "Authorization": f"Bearer {WAVESPEED_API_KEY}",
}

# ===================== FastAPI App =====================

app = FastAPI(
    title="Artifact Analyzer API",
    description="تحليل صور القطع الأثرية باستخدام Gemini + توليد 3D عبر WaveSpeed/Qwen",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # عدّلها للإنتاج
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== Schemas =====================

class ArtifactResponse(BaseModel):
    arabic_definition: str
    image_prompt_3d: str


class WaveSpeedEditResponse(BaseModel):
    image_url: str


class Artifact3DPipelineWaveSpeedResponse(BaseModel):
    arabic_definition: str
    image_prompt_3d: str
    image_url: str


# ===================== SYSTEM PROMPT =====================

SYSTEM_PROMPT = """
You are an expert in archaeology and museum curation, specialized in describing ancient artifacts in Modern Standard Arabic, and in designing advanced image-generation prompts.

TASK:
You will receive an image of an archaeological artifact. Carefully analyze the image and then respond ONLY in JSON with the following fields:

{
  "arabic_definition": "...",
  "image_prompt_3d": "..."
}

====================
1) "arabic_definition" (Arabic)
====================
Write a detailed museum-style Arabic description explaining:
- What the artifact represents
- Possible cultural meaning or ritual purpose
- Historical period (if estimable)
- Material, craftsmanship, and visual characteristics
- Interpretation suitable for museum visitors or archaeology students
Avoid stating that you are an AI model.

====================
2) "image_prompt_3d" (English)
====================
Write a powerful image-generation prompt that produces a SINGLE composite 3D render containing:
- A main large 3/4 (three-quarter) view of the artifact
- Smaller inset frames showing:
    • front view
    • side profile view
    • rear view
- All views must appear in ONE combined image (museum-style composite layout)
- Emphasize:
    • realistic 3D modeling
    • physically accurate material (gypsum / stone / clay as shown)
    • cracks, erosion, aging marks
    • subtle soft lighting (museum or neutral studio)
    • clean pedestal under the main statue
    • depth, realism, and high-detail textures
- The tone: “high-end virtual museum render”, cohesive and elegant.

====================
IMPORTANT
====================
Return ONLY valid JSON. No markdown, no extra explanation.
"""


# ===================== Helpers =====================

def call_gemini_analyze(img_bytes: bytes, mime_type: str) -> ArtifactResponse:
    """استدعاء Gemini لتحليل الصورة وإرجاع الوصف + 3D prompt."""
    image_part = types.Part.from_bytes(
        data=img_bytes,
        mime_type=mime_type,
    )

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=[
            image_part,
            SYSTEM_PROMPT,
        ],
    )

    raw_text = response.text.strip()

    # احتياط لو رجّع ```json
    if raw_text.startswith("```"):
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1:
            raw_text = raw_text[start:end + 1]

    data = json.loads(raw_text)

    if "arabic_definition" not in data or "image_prompt_3d" not in data:
        raise HTTPException(
            status_code=500,
            detail="استجابة Gemini لا تحتوي على الحقول المطلوبة (arabic_definition, image_prompt_3d).",
        )

    return ArtifactResponse(
        arabic_definition=data["arabic_definition"],
        image_prompt_3d=data["image_prompt_3d"],
    )


def call_wavespeed_edit(image_url: str, prompt: str) -> str:
    """
    استدعاء WaveSpeed Qwen Image Edit:
    - يرسل URL للصورة + prompt
    - يعمل polling حتى تكتمل المهمة
    - يرجع URL للصورة الناتجة
    """
    payload = {
        "enable_base64_output": False,
        "enable_sync_mode": False,
        "images": [image_url],  # URL عام للصورة الأصلية
        "output_format": "jpeg",
        "prompt": prompt,
        "seed": -1,
    }

    begin = time.time()
    response = requests.post(
        WAVESPEED_JOB_URL,
        headers=WAVESPEED_HEADERS_JSON,
        data=json.dumps(payload),
        timeout=30,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"WaveSpeed job submit error: {response.text}",
        )

    result = response.json().get("data")
    if not result or "id" not in result:
        raise HTTPException(
            status_code=500,
            detail=f"WaveSpeed job response غير متوقع: {response.text}",
        )

    request_id = result["id"]

    # Poll for result
    result_url = WAVESPEED_RESULT_URL.format(request_id=request_id)

    while True:
        resp = requests.get(result_url, headers=WAVESPEED_HEADERS_AUTH, timeout=30)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"WaveSpeed polling error: {resp.text}",
            )

        data = resp.json().get("data", {})
        status = data.get("status")

        if status == "completed":
            outputs = data.get("outputs") or []
            if not outputs:
                raise HTTPException(
                    status_code=500,
                    detail="WaveSpeed: لم يتم العثور على outputs في النتيجة.",
                )
            # أول URL للصورة الناتجة
            out_url = outputs[0]
            return out_url

        if status == "failed":
            error_msg = data.get("error", "WaveSpeed: المهمة فشلت بدون تفاصيل.")
            raise HTTPException(status_code=500, detail=error_msg)

        # ما زال يعمل
        # لتفادي احتراق CPU، ننتظر قليلاً
        if time.time() - begin > 120:  # مهلة 120 ثانية
            raise HTTPException(
                status_code=504,
                detail="WaveSpeed: انتهت مهلة الانتظار قبل إكمال المهمة.",
            )

        time.sleep(0.2)


# ===================== Endpoints =====================

@app.get("/")
async def root():
    return {"message": "Artifact Analyzer API is running (Gemini + WaveSpeed)."}


# ---------- 1) تحليل الأثر عبر Gemini فقط ----------

@app.post("/analyze-artifact", response_model=ArtifactResponse)
async def analyze_artifact(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="الملف يجب أن يكون صورة (image/*).")

    try:
        img_bytes = await image.read()
        return call_gemini_analyze(img_bytes, image.content_type)
    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="تعذر قراءة استجابة Gemini كـ JSON. راجع response.text أو عدّل SYSTEM_PROMPT.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 2) Endpoint: استخدام WaveSpeed مباشرة (image_url + prompt جاهز) ----------

@app.post("/wavespeed-edit", response_model=WaveSpeedEditResponse)
async def wavespeed_edit(
    image_url: str = Form(...),
    prompt: str = Form(...),
):
    """
    يستخدم عندما يكون عندك:
    - image_url: رابط عام للصورة الأصلية (نفس صورة الأثر)
    - prompt: مثلاً الـ image_prompt_3d القادم من Gemini

    ويرجع URL للصورة الناتجة.
    """
    try:
        out_url = call_wavespeed_edit(image_url=image_url, prompt=prompt)
        return WaveSpeedEditResponse(image_url=out_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 3) Pipeline كامل: صورة ملف + image_url + Gemini + WaveSpeed ----------

@app.post("/artifact-3d-pipeline-wavespeed", response_model=Artifact3DPipelineWaveSpeedResponse)
async def artifact_3d_pipeline_wavespeed(
    image: UploadFile = File(...),
    image_url: str = Form(...),
):
    """
    Pipeline كامل:
    - يأخذ:
        * image: ملف صورة أثري (للتحليل عبر Gemini)
        * image_url: رابط عام لنفس الصورة (للاستخدام مع WaveSpeed)
    - 1) يحلل الصورة عبر Gemini -> arabic_definition + image_prompt_3d
    - 2) يولّد صورة 3D مركبة عبر WaveSpeed باستخدام image_url + prompt
    - يرجع الكل في استجابة واحدة.
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="الملف يجب أن يكون صورة (image/*).")

    try:
        img_bytes = await image.read()

        # 1) تحليل الصورة عبر Gemini
        artifact_info = call_gemini_analyze(img_bytes, image.content_type)

        # 2) توليد الصورة 3D عبر WaveSpeed باستخدام image_url ونفس الـ prompt
        out_url = call_wavespeed_edit(image_url=image_url, prompt=artifact_info.image_prompt_3d)

        return Artifact3DPipelineWaveSpeedResponse(
            arabic_definition=artifact_info.arabic_definition,
            image_prompt_3d=artifact_info.image_prompt_3d,
            image_url=out_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
