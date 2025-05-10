FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y git ffmpeg && \
    pip install --no-cache-dir fastapi uvicorn python-multipart gradio torch torchvision python-dotenv && \
    pip install -r /workspace/SUPIR-Installation/SUPIR/requirements.txt || true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
