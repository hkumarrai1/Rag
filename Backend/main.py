import os
import shutil
import logging
from typing import List
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware #type:ignore

from config import config
from models import FileUploadResponse, AnswerResponse, HealthResponse
from vectorstore import vector_store_manager
from rag import answer_question

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Backend API",
    description="Retrieval Augmented Generation Backend Service",
    version="1.0.0"
)

# Rate limiting - FIXED: Use correct initialization
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def secure_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    return Path(filename).name

def validate_file_size(file: UploadFile) -> None:
    """Validate file size"""
    # Get file size by seeking to end
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if config.MAX_FILE_SIZE and file_size > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File {file.filename} exceeds maximum size of {config.MAX_FILE_SIZE} bytes"
        )

def validate_file_extension(filename: str) -> None:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not supported. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "RAG Backend API is running"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@app.post("/admin/upload", response_model=FileUploadResponse)
@limiter.limit("10/minute")  # FIXED: Use decorator instead of manual check
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """Upload and process files (append to existing knowledge base)"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    file_paths = []
    processed_files = 0
    
    for file in files:
        try:
            # Security validations
            filename = secure_filename(file.filename)
            validate_file_extension(filename)
            validate_file_size(file)
            
            # Save file
            path = os.path.join(config.UPLOAD_DIR, filename)
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(path)
            processed_files += 1
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            continue
    
    if not file_paths:
        raise HTTPException(status_code=400, detail="No valid files to process")
    
    # Process files with vector store
    results = vector_store_manager.add_files(file_paths)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    return FileUploadResponse(
        message=f"Processed {successful} files successfully, {failed} failed",
        processed_files=successful,
        failed_files=failed,
        total_files=len(files)
    )

@app.post("/admin/reset_upload", response_model=FileUploadResponse)
@limiter.limit("5/minute")  # FIXED: Use decorator
async def reset_upload(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """Clear knowledge base and upload new files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # FIRST: Clear the upload directory before saving new files
    logger.info("Clearing existing upload directory...")
    for existing_file in os.listdir(config.UPLOAD_DIR):
        try:
            os.remove(os.path.join(config.UPLOAD_DIR, existing_file))
            logger.info(f"Removed existing file: {existing_file}")
        except Exception as e:
            logger.warning(f"Failed to remove {existing_file}: {e}")
    
    # SECOND: Save new files
    file_paths = []
    processed_files = 0
    
    for file in files:
        try:
            filename = secure_filename(file.filename)
            validate_file_extension(filename)
            validate_file_size(file)
            
            path = os.path.join(config.UPLOAD_DIR, filename)
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            file_paths.append(path)
            processed_files += 1
            logger.info(f"Saved new file: {filename}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            continue
    
    if not file_paths:
        raise HTTPException(status_code=400, detail="No valid files to process")
    
    # THIRD: Reset vector store and add new files
    logger.info(f"Starting vector store reset with {len(file_paths)} files")
    results = vector_store_manager.reset_and_add_files(file_paths)
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    return FileUploadResponse(
        message=f"Knowledge base reset and {successful} files processed successfully, {failed} failed",
        processed_files=successful,
        failed_files=failed,
        total_files=len(files)
    )

@app.get("/ask")
@limiter.limit("30/minute")  # FIXED: Use decorator
async def ask_question(
    request: Request,
    question: str
):
    """Ask a question to the RAG system"""
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if len(question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long")
    
    result = answer_question(question)
    return AnswerResponse(**result)

@app.get("/admin/status")
async def get_system_status():
    """Get system status and vector store information"""
    try:
        collection_info = vector_store_manager.get_collection_info()
        upload_files = os.listdir(config.UPLOAD_DIR)
        
        return {
            "status": "operational",
            "vector_store": collection_info,
            "uploaded_files": upload_files,
            "upload_dir": config.UPLOAD_DIR,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )