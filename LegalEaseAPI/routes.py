from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import GeminiDocumentGenerator


router = APIRouter()


# =========================================================
# GEMINI SERVICE
# =========================================================

try:
    gemini_generator = GeminiDocumentGenerator()
    GEMINI_READY = True
    GEMINI_ERROR = None

except Exception as e:
    gemini_generator = None
    GEMINI_READY = False
    GEMINI_ERROR = str(e)


# =========================================================
# REQUEST MODEL
# =========================================================

class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=3000
    )

    terms: str = Field(
        default="",
        max_length=10000
    )

    dates: str = Field(
        default="",
        max_length=1000
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates"
    )
    @classmethod
    def clean_text(cls, value: str) -> str:

        return value.strip()


# =========================================================
# RESPONSE MODEL
# =========================================================

class DocumentResponse(BaseModel):

    document: str
    model: str
    status: str


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "LegalEase API",
        "gemini": (
            "ready"
            if GEMINI_READY
            else "not_ready"
        ),
        "model": (
            gemini_generator.model_name
            if gemini_generator
            else None
        )
    }


# =========================================================
# GENERATE DOCUMENT
# =========================================================

@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK
)
def generate_legal_document(
    request: DocumentRequest
):

    if not gemini_generator:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Gemini service is not available. "
                "Please check GEMINI_API_KEY configuration."
            )
        )

    if not request.document_type:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document type is required."
        )

    if not request.parties:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parties involved are required."
        )

    try:

        generated_text = (
            gemini_generator.generate_document(
                document_type=request.document_type,
                parties=request.parties,
                terms=request.terms,
                dates=request.dates
            )
        )

        if not generated_text:

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini returned an empty document."
            )

        return DocumentResponse(
            document=generated_text,
            model=gemini_generator.model_name,
            status="success"
        )

    except HTTPException:
        raise

    except Exception as error:

        error_message = str(error)

        # Keep the actual Gemini error visible to the frontend
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Gemini document generation failed. "
                f"Details: {error_message}"
            )
        )