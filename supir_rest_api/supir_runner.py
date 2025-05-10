import uuid
import shutil
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import HTTPException
import subprocess
import os
import time
import threading

JOBS_DIR = Path("/workspace/SUPIR-Installation/supir_jobs")
JOBS_DIR.mkdir(parents=True, exist_ok=True)

SUPIR_SCRIPT = "/workspace/SUPIR-Installation/SUPIR/test.py"
SUPIR_OUTPUTS = Path("/workspace/SUPIR-Installation/SUPIR/outputs")

# Updated path to point to the correct SUPIR config
SUPIR_CONFIG = "/workspace/SUPIR-Installation/SUPIR/options/SUPIR_v0.yaml"

def get_job_status(job_id):
    result_path = JOBS_DIR / job_id / "result.png"
    return {"status": "completed" if result_path.exists() else "pending"}

def get_result(job_id):
    result_path = JOBS_DIR / job_id / "result.png"
    if result_path.exists():
        return FileResponse(str(result_path))
    raise HTTPException(404, "Result not found")

async def process_image(uploaded_file):
    job_id = str(uuid.uuid4())
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    input_path = job_dir / "input.png"
    with open(input_path, "wb") as f:
        shutil.copyfileobj(uploaded_file.file, f)

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0,1"

    cmd = [
        "python", SUPIR_SCRIPT,
        "--img_dir", str(job_dir),
        "--save_dir", str(job_dir),
        "--upscale", "2",
        "--SUPIR_sign", "Q",
        "--ae_dtype", "bf16",
        "--diff_dtype", "bf16",
        "--color_fix_type", "Wavelet"
    ]

    subprocess.Popen(cmd, env=env)

    def monitor_output():
        for _ in range(120):
            result_path = job_dir / "input_0.png"
            if result_path.exists():
                shutil.move(result_path, job_dir / "result.png")
                return
            time.sleep(2)

    threading.Thread(target=monitor_output, daemon=True).start()

    return {"job_id": job_id, "status": "queued"}