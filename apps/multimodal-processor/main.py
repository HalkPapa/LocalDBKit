"""
Multimodal Processor API
FastAPI service for processing images, PDFs, audio, and video
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

from config import get_settings
from processors.ocr_processor import OCRProcessor
from processors.pdf_processor import PDFProcessor
# from processors.audio_processor import AudioProcessor
# from processors.video_processor import VideoProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Initialize FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
ocr_processor = OCRProcessor(lang=settings.tesseract_lang)
pdf_processor = PDFProcessor()
# audio_processor = AudioProcessor(model_size=settings.whisper_model)
# video_processor = VideoProcessor()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


# OCR Endpoints
@app.post(f"{settings.api_prefix}/ocr/extract")
async def extract_text_from_image(
    file: UploadFile = File(...),
    with_boxes: bool = False,
):
    """
    Extract text from image using OCR

    Args:
        file: Image file (PNG, JPEG, etc.)
        with_boxes: Include bounding box information
    """
    try:
        # Validate file size
        content = await file.read()
        if len(content) > settings.max_image_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_image_size} bytes",
            )

        # Process image
        if with_boxes:
            result = await ocr_processor.process_image_with_boxes(content)
        else:
            result = await ocr_processor.process_image(content)

        return result

    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# PDF Endpoints
@app.post(f"{settings.api_prefix}/pdf/extract")
async def extract_from_pdf(file: UploadFile = File(...)):
    """
    Extract text and metadata from PDF

    Args:
        file: PDF file
    """
    try:
        # Validate file size
        content = await file.read()
        if len(content) > settings.max_pdf_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_pdf_size} bytes",
            )

        # Process PDF
        result = await pdf_processor.process_pdf(content)
        return result

    except Exception as e:
        logger.error(f"PDF processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{settings.api_prefix}/pdf/images")
async def extract_images_from_pdf(file: UploadFile = File(...)):
    """
    Extract images from PDF

    Args:
        file: PDF file
    """
    try:
        content = await file.read()
        if len(content) > settings.max_pdf_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_pdf_size} bytes",
            )

        result = await pdf_processor.extract_images(content)
        return result

    except Exception as e:
        logger.error(f"PDF image extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{settings.api_prefix}/pdf/tables")
async def extract_tables_from_pdf(file: UploadFile = File(...)):
    """
    Extract tables from PDF

    Args:
        file: PDF file
    """
    try:
        content = await file.read()
        if len(content) > settings.max_pdf_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_pdf_size} bytes",
            )

        result = await pdf_processor.extract_tables(content)
        return result

    except Exception as e:
        logger.error(f"PDF table extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Audio Endpoints (Coming Soon)
@app.post(f"{settings.api_prefix}/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    with_timestamps: bool = False,
):
    """
    Transcribe audio to text using Whisper

    Note: Audio processing features coming soon in next release
    """
    return {
        "status": "coming_soon",
        "message": "Audio transcription will be available in the next release"
    }


@app.post(f"{settings.api_prefix}/audio/detect-language")
async def detect_audio_language(file: UploadFile = File(...)):
    """
    Detect language of audio

    Note: Audio processing features coming soon in next release
    """
    return {
        "status": "coming_soon",
        "message": "Language detection will be available in the next release"
    }


# Video Endpoints (Coming Soon)
@app.post(f"{settings.api_prefix}/video/metadata")
async def extract_video_metadata(file: UploadFile = File(...)):
    """
    Extract metadata from video

    Note: Video processing features coming soon in next release
    """
    return {
        "status": "coming_soon",
        "message": "Video metadata extraction will be available in the next release"
    }


@app.post(f"{settings.api_prefix}/video/frames")
async def extract_video_frames(
    file: UploadFile = File(...), num_frames: int = 10
):
    """
    Extract frames from video

    Note: Video processing features coming soon in next release
    """
    return {
        "status": "coming_soon",
        "message": "Frame extraction will be available in the next release"
    }


@app.post(f"{settings.api_prefix}/video/audio")
async def extract_video_audio(file: UploadFile = File(...)):
    """
    Extract audio from video

    Note: Video processing features coming soon in next release
    """
    return {
        "status": "coming_soon",
        "message": "Audio extraction from video will be available in the next release"
    }


@app.post(f"{settings.api_prefix}/video/scenes")
async def detect_video_scenes(
    file: UploadFile = File(...), threshold: float = 30.0
):
    """
    Detect scene changes in video

    Note: Video processing features coming soon in next release
    """
    return {
        "status": "coming_soon",
        "message": "Scene detection will be available in the next release"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
