from fastapi import FastAPI, UploadFile, File, HTTPException, Security
from fastapi.responses import FileResponse,JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supir_runner import process_image, get_job_status, get_result
from dotenv import load_dotenv
import os

load_dotenv()

security = HTTPBearer()

app = FastAPI()

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"})

@app.post("/job")
async def create_job(file: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token != os.getenv("TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return await process_image(file)

@app.get("/job/{job_id}")
def job_status(job_id: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != os.getenv("TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return get_job_status(job_id)

@app.get("/job/{job_id}/result")
def job_result(job_id: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != os.getenv("TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return get_result(job_id)
