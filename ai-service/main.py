from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import os

from services.embedding_service import EmbeddingService
from services.rag_service import RAGService
from services.report_service import ReportService
from services.document_service import DocumentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Semantic Patient File AI Service",
    description="AI-powered patient file analysis with RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_service = EmbeddingService()
rag_service = RAGService(embedding_service)
report_service = ReportService(embedding_service)
document_service = DocumentService()


# Pydantic models
class ChatRequest(BaseModel):
    patient_id: str
    question: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    timestamp: str


class ReportRequest(BaseModel):
    patient_id: str


class ReportResponse(BaseModel):
    report: Dict[str, Any]
    timestamp: str


class PatientInfo(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    admission_date: Optional[str]
    department: Optional[str]
    document_count: int


class UploadResponse(BaseModel):
    patient_id: str
    files_processed: int
    chunks_created: int
    message: str


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ai-service"
    }


# Get available patients
@app.get("/patients", response_model=List[PatientInfo])
async def get_patients():
    """Get list of all available patients"""
    try:
        logger.info("Fetching available patients")
        patients = document_service.get_available_patients()

        patient_list = []
        for patient_data in patients:
            patient_list.append(PatientInfo(
                patient_id=patient_data['patient_id'],
                name=patient_data.get('name', 'Unknown'),
                age=patient_data.get('age', 0),
                gender=patient_data.get('gender', 'Unknown'),
                admission_date=patient_data.get('admission_date'),
                department=patient_data.get('department'),
                document_count=patient_data.get('document_count', 0)
            ))

        logger.info(f"Found {len(patient_list)} patients")
        return patient_list

    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Upload patient documents
@app.post("/upload", response_model=UploadResponse)
async def upload_documents(
    patient_id: str,
    files: List[UploadFile] = File(...)
):
    """Upload and process patient documents"""
    try:
        logger.info(f"Uploading documents for patient {patient_id}")

        # Process uploaded files
        processed_files = 0
        total_chunks = 0

        for file in files:
            content = await file.read()
            filename = file.filename

            # Determine file type and process
            if filename.endswith('.json'):
                chunks = document_service.process_json(content, patient_id, filename)
            elif filename.endswith('.pdf'):
                chunks = document_service.process_pdf(content, patient_id, filename)
            elif filename.endswith('.txt'):
                chunks = document_service.process_text(content, patient_id, filename)
            else:
                logger.warning(f"Unsupported file type: {filename}")
                continue

            # Store in vector database
            if chunks:
                rag_service.store_documents(patient_id, chunks)
                processed_files += 1
                total_chunks += len(chunks)
                logger.info(f"Processed {filename}: {len(chunks)} chunks")

        return UploadResponse(
            patient_id=patient_id,
            files_processed=processed_files,
            chunks_created=total_chunks,
            message=f"Successfully processed {processed_files} files with {total_chunks} chunks"
        )

    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with patient file using RAG"""
    try:
        logger.info(f"Chat request for patient {request.patient_id}: {request.question}")

        # Get answer using RAG
        result = rag_service.query(
            patient_id=request.patient_id,
            question=request.question,
            conversation_history=request.conversation_history
        )

        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Generate report
@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate discharge report for patient"""
    try:
        logger.info(f"Generating report for patient {request.patient_id}")

        # Generate report
        report = report_service.generate_report(request.patient_id)

        return ReportResponse(
            report=report,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Initialize sample data on startup
@app.on_event("startup")
async def startup_event():
    """Load sample patient data on startup"""
    try:
        logger.info("Starting AI service...")
        logger.info("Loading sample patient data...")

        # Check if data already loaded (prevent duplicates on reload)
        try:
            existing_count = rag_service.qdrant_service.client.count(
                collection_name="patient_documents"
            )
            if existing_count.count > 0:
                logger.info(f"Sample data already loaded ({existing_count.count} vectors in database)")
                return
        except Exception as e:
            logger.info(f"No existing data found, loading sample data...")

        # Check if sample data exists
        sample_data_dir = "/app/sample-data"
        if os.path.exists(sample_data_dir):
            # Load sample patients
            for patient_dir in os.listdir(sample_data_dir):
                patient_path = os.path.join(sample_data_dir, patient_dir)
                if os.path.isdir(patient_path):
                    logger.info(f"Loading patient: {patient_dir}")

                    # Process all files in patient directory
                    chunks = []
                    for filename in os.listdir(patient_path):
                        file_path = os.path.join(patient_path, filename)

                        with open(file_path, 'rb') as f:
                            content = f.read()

                        if filename.endswith('.json'):
                            patient_chunks = document_service.process_json(content, patient_dir, filename)
                        elif filename.endswith('.txt'):
                            patient_chunks = document_service.process_text(content, patient_dir, filename)
                        else:
                            continue

                        chunks.extend(patient_chunks)

                    # Store in vector database
                    if chunks:
                        rag_service.store_documents(patient_dir, chunks)
                        logger.info(f"Loaded {len(chunks)} chunks for {patient_dir}")

        logger.info("Sample data loaded successfully")

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
