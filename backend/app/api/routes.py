
import logging
import tempfile

from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

from backend.app.generation.answer import AnswerService
from backend.app.ingestion.service import IngestionService
from backend.app.db.repository import (
    save_document,
    list_documents,
    get_document,
    delete_document,
    DuplicateDocumentError,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services once
answer_service = AnswerService()
ingestion_service = IngestionService()


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty.")

        return value

@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        return await answer_service.answer_question(
            question=request.question,
            top_k=request.top_k,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        logger.exception("Answer generation failed.")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer. Check server logs.",
        )


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        await file.close()
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            temp_path = Path(temp_file.name)
            total_size = 0
            first_bytes = b""

            while True:
                content = await file.read(1024 * 1024)

                if not content:
                    break

                total_size += len(content)

                if total_size > 20 * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the 20 MB upload limit.",
                    )

                if len(first_bytes) < 5:
                    first_bytes += content[:5 - len(first_bytes)]

                temp_file.write(content)

        # Validate PDF file signature
        if first_bytes != b"%PDF-":
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid PDF.",
            )

        # Extract text, create chunks and generate embeddings
        chunks = await run_in_threadpool(
            ingestion_service.process_pdf,
            temp_path,
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in the PDF.",
            )

        # Save document and chunks to PostgreSQL
        document_id = await run_in_threadpool(
            save_document,
            temp_path,
            chunks,
            original_filename=file.filename,
        )

        return {
            "message": "Document uploaded and processed successfully.",
            "document_id": document_id,
            "filename": file.filename,
            "chunks_saved": len(chunks),
            "status": "completed",
        }

    except DuplicateDocumentError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "This document has already been uploaded.",
                "existing_document_id": exc.document_id,
            },
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Document ingestion failed.")

        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Check server logs.",
        )

    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                logger.exception(
                    "Failed to remove temporary file: %s",
                    temp_path,
                )

        await file.close()


@router.get("/documents")
def get_documents():
    try:
        documents = list_documents()

        return {
            "total": len(documents),
            "documents": documents,
        }

    except Exception:
        logger.exception("Failed to retrieve documents.")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve documents.",
        )


@router.get("/documents/{document_id}")
def get_document_details(document_id: int):
    try:
        document = get_document(document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return document

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to retrieve document details.")

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document details.",
        )


@router.delete("/documents/{document_id}")
def remove_document(document_id: int):
    try:
        deleted = delete_document(document_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        return {
            "message": "Document and associated chunks deleted successfully.",
            "document_id": document_id,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Document deletion failed.")

        raise HTTPException(
            status_code=500,
            detail="Failed to delete document.",
        )
